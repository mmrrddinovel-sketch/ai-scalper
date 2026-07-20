import streamlit as st
import yfinance as yf
import pandas as pd

# Оптимизация интерфейса
st.set_page_config(page_title="Scalper Fast", layout="wide")
st.title("⚡ Ultra-Fast Scalper (M1)")

# Кэшируем данные для скорости (обновление каждые 30 секунд)
@st.cache_data(ttl=30)
def fetch_data(ticker):
    return yf.download(ticker, period="1d", interval="1m", progress=False).tail(50)

if st.button("🚀 МГНОВЕННЫЙ СКАН"):
    pairs = {"Золото": "GC=F", "EUR/USD": "EUR=X", "BTC": "BTC-USD"}
    
    # Создаем сетку для вывода (быстрее, чем список)
    cols = st.columns(len(pairs))
    
    for i, (name, ticker) in enumerate(pairs.items()):
        try:
            df = fetch_data(ticker)
            close = df['Close']
            
            # Быстрый расчет RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / (loss + 1e-9)))).iloc[-1]
            
            # Сигнал
            price = close.iloc[-1]
            signal = "🟡 ЖДАТЬ"
            if rsi < 30: signal = "🟢 ЛОНГ"
            if rsi > 70: signal = "🔴 ШОРТ"
            
            cols[i].metric(name, f"{price:.4f}", f"RSI: {rsi:.1f}")
            cols[i].write(f"### {signal}")
            
        except:
            cols[i].error(f"{name}: Ошибка")

st.info("Бот настроен на экстремальную скорость. Нажимайте 'МГНОВЕННЫЙ СКАН' для обновления данных.")

          
