import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from indicators import Indicators
from strategy import ema_crossover_strategy, simulate_ema_strategy_trades, add_risk_reward_column

# 1. VERİYİ HAZIRLA

def prepare_ml_data(df, ema_window=20, risk_reward=2):
    """
    Feature engineering ve hedef sütunu oluşturma.
    Hedef: Sinyalden sonra TP mi SL mi olmuş? (1: TP, 0: SL)
    """
    # EMA stratejisi uygula
    result = ema_crossover_strategy(df, ema_window=ema_window, risk_reward=risk_reward)
    simulated = simulate_ema_strategy_trades(result)
    simulated = add_risk_reward_column(simulated, risk_reward=risk_reward)
    # Sadece sinyal olanları al
    trades = simulated.dropna(subset=['signal']).copy()
    # Hedef sütunu: TP ise 1, SL ise 0
    trades['target'] = trades['result'].map({'TP': 1, 'SL': 0})
    # Feature engineering: EMA, RSI, MACD, fiyat, vs.
    features = [
        'Close',
        f'EMA_{ema_window}',
        'RSI_14',
        'MACD_Line',
        'Signal_Line',
        'MACD_Histogram',
    ]
    X = trades[features].fillna(0)
    y = trades['target']
    return X, y, trades

# 2. MODEL EĞİTİMİ ve TAHMİN

def train_and_evaluate_ml(X, y):
    """
    RandomForest ile model eğitimi ve değerlendirme (gerçekçi: train/test split ile).
    """
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    cr = classification_report(y_test, y_pred, output_dict=True)
    return model, cm, acc, cr

# 3. KULLANIM ÖRNEĞİ
if __name__ == "__main__":
    df = pd.read_excel("EURUSD_1yil_Daily_Processed.xlsx")
    indicators = Indicators(df)
    df_with_ind = indicators.get_all_indicators()
    risk_reward = 2
    X, y, trades = prepare_ml_data(df_with_ind, ema_window=20, risk_reward=risk_reward)
    model, cm, acc, cr = train_and_evaluate_ml(X, y)
    # trades['ml_pred'] = model.predict(X)
    # print(trades[['Date','Close','signal','result','ml_pred']]) 