import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

#gecici fonksiyon sonra değiştirecem amacım distanceyi belirelmek hangi aralık yani
def calculate_window(data, min_distance=3):
    """
    Tarih aralığına göre dinamik bir mesafe (window) hesaplar.
    :param data: DataFrame (Date sütunu olmalı)
    :param min_distance: Minimum mesafe (default: 2)
    :return: Hesaplanan mesafe
    """
    # Tarih sütununu datetime formatına çevir
    data['Date'] = pd.to_datetime(data['Date'])
    # Tarih aralığını hesapla
    start_date = data['Date'].min()
    end_date = data['Date'].max()
    date_range_years = (end_date - start_date).days / 365.25  # Toplam yıl
    return max(min_distance, int(date_range_years))

def find_local_extremes(close_prices, distance, dates):
    """
    Lokal dip ve tepe noktalarını bulur ve hem indekslerini hem de fiyat değerlerini döndürür.
    :param close_prices: Fiyatların pandas Series formatında listesi
    :param distance: Tepe/dip noktaları arasında olması gereken minimum mesafe
    :param dates: Tarihlerin pandas Series formatında listesi
    :return: (tepe_indisleri, dip_indisleri, tepe_fiyatları, dip_fiyatları, tepe_tarihleri, dip_tarihleri)
    """
    peaks, _ = find_peaks(close_prices, distance=distance)
    troughs, _ = find_peaks(-close_prices, distance=distance)

    peak_values   = close_prices.iloc[peaks].tolist()
    trough_values = close_prices.iloc[troughs].tolist()
    peak_dates    = dates.iloc[peaks].tolist()
    trough_dates  = dates.iloc[troughs].tolist()

    return peaks, troughs, peak_values, trough_values, peak_dates, trough_dates


def optimized_local_extremes(close_prices, distance, dates):
    """
    - Önce find_local_extremes ile tüm peak ve trough'ları alır.
    - Ardından tarihe (indekse) göre sıralar ve yalnızca peak→trough→peak→... ya da trough→peak→trough→... 
      ardışıklığını koruyacak şekilde filtreler.
    - Eğer iki aynı tür ekström ardışık gelirse, peak'ler için en yükseğini; trough'lar için en düşüğünü tutar.
    :param close_prices: pandas Series kapanış fiyatları
    :param distance: ekströmler arası minimum mesafe
    :param dates: pandas Series tarihleri
    :return: (opt_peaks, opt_troughs, opt_peak_vals, opt_trough_vals, opt_peak_dates, opt_trough_dates)
    """
    # 1) İlk haller
    peaks, troughs, p_vals, t_vals, p_dates, t_dates = \
        find_local_extremes(close_prices, distance, dates)

    # 2) Tümünü bir listeye toplayıp sırala
    events = []
    for idx, val, dt in zip(peaks, p_vals, p_dates):
        events.append({'type':'peak',   'index':idx, 'value':val, 'date':dt})
    for idx, val, dt in zip(troughs, t_vals, t_dates):
        events.append({'type':'trough', 'index':idx, 'value':val, 'date':dt})
    events.sort(key=lambda x: x['index'])

    # 3) Ardışık aynı tipleri elenmiş, alternation sağlanmış yeni liste
    filtered = []
    for ev in events:
        if not filtered:
            filtered.append(ev)
            continue

        last = filtered[-1]
        if ev['type'] != last['type']:
            # Tür değişmiş: ekle
            filtered.append(ev)
        else:
            # Aynı tür → peak ise yüksek olanı, trough ise düşük olanı tut
            if ev['type'] == 'peak':
                if ev['value'] > last['value']:
                    filtered[-1] = ev
            else:  # trough
                if ev['value'] < last['value']:
                    filtered[-1] = ev

    # 4) Sonuçları ayrıştır
    opt_peaks, opt_peak_vals, opt_peak_dates     = [], [], []
    opt_troughs, opt_trough_vals, opt_trough_dates = [], [], []

    for ev in filtered:
        if ev['type'] == 'peak':
            opt_peaks.append(ev['index'])
            opt_peak_vals.append(ev['value'])
            opt_peak_dates.append(ev['date'])
        else:
            opt_troughs.append(ev['index'])
            opt_trough_vals.append(ev['value'])
            opt_trough_dates.append(ev['date'])

    return (opt_peaks, opt_troughs,
            opt_peak_vals, opt_trough_vals,
            opt_peak_dates, opt_trough_dates)



def visualize_extremes(dates, close_prices, peaks, troughs):
    """
    find_local_extremes fonksiyonundan dönen tepe ve dip indekslerini fiyat grafiği üzerinde gösterir.
    """
    plt.figure(figsize=(15, 7))
    plt.plot(dates, close_prices, label='Close Price', color='gray', alpha=0.7)
    plt.scatter([dates.iloc[i] for i in peaks], [close_prices.iloc[i] for i in peaks], color='red', marker='^', s=100, label='Peaks')
    plt.scatter([dates.iloc[i] for i in troughs], [close_prices.iloc[i] for i in troughs], color='blue', marker='v', s=100, label='Troughs')
    plt.title('find_local_extremes: Peaks and Troughs')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()

