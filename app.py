import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Настройка страницы
st.set_page_config(page_title="AI Scalping Pro", page_icon="📈", layout="centered")

st.title("🤖 AI Scalper Pro (GOLD Ready)")

# --- БОКОВАЯ ПАНЕЛЬ НАСТРОЕК ---
st.sidebar.header("⚙️ Конфигурация ИИ")
sensitivity = st.sidebar.slider("Порог уверенности (%), для точности", 50, 80, 65)
estimators = st.sidebar.slider("Глубина анализа (n_estimators)", 50, 300, 150)

# Список активов
symbols = {
    "GOLD (XAU/USD)": "XAUUSD=X", 
    "EUR/USD": "EURUSD=X", 
    "BTC/USD": "BTC-USD"
}
selected = st.selectbox("Выберите актив:", list(symbols.keys()))

# --- ЛОГИКА ИИ ---
if st.button("🚀 Анализировать рынок", use_container_width=True):
    with st.spinner("ИИ вычисляет паттерны..."):
        try:
            ticker = symbols[selected]
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            
            if len(data) > 30:
                close = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
                last_price = float(close.iloc[-1])
                
                df = pd.DataFrame(index=close.index)
                df['Close'] = close
                df['MA5'] = df['Close'].rolling(5).mean()
                df['MA20'] = df['Close'].rolling(20).mean()
                df['Volatility'] = df['Close'].pct_change().rolling(10).std()
                df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
                df = df.dropna()
                
                model = RandomForestClassifier(n_estimators=estimators, random_state=42)
                model.fit(df[['MA5', 'MA20', 'Volatility']].iloc[:-1], df['Target'].iloc[:-1])
                
                prob = model.predict_proba(df[['MA5', 'MA20', 'Volatility']].iloc[[-1]])[0][1]
                
                st.metric("Цена", f"{last_price:.4f}")
                st.metric("Вероятность роста", f"{prob*100:.1f}%")
                
                if prob > (sensitivity/100):
                    st.success("🟢 СИГНАЛ: BUY")
                elif prob < (1 - sensitivity/100):
                    st.error("🔴 СИГНАЛ: SELL")
                else:
                    st.info("🟡 СИГНАЛ: ВНЕ РЫНКА (WAIT)")
        except Exception as e:
            st.error(f"Ошибка: {e}")

# --- ЧАТ ---
st.divider()
st.subheader("💬 Чат с ИИ-помощником")
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("Спроси про золото или риск..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    response = "Я анализирую ситуацию. Помните: золото (XAU/USD) очень волатильно. Используйте настройки слева, чтобы повысить точность сигналов."
    if "золот" in prompt.lower(): response = "Золото сейчас находится под давлением. Для входа ждите подтверждения сигнала с вероятностью выше вашего порога."
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)


