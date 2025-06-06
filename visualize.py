import matplotlib.pyplot as plt

def visualize_all_structures(trend_data):
    
    # Verileri ayrıştır
    highs_x = [data["high"]["dates"] for data in trend_data]
    highs_y = [data["high"]["current_value"] for data in trend_data]
    lows_x = [data["low"]["dates"] for data in trend_data]
    lows_y = [data["low"]["current_value"] for data in trend_data]

    # Yapıları etiketle
    high_labels = [data["high"]["structure"] for data in trend_data]
    low_labels = [data["low"]["structure"] for data in trend_data]

    # Grafik oluştur
    plt.figure(figsize=(14, 7))

    # Tepe noktalarını çiz
    plt.scatter(highs_x, highs_y, color='red', label='Tepe Noktası', s=15, alpha=0.7)
    for i, label in enumerate(high_labels):
        plt.text(highs_x[i], highs_y[i], label, fontsize=6, color='red', ha='left', va='bottom')

    # Dip noktalarını çiz
    plt.scatter(lows_x, lows_y, color='green', label='Dip Noktası', s=15, alpha=0.7)
    for i, label in enumerate(low_labels):
        plt.text(lows_x[i], lows_y[i], label, fontsize=6, color='green', ha='right', va='top')

    # Grafik detayları
    plt.title("Trend Yapılarının Görselleştirilmesi", fontsize=16)
    plt.xlabel("Tarih", fontsize=12)
    plt.ylabel("Fiyat", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(alpha=0.5)
    plt.tight_layout()

    # Grafiği göster
    # plt.show()
    return plt.gcf()


# Örnek çağrı
# trend_data = find_all_structures(close_prices, distance, dates)
# visualize_all_structures(trend_data)


def visualize_all_structures_v2(dates, close_prices, trend_data):
    """
    Daha net ve anlaşılır bir tepe ve dip noktaları görselleştirme fonksiyonu.

    :param dates: Fiyatların tarih bilgilerinin pandas Series formatında listesi.
    :param close_prices: Fiyatların pandas Series formatında listesi.
    :param trend_data: find_all_structures fonksiyonundan dönen yapılandırılmış trend verileri.
    """
    plt.figure(figsize=(16, 8))
    plt.plot(dates, close_prices, label="Close Prices", color="blue", alpha=0.7)

    # Tepe ve dip noktalarını işaretle
    for data in trend_data:
        # Dip noktaları (yeşil)
        plt.scatter(data["low"]["dates"], data["low"]["current_value"], color="green", s=50,
                    label="Troughs" if "Troughs" not in plt.gca().get_legend_handles_labels()[1] else "")
        plt.annotate(f"{data['low']['structure']}",
                     (data["low"]["dates"], data["low"]["current_value"]),
                     textcoords="offset points", xytext=(-10, 10), ha='center', fontsize=8, color="green")

        # Tepe noktaları (kırmızı)
        plt.scatter(data["high"]["dates"], data["high"]["current_value"], color="red", s=50,
                    label="Peaks" if "Peaks" not in plt.gca().get_legend_handles_labels()[1] else "")
        plt.annotate(f"{data['high']['structure']}",
                     (data["high"]["dates"], data["high"]["current_value"]),
                     textcoords="offset points", xytext=(10, -10), ha='center', fontsize=8, color="red")

    # Grafik düzenlemeleri
    plt.title("Trend Analysis Visualization", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.xticks(rotation=45)  # Tarihlerin daha net görünmesi için eğimli gösterim
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()  # Eksik kenar boşluklarını düzenler
    # plt.show()
    return plt.gcf()

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
    # plt.show()
    return plt.gcf()


def plot_trend_market(trend_market, close_prices, dates):
    """
    Trend market verilerini görselleştirir.
    :param trend_market: market_structure fonksiyonundan dönen trend market verileri
    :param close_prices: Kapanış fiyatları
    :param dates: Tarihler
    """
    import matplotlib.dates as mdates
    
    plt.figure(figsize=(15, 7))
    
    # Kapanış fiyatlarını çiz
    plt.plot(dates, close_prices, label='Close Price', color='gray', alpha=0.5)
    
    # Her bir trend yapısı için MSB ve BOS noktalarını işaretle
    for structure in trend_market:
        msb_date = structure["MSB"]["dates"]
        msb_price = structure["MSB"]["price"]
        bos_date = structure["BOS"]["dates"]
        bos_price = structure["BOS"]["price"]
        trend = structure["Trend"]
        
        # Trend rengini belirle
        color = 'green' if trend == 'Bullish' else 'red'
        
        # MSB ve BOS noktalarını işaretle
        plt.scatter(msb_date, msb_price, color=color, s=100, marker='^' if trend == 'Bullish' else 'v', label=f'{trend} MSB')
        plt.scatter(bos_date, bos_price, color=color, s=100, marker='o', label=f'{trend} BOS')
        
        # MSB ve BOS arasında çizgi çiz
        plt.plot([msb_date, bos_date], [msb_price, bos_price], color=color, linestyle='--', alpha=0.5)
    
    # Grafik ayarları
    plt.title('Trend Market Structure')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, alpha=0.3)
    
    # Tarih formatını ayarla
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    
    # Tekrarlanan etiketleri kaldır
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    
    plt.tight_layout()
    # plt.show()
    return plt.gcf()

def plot_structures(dates, close_prices, structures):
    """
    find_structure fonksiyonundan dönen yapıları görselleştirir.
    HL ve HH noktalarını yeşil, LL ve LH noktalarını kırmızı gösterir.
    High noktaları yukarı üçgen (^), low noktaları aşağı üçgen (v) ile gösterilir.
    """
    plt.figure(figsize=(15, 7))
    plt.plot(dates, close_prices, color='gray', alpha=0.5, label='Close Price')

    for structure in structures:
        # Low noktası
        low_date = structure['low']['dates']
        low_value = structure['low']['current_value']
        low_structure = structure['low']['structure']
        # High noktası
        high_date = structure['high']['dates']
        high_value = structure['high']['current_value']
        high_structure = structure['high']['structure']

        # Low için renk ve marker
        if low_structure == "HL":
            color_low = 'green'
        elif low_structure == "LL":
            color_low = 'red'
        else:
            color_low = 'gray'
        plt.scatter(low_date, low_value, color=color_low, s=100, marker='v', label=f'Low: {low_structure}')

        # High için renk ve marker
        if high_structure == "HH":
            color_high = 'green'
        elif high_structure == "LH":
            color_high = 'red'
        else:
            color_high = 'gray'
        plt.scatter(high_date, high_value, color=color_high, s=100, marker='^', label=f'High: {high_structure}')

    plt.title('Market Structure Analysis')
    plt.xlabel('Date')
    plt.ylabel('Price')
    # Legend tekrarını önle
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # plt.show()
    return plt.gcf()


def plot_trend_by_extremes(dates, close_prices, trend_data):
    """
    find_trend_by_extremes fonksiyonundan dönen trend_data listesini fiyat grafiği üzerinde
    trend tipine göre (Bullish, Bearish, Acumulation) renklendirerek gösterir.
    """
    plt.figure(figsize=(15, 7))
    plt.plot(dates, close_prices, color='gray', alpha=0.5, label='Close Price')

    color_map = {
        "Bullish": 'green',
        "Bearish": 'red',
        "Acumulation": 'blue'
    }

    for i, struct in enumerate(trend_data):
        if i == 0:
            continue  # İlk elemana trend atanamaz
        trend = struct.get("trend_by_extremes", "Acumulation")
        low_date = struct["low"]["dates"]
        high_date = struct["high"]["dates"]
        low_value = struct["low"]["current_value"]
        high_value = struct["high"]["current_value"]

        # Trend rengine göre noktaları çiz
        plt.scatter(low_date, low_value, color=color_map[trend], marker='v', s=100, label=f"{trend} Low" if i == 1 else "")
        plt.scatter(high_date, high_value, color=color_map[trend], marker='^', s=100, label=f"{trend} High" if i == 1 else "")

        # İki yapı arası arka planı renklendir (isteğe bağlı)
        if i > 0:
            prev_date = trend_data[i-1]["high"]["dates"]
            plt.axvspan(prev_date, high_date, color=color_map[trend], alpha=0.08)

    # Legend tekrarını önle
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.title('Trend by Extremes')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # plt.show()
    return plt.gcf()