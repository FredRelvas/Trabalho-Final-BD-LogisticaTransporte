import os
import psycopg2
from google.cloud import bigquery, firestore
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis
load_dotenv()

print("🔍 Testando consultas nos 3 bancos de dados...")
print("=" * 60)

# 1. POSTGRESQL - Consulta Operacional
print("\n1️⃣ POSTGRESQL - Motoristas e seus salários") # -- MODIFICADO --
print("-" * 40)

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASS'),
        database=os.getenv('POSTGRES_DB')
    )
    cur = conn.cursor()
    
    # -- QUERY MODIFICADA --
    query = """
    SELECT nome, salario
    FROM motoristas
    ORDER BY salario DESC
    LIMIT 5
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    for row in results:
        print(f"  - {row[0]} - Salário: R$ {row[1]:,.2f}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro PostgreSQL: {e}")

# 2. BIGQUERY - Consulta Analítica
print("\n2️⃣ BIGQUERY - Desempenho dos motoristas com mais KM") # -- MODIFICADO --
print("-" * 40)

try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
    client = bigquery.Client(project='trabalho-final-bd-463916')
    
    # -- QUERY MODIFICADA para usar a nova view --
    query = """
    SELECT 
        nome,
        total_viagens,
        km_total
    FROM `trabalho-final-bd-463916.frota_dw.desempenho_por_motorista`
    WHERE km_total > 0
    ORDER BY km_total DESC
    LIMIT 5
    """
    
    df = client.query(query).to_dataframe()
    
    for _, row in df.iterrows():
        print(f"  - {row['nome']}: {row['total_viagens']} viagens, {row['km_total']:,} km rodados")
    
except Exception as e:
    print(f"❌ Erro BigQuery: {e}")

# 3. FIRESTORE - Consulta Tempo Real
print("\n3️⃣ FIRESTORE - Veículos em viagem e seus motoristas") # -- MODIFICADO --
print("-" * 40)

try:
    db = firestore.Client(project='trabalho-final-bd-463916')
    
    # -- QUERY MODIFICADA --
    query = db.collection('veiculos_status') \
        .where('status', '==', 'Em viagem') \
        .limit(5)
    
    count = 0
    for doc in query.stream():
        data = doc.to_dict()
        viagem_info = data.get('viagem_atual', {})
        motorista = viagem_info.get('motorista_nome', 'N/A')
        destino = viagem_info.get('destino', 'N/A')
        print(f"  - Veículo {data['placa']} com motorista {motorista} a caminho de {destino}")
        count += 1
    
    if count == 0:
        print("  Nenhum veículo em viagem encontrado.")
    
except Exception as e:
    print(f"❌ Erro Firestore: {e}")

# ... (o resto do arquivo permanece o mesmo)
# 4. CONSULTA INTEGRADA - Visão 360°
# print("\n4️⃣ CONSULTA INTEGRADA - Status completo da frota")
# print("-" * 40)

# try:
#     # Firestore - Métricas gerais
#     db = firestore.Client(project='trabalho-final-bd-463916')
#     metricas = db.collection('metricas_tempo_real').document('dashboard').get().to_dict()
    
#     print(f"📊 Status Geral da Frota:")
#     print(f"  • Total de veículos: {metricas['frota_total']}")
#     print(f"  • Total de motoristas: {metricas.get('motoristas_total', 'N/A')}") # -- ADICIONADO --
#     print(f"  • Disponíveis: {metricas['veiculos_disponiveis']}")
#     print(f"  • Em viagem: {metricas['veiculos_em_viagem']}")
#     print(f"  • Em manutenção: {metricas['veiculos_manutencao']}")
#     print(f"  • Eficiência: {metricas['eficiencia_frota']}%")
#     print(f"  • Alertas ativos: {metricas['alertas_ativos']['total']}")
    
#     # BigQuery - Custo total do mês atual
#     client = bigquery.Client(project='trabalho-final-bd-463916')
#     mes_atual = datetime.now().strftime('%Y-%m')
    
#     query = f"""
#     SELECT custo_total, km_total
#     FROM `trabalho-final-bd-463916.frota_dw.resumo_mensal`
#     WHERE mes = '{mes_atual}'
#     """
    
    # df = client.query(query).to_dataframe()
    # if not df.empty:
    #     print(f"\n💰 Custos do mês atual ({mes_atual}):")
    #     print(f"  • Total gasto: R$ {df.iloc[0]['custo_total']:,.2f}")
    #     print(f"  • KM rodados: {df.iloc[0]['km_total']:,}")
    
except Exception as e:
    print(f"❌ Erro na consulta integrada: {e}")

print("\n" + "=" * 60)
print("✅ Testes concluídos!")