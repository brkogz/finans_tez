import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd

def plot_candlestick(df, date_col='Date', open_col='Open', high_col='High', low_col='Low', close_col='Close'):
    """
    Klasik mum grafiği (candlestick) çizer. Yükselen mumlar yeşil, düşenler kırmızı olur.
    :param df: OHLC içeren DataFrame
    :return: fig
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    fig, ax = plt.subplots(figsize=(15, 7))
    width = 0.6  # mum gövdesi genişliği
    width2 = 0.1 # iğne genişliği
    for idx, row in df.iterrows():
        o = row[open_col]
        h = row[high_col]
        l = row[low_col]
        c = row[close_col]
        date = row[date_col]
        color = 'green' if c >= o else 'red'
        # Mum gövdesi
        ax.add_patch(Rectangle((mdates.date2num(date) - width/2, min(o, c)),
                               width, abs(c - o), color=color, alpha=0.8))
        # İğneler
        ax.plot([mdates.date2num(date), mdates.date2num(date)], [l, h], color=color, linewidth=1.5)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.set_title('Mum Grafiği (Candlestick)', fontsize=16)
    ax.set_xlabel('Tarih')
    ax.set_ylabel('Fiyat')
    ax.grid(alpha=0.3)
    return fig 