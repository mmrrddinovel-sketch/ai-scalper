import streamlit as st
import yfinance as yf
import pandas as pd

# Элитный интерфейс
st.set_page_config(page_title="ELITE QUANT CORE", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #050505;}
    h1 {color: #ffd700; text-align: center; text-transform: uppercase; letter-spacing: 2px;}
    .stMetric {background: #111; padding: 15px; border-left: 4px solid #ffd700;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ ELITE QUANTUM SCALPER")

# Используем GC=F (золото), так как он всегда стабилен для получения данных
asset = st.selectbox("ВЫБОР АКТИВА:", ["GC=F", "EURUSD=X", "BTC-USD"])

@st.cache_data(ttl=5)
def get_data(ticker):
    try:
        # Увеличиваем период до 5 дней, чтобы гарантированно получить историю
        df = yf.download(ticker, period="5d", interval="5m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        return df['Close']
    except Exception: return None

if st.button("🚀 EXECUTE QUANT ANALYSIS"):
    data = get_data(asset)
    
    if data is not None and not data.empty:
        price = float(data.iloc[-1])
        
        # 1. Трендовый ИИ
        f_ema = data.ewm(span=5).mean().iloc[-1]
        s_ema = data.ewm(span=20).mean().iloc[-1]
        
        # 2. Аномалии (Z-Score)
        std = data.iloc[-30:].std()
        mean = data.iloc[-30:].mean()
        z_score = (price - mean) / (std + 1e-9)
        
        st.metric("CURRENT PRICE", f"{price:.4f}")
        
        # Логика сигналов
        if z_score < -1.5 and f_ema > s_ema:
            st.markdown("<h2 style='color:#00ff00;'>🟢 BUY SIGNAL: QUANTUM APPROVED</h2>", unsafe_allow_html=True)
        elif z_score > 1.5 and f_ema < s_ema:
            st.markdown("<h2 style='color:#ff4b4b;'>🔴 SELL SIGNAL: QUANTUM APPROVED</h2>", unsafe_allow_html=True)
        else:
            st.warning("🟡 QUANTUM CORE: ОЖИДАНИЕ АНОМАЛИИ")
    else:
        st.error("QUANTUM CORE: ПЕРЕЗАГРУЗИТЕ СТРАНИЦУ (ОШИБКА ДАННЫХ)")
