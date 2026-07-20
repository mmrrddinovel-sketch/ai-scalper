import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Настройка
st.set_page_config(page_title="HackerAI Pro", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ULTIMATE PRO TERMINAL")

assets = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "NZDUSD=X", "USDCAD=X", "EURGBP=X", "BTC-USD", "GC=F"]

with st.sidebar:
    api_key = st.text_input("GEMINI API KEY:", type="password")
    selected_asset = st.selectbox("АКТИВ:", assets)

def get_data(symbol):
    try:
        # Указываем headers для обхода блокировок yfinance
        df = yf.download(symbol, period="1mo", interval="15m", progress=False, threads=True)
        if df.empty or len(df) < 20: return None
        
        last = df.iloc[-1]
        sma = df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss if loss != 0 else 1)))
        
        return {'Price': float(last['Close']), 'SMA': float(sma), 'RSI': float(rsi), 'Upper': float(sma + (std * 2)), 'Lower': float(sma - (std * 2))}
    except: return None

data = get_data(selected_asset)

if data:
    st.metric(f"ЦЕНА {selected_asset}:", f"{data['Price']:.5f}")
    
    if st.button(f"💀 АНАЛИЗ {selected_asset}"):
        if not api_key:
            st.error("ВВЕДИТЕ API КЛЮЧ")
        else:
            with st.spinner("Скан рынка..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Ты — эксперт Pocket Option. Проанализируй {selected_asset}.
                    Цена: {data['Price']}, RSI: {data['RSI']:.2f}, Bollinger: {data['Lower']:.5f}-{data['Upper']:.5f}.
                    
                    Дай четкий ПРИКАЗ:
                    1. SIGNAL: [CALL/PUT/WAIT]
                    2. TIME: [1 мин / 5 мин]
                    3. ENTRY: {data['Price']}
                    4. CONFIDENCE: [High/Medium]
                    5. ОБОСНОВАНИЕ: (Коротко)
                    """
                    st.code(model.generate_content(prompt).text)
                except Exception as e:
                    st.error(f"Ошибка ИИ: {e}")
else:
    # Если данные не получены, пробуем принудительно обновить
    st.warning("Нет данных. Нажмите кнопку перезагрузки (R) в интерфейсе Streamlit.")
