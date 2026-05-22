import streamlit as st
import requests
import math
import pandas as pd

# Configuração da URL do seu Apps Script publicado
GAS_URL = "SUA_URL_DO_GOOGLE_APPS_SCRIPT_AQUI"

st.set_page_config(page_title="Simulador de Amortização Caixa - Price", layout="centered")
st.title("🏠 Simulador de Amortização Imobiliária")
st.subheader("Padrão Caixa Habitação (Tabela Price)")

# --- BUSCA AUTOMÁTICA DOS DADOS (GOOGLE SHEETS) ---
# Inicializa variáveis com valores padrão de segurança (fallback)
saldo_base = 250000.00
taxa_base = 9.5
prazo_base = 300

try:
    # Tenta conectar com o Google Sheets
    response = requests.get(GAS_URL, timeout=5)
    if response.status_code == 200:
        data = response.json()
        saldo_base = float(data["saldoDevedor"])
        taxa_base = float(data["taxaJurosAnual"])
        prazo_base = int(data["mesesRestantes"])
        st.success("🔄 Dados sincronizados com o Google Sheets com sucesso!")
except Exception as e:
    st.sidebar.warning("⚠️ Executando localmente: Não foi possível conectar ao Google Sheets (Usando valores padrão).")

# --- CRIAÇÃO DOS CAMPOS NA PÁGINA ---
st.markdown("### 📋 Configuração do Contrato")
st.caption("Altere os valores abaixo para ajustar o saldo puxado da planilha ou simular do zero:")

# Organiza os campos lado a lado em 3 colunas
c1, c2, c3 = st.columns(3)

with c1:
    saldo_devedor_atual = st.number_input(
        "Saldo Devedor Atual (R$)", 
        min_value=0.0, 
        value=saldo_base, 
        step=1000.0,
        format="%.2f"
    )

with c2:
    taxa_anual_input = st.number_input(
        "Taxa de Juros Anual (%)", 
        min_value=0.0, 
        max_value=100.0, 
        value=taxa_base, 
        step=0.1,
        format="%.2f"
    )

with c3:
    prazo_restante = st.number_input(
        "Meses Restantes", 
        min_value=1, 
        max_value=420, 
        value=prazo_base, 
        step=1
    )

# Transforma a taxa percentual em decimal para os cálculos matemáticos
taxa_anual = taxa_anual_input / 100
taxa_mensal = taxa_anual / 12

# --- CÁLCULO DA PARCELA CONTRATUAL PRICE ---
fator_potencia = (1 + taxa_mensal) ** prazo_restante
parcela_fixa = saldo_devedor_atual * (taxa_mensal * fator_potencia) / (fator_potencia - 1)

# Painel Informativo Resumido
st.info(f"Sua parcela fixa calculada para este cenário é de: **R$ {parcela_fixa:,.2f}**")
st.markdown("---")

# --- ÁREA DE SIMULAÇÃO DE AMORTIZAÇÃO ---
st.markdown("### 📉 Simular Desconto no Prazo")
valor_amortizar = st.number_input("Quanto você deseja amortizar hoje?", min_value=0.0, step=500.0, value=5000.0)

# Função para gerar a evolução do saldo devedor mês a mês
def gerar_evolucao_price(saldo_inicial, pmt, taxa, meses):
    saldo = saldo_inicial
    historico = []
    for mes in range(1, meses + 1):
        juros_mes = saldo * taxa
        amortizacao_mes = pmt - juros_mes
        
        if saldo - amortizacao_mes < 0 or mes == meses:
            amortizacao_mes = saldo
            saldo = 0.0
        else:
            saldo -= amortizacao_mes
            
        historico.append({
            "Mês": mes,
            "Parcela": pmt,
            "Amortização": amortizacao_mes,
            "Juros": juros_mes,
            "Saldo Devedor": max(0.0, saldo)
        })
        if saldo <= 0:
            break
    return pd.DataFrame(historico)

if valor_amortizar > 0:
    if valor_amortizar >= saldo_devedor_atual:
        st.success("🎉 Com este valor você quita integralmente o saldo devedor!")
    else:
        # Lógica de amortização Price (Prazo)
        novo_saldo = saldo_devedor_atual - valor_amortizar
        
        try:
            termo_log = 1 - (novo_saldo * taxa_mensal) / parcela_fixa
            
            if termo_log > 0:
                novo_prazo_estimado = -math.log(termo_log) / math.log(1 + taxa_mensal)
                novo_prazo_estimado = round(novo_prazo_estimado)
                parcelas_deletadas = prazo_restante - novo_prazo_estimado
                
                # Exibição do impacto imediato
                st.markdown("#### 🎯 Resultado da Simulação")
                res1, res2 = st.columns(2)
                with res1:
                    st.markdown(f"### 🛑 Eliminadas: **{max(0, parcelas_deletadas)} parcelas**")
                    st.caption("Meses poupados do final do seu contrato.")
                with res2:
                    st.markdown(f"### ⏳ Novo Prazo: **{novo_prazo_estimado} meses**")
                    st.caption(f"Seu contrato cai de {prazo_restante} para {novo_prazo_estimado} meses.")
                
                # --- GERANDO GRÁFICO E TABELA ---
                df_original = gerar_evolucao_price(saldo_devedor_atual, parcela_fixa, taxa_mensal, prazo_restante)
                df_simulado = gerar_evolucao_price(novo_saldo, parcela_fixa, taxa_mensal, novo_prazo_estimado)
                
                st.markdown("### 📈 Curva de Queda da Dívida")
                df_grafico = pd.DataFrame(index=range(1, prazo_restante + 1))
                df_grafico["Fluxo Original"] = df_original.set_index("Mês")["Saldo Devedor"]
                df_grafico["Com Amortização"] = df_simulado.set_index("Mês")["Saldo Devedor"]
                df_grafico.fillna(0, inplace=True)
                
                st.line_chart(df_grafico)

                st.markdown("### 📋 Projeção Detalhada Mês a Mês (Novo Cenário)")
                df_visual = df_simulado.copy()
                df_visual["Parcela"] = df_visual["Parcela"].map("R$ {:,.2f}".format)
                df_visual["Amortização"] = df_visual["Amortização"].map("R$ {:,.2f}".format)
                df_visual["Juros"] = df_visual["Juros"].map("R$ {:,.2f}".format)
                df_visual["Saldo Devedor"] = df_visual["Saldo Devedor"].map("R$ {:,.2f}".format)
                
                st.dataframe(df_visual, use_container_width=True, hide_index=True)
                
            else:
                st.error("O valor inserido é muito alto para a estrutura de parcelas atual.")
        except Exception as e:
            st.error("Erro no recálculo financeiro. Revise os dados de entrada.")
