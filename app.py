import streamlit as st
import math
import pandas as pd

# Configuração da página em modo Wide para melhor aproveitamento visual
st.set_page_config(page_title="Quantum Amortização - Caixa", layout="wide")

# --- TEXTO DE ESTILO CSS (ISOLADO PARA EVITAR COMPILAÇÃO INCORRETA) ---
Estilo_Futurista = """
<style>
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #e5e7eb;
    }
    h1 {
        color: #00f2fe !important;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.6);
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 2px;
    }
    h3 {
        color: #4facfe !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
        transition: all 0.3s ease-in-out;
    }
    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: #00f2fe;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        transform: translateY(-2px);
    }
    div[data-testid="stMetricValue"] {
        color: #00f2fe !important;
        font-size: 2.2rem !important;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 242, 254, 0.3);
    }
    div[data-testid="stMetricDelta"] > div {
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; text-shadow: 0 0 8px rgba(0, 242, 254, 0.6); }
        100% { opacity: 0.7; }
    }
    .stNumberInput input {
        background-color: #1f2937 !important;
        color: #00f2fe !important;
        border: 1px solid #4facfe !important;
    }
    .stAlert {
        background-color: rgba(79, 172, 254, 0.1) !important;
        border: 1px solid #4facfe !important;
        color: #e5e7eb !important;
    }
</style>
"""

# Injeta o estilo de forma segura na página
st.markdown(Estilo_Futurista, unsafe_allow_html=True)

# --- Cabeçalho do Painel ---
st.title("⚡ QUANTUM AMORTIZAÇÃO")
st.markdown("<p style='color:#4facfe; font-size:1.1rem; margin-top:-15px;'>Módulo de Projeção Dinâmica • Tabela Price</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Interface em Duas Colunas (Inputs à Esquerda, Resultados à Direita) ---
col_menu, col_Painel = st.columns([1, 2], gap="large")

with col_menu:
    st.markdown("### 🎛️ Painel de Controle")
    
    saldo_devedor_atual = st.number_input(
        "⚡ Saldo Devedor Atual (R$)", 
        min_value=0.0, value=327639.45, step=1000.0, format="%.2f"
    )
    
    taxa_anual_input = st.number_input(
        "📈 Taxa de Juros Anual (%)", 
        min_value=0.0, max_value=100.0, value=9.5, step=0.1, format="%.2f"
    )
    
    prazo_restante = st.number_input(
        "⏳ Meses Restantes", 
        min_value=1, max_value=420, value=420, step=1
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧬 Vetor de Amortização")
    
    valor_amortizar = st.number_input(
        "🔮 Quanto deseja injetar?", 
        min_value=0.0, value=2950.00, step=50.0, format="%.2f"
    )
    
    tipo_amortizacao = st.radio(
        "🎯 Diretriz do Algoritmo:",
        ["Prazo", "Prestação"],
        help="Prazo: Derruba o tempo restante. Prestação: Encolhe o boleto mensal."
    )
    
    taxas_somadas = 45.00 + 15.00 + 25.00  # Encargos padrão (MIP + DFI + Adm)

# --- Mecanismo de Cálculo de Fluxo ---
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
        try:
            termo_log = 1 - (novo_saldo * taxa_mensal)
