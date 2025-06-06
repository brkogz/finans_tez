import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Indicators:
    def __init__(self, data):
        self.data = data.copy()
        
    def calculate_rsi(self, window=14):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.data[f'RSI_{window}'] = 100 - (100 / (1 + rs))
        return self.data[f'RSI_{window}']
    
    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        self.data['MACD_Line'] = self.data['Close'].ewm(span=short_window, adjust=False).mean() - \
                                 self.data['Close'].ewm(span=long_window, adjust=False).mean()
        self.data['Signal_Line'] = self.data['MACD_Line'].ewm(span=signal_window, adjust=False).mean()
        self.data['MACD_Histogram'] = self.data['MACD_Line'] - self.data['Signal_Line']
        return self.data[['MACD_Line', 'Signal_Line', 'MACD_Histogram']]
    
    def calculate_atr(self, window=14):
        high_low = self.data['High'] - self.data['Low']
        high_close = abs(self.data['High'] - self.data['Close'].shift(1))
        low_close = abs(self.data['Low'] - self.data['Close'].shift(1))
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.data[f'ATR_{window}'] = true_range.rolling(window=window).mean()
        return self.data[f'ATR_{window}']
    
    def calculate_sma(self, window=20):
        self.data[f'SMA_{window}'] = self.data['Close'].rolling(window=window).mean()
        return self.data[f'SMA_{window}']
    
    def calculate_ema(self, window=20):
        self.data[f'EMA_{window}'] = self.data['Close'].ewm(span=window, adjust=False).mean()
        return self.data[f'EMA_{window}']
    
    def calculate_rsi_with_bands(self, window=14, ma_window=7):
        self.calculate_rsi(window)
        self.data[f'RSI_MA_{ma_window}'] = self.data[f'RSI_{window}'].rolling(window=ma_window).mean()
        self.data['RSI_Upper'] = 70
        self.data['RSI_Middle'] = 50
        self.data['RSI_Lower'] = 30
        return self.data[[f'RSI_{window}', f'RSI_MA_{ma_window}', 'RSI_Upper', 'RSI_Middle', 'RSI_Lower']]
    
    def get_all_indicators(self):
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_atr()
        self.calculate_sma(window=20)
        self.calculate_ema(window=20)
        self.calculate_rsi_with_bands()
        return self.data 

def plot_indicators(data, indicators):
    """
    İndikatörleri görselleştirme
    :param data: DataFrame
    :param indicators: Indicators sınıfı instance'ı
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [3, 1, 1]})

    # Fiyat grafiği ve hareketli ortalamalar
    ax1.plot(data['Date'], data['Close'], label='Close', color='gray', alpha=0.7)
    ax1.plot(data['Date'], data['SMA_20'], label='SMA 20', color='blue', alpha=0.7)
    ax1.plot(data['Date'], data['EMA_20'], label='EMA 20', color='red', alpha=0.7)
    ax1.set_title('Price and Moving Averages')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # MACD
    ax2.plot(data['Date'], data['MACD_Line'], label='MACD', color='blue')
    ax2.plot(data['Date'], data['Signal_Line'], label='Signal', color='red')
    macd_hist = data['MACD_Histogram']
    ax2.bar(data['Date'][macd_hist >= 0], macd_hist[macd_hist >= 0], label='Histogram+', color='green', alpha=0.5)
    ax2.bar(data['Date'][macd_hist < 0], macd_hist[macd_hist < 0], label='Histogram-', color='red', alpha=0.5)
    ax2.set_title('MACD')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # RSI
    ax3.plot(data['Date'], data['RSI_14'], label='RSI', color='purple')
    ax3.axhline(y=70, color='r', linestyle='--', alpha=0.3)
    ax3.axhline(y=30, color='g', linestyle='--', alpha=0.3)
    ax3.set_title('RSI')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


df = pd.read_excel("EURUSD_1yil_Daily_Processed.xlsx")
indicators = Indicators(df)
df_with_indicators = indicators.get_all_indicators()
plot_indicators(df_with_indicators, indicators)
