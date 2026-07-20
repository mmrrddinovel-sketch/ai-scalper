import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading

st.set_page_config(page_title="ScalpX", layout="wide", page_icon="🪙")

# Инициализация данных
if 'data' not in st.session_state:
    now = datetime.now()
    times = [now - timedelta(seconds=i*2) for i in range(50, 0, -1)]
    prices = 4032.45 + np.cumsum(np.random.normal(0, 1.3, 50))
    st.session_state.data = pd.DataFrame({'time': times, 'price': prices})

if 'signals_history' not in st.session_state:
    st.session_state.signals_history = []
if 'running' not in st.session_state:
    st.session_state.running = True

def price_updater():
    price = float(st.session_state.data['price'].iloc[-1])
    while st.session_state.running:
        time.sleep(1.8)
        price += np.random.normal(0, 1.8)
        new_time = datetime.now()
        new_row = pd.DataFrame({'time': [new_time], 'price': [price]})
        st.session_state.data = pd.concat([st.session_state.data, new_row]).tail(200)

# Запуск обновлений
if not any(t.name == "price_updater" for t in threading.enumerate()):
    threading.Thread(target=price_updater, daemon=True, name="price_updater").start()

def generate_signal():
    current = float(st.session_state.data['price'].iloc[-1])
    ma9 = st.session_state.data['price'].rolling(9).mean().iloc[-1]
    ma21 = st.session_state.data['price'].rolling(21).mean().iloc[-1]
    
    if current > ma9 > ma21:
        return {"signal": "🟢 STRONG BUY", "reason": "Бычий тренд", "levels": "TP +18p | SL -9p", "price": round(current, 2)}
    elif current < ma9 < ma21:
        return {"signal": "🔴 STRONG SELL", "reason": "Медвежий тренд", "levels": "TP +15p | SL -8p", "price": round(current, 2)}
    else:
        return {"signal": "🟡 НЕЙТРАЛЬНО", "reason": "Боковик", "levels": "Ждём пробоя", "price": round(current, 2)}

# ==================== ИНТЕРФЕЙС ====================
st.title("🪙 ScalpX — Скальпинг Бот")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("XAUUSD — Живой график")
    st.line_chart(st.session_state.data.set_index('time')['price'], use_container_width=True)

with col2:
    current = float(st.session_state.data['price'].iloc[-1])
    st.metric("Текущая цена XAUUSD", f"${current:.2f}")
    
    if st.button("📡 Запросить сигнал сейчас", type="primary", use_container_width=True):
        with st.spinner("Анализирую рынок..."):
            signal = generate_signal()
            st.success(f"{signal['signal']} — ${signal['price']}")
            st.caption(signal['reason'])
            st.caption(signal['levels'])
            
            st.session_state.signals_history.insert(0, signal)
            if len(st.session_state.signals_history) > 8:
                st.session_state.signals_history.pop()
    
    st.subheader("История сигналов")
    for s in st.session_state.signals_history:
        st.markdown(f"**{datetime.now().strftime('%H:%M')}** — {s['signal']} @ ${s['price']}")
        st.caption(s['reason'])
        st.divider()

st.caption("Обновление каждые ~2 секунды")
