import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Simulador Caixa Habitação", layout="wide")
st.title("🏠 Simulador de Amortização Imobiliária")
st.subheader("Fiel ao Padrão do App Caixa Habitação (Tabela Price)")

# --- Interface em Duas Colunas (Inputs à Esquerda, Resultados à Direita) ---
col_menu, col_Painel = st.columns([1, 2], gap="large")

with col_menu:
    st.markdown("### 📋 Configuração do Contrato")
    
    # Alimentado com os dados exatos da imagem enviada
    saldo_devedor_atual = st.number_input(
        "Saldo Devedor Atual (R$)", 
        min_value=0.0, value=327639.45, step=1000.0, format="%.2f"
    )
    
    # Assumindo uma taxa média praticada pela Caixa em contratos novos (ex: 9.5% a.a.)
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
    
    # Seguros e taxas médias em background para compor a parcela real da Caixa
    taxas_somadas = 45.00 + 15.00 + 25.00  # MIP + DFI + Taxa Adm

# --- Processamento Matemático ---
taxa_mensal = (taxa_anual_input / 100) / 12

# 1. Cálculo da Parcela Original
if saldo_devedor_atual > 0 and prazo_restante > 0:
    fator_orig = (1 + taxa_mensal) ** prazo_restante
    pmt_original = saldo_devedor_atual * (taxa_mensal * fator_orig) / (fator_orig - 1)
else:
    pmt_original = 0.0

# 2. Lógica de Amortização
novo_saldo = max(0.0, saldo_devedor_atual - valor_amortizar)

# Inicializa variáveis do novo cenário
novo_prazo_estimado = prazo_restante
nova_pmt = pmt_original

if valor_amortizar > 0 and pmt_original > 0:
    if tipo_amortizacao == "Prazo":
        # Mantém a prestação original e calcula o novo tempo necessário para zerar o novo saldo
        try:
            termo_log = 1 - (novo_saldo * taxa_mensal) / pmt_original
            if termo_log > 0:
                novo_prazo_estimado = -math.log(termo_log) / math.log(1 + taxa_mensal)
                novo_prazo_estimado = round(novo_prazo_estimado)
            else:
                novo_prazo_estimado = 0
        except:
            novo_prazo_estimado = 0
    else:
        # Reduzir Prestação: Mantém o tempo (prazo) e recalcula o valor da parcela para o novo saldo
        fator_novo = (1 + taxa_mensal) ** prazo_restante
        nova_pmt = novo_saldo * (taxa_mensal * fator_novo) / (fator_novo - 1)

parcelas_eliminadas = prazo_restante - novo_prazo_estimado

# Função simplificada apenas para alimentar o gráfico de linha com segurança
def gerar_saldos_grafico(saldo_ini, meses, pmt_base, taxa):
    saldo = saldo_ini
    historico = []
    for mes in range(1, meses + 1):
        if saldo <= 0: break
        juros_mes = saldo * taxa
        pmt_atual = pmt_base if pmt_base < (saldo + juros_mes) else (saldo + juros_mes)
        amortizacao_tabela = pmt_atual - juros_mes
        saldo = max(0.0, saldo - amortizacao_tabela)
        historico.append({"Mês": mes, "Saldo Devedor": saldo})
    return pd.DataFrame(historico)

# Gera dados para o gráfico de linhas
df_original = gerar_saldos_grafico(saldo_devedor_atual, prazo_restante, pmt_original, taxa_mensal)
df_simulado = gerar_saldos_grafico(novo_saldo, novo_prazo_estimado, nova_pmt, taxa_mensal)

# --- Painel de Resultados (Direita) ---
with col_Painel:
    st.markdown("### 🎯 Resultado da Simulação")
    
    res1, res2 = st.columns(2)
    with res1:
        st.metric("Prazo Atual", f"{prazo_restante} meses")
    with res2:
        st.metric("Novo Prazo", f"{novo_prazo_estimado} meses", 
                  delta=f"-{parcelas_eliminadas} meses" if parcelas_eliminadas > 0 else None, 
                  delta_color="inverse")
        
    st.markdown("---")
    st.markdown("### 📊 Diagnóstico Financeiro")
    
    # Estimativa simples de economia de juros baseada no saldo e prestações
    juros_estimados_orig = (pmt_original * prazo_restante) - saldo_devedor_atual
    juros_estimados_sim = (nova_pmt * novo_prazo_estimado) - novo_saldo
    economia_juros = max(0.0, juros_estimados_orig - juros_estimados_sim)
    
    m1, m2 = st.columns(2)
    m1.metric("Próxima Parcela Total", f"R$ {nova_pmt + taxas_somadas:,.2f}", 
              delta=f"R$ {(nova_pmt - pmt_original):,.2f}" if tipo_amortizacao == "Prestação" else None,
              delta_color="inverse")
    m2.metric("Economia Estimada de Juros", f"R$ {economia_juros:,.2f}")
    
    st.info(f"📋 **Nota sobre encargos:** O valor da parcela inclui uma estimativa de R$ {taxas_somadas:,.2f} referente a seguros (MIP/DFI) e taxa de administração de contrato da Caixa.")
    
    # Gráfico de Evolução
    st.markdown("---")
    st.markdown("### 📈 Curva de Queda da Dívida")
    
    if not df_original.empty:
        df_grafico = pd.DataFrame(index=range(1, prazo_restante + 1))
        df_grafico["Contrato Original"] = df_original.set_index("Mês")["Saldo Devedor"]
        if not df_simulado.empty:
            df_grafico["Com Amortização"] = df_simulado.set_index("Mês")["Saldo Devedor"]
        df_grafico.fillna(0, inplace=True)
        st.line_chart(df_grafico)
    else:
        st.caption("Insira os dados do contrato para renderizar o gráfico.")
