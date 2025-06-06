import pandas as pd
from binance.client import Client
from datetime import datetime
import time

class LiveDataFrameCollector:
    def __init__(self, symbol="BTCUSDT", interval="1m"):
        self.client = Client()
        self.symbol = symbol
        self.interval = interval
        self.last_minute = None
        self.df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    def get_live_data(self, limit=2):
        try:
            klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            return df
        except Exception as e:
            print(f"Veri alınırken hata oluştu: {e}")
            return None

    def monitor_and_store(self):
        print(f"\n{self.symbol} için canlı veri izleme ve DataFrame'e ekleme başladı...")
        print("Çıkmak için Ctrl+C tuşlarına basın\n")
        try:
            while True:
                current_minute = datetime.now().minute
                if current_minute != self.last_minute:
                    df = self.get_live_data(limit=2)
                    if df is not None and len(df) >= 2:
                        last_data = df.iloc[-2]
                        # Eğer bu zaman daha önce eklenmediyse ekle
                        if last_data['timestamp'] not in self.df['timestamp'].values:
                            self.df = pd.concat([self.df, pd.DataFrame([last_data])], ignore_index=True)
                            print(self.df.tail())  # Son eklenenleri göster
                    self.last_minute = current_minute
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nİzleme durduruldu.")
            # Çıkarken kaydetmek istersen:
            self.df.to_excel(f"{self.symbol}_canli_veri_kayit.xlsx", index=False)
            print(f"Veriler Excel dosyasına kaydedildi: {self.symbol}_canli_veri_kayit.xlsx")

if __name__ == "__main__":
    collector = LiveDataFrameCollector(symbol="BTCUSDT", interval="1m")
    collector.monitor_and_store() 