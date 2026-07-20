import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Настройка страницы
st.set_page_config(page_title="AI Scalping Ultimate", page_icon="⚡", layout="centered")

st.title("⚡ AI Forex & Crypto Scalper")
st.write("Продвинутый ИИ-анализ рынка с интеграцией глобальных Форекс-котировок.")

# --- БОКОВАЯ ПАНЕЛЬ НАСТРОЕК ---
st.sidebar.header("⚙️ Тонкая настройка ИИ")
sensitivity = st.sidebar.slider("Минимальная уверенность ИИ для сигнала (%)", 50, 85, 70, 
                                help="Чем выше процент, тем строже ИИ фильтрует ложные входы.")
estimators = st.sidebar.slider("Глубина нейросети (Количество деревьев)", 50, 500, 200)

# РАСШИРЕННЫЙ СПИСОК ФОРЕКС И КРИПТО АКТИВОВ
symbols_config = {
    "🥇 ЗОЛОТО (XAU/USD)": {"primary": "GC=F", "secondary": "GLD"}, 
    "🇪🇺 EUR/USD (Евро/Доллар)": {"primary": "EUR=X", "secondary": "EURUSD=X"}, 
    "🇬🇧 GBP/USD (Фунт/Доллар)": {"primary": "GBP=X", "secondary": "GBPUSD=X"},
    "🇯🇵 USD/JPY (Доллар/Йена)": {"primary": "JPY=X", "secondary": "USDJPY=X"},
    "🇦🇺 AUD/USD (Австралиец)": {"primary": "AUD=X", "secondary": "AUDUSD=X"},
    "₿ BITCOIN (BTC/USD)": {"primary": "BTC-USD", "secondary": "BTC-USD"},
    "♦️ ETHEREUM (ETH/USD)": {"primary": "ETH-USD", "secondary": "ETH-USD"}
}
selected = st.selectbox("🌍 Выберите актив для сканирования:", list(symbols_config.keys()))

# --- ФУНКЦИЯ УМНОЙ ЗАГРУЗКИ ДАННЫХ ---
def load_market_data(asset_name):
    cfg = symbols_config[asset_name]
    try:
        df = yf.download(cfg["primary"], period="1d", interval="1m", progress=False, timeout=15)
        if len(df) > 30:
            return df, cfg["primary"]
    except:
        pass
    
    df = yf.download(cfg["secondary"], period="1d", interval="1m", progress=False, timeout=15)
    return df, cfg["secondary"]

# --- ЛОГИКА ИИ И ТЕХАНАЛИЗА ---
if st.button("🚀 Запустить ИИ-сканирование", use_container_width=True):
    with st.spinner("Связь с биржами и расчет индикаторов..."):
        try:
            raw_data, final_ticker = load_market_data(selected)
            
            if len(raw_data) > 35:
                close = raw_data['Close'].iloc[:, 0] if isinstance(raw_data['Close'], pd.DataFrame) else raw_data['Close']
                last_price = float(close.iloc[-1])
                
                df = pd.DataFrame(index=close.index)
                df['Close'] = close
                
                df['MA5'] = df['Close'].rolling(5).mean()
                df['MA20'] = df['Close'].rolling(20).mean()
                
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / (loss + 1e-9)
                df['RSI'] = 100 - (100 / (1 + rs))
                
                df['Std'] = df['Close'].rolling(20).std()
                df['Volatility'] = df['Close'].pct_change().rolling(10).std()
                
                df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
                df = df.dropna()
                
                features = ['MA5', 'MA20', 'RSI', 'Volatility']
                
                model = RandomForestClassifier(n_estimators=estimators, max_depth=10, random_state=42)
                model.fit(df[features].iloc[:-1], df['Target'].iloc[:-1])
                
                prob = model.predict_proba(df[features].iloc[[-1]])[0][1]
                current_rsi = df['RSI'].iloc[-1]
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Текущая цена", f"{last_price:.4f}")
                col2.metric("Уверенность в росте", f"{prob*100:.1f}%")
                col3.metric("Индикатор RSI", f"{current_rsi:.1f}")
                
                st.caption(f"Источник данных: Глобальный Форекс/OTC (Тикер: {final_ticker})")
                
                sl_dist = df['Std'].iloc[-1] * 1.5 if df['Std'].iloc[-1] > 0 else last_price * 0.002
                buy_trigger = sensitivity / 100.0
                sell_trigger = 1.0 - buy_trigger
                
                st.divider()
                st.subheader("📋 Торговый план скальпера:")
                
                if prob > buy_trigger:
                    st.success("🟢 СИГНАЛ: ПОКУПАТЬ (BUY)")
                    st.write(f"**Точка входа:** {last_price:.4f}")
                    st.write(f"**Защитный Stop-Loss:** {last_price - sl_dist:.4f}")
                    st.write(f"**Целевой Take-Profit:** {last_price + (sl_dist * 2):.4f}")
                elif prob < sell_trigger:
                    st.error("🔴 СИГНАЛ: ПРОДАВАТЬ (SELL)")
                    st.write(f"**Точка входа:** {last_price:.4f}")
                    st.write(f"**Защитный Stop-Loss:** {last_price + sl_dist:.4f}")
                    st.write(f"**Целевой Take-Profit:** {last_price - (sl_dist * 2):.4f}")
                else:
                    st.info("🟡 СИГНАЛ: ВНЕ РЫНКА (WAIT)")
                    st.write(f"Рыночный шум. Уверенность алгоритма ({prob*100:.1f}%) ниже вашего фильтра ({sensitivity}%).")
                    
            else:
                st.warning("Нет связи с поставщиком ликвидности. Попробуйте еще раз.")
        except Exception as e:
            st.error(f"Сбой систем анализа: {e}")

# --- ИНТЕЛЛЕКТУАЛЬНЫЙ ЧАТ ---
st.divider()
st.subheader("💬 Аналитический онлайн-чат")
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("Спросите про Форекс, крипту или риски..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    prompt_l = prompt.lower()
    if "золот" in prompt_l or "xau" in prompt_l:
        response = "Золото (XAU/USD) обладает высокой волатильностью. Скальпинг по нему требует коротких Stop-Loss."
    elif "крипт" in prompt_l or "биткоин" in prompt_l or "btc" in prompt_l:
        response = "Криптовалютные рынки торгуются 24/7. Биткоин и Эфириум отлично поддаются техническому анализу, но остерегайтесь резких импульсов на новостях."
    elif "риск" in prompt_l or "депозит" in prompt_l:
        response = "Не рискуйте более чем 1-2% от баланса в одной сделке. Строго следуйте уровням Stop-Loss, которые рассчитывает алгоритм."
    else:
        response = "Принято. Рекомендую выбрать нужную Форекс-пару в меню выше и запустить сканирование. Алгоритм проанализирует последние объемы и волатильность."
        
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)




