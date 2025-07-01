import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import os # -- ADICIONADO --

fake = Faker('pt_BR')

# Configurações
NUM_VEICULOS = 20
NUM_VIAGENS = 500
NUM_EVENTOS = 100
NUM_MOTORISTAS = 30 # -- ADICIONADO --

# -- ADICIONADO --
# Criar pasta de dados se não existir
if not os.path.exists('data'):
    os.makedirs('data')

# 1. Gerar Veículos
print("Gerando veículos...")
veiculos = []
tipos = ['Caminhão', 'Van', 'Utilitário']
marcas = ['Mercedes', 'Volkswagen', 'Ford', 'Iveco']

for i in range(1, NUM_VEICULOS + 1):
    veiculo = {
        'id': i,
        'placa': fake.license_plate(),
        'modelo': f"{random.choice(marcas)} {random.choice(['Sprinter', 'Daily', 'Cargo', 'Delivery'])}",
        'tipo': random.choice(tipos),
        'ano': random.randint(2018, 2024),
        'km_atual': random.randint(10000, 150000),
        'capacidade_carga': random.randint(1000, 5000),
        'consumo_medio': round(random.uniform(8.0, 15.0), 1),
        'status': random.choice(['Disponível', 'Em viagem', 'Manutenção'])
    }
    veiculos.append(veiculo)

df_veiculos = pd.DataFrame(veiculos)

# -- ADICIONADO: Gerar Motoristas --
print("Gerando motoristas...")
motoristas = []
for i in range(1, NUM_MOTORISTAS + 1):
    motorista = {
        'id': i,
        'nome': fake.name(),
        'salario': round(random.uniform(2800.0, 6500.0), 2)
    }
    motoristas.append(motorista)

df_motoristas = pd.DataFrame(motoristas)


# 2. Gerar Viagens
print("Gerando viagens...")
viagens = []
cidades = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 
           'Salvador', 'Recife', 'Fortaleza', 'Brasília', 'Goiânia']

for i in range(1, NUM_VIAGENS + 1):
    dias_atras = random.randint(0, 180)
    data_viagem = datetime.now() - timedelta(days=dias_atras)
    duracao_horas = random.randint(2, 48)
    
    viagem = {
        'id': i,
        'veiculo_id': random.randint(1, NUM_VEICULOS),
        'motorista_id': random.randint(1, NUM_MOTORISTAS), # -- ADICIONADO --
        'data_saida': data_viagem.strftime('%Y-%m-%d %H:%M:%S'),
        'data_chegada': (data_viagem + timedelta(hours=duracao_horas)).strftime('%Y-%m-%d %H:%M:%S'),
        'origem': random.choice(cidades),
        'destino': random.choice(cidades),
        'km_percorridos': random.randint(50, 1500),
        'combustivel_litros': round(random.uniform(20, 200), 2),
        'custo_combustivel': round(random.uniform(100, 1000), 2),
        'carga_kg': random.randint(100, 4000)
    }
    viagens.append(viagem)

df_viagens = pd.DataFrame(viagens)

# 3. Gerar Eventos/Alertas
print("Gerando eventos...")
eventos = []
tipos_evento = ['Manutenção Preventiva', 'Alerta de Combustível', 'Excesso de Velocidade', 
                'Parada Não Programada', 'Troca de Óleo', 'Revisão Completa']

for i in range(1, NUM_EVENTOS + 1):
    dias_atras = random.randint(0, 30)
    data_evento = datetime.now() - timedelta(days=dias_atras)
    
    evento = {
        'id': i,
        'veiculo_id': random.randint(1, NUM_VEICULOS),
        'tipo': random.choice(tipos_evento),
        'data_evento': data_evento.strftime('%Y-%m-%d %H:%M:%S'),
        'descricao': fake.sentence(nb_words=10),
        'prioridade': random.choice(['Baixa', 'Média', 'Alta']),
        'resolvido': random.choice([True, False])
    }
    eventos.append(evento)

df_eventos = pd.DataFrame(eventos)

# 4. Salvar arquivos
print("Salvando arquivos...")
df_veiculos.to_csv('data/veiculos.csv', index=False, encoding='utf-8')
df_motoristas.to_csv('data/motoristas.csv', index=False, encoding='utf-8') # -- ADICIONADO --
df_viagens.to_csv('data/viagens.csv', index=False, encoding='utf-8')
df_eventos.to_csv('data/eventos.csv', index=False, encoding='utf-8')

# 5. Mostrar resumo
print("\n✅ Dados gerados com sucesso!")
print(f"- {NUM_VEICULOS} veículos")
print(f"- {NUM_MOTORISTAS} motoristas") # -- ADICIONADO --
print(f"- {NUM_VIAGENS} viagens (últimos 6 meses)")
print(f"- {NUM_EVENTOS} eventos (últimos 30 dias)")

# Mostrar amostras
print("\n📊 Amostra dos dados:")
print("\nVeículos:")
print(df_veiculos.head(3))
print("\nMotoristas:") # -- ADICIONADO --
print(df_motoristas.head(3)) # -- ADICIONADO --
print("\nViagens:")
print(df_viagens.head(3))
print("\nEventos:")
print(df_eventos.head(3))