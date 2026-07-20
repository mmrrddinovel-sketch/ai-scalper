import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Настройка интерфейса
st.set_page_config(page_title="Pro Scalper AI", layout="centered")
st.title("⚡ Pro Scalper AI (Neural Core V2)")

ticker = "GC=F"

@st.cache_data(ttl=5)
def fetch_market_data(t):
    try:
        # Берем больше данных для обучения ИИ на лету
        df = yf.download(t, period="5d", interval="1m", progress=False)
        if df.empty: return None
        return df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    except: return None

def ai_scalper_engine(close_data):
    # Векторизация данных (подготовка для ИИ)
    close = close_data.values
    if len(close) < 50: return "🟡 Обучение...", 0, 0, "Сбор данных..."

    # 1. Интеллектуальный расчет EMA (быстрая реакция)
    fast_ema = pd.Series(close).ewm(span=7).mean().values
    slow_ema = pd.Series(close).ewm(span=20).mean().values
    
    # 2. "Хакерский" индикатор аномалий (Z-Score)
    # Показывает, насколько текущая цена отклонилась от нормы (выброс)
    std = np.std(close[-30:])
    mean = np.mean(close[-30:])
    z_score = (close[-1] - mean) / (std + 1e-9)
    
    # 3. AI-сигнал (комбинированная логика)
    # ИИ ищет: Перепроданность + Импульс вверх + Ценовое отклонение (аномалия)
    buy_signal = (z_score < -1.5) and (fast_ema[-1] > slow_ema[-1])
    sell_signal = (z_score > 1.5) and (fast_ema[-1] < slow_ema[-1])
    
    # 4. Формирование ответа
    if buy_signal:
        return "🟢 BUY (AI-Anomaly)", close[-1], "Найдена аномалия перепроданности. Вход в импульс."
    elif sell_signal:
        return "🔴 SELL (AI-Anomaly)", close[-1], "Найдена аномалия перекупленности. Вход в откат."
    
    return "🟡 WAIT (Market Neutral)", close[-1], "Нет статистических аномалий для скальпинга."

# Интерфейс
if st.button("🚀 ЗАПУСТИТЬ AI-АНАЛИЗ"):
    data = fetch_market_data(ticker)
    if data is not None:
        signal, price, reason = ai_scalper_engine(data)
        st.metric("Цена (Gold)", f"{price:.2f}")
        st.subheader(f"Сигнал: {signal}")
        st.write(f"**Аналитика:** {reason}")
    else:
        st.error("Ошибка сети или данных.")
