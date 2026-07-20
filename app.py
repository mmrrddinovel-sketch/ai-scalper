import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Scalper Stable", layout="centered")
st.title("⚡ Scalper Stable (M1)")

pairs = {"Золото": "GC=F", "EUR/USD": "EUR=X", "BTC": "BTC-USD"}

if st.button("🚀 ОБНОВИТЬ ДАННЫЕ"):
    for name, ticker in pairs.items():
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if df is not None and len(df) > 14:
                close = df['Close']
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                
                # Безопасный расчет RSI
                rs = gain / (loss + 1e-9)
                rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
                
                # Принудительная проверка на число
                if np.isnan(rsi_val):
                    st.write(f"### {name}: Ожидание данных...")
                else:
                    price = close.iloc[-1]
                    color = "🟢" if rsi_val < 30 else "🔴" if rsi_val > 70 else "🟡"
                    st.write(f"### {name}: {price:.2f} | RSI: {rsi_val:.1f} {color}")
            else:
                st.write(f"### {name}: Нет данных")
        except Exception as e:
            st.write(f"### {name}: Ошибка доступа")
