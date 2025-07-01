import os
import pandas as pd
from google.cloud import firestore
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Firestore
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
db = firestore.Client(project='trabalho-final-bd-463916')

print("🔄 Configurando Firestore...")

# Carregar dados dos CSVs
print("📥 Carregando dados dos CSVs...")
df_veiculos = pd.read_csv('data/veiculos.csv')
df_viagens = pd.read_csv('data/viagens.csv')
df_eventos = pd.read_csv('data/eventos.csv')
df_motoristas = pd.read_csv('data/motoristas.csv') # -- ADICIONADO --

# 1. Criar coleção de status atual dos veículos
print("\n🚗 Criando status atual dos veículos...")
veiculos_ref = db.collection('veiculos_status')

# Limpar coleção existente
for doc in veiculos_ref.stream():
    doc.reference.delete()

status_opcoes = {
    'Disponível': {'cor': 'verde', 'icone': '✅'},
    'Em viagem': {'cor': 'azul', 'icone': '🚛'},
    'Manutenção': {'cor': 'vermelho', 'icone': '🔧'}
}

# Inserir status de cada veículo
for _, veiculo in df_veiculos.iterrows():
    viagens_veiculo = df_viagens[df_viagens['veiculo_id'] == veiculo['id']]
    
    ultima_localizacao = 'Base' if viagens_veiculo.empty else viagens_veiculo.sort_values('data_saida').iloc[-1]['destino']
    
    doc_data = {
        'veiculo_id': int(veiculo['id']),
        'placa': veiculo['placa'],
        'modelo': veiculo['modelo'],
        'status': veiculo['status'],
        'status_info': status_opcoes[veiculo['status']],
        'ultima_atualizacao': datetime.now(),
        'localizacao_atual': ultima_localizacao,
        'latitude': -23.5505 + random.uniform(-2, 2),  # -- ADICIONADO --
        'longitude': -46.6333 + random.uniform(-2, 2), # -- ADICIONADO --
        'km_atual': int(veiculo['km_atual']),
        'proximo_servico_km': int(veiculo['km_atual']) + 5000,
        'combustivel_nivel': random.randint(20, 100),
        'temperatura_motor': random.randint(80, 95),
    }
    
    # Se em viagem, adicionar info da viagem -- MODIFICADO --
    if veiculo['status'] == 'Em viagem':
        motorista_aleatorio = df_motoristas.sample(1).iloc[0]
        viagem_veiculo = viagens_veiculo.iloc[-1] # Pega a ultima viagem
        
        doc_data['viagem_atual'] = {
            'origem': viagem_veiculo['origem'],
            'destino': viagem_veiculo['destino'],
            'previsao_chegada': pd.to_datetime(viagem_veiculo['data_chegada']),
            'carga': f"{viagem_veiculo['carga_kg']} kg",
            'motorista_id': int(motorista_aleatorio['id']),
            'motorista_nome': motorista_aleatorio['nome']
        }
    
    veiculos_ref.document(veiculo['placa']).set(doc_data)

print(f"✅ {len(df_veiculos)} status de veículos inseridos!")

# ... (o resto do arquivo permanece o mesmo)
# 2. Criar coleção de alertas/eventos em tempo real
print("\n🚨 Criando alertas e eventos...")
alertas_ref = db.collection('alertas')

# Limpar coleção existente
docs = alertas_ref.stream()
for doc in docs:
    doc.reference.delete()

# Criar alertas baseados nos eventos
alertas_ativos = []
for _, evento in df_eventos.iterrows():
    if not evento['resolvido']:  # Apenas eventos não resolvidos
        alerta = {
            'evento_id': int(evento['id']),
            'veiculo_id': int(evento['veiculo_id']),
            'placa': df_veiculos[df_veiculos['id'] == evento['veiculo_id']].iloc[0]['placa'],
            'tipo': evento['tipo'],
            'prioridade': evento['prioridade'],
            'descricao': evento['descricao'],
            'data_criacao': pd.to_datetime(evento['data_evento']).to_pydatetime(),
            'tempo_aberto': str(datetime.now() - pd.to_datetime(evento['data_evento']).to_pydatetime()).split('.')[0],
            'responsavel': random.choice(['João Silva', 'Maria Santos', 'Pedro Costa', None]),
            'observacoes': []
        }
        
        # Adicionar cores por prioridade
        cores_prioridade = {
            'Alta': {'cor': '#FF0000', 'peso': 3},
            'Média': {'cor': '#FFA500', 'peso': 2},
            'Baixa': {'cor': '#008000', 'peso': 1}
        }
        alerta['prioridade_info'] = cores_prioridade[evento['prioridade']]
        
        alertas_ref.add(alerta)
        alertas_ativos.append(alerta)

print(f"✅ {len(alertas_ativos)} alertas ativos inseridos!")

# 3. Criar coleção de métricas em tempo real
print("\n📊 Criando métricas em tempo real...")
metricas_ref = db.collection('metricas_tempo_real')

# Calcular métricas
viagens_hoje = df_viagens[
    pd.to_datetime(df_viagens['data_saida']).dt.date == datetime.now().date()
]

metricas = {
    'ultima_atualizacao': datetime.now(),
    'frota_total': len(df_veiculos),
    'motoristas_total': len(df_motoristas), # -- ADICIONADO --
    'veiculos_disponiveis': len(df_veiculos[df_veiculos['status'] == 'Disponível']),
    'veiculos_em_viagem': len(df_veiculos[df_veiculos['status'] == 'Em viagem']),
    'veiculos_manutencao': len(df_veiculos[df_veiculos['status'] == 'Manutenção']),
    'viagens_hoje': len(viagens_hoje),
    'km_total_hoje': int(viagens_hoje['km_percorridos'].sum()) if not viagens_hoje.empty else 0,
    'alertas_ativos': {
        'total': len(alertas_ativos),
        'alta_prioridade': len([a for a in alertas_ativos if a['prioridade'] == 'Alta']),
        'media_prioridade': len([a for a in alertas_ativos if a['prioridade'] == 'Média']),
        'baixa_prioridade': len([a for a in alertas_ativos if a['prioridade'] == 'Baixa'])
    },
    'eficiencia_frota': round(
        (len(df_veiculos[df_veiculos['status'] != 'Manutenção']) / len(df_veiculos)) * 100, 1
    )
}

metricas_ref.document('dashboard').set(metricas)
print("✅ Métricas em tempo real criadas!")

# ... (o resto do arquivo permanece o mesmo)