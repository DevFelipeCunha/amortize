import streamlit as st
import requests
import math
import pandas as pd

# Configuração da URL do seu Apps Script publicado
GAS_URL = "SUA_URL_DO_GOOGLE_APPS_SCRIPT_AQUI"

st.set_page_config(page_title="Simulador de Amortização Caixa - Price", layout="centered")
st.title("🏠 Simulador de Amortização Imobiliária")
st.subheader("Padrão Caixa Habitação (Tabela Price)")

# Cole o link gerado pelo Google aqui dentro das aspas:
GAS_URL = "https://script.google.com/macros/s/AKfycbzXx2WeQveDsS5exaxf3Lf0yoHROr4TyKHAUE32b6LcgQT8CLHKhTNlFEOVcwh-WL_dgg/exec"
# 1. Busca dados do Google Sheets
try:
    response = requests.get(GAS_URL)
    data = response.json()
    
    saldo_devedor_atual = float(data["saldoDevedor"])
    taxa_anual = float(data["taxaJurosAnual"]) / 100
    prazo_restante = int(data["mesesRestantes"])
except Exception as e:
    st.error("Não foi possível carregar os dados do Google Sheets. Usando valores genéricos para teste.")
    saldo_devedor_atual = 250000.00
    taxa_anual = 0.095  # 9.5% a.a.
    prazo_restante = 300

# Taxa mensal proporcionalizada usada no imobiliário
taxa_mensal = taxa_anual / 12

# Cálculo da Parcela Fixa Atual (Fórmula da Tabela Price)
fator_potencia = (1 + taxa_mensal) ** prazo_restante
parcela_fixa = saldo_devedor_atual * (taxa_mensal * fator_potencia) / (fator_potencia - 1)

# Exibição dos Dados Atuais
st.markdown("### 📊 Resumo Atual do Contrato (Price)")
col1, col2, col3 = st.columns(3)
col1.metric("Saldo Devedor", f"R$ {saldo_devedor_atual:,.2f}")
col2.metric("Prazo Restante", f"{prazo_restante} meses")
col3.metric("Taxa de Juros", f"{taxa_anual*100:.2f}% a.a.")

st.info(f"Sua parcela fixa contratual (sem seguros/taxas) é de: **R$ {parcela_fixa:,.2f}**")
st.markdown("---")

# 2. Área de Simulação
st.markdown("### 📉 Simular Desconto no Prazo")
valor_amortizar = st.number_input("Quanto você deseja amortizar hoje?", min_value=0.0, step=500.0, value=5000.0)

# Função auxiliar para gerar a evolução do saldo devedor mês a mês
def gerar_evolucao_price(saldo_inicial, pmt, taxa, meses):
    saldo = saldo_inicial
    historico = []
    for mes in range(1, meses + 1):
        juros_mes = saldo * taxa
        amortizacao_mes = pmt - juros_mes
        
        # Evita pequenos resíduos de ponto flutuante no último mês
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
                
                # --- GERAÇÃO DOS DADOS DE EVOLUÇÃO ---
                # Linha do tempo Sem Amortização
                df_original = gerar_evolucao_price(saldo_devedor_atual, parcela_fixa, taxa_mensal, prazo_restante)
                # Linha do tempo Com Amortização
                df_simulado = gerar_evolucao_price(novo_saldo, parcela_fixa, taxa_mensal, novo_prazo_estimado)
                
                # 3. Gráfico de Comparação do Saldo Devedor
                st.markdown("### 📈 Curva de Queda da Dívida")
                
                # Unificando os dados para plotar no gráfico do Streamlit
                df_grafico = pd.DataFrame(index=range(1, prazo_restante + 1))
                df_grafico["Fluxo Original"] = df_original.set_index("Mês")["Saldo Devedor"]
                df_grafico["Com Amortização"] = df_simulado.set_index("Mês")["Saldo Devedor"]
                df_grafico.fillna(0, inplace=True) # Zera o saldo após o término no simulado
                
                st.line_chart(df_grafico)
                st.caption("O gráfico mostra como a sua dívida chega a zero muito mais rápido (linha vermelha/abaixo) se comparado ao contrato original.")

                # 4. Tabela Dinâmica Detalhada
                st.markdown("### 📋 Projeção Detalhada Mês a Mês (Novo Cenário)")
                st.caption("Veja como se comportará cada parcela daqui para frente:")
                
                # Formatando a tabela para exibição amigável em Real (R$)
                df_visual = df_simulado.copy()
                df_visual["Parcela"] = df_visual["Parcela"].map("R$ {:,.2f}".format)
                df_visual["Amortização"] = df_visual["Amortização"].map("R$ {:,.2f}".format)
                df_visual["Juros"] = df_visual["Juros"].map("R$ {:,.2f}".format)
                df_visual["Saldo Devedor"] = df_visual["Saldo Devedor"].map("R$ {:,.2f}".format)
                
                st.dataframe(df_visual, use_container_width=True, hide_index=True)
                
            else:
                st.error("O valor inserido é incompatível com a estrutura de parcelas atual.")
        except Exception as e:
            st.error("Erro no recálculo financeiro. Revise os dados de entrada.")
