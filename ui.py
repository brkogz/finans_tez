import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
import time
from streamlit_autorefresh import st_autorefresh
import os

# Modülleri import et
# from veri_onisleme import preprocess_data
from structers import find_all_structures, find_trend_by_extremes, visualize_optimized_extremes
from visualize import plot_structures, plot_trend_by_extremes
from indicators import plot_indicators, Indicators
from ml import prepare_ml_data, train_and_evaluate_ml
from strategy import ema_crossover_strategy, simulate_ema_strategy_trades, add_risk_reward_column, sum_risk_reward, plot_ema_strategy_trades
from candlestick import plot_candlestick
from destek_direnc import find_support_resistance_levels, plot_candlestick_with_sr

TELEGRAM_TOKEN = "7575130658:AAGFkjMI-33mre8ejWfnM-x4Hak1RY3Y7Vg"
TELEGRAM_CHAT_ID = "1698539573"

def send_telegram_message(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram bildirimi gönderilemedi: {e}")

def data_preparation(uploaded_file):
    # Dosya uzantısına göre oku
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file, delimiter='\t', header=0)
    else:
        data = pd.read_excel(uploaded_file)

    columns = data.columns.tolist()
    if 'TIME' in [col.upper().replace('<','').replace('>','') for col in columns]:
        # Alt zaman dilimi: DATE + TIME var
        data.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'TickVolume', 'Volume', 'Spread']
        data = data[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
        data['Date'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], errors='coerce')
        data = data.drop(['Time'], axis=1)
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
    else:
        # Sadece günlük: DATE var
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume', 'Volume', 'Spread']
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data['Date'] = data['Date'].dt.date

    return data

def get_binance_ohlc(symbol="BTCUSDT", interval="1m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    df = df.rename(columns={
        'timestamp': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'TickVolume'
    })
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
    return df

# Hazır veri setleri klasörü ve dosya isimleri
veri_seti_klasoru = "."
hazir_dosyalar = [
    "BTCUSD_Daily.csv",
    "ETHUSD_Daily.csv",
    "SOLUSD_Daily.csv",
    "EURUSD_Daily.csv",
    "SPX500_Daily.csv",
    "USDJPY_Daily.csv",
    "USOIL_Daily.csv",
    "XAUUSD_Daily.csv"
]

st.set_page_config(page_title="Finansal Analiz & ML Demo", layout="wide")
st.title("📊 Finansal Zaman Serisi Analiz ve Makine Öğrenmesi")

# --- Veri Yükleme ve Ön İşleme ---
st.sidebar.header("Veri Yükle")
data_source = st.sidebar.radio("Veri Kaynağı Seçin", ["Dosya Yükle", "Canlı Veri"])

if data_source == "Dosya Yükle":
    uploaded_file = st.sidebar.file_uploader("Excel/CSV dosyası yükle", type=["xlsx", "csv"])
    st.sidebar.markdown("---")
    st.sidebar.write("veya hazır veri seti seçin:")
    secili_hazir = st.sidebar.selectbox("Hazır Veri Setleri", hazir_dosyalar)
    if uploaded_file:
        df = data_preparation(uploaded_file)
    else:
        dosya_yolu = os.path.join(veri_seti_klasoru, secili_hazir)
        with open(dosya_yolu, "rb") as f:
            df = data_preparation(f)
else:
    st.sidebar.header("Canlı Veri Ayarları")
    # Sembol selectbox'u buraya taşındı
    populer_semboller = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "AVAXUSDT", "MINAUSDT", "SUIUSDT", "DOTUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "MATICUSDT", "OPUSDT", "LINKUSDT", "PEPEUSDT", "SHIBUSDT"
    ]
    symbol = st.sidebar.selectbox("Sembol", populer_semboller, index=0)
    interval = st.sidebar.selectbox("Zaman Dilimi", ["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
    df = get_binance_ohlc(symbol=symbol, interval=interval, limit=100)

st.subheader("Veri Önizleme")
st.dataframe(df.head())

st.sidebar.header("Parametreler")
risk_reward = st.sidebar.number_input("Risk/Ödül Oranı (R)", min_value=1, max_value=10, value=3, step=1)

# --- Sekmeler ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Yapı Analizi", "İndikatörler", "Strateji", "Makine Öğrenmesi", "Görselleştirme", "Trend Analizi", "Canlı Veri"
])

