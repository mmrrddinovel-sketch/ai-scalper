import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Настройка стиля
st.set_page_config(page_title="HackerAI Pro", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ULTIMATE PRO TERMINAL")

# Полный список пар Pocket Option
assets = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "NZDUSD=X", "USDCAD=X",
    "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CHFJPY=X", "EURCAD=X", "GBPCAD=X",
    "BTC-USD", "ETH-USD", "SOL-USD", "GC=F", "SI=F"
]

with st.sidebar:
    api_key = st.text_input("ENTER GEMINI API KEY:", type="password")
    selected_asset = st.selectbox("ВЫБОР АКТИВА:", assets)

# Функция надежного получения данных
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1mo", interval="15m", progress=False)
        if df.empty: return None
        
        last = df.iloc[-1]
        sma = df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss if loss != 0 else 1)))
        
        return {
            'Price': float(last['Close']),
            'SMA': float(sma),
            'Upper': float(sma + (std * 2)),
            'Lower': float(sma - (std * 2)),
            'RSI': float(rsi)
        }
    except: return None

# Основная логика
data = get_data(selected_asset)

if data:
    st.metric(f"ТЕКУЩАЯ ЦЕНА {selected_asset}:", f"{data['Price']:.5f}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("RSI", f"{data['RSI']:.2f}")
    col2.metric("TREND", "BULLISH" if data['Price'] > data['SMA'] else "BEARISH")
    col3.metric("BB STATUS", "OVERBOUGHT" if data['Price'] > data['Upper'] else "OVERSOLD" if data['Price'] < data['Lower'] else "NEUTRAL")

    # Кнопка для получения сигнала по выбранному активу
    if st.button(f"💀 ПОЛУЧИТЬ СИГНАЛ ПО {selected_asset}"):
        if not api_key:
            st.error("Ошибка: Введите API ключ в боковой панели!")
        else:
            with st.spinner("AI-анализ в процессе..."):
                try:
                    genai.configure(api_key=api_key)
                    prompt = f"""
                    Ты — профи трейдер. Анализ {selected_asset}:
                    Цена: {data['Price']}, RSI: {data['RSI']}, Bollinger: {data['Lower']}-{data['Upper']}.
                    Выдай решение:
                    1. SIGNAL: [CALL / PUT / WAIT]
                    2. TIME: [1 мин / 5 мин]
                    3. ENTRY: {data['Price']}
                    4. CONFIDENCE: [High/Medium/Low]
                    5. LOGIC: Кратко (почему).
                    """
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    st.code(response.text)
                except Exception as e:
                    st.error(f"Ошибка ИИ: {e}")
else:
    st.error("⚠️ Данные не получены. Попробуйте обновить страницу или сменить актив.")
