import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Настройка
st.set_page_config(page_title="Pro Scalper AI", layout="centered")
st.title("⚡ Pro Scalper AI (Neural Core)")

ticker = "GC=F"

@st.cache_data(ttl=5)
def fetch_market_data(t):
    try:
        df = yf.download(t, period="2d", interval="1m", progress=False)
        if df.empty: return None
        # Приводим к плоскому формату, чтобы избежать ошибок размерности
        if isinstance(df['Close'], pd.DataFrame):
            return df['Close'].iloc[:, 0]
        return df['Close']
    except:
        return None

def get_ai_signal(close_data):
    # Преобразуем в массив numpy для скорости
    close = close_data.values
    if len(close) < 30: return "🟡 Инициализация...", 0, 0, "Сбор данных..."

    # Индикаторы
    ema9 = pd.Series(close).ewm(span=9).mean().values
    ema21 = pd.Series(close).ewm(span=21).mean().values
    
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(14).mean().values
    avg_loss = pd.Series(loss).rolling(14).mean().values
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    
    c_rsi, c_price = rsi[-1], close[-1]
    
    # Логика сигнала
    if c_rsi < 32 and ema9[-1] > ema21[-1]:
        return "🟢 BUY", c_rsi, c_price, "Импульс вверх + RSI перепродан"
    elif c_rsi > 68 and ema9[-1] < ema21[-1]:
        return "🔴 SELL", c_rsi, c_price, "Импульс вниз + RSI перекуплен"
    
    return "🟡 WAIT", c_rsi, c_price, "Нейтральная зона"

# Интерфейс
if st.button("🚀 SCAN MARKET"):
    data = fetch_market_data(ticker)
    if data is not None:
        signal, rsi_val, price, reason = get_ai_signal(data)
        st.metric("Price", f"{price:.2f}")
        st.subheader(f"Status: {signal}")
        st.write(f"RSI: {rsi_val:.2f}")
        st.write(f"Logic: {reason}")
    else:
        st.error("Ошибка данных. Попробуйте еще раз.")


