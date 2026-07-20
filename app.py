import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

# Элитный дизайн
st.set_page_config(page_title="ELITE QUANT CORE", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #050505; color: #ffd700;}
    h1 {text-align: center; color: #ffd700; text-transform: uppercase; letter-spacing: 5px;}
    .stMetric {background: #111; padding: 20px; border-left: 5px solid #ffd700; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ ELITE QUANTUM CORE")

# Боковая панель
with st.sidebar:
    st.header("⚙️ КОНФИГУРАЦИЯ")
    ticker = st.selectbox("ВЫБОР АКТИВА:", ["XAUUSD=X", "GC=F"])
    ai_model = st.selectbox("ВЫБОР ИИ-АНАЛИТИКА:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input(f"API КЛЮЧ ДЛЯ {ai_model}:", type="password")

@st.cache_data(ttl=5)
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        return df['Close'].iloc[-1] if not df.empty else None
    except: return None

# Анализ
price = get_data(ticker)
if price:
    st.metric(f"ТЕКУЩАЯ ЦЕНА ({ticker})", f"{price:.2f}")
    
    if st.button("🚀 АНАЛИЗ С ПОМОЩЬЮ ИИ"):
        if not api_key:
            st.error("Введите API ключ в боковой панели!")
        else:
            with st.spinner(f"ИИ {ai_model} рассчитывает вероятность..."):
                prompt = f"Цена золота {ticker}: {price}. Проведи скальпинг-анализ и дай рекомендацию BUY/SELL."
                try:
                    if ai_model == "Groq (Llama 3)":
                        client = Groq(api_key=api_key)
                        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                        st.info(res.choices[0].message.content)
                    elif ai_model == "Google Gemini":
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        st.info(model.generate_content(prompt).text)
                    elif ai_model == "Claude":
                        client = Anthropic(api_key=api_key)
                        res = client.messages.create(model="claude-3-haiku-20240307", max_tokens=300, messages=[{"role": "user", "content": prompt}])
                        st.info(res.content[0].text)
                except Exception as e:
                    st.error(f"Ошибка ИИ: {e}")
else:
    st.error("Данные недоступны. Попробуйте сменить актив.")
