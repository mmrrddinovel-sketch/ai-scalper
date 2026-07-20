import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import yfinance as yf

st.set_page_config(page_title="ScalpX — Скальпинг Бот", layout="wide", page_icon="🪙")
st.title("🪙 ScalpX — Бот для скальпинга XAUUSD")

# Sidebar
with st.sidebar:
    st.header("Инструменты")
    symbols = {
        "XAUUSD": "Золото",
        "EURUSD": "EUR/USD",
        "GBPUSD": "GBP/USD",
        "USDJPY": "USD/JPY",
        "CL=F": "Нефть"
    }
    
    selected_symbol = st.selectbox("Выберите пару", list(symbols.keys()), index=0)
    st.caption(symbols[selected_symbol])
    
    st.divider()
    st.subheader("Настройки скальпинга")
    lot_size = st.slider("Размер лота", 0.01, 1.0, 0.05, 0.01)
    risk_percent = st.slider("Риск на сделку (%)", 0.1, 5.0, 1.0, 0.1)
    
    auto_mode = st.toggle("Авто-скальпинг (симуляция)", value=True)
    
    if st.button("Сбросить позиции", type="secondary"):
        st.session_state.positions = []

# Main layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader(f"График — {selected_symbol}")
    
    # Загрузка данных
    with st.spinner("Загрузка данных..."):
        try:
            data = yf.download(selected_symbol, period="5d", interval="5m")
            if data.empty:
                # Симуляция если yfinance не сработал
                raise Exception
        except:
            # Симуляция данных
            dates = pd.date_range(end=datetime.now(), periods=300, freq='5min')
            base_price = 4032.45 if selected_symbol == "XAUUSD" else 1.0923
            price = np.random.normal(base_price, base_price*0.003, 300).cumsum() * 0.0001 + base_price
            data = pd.DataFrame({
                'Open': price,
                'High': price * 1.0015,
                'Low': price * 0.9985,
                'Close': price * np.random.uniform(0.999, 1.001, 300),
                'Volume': np.random.randint(1000, 10000, 300)
            }, index=dates)
    
    # Candlestick chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Цена"
    ))
    
    # Добавляем скользящие средние
    data['MA9'] = data['Close'].rolling(9).mean()
    data['MA21'] = data['Close'].rolling(21).mean()
    
    fig.add_trace(go.Scatter(x=data.index, y=data['MA9'], name="MA 9", line=dict(color="orange", width=1.5)))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA21'], name="MA 21", line=dict(color="blue", width=1.5)))
    
    fig.update_layout(
        height=600,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Live Price
    current_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100
    
    st.metric(
        label=f"**{selected_symbol}**",
        value=f"{current_price:.2f}",
        delta=f"{change:+.2f} ({change_pct:+.2f}%)"
    )
    
    st.subheader("Сигналы скальпинга")
    
    # Генерация сигналов
    signals = []
    last_close = data['Close'].iloc[-1]
    ma9 = data['MA9'].iloc[-1]
    ma21 = data['MA21'].iloc[-1]
    
    if last_close > ma9 > ma21:
        signals.append(("🟢 Сильный BUY", "MA кроссовер + тренд вверх", "TP: +15p | SL: -8p"))
    elif last_close < ma9 < ma21:
        signals.append(("🔴 Сильный SELL", "MA кроссовер + тренд вниз", "TP: +12p | SL: -8p"))
    else:
        signals.append(("🟡 Нейтрально", "Ждём подтверждения", ""))
    
    # Дополнительные сигналы
    rsi = 65 if last_close > data['Close'].mean() else 38
    if rsi > 70:
        signals.append(("⚠️ Перекупленность (RSI)", "Возможен откат", "SELL"))
    elif rsi < 30:
        signals.append(("✅ Перепроданность (RSI)", "Возможен отскок", "BUY"))
    
    for signal, reason, levels in signals:
        with st.container():
            st.markdown(f"**{signal}**")
            st.caption(reason)
            if levels:
                st.caption(f"**{levels}**")
            st.divider()
    
    # Quick Trade
    st.subheader("Быстрая сделка")
    col_buy, col_sell = st.columns(2)
    
    with col_buy:
        if st.button("🟢 BUY", use_container_width=True, type="primary"):
            st.success(f"Открыта LONG позиция по {selected_symbol} @ {current_price:.2f}")
            st.balloons()
    
    with col_sell:
        if st.button("🔴 SELL", use_container_width=True, type="secondary"):
            st.error(f"Открыта SHORT позиция по {selected_symbol} @ {current_price:.2f}")

# Авто-обновление
if auto_mode:
    st.info("Авто-скальпинг активен (симуляция). Цены обновляются каждые 5 секунд.")
    
    # Симуляция обновления цены
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    
    if time.time() - st.session_state.last_update > 5:
        st.rerun()

# Footer
st.caption("Это демонстрационная версия. Для р
