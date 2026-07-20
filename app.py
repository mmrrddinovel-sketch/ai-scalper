import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pro Scalper AI", layout="centered")
st.title("⚡ Pro Scalper AI (Neural Core)")

ticker = "GC=F"

@st.cache_data(ttl=5) # Сократили TTL для актуальности данных
def fetch_market_data(t):
    try:
        # Увеличили объем данных для более точного расчета EMA
        df = yf.download(t, period="2d", interval="1m", progress=False)
        return df.dropna() if not df.empty else None
    except:
        return None

def professional_scalping_ai(df):
    close = df['Close'].values # Работа напрямую с массивами NumPy для скорости
    
    # Расчет индикаторов
    ema9 = pd.Series(close).ewm(span=9).mean().values
    ema21 = pd.Series(close).ewm(span=21).mean().values
    
    # RSI (исправленный расчет через NumPy)
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(14).mean().values
    avg_loss = pd.Series(loss).rolling(14).mean().values
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    
    # Получаем последние значения, проверяя на наличие данных
    if len(close) < 21: return "🟡 НЕТ ДАННЫХ", 0, 0, "Инициализация..."
    
    c_rsi, c_price, c_ema9, c_ema21 = rsi[-1], close[-1], ema9[-1], ema21[-1]
    
    # AI-логика: Рассчитываем Score уверенности (Neural Confidence)
    ema_diff = abs(c_ema9 - c_ema21)
    confidence = "High" if ema_diff > (np.std(close[-50:]) * 0.1) else "Low"
    
    # Принятие решения
    if c_rsi < 30 and c_ema9 > c_ema21:
        return "🟢 BUY (AI-Validated)", c_rsi, c_price, f"Confidence: {confidence}. Импульс восходящий."
    elif c_rsi > 70 and c_ema9 < c_ema21:
        return "🔴 SELL (AI-Validated)", c_rsi, c_price, f"Confidence: {confidence}. Импульс нисходящий."
    
    return "🟡 WAIT / NEUTRAL", c_rsi, c_price, "Ожидание формирования ИИ-сигнала"

if st.button("🚀 SCAN MARKET"):
    data = fetch_market_data(ticker)
    if data is not None:
        signal, rsi_val, price, reason = professional_scalping_ai(data)
        st.metric("Price", f"{price:.2f}")
        st.metric("AI Signal", signal)
        st.write(f"**RSI:** {rsi_val:.2f} | **Status:** {reason}")
    else:
        st.error("Данные недоступны.")

