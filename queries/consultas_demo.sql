-- ========================================
-- CONSULTAS POSTGRESQL (Operacional)
-- ========================================

-- 1. Veículos que precisam de manutenção (rodaram mais de 5000km desde última)
SELECT 
    v.placa,
    v.modelo,
    v.km_atual,
    v.km_atual - COALESCE(
        (SELECT MAX(e.km_veiculo) 
         FROM eventos e 
         WHERE e.veiculo_id = v.id 
         AND e.tipo IN ('Manutenção Preventiva', 'Revisão Completa')), 
        v.km_atual - 5000
    ) as km_desde_manutencao
FROM veiculos v
WHERE v.km_atual - COALESCE(
    (SELECT MAX(e.km_veiculo) 
     FROM eventos e 
     WHERE e.veiculo_id = v.id 
     AND e.tipo IN ('Manutenção Preventiva', 'Revisão Completa')), 
    v.km_atual - 5000
) > 5000
ORDER BY km_desde_manutencao DESC;

-- 2. Viagens em andamento (status tempo real)
SELECT 
    v.placa,
    v.modelo,
    vg.origem,
    vg.destino,
    vg.data_saida,
    EXTRACT(HOUR FROM (NOW() - vg.data_saida)) as horas_viajando
FROM veiculos v
JOIN viagens vg ON v.id = vg.veiculo_id
WHERE v.status = 'Em viagem'
AND vg.data_chegada > NOW()
ORDER BY vg.data_saida DESC;

-- 3. Consumo médio por tipo de veículo (últimos 30 dias)
SELECT 
    v.tipo,
    COUNT(DISTINCT v.id) as qtd_veiculos,
    COUNT(vg.id) as total_viagens,
    ROUND(AVG(vg.combustivel_litros / vg.km_percorridos * 100), 2) as consumo_medio_l_100km,
    ROUND(AVG(vg.custo_combustivel / vg.km_percorridos), 2) as custo_medio_por_km
FROM veiculos v
JOIN viagens vg ON v.id = vg.veiculo_id
WHERE vg.data_saida >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY v.tipo
ORDER BY consumo_medio_l_100km;

-- ========================================
-- CONSULTAS BIGQUERY (Analítico)
-- ========================================

-- 4. Análise de custos mensais (trend)
SELECT 
    mes,
    veiculos_ativos,
    total_viagens,
    km_total,
    custo_total,
    ROUND(custo_total / km_total, 2) as custo_por_km,
    ROUND(custo_total / total_viagens, 2) as custo_medio_viagem
FROM `gestao-frota-db.frota_dw.resumo_mensal`
ORDER BY mes DESC
LIMIT 6;

-- 5. Ranking de eficiência dos veículos
SELECT 
    placa,
    modelo,
    tipo,
    total_viagens,
    km_total,
    custo_total,
    custo_por_km,
    RANK() OVER (ORDER BY custo_por_km ASC) as ranking_eficiencia
FROM `gestao-frota-db.frota_dw.analise_por_veiculo`
WHERE km_total > 0
ORDER BY ranking_eficiencia;

-- 6. Comparação YoY (Year over Year) - se tivéssemos dados históricos
SELECT 
    EXTRACT(YEAR FROM PARSE_TIMESTAMP('%Y-%m', mes)) as ano,
    SUM(km_total) as km_anual,
    SUM(custo_total) as custo_anual,
    COUNT(DISTINCT mes) as meses_operacao,
    ROUND(SUM(custo_total) / SUM(km_total), 2) as custo_medio_km_anual
FROM `gestao-frota-db.frota_dw.resumo_mensal`
GROUP BY ano
ORDER BY ano DESC;

-- ========================================
-- CONSULTAS FIRESTORE (via Python/API)
-- ========================================

-- 7. Status em tempo real (pseudo-SQL para demonstração)
/*
collection: veiculos_status
query: where('status', '==', 'Em viagem')
fields: placa, modelo, localizacao_atual, viagem_atual.destino, viagem_atual.previsao_chegada
*/

-- 8. Alertas prioritários
/*
collection: alertas
query: where('prioridade', '==', 'Alta').where('responsavel', '==', null)
order: data_criacao DESC
fields: placa, tipo, descricao, tempo_aberto
*/

-- 9. Métricas do dashboard
/*
collection: metricas_tempo_real
document: dashboard
fields: ALL (frota_total, veiculos_disponiveis, veiculos_em_viagem, 
         veiculos_manutencao, alertas_ativos, eficiencia_frota)
*/

-- ========================================
-- CONSULTA INTEGRADA (Cross-Database)
-- ========================================

-- 10. Visão 360° do veículo (combina os 3 bancos)
/*
Processo:
1. PostgreSQL: Dados básicos + histórico viagens
2. BigQuery: Métricas agregadas e ranking
3. Firestore: Status tempo real + alertas ativos

Exemplo para veículo 'ABC-1234':
- Info básica (PostgreSQL)
- KM total e custos (BigQuery) 
- Localização atual e alertas (Firestore)
- Consolidar em uma única resposta
*/