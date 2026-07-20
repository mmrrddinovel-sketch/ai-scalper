import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic

st.set_page_config(page_title="ELITE SCALPER", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #ffd700;}</style>", unsafe_allow_html=True)

st.title("⚡ ELITE QUANTUM SCALPER PRO")

assets = {"GOLD (XAUUSD)": "GC=F", "EUR/USD": "EURUSD=X", "BITCOIN": "BTC-USD", "GBP/USD": "GBPUSD=X"}

with st.sidebar:
    selected_name = st.selectbox("АКТИВ:", list(assets.keys()))
    ticker = assets[selected_name]
    ai_model = st.selectbox("ИИ-АНАЛИТИК:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("ВВЕДИТЕ API КЛЮЧ:", type="password")

@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df['EMA_Fast'] = df['Close'].ewm(span=9).mean()
            df['EMA_Slow'] = df['Close'].ewm(span=21).mean()
            return df
    except: return None
    return None

df = get_data(ticker)

if df is not None:
    last_row = df.iloc[-1]
    curr_price = float(last_row['Close'].item() if hasattr(last_row['Close'], 'item') else last_row['Close'])
    fast = float(last_row['EMA_Fast'].item() if hasattr(last_row['EMA_Fast'], 'item') else last_row['EMA_Fast'])
    slow = float(last_row['EMA_Slow'].item() if hasattr(last_row['EMA_Slow'], 'item') else last_row['EMA_Slow'])
    
    # Сигналы: LONG/SHORT
    math_signal = "LONG" if fast > slow else "SHORT"
    
    st.metric(f"ТЕКУЩАЯ ЦЕНА ({selected_name})", f"{curr_price:,.2f}")
    st.subheader(f"SIGNAL: {math_signal}")

    if st.button("🚀 ПОДТВЕРДИТЬ ИИ"):
        if not api_key:
            st.warning("Введите API ключ!")
        else:
            # Указание ИИ отвечать строго кратко
            prompt = f"Цена {selected_name}: {curr_price}. Технический сигнал: {math_signal}. Ответь строго одним из вариантов: 'CONFIRMED' или 'REJECTED' и добавь одно слово причины."
            with st.spinner("Анализ..."):
                try:
                    if ai_model == "Groq (Llama 3)":
                        res = Groq(api_key=api_key).chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                        st.info(res.choices[0].message.content)
                    elif ai_model == "Google Gemini":
                        genai.configure(api_key=api_key)
                        st.info(genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text)
                    elif ai_model == "Claude":
                        res = Anthropic(api_key=api_key).messages.create(model="claude-3-haiku-20240307", max_tokens=50, messages=[{"role": "user", "content": prompt}])
                        st.info(res.content[0].text)
                except Exception as e:
                    st.error(f"Ошибка ИИ: {e}")
