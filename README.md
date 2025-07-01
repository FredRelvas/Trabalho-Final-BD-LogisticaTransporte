# 🚗 Gestão de Frota com Python, Firestore, PostgreSQL e BigQuery

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📄 Descrição

Este projeto foi desenvolvido para gerenciar e analisar dados de uma frota de veículos, utilizando uma arquitetura de dados completa. Ele emprega scripts Python para processamento, **PostgreSQL** como banco de dados relacional para dados estruturados, **Google Firestore** como banco de dados NoSQL para informações flexíveis e em tempo real, e **Google BigQuery** como Data Warehouse para análises complexas e em larga escala.

## ✨ Features

-   **Arquitetura Híbrida:** Combina o poder de um banco de dados relacional (PostgreSQL) com a flexibilidade de um NoSQL (Firestore).
-   **Data Warehouse:** Utiliza o Google BigQuery para análises avançadas e business intelligence.
-   **Conexão Segura:** Autenticação com serviços Google Cloud usando um arquivo de credenciais de serviço.
-   **Manipulação de Dados:** Scripts para inserir, atualizar e consultar dados nos diferentes bancos de dados.
-   **Visualização de Dados:** Um notebook Jupyter para criar gráficos e dashboards interativos a partir dos dados consolidados.

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python 3
-   **Banco de Dados Relacional:** PostgreSQL
-   **Banco de Dados NoSQL:** Google Firestore
-   **Data Warehouse:** Google BigQuery
-   **Bibliotecas Principais:**
    -   `psycopg2-binary` (para PostgreSQL)
    -   `google-cloud-firestore`
    -   `google-cloud-bigquery`
    -   `pandas`
    -   `jupyterlab`

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar o ambiente e executar o projeto localmente.

#### Pré-requisitos

-   [Python 3.8+](https://www.python.org/downloads/)
-   Acesso a um servidor PostgreSQL.
-   Uma conta no [Google Cloud Platform](https://cloud.google.com/) com um projeto e as APIs do Firestore e BigQuery habilitadas.

#### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/FredRelvas/Trabalho-Final-BD-LogisticaTransporte
    
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as credenciais:**
    -   **Google Cloud:** Crie uma **Conta de Serviço** (Service Account) com permissões para Firestore e BigQuery. Gere uma chave JSON, copie o arquivo `config.example.json` para `credentials.json` e cole o conteúdo da chave nele.
    -   **PostgreSQL:** Configure suas variáveis de ambiente ou um arquivo de configuração para armazenar o host, usuário, senha e banco de dados do PostgreSQL.
    > ⚠️ **Importante:** Arquivos de credenciais e senhas **nunca** devem ser enviados para o repositório. Certifique-se de que estão no `.gitignore`.

## 🚀 Como Usar

Com o ambiente configurado, você pode executar as diferentes partes do projeto.

#### Executar Scripts de Processamento

Para executar um script de manipulação de dados, navegue até a pasta `src` e execute o arquivo desejado:
```bash
python src/nome_do_script.py
