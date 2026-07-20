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

# Background price updater (имитация WebSocket)
def price_updater():
    price = 4032.45
    while st.session_state.running:
        time.sleep(2)
        price += np.random.normal(0, 1.5)
        
        new_row = pd.DataFrame({
            'time': [datetime.now()],
            'price': [price]
        })
        st.session_state.data = pd.concat([st.session_state.data, new_row]).tail(200)

# Запуск потока один раз
if len([t for t in threading.enumerate() if t.name == "price_updater"]) == 0:
    thread = threading.Thread(target=price_updater, daemon=True, name="price_updater")
    thread.start()

# ==================== Функция генерации сигнала ====================
def generate_signal():
    if st.session_state.data.empty:
        return "⏳ Данные ещё загружаются..."
    
    current_price = st.session_state.data['price'].iloc[-1]
    ma_short = st.session_state.data['price'].rolling(9).mean().iloc[-1]
    ma_long = st.session_state.data['price'].rolling(21).mean().iloc[-1]
    
    if current_price > ma_short > ma_long:
        signal = "🟢 **STRONG BUY**"
        reason = "Цена выше обеих скользящих средних (бычий тренд)"
        levels = "TP: +18p | SL: -9p"
    elif current_price < ma_short < ma_long:
        signal = "🔴 **STRONG SELL**"
        reason = "Цена ниже обеих скользящих средних (медвежий тренд)"
        levels = "TP: +15p | SL: -8p"
    else:
        signal = "🟡 **НЕЙТРАЛЬНО**"
        reason = "Цена между MA9 и MA21 — ждём пробоя"
        levels = "Наблюдаем"
    
    full_signal = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "signal": signal,
        "reason": reason,
        "levels": levels,
        "price": round(current_price, 2)
    }
    
    st.session_state.signals_history.insert(0, full_signal)
    if len(st.session_state.signals_history) > 10:
        st.session_state.signals_history.pop()
    
    return full_signal

# ==================== UI ====================
st.title("🪙 ScalpX — Скальпинг Бот")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("XAUUSD — Живой график")
    if not st.session_state.data.empty:
        st.line_chart(st.session_state.data.set_index('time')['price'], use_container_width=True)
    else:
        st.info("Ожидаем первые тики...")

with col2:
    if not st.session_state.data.empty:
        current = st.session_state.data['price'].iloc[-1]
        delta = current - st.session_state.data['price'].iloc[-2] if len(st.session_state.data) > 1 else 0
        st.metric("Текущая цена XAUUSD", f"${current:.2f}", f"{delta:+.2f}")
    
    # Кнопка запроса сигнала
    if st.button("📡 Запросить сигнал сейчас", type="primary", use_container_width=True):
        with st.spinner("Анализирую рынок..."):
            signal = generate_signal()
            st.success(f"{signal['signal']} по цене ${signal['price']}")
            st.caption(signal['reason'])
            st.caption(signal['levels'])
    
    st.subheader("История сигналов")
    if st.session_state.signals_history:
        for s in st.session_state.signals_history[:5]:
            st.markdown(f"**{s['time']}** — {s['signal']} @ ${s['price']}")
            st.caption(s['reason'])
            st.divider()
    else:
        st.info("Нажми кнопку выше, чтобы получить первый сигнал")

st.caption("Цены обновляются автоматически • Нажми кнопку для мгновенного сигнала")
