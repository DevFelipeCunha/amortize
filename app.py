import streamlit as st
import requests
import math

# Configuração da URL do seu Apps Script publicado
GAS_URL = "SUA_URL_DO_GOOGLE_APPS_SCRIPT_AQUI"

st.set_page_config(page_title="Simulador de Amortização Caixa - Price", layout="centered")
st.title("🏠 Simulador de Amortização Imobiliária")
st.subheader("Padrão Caixa Habitação (Tabela Price)")

# Busca dados do Google Sheets
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

# Na Price imobiliária, a taxa mensal é calculada de forma proporcional (taxa anual / 12)
taxa_mensal = taxa_anual / 12

# Cálculo da Parcela Fixa Atual (Fórmula da Tabela Price)
# PMT = PV * [i * (1 + i)^n] / [(1 + i)^n - 1]
fator_potencia = (1 + taxa_mensal) ** prazo_restante
parcela_fixa = saldo_devedor_atual * (taxa_mensal * fator_potencia) / (fator_potencia - 1)

# Exibição dos Dados Atuais
st.markdown("### 📊 Resumo Atual do Contrato (Price)")
col1, col2, col3 = st.columns(3)
col1.metric("Saldo Devedor", f"R$ {saldo_devedor_atual:,.2f}")
col2.metric("Prazo Restante", f"{prazo_restante} meses")
col3.metric("Taxa de Juros", f"{taxa_anual*100:.2f}% a.a.")

juros_primeiro_mes = saldo_devedor_atual * taxa_mensal
amortizacao_primeiro_mes = parcela_fixa - juros_primeiro_mes

st.info(
    f"Sua parcela fixa contratual (sem seguros/taxas) é de: **R$ {parcela_fixa:,.2f}**\n\n"
    f"👉 Na próxima parcela: **R$ {juros_primeiro_mes:,.2f}** serão apenas juros e **R$ {amortizacao_primeiro_mes:,.2f}** vão reduzir sua dívida."
)

st.markdown("---")

# Área de Simulação
st.markdown("### 📉 Simular Desconto no Prazo")
valor_amortizar = st.number_input("Quanto você deseja amortizar?", min_value=0.0, step=500.0, value=5000.0)

if valor_amortizar > 0:
    if valor_amortizar >= saldo_devedor_atual:
        st.success("🎉 Com este valor você quita integralmente o saldo devedor!")
    else:
        # 1. Novo Saldo Devedor após a amortização extra
        novo_saldo = saldo_devedor_atual - valor_amortizar
        
        # 2. Lógica Price para Redução de Prazo (Mantendo a mesma Parcela Fixa)
        # Vamos isolar o 'n' (prazo) na fórmula da Price:
        # n = -log(1 - (PV * i) / PMT) / log(1 + i)
        try:
            termo_log = 1 - (novo_saldo * taxa_mensal) / parcela_fixa
            
            if termo_log > 0:
                # Calcula o novo prazo exato (em meses fracionados) e arredonda
                novo_prazo_estimado = -math.log(termo_log) / math.log(1 + taxa_mensal)
                novo_prazo_estimado = round(novo_prazo_estimado)
                
                # Parcelas eliminadas lá do final do contrato
                parcelas_deletadas = prazo_restante - novo_prazo_estimado
                
                # Exibição dos Resultados
                st.markdown("#### 🎯 Resultado da Simulação")
                
                res1, res2 = st.columns(2)
                with res1:
                    st.markdown(f"### 🛑 Eliminadas: **{max(0, parcelas_deletadas)} parcelas**")
                    st.caption("Meses riscados do final do seu contrato.")
                with res2:
                    st.markdown(f"### ⏳ Novo Prazo: **{novo_prazo_estimado} meses**")
                    st.caption(f"Seu tempo de contrato cai de {prazo_restante} para {novo_prazo_estimado} meses.")
                
                st.success(
                    f"💡 **Vantagem da Price:** Como você reduziu o saldo devedor e manteve o valor da parcela em **R$ {parcela_fixa:,.2f}**, "
                    f"a partir do mês que vem a sua amortização real por parcela será muito maior, acelerando ainda mais o fim da dívida!"
                )
            else:
                st.error("O valor amortizado gera uma inconsistência matemática para o valor da parcela atual. O saldo devedor ficou baixo demais para essa estrutura.")
        except Exception as e:
            st.error("Erro ao calcular o novo prazo. Verifique os valores informados.")
