import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import threading

st.set_page_config(page_title="ScalpX", layout="wide", page_icon="🪙")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['time', 'price'])
if 'signals_history' not in st.session_state:
    st.session_state.signals_history = []
if 'running' not in st.session_state:
    st.session_state.running = True

def price_updater():
    price = 4032.45
    # Инициализируем сразу несколько точек
    for i in range(30):
        price += np.random.normal(0, 1.2)
        st.session_state.data = pd.concat([st.session_state.data, 
            pd.DataFrame({'time': [datetime.now()], 'price': [price]})])
    
    while st.session_state.running:
        time.sleep(1.8)
        price += np.random.normal(0, 1.5)
        new_row = pd.DataFrame({'time': [datetime.now()], 'price': [price]})
        st.session_state.data = pd.concat([st.session_state.data, new_row]).tail(200)

# Запуск потока
if len([t for t in threading.enumerate() if t.name == "price_updater"]) == 0:
    threading.Thread(target=price_updater, daemon=True, name="price_updater").start()

def generate_signal():
    if len(st.session_state.data) < 5:
        return {"signal": "⏳ Загрузка...", "reason": "Недостаточно данных", "levels": "", "price": 0}
    
    current = st.session_state.data['price'].iloc[-1]
    ma9 = st.session_state.data['price'].rolling(9).mean().iloc[-1]
    ma21 = st.session_state.data['price'].rolling(21).mean().iloc[-1]
    
    if current > ma9 > ma21:
        return {"signal": "🟢 STRONG BUY", "reason": "Бычий тренд", "levels": "TP +18 | SL -9", "price": round(current, 2)}
    elif current < ma9 < ma21:
        return {"signal": "🔴 STRONG SELL", "reason": "Медвежий тренд", "levels": "TP +15 | SL -8", "price": round(current, 2)}
    else:
        return {"signal": "🟡 НЕЙТРАЛЬНО", "reason": "Боковик", "levels": "Ждём пробоя", "price": round(current, 2)}

# UI
st.title("🪙 ScalpX — Скальпинг Бот")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("XAUUSD — Живой график")
    if not st.session_state.data.empty:
        st.line_chart(st.session_state.data.set_index('time')['price'], use_container_width=True)
    else:
        st.info("Загрузка графика...")

with col2:
    if not st.session_state.data.empty:
        current = st.session_state.data['price'].iloc[-1]
        st.metric("Текущая цена XAUUSD", f"${current:.2f}")
    
    if st.button("📡 Запросить сигнал сейчас", type="primary", use_container_width=True):
        with st.spinner("Анализ рынка..."):
            signal = generate_signal()
            st.success(f"{signal['signal']} — ${signal['price']}")
            st.caption(signal['reason'])
            st.caption(signal['levels'])
    
    st.subheader("История сигналов")
    for s in st.session_state.signals_history:
        st.markdown(f"**{s.get('time', '')}** — {s['signal']} @ ${s['price']}")
        st.caption(s['reason'])
        st.divider()

st.caption("Данные обновляются автоматически")
