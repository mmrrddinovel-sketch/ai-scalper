import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="AI Scalping Assistant", page_icon="🤖", layout="centered")

st.title("🤖 AI Scalper Web App (Advanced)")
symbols = {"EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "BTC/USD": "BTC-USD"}
selected = st.selectbox("Выберите актив:", list(symbols.keys()))

if st.button("🚀 Запросить ИИ-сигнал", use_container_width=True):
    with st.spinner("Анализ рынка..."):
        try:
            ticker = symbols[selected]
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            
            if len(data) < 30:
                st.warning("Мало данных для анализа.")
            else:
                close = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
                last_price = float(close.iloc[-1])
                
                df = pd.DataFrame(index=close.index)
                df['Close'] = close
                df['Returns'] = df['Close'].pct_change()
                df['MA5'] = df['Close'].rolling(window=5).mean()
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['Volatility'] = df['Returns'].rolling(window=10).std()
                df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
                df = df.dropna()
                
                features = ['Returns', 'MA5', 'MA20', 'Volatility']
                model = RandomForestClassifier(n_estimators=50, random_state=42)
                model.fit(df[features].iloc[:-1], df['Target'].iloc[:-1])
                
                prob_up = model.predict_proba(df[features].iloc[[-1]])[0][1]
                volatility = df['Volatility'].iloc[-1]
                stop_loss_dist = last_price * (volatility * 2)

                st.metric("Текущая цена", f"{last_price:.4f}")
                st.metric("Вероятность роста", f"{prob_up*100:.1f}%")
                
                st.divider()
                st.subheader("📋 Детальный торговый план:")
                
                if prob_up > 0.58:
                    st.success("🟢 РЕКОМЕНДАЦИЯ: ПОКУПАТЬ (BUY)")
                    st.write(f"**Анализ:** ИИ выявил бычий паттерн (вероятность {prob_up*100:.1f}%).")
                    st.write(f"**Вход:** {last_price:.4f}")
                    st.write(f"**Stop-Loss:** {last_price - stop_loss_dist:.4f}")
                    st.write(f"**Take-Profit:** {last_price + (stop_loss_dist * 1.5):.4f}")
                elif prob_up < 0.42:
                    st.error("🔴 РЕКОМЕНДАЦИЯ: ПРОДАВАТЬ (SELL)")
                    st.write(f"**Анализ:** ИИ выявил медвежий тренд (вероятность роста всего {(1-prob_up)*100:.1f}%).")
                    st.write(f"**Вход:** {last_price:.4f}")
                    st.write(f"**Stop-Loss:** {last_price + stop_loss_dist:.4f}")
                    st.write(f"**Take-Profit:** {last_price - (stop_loss_dist * 1.5):.4f}")
                else:
                    st.info("🟡 РЕКОМЕНДАЦИЯ: ВНЕ РЫНКА (WAIT)")
                    st.write("Рынок нестабилен, статистического преимущества нет.")
        except Exception as e:
            st.error(f"Ошибка: {e}")

