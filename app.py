import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Настройка интерфейса
st.set_page_config(page_title="HackerAI Signal", layout="centered")
st.markdown("<style>.main {background-color: #050505; color: #00ff00;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: SIGNALS")

assets = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "NZDUSD=X", "USDCAD=X", "EURGBP=X", "BTC-USD", "GC=F"]

with st.sidebar:
    api_key = st.text_input("ENTER API KEY:", type="password")
    selected_asset = st.selectbox("ВЫБОР АКТИВА:", assets)

def get_data(symbol):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        df = yf.download(symbol, period="1mo", interval="15m", progress=False, headers=headers)
        if df.empty or len(df) < 20: return None
        
        last = df.iloc[-1]
        sma = df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss if loss != 0 else 1)))
        
        return {'Price': float(last['Close']), 'RSI': float(rsi), 'Lower': float(sma - (std * 2)), 'Upper': float(sma + (std * 2))}
    except: return None

data = get_data(selected_asset)

if data:
    st.metric(f"ТЕКУЩАЯ ЦЕНА {selected_asset}:", f"{data['Price']:.5f}")
    
    if st.button(f"💀 ПОЛУЧИТЬ СИГНАЛ"):
        if not api_key:
            st.error("ВВЕДИТЕ API КЛЮЧ!")
        else:
            with st.spinner("Анализ..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Четкий промпт для сигнала
                prompt = f"""
                Ты — скальпер. Анализ {selected_asset}: Цена={data['Price']}, RSI={data['RSI']:.2f}.
                Если RSI < 30 — дай сигнал ВВЕРХ (CALL).
                Если RSI > 70 — дай сигнал ВНИЗ (PUT).
                Иначе — ЖДИ (WAIT).
                Выдай результат ОДНИМ СЛОВОМ (CALL / PUT / WAIT).
                """
                
                signal = model.generate_content(prompt).text.strip()
                
                # Окраска сигнала
                if "CALL" in signal.upper():
                    st.success("✅ СИГНАЛ: ВВЕРХ (CALL)")
                elif "PUT" in signal.upper():
                    st.error("❌ СИГНАЛ: ВНИЗ (PUT)")
                else:
                    st.warning("⚠️ СИГНАЛ: ЖДИ (WAIT)")
else:
    st.error("Данные не получены. Нажмите 'R' для перезагрузки.")
