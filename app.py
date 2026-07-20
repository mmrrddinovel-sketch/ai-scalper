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

# Настройка интерфейса
st.set_page_config(page_title="HackerAI Terminal", layout="wide")
st.markdown("<style>.main {background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace;}</style>", unsafe_allow_html=True)

st.title("💀 HackerAI: ALGO-ENGINE V.4.0 (FULL VERSION)")

with st.sidebar:
    st.header("⚙️ TRADE SETTINGS")
    balance = st.number_input("BALANCE ($):", value=1000.0)
    risk_pct = st.slider("RISK PER TRADE (%):", 0.1, 5.0, 1.0)
    selected_name = st.selectbox("ASSET:", ["GOLD (XAUUSD)", "EUR/USD", "BITCOIN"])
    ai_model = st.selectbox("CORE:", ["Groq (Llama 3)", "Google Gemini", "Claude"])
    api_key = st.text_input("API KEY:", type="password")

def get_ticker(name):
    return "GC=F" if "GOLD" in name else "EURUSD=X" if "EUR" in name else "BTC-USD"

# Стратегия для PyAlgoTrade
class VSAStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(VSAStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        self.trend = "FLAT"
    def onBars(self, bars):
        bar = bars[self.__instrument]
        if self.__sma[-1] is not None:
            self.trend = "BULLISH" if bar.getClose() > self.__sma[-1] else "BEARISH"

def run_analysis(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1d", progress=False)
        if data.empty: return "NO DATA", 0.0
        
        # Сохраняем в память для PyAlgoTrade
        data.to_csv("market.csv")
        feed = yahoofeed.Feed()
        feed.addBarsFromCSV(symbol, "market.csv")
        strat = VSAStrategy(feed, symbol)
        strat.run()
        
        price = float(data['Close'].iloc[-1])
        return strat.trend, price
    except: return "ERROR", 0.0

trend, price = run_analysis(get_ticker(selected_name))

col1, col2 = st.columns(2)
col1.metric("LIVE PRICE:", f"{price:,.2f}")
col2.metric("ALGO TREND:", trend)

if st.button("💀 EXECUTE HACK"):
    if not api_key: st.error("ВВЕДИТЕ API КЛЮЧ")
    elif price == 0.0: st.error("MARKET ERROR")
    else:
        with st.spinner("HackerAI: Analyzing..."):
            prompt = f"""
            Ты — HackerAI. АНАЛИЗ ДЛЯ СКАЛЬПИНГА.
            АКТИВ: {selected_name}, ЦЕНА: {price}, ТРЕНД: {trend}.
            БАЛАНС: {balance}$, РИСК: {risk_pct}%.
            1. СИГНАЛ: LONG/SHORT/WAIT.
            2. ПАРАМЕТРЫ: Entry={price}, SL={price*0.999}, TP={price*1.002}.
            3. ЛОТ: Рассчитай лот для риска {risk_pct}% от {balance}$.
            """
            try:
                if ai_model == "Google Gemini":
                    genai.configure(api_key=api_key)
                    st.code(genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text)
                else: st.info("Используйте Gemini для быстрого ответа.")
            except Exception as e: st.error(f"FAIL: {e}")
