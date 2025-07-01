import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv
import time

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente BigQuery
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='trabalho-final-bd-463916')

print("🔄 Configurando BigQuery...")

# Dataset ID
dataset_id = 'trabalho-final-bd-463916.frota_dw'

try:
    dataset = client.get_dataset('frota_dw')
    print("✅ Dataset 'frota_dw' encontrado!")
except:
    print("❌ Dataset não encontrado. Criando...")
    dataset = bigquery.Dataset('trabalho-final-bd-463916.frota_dw')
    dataset.location = "US"
    dataset = client.create_dataset(dataset, timeout=30)
    print("✅ Dataset criado!")

# Carregar dados dos CSVs
print("\n📥 Carregando dados dos CSVs...")
df_veiculos = pd.read_csv('data/veiculos.csv')
df_motoristas = pd.read_csv('data/motoristas.csv') # -- ADICIONADO --
df_viagens = pd.read_csv('data/viagens.csv')
df_eventos = pd.read_csv('data/eventos.csv')

print(f"- Veículos: {len(df_veiculos)} registros")
print(f"- Motoristas: {len(df_motoristas)} registros") # -- ADICIONADO --
print(f"- Viagens: {len(df_viagens)} registros")
print(f"- Eventos: {len(df_eventos)} registros")

# Função auxiliar para criar e popular tabelas
def create_and_populate(table_id, schema, dataframe):
    table = bigquery.Table(table_id, schema=schema)
    try:
        table = client.create_table(table)
        print(f"✅ Tabela {table_id} criada!")
    except:
        print(f"⚠️  Tabela {table_id} já existe, recriando...")
        client.delete_table(table_id, not_found_ok=True)
        time.sleep(2)
        table = client.create_table(table)

    print(f"📥 Inserindo dados em {table_id}...")
    errors = client.insert_rows_json(table_id, dataframe.to_dict('records'))
    if errors:
        print(f"❌ Erros ao inserir: {errors}")
    else:
        print(f"✅ {len(dataframe)} registros inseridos em {table_id}!")

# 1. Criar e popular tabela de veículos
print("\n🚗 Criando tabela de veículos...")
schema_veiculos = [
    bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("placa", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("modelo", "STRING"),
    bigquery.SchemaField("tipo", "STRING"),
    bigquery.SchemaField("ano", "INTEGER"),
    bigquery.SchemaField("km_atual", "INTEGER"),
    bigquery.SchemaField("capacidade_carga", "INTEGER"),
    bigquery.SchemaField("consumo_medio", "FLOAT"),
    bigquery.SchemaField("status", "STRING"),
]
create_and_populate(f"{dataset_id}.veiculos", schema_veiculos, df_veiculos)

# -- ADICIONADO: Criar e popular tabela de motoristas --
print("\n👨‍✈️ Criando tabela de motoristas...")
schema_motoristas = [
    bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("nome", "STRING"),
    bigquery.SchemaField("salario", "FLOAT"),
]
create_and_populate(f"{dataset_id}.motoristas", schema_motoristas, df_motoristas)


# 2. Criar tabela de viagens -- MODIFICADO --
print("\n✈️  Criando tabela de viagens...")
table_viagens_id = f"{dataset_id}.viagens"
schema_viagens = [
    bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("veiculo_id", "INTEGER"),
    bigquery.SchemaField("motorista_id", "INTEGER"), # -- ADICIONADO --
    bigquery.SchemaField("data_saida", "TIMESTAMP"),
    bigquery.SchemaField("data_chegada", "TIMESTAMP"),
    bigquery.SchemaField("origem", "STRING"),
    bigquery.SchemaField("destino", "STRING"),
    bigquery.SchemaField("km_percorridos", "INTEGER"),
    bigquery.SchemaField("combustivel_litros", "FLOAT"),
    bigquery.SchemaField("custo_combustivel", "FLOAT"),
    bigquery.SchemaField("carga_kg", "INTEGER"),
]
create_and_populate(table_viagens_id, schema_viagens, df_viagens)


# 3. Criar views analíticas
print("\n📊 Criando views analíticas...")

# View resumo mensal
view_query = f"""
CREATE OR REPLACE VIEW `{dataset_id}.resumo_mensal` AS
SELECT 
    FORMAT_TIMESTAMP('%Y-%m', data_saida) as mes,
    COUNT(DISTINCT veiculo_id) as veiculos_ativos,
    COUNT(DISTINCT motorista_id) as motoristas_ativos, -- ADICIONADO
    COUNT(*) as total_viagens,
    SUM(km_percorridos) as km_total,
    SUM(custo_combustivel) as custo_total,
    ROUND(AVG(custo_combustivel / NULLIF(km_percorridos, 0)), 2) as custo_medio_por_km
FROM `{dataset_id}.viagens`
GROUP BY mes
ORDER BY mes DESC
"""
client.query(view_query).result()
print("✅ View resumo_mensal criada/atualizada!")

# View por veículo
view_veiculo_query = f"""
CREATE OR REPLACE VIEW `{dataset_id}.analise_por_veiculo` AS
SELECT 
    v.placa, v.modelo, v.tipo,
    COUNT(vg.id) as total_viagens,
    SUM(vg.km_percorridos) as km_total,
    SUM(vg.custo_combustivel) as custo_total,
    ROUND(SUM(vg.custo_combustivel) / SUM(vg.km_percorridos), 2) as custo_por_km
FROM `{dataset_id}.veiculos` v
LEFT JOIN `{dataset_id}.viagens` vg ON v.id = vg.veiculo_id
GROUP BY v.placa, v.modelo, v.tipo
ORDER BY km_total DESC
"""
client.query(view_veiculo_query).result()
print("✅ View analise_por_veiculo criada/atualizada!")

# -- ADICIONADO: View por motorista --
view_motorista_query = f"""
CREATE OR REPLACE VIEW `{dataset_id}.desempenho_por_motorista` AS
SELECT 
    m.nome,
    COUNT(vg.id) as total_viagens,
    SUM(vg.km_percorridos) as km_total,
    SUM(vg.custo_combustivel) as custo_total,
    ROUND(SUM(vg.custo_combustivel) / SUM(vg.km_percorridos), 2) as custo_por_km
FROM `{dataset_id}.motoristas` m
LEFT JOIN `{dataset_id}.viagens` vg ON m.id = vg.motorista_id
GROUP BY m.nome
ORDER BY km_total DESC
"""
client.query(view_motorista_query).result()
print("✅ View desempenho_por_motorista criada!")

print("\n✅ BigQuery configurado!")
print("\n📋 Recursos criados/atualizados:")
print(f"- Tabela veiculos: {dataset_id}.veiculos")
print(f"- Tabela motoristas: {dataset_id}.motoristas")
print(f"- Tabela viagens: {dataset_id}.viagens")
print(f"- View mensal: {dataset_id}.resumo_mensal")
print(f"- View por veículo: {dataset_id}.analise_por_veiculo")
print(f"- View por motorista: {dataset_id}.desempenho_por_motorista")