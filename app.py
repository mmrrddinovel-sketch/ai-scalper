import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="HackerAI Ultimate PRO", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ULTIMATE PRO TERMINAL")

# Полный список доступных ликвидных активов
all_assets = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "NZDUSD=X", "USDCAD=X", 
    "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CHFJPY=X", "EURCAD=X", "GBPCAD=X",
    "BTC-USD", "ETH-USD", "SOL-USD", "GC=F", "SI=F"
]

with st.sidebar:
    api_key = st.text_input("ENTER GEMINI API KEY:", type="password")
    asset = st.selectbox("ВЫБОР АКТИВА:", all_assets)
    st.warning("Примечание: Бот анализирует рыночные данные. OTC-активы брокера являются синтетическими, используйте анализ основной пары как ориентир.")

def get_pro_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        if df.empty or 'Close' not in df.columns: return None
        
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['StdDev'] = df['Close'].rolling(20).std()
        df['Upper'] = df['SMA_20'] + (df['StdDev'] * 2)
        df['Lower'] = df['SMA_20'] - (df['StdDev'] * 2)
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).fillna(0).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + gain / loss))
        
        low_min = df['Low'].rolling(14).min()
        high_max = df['High'].rolling(14).max()
        df['Stoch'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        return df.iloc[-1]
    except: return None

data = get_pro_data(asset)

if data is not None and not data.empty:
    price = float(data['Close'])
    st.metric("PRICE:", f"{price:.5f}")
    c1, c2, c3 = st.columns(3)
    c1.metric("RSI", f"{float(data['RSI']):.2f}")
    c2.metric("STOCH", f"{float(data['Stoch']):.2f}")
    c3.metric("TREND", "BULLISH" if price > float(data['SMA_20']) else "BEARISH")

    if st.button("💀 ПОЛУЧИТЬ ПРИКАЗ НА ВХОД"):
        if not api_key: st.error("Введите API ключ")
        else:
            with st.spinner("AI-Scanning..."):
                prompt = f"""
                Ты — элитный скальпер. Проанализируй {asset} для Pocket Option.
                Цена: {price}, RSI: {data['RSI']}, Stoch: {data['Stoch']}, Bollinger: {data['Lower']}-{data['Upper']}
                
                Выдай ПРИКАЗ:
                1. SIGNAL: [CALL / PUT / WAIT]
                2. TIME: [1 мин / 5 мин]
                3. ENTRY: {price}
                4. CONFIDENCE: [High/Medium/Low]
                5. LOGIC: Почему вход.
                """
                genai.configure(api_key=api_key)
                resp = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
                st.code(resp)
else:
    st.error("⚠️ Ошибка получения данных. Попробуйте другой актив.")
