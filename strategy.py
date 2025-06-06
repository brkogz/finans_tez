import pandas as pd
import matplotlib.pyplot as plt

# EMA tabanlı basit strateji

def ema_crossover_strategy(data, ema_window=20, stop_buffer=0.001, risk_reward=2):
    """
    Fiyat EMA'nın üstüne çıkınca buy, altına inince sell sinyali üretir.
    Stop loss, EMA'nın biraz üstü/altı, take profit ise stop mesafesinin 2 katı olur.
    :param data: DataFrame (Close ve EMA_{ema_window} sütunları olmalı)
    :param ema_window: EMA penceresi
    :param stop_buffer: Stop mesafesi için EMA'ya eklenecek buffer (ör: 0.001)
    :param risk_reward: TP/SL oranı
    :return: Sinyal, stop ve tp seviyeleri eklenmiş DataFrame
    """
    ema_col = f'EMA_{ema_window}'
    df = data.copy()
    df['signal'] = None
    df['stop_loss'] = None
    df['take_profit'] = None

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]
        ema = df[ema_col].iloc[i]
        prev_price = df['Close'].iloc[i-1]
        prev_ema = df[ema_col].iloc[i-1]

        # Buy sinyali: fiyat EMA'nın altından üstüne geçerse
        if prev_price < prev_ema and price > ema:
            df.at[df.index[i], 'signal'] = 'buy'
            stop = ema - stop_buffer
            tp = price + risk_reward * (price - stop)
            df.at[df.index[i], 'stop_loss'] = stop
            df.at[df.index[i], 'take_profit'] = tp
        # Sell sinyali: fiyat EMA'nın üstünden altına geçerse
        elif prev_price > prev_ema and price < ema:
            df.at[df.index[i], 'signal'] = 'sell'
            stop = ema + stop_buffer
            tp = price - risk_reward * (stop - price)
            df.at[df.index[i], 'stop_loss'] = stop
            df.at[df.index[i], 'take_profit'] = tp
    return df




def simulate_ema_strategy_trades(df, price_col='Close'):
    """
    EMA stratejisiyle üretilen sinyallerin TP mi SL mi olduğunu simüle eder.
    Her sinyalden sonra, fiyat hareketini izler ve önce TP mi SL mi tetiklenmiş belirler.
    Sonuçları df'ye 'result' sütunu olarak ekler.
    """
    df = df.copy()
    df['result'] = None

    signals = df.dropna(subset=['signal']).index

    for idx in signals:
        signal = df.at[idx, 'signal']
        entry_price = df.at[idx, price_col]
        stop = df.at[idx, 'stop_loss']
        tp = df.at[idx, 'take_profit']

        # Sinyalden sonraki barlardan itibaren bak
        for j in range(idx+1, len(df)):
            price = df.at[df.index[j], price_col]
            if signal == 'buy':
                if price >= tp:
                    df.at[idx, 'result'] = 'TP'
                    break
                elif price <= stop:
                    df.at[idx, 'result'] = 'SL'
                    break
            elif signal == 'sell':
                if price <= tp:
                    df.at[idx, 'result'] = 'TP'
                    break
                elif price >= stop:
                    df.at[idx, 'result'] = 'SL'
                    break
    return df

def add_risk_reward_column(df, risk_reward=2):
    """
    TP olursa +risk_reward*R, SL olursa -1R olarak yeni bir sütun ekler.
    """
    df = df.copy()
    rr_list = []
    for idx, row in df.iterrows():
        if row['result'] == 'TP':
            rr_list.append(f"+{risk_reward}R")
        elif row['result'] == 'SL':
            rr_list.append("-1R")
        else:
            rr_list.append("")
    df['rr_result'] = rr_list
    return df 

def sum_risk_reward(rr_results, risk_reward=2):
    """
    rr_result sütunundaki +xR ve -1R değerlerini toplar.
    :param rr_results: DataFrame'in 'rr_result' sütunu veya bir liste
    :param risk_reward: TP için kullanılan risk/ödül oranı (ör: 2 veya 3)
    :return: Toplam R kazancı/zararı (float)
    """
    total = 0
    for val in rr_results:
        if val == f"+{risk_reward}R":
            total += risk_reward
        elif val == "-1R":
            total -= 1
    return total

from indicators import Indicators
df = pd.read_excel("EURUSD_1yil_Daily_Processed.xlsx")
indicators = Indicators(df)
df_with_ind = indicators.get_all_indicators()
risk_reward = 5  # veya istediğin oran
result = ema_crossover_strategy(df_with_ind, ema_window=20, risk_reward=risk_reward)
simulated = simulate_ema_strategy_trades(result)
simulated = add_risk_reward_column(simulated, risk_reward=risk_reward)
print(simulated[['Date','Close','signal','stop_loss','take_profit','result','rr_result']].dropna())

total_r = sum_risk_reward(simulated['rr_result'], risk_reward=risk_reward)
print(f"Toplam R: {total_r}")

def plot_ema_strategy_trades(df, ema_window=20):
    """
    EMA stratejisi işlemlerini fiyat grafiği üzerinde gösterir.
    Buy/sell sinyalleri, TP ve SL sonuçları renkli olarak işaretlenir.
    """
    plt.figure(figsize=(15, 7))
    plt.plot(df['Date'], df['Close'], label='Close', color='gray', alpha=0.7)
    plt.plot(df['Date'], df[f'EMA_{ema_window}'], label=f'EMA {ema_window}', color='blue', alpha=0.7)

    # Buy sinyalleri
    buys = df[df['signal'] == 'buy']
    plt.scatter(buys['Date'], buys['Close'], marker='^', color='green', s=100, label='Buy Signal')

    # Sell sinyalleri
    sells = df[df['signal'] == 'sell']
    plt.scatter(sells['Date'], sells['Close'], marker='v', color='red', s=100, label='Sell Signal')

    # TP ve SL sonuçları
    tp = df[df['result'] == 'TP']
    sl = df[df['result'] == 'SL']
    plt.scatter(tp['Date'], tp['take_profit'], marker='*', color='lime', s=150, label='Take Profit (TP)')
    plt.scatter(sl['Date'], sl['stop_loss'], marker='x', color='darkred', s=100, label='Stop Loss (SL)')

    plt.title('EMA Crossover Strategy Trades')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()

plot_ema_strategy_trades(simulated, ema_window=20)

