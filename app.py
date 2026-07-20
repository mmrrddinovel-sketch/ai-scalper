def neural_ai_engine(data):
    # Создаем DataFrame
    df = pd.DataFrame(data)
    # Вычисляем признаки
    df['returns'] = df.iloc[:, 0].pct_change()
    df['volatility'] = df.iloc[:, 0].rolling(10).std()
    df['ema_fast'] = df.iloc[:, 0].ewm(span=5).mean()
    df['ema_slow'] = df.iloc[:, 0].ewm(span=20).mean()
    
    # --- ИСПРАВЛЕНИЕ: Удаляем все пустые значения ---
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    # -----------------------------------------------
    
    if len(df) < 20: return "🟡 Инициализация...", "#ffff00", "Мало данных"
    
    # Целевая переменная
    df['target'] = (df.iloc[:, 0].shift(-5) > df.iloc[:, 0]).astype(int)
    df.dropna(inplace=True)
    
    X = df[['returns', 'volatility', 'ema_fast', 'ema_slow']]
    y = df['target']
    
    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X, y)
    
    prediction = model.predict([X.iloc[-1]])
    proba = model.predict_proba([X.iloc[-1]])[0][1]
    
    if prediction == 1 and proba > 0.6:
        return "🟢 BUY SIGNAL", "#00ff00", f"Conf: {proba:.2%}"
    elif prediction == 0 and proba < 0.4:
        return "🔴 SELL SIGNAL", "#ff0000", f"Conf: {1-proba:.2%}"
    
    return "🟡 NEUTRAL", "#ffff00", "Низкая уверенность"
