from datetime import datetime, timedelta
from airflow import DAG

from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowSkipException

import pandas as pd
import requests
import logging
from io import StringIO
import os

# DAG
dag = DAG(
    dag_id='fin_cotacoes_bcb_classic',
    schedule='@daily',
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 4, 7), 
    catchup=True,
    default_args={
        'owner': 'airflow',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
    },
    tags=["bcb"]
)

###### EXTRACT ######

def extract(**context):
    ds_nodash = context["ds_nodash"]

    url = f"https://www4.bcb.gov.br/Download/fechamento/{ds_nodash}.csv"
    logging.info(f"Baixando: {url}")

    response = requests.get(url, timeout=30)

    if response.status_code == 404:
        logging.warning(f"Sem dados para {ds_nodash}")
        raise AirflowSkipException("Dia sem cotação (fim de semana/feriado)")

    if response.status_code != 200:
        raise Exception(f"Erro HTTP: {response.status_code}")

    path = f"/tmp/cotacoes_{ds_nodash}.csv"

    with open(path, "w", encoding="utf-8") as f:
        f.write(response.content.decode("utf-8"))

    return path


extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag
)

###### TRANSFORM ######

def transform(**context):
    path = context['ti'].xcom_pull(task_ids='extract')

    if not path or not os.path.exists(path):
        raise ValueError("Arquivo não encontrado no transform")

    df = pd.read_csv(
        path,
        sep=";",
        decimal=",",
        thousands=".",
        encoding="utf-8",
        header=None,
        names=[
            "DT_FECHAMENTO",
            "COD_MOEDA",
            "TIPO_MOEDA",
            "DESC_MOEDA",
            "TAXA_COMPRA",
            "TAXA_VENDA",
            "PARIDADE_COMPRA",
            "PARIDADE_VENDA"
        ]
    )

    df['DT_FECHAMENTO'] = pd.to_datetime(df['DT_FECHAMENTO'], dayfirst=True)

    df['data_processamento'] = pd.to_datetime(context['ds'])

    output_path = path.replace(".csv", "_tratado.csv")
    df.to_csv(output_path, index=False)

    return output_path


transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag
)

###### CREATE TABLE ######

create_table_ddl = """
CREATE TABLE IF NOT EXISTS cotacoes (
    dt_fechamento DATE,
    cod_moeda TEXT,
    tipo_moeda TEXT,
    desc_moeda TEXT,
    taxa_compra REAL,
    taxa_venda REAL,
    paridade_compra REAL,
    paridade_venda REAL,
    data_processamento TIMESTAMP,
    CONSTRAINT table_pk PRIMARY KEY (dt_fechamento, cod_moeda)
)
"""

create_table_postgres = PostgresOperator(
    task_id="create_table_postgres",
    postgres_conn_id="postgres_astro",
    sql=create_table_ddl,
    dag=dag
)

###### LOAD ######

def load(**context):
    path = context['ti'].xcom_pull(task_ids='transform')

    if not path or not os.path.exists(path):
        raise ValueError("Arquivo não encontrado no load")

    df = pd.read_csv(path)

    postgres_hook = PostgresHook(postgres_conn_id="postgres_astro")

    rows = list(df.itertuples(index=False, name=None))

    postgres_hook.insert_rows(
        table="cotacoes",
        rows=rows,
        target_fields=[
            "dt_fechamento",
            "cod_moeda",
            "tipo_moeda",
            "desc_moeda",
            "taxa_compra",
            "taxa_venda",
            "paridade_compra",
            "paridade_venda",
            "data_processamento"
        ]
    )

    logging.info(f"{len(rows)} linhas inseridas com sucesso")


load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag
)

###### PIPELINE ######

extract_task >> transform_task >> create_table_postgres >> load_task