import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import time

st.set_page_config(page_title="HackerAI", layout="centered")

st.title("💀 HackerAI: SIGNALS")

# Список активов
assets = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"]

with st.sidebar:
    api_key = st.text_input("ENTER API KEY:", type="password")
    selected_asset = st.selectbox("АКТИВ:", assets)

def get_data(symbol):
    try:
        # Используем Ticker для более стабильного соединения
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1mo", interval="15m")
        if df.empty: return None
        
        last = df.iloc[-1]
        sma = df['Close'].rolling(20).mean().iloc[-1]
        
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss if loss != 0 else 1)))
        
        return {'Price': float(last['Close']), 'RSI': float(rsi)}
    except: return None

# Принудительная пауза перед загрузкой (чтобы сервер Streamlit не улетел в бан)
time.sleep(1)
data = get_data(selected_asset)

if data:
    st.write(f"### Актив: {selected_asset}")
    st.metric("Цена", f"{data['Price']:.5f}")
    
    if st.button("💀 ЗАПРОСИТЬ СИГНАЛ"):
        if not api_key:
            st.error("ВВЕДИТЕ API КЛЮЧ")
        else:
            with st.spinner("Анализ..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Цена {selected_asset} сейчас {data['Price']}, RSI={data['RSI']:.2f}. Если RSI < 30 - CALL, если RSI > 70 - PUT, иначе WAIT. Ответь ТОЛЬКО одним словом."
                signal = model.generate_content(prompt).text.strip()
                
                if "CALL" in signal.upper(): st.success("✅ СИГНАЛ: ВВЕРХ (CALL)")
                elif "PUT" in signal.upper(): st.error("❌ СИГНАЛ: ВНИЗ (PUT)")
                else: st.warning("⚠️ СИГНАЛ: ЖДИ (WAIT)")
else:
    st.error("⚠️ Биржа временно недоступна. Попробуйте нажать R через 10 секунд.")
