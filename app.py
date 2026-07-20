import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Elite Scalper M5", layout="centered")
st.markdown("<h1 style='text-align: center; color: #ffd700;'>⚡ ELITE M5 SCALPER</h1>", unsafe_allow_html=True)

# Меню выбора валюты
asset = st.selectbox("Выберите актив:", ["XAUUSD=X", "EURUSD=X", "BTC-USD", "ETH-USD"])

@st.cache_data(ttl=60)
def get_m5_data(ticker):
    try:
        # Анализ графика M5 (как на вашем скриншоте)
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df['Close']
    except: return None

if st.button("🚀 АНАЛИЗИРОВАТЬ ГРАФИК M5"):
    data = get_m5_data(asset)
    
    if data is not None and len(data) > 20:
        price = float(data.iloc[-1])
        # "Хакерский" ИИ-индикатор: быстрое пересечение EMA
        fast_ema = data.ewm(span=5).mean().iloc[-1]
        slow_ema = data.ewm(span=15).mean().iloc[-1]
        
        st.metric(f"Цена {asset}", f"{price:.4f}")
        
        # Логика сигнала
        if fast_ema > slow_ema:
            st.markdown("<h2 style='text-align: center; color: #00ff00;'>🟢 СИГНАЛ: BUY (LONG)</h2>", unsafe_allow_html=True)
            st.write("Импульс M5: Бычья фаза подтверждена.")
        else:
            st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🔴 СИГНАЛ: SELL (SHORT)</h2>", unsafe_allow_html=True)
            st.write("Импульс M5: Медвежья фаза подтверждена.")
            
        st.info("Анализ проведен по свечам M5. EMA-ядро готово.")
    else:
        st.error("Ошибка получения данных. Обновите страницу.")
