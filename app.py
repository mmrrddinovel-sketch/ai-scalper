import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Элитный интерфейс
st.set_page_config(page_title="ELITE QUANT CORE", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #050505;}
    h1 {color: #ffd700; text-align: center; text-transform: uppercase; letter-spacing: 2px;}
    .stMetric {background: #111; padding: 15px; border-left: 4px solid #ffd700;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ ELITE QUANTUM SCALPER")

# Выбор котировок (включая Spot Gold XAU/USD)
asset = st.selectbox("ВЫБОР АКТИВА:", ["XAUUSD=X", "GC=F", "EURUSD=X", "BTC-USD"])

@st.cache_data(ttl=2) # Минимально возможный кеш для скорости
def get_fast_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df['Close']
    except: return None

if st.button("🚀 EXECUTE QUANT ANALYSIS"):
    data = get_fast_data(asset)
    
    if data is not None and len(data) > 30:
        price = float(data.iloc[-1])
        
        # 1. Профессиональный ИИ: Трендовый анализ (EMA)
        f_ema = data.ewm(span=5).mean().iloc[-1]
        s_ema = data.ewm(span=20).mean().iloc[-1]
        
        # 2. Хакерский ИИ: Z-Score (выявление ценовых аномалий)
        std = data.iloc[-30:].std()
        mean = data.iloc[-30:].mean()
        z_score = (price - mean) / (std + 1e-9)
        
        # 3. Решающее правило (Ансамбль ИИ)
        st.metric("CURRENT PRICE", f"{price:.4f}")
        
        col1, col2 = st.columns(2)
        
        # Логика: Вход в сделку при подтверждении тренда ИИ и аномалии волатильности
        if z_score < -1.5 and f_ema > s_ema:
            st.markdown("<h2 style='color:#00ff00;'>🟢 BUY SIGNAL: QUANTUM APPROVED</h2>", unsafe_allow_html=True)
            st.write("Статус: Оптимизированный вход (Anomaly Detected)")
        elif z_score > 1.5 and f_ema < s_ema:
            st.markdown("<h2 style='color:#ff4b4b;'>🔴 SELL SIGNAL: QUANTUM APPROVED</h2>", unsafe_allow_html=True)
            st.write("Статус: Оптимизированный вход (Anomaly Detected)")
        else:
            st.warning("🟡 QUANTUM CORE: СИГНАЛ НЕ ПОДТВЕРЖДЕН (Ожидание аномалии)")
            
    else:
        st.error("QUANTUM CORE: ОШИБКА ДАННЫХ (НЕТ ЛАТЕНТНОСТИ)")
