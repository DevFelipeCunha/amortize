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
    
    saldo_devedor_atual = st.number_
