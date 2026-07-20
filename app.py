import streamlit as st
import yfinance as yf
import pandas as pd
import os
import time
from groq import Groq
import google.generativeai as genai
from anthropic import Anthropic
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma

# --- НАСТРОЙКА ИНТЕРФЕЙСА ---
st.set_page_config(page_title="HackerAI Terminal", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ALGO-ENGINE V.4.0 (PyAlgoTrade)")

# --- НАСТРОЙКИ В БОКОВОЙ ПАНЕЛИ ---
with st.sidebar:
    st.header("⚙️ TRADE SETTINGS")
    balance = st.number_input("ACCOUNT BALANCE ($):", min_value=10.0, value=1000.0)
    risk_pct = st.slider("RISK PER TRADE (%):", 0.1, 5.0, 1.0)
    selected_name = st.selectbox("ASSET:", ["GOLD (XAUUSD)", "EUR/USD", "BITCOIN"])
    ai_model = st.selectbox("CORE:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("API KEY:", type="password")

# --- ЛОГИКА ТИКЕРОВ ---
def get_ticker(asset_name):
    if "GOLD" in asset_name: return "GC=F"
    if "EUR" in asset_name: return "EURUSD=X"
    return "BTC-USD"

ticker = get_ticker(selected_name)

# --- БАЗОВАЯ СТРАТЕГИЯ PYALGOTRADE ---
class VSAStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(VSAStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        self.trend = "FLAT"

    def onBars(self, bars):
        bar = bars[self.__instrument]
        if self.__sma[-1] is not None:
            if bar.getClose() > self.__sma[-1]:
                self.trend = "BULLISH (UPTREND)"
            elif bar.getClose() < self.__sma[-1]:
                self.trend = "BEARISH (DOWNTREND)"

# --- ГЕНЕРАЦИЯ ДАННЫХ И АНАЛИЗ ---
def run_pyalgotrade_analysis(symbol):
    try:
        # 1. Скачиваем данные за последние 5 дней
        data = yf.download(symbol, period="5d", interval="1d", progress=False)
        if data.empty: return "Нет данных для PyAlgoTrade", 0.0
        
        # 2. Подготавливаем CSV для PyAlgoTrade (формат Yahoo)
        csv_file = "market_data.csv"
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
        data['Adj Close'] = data['Close']
        data.to_csv(csv_file, index=False)
        
        # 3. Запускаем PyAlgoTrade
        feed = yahoofeed.Feed()
        feed.addBarsFromCSV(symbol, csv_file)
        strat = VSAStrategy(feed, symbol)
        strat.run()
        
        # Убираем временный файл
        if os.path.exists(csv_file): os.remove(csv_file)
        
        current_price = float(data['Close'].iloc[-1])
        return strat.trend, current_price
    except Exception as e:
        return f"Ошибка PyAlgoTrade: {e}", 0.0

# --- ГЛАВНЫЙ ЭКРАН ---
trend_status, price = run_pyalgotrade_analysis(ticker)

col1, col2 = st.columns(2)
with col1: st.metric("LIVE PRICE:", f"{price:,.2f}")
with col2: st.metric("ALGO TREND (PyAlgoTrade):", trend_status)

# --- ЗАПУСК ХАКЕРА ---
if st.button("💀 EXECUTE HACK"):
    if not api_key: 
        st.error("ACCESS DENIED: ВВЕДИТЕ API КЛЮЧ")
    elif price == 0.0:
        st.error("MARKET OFFLINE: Не удалось получить цену.")
    else:
        with st.spinner("HackerAI: Компиляция данных PyAlgoTrade и генерация сигнала..."):
            
            prompt = f"""
            Ты — HackerAI. Эксперт по скальпингу (FxPro).
            АКТИВ: {selected_name}
            ЦЕНА: {price}
            АЛГО-ТРЕНД (от PyAlgoTrade): {trend_status}
            БАЛАНС: {balance}$ | РИСК: {risk_pct}%
            
            Выдай сухой отчет 'HACKED':
            1. [!] MARKET STATE: Учти алго-тренд {trend_status}.
            2. [!] VSA SIGNAL: Анализ текущей цены.
            3. [!] DECISION: LONG / SHORT / WAIT
            4. [!] MT5 COMMANDS: Entry={price}, SL=(рассчитай 0.15% от цены), TP=(рассчитай 0.3% от цены)
            5. [!] RISK-LOT: Рассчитай точный объем лота в MT5, чтобы потеря при SL не превышала {risk_pct}% от {balance}$.
            """
            try:
                if ai_model == "Groq (Llama 3)":
                    res = Groq(api_key=api_key).chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    st.code(res.choices[0].message.content)
                elif ai_model == "Google Gemini":
                    genai.configure(api_key=api_key)
                    st.code(genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text)
                elif ai_model == "Claude":
                    res = Anthropic(api_key=api_key).messages.create(model="claude-3-haiku-20240307", max_tokens=350, messages=[{"role": "user", "content": prompt}])
                    st.code(res.content[0].text)
            except Exception as e:
                st.error(f"SYSTEM FAILURE: {e}")
