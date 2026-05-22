import streamlit as st
import math
import pandas as pd

# 1. Configuração inicial da página
st.set_page_config(page_title="Simulador Caixa Habitação", layout="wide")
st.title("🏠 Simulador de Amortização Imobiliária")
st.subheader("Padrão App Caixa Habitação (Tabela Price)")

# 2. Interface em duas colunas (Inputs à esquerda, Resultados à direita)
col_menu, col_Painel = st.columns([1, 2], gap="large")

with col_menu:
    st.markdown("### 📋 Configuração do Contrato")
    
    saldo_devedor_atual = st.number_input(
        "Saldo Devedor Atual (R$)", 
        min_value=0.0, value=327639.45, step=1000.0, format="%.2f"
    )
    
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
    
    valor_amortizar = st.number_input(
        "Quanto você gostaria de amortizar?", 
        min_value=0.0, value=2950.00, step=50.0, format="%.2f"
    )
    
    tipo_amortizacao = st.radio(
        "Qual tipo de amortização?",
        ["Prazo", "Prestação"],
        help="Prazo: Diminui o número de prestações restantes. Prestação: Diminui o valor mensal."
    )
    
    taxas_somadas = 45.00 + 15.00 + 25.00  # MIP + DFI + Taxa Adm

# 3. Processamento Matemático Seguro
taxa_mensal = (taxa_anual_input / 100) / 12

if saldo_devedor_atual > 0 and prazo_restante > 0:
    fator_orig = (1 + taxa_mensal) ** prazo_restante
    pmt_original = saldo_devedor_atual * (taxa_mensal * fator_orig) / (fator_orig - 1)
else:
    pmt_original = 0.0

novo_saldo = max(0.0, saldo_devedor_atual - valor_amortizar)
novo_prazo_estimado = prazo_restante
nova_pmt = pmt_original

if valor_amortizar > 0 and pmt_original > 0:
    if tipo_amortizacao == "Prazo":
        termo_log = 1 - (novo_saldo * taxa_mensal) / pmt_original
        if termo_log > 0:
            novo_prazo_estimado = -math.log(termo_log) / math.log(1 + taxa_mensal)
            novo_prazo_estimado = round(novo_prazo_estimado)
        else:
            novo_prazo_estimado = 0
    else:
        fator_novo = (1 + taxa_mensal) ** prazo_restante
        nova_pmt = novo_saldo * (taxa_mensal * fator_novo) / (fator_novo - 1)

parcelas_eliminadas = prazo_restante - novo_prazo_estimado

# 4. Função para alimentar o gráfico
def gerar_saldos_grafico(saldo_ini, meses, pmt_base, taxa):
    saldo = saldo_ini
    historico = []
    for mes in range(1, meses + 1):
        if saldo <= 0: 
            break
        juros_mes = saldo * taxa
        pmt_atual = pmt_base if pmt_base < (saldo + juros_mes) else (saldo + juros_mes)
        amortizacao_tabela = pmt_atual - juros_mes
        saldo = max(0.0, saldo - amortizacao_tabela)
        historico.append({"Mês": mes, "Saldo Devedor": saldo})
    return pd.DataFrame(historico)

df_original = gerar_saldos_grafico(saldo_devedor_atual, prazo_restante, pmt_original, taxa_mensal)
df_simulado = gerar_saldos_grafico(novo_saldo, novo_prazo_estimado, nova_pmt, taxa_mensal)

# 5. Painel de Resultados (Direita)
with col_Painel:
    st.markdown("### 🎯 Resultado da Simulação")
