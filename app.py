import streamlit as st
import yfinance as yf
import time
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

# Настройка страницы
st.set_page_config(page_title="PRO SCALPER MASTER", layout="wide")
st.markdown("<style>.main {background-color: #0a0a0a; color: #00ff00; font-family: 'Courier New';}</style>", unsafe_allow_html=True)

st.title("🛡️ PRO SCALPER MASTER: ALGO-ENGINE")

# Список активов
assets = {"GOLD (XAUUSD)": "GC=F", "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "BITCOIN": "BTC-USD"}

if 'last_price' not in st.session_state: st.session_state.last_price = 0.0

with st.sidebar:
    st.header("⚙️ КОНФИГУРАЦИЯ")
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ЯДРО ИИ:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("API KEY:", type="password")

# Профессиональная функция получения живых данных
def get_market_data(symbol):
    try:
        # Используем .history для максимально быстрой и свежей цены
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except: 
        return 0.0
    return 0.0

price = get_market_data(ticker)
if price:
    st.session_state.last_price = price
    st.metric(f"LIVE FEED: {selected_name}", f"{price:,.2f}")

# Кнопка анализа
if st.button("💀 ЗАПУСТИТЬ ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗ"):
    if not api_key:
        st.error("ВСТАВЬТЕ API КЛЮЧ!")
    else:
        with st.spinner("Анализ рыночных дисбалансов (VSA/Price Action)..."):
            # Профессиональный промпт
            prompt = f"""
            Ты — элитный алготрейдер. Экспертиза: VSA, Price Action, Order Flow.
            Текущая котировка {selected_name}: {st.session_state.last_price}.
            
            Проанализируй рынок для скальпинга:
            1. СТРУКТУРА: Агрессивный/Коррекционный тренд.
            2. VSA/Анализ: Признаки кульминации или накопления.
            3. СИГНАЛ: LONG / SHORT / WAIT.
            4. ПАРАМЕТРЫ ДЛЯ MT5 (ТОЧНО): 
               - Entry: {st.session_state.last_price}
               - SL: (рассчитай 0.1% от цены)
               - TP: (рассчитай 0.2% от цены)
            5. РИСК-МЕНЕДЖМЕНТ: Рекомендация лота на 1000$ депозита.
            
            Будь краток, используй термины профи.
            """
            try:
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
