import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(page_title="Pro Scalper AI", layout="centered")

# Элитный заголовок
st.markdown("<h1 style='text-align: center; color: #ffd700;'>⚡ ELITE SCALPER AI</h1>", unsafe_allow_html=True)

# Выбор актива
ticker = st.selectbox("Выберите инструмент:", ["GC=F", "EURUSD=X", "BTC-USD", "ETH-USD"])

@st.cache_data(ttl=5)
def get_market_data(t):
    try:
        # Загрузка данных с обработкой структуры
        df = yf.download(t, period="2d", interval="1m", progress=False)
        if df.empty: return None
        
        # Исправление структуры данных (универсальный метод для yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df['Close']
    except Exception:
        return None

# Основная кнопка
if st.button("🚀 АНАЛИЗ РЫНКА"):
    data = get_market_data(ticker)
    
    if data is not None and len(data) > 25:
        # Расчет индикаторов
        price = float(data.iloc[-1])
        ema_fast = data.ewm(span=5).mean().iloc[-1]
        ema_slow = data.ewm(span=20).mean().iloc[-1]
        
        # Вывод показателей
        st.metric("Текущая цена", f"{price:.4f}")
        
        # Профессиональная логика скальпинга
        if ema_fast > ema_slow:
            st.markdown("<h2 style='text-align: center; color: #00ff00;'>🟢 СИГНАЛ: BUY</h2>", unsafe_allow_html=True)
            st.info("Импульс восходящий: Быстрая EMA выше медленной.")
        else:
            st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🔴 СИГНАЛ: SELL</h2>", unsafe_allow_html=True)
            st.error("Импульс нисходящий: Быстрая EMA ниже медленной.")
            
        st.write(f"Анализ завершен. Параметры EMA(5/20).")
    else:
        st.error("Ошибка получения данных. Попробуйте обновить страницу.")
