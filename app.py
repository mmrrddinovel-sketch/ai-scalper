import streamlit as st
import yfinance as yf
import pandas as pd
import time
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

# Настройка страницы
st.set_page_config(page_title="ELITE LIVE SCALPER", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #ffd700;}</style>", unsafe_allow_html=True)

st.title("⚡ ELITE LIVE QUANTUM SCALPER")

assets = {"GOLD (XAUUSD)": "GC=F", "EUR/USD": "EURUSD=X", "BITCOIN": "BTC-USD"}

# Инициализация сессии
if 'last_price' not in st.session_state: st.session_state.last_price = 0.0

with st.sidebar:
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ИИ-АНАЛИТИК:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("ВВЕДИТЕ API КЛЮЧ:", type="password")

def get_live_data(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if not data.empty:
            val = data['Close'].iloc[-1]
            return float(val.item() if hasattr(val, 'item') else val)
    except: return None
    return None

# Получение и отображение цены
price = get_live_data(ticker)
if price:
    st.session_state.last_price = price
    st.metric(f"LIVE PRICE ({selected_name})", f"{price:,.2f}")

# Кнопка запроса сигнала
if st.button("🚀 ЗАПРОСИТЬ СИГНАЛ У ИИ"):
    if not api_key:
        st.warning("Введите API ключ в боковой панели!")
    else:
        with st.spinner("Анализ..."):
            prompt = f"""
            Цена {selected_name}: {st.session_state.last_price}. 
            Проведи быстрый технический анализ для скальпинга.
            Ответь строго ОДНИМ из вариантов: 'LONG', 'SHORT' или 'WAIT'. 
            Через дефис добавь краткую причину. 
            Пример: 'SHORT - высокий уровень сопротивления'.
            """
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
                    res = client.messages.create(model="claude-3-haiku-20240307", max_tokens=50, messages=[{"role": "user", "content": prompt}])
                    st.info(res.content[0].text)
            except Exception as e:
                st.error(f"Ошибка ИИ: {e}")

# Авто-обновление каждые 5 секунд
time.sleep(5)
st.rerun()
