import streamlit as st

st.title("⚡ ELITE MULTI-AI SCALPER")

# Меню выбора нейросети
ai_engine = st.selectbox(
    "ВЫБЕРИТЕ НЕЙРОСЕТЬ ДЛЯ АНАЛИЗА:", 
    ["Groq (Llama 3)", "Google Gemini", "OpenRouter (Claude/DeepSeek)"]
)

# Поле для ввода ключа в зависимости от выбора
api_key = st.text_input(f"Введите API ключ для {ai_engine}:", type="password")

if st.button("🚀 ПРОВЕРИТЬ СОЕДИНЕНИЕ"):
    if not api_key:
        st.error("Ключ не введен!")
    else:
        st.success(f"Система готова к интеграции с {ai_engine}")
