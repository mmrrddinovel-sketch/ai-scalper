import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="XAUUSD QUANT CORE", layout="centered")
st.markdown("<h1 style='text-align: center; color: #ffd700;'>⚡ XAUUSD QUANT CORE</h1>", unsafe_allow_html=True)

# Использование тикера, который максимально точно отображает XAUUSD
ticker = "XAUUSD=X"

@st.cache_data(ttl=5)
def get_xau_data():
    try:
        # Загрузка данных с интервалом 5 минут (как на вашем графике)
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df['Close']
    except Exception:
        return None
    return None

if st.button("🚀 ANALYZE XAUUSD"):
    data = get_xau_data()
    
    if data is not None and not data.empty:
        price = float(data.iloc[-1])
        st.metric("XAU/USD SPOT PRICE", f"{price:.2f}")
        
        # Индикаторы для скальпинга
        ema_f = data.ewm(span=5).mean().iloc[-1]
        ema_s = data.ewm(span=15).mean().iloc[-1]
        
        if ema_f > ema_s:
            st.markdown("<h2 style='text-align: center; color: #00ff00;'>🟢 BUY SIGNAL</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🔴 SELL SIGNAL</h2>", unsafe_allow_html=True)
    else:
        st.error("Данные XAUUSD временно недоступны. Обновите страницу.")
