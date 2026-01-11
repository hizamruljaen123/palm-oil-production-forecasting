from flask import Flask, render_template, request, redirect, url_for, send_file, abort
import pandas as pd
import mysql.connector
import os
import io
from datetime import datetime
from utils.des import double_exponential_smoothing, calculate_mape
from pathlib import Path  # <-- Tambahkan baris ini


app = Flask(__name__)
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bulan_list = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'air_prediksi'
}

def simpan_ke_database(df):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data_produksi")
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO data_produksi (bulan, Tahun, jumlah_produksi_air_m3)
            VALUES (%s, %s, %s)
        """, (row['bulan'], int(row['Tahun']), float(row['jumlah_produksi_air_m3'])))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/dashboard/input', methods=['GET', 'POST'])
def input_dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        alpha = float(request.form.get('alpha', 0.8))
        beta = float(request.form.get('beta', 0.2))
        years = int(request.form.get('years', 2))

        if not file or not file.filename.endswith('.csv'):
            return "File CSV tidak valid."

        try:
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()

            if not all(col in df.columns for col in ['bulan', 'Tahun', 'jumlah_produksi_air_m3']):
                return "CSV harus memiliki kolom: bulan, tahun, jumlah_produksi_air_m3"

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Simpan ke tabel file_uploads
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                 INSERT INTO file_uploads (filename, upload_time)
                VALUES (%s, %s)
                """, (file.filename, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()

            simpan_ke_database(df)
            return redirect(url_for('output_dashboard', alpha=alpha, beta=beta, years=years))

        except Exception as e:
            return f"Terjadi kesalahan: {e}"

    return render_template('dashboard/input.html')

@app.route('/dashboard/output')
def output_dashboard():
    alpha = float(request.args.get('alpha', 0.8))
    beta = float(request.args.get('beta', 0.2))
    years = int(request.args.get('years', 2))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM data_produksi
        ORDER BY Tahun, FIELD(bulan, 'Januari','Februari','Maret','April','Mei','Juni',
                              'Juli','Agustus','September','Oktober','November','Desember')
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return "Tidak ada data tersedia."

    df = pd.DataFrame(rows)
    data = df['jumlah_produksi_air_m3'].tolist()

    try:
        prediksi, smooth, trend = double_exponential_smoothing(data, alpha, beta, n_preds=years * 12)
    except Exception as e:
        return f"Error dalam perhitungan DES: {e}"

    mape = calculate_mape(data, prediksi[:len(data)])

    def bersihkan(lst):
        return [0 if pd.isna(x) else round(x, 2) for x in lst]

    data = bersihkan(data)
    smooth = bersihkan(smooth)
    trend = bersihkan(trend)
    prediksi = bersihkan(prediksi)

    last_bulan = df['bulan'].iloc[-1]
    last_tahun = df['Tahun'].iloc[-1]
    bulan_index = bulan_list.index(last_bulan)
    tahun = last_tahun

    pred_labels = []
    future_tabel = []
    for i in range(years * 12):
        bulan_index += 1
        if bulan_index >= 12:
            bulan_index = 0
            tahun += 1
        label = f"{bulan_list[bulan_index]} {tahun}"
        pred_labels.append(label)
        future_tabel.append({
            'periode': label,
            'prediksi': prediksi[len(data) + i]
        })

    pred_values = prediksi[len(data):]

    hasil_tabel = []
    for i in range(len(data)):
        periode = f"{df['bulan'].iloc[i]} {df['Tahun'].iloc[i]}"
        hasil_tabel.append({
            'periode': periode,
            'aktual': data[i],
            'smoothed': smooth[i],
            'prediksi': prediksi[i]
        })

    data_table = hasil_tabel + [
        {
            'periode': f['periode'],
            'aktual': None,
            'smoothed': None,
            'prediksi': f['prediksi']
        } for f in future_tabel
    ]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data_upload_history")
    for item in data_table:
        cursor.execute("""
            INSERT INTO data_upload_history (periode, aktual, smoothed, prediksi)
            VALUES (%s, %s, %s, %s)
        """, (item['periode'], item['aktual'], item['smoothed'], item['prediksi']))
    conn.commit()
    cursor.close()
    conn.close()

    chart_labels = [item['periode'] for item in hasil_tabel] + pred_labels
    chart_aktual = [item['aktual'] for item in hasil_tabel] + [None] * len(pred_labels)
    chart_prediksi = [item['prediksi'] for item in hasil_tabel] + pred_values

    return render_template('dashboard/output.html',
        alpha=alpha,
        beta=beta,
        mape=round(mape, 2),
        data=data_table,
        chart_labels=chart_labels,
        chart_aktual=chart_aktual,
        chart_prediksi=chart_prediksi,
        pred_labels=pred_labels,
        pred_values=pred_values
    )


@app.route('/dashboard/data')
def data_dashboard():
    files = []
    data_path = Path(UPLOAD_FOLDER)
    for file in data_path.glob("*.csv"):
        files.append({
            'filename': file.name,
            'upload_time': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })

    files.sort(key=lambda x: x['upload_time'], reverse=True)
    print("FILES:", files)  # Debug
    return render_template('dashboard/data.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "File tidak ditemukan", 404

@app.route('/delete/<filename>')
def delete_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('data_dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
