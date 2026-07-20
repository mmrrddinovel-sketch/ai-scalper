import streamlit as st
import yfinance as yf
import pandas as pd
import time
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

st.set_page_config(page_title="ELITE LIVE SCALPER", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #ffd700;}</style>", unsafe_allow_html=True)

st.title("⚡ ELITE LIVE QUANTUM SCALPER")

assets = {"GOLD (XAUUSD)": "GC=F", "EUR/USD": "EURUSD=X", "BITCOIN": "BTC-USD"}

with st.sidebar:
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ИИ-АНАЛИТИК:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("ВВЕДИТЕ API КЛЮЧ:", type="password")

# Место для живой цены
price_placeholder = st.empty()

def get_live_data(symbol):
    try:
        # Используем минимальный интервал для получения свежих данных
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        if not data.empty:
            price = float(data['Close'].iloc[-1].item() if hasattr(data['Close'].iloc[-1], 'item') else data['Close'].iloc[-1])
            return price
    except: return None
    return None

# Основной цикл обновления
while True:
    price = get_live_data(ticker)
    if price:
        with price_placeholder.container():
            st.metric(f"LIVE PRICE ({selected_name})", f"{price:,.2f}")
            
            # Быстрая визуализация сигнала
            st.subheader("SIGNAL: MONITORING...")
    
    time.sleep(5) # Авто-обновление каждые 5 секунд (минимально допустимое для yfinance)
    st.rerun()
