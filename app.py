import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Caixa Habitação", layout="wide")
st.title("🏠 Simulador de Amortização Imobiliária")
st.subheader("Fiel ao Padrão do App Caixa Habitação (Tabela Price)")

# --- Interface em Duas Colunas (Inputs à Esquerda, Resultados à Direita) ---
col_menu, col_Painel = st.columns([1, 2], gap="large")

with col_menu:
    st.markdown("### 📋 Configuração do Contrato")
    
    # Dados exatos da sua imagem
    saldo_devedor_atual = st.number_input(
        "Saldo Devedor Atual (R$)", 
        min_value=0.0, value=327639.45, step=1000.0, format="%.2f"
    )
    
    # Taxa média Caixa (reajuste aqui se precisar calibrar mais)
    taxa_anual_input = st.number_input(
        "Taxa de Juros Anual (%)", 
        min_value=0.0, max_value=100.0, value=9.5, step=0.1, format="%.2f"
    )
    
    prazo_restante = st.number_input(
        "Meses Restantes", 
        min_value=1, max_value=420, value=420, step=1
    )
    
    st.markdown("---")
    st.markdown("### 📉 Simular Amortização")
    
    # Coloquei os 1000 reais que você usou na realidade
    valor_amortizar = st.number_input(
        "Quanto você gostaria de amortizar?", 
        min_value=0.0, value=1000.00, step=50.0, format="%.2f"
    )
    
    tipo_amortizacao = st.radio(
        "Qual tipo de amortização?",
        ["Prazo", "Prestação"],
        help="Prazo: Diminui o número de prestações restantes. Prestação: Diminui o valor mensal."
    )
    
    taxas_somadas = 45.00 + 15.00 + 25.00  # Seguros aproximados Caixa (MIP + DFI + Taxa)

# --- Processamento Matemático Simulado (Sem Logaritmo Propenso a Erros) ---
taxa_mensal = (taxa_anual_input / 100) / 12

# 1. Cálculo exato da parcela base (Price)
if saldo_devedor_atual > 0 and prazo_restante > 0:
    fator_orig = (1 + taxa_mensal) ** prazo_restante
    pmt_original = saldo_devedor_atual * (taxa_mensal * fator_orig) / (fator_orig - 1)
else:
    pmt_original = 0.0

# 2. Função Simuladora de Linha de Tempo (Varredura)
def rodar_cronograma(saldo_inicial, pmt_limite, taxa, reduzir_parcela, saldo_alvo_parcial=0):
    saldo = saldo_inicial
    meses_decorridos = 0
    historico_saldos = []
    
    # Se for redução de parcela, recalculamos a PMT para o novo saldo
    if reduzir_parcela and saldo_inicial > 0:
        fator_novo = (1 + taxa) ** prazo_restante
        pmt_fluxo = saldo_inicial * (taxa * fator_novo) / (fator_novo - 1)
    else:
        pmt_fluxo = pmt_limite

    while saldo > 0.01 and meses_decorridos < 600:  # Trava de segurança de 50 anos
        meses_decorridos += 1
        juros_mes = saldo * taxa
        
        # Garante que a parcela não pague mais do que a dívida restante
        pmt_atual = pmt_fluxo if pmt_fluxo < (saldo + juros_mes) else (saldo + juros_mes)
        amortizacao_mes = pmt_atual - juros_mes
        
        saldo = max(0.0, saldo - amortizacao_mes)
        historico_saldos.append({"Mês": meses_decorridos, "Saldo Devedor": saldo})
        
    return meses_decorridos, pmt_fluxo, historico_saldos

# --- Geração dos Cenários ---
# Cenário A: Contrato Original
prazo_real_orig, pmt_real_orig, saldos_orig = rodar_cronograma(saldo_devedor_atual, pmt_original, taxa_mensal, False)

# Cenário B: Com o abatimento aplicado hoje
saldo_apos_amortizacao = max(0.0, saldo_devedor_atual - valor_amortizar)
is_reduzir_parcela = (tipo_amortizacao == "Prestação")

prazo_real_sim, pmt_real_sim, saldos_sim = rodar_cronograma(
    saldo_apos_amortizacao, pmt_original, taxa_mensal, is_reduzir_parcela
)

# Ajuste do prazo simulado para refletir o contrato atual
if tipo_amortizacao == "Prazo":
    novo_prazo_final = prazo_real_sim
    parcelas_eliminadas = prazo_restante - novo_prazo_final
else:
    novo_prazo_final = prazo_restante
    parcelas_eliminadas = 0

# --- Painel de Resultados (Direita) ---
with col_Painel:
    st.markdown("### 🎯 Resultado da Simulação")
    
    res1, res2 = st.columns(2)
    with res1:
        st.metric("Prazo Atual", f"{prazo_restante} meses")
    with res2:
        st.metric("Novo Prazo", f"{novo_prazo_final} meses", 
                  delta=f"-{parcelas_eliminadas} meses" if parcelas_eliminadas > 0 else None, 
                  delta_color="inverse")
        
    st.markdown("---")
    st.markdown("### 📊 Diagnóstico Financeiro")
    
    # Cálculo de juros por soma real das parcelas simuladas
    juros_totais_orig = (pmt_original * prazo_restante) - saldo_devedor_atual
    if tipo_amortizacao == "Prazo":
        juros_totais_sim = (pmt_original * novo_prazo_final) - saldo_apos_amortizacao
    else:
        j
