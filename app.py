import streamlit as st
import yfinance as yf
import pandas as pd
import time
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

st.set_page_config(page_title="PRO SCALPER ELITE", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #ffd700;}</style>", unsafe_allow_html=True)

st.title("⚡ PRO SCALPER ELITE (Impulse/Lizard/SGI Engine)")

assets = {"GOLD (XAUUSD)": "GC=F", "EUR/USD": "EURUSD=X", "BITCOIN": "BTC-USD"}

if 'last_price' not in st.session_state: st.session_state.last_price = 0.0

with st.sidebar:
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ИИ-МОДУЛЬ (EXPERT ADVISOR):", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("ВВЕДИТЕ API КЛЮЧ:", type="password")

def get_live_data(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if not data.empty:
            val = data['Close'].iloc[-1]
            return float(val.item() if hasattr(val, 'item') else val)
    except: return None
    return None

price = get_live_data(ticker)
if price:
    st.session_state.last_price = price
    st.metric(f"LIVE PRICE ({selected_name})", f"{price:,.2f}")

if st.button("🚀 ЗАПУСТИТЬ АНАЛИЗ (PRO MODE)"):
    if not api_key:
        st.warning("Введите API ключ!")
    else:
        with st.spinner("Интеграция стратегий (Impulse, SGI, Lizard)..."):
            prompt = f"""
            Цена {selected_name}: {st.session_state.last_price}.
            Ты — объединенный скальпинг-робот (аналог Impulse, SGI, Lizard, Twister Pro).
            Твоя задача: дать точный сигнал по золоту (XAUUSD) или валютам.
            Ответ в формате:
            1. СИГНАЛ: LONG / SHORT / WAIT
            2. ПРИЧИНА: анализ волатильности и тренда
            3. ПАРАМЕТРЫ MT5: Entry={st.session_state.last_price}, SL=..., TP=...
            4. РИСК-МЕНЕДЖМЕНТ: (рекомендация по лоту)
            """
            try:
                if ai_model == "Groq (Llama 3)":
                    res = Groq(api_key=api_key).chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    st.info(res.choices[0].message.content)
                elif ai_model == "Google Gemini":
                    genai.configure(api_key=api_key)
                    st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text)
                elif ai_model == "Claude":
                    res = Anthropic(api_key=api_key).messages.create(model="claude-3-haiku-20240307", max_tokens=200, messages=[{"role": "user", "content": prompt}])
                    st.info(res.content[0].text)
            except Exception as e:
                st.error(f"Ошибка ИИ: {e}")

time.sleep(5)
st.rerun()
