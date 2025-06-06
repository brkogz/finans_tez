import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import argrelextrema

def find_support_resistance_levels(df, price_col='Close', order=10, tolerance=0.002):
    """
    Lokal ekstremumlara göre destek ve direnç seviyelerini bulur ve yakın seviyeleri gruplayarak sadeleştirir.
    :param df: Fiyat verisi DataFrame'i
    :param price_col: Kullanılacak fiyat sütunu (genelde 'Close')
    :param order: Ekstremum arama penceresi (kaç bar sağ/sol daha büyük/küçük olmalı)
    :param tolerance: Yakın seviyeleri gruplayacak tolerans oranı (ör: 0.002 = %0.2)
    :return: (destekler, dirençler)
    """
    prices = df[price_col].values
    # Lokal min ve max bul
    min_idx = argrelextrema(prices, np.less, order=order)[0]
    max_idx = argrelextrema(prices, np.greater, order=order)[0]
    supports = prices[min_idx]
    resistances = prices[max_idx]
    # Yakın seviyeleri grupla
    def group_levels(levels):
        levels = sorted(levels)
        grouped = []
        for lvl in levels:
            if not grouped or abs(lvl - grouped[-1]) > tolerance * lvl:
                grouped.append(lvl)
        return grouped
    return group_levels(supports), group_levels(resistances)

def plot_candlestick_with_sr(df, supports, resistances, date_col='Date', open_col='Open', high_col='High', low_col='Low', close_col='Close'):
    """
    Mum grafiği ile birlikte destek ve direnç seviyelerini çizer.
    """
    from candlestick import plot_candlestick
    fig = plot_candlestick(df, date_col, open_col, high_col, low_col, close_col)
    ax = fig.gca()
    for s in supports:
        ax.axhline(s, color='blue', linestyle='--', alpha=0.6, label='Destek')
    for r in resistances:
        ax.axhline(r, color='orange', linestyle='--', alpha=0.6, label='Direnç')
    # Tekrarlanan legend'ları önle
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    return fig
