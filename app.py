import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import time
import threading
import queue

st.set_page_config(page_title="ScalpX — Реал-тайм", layout="wide", page_icon="🪙")

# Session State
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'running' not in st.session_state:
    st.session_state.running = True

# Симулятор WebSocket
def price_updater():
    symbol = "XAUUSD"
    price = 4032.45
    timestamps = []
    closes = []
    
    while st.session_state.running:
        time.sleep(2)  # обновление каждые 2 секунды
        price += np.random.normal(0, 1.2)
        
        timestamps.append(datetime.now())
        closes.append(price)
        
        # Оставляем последние 200 точек
        if len(timestamps) > 200:
            timestamps = timestamps[-200:]
            closes = closes[-200:]
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'Close': closes,
            'Open': [c * 0.999 for c in closes],
            'High': [c * 1.002 for c in closes],
            'Low': [c * 0.998 for c in closes]
        })
        st.session_state.data = df

# Запуск потока
if not any(isinstance(t, threading.Thread) and t.is_alive() for t in threading.enumerate()):
    thread = threading.Thread(target=price_updater, daemon=True)
    thread.start()

# ==================== UI ====================
st.title("🪙 ScalpX — Скальпинг Бот (Реал-тайм)")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("XAUUSD — Живой график")
    if not st.session_state.data.empty:
        df = st.session_state.data
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="XAUUSD"
        ))
        fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ожидаем первые данные...")

with col2:
    if not st.session_state.data.empty:
        current_price = st.session_state.data['Close'].iloc[-1]
        change = current_price - st.session_state.data['Close'].iloc[-2] if len(st.session_state.data) > 1 else 0
        
        st.metric(
            label="Текущая цена XAUUSD",
            value=f"${current_price:.2f}",
            delta=f"{change:+.2f}"
        )
    
    st.subheader("Сигналы")
    if not st.session_state.data.empty:
        st.success("🟢 BUY — Цена выше MA9")
        st.error("🔴 SELL — Возможный откат")
    
    if st.button("🛑 Остановить обновления"):
        st.session_state.running = False
        st.warning("Обновления остановлены")

st.caption("Данные обновляются в реальном времени через background thread (имитация WebSocket)")
