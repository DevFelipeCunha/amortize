import streamlit as st
import math
import pandas as pd
import io

st.set_page_config(page_title="Super Simulador Imobiliário - Price", layout="wide")
st.title("🏠 Super Simulador de Amortização Imobiliária")
st.subheader("Modelo Avançado: Padrão Caixa Habitação com Tabela Price")

# --- Interface em Duas Colunas (Configurações à Esquerda, Resultados à Direita) ---
col_menu, col_Painel = st.columns([1, 2], gap="large")

with col_menu:
    st.markdown("### 📋 1. Configuração do Contrato")
    
    saldo_devedor_atual = st.number_input(
        "Saldo Devedor Atual (R$)", 
        min_value=0.0, value=326900.00, step=5000.0, format="%.2f"
    )
    
    taxa_anual_input = st.number_input(
        "Taxa de Juros Anual (%)", 
        min_value=0.0, max_value=100.0, value=10.0, step=0.1, format="%.2f"
    )
    
    prazo_restante = st.number_input(
        "Meses Restantes", 
        min_value=1, max_value=420, value=420, step=1
    )
    
    st.markdown("#### 🛡️ Taxas e Seguros Mensais")
    st.caption("A Caixa embuti estes valores fixos/proporcionais na sua parcela real:")
    
    seguro_mip = st.number_input("Seguro MIP (Morte/Invalidez) - R$", min_value=0.0, value=45.00, step=5.0)
    seguro_dfi = st.number_input("Seguro DFI (Danos ao Imóvel) - R$", min_value=0.0, value=15.00, step=5.0)
    taxa_adm = st.number_input("Taxa de Administração - R$", min_value=0.0, value=25.00, step=5.0)
    
    taxas_somadas = seguro_mip + seguro_dfi + taxa_adm

    st.markdown("---")
    st.markdown("### 📉 2. Estratégia de Amortização")
    
    tipo_amortizacao = st.radio(
        "Onde aplicar a amortização?",
        ["Reduzir o Prazo (Tempo)", "Reduzir a Parcela (Valor mensal)"]
    )
valor_amortizar_hoje = st.number_input(
        "Aporte Único Hoje (R$)", 
        min_value=0.0, value=5000.0, step=500.0, format="%.2f"
    )
    
    # CORREÇÃO AQUI: Passamos a explicação para o argumento 'help'
    valor_recorrente_mes = st.number_input(
        "Aporte Mensal Recorrente (R$)",
        help="Valor extra que pretende pagar todo mês além da parcela",
        min_value=0.0, value=500.0, step=100.0, format="%.2f"
    )
# --- Processamento Matemático ---
taxa_mensal = (taxa_anual_input / 100) / 12

def simular_fluxo(saldo_ini, meses_limite, pmt_base, taxa, aporte_unico, aporte_recorrente, modo):
    saldo = saldo_ini
    historico = []
    
    # Aplica o aporte único imediatamente no saldo inicial
    if aporte_unico > 0:
        saldo = max(0.0, saldo - aporte_unico)
        
    for mes in range(1, meses_limite + 1):
        if saldo <= 0:
            break
            
        juros_mes = saldo * taxa
        
        # No modo "Reduzir Parcela", a PMT é recalculada todo mês com base no novo saldo e prazo restante
        if modo == "Reduzir a Parcela (Valor mensal)":
            meses_faltantes = meses_limite - mes + 1
            if meses_faltantes > 0 and saldo > 0:
                fator = (1 + taxa) ** meses_faltantes
                pmt_atual = saldo * (taxa * fator) / (fator - 1)
            else:
                pmt_atual = saldo + juros_mes
        else:
            pmt_atual = pmt_base
            
        amortizacao_tabela = pmt_atual - juros_mes
        
        # Amortização extra daquele mês
        extra = aporte_recorrente if saldo > (amortizacao_tabela + juros_mes) else 0.0
        
        total_amortizado_mes = amortizacao_tabela + extra
        
        if saldo - total_amortizado_mes <= 0:
            total_amortizado_mes = saldo
            pmt_final = total_amortizado_mes + juros_mes
            saldo = 0.0
            historico.append({
                "Mês": mes, "Parcela Pura": pmt_final, "Taxas/Seguros": taxas_somadas,
                "Total Pago": pmt_final + taxas_somadas, "Amortização Real": total_amortizado_mes,
                "Juros": juros_mes, "Saldo Devedor": 0.0
            })
            break
        else:
            saldo -= total_amortizado_mes
            
        historico.append({
            "Mês": mes, "Parcela Pura": pmt_atual, "Taxas/Seguros": taxas_somadas,
            "Total Pago": pmt_atual + taxas_somadas, "Amortização Real": total_amortizado_mes,
            "Juros": juros_mes, "Saldo Devedor": saldo
        })
        
    return pd.DataFrame(historico)

