from binance.client import Client
import pandas as pd
from datetime import datetime
import time

class BinanceAPI:
    def __init__(self):
        # API anahtarları olmadan public client oluştur
        self.client = Client()
        self.last_minute = None
    
    def get_live_data(self, symbol="BTCUSDT", interval="1m", limit=1):
        """
        Canlı veri almak için kullanılacak fonksiyon
        
        Parametreler:
        - symbol: İşlem çifti (örn: BTCUSDT, ETHUSDT)
        - interval: Zaman dilimi (1m, 5m, 15m, 30m, 1h, 4h, 1d)
        - limit: Kaç mum verisi alınacağı
        
        Dönüş:
        - DataFrame: Tarih, Açılış, Yüksek, Düşük, Kapanış, Hacim bilgilerini içeren veri seti
        """
        try:
            # Son kline verilerini al
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Veriyi DataFrame'e dönüştür
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Veri tiplerini düzenle
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Sadece ihtiyacımız olan sütunları seç
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            print(f"Veri alınırken hata oluştu: {e}")
            return None
    
    def get_all_symbols(self):
        """
        Tüm işlem çiftlerini almak için kullanılacak fonksiyon
        """
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING']
            return symbols
        except Exception as e:
            print(f"Sembol bilgileri alınırken hata oluştu: {e}")
            return None

    def monitor_live_data(self, symbol="BTCUSDT", interval="1m"):
        """
        Sürekli olarak canlı veriyi izleyen fonksiyon
        """
        print(f"\n{symbol} için canlı veri izleme başladı...")
        print("Çıkmak için Ctrl+C tuşlarına basın\n")
        
        try:
            while True:
                # Şu anki dakikayı al
                current_minute = datetime.now().minute
                
                # Eğer yeni bir dakikaya geçtiyse
                if current_minute != self.last_minute:
                    # Veriyi al
                    df = self.get_live_data(symbol=symbol, interval=interval)
                    if df is not None:
                        # Son veriyi göster
                        last_data = df.iloc[-1]
                        print(f"\nZaman: {last_data['timestamp']}")
                        print(f"Açılış: {last_data['open']:.2f}")
                        print(f"Yüksek: {last_data['high']:.2f}")
                        print(f"Düşük: {last_data['low']:.2f}")
                        print(f"Kapanış: {last_data['close']:.2f}")
                        print(f"Hacim: {last_data['volume']:.2f}")
                        print("-" * 50)
                    
                    # Son dakikayı güncelle
                    self.last_minute = current_minute
                
                # 1 saniye bekle
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nİzleme durduruldu.")

# Test için örnek kullanım
if __name__ == "__main__":
    # API nesnesini oluştur
    api = BinanceAPI()
    
    # Canlı veriyi izle
    api.monitor_live_data(symbol="BTCUSDT", interval="1m") 