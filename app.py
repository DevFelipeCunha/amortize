import streamlit as st
import math
import pandas as pd

# Configuração da página em modo Wide para melhor aproveitamento visual
st.set_page_config(page_title="Quantum Amortização - Caixa", layout="wide")

# --- INJEÇÃO DE CSS FUTURISTA (CYBERPUNK / SCI-FI) ---
st.markdown("""
<style>
    /* Fundo geral escuro com gradiente dinâmico sutil */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #e5e7eb;
    }
    
    /* Customização dos Títulos com efeito de Brilho Neon */
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
    
    /* Efeito de Vidro (Glassmorphic) nos blocos de menu e painéis */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
        transition: all 0.3s ease-in-out;
    }
    
    /* Movimento/Dinamismo: Efeito flutuante ao passar o mouse nos blocos */
    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: #00f2fe;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        transform: translateY(-2px);
    }
    
    /* Customização dos Cards de Métricas (Métricas de Impacto) */
    div[data-testid="stMetricValue"] {
        color: #00f2fe !important;
        font-size: 2.2rem !important;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 242, 254, 0.3);
    }
    
    /* Animação de pulso dinâmico para as reduções (Delta positivo/negativo) */
    div[data-testid="stMetricDelta"] > div {
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; text-shadow: 0 0 8px rgba(0,
        