# Cálculo do Cenário Original (Sem amortizações)
if saldo_devedor_atual > 0 and prazo_restante > 0:
    fator_orig = (1 + taxa_mensal) ** prazo_restante
    pmt_original = saldo_devedor_atual * (taxa_mensal * fator_orig) / (fator_orig - 1)
else:
    pmt_original = 0.0

df_original = simular_fluxo(saldo_devedor_atual, prazo_restante, pmt_original, taxa_mensal, 0, 0, "Prazo")
df_simulado = simular_fluxo(saldo_devedor_atual, prazo_restante, pmt_original, taxa_mensal, valor_amortizar_hoje, valor_recorrente_mes, tipo_amortizacao)

# --- Painel de Resultados (Direita) ---
with col_Painel:
    st.markdown("### 📊 3. Diagnóstico e Comparação de Cenários")
    
    # 1. Indicadores de Economia Real
    juros_total_original = df_original["Juros"].sum()
    juros_total_simulado = df_simulado["Juros"].sum()
    economia_juros = juros_total_original - juros_total_simulado
    
    prazo_final_simulado = len(df_simulado)
    meses_poupados = len(df_original) - prazo_final_simulado
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Parcelas Eliminadas", f"{max(0, meses_poupados)} meses", help="Tempo cortado do seu financiamento")
    m2.metric("Economia Real de Juros", f"R$ {economia_juros:,.2f}", delta="Dinheiro que fica no seu bolso", delta_color="inverse")
    m3.metric("Novo Prazo de Quitação", f"{prazo_final_simulado} meses", f"Antes: {prazo_restante} meses")
    
    st.info(f"📋 **Boleto Caixa Inicial:** Sua parcela total começa em **R$ {pmt_original + taxas_somadas:,.2f}** "
            f"(Sendo R$ {pmt_original:,.2f} da Price pura + R$ {taxas_somadas:,.2f} de encargos/seguros).")
    
    st.markdown("---")
    
    # 2. Gráfico de Evolução Comparativo
    st.markdown("### 📈 Curva de Descolamento da Dívida")
    df_grafico = pd.DataFrame(index=range(1, prazo_restante + 1))
    df_grafico["Contrato Original"] = df_original.set_index("Mês")["Saldo Devedor"]
    df_grafico["Estratégia Simulada"] = df_simulado.set_index("Mês")["Saldo Devedor"]
    df_grafico.fillna(0, inplace=True)
    st.line_chart(df_grafico)
    
    st.markdown("---")
    
    # 3. Tabela Dinâmica e Botão de Exportação
    st.markdown("### 📋 Projeção Detalhada com a Nova Estratégia")
    
    # Preparando arquivo Excel em memória para download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_simulado.to_excel(writer, index=False, sheet_name="Nova_Projeção_Price")
    buffer.seek(0)
    
    st.download_button(
        label="📥 Exportar Projeção para o Excel",
        data=buffer,
        file_name="simulacao_amortizacao_caixa.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Formatação visual da tabela na tela
    df_visual = df_simulado.copy()
    for col in ["Parcela Pura", "Taxas/Seguros", "Total Pago", "Amortização Real", "Juros", "Saldo Devedor"]:
        df_visual[col] = df_visual[col].map("R$ {:,.2f}".format)
        
    st.dataframe(df_visual, use_container_width=True, hide_index=True)
