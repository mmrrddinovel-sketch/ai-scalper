import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Scalper Stable", layout="centered")
st.title("⚡ Scalper Stable (M1)")

pairs = {"Золото": "GC=F", "EUR/USD": "EUR=X", "BTC": "BTC-USD"}

def get_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        return df.tail(20) if not df.empty else None
    except:
        return None

if st.button("🚀 ОБНОВИТЬ ДАННЫЕ"):
    for name, ticker in pairs.items():
        df = get_data(ticker)
        
        if df is not None and len(df) > 14:
            close = df['Close']
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 1e-9)
            rsi_series = 100 - (100 / (1 + rs))
            
            # Получаем последнее значение и проверяем его на корректность
            current_rsi = rsi_series.iloc[-1]
            
            if pd.isna(current_rsi):
                st.write(f"### {name}: Нет данных RSI")
            else:
                price = close.iloc[-1]
                # Корректная логика выбора цвета
                if current_rsi < 30:
                    color = "🟢"
                elif current_rsi > 70:
                    color = "🔴"
                else:
                    color = "🟡"
                
                st.write(f"### {name}: {price:.2f} | RSI: {current_rsi:.1f} {color}")
        else:
            st.warning(f"{name}: Загрузка данных...")

