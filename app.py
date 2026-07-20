import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Scalper Stable", layout="centered")
st.title("⚡ Scalper Stable (M1)")

# Список пар с точными тикерами для Yahoo Finance
pairs = {"Золото": "GC=F", "EUR/USD": "EUR=X", "BTC": "BTC-USD"}

def get_data(ticker):
    try:
        # Уменьшаем запрос до минимума для скорости
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        return df.tail(20) if not df.empty else None
    except:
        return None

if st.button("🚀 ОБНОВИТЬ ДАННЫЕ"):
    for name, ticker in pairs.items():
        df = get_data(ticker)
        
        if df is not None and len(df) > 14:
            close = df['Close']
            # Расчет RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / (loss + 1e-9)))).iloc[-1]
            
            price = close.iloc[-1]
            
            # Статус
            color = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡"
            st.write(f"### {name}: {price:.2f} | RSI: {rsi:.1f} {color}")
        else:
            st.warning(f"{name}: Ждем данные...")
