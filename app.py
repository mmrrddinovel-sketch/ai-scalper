import streamlit as st
import ccxt
import pandas as pd

st.set_page_config(page_title="BingX Elite Scalper", layout="centered")
st.title("⚡ BINGX QUANT CORE")

@st.cache_data(ttl=5)
def get_bingx_data():
    try:
        # Инициализация биржи
        exchange = ccxt.bingx()
        # Получение свечей (OHLCV) по золоту
        bars = exchange.fetch_ohlcv('XAU/USDT', timeframe='5m', limit=20)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df['close']
    except Exception:
        return None

if st.button("🚀 SYNC BINGX DATA"):
    data = get_bingx_data()
    
    if data is not None:
        price = float(data.iloc[-1])
        # Трендовый ИИ (EMA)
        fast_ema = data.ewm(span=5).mean().iloc[-1]
        slow_ema = data.ewm(span=15).mean().iloc[-1]
        
        st.metric("Цена BINGX (XAU/USDT)", f"{price:.2f}")
        
        if fast_ema > slow_ema:
            st.markdown("<h2 style='color:#00ff00;'>🟢 СИГНАЛ: BUY</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color:#ff4b4b;'>🔴 СИГНАЛ: SELL</h2>", unsafe_allow_html=True)
    else:
        st.error("Ошибка подключения к BingX. Проверьте API или статус биржи.")
