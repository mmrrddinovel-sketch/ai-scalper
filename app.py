import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="AI Scalping Assistant", page_icon="🤖", layout="centered")

st.title("🤖 AI Scalper Web App (Machine Learning)")
st.write("Приложение для скальпинга на базе ИИ (Random Forest) для EUR/USD, XAU/USD и BTC/USD.")

# Выбор актива
symbols = {
    "EUR/USD": "EURUSD=X", 
    "XAU/USD": "GC=F", 
    "BTC/USD": "BTC-USD"
}

selected = st.selectbox("Выберите актив для анализа:", list(symbols.keys()))

if st.button("🚀 Запросить ИИ-сигнал", use_container_width=True):
    with st.spinner("ИИ анализирует рыночные паттерны..."):
        try:
            # Загружаем свежие данные за 1 день с интервалом в 1 минуту
            ticker = symbols[selected]
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            
            if data.empty or len(data) < 30:
                st.warning("Недостаточно данных для обучения ИИ. Попробуйте позже.")
            else:
                # Извлекаем цены закрытия
                close_prices = data['Close']
                if isinstance(close_prices, pd.DataFrame):
                    close_prices = close_prices.iloc[:, 0]
                
                last_price = float(close_prices.iloc[-1])
                
                # --- ПОДГОТОВКА ДАННЫХ ДЛЯ ИИ (Feature Engineering) ---
                df = pd.DataFrame(index=close_prices.index)
                df['Close'] = close_prices
                
                # Создаем признаки (features) для ИИ: разница цен, скользящие средние, волатильность
                df['Returns'] = df['Close'].pct_change()
                df['MA5'] = df['Close'].rolling(window=5).mean()
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['Volatility'] = df['Returns'].rolling(window=10).std()
                
                # Целевая переменная: пойдет ли цена вверх через 1 минуту (1 - да, 0 - нет)
                df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
                
                # Удаляем строки с пропущенными значениями
                df = df.dropna()
                
                if len(df) < 15:
                    st.warning("Слишком мало данных после очистки. Попробуйте другой актив.")
                else:
                    # Выделяем признаки для обучения
                    features = ['Returns', 'MA5', 'MA20', 'Volatility']
                    X = df[features].iloc[:-1] # Все кроме последней точки
                    y = df['Target'].iloc[:-1]
                    
                    # Последняя строка для предсказания (текущий срез рынка)
                    X_current = df[features].iloc[[-1]]
                    
                    # --- ОБУЧЕНИЕ МОДЕЛИ ИИ ---
                    model = RandomForestClassifier(n_estimators=50, random_state=42)
                    model.fit(X, y)
                    
                    # Прогноз ИИ (вероятность роста)
                    prediction_prob = model.predict_proba(X_current)[0]
                    prob_up = prediction_prob[1] # Вероятность того, что цена вырастет
                    
                    # Вывод результатов
                    st.metric(label=f"Текущая цена {selected}", value=f"{last_price:.4f}")
                    st.metric(label="Вероятность роста по версии ИИ", value=f"{prob_up * 100:.1f}%")
                    
                    st.divider()
                    st.subheader("💡 Торговый сигнал ИИ:")
                    
                    # Логика выдачи сигнала на основе вероятности ИИ
                    if prob_up > 0.58:
                        st.success(f"🟢 СИГНАЛ НА ПОКУПКУ (BUY)\n\n*Вердикт ИИ:* Модель видит паттерн роста с вероятностью {prob_up*100:.1f}%.")
                        st.write(f"**Stop-Loss:** ~{last_price * 0.998:.4f}")
                        st.write(f"**Take-Profit:** ~{last_price * 1.003:.4f}")
                    elif prob_up < 0.42:
                        st.error(f"🔴 СИГНАЛ НА ПРОДАЖУ (SELL)\n\n*Вердикт ИИ:* Модель фиксирует тенденцию к падению (вероятность роста всего {prob_up*100:.1f}%).")
                        st.write(f"**Stop-Loss:** ~{last_price * 1.002:.4f}")
                        st.write(f"**Take-Profit:** ~{last_price * 0.997:.4f}")
                    else:
                        st.info("🟡 СИГНАЛ: ВНЕ РЫНКА (WAIT)\n\n*Вердикт ИИ:* Рынок находится в зоне неопределенности. Сигнал слабый.")
                        
        except Exception as e:
            st.error(f"Произошла ошибка при работе ИИ: {e}")
