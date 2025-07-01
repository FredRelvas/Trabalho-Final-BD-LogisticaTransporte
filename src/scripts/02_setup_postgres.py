import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import time

# Carregar variáveis de ambiente
load_dotenv()

print("⏳ Aguardando Cloud SQL ficar pronto...")
print("Por favor, certifique-se que a instância está criada antes de continuar.")
input("Pressione ENTER quando a instância estiver pronta...")

# Configurações de conexão
# IMPORTANTE: Vamos usar IP público temporariamente
INSTANCE_CONNECTION_NAME = "trabalho-final-bd-463916:us-central1:postgres"
DB_USER = "postgres"
DB_PASS = "123"
DB_NAME = "frota_db"

print("\n🔗 Para conectar, precisamos:")
print("1. Ir no Console GCP → SQL → frota-postgres")
print("2. Clicar em 'Connections' → 'Networking'")
print("3. Em 'Authorized networks', clicar 'ADD NETWORK'")
print("4. Name: 'temp-connection'")
print("5. Network: Digite 0.0.0.0/0 (permite qualquer IP temporariamente)")
print("6. Clicar 'DONE' e depois 'SAVE'")
print("\n⚠️  NOTA: Isso é apenas para teste. Em produção, use conexões seguras!")

input("\nPressione ENTER após adicionar a rede autorizada...")

# Pegar o IP público da instância
print("\n📍 Agora precisamos do IP público:")
print("1. Na página da instância, procure por 'Public IP address'")
print("2. Copie o endereço IP (algo como 34.XXX.XXX.XXX)")

PUBLIC_IP = input("\nCole o IP público aqui: ").strip()

# Conectar ao PostgreSQL
try:
    print(f"\n🔄 Conectando ao PostgreSQL em {PUBLIC_IP}...")
    
    # Primeiro conecta ao banco padrão para criar nosso banco
    conn = psycopg2.connect(
        host=PUBLIC_IP,
        user=DB_USER,
        password=DB_PASS,
        database="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Criar banco de dados
    print("📦 Criando banco de dados...")
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    
    cur.close()
    conn.close()
    
    # Conectar ao novo banco
    conn = psycopg2.connect(
        host=PUBLIC_IP,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cur = conn.cursor()
    
    # Criar tabelas
    print("📋 Criando tabelas...")
    
    # Tabela veículos
    cur.execute("""
        CREATE TABLE veiculos (
            id INTEGER PRIMARY KEY,
            placa VARCHAR(10) UNIQUE NOT NULL,
            modelo VARCHAR(100),
            tipo VARCHAR(50),
            ano INTEGER,
            km_atual INTEGER,
            capacidade_carga INTEGER,
            consumo_medio DECIMAL(5,2),
            status VARCHAR(20)
        )
    """)
    
    # -- ADICIONADO: Tabela motoristas --
    cur.execute("""
        CREATE TABLE motoristas (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            salario DECIMAL(10, 2)
        )
    """)
    
    # Tabela viagens -- MODIFICADO --
    cur.execute("""
        CREATE TABLE viagens (
            id INTEGER PRIMARY KEY,
            veiculo_id INTEGER REFERENCES veiculos(id),
            motorista_id INTEGER REFERENCES motoristas(id),
            data_saida TIMESTAMP,
            data_chegada TIMESTAMP,
            origem VARCHAR(100),
            destino VARCHAR(100),
            km_percorridos INTEGER,
            combustivel_litros DECIMAL(8,2),
            custo_combustivel DECIMAL(10,2),
            carga_kg INTEGER
        )
    """)
    
    # Tabela eventos
    cur.execute("""
        CREATE TABLE eventos (
            id INTEGER PRIMARY KEY,
            veiculo_id INTEGER REFERENCES veiculos(id),
            tipo VARCHAR(100),
            data_evento TIMESTAMP,
            descricao TEXT,
            prioridade VARCHAR(20),
            resolvido BOOLEAN
        )
    """)
    
    # Inserir dados
    print("📥 Inserindo dados...")
    
    # Carregar e inserir veículos
    df_veiculos = pd.read_csv('data/veiculos.csv')
    for _, row in df_veiculos.iterrows():
        cur.execute("""
            INSERT INTO veiculos VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))
        
    # -- ADICIONADO: Carregar e inserir motoristas --
    df_motoristas = pd.read_csv('data/motoristas.csv')
    for _, row in df_motoristas.iterrows():
        cur.execute("""
            INSERT INTO motoristas VALUES (%s, %s, %s)
        """, tuple(row))

    # Carregar e inserir viagens -- MODIFICADO --
    df_viagens = pd.read_csv('data/viagens.csv')
    for _, row in df_viagens.iterrows():
        cur.execute("""
            INSERT INTO viagens VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))
    
    # Carregar e inserir eventos
    df_eventos = pd.read_csv('data/eventos.csv')
    for _, row in df_eventos.iterrows():
        cur.execute("""
            INSERT INTO eventos VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))
    
    conn.commit()
    
    # Verificar dados
    print("\n✅ Verificando dados inseridos:")
    cur.execute("SELECT COUNT(*) FROM veiculos")
    print(f"- Veículos: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM motoristas") # -- ADICIONADO --
    print(f"- Motoristas: {cur.fetchone()[0]}") # -- ADICIONADO --
    
    cur.execute("SELECT COUNT(*) FROM viagens")
    print(f"- Viagens: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM eventos")
    print(f"- Eventos: {cur.fetchone()[0]}")
    
    # Salvar informações de conexão
    with open('.env', 'a') as f:
        f.write(f"\nPOSTGRES_HOST={PUBLIC_IP}")
        f.write(f"\nPOSTGRES_USER={DB_USER}")
        f.write(f"\nPOSTGRES_PASS={DB_PASS}")
        f.write(f"\nPOSTGRES_DB={DB_NAME}")
    
    print("\n✅ PostgreSQL configurado com sucesso!")
    print("🔒 LEMBRE-SE: Remova a rede 0.0.0.0/0 após os testes!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    print("\nVerifique:")
    print("1. A instância está rodando?")
    print("2. O IP está correto?")
    print("3. A rede foi autorizada?")
    print("4. A senha está correta?")