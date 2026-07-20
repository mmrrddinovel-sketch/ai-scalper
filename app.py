import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="HackerAI Ultimate PRO", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ULTIMATE PRO TERMINAL")

# Список всех популярных пар для торговли
all_assets = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "NZDUSD=X", "USDCAD=X", 
    "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CHFJPY=X", "EURCAD=X", "GBPCAD=X",
    "BTC-USD", "ETH-USD", "SOL-USD", "GC=F", "SI=F"
]

with st.sidebar:
    api_key = st.text_input("ENTER GEMINI API KEY:", type="password")
    asset = st.selectbox("ВЫБОР АКТИВА:", all_assets)

def get_pro_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        if df.empty: return None
        
        # Берем последнюю строку данных
        last_row = df.iloc[-1]
        
        # Расчет индикаторов
        sma = df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0).rolling(14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).fillna(0).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss) if loss != 0 else 1))
        
        return {
            'Price': float(last_row['Close']),
            'SMA': float(sma),
            'Upper': float(upper),
            'Lower': float(lower),
            'RSI': float(rsi)
        }
    except: return None

data = get_pro_data(asset)

if data:
    st.metric("PRICE:", f"{data['Price']:.5f}")
    c1, c2 = st.columns(2)
    c1.metric("RSI", f"{data['RSI']:.2f}")
    c2.metric("TREND", "BULLISH" if data['Price'] > data['SMA'] else "BEARISH")

    if st.button("💀 ПОЛУЧИТЬ ПРИКАЗ НА ВХОД"):
        if not api_key: st.error("Введите API ключ")
        else:
            with st.spinner("AI-Scanning..."):
                prompt = f"""
                Ты — элитный скальпер. Проанализируй {asset}.
                Цена: {data['Price']}, RSI: {data['RSI']}, Bollinger: {data['Lower']}-{data['Upper']}.
                
                Выдай ПРИКАЗ:
                1. SIGNAL: [CALL / PUT / WAIT]
                2. TIME: [1 мин / 5 мин]
                3. ENTRY: {data['Price']}
                4. CONFIDENCE: [High/Medium/Low]
                5. LOGIC: Краткое обоснование.
                """
                genai.configure(api_key=api_key)
                resp = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
                st.code(resp)
else:
    st.error("⚠️ Данные не получены. Попробуйте другой актив.")
