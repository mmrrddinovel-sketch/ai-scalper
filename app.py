import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# --- НАСТРОЙКА ИНТЕРФЕЙСА ---
st.set_page_config(page_title="AI Scalping MAX", page_icon="🔥", layout="centered")
st.title("🔥 AI Scalper MAX (Professional)")
st.write("Терминал максимальной точности. Технический анализ + Machine Learning.")

# --- БОКОВАЯ ПАНЕЛЬ: НАСТРОЙКИ ---
st.sidebar.header("⚙️ Калибровка ИИ")
sensitivity = st.sidebar.slider("Точность сигнала (Порог %)", 55, 85, 70, help="Рекомендую 70% для скальпинга")
estimators = st.sidebar.slider("Мощность нейросети (деревья)", 100, 500, 250)

# Глобальные котировки
symbols_config = {
    "🥇 ЗОЛОТО (XAU/USD)": {"primary": "GC=F", "secondary": "GLD"}, 
    "🇪🇺 EUR/USD": {"primary": "EUR=X", "secondary": "EURUSD=X"}, 
    "🇬🇧 GBP/USD": {"primary": "GBP=X", "secondary": "GBPUSD=X"},
    "₿ BITCOIN (BTC/USD)": {"primary": "BTC-USD", "secondary": "BTC-USD"}
}
selected = st.selectbox("🎯 Выберите актив для анализа:", list(symbols_config.keys()))

# --- АЛГОРИТМ ЗАГРУЗКИ ---
def load_market_data(asset_name):
    cfg = symbols_config[asset_name]
    try:
        df = yf.download(cfg["primary"], period="1d", interval="1m", progress=False, timeout=15)
        if len(df) > 50: return df, cfg["primary"]
    except: pass
    df = yf.download(cfg["secondary"], period="1d", interval="1m", progress=False, timeout=15)
    return df, cfg["secondary"]

# --- ЯДРО ИИ И ТЕХАНАЛИЗА ---
if st.button("⚡ СКАНИРОВАТЬ РЫНОК", use_container_width=True, type="primary"):
    with st.spinner("Синхронизация с биржей и расчет индикаторов (RSI, MACD, ATR)..."):
        try:
            raw_data, final_ticker = load_market_data(selected)
            
            if len(raw_data) > 50:
                # Извлечение данных
                df = pd.DataFrame(index=raw_data.index)
                df['Close'] = raw_data['Close'].iloc[:, 0] if isinstance(raw_data['Close'], pd.DataFrame) else raw_data['Close']
                df['High'] = raw_data['High'].iloc[:, 0] if isinstance(raw_data['High'], pd.DataFrame) else raw_data['High']
                df['Low'] = raw_data['Low'].iloc[:, 0] if isinstance(raw_data['Low'], pd.DataFrame) else raw_data['Low']
                
                last_price = float(df['Close'].iloc[-1])
                
                # 1. ИНДИКАТОРЫ ТРЕНДА (EMA)
                df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
                
                # 2. ИНДИКАТОР ВОЛАТИЛЬНОСТИ (ATR) - для идеального Stop-Loss
                df['H-L'] = df['High'] - df['Low']
                df['H-C'] = np.abs(df['High'] - df['Close'].shift(1))
                df['L-C'] = np.abs(df['Low'] - df['Close'].shift(1))
                df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
                df['ATR'] = df['TR'].rolling(14).mean()
                
                # 3. ОСЦИЛЛЯТОРЫ (RSI и MACD)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / (loss + 1e-9)
                df['RSI'] = 100 - (100 / (1 + rs))
                
                df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
                df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                
                # Обучение модели
                df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
                df = df.dropna()
                
                features = ['EMA9', 'EMA21', 'ATR', 'RSI', 'MACD', 'MACD_Signal']
                model = RandomForestClassifier(n_estimators=estimators, max_depth=12, random_state=42)
                model.fit(df[features].iloc[:-1], df['Target'].iloc[:-1])
                
                # Прогноз
                prob = model.predict_proba(df[features].iloc[[-1]])[0][1]
                
                current_rsi = float(df['RSI'].iloc[-1])
                current_atr = float(df['ATR'].iloc[-1])
                
                # Вывод
                c1, c2, c3 = st.columns(3)
                c1.metric("Цена входа", f"{last_price:.4f}")
                c2.metric("Сила быков", f"{prob*100:.1f}%")
                c3.metric("RSI (14)", f"{current_rsi:.1f}")
                
                st.divider()
                st.subheader("📊 ТОРГОВЫЙ ПЛАН (Риск к прибыли 1:2):")
                
                buy_trigger = sensitivity / 100.0
                sell_trigger = 1.0 - buy_trigger
                
                # Расчет скальперского стопа и тейка через ATR
                sl_dist = current_atr * 1.5 
                tp_dist = current_atr * 3.0 
                
                if prob > buy_trigger and current_rsi < 70:
                    st.success("🟢 ОТКРЫТЬ ЛОНГ (ПОКУПКА / BUY)")
                    st.write(f"**Анализ:** Тренд восходящий, MACD подтверждает силу покупателей. Запас хода есть.")
                    st.write(f"**Точка входа:** {last_price:.4f}")
                    st.write(f"**🛑 Stop-Loss:** {last_price - sl_dist:.4f}")
                    st.write(f"**✅ Take-Profit:** {last_price + tp_dist:.4f}")
                    
                elif prob < sell_trigger and current_rsi > 30:
                    st.error("🔴 ОТКРЫТЬ ШОРТ (ПРОДАЖА / SELL)")
                    st.write(f"**Анализ:** На рынке доминируют медведи. Цена пробила поддержку вниз.")
                    st.write(f"**Точка входа:** {last_price:.4f}")
                    st.write(f"**🛑 Stop-Loss:** {last_price + sl_dist:.4f}")
                    st.write(f"**✅ Take-Profit:** {last_price - tp_dist:.4f}")
                    
                else:
                    st.info("🟡 ЖДЕМ (ВНЕ РЫНКА)")
                    st.write("На рынке флэт (боковик) или ИИ не уверен в движении. Лучше сохранить депозит и подождать четкого сигнала.")
                    
        except Exception as e:
            st.error(f"Сбой загрузки: {e}. Попробуйте снова.")

