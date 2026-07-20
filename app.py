import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Elite Scalper Pro", layout="centered")
st.markdown("<h1 style='text-align: center; color: #ffd700;'>⚡ ELITE SPOT SCALPER</h1>", unsafe_allow_html=True)

# Использование тикера XAUUSD=X для спотового золота
ticker = "XAUUSD=X"

@st.cache_data(ttl=5)
def get_data(t):
    try:
        # Берем M5, так как у вас на скрине график M5
        df = yf.download(t, period="2d", interval="5m", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df['Close']
    except: return None

if st.button("🚀 ЗАПУСТИТЬ ИИ-АНАЛИЗ (SPOT)"):
    data = get_data(ticker)
    if data is not None and len(data) > 20:
        price = float(data.iloc[-1])
        
        # Индикатор импульса (Momentum)
        momentum = data.iloc[-1] - data.iloc[-5]
        # EMA для тренда
        ema_f = data.ewm(span=5).mean().iloc[-1]
        ema_s = data.ewm(span=20).mean().iloc[-1]
        
        st.metric("Цена SPOT GOLD (XAU/USD)", f"{price:.2f}")
        
        # Хакерская логика: ИИ-фильтр по импульсу и тренду
        if momentum > 0 and ema_f > ema_s:
            st.markdown("<h2 style='text-align: center; color: #00ff00;'>🟢 СИГНАЛ: BUY</h2>", unsafe_allow_html=True)
            st.info("Импульс подтвержден: Цена растет и выше EMA.")
        elif momentum < 0 and ema_f < ema_s:
            st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🔴 СИГНАЛ: SELL</h2>", unsafe_allow_html=True)
            st.error("Импульс подтвержден: Цена падает и ниже EMA.")
        else:
            st.warning("🟡 СОСТОЯНИЕ: ФЛЭТ (Ждем подтверждения)")
            
        st.write(f"Индикатор Momentum: {momentum:.3f}")
    else:
        st.error("Ошибка сети или данных.")

