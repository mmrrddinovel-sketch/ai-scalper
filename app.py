import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import threading

st.set_page_config(page_title="ScalpX", layout="wide", page_icon="🪙")

# Session State
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['time', 'price'])
if 'signals_history' not in st.session_state:
    st.session_state.signals_history = []
if 'running' not in st.session_state:
    st.session_state.running = True

# Background updater
def price_updater():
    price = 4032.45
    while st.session_state.running:
        time.sleep(2)
        price += np.random.normal(0, 1.5)
        new_row = pd.DataFrame({'time': [datetime.now()], 'price': [price]})
        st.session_state.data = pd.concat([st.session_state.data, new_row]).tail(200)

if len([t for t in threading.enumerate() if t.name == "price_updater"]) == 0:
    threading.Thread(target=price_updater, daemon=True, name="price_updater").start()

# Генерация сигнала
def generate_signal():
    if st.session_state.data.empty:
        return {
            "signal": "⏳ Ожидаем данные...",
            "reason": "График ещё загружается",
            "levels": "",
            "price": 0
        }
    
    current_price = st.session_state.data['price'].iloc[-1]
    ma9 = st.session_state.data['price'].rolling(9).mean().iloc[-1]
    ma21 = st.session_state.data['price'].rolling(21).mean().iloc[-1]
    
    if current_price > ma9 > ma21:
        signal_text = "🟢 STRONG BUY"
        reason = "Бычий тренд (цена выше MA9 и MA21)"
        levels = "TP +18p | SL -9p"
    elif current_price < ma9 < ma21:
        signal_text = "🔴 STRONG SELL"
        reason = "Медвежий тренд (цена ниже MA)"
        levels = "TP +15p | SL -8p"
    else:
        signal_text = "🟡 НЕЙТРАЛЬНО"
        reason = "Цена между скользящими средними"
        levels = "Ждём пробоя"
    
    signal_dict = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "signal": signal_text,
        "reason": reason,
        "levels": levels,
        "price": round(current_price, 2)
    }
    
    st.session_state.signals_history.insert(0, signal_dict)
    if len(st.session_state.signals_history) > 8:
        st.session_state.signals_history.pop()
    
    return signal_dict

# ==================== ИНТЕРФЕЙС ====================
st.title("🪙 ScalpX — Скальпинг Бот")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("XAUUSD — Живой график")
    if not st.session_state.data.empty:
        st.line_chart(st.session_state.data.set_index('time'), use_container_width=True)
    else:
        st.info("Ожидаем первые тики...")

with col2:
    if not st.session_state.data.empty:
        current = st.session_state.data['price'].iloc[-1]
        delta = current - st.session_state.data['price'].iloc[-2] if len(st.session_state.data) > 1 else 0
        st.metric("Текущая цена", f"${current:.2f}", f"{delta:+.2f}")
    
    # Кнопка сигнала
    if st.button("📡 Запросить сигнал сейчас", type="primary", use_container_width=True):
        with st.spinner("Анализирую рынок..."):
            signal = generate_signal()
            st.success(f"{signal['signal']} — ${signal['price']}")
            st.caption(signal['reason'])
            if signal['levels']:
                st.caption(signal['levels'])
    
    st.subheader("История сигналов")
    for s in st.session_state.signals_history[:6]:
        st.markdown(f"**{s['time']}** — {s['signal']} @ ${s['price']}")
        st.caption(s['reason'])
        st.divider()

st.caption("Автообновление каждые 2 секунды • Кнопка для мгновенного сигнала")