def visualize_optimized_extremes(dates, close_prices, opt_peaks, opt_troughs):
    """
    optimized_local_extremes fonksiyonundan dönen tepe ve dip indekslerini fiyat grafiği üzerinde gösterir.
    """
    plt.figure(figsize=(15, 7))
    plt.plot(dates, close_prices, label='Close Price', color='gray', alpha=0.7)
    plt.scatter([dates.iloc[i] for i in opt_peaks], [close_prices.iloc[i] for i in opt_peaks], color='green', marker='^', s=100, label='Optimized Peaks')
    plt.scatter([dates.iloc[i] for i in opt_troughs], [close_prices.iloc[i] for i in opt_troughs], color='purple', marker='v', s=100, label='Optimized Troughs')
    plt.title('optimized_local_extremes: Ordered Peaks and Troughs')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()

# Veriyi yükle
df = pd.read_excel("EURUSD_1yil_Daily_Processed.xlsx")
close_prices = df['Close']
dates = pd.to_datetime(df['Date'])
# Dinamik pencere (window) hesapla
distance = calculate_window(df, min_distance=4)
peaks, troughs, peak_values, trough_values, peak_dates, trough_dates = find_local_extremes(close_prices, distance, dates)
visualize_extremes(dates, close_prices, peaks, troughs)
# Call optimized visualization
opt_peaks, opt_troughs, opt_peak_vals, opt_trough_vals, opt_peak_dates, opt_trough_dates = optimized_local_extremes(close_prices, distance, dates)
visualize_optimized_extremes(dates, close_prices, opt_peaks, opt_troughs)











def find_current_structure(current_value, previous_value, structure_type):
    """
    Mevcut tepe/dip yapısını analiz eder.
    :param current_value: Şimdiki değer (tepe veya dip)
    :param previous_value: Önceki değer (tepe veya dip)
    :param structure_type: 'low' (dip) veya 'high' (tepe) türü
    :return: 'LL', 'HL', 'LH', 'HH'
    """
    
    if structure_type == 'low':  # Dip analizi
        if float(current_value) < float(previous_value):
            return 'LL'  # Lower Low
        else:
            return 'HL'  # Higher Low
    elif structure_type == 'high':  # Tepe analizi
        if float(current_value) < float(previous_value):
            return 'LH'  # Lower High
        else:
            return 'HH'  # Higher High


def find_all_structures(close_prices, distance,dates):
    """
    Tepe ve dip noktalarının yapısını analiz eder ve sözlük formatında birleştirir.

    :param close_prices: Fiyatların pandas Series formatında listesi
    :param distance: Tepe ve dip noktaları arasındaki minimum mesafe
    :return: Sözlük formatında birleşik yapı listesi.
    """
    # Tepe ve dip noktalarını bul
    peaks, troughs, peak_values, trough_values, peak_dates, trough_dates = optimized_local_extremes(close_prices, distance,dates)

    # Dip ve tepe noktalarının trend bilgilerini saklamak için sözlük listesi
    trend_data = []

    # Uzunluğa göre en küçük listeyi temel alarak indeksleme
    for i in range(1, min(len(trough_values), len(peak_values))):
        # Dip ve tepe noktalarını sözlük formatında birleştir
        trend_data.append({
            "low": {
                "dates": trough_dates[i],
                "structure": find_current_structure(trough_values[i], trough_values[i - 1], 'low'),
                "current_value": trough_values[i],
                "previous_value": trough_values[i - 1]
            },
            "high": {
                "dates": peak_dates[i],
                "structure": find_current_structure(peak_values[i], peak_values[i - 1], 'high'),
                "current_value": peak_values[i],
                "previous_value": peak_values[i - 1]
            }
        })

    return trend_data


def find_trend_by_extremes(trend_data):
    """
    find_all_structures fonksiyonundan dönen trend_data listesini kullanarak,
    her bir yapı için bir öncekiyle karşılaştırmalı trend belirler.
    """
    for i in range(1, len(trend_data)):
        prev = trend_data[i-1]
        curr = trend_data[i]
        low_now = curr["low"]["current_value"]
        low_prev = prev["low"]["current_value"]
        high_now = curr["high"]["current_value"]
        high_prev = prev["high"]["current_value"]

        if low_now < low_prev and high_now < high_prev:
            trend = "Bearish"
        elif low_now > low_prev and high_now > high_prev:
            trend = "Bullish"
        else:
            trend = "Acumulation"
        curr["trend_by_extremes"] = trend
    # İlk elemana trend atanamaz, None bırakıyoruz
    if trend_data:
        trend_data[0]["trend_by_extremes"] = None
    return trend_data




df = pd.read_excel("EURUSD_Daily_Processed.xlsx")
close_prices = df['Close']
dates = pd.to_datetime(df['Date'])

# Dinamik pencere (window) hesapla
distance = calculate_window(df, min_distance=10)

structures = find_all_structures(close_prices, distance, dates)
trend_data = find_trend_by_extremes(structures)

print(trend_data)










