import pandas as pd


def data_preparation(file_path):
    # File pathi belirleme
    file_path = f"{file_path}_Daily.csv"

    # Veriyi tab ('\t') ile ayrılmış olarak okuma
    data = pd.read_csv(file_path, delimiter='\t', header=0)

    # Sütun isimlerini otomatik algıla
    columns = data.columns.tolist()

    # Sütun isimlerini düzenle (günlük ve alt zaman dilimi için)
    if 'TIME' in [col.upper().replace('<','').replace('>','') for col in columns]:
        # Alt zaman dilimi: DATE + TIME var
        data.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'TickVolume', 'Volume', 'Spread']
        # Gereksiz sütunları kaldırma
        data = data[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
        # Tarih ve saat sütununu birleştirip Date olarak adlandır
        data['Date'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], errors='coerce')
        data = data.drop(['Time'], axis=1)
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
    else:
        # Sadece günlük: DATE var
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume', 'Volume', 'Spread']
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'TickVolume']]
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data['Date'] = data['Date'].dt.date

    # Düzenlenmiş veriyi tekrar Excel'e kaydetme
    output_file_path = "{}_Processed.xlsx".format(file_path.split(".csv")[0].split("/")[-1])
    data.to_excel(output_file_path, index=False)

    print(f"Veri başarıyla {output_file_path} olarak kaydedildi.")

if __name__ == "__main__":
    data_preparation("EURUSD_1yil")