with tab1:
    st.header("Yapı Analizi")
    structures = find_all_structures(df['Close'], distance=10, dates=df['Date'])
    trend_data = find_trend_by_extremes(structures)
    st.dataframe(trend_data)
    # optimized_local_extremes için parametreleri hazırla
    from structers import optimized_local_extremes
    opt_peaks, opt_troughs, opt_peak_vals, opt_trough_vals, opt_peak_dates, opt_trough_dates = optimized_local_extremes(df['Close'], 10, df['Date'])
    fig = visualize_optimized_extremes(df['Date'], df['Close'], opt_peaks, opt_troughs)
    st.pyplot(fig)

with tab2:
    st.header("İndikatörler")
    indicators = Indicators(df)
    df_with_ind = indicators.get_all_indicators()
    st.dataframe(df_with_ind.tail())
    fig = plot_indicators(df_with_ind, indicators)
    st.pyplot(fig)

with tab3:
    st.header("Strateji")
    result = ema_crossover_strategy(df_with_ind, ema_window=20, risk_reward=risk_reward)
    simulated = simulate_ema_strategy_trades(result)
    simulated = add_risk_reward_column(simulated, risk_reward=risk_reward)
    total_r = sum_risk_reward(simulated['rr_result'], risk_reward=risk_reward)
    # Sadece TP/SL olan işlemleri kontrol et
    valid_trades = simulated[simulated['rr_result'].isin([f"+{risk_reward}R", "-1R"])]
    if valid_trades.empty:
        st.warning(f"Bu veri seti için bu risk/ödül oranı ({risk_reward}) desteklenmiyor. Lütfen daha küçük bir değer giriniz.")
    else:
        st.write(f"Toplam R: **{total_r}**")
        st.dataframe(valid_trades[['Date','Close','signal','stop_loss','take_profit','result','rr_result']])
        fig = plot_ema_strategy_trades(simulated, ema_window=20)
        st.pyplot(fig)

with tab4:
    st.header("Makine Öğrenmesi")
    X, y, trades = prepare_ml_data(df_with_ind, ema_window=20, risk_reward=risk_reward)
    X = X.replace([np.inf, -np.inf], np.nan).dropna()
    y = y.loc[X.index]
    # Sadece X ve y tamamen doluysa modeli eğit
    if X.empty or y.empty or X.isnull().values.any() or y.isnull().values.any():
        st.warning(f"Bu veri seti için bu risk/ödül oranı ({risk_reward}) desteklenmiyor. Lütfen daha küçük bir değer giriniz.")
    else:
        model, cm, ml_acc, cr = train_and_evaluate_ml(X, y)
        trades['ml_pred'] = model.predict(X)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"ML Doğruluk: **{ml_acc:.2%}**")
            fig_cm, ax = plt.subplots(figsize=(3, 3))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=False)
            ax.set_xlabel('Tahmin')
            ax.set_ylabel('Gerçek')
            ax.set_title('Confusion Matrix')
            st.pyplot(fig_cm)
        with col2:
            st.dataframe(trades[['Date','Close','signal','result','ml_pred']].dropna())

with tab5:
    st.header("Görselleştirme")
    st.subheader("Fiyat Mum Grafiği + Destek/Direnç")
    if data_source == "Canlı Veri":
        df_viz = df.copy()
        df_viz = df_viz.drop_duplicates(subset='Date')
        df_viz = df_viz.sort_values('Date')
        df_viz = df_viz.reset_index(drop=True)
        df_viz = df_viz.dropna()
        df_viz = df_viz.tail(50)  # Son 50 mum
        st.info("Canlı veri ile sade fiyat çizgi grafiği ve destek/direnç seviyeleri gösteriliyor.")
        min_price = df_viz['Close'].min() - 100
        max_price = df_viz['Close'].max() + 100
        supports, resistances = find_support_resistance_levels(df_viz, price_col='Close', order=10, tolerance=0.002)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_viz['Date'], df_viz['Close'], color='dodgerblue', label='Close')
        ax.set_ylim(min_price, max_price)
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Fiyat')
        ax.set_title('Canlı Veri - Fiyat Çizgi Grafiği')
        # Destek ve dirençleri çiz
        for s in supports:
            ax.axhline(s, color='deepskyblue', linestyle='--', linewidth=1, alpha=0.7, label='Destek')
        for r in resistances:
            ax.axhline(r, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='Direnç')
        # Tek seferlik legend için
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
        plt.xticks(rotation=30)
        st.pyplot(fig)
    else:
        supports, resistances = find_support_resistance_levels(df, price_col='Close', order=10, tolerance=0.002)
        if len(supports) == 0 or len(resistances) == 0 or np.any(np.isnan(supports)) or np.any(np.isnan(resistances)):
            st.warning(f"Bu veri seti için bu risk/ödül oranı ({risk_reward}) desteklenmiyor. Lütfen daha küçük bir değer giriniz.")
        else:
            fig = plot_candlestick_with_sr(df, supports, resistances)
            st.pyplot(fig)

