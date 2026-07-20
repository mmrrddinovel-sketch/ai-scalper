import streamlit as st
import yfinance as yf
import time
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

st.set_page_config(page_title="PRO SCALPER MASTER", layout="wide")
st.markdown("<style>.main {background-color: #0a0a0a; color: #00ff00; font-family: 'Courier New';}</style>", unsafe_allow_html=True)

st.title("🛡️ PRO SCALPER MASTER: ALGO-ENGINE")

# Улучшенные тикеры для точности
assets = {"GOLD (XAUUSD)": "XAUUSD=X", "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "BITCOIN": "BTC-USD"}

if 'last_price' not in st.session_state: st.session_state.last_price = 0.0

with st.sidebar:
    st.header("⚙️ КОНФИГУРАЦИЯ")
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ЯДРО ИИ:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("API KEY:", type="password")

def get_market_data(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1m", progress=False)
        price = float(data['Close'].iloc[-1])
        return price if price > 1 else yf.download("GC=F", period="1d", interval="1m")['Close'].iloc[-1]
    except: return None

price = get_market_data(ticker)
if price:
    st.session_state.last_price = price
    st.metric(f"LIVE FEED: {selected_name}", f"{price:,.2f}")

if st.button("💀 ЗАПУСТИТЬ ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗ"):
    if not api_key:
        st.error("ВСТАВЬТЕ API КЛЮЧ!")
    else:
        with st.spinner("Анализ рыночных дисбалансов (VSA/Price Action)..."):
            prompt = f"""
            Ты — элитный алготрейдер и хакер рынков. Твоя экспертиза: VSA, Price Action, Order Flow.
            Проанализируй текущую котировку {selected_name}: {st.session_state.last_price}.
            
            Выдай отчет как для профессионала:
            1. СТРУКТУРА: (Агрессивный/Коррекционный тренд)
            2. VSA/Анализ объема: (Есть ли кульминация покупок/продаж или признаки накопления)
            3. СИГНАЛ: LONG / SHORT / WAIT
            4. ПАРАМЕТРЫ ДЛЯ MT5 (ТОЧНО): Entry={st.session_state.last_price}, SL=..., TP=...
            5. РИСК-МЕНЕДЖМЕНТ: (Размер лота в % от депозита)
            
            Будь краток, используй термины профи.
            """
            try:
                # (Логика обращения к ИИ - без изменений, структура промпта теперь профессиональная)
                if ai_model == "Groq (Llama 3)":
                    res = Groq(api_key=api_key).chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    st.success(res.choices[0].message.content)
                elif ai_model == "Google Gemini":
                    genai.configure(api_key=api_key)
                    st.success(genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text)
                elif ai_model == "Claude":
                    res = Anthropic(api_key=api_key).messages.create(model="claude-3-haiku-20240307", max_tokens=300, messages=[{"role": "user", "content": prompt}])
                    st.success(res.content[0].text)
            except Exception as e:
                st.error(f"SYSTEM ERROR: {e}")

time.sleep(5)
st.rerun()
