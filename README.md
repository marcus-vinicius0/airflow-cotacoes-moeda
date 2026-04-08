# 📊 Pipeline de Cotações do Banco Central (Airflow)

## Sumário

* [Visão Geral](#-visão-geral)
* [Tecnologias Utilizadas](#tecnologias-utilizadas)
* [Arquitetura do Pipeline](#arquitetura-do-pipeline)
* [Configuração da DAG](#configuração-da-dag)
* [Conexão com o Banco](#conexão-com-o-banco)
* [Ambiente com Docker](#ambiente-com-docker)
* [Acessando o Banco com DBeaver](#acessando-o-banco-com-dbeaver)
* [Como Executar o Projeto](#como-executar-o-projeto)
* [Estrutura de Arquivos](#estrutura-de-arquivos)
* [Tratamento de Erros](#tratamento-de-erros)
* [Possíveis Melhorias](#possíveis-melhorias)
* [Objetivo do Projeto](#objetivo-do-projeto)
* [Evidências de Execução](#evidências-de-execução)


## 📌 Visão Geral

Este projeto implementa um pipeline de dados utilizando **Apache Airflow** para coletar, transformar e armazenar cotações de moedas disponibilizadas pelo **Banco Central do Brasil (BCB)**.

O pipeline segue o padrão **ETL (Extract, Transform, Load)** e executa diariamente para um intervalo histórico definido.

---

## ⚙️ Tecnologias Utilizadas

* Python
* Apache Airflow
* PostgreSQL
* Pandas
* Docker (via Astro CLI)

---

## 🏗️ Arquitetura do Pipeline

O fluxo da DAG é composto pelas seguintes etapas:

```text
Extract → Transform → Create Table → Load
```

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

* Cria a tabela `cotacoes` no PostgreSQL (caso não exista)

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

## 📅 Configuração da DAG

```python
schedule='@daily'
start_date=datetime(2026, 1, 1)
end_date=datetime(2026, 4, 7)
catchup=True
```

### 🔎 Explicação

* **@daily**: executa diariamente
* **catchup=True**: executa retroativamente para todas as datas no intervalo
* **intervalo fechado**: de 01/01/2026 até 07/04/2026

---

## 🔌 Conexão com o Banco (PostgreSQL)

A DAG utiliza a conexão:

```
postgres_conn_id = "postgres_astro"
```

### Configuração no Airflow (Valores padrão):

* Host: postgres
* Database: postgres
* User: postgres
* Password: postgres
* Port: 5432

> ⚠️ Esses valores podem variar dependendo do seu `docker-compose` / Astro

---

## 🐳 Ambiente com Docker (Astro)

Este projeto utiliza **Docker** via **Astro CLI** para subir o ambiente completo do Airflow.

### 📦 Serviços executados

* Airflow Webserver
* Airflow Scheduler
* PostgreSQL
* Redis

---

### ▶️ Subir o ambiente

```bash
astro dev start
```

### ⛔ Parar o ambiente

```bash
astro dev stop
```

### 🔄 Reiniciar

```bash
astro dev restart
```

---

### 🌐 Acessos

* Airflow UI: [http://localhost:8080](http://localhost:8080)
* PostgreSQL (interno Docker): `postgres:5432`

---

## 🛢️ Acessando o Banco com DBeaver

Você pode conectar ao PostgreSQL do Airflow usando o **DBeaver**.

### 🔌 Configuração da conexão

| Campo    | Valor     |
| -------- | --------- |
| Host     | localhost |
| Port     | 5432      |
| Database | postgres  |
| User     | postgres  |
| Password | postgres  |

> ⚠️ Caso não funcione, verifique se a porta 5432 está exposta no Docker

---

### 📊 Verificando os dados

Após rodar a DAG:

```sql
SELECT * FROM cotacoes;
```

---

## ▶️ Como Executar o Projeto

### 1. Subir ambiente

```bash
astro dev start
```

### 2. Acessar Airflow

```
http://localhost:8080
```

### 3. Ativar DAG

* Buscar: `fin_cotacoes_bcb_classic`
* Ativar (toggle ON)
* Executar manualmente ou aguardar scheduler

---

## 📂 Estrutura de Arquivos

```bash
.
├── dags/
│   └── fin_cotacoes_bcb_classic.py
├── include/
├── plugins/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚠️ Tratamento de Erros

* Dias sem cotação → `AirflowSkipException`
* Falha HTTP → Exception
* Arquivo inexistente → validação em cada etapa

---

## 📈 Possíveis Melhorias

* Implementar **upsert (ON CONFLICT)** no PostgreSQL
* Adicionar logs estruturados
* Armazenar arquivos em Data Lake (S3, GCS)
* Criar camada de validação de dados
* Orquestrar múltiplas fontes de dados

---

## 🎯 Objetivo do Projeto

Demonstrar habilidades em:

* Engenharia de Dados
* Orquestração com Airflow
* Integração com APIs públicas
* Processamento de dados com Pandas
* Persistência em banco relacional
---
## Evidências de Execução

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