with tab6:
    st.header("Trend Analizi")
    # Trend analizi için gerekli verileri hazırla
    structures = find_all_structures(df['Close'], distance=10, dates=df['Date'])
    trend_data = find_trend_by_extremes(structures)
    fig = plot_trend_by_extremes(df['Date'], df['Close'], trend_data)
    st.pyplot(fig)

with tab7:
    st.header("Canlı Veri Analizi")
    # Otomatik yenileme anahtarı
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False
    # Son gönderilen sinyalin id'sini tut
    if "last_signal_id" not in st.session_state:
        st.session_state.last_signal_id = None

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Otomatik Yenilemeyi Aç/Kapat"):
            st.session_state.auto_refresh = not st.session_state.auto_refresh
    with col2:
        if st.session_state.auto_refresh:
            st.success("Otomatik yenileme açık (her 1 dakikada bir).")
        else:
            st.info("Otomatik yenileme kapalı.")

    # Otomatik yenileme aktifse, 60 saniyede bir sayfa yenile
    if st.session_state.auto_refresh:
        st_autorefresh(interval=60 * 1000, key="otorefresh")

    if data_source == "Canlı Veri":
        st.subheader(f"{symbol} - {interval} Son Veriler")
        st.dataframe(df.tail())
        indicators = Indicators(df)
        df_with_ind = indicators.get_all_indicators()
        result = ema_crossover_strategy(df_with_ind, ema_window=20, risk_reward=risk_reward)
        simulated = simulate_ema_strategy_trades(result)
        st.subheader("Son Sinyaller")
        last_signals = simulated[simulated['signal'] != 0].tail(5)
        # Sütun isimlerini kısalt ve sayısal değerleri kısalt
        if 'take_profit' in last_signals.columns:
            last_signals = last_signals.rename(columns={'take_profit': 'TP'})
        if 'stop_loss' in last_signals.columns:
            last_signals = last_signals.rename(columns={'stop_loss': 'SL'})
        cols = ['Date', 'Close', 'signal', 'TP', 'SL']
        for col in cols:
            if col not in last_signals.columns:
                last_signals[col] = None
        # TP, SL ve Close'u 6 ondalık basamakla göster
        for col in ['TP', 'SL', 'Close']:
            if col in last_signals.columns:
                last_signals[col] = last_signals[col].apply(lambda x: f"{float(x):.6f}" if pd.notnull(x) else None)
        st.dataframe(last_signals[cols], use_container_width=True)
        # Sütun adlarını kontrol et
        # st.write('DataFrame sütunları:', df.columns)

        # Eğer 'signal' yoksa ekle
        if 'signal' not in df.columns:
            df['signal'] = None

        # Session state başlat
        if 'last_sent_signal' not in st.session_state:
            st.session_state['last_sent_signal'] = None

        # Son sinyalleri içeren DataFrame'den son satırı al
        if not last_signals.empty:
            last_signal_row = last_signals.iloc[-1]
            last_signal = last_signal_row['signal']
            st.write('Son sinyal:', last_signal)
            # Sinyal kontrolü: None, 'None', boş string ve tekrar kontrolü
            if last_signal and str(last_signal).lower() != 'none' and str(last_signal).strip() != '' and st.session_state.get('last_sent_signal') != last_signal:
                tp = last_signal_row.get('TP', '')
                sl = last_signal_row.get('SL', '')
                close = last_signal_row['Close']
                def fmt6(x):
                    try:
                        return f"{float(x):.6f}"
                    except:
                        return x
                msg = (
                    f"{symbol} | Risk/Ödül: {risk_reward}\n"
                    f"{last_signal_row['Date']} tarihinde {last_signal.upper()} sinyali!\n"
                    f"Fiyat: {fmt6(close)} TP: {fmt6(tp)} SL: {fmt6(sl)}"
                )
                st.write('Telegram bildirimi gönderiliyor:', msg)
                send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
                st.session_state['last_sent_signal'] = last_signal
        else:
            st.write('Son sinyal: None')

        if st.button("Verileri Yenile"):
            st.experimental_rerun()
    if st.button("Verileri Excel'e Kaydet"):
        df.to_excel(f"{symbol}_{interval}_canli_veri.xlsx", index=False)
        st.success("Veriler kaydedildi!")
