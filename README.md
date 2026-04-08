# 📊 Pipeline de Cotações do Banco Central (Airflow)

## Sumário

* [Visão Geral](#visao-geral)
* [Tecnologias Utilizadas](#tecnologias-utilizadas)
* [Arquitetura do Pipeline](#arquitetura-do-pipeline)
* [Configuração da DAG](#configuracao-da-dag)
* [Conexão com o Banco](#conexao-com-o-banco)
* [Ambiente com Docker](#ambiente-com-docker)
* [Acessando o Banco com DBeaver](#acessando-o-banco-com-dbeaver)
* [Como Executar o Projeto](#como-executar-o-projeto)
* [Estrutura de Arquivos](#estrutura-de-arquivos)
* [Tratamento de Erros](#tratamento-de-erros)
* [Possíveis Melhorias](#possiveis-melhorias)
* [Objetivo do Projeto](#objetivo-do-projeto)
* [Evidências de Execução](#evidencias-de-execucao)

---

<h2 id="visao-geral">📌 Visão Geral</h2>

Este projeto implementa um pipeline de dados utilizando **Apache Airflow** para coletar, transformar e armazenar cotações de moedas disponibilizadas pelo **Banco Central do Brasil (BCB)**.

O pipeline segue o padrão **ETL (Extract, Transform, Load)** e executa diariamente para um intervalo histórico definido.

---

<h2 id="tecnologias-utilizadas">⚙️ Tecnologias Utilizadas</h2>

* Python
* Apache Airflow
* PostgreSQL
* Pandas
* Docker (via Astro CLI)

---

<h2 id="arquitetura-do-pipeline">🏗️ Arquitetura do Pipeline</h2>

O fluxo da DAG é composto pelas seguintes etapas:

```text
Extract → Transform → Create Table → Load
````

### 1. Extract

* Baixa arquivos CSV diretamente do site do BCB
* Endpoint:

```
https://www4.bcb.gov.br/Download/fechamento/YYYYMMDD.csv
```

* Trata erros:

  * `404`: dias sem cotação (feriados/finais de semana)
  * Outros erros HTTP
* Salva o arquivo temporariamente em `/tmp`

---

### 2. Transform

* Lê o CSV com Pandas
* Define esquema das colunas
* Converte tipos de dados
* Adiciona coluna de `data_processamento`
* Gera um novo arquivo tratado (`_tratado.csv`)

---

### 3. Create Table

```sql
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
);
```

---

### 4. Load

* Lê os dados tratados
* Insere no PostgreSQL usando `PostgresHook`
* Utiliza inserção em lote

---

<h2 id="configuracao-da-dag">📅 Configuração da DAG</h2>

```python
schedule='@daily'
start_date=datetime(2026, 1, 1)
end_date=datetime(2026, 4, 7)
catchup=True
```

### 🔎 Explicação

* **@daily**: executa diariamente
* **catchup=True**: executa retroativamente
* Intervalo: 01/01/2026 até 07/04/2026

---

<h2 id="conexao-com-o-banco">🔌 Conexão com o Banco (PostgreSQL) - Configurações Padrão</h2>

```
postgres_conn_id = "postgres_astro"
```

* Host: postgres
* Database: postgres
* User: postgres
* Password: postgres
* Port: 5432

---

<h2 id="ambiente-com-docker">🐳 Ambiente com Docker (Astro)</h2>

### ▶️ Subir

```bash
astro dev start
```

### ⛔ Parar

```bash
astro dev stop
```

### 🔄 Reiniciar

```bash
astro dev restart
```

---

<h2 id="acessando-o-banco-com-dbeaver">🛢️ Acessando o Banco com DBeaver  - Configurações Padrão</h2>

| Campo    | Valor     |
| -------- | --------- |
| Host     | localhost |
| Port     | 5432      |
| Database | postgres  |
| User     | postgres  |
| Password | postgres  |

---

<h2 id="como-executar-o-projeto">▶️ Como Executar o Projeto</h2>

1. Subir ambiente:

```bash
astro dev start
```

2. Acessar:

```
http://localhost:8080
```

3. Ativar DAG:

* `fin_cotacoes_bcb_classic`

---

<h2 id="estrutura-de-arquivos">📂 Estrutura de Arquivos</h2>

```bash
.
├── dags/
├── screenshots/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

<h2 id="tratamento-de-erros">⚠️ Tratamento de Erros</h2>

* `AirflowSkipException`
* Erros HTTP
* Validação de arquivos

---

<h2 id="possiveis-melhorias">📈 Possíveis Melhorias</h2>

* Upsert no PostgreSQL
* Logs estruturados
* Data Lake (S3/GCS)
* Validação de dados

---

<h2 id="objetivo-do-projeto">🎯 Objetivo do Projeto</h2>

* Engenharia de Dados
* Airflow
* APIs públicas
* Pandas
* PostgreSQL

---

<h2 id="evidencias-de-execucao">📸 Evidências de Execução</h2>

Site com as cotações do Banco Central do Brasil: 

![Evidência 1](/screenshots/ev1.png) 

Dados no DBeaver: 

![Evidência 2](/screenshots/ev2.png) 

DAG no airflow: 

![Evidência 3](/screenshots/ev3.png) 

Visão geral da DAG: 

![Evidência 4](/screenshots/ev4.png) 

Visualização gráfica da DAG: 

![Evidência 5](/screenshots/ev5.png) 

Docker executando o ambiente: 

![Evidência 6](/screenshots/ev6.png)