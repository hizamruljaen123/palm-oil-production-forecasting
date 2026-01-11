from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash, jsonify
import pandas as pd
import mysql.connector
import os
from datetime import datetime
from pathlib import Path
import numpy as np
from werkzeug.utils import secure_filename
import uuid
from auth import login_required, admin_required, verify_user, create_user
from dropbox_integration import list_csv_files_from_dropbox, download_csv_from_dropbox, get_file_info_dropbox, upload_file_to_dropbox, check_dropbox_connection

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Ganti dengan secret key yang aman
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

# Alpha & Beta options (0.1 .. 0.9 step 0.1)
ALPHA_OPTIONS = [round(x/10.0, 1) for x in range(1, 10)]
BETA_OPTIONS = ALPHA_OPTIONS.copy()

bulan_list = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'data_air'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===============================
# Double Exponential Smoothing (Holt) - improved initialisation
# ===============================
def double_exponential_smoothing(data, alpha, beta, n_preds=24, recursive=False):
    """
    Implementasi Holt's linear method.
    Jika `recursive=True`, masa depan diprediksi secara iteratif dan level/trend diperbarui
    menggunakan nilai prediksi sebelumnya.
    """
    n = len(data)
    if n < 2:
        raise ValueError("Data harus memiliki setidaknya dua poin.")

    result = []
    smoothed = []
    trend = []

    # Inisialisasi otomatis: L1 = X1, T1 = X2 - X1
    level = float(data[0])
    slope = float(data[1]) - float(data[0])

    smoothed.append(level)
    trend.append(slope)
    # Forecast pertama adalah L1 + T1 (menunjukkan F2)
    result.append(level + slope)

    for i in range(1, n):
        last_level = level
        last_trend = slope

        # Update level & trend (Holt)
        level = alpha * float(data[i]) + (1 - alpha) * (level + slope)
        slope = beta * (level - last_level) + (1 - beta) * slope

        # Forecast untuk waktu i (menggunakan level & trend sebelumnya)
        forecast = last_level + last_trend

        smoothed.append(level)
        trend.append(slope)
        result.append(forecast)

    # Prediksi ke depan
    if not recursive:
        for m in range(1, n_preds + 1):
            future_forecast = level + m * slope
            result.append(future_forecast)
        for m in range(1, n_preds + 1):
            smoothed.append(level)
            trend.append(slope)
    else:
        last_level = level
        last_trend = slope
        for m in range(1, n_preds + 1):
            forecast = last_level + last_trend
            result.append(forecast)

            # Treat forecast as observation
            new_level = alpha * forecast + (1 - alpha) * (last_level + last_trend)
            new_trend = beta * (new_level - last_level) + (1 - beta) * last_trend

            smoothed.append(new_level)
            trend.append(new_trend)

            last_level = new_level
            last_trend = new_trend

    return result, smoothed, trend

# ===============================
# MAPE
# ===============================
def calculate_mape(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted[:len(actual)])

    # Abaikan APE pertama (mulai dari indeks ke-1)
    if len(actual) <= 1:
        return None
    actual = actual[1:]
    predicted = predicted[1:]

    mask = actual != 0
    if not mask.any():
        return None

    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    return mape

# ===============================
# Simpan CSV ke database
# ===============================
def simpan_ke_database(df):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data_produksi")
    for _, row in df.iterrows():
        # pastikan tipe data aman (jika ada float -> int cast dengan round)
        jumlah = int(round(float(row['jumlah_produksi_air_m3'])))
        cursor.execute("""
            INSERT INTO data_produksi (bulan, Tahun, jumlah_produksi_air_m3)
            VALUES (%s, %s, %s)
        """, (row['bulan'], int(row['Tahun']), jumlah))
    conn.commit()
    cursor.close()
    conn.close()

# ===============================
# Authentication Routes
# ===============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user.get('full_name', username)
            flash(f'Selamat datang, {session["full_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # Regular users go directly to output dashboard (view-only)
    if session.get('role') != 'admin':
        return redirect(url_for('output_dashboard'))
    # Admins see the home page
    return render_template('home.html', user=session)

@app.route('/dashboard/input', methods=['GET', 'POST'])
@admin_required
def input_dashboard():
    if request.method == 'POST':
        # Get alpha and beta from dropdowns (0.1 .. 0.9)
        try:
            alpha = float(request.form.get('alpha', 0.5))
            beta = float(request.form.get('beta', 0.3))
        except Exception:
            flash('Nilai α / β tidak valid.', 'warning')
            return redirect(url_for('input_dashboard'))

        if alpha not in ALPHA_OPTIONS or beta not in BETA_OPTIONS:
            flash('Nilai α / β harus salah satu dari 0.1 sampai 0.9.', 'warning')
            return redirect(url_for('input_dashboard'))
        years = int(request.form.get('years', 2))
        
        # Check data source: Google Drive, manual upload, or database
        data_source = request.form.get('data_source', 'upload')
        
        df = None
        filename_to_save = None
        stored_filename_to_use = None
        
        if data_source == 'dropbox':
            # Dropbox file
            file_path = request.form.get('dropbox_file_id') # We use path as ID
            if not file_path:
                flash('Silakan pilih file dari Dropbox.', 'warning')
                return redirect(url_for('input_dashboard'))
            
            try:
                df = download_csv_from_dropbox(file_path)
                file_info = get_file_info_dropbox(file_path)
                filename_to_save = file_info['name'] if file_info else 'dropbox_file.csv'
            except Exception as e:
                flash(f'Gagal mengunduh file dari Dropbox: {e}', 'danger')
                return redirect(url_for('input_dashboard'))

        elif data_source == 'server_file':
            # File from server 'data' folder
            stored_filename = request.form.get('server_filename')
            if not stored_filename:
                flash('Silakan pilih file dari server.', 'warning')
                return redirect(url_for('input_dashboard'))
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
            if not os.path.exists(filepath):
                 flash('File fisik tidak ditemukan di server.', 'danger')
                 return redirect(url_for('input_dashboard'))
            
            try:
                df = pd.read_csv(filepath)
                stored_filename_to_use = stored_filename
            except Exception as e:
                flash(f'Gagal membaca file dari server: {e}', 'danger')
                return redirect(url_for('input_dashboard'))

        elif data_source == 'database_last':
            # Data from 'data_upload_history' table
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT periode, aktual FROM data_upload_history WHERE aktual IS NOT NULL")
                rows = cursor.fetchall()
                cursor.close()
                conn.close()

                if not rows:
                     flash('Tidak ada data tersimpan di database.', 'warning')
                     return redirect(url_for('input_dashboard'))
                
                # Reconstruct DataFrame: periode "Januari 2020" -> bulan="Januari", Tahun=2020
                data_list = []
                for row in rows:
                    parts = row['periode'].split(' ')
                    if len(parts) >= 2:
                        bulan = parts[0]
                        tahun = parts[1]
                        jumlah = row['aktual']
                        data_list.append({'bulan': bulan, 'Tahun': tahun, 'jumlah_produksi_air_m3': jumlah})
                
                df = pd.DataFrame(data_list)
                filename_to_save = 'database_history.csv' # Virtual filename
            except Exception as e:
                flash(f'Gagal mengambil data dari database: {e}', 'danger')
                return redirect(url_for('input_dashboard'))
        
        else:
            # Manual upload (available for all users)
            file = request.files.get('file')
            if not file or file.filename == '':
                flash('File CSV tidak valid.', 'warning')
                return redirect(url_for('input_dashboard'))
            
            if not allowed_file(file.filename):
                flash('File harus berekstensi .csv', 'warning')
                return redirect(url_for('input_dashboard'))
            
            try:
                # Read file for processing
                df = pd.read_csv(file)
                filename_to_save = secure_filename(file.filename)
                
                # Checkbox Upload ke Dropbox
                if request.form.get('upload_to_dropbox') == 'yes':
                    try:
                        # Reset pointer file agar bisa dibaca lagi
                        file.seek(0)
                        file_bytes = file.read()
                        
                        # Upload ke Dropbox
                        upload_res = upload_file_to_dropbox(file_bytes, filename_to_save)
                        if upload_res:
                            flash('File berhasil dibackup ke Dropbox!', 'success')
                        else:
                            flash('Gagal backup ke Dropbox.', 'warning')
                            
                        # Reset pointer lagi untuk pd.read_csv (walaupun df sudah dibuat di atas, 
                        # tapi good practice jika ada operasi lain yang butuh baca file lagi)
                        file.seek(0)
                        
                    except Exception as e:
                        print(f"Error uploading to Dropbox in route: {e}")
                        flash(f"Gagal backup ke Dropbox: {e}", 'warning')
                        
            except Exception as e:
                flash(f'Gagal membaca file CSV: {e}', 'danger')
                return redirect(url_for('input_dashboard'))
        
        # Validate and process DataFrame
        if df is None:
            flash('Gagal memproses data.', 'danger')
            return redirect(url_for('input_dashboard'))
        
        try:
            df.columns = df.columns.str.strip()
            if not all(col in df.columns for col in ['bulan', 'Tahun', 'jumlah_produksi_air_m3']):
                flash('CSV harus memiliki kolom: bulan, Tahun, jumlah_produksi_air_m3', 'warning')
                return redirect(url_for('input_dashboard'))
            
            # Save file if it's new (Gdrive or Upload)
            if filename_to_save:
                unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + uuid.uuid4().hex[:6]
                stored_filename = f"{Path(filename_to_save).stem}_{unique_suffix}{Path(filename_to_save).suffix}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
                df.to_csv(filepath, index=False)
                
                # Save file info to database
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO file_uploads (filename, stored_filename, upload_time, uploaded_by)
                    VALUES (%s, %s, %s, %s)
                """, (filename_to_save, stored_filename, datetime.now(), session.get('username')))
                conn.commit()
                cursor.close()
                conn.close()
            
            simpan_ke_database(df)
            flash('Data berhasil diproses!', 'success')
            # `selected_option` doesn't exist here; derive an `option_name` safely
            option_name = request.form.get('option_name')
            if not option_name:
                # Prefer the original filename (if uploaded or from dropbox),
                # then stored server filename, otherwise fall back to 'Custom'
                option_name = filename_to_save or stored_filename_to_use or 'Custom'
            # Include whether to use recursive forecasting (iterative) in the redirect
            recursive_flag = '1' if request.form.get('recursive') == '1' else '0'
            return redirect(url_for('output_dashboard', alpha=alpha, beta=beta, years=years, option_name=option_name, recursive=recursive_flag))
        except Exception as e:
            flash(f'Terjadi kesalahan: {e}', 'danger')
            return redirect(url_for('input_dashboard'))
    
    # GET request - show form
    dropbox_files = []
    local_files = []
    
    # Check Dropbox Connection
    dropbox_connected = check_dropbox_connection()
    if dropbox_connected:
        # Fetch Dropbox files only if connected
        try:
            dropbox_files = list_csv_files_from_dropbox()
            flash('Terhubung ke Dropbox.', 'success')
        except Exception as e:
            print(f"Error listing Dropbox files: {e}")
    else:
        flash('Gagal terhubung ke Dropbox. Cek koneksi internet atau token API.', 'warning')

    # Fetch Local Files
    local_files = []
    try:
        data_path = Path(app.config['UPLOAD_FOLDER'])
        for file in data_path.glob("*.csv"):
             # Get basic info
             stats = file.stat()
             local_files.append({
                 'filename': file.name,
                 'size': f"{stats.st_size / 1024:.2f} KB",
                 'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
             })
        # Sort by modified desc
        local_files.sort(key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        print(f"Error listing local files: {e}")
    
    return render_template('dashboard/input.html', 
                         alpha_options=ALPHA_OPTIONS,
                         beta_options=BETA_OPTIONS,
                         dropbox_files=dropbox_files,
                         local_files=local_files,
                         dropbox_connected=dropbox_connected,
                         user=session)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        full_name = request.form.get('full_name', '').strip()

        if not username or not password:
            flash('Username dan password harus diisi.', 'warning')
            return redirect(url_for('register'))

        if password != password2:
            flash('Password dan konfirmasi tidak cocok.', 'warning')
            return redirect(url_for('register'))

        success = create_user(username, password, role='user', full_name=full_name)
        if success:
            flash('Pendaftaran berhasil. Silakan login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Gagal membuat akun. Mungkin username sudah ada.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dashboard/output')
@login_required
def output_dashboard():
    years = int(request.args.get('years', 2))

    # If user is admin and alpha/beta provided (admin triggered prediction), recalc & save
    if session.get('role') == 'admin' and ('alpha' in request.args or 'option_name' in request.args or True):
        # allow admin to pass alpha & beta as args or via defaults
        alpha = float(request.args.get('alpha', 0.8))
        beta = float(request.args.get('beta', 0.2))
        # Get recursive flag from request args
        recursive = request.args.get('recursive', '0') == '1'

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
        # Normalize column names (strip + case-insensitive mapping)
        df.columns = [c.strip() for c in df.columns]
        col_map = {}
        # map Tahun
        if 'Tahun' not in df.columns:
            for c in df.columns:
                if c.lower() in ('tahun', 'year'):
                    col_map[c] = 'Tahun'
                    break
        # map bulan
        if 'bulan' not in df.columns:
            for c in df.columns:
                if c.lower() == 'bulan':
                    col_map[c] = 'bulan'
                    break
        # map jumlah_produksi_air_m3 (accept variants)
        if 'jumlah_produksi_air_m3' not in df.columns:
            for c in df.columns:
                low = c.lower()
                if 'jumlah' in low or 'produksi' in low or 'm3' in low:
                    col_map[c] = 'jumlah_produksi_air_m3'
                    break
        if col_map:
            df = df.rename(columns=col_map)

        # Ensure required columns exist now
        required = ['bulan', 'Tahun', 'jumlah_produksi_air_m3']
        for r in required:
            if r not in df.columns:
                return f"Kolom diperlukan tidak ditemukan di data: {r}", 400

        data = [int(x) for x in df['jumlah_produksi_air_m3'].tolist()]

        # Hitung prediksi dengan parameter recursive
        prediksi, smooth, trend = double_exponential_smoothing(data, alpha, beta, n_preds=years * 12, recursive=recursive)
        mape = calculate_mape(data, prediksi[:len(data)])

        # Bersihkan NaN -> tetap gunakan None supaya template bisa menampilkan '-'
        def bersihkan_na(lst):
            return [None if pd.isna(x) else x for x in lst]

        data_clean = bersihkan_na(data)
        smooth_clean = bersihkan_na(smooth)
        trend_clean = bersihkan_na(trend)
        prediksi_clean = bersihkan_na(prediksi)

        # ===============================
        # Format L, T, F per periode (historis)
        # ===============================
        hasil_manual = []
        for i in range(len(data_clean)):
            periode = f"{df['bulan'].iloc[i]} {df['Tahun'].iloc[i]}"
            L = round(smooth_clean[i], 2) if smooth_clean[i] is not None else None
            T = round(trend_clean[i], 2) if trend_clean[i] is not None else None
            F = round(prediksi_clean[i], 2) if i > 0 and prediksi_clean[i] is not None else None  # Kosongkan prediksi pertama
            hasil_manual.append({'periode': periode, 'L': L, 'T': T, 'F': F})

        # Prediksi ke depan
        future_manual = []
        bulan_index = bulan_list.index(df['bulan'].iloc[-1])
        tahun = int(df['Tahun'].iloc[-1])
        for i in range(years * 12):
            bulan_index += 1
            if bulan_index >= 12:
                bulan_index = 0
                tahun += 1
            periode = f"{bulan_list[bulan_index]} {tahun}"
            future_index = len(data_clean) + i
            # Jika smoothed/trend masa depan tersedia (recursive mode), gunakan itu
            if future_index < len(smooth_clean):
                L_val = smooth_clean[future_index]
                T_val = trend_clean[future_index]
            else:
                L_val = smooth_clean[-1] if smooth_clean else None
                T_val = trend_clean[-1] if trend_clean else None

            L = round(L_val, 2) if L_val is not None else None
            T = round(T_val, 2) if T_val is not None else None
            F = round(prediksi_clean[future_index], 2) if prediksi_clean[future_index] is not None else None
            future_manual.append({'periode': periode, 'L': L, 'T': T, 'F': F})

        full_manual = hasil_manual + future_manual

        # ===============================
        # Simpan data DES ke tabel history
        # ===============================
        data_table = []
        for i in range(len(data_clean)):
            data_table.append({
                'periode': f"{df['bulan'].iloc[i]} {df['Tahun'].iloc[i]}",
                'aktual': data_clean[i],
                'smoothed': round(smooth_clean[i],2) if smooth_clean[i] is not None else None,
                'prediksi': round(prediksi_clean[i],2) if i > 0 and prediksi_clean[i] is not None else None  # Kosongkan prediksi pertama
            })

        for i, f in enumerate(future_manual):
            data_table.append({
                'periode': f['periode'],
                'aktual': None,
                'smoothed': None,
                'prediksi': f['F']
            })

        # Simpan ke history (hapus sebelumnya lalu insert baru)
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

        chart_labels = [item['periode'] for item in data_table]
        chart_aktual = [item['aktual'] for item in data_table]
        chart_prediksi = [item['prediksi'] for item in data_table]

        # Render template based on role
        template_name = 'dashboard/output.html' if session.get('role') == 'admin' else 'dashboard/output_user.html'
        
        return render_template(template_name,
                               alpha=alpha, beta=beta, mape=(round(mape, 2) if mape is not None else None),
                               data=data_table, chart_labels=chart_labels,
                               chart_aktual=chart_aktual, chart_prediksi=chart_prediksi,
                               full_manual=full_manual,
                               option_name=request.args.get('option_name', 'Custom'),
                               user=session)

    # Non-admin users: show last saved results from data_upload_history (read-only)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT periode, aktual, smoothed, prediksi FROM data_upload_history ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        flash('Belum ada hasil prediksi yang dijalankan admin.', 'info')
        return render_template('dashboard/output_user.html', data=[], chart_labels=[], chart_aktual=[], chart_prediksi=[], full_manual=[], alpha=None, beta=None, mape=None, option_name='Saved', user=session)

    # Build data_table & charts from rows
    data_table = []
    chart_labels = []
    chart_aktual = []
    chart_prediksi = []
    for r in rows:
        data_table.append({'periode': r['periode'], 'aktual': r['aktual'], 'smoothed': r['smoothed'], 'prediksi': r['prediksi']})
        chart_labels.append(r['periode'])
        chart_aktual.append(r['aktual'])
        chart_prediksi.append(r['prediksi'])

    return render_template('dashboard/output_user.html', data=data_table, chart_labels=chart_labels, chart_aktual=chart_aktual, chart_prediksi=chart_prediksi, full_manual=[], alpha=None, beta=None, mape=None, option_name='Saved', user=session)

# ===============================
# Data CSV
# ===============================
@app.route('/dashboard/data')
@login_required
def data_dashboard():
    files = []
    data_path = Path(UPLOAD_FOLDER)
    # Ambil dari DB agar lebih rapi (menyimpan original dan stored nama)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT filename, stored_filename, upload_time FROM file_uploads ORDER BY upload_time DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for r in rows:
            files.append({
                'original_name': r['filename'],
                'stored_name': r['stored_filename'],
                'upload_time': r['upload_time'].strftime('%Y-%m-%d %H:%M:%S')
            })
    except Exception:
        # fallback: baca dari filesystem jika DB bermasalah
        for file in data_path.glob("*.csv"):
            files.append({
                'original_name': file.name,
                'stored_name': file.name,
                'upload_time': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return render_template('dashboard/data.html', files=files)

@app.route('/download/<stored_filename>')
def download_file(stored_filename):
    filepath = os.path.join(UPLOAD_FOLDER, stored_filename)
    if os.path.exists(filepath):
        # pastikan file terbaca — kirim sebagai binary; send_file sudah menangani ini
        return send_file(filepath, as_attachment=True)
    return "File tidak ditemukan", 404

@app.route('/delete/<stored_filename>')
def delete_file(stored_filename):
    filepath = os.path.join(UPLOAD_FOLDER, stored_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    # juga hapus catatan di DB (jika ada)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_uploads WHERE stored_filename = %s", (stored_filename,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass
    return redirect(url_for('data_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
