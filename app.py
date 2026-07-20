import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Настройка интерфейса
st.set_page_config(page_title="HackerAI Ultimate PRO", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ULTIMATE PRO TERMINAL")

# Расширенный список активов (валюты, крипта, золото)
all_assets = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", 
    "NZDUSD=X", "USDCAD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", 
    "BTC-USD", "ETH-USD", "GC=F"
]

with st.sidebar:
    api_key = st.text_input("ENTER GEMINI API KEY:", type="password")
    asset = st.selectbox("ВЫБОР АКТИВА:", all_assets)
    st.write("---")
    st.info("Рекомендация: Торгуйте по сигналу только при CONFIDENCE: High")

# Получение данных
def get_pro_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['StdDev'] = df['Close'].rolling(20).std()
        df['Upper'] = df['SMA_20'] + (df['StdDev'] * 2)
        df['Lower'] = df['SMA_20'] - (df['StdDev'] * 2)
        gain = df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean()
        loss = -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + gain / loss))
        low_min = df['Low'].rolling(14).min()
        high_max = df['High'].rolling(14).max()
        df['Stoch'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        return df.iloc[-1]
    except: return None

data = get_pro_data(asset)

if data is not None:
    st.metric("PRICE:", f"{data['Close']:.5f}")
    c1, c2, c3 = st.columns(3)
    c1.metric("RSI", f"{data['RSI']:.2f}")
    c2.metric("STOCH", f"{data['Stoch']:.2f}")
    c3.metric("TREND", "BULLISH" if data['Close'] > data['SMA_20'] else "BEARISH")

if st.button("💀 ПОЛУЧИТЬ ПРИКАЗ НА ВХОД"):
    if not api_key: st.error("ACCESS DENIED: Введите API ключ")
    else:
        with st.spinner("AI-Scanning..."):
            prompt = f"""
            Ты — элитный скальпер для Pocket Option. Проанализируй данные для {asset}:
            Цена: {data['Close']}, RSI: {data['RSI']}, Stoch: {data['Stoch']}, Bollinger: {data['Lower']}-{data['Upper']}
            
            Выдай ПРИКАЗ в следующем формате:
            1. SIGNAL: [CALL / PUT]
            2. EXPIRATION: [1 минута / 5 минут] (исходя из текущей волатильности)
            3. ENTRY: [Текущая цена]
            4. CONFIDENCE: [High/Medium/Low]
            5. STRATEGY: (Кратко: почему именно сейчас вход)
            
            Если показатели не дают 100% уверенности, пиши СИГНАЛ: WAIT.
            """
            genai.configure(api_key=api_key)
            resp = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
            st.code(resp)
