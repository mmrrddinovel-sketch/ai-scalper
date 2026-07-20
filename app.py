import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

st.set_page_config(page_title="ELITE QUANT CORE", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #ffd700;}</style>", unsafe_allow_html=True)

st.title("⚡ ELITE QUANTUM SCALPER PRO")

assets = {"GOLD (XAUUSD)": "GC=F", "EUR/USD": "EURUSD=X", "BITCOIN": "BTC-USD"}

with st.sidebar:
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ИИ-АНАЛИТИК:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("API КЛЮЧ:", type="password")

@st.cache_data(ttl=60)
def get_data(symbol):
    df = yf.download(symbol, period="1d", interval="5m", progress=False)
    if not df.empty:
        df['EMA_Fast'] = df['Close'].ewm(span=9).mean()
        df['EMA_Slow'] = df['Close'].ewm(span=21).mean()
        return df
    return None

df = get_data(ticker)

if df is not None:
    curr_price = float(df['Close'].iloc[-1])
    fast = float(df['EMA_Fast'].iloc[-1])
    slow = float(df['EMA_Slow'].iloc[-1])
    
    # Логика математического бота (Сигнал)
    math_signal = "BUY" if fast > slow else "SELL"
    
    st.metric(f"ТЕКУЩАЯ ЦЕНА ({selected_name})", f"{curr_price:,.2f}")
    st.write(f"### МАТЕМАТИЧЕСКИЙ СИГНАЛ: {math_signal}")

    if st.button("🚀 ПОДТВЕРДИТЬ СИГНАЛ ЧЕРЕЗ ИИ"):
        if not api_key:
            st.warning("Введите API ключ!")
        else:
            prompt = f"Цена {selected_name}: {curr_price}. Математический бот выдал {math_signal}. Подтверди или опровергни этот сигнал на основе тренда. Дай короткий ответ."
            with st.spinner("Анализ..."):
                try:
                    if ai_model == "Groq (Llama 3)":
                        res = Groq(api_key=api_key).chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                        st.info(f"ИИ подтверждение: {res.choices[0].message.content}")
                    elif ai_model == "Google Gemini":
                        genai.configure(api_key=api_key)
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text)
                    elif ai_model == "Claude":
                        res = Anthropic(api_key=api_key).messages.create(model="claude-3-haiku-20240307", max_tokens=300, messages=[{"role": "user", "content": prompt}])
                        st.info(f"ИИ подтверждение: {res.content[0].text}")
                except Exception as e:
                    st.error(f"Ошибка ИИ: {e}")
