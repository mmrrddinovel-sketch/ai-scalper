import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

st.set_page_config(page_title="ELITE QUANT CORE", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #ffd700;}</style>", unsafe_allow_html=True)

st.title("⚡ ELITE QUANTUM CORE")

# Список активов
assets = {
    "GOLD (XAUUSD)": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "BITCOIN (BTC/USD)": "BTC-USD",
    "ETH/USD": "ETH-USD"
}

with st.sidebar:
    selected_name = st.selectbox("ВЫБОР АКТИВА:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ИИ-АНАЛИТИК:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("API КЛЮЧ:", type="password")

@st.cache_data(ttl=10)
def get_price(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if not data.empty and 'Close' in data.columns:
            val = data['Close'].iloc[-1]
            return float(val.iloc[0]) if hasattr(val, 'iloc') else float(val)
    except:
        return None
    return None

price = get_price(ticker)

if price is not None:
    st.metric(f"ТЕКУЩАЯ ЦЕНА ({selected_name})", f"{price:,.2f}")
    
    if st.button("🚀 АНАЛИЗ С ИИ"):
        if not api_key:
            st.warning("Введите ключ API в боковой панели!")
        else:
            with st.spinner("Анализ..."):
                prompt = f"Цена {selected_name}: {price}. Проведи скальпинг-анализ и дай торговый сигнал BUY/SELL."
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
    st.write("⏳ Ожидание данных...")
    if st.button("🔄 Обновить"):
        st.rerun()