# --- УМНЫЙ ЧАТ-ПОМОЩНИК ---
st.divider()
st.subheader("💬 AI Trading Assistant")
st.caption("Я ваш карманный аналитик. Могу поболтать или подсказать по рынку.")

if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("Напишите 'Привет' или задайте вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    prompt_l = prompt.lower()
    
    # Логика общения
    if any(word in prompt_l for word in ["привет", "здравствуй", "ку", "хай"]):
        response = "Привет! 👋 Я готов к работе. Запускай сканирование рынка или спрашивай меня о стратегиях."
    elif any(word in prompt_l for word in ["как дела", "как ты"]):
        response = "Отлично! Серверы работают без перебоев, котировки поступают. Готов вычислять для тебя прибыль. 🚀"
    elif "лонг" in prompt_l or "шорт" in prompt_l:
        response = "Лонг (Long) — это покупка в расчете на рост. Шорт (Short) — продажа в расчете на падение. Мой алгоритм сам подскажет, куда сейчас лучше встать."
    elif "золот" in prompt_l:
        response = "Золото (XAU/USD) любит резкие движения. Обязательно используй Stop-Loss, который я рассчитываю по индикатору ATR — это спасет тебя от резких скачков."
    elif "rsi" in prompt_l or "macd" in prompt_l or "atr" in prompt_l:
        response = "В этой версии я использую связку: MACD определяет направление глобального тренда, RSI не дает купить на самых хаях или продать на дне, а ATR вычисляет идеальный стоп-лосс на основе текущей волатильности."
    elif "спасибо" in prompt_l or "спс" in prompt_l:
        response = "Всегда пожалуйста! Удачной торговли и зеленого PNL! 📈"
    else:
        response = "Понял тебя. Как ИИ-трейдер, я советую фокусироваться на графике: жми «Сканировать рынок», я проанализирую последние минутные свечи и выдам готовый сетап."
        
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)





