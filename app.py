import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Элитный интерфейс
st.set_page_config(page_title="Pro Scalper AI | Elite", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #0a0a0a; color: #e0e0e0;}
    .stButton>button {width: 100%; background: linear-gradient(90deg, #1a1a1a, #333); color: #ffd700; border: 1px solid #ffd700;}
    h1 {color: #ffd700; text-align: center; border-bottom: 2px solid #ffd700;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ ELITE AI NEURAL CORE")

ticker = st.selectbox("Выберите актив:", ["GC=F", "EURUSD=X", "BTC-USD", "ETH-USD"])

@st.cache_data(ttl=5)
def get_data(t):
    try:
        df = yf.download(t, period="10d", interval="1m", progress=False)
        return df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    except: return None

def neural_ai_engine(data):
    # Подготовка признаков для нейросети (хакерский подход к данным)
    df = pd.DataFrame(data)
    df['returns'] = df.iloc[:, 0].pct_change()
    df['volatility'] = df.iloc[:, 0].rolling(10).std()
    df['ema_fast'] = df.iloc[:, 0].ewm(span=5).mean()
    df['ema_slow'] = df.iloc[:, 0].ewm(span=20).mean()
    df = df.dropna()
    
    # Целевая переменная: пойдет ли цена вверх через 5 минут
    df['target'] = (df.iloc[:, 0].shift(-5) > df.iloc[:, 0]).astype(int)
    
    # Обучение модели "на лету" (Random Forest - классика ИИ в трейдинге)
    X = df[['returns', 'volatility', 'ema_fast', 'ema_slow']]
    y = df['target']
    
    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X[:-5], y[:-5]) # Обучаем на прошлых данных
    
    prediction = model.predict([X.iloc[-1]])
    proba = model.predict_proba([X.iloc[-1]])[0][1]
    
    if prediction == 1 and proba > 0.65:
        return "🟢 BUY SIGNAL (AI Neural)", "#00ff00", f"Confidence: {proba:.2%}"
    elif prediction == 0 and proba < 0.35:
        return "🔴 SELL SIGNAL (AI Neural)", "#ff0000", f"Confidence: {1-proba:.2%}"
    
    return "🟡 WAIT (Neural Neutral)", "#ffff00", "Слабый сигнал, высокая неопределенность."

if st.button("🚀 RUN NEURAL ANALYSIS"):
    data = get_data(ticker)
    if data is not None:
        signal, color, conf = neural_ai_engine(data)
        st.markdown(f"<h2 style='text-align: center; color: {color};'>{signal}</h2>", unsafe_allow_html=True)
        st.write(f"**Вероятность успеха:** {conf}")
        st.info("Neural Engine: Обучение модели завершено. Анализ проведен по 4-м векторным признакам.")
    else:
        st.error("Ошибка инициализации ядра.")
