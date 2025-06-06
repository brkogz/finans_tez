# Finansal Zaman Serisi Analiz ve Makine Öğrenmesi Uygulaması

Bu uygulama, finansal zaman serisi verileri üzerinde teknik analiz, otomatik strateji sinyalleri, makine öğrenmesi ve canlı veri takibi yapmanızı sağlar. Streamlit tabanlıdır ve hem dosya yükleme hem de canlı Binance verisiyle çalışır.

## 🚀 Özellikler

- **Dosya Yükle:** Kendi veri dosyanızı (CSV/XLSX) yükleyin veya hazır veri setlerinden birini seçin.
- **Canlı Veri:** Binance Futures üzerinden popüler coinlerde anlık veri çekin.
- **Yapı Analizi:** Tepe/dip, trend ve market structure analizi.
- **İndikatörler:** RSI, MACD, ATR, EMA, SMA gibi teknik göstergeler.
- **Strateji:** EMA crossover tabanlı otomatik al/sat sinyalleri ve risk/ödül analizi.
- **Makine Öğrenmesi:** Sinyal sonrası TP/SL tahmini için RandomForest ile ML eğitimi.
- **Görselleştirme:** Mum grafiği, destek/direnç, trend ve yapı görselleştirmeleri.
- **Telegram Bildirimi:** Yeni sinyal oluştuğunda otomatik Telegram mesajı.
- **Hazır Veri Setleri:** Demo için hızlıca analiz başlatabileceğiniz örnek veri dosyaları.

## 📦 Kurulum

1. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uygulamayı başlatın:**
   ```bash
   streamlit run ui.py
   ```

3. **(Opsiyonel) Telegram bildirimi için:**
   - `TELEGRAM_TOKEN` ve `TELEGRAM_CHAT_ID` değişkenlerini kendi bot bilgilerinizle güncelleyin.

## 📁 Dosya Yapısı

- `ui.py` : Ana Streamlit uygulaması
- `api.py`, `dataframe.py` : Binance canlı veri ve veri toplama
- `indicators.py`, `strategy.py`, `ml.py` : Teknik analiz, strateji ve makine öğrenmesi
- `structers.py`, `destek_direnc.py`, `candlestick.py`, `visualize.py` : Yapı, destek/direnç ve grafik fonksiyonları
- `veri_onisleme.py` : Dosya ön işleme
- `requirements.txt` : Bağımlılıklar
- `README.md` : Bu dosya
- `BTCUSD_Daily.csv`, ... : Hazır veri setleri

## 📝 Kullanım

1. **Veri Yükle:**  
   - Kendi dosyanızı yükleyin veya hazır veri setlerinden birini seçin.
2. **Parametreleri Ayarla:**  
   - Sembol, zaman dilimi, risk/ödül oranı gibi ayarları yapın.
3. **Sekmeler Arasında Gezin:**  
   - Yapı analizi, indikatörler, strateji, ML, görselleştirme, trend ve canlı veri sekmelerini kullanın.
4. **Telegram Bildirimi:**  
   - Canlı veri sekmesinde yeni sinyal oluştuğunda otomatik bildirim alın.

## 💡 Notlar

- Hazır veri setleri ana klasörde olmalı.
- Büyük veri dosyalarında performans için satır sayısını azaltabilirsiniz.
- Kod modülerdir, kolayca yeni strateji veya indikatör ekleyebilirsiniz.

---

**Herhangi bir sorun veya geliştirme öneriniz olursa iletişime geçebilirsiniz!** 
mail= 201805050@stu.adu.edu.tr
Berk OĞUZ