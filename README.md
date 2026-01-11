# NISA - Sistem Prediksi Kebutuhan Air PDAM

Sistem prediksi kebutuhan air menggunakan metode **Double Exponential Smoothing (Holt's Method)** dengan fitur login multi-level dan integrasi Dropbox.

## 🆕 Fitur Baru

### 1. **Sistem Login dengan Dua Level Akses**
- **Admin**: Akses penuh termasuk upload manual file CSV
- **User**: Akses untuk melihat dan menggunakan data dari Dropbox

### 2. **Integrasi Dropbox**
- Upload data tidak lagi manual
- File CSV dapat diambil langsung dari Dropbox
- Backup otomatis ke Dropbox saat upload manual
- Sinkronisasi otomatis dengan cloud storage

### 3. **Parameter Alpha & Beta**
- Alpha (α) dan Beta (β) sekarang dipilih **satu-per-satu** dari pilihan nilai 0.1 sampai 0.9 (step 0.1).
  Pilih kombinasi yang sesuai dengan karakteristik data.

## 📋 Persyaratan Sistem

- Python 3.8+
- MySQL/MariaDB
- Akun Dropbox dan Dropbox App Key/Secret

## 🔧 Instalasi

### 1. Install Dependencies

```bash
pip install flask pandas mysql-connector-python numpy werkzeug dropbox
```

### 2. Setup Database

Jalankan script SQL untuk membuat database dan tabel:

```bash
mysql -u root -p < database_setup.sql
```

Atau import manual melalui phpMyAdmin/MySQL Workbench.

### 3. Buat User Default

Jalankan script untuk membuat user admin dan user biasa:

```bash
python create_users.py
```

Pilih opsi 1 untuk membuat user default:
- **Admin**: username=`admin`, password=`admin123`
- **User**: username=`user`, password=`user123`

### 4. Konfigurasi Dropbox

Integrasi Dropbox sudah dikonfigurasi secara otomatis menggunakan App Key dan Secret yang tertanam di aplikasi.
Pastikan file CSV yang ingin diproses berada di folder aplikasi Dropbox Anda (misal: `/Apps/aplikasi_nisa/`).

## 🚀 Menjalankan Aplikasi

```bash
python app.py
```

Aplikasi akan berjalan di: `http://localhost:5000`

## 👤 Login

### Default Accounts

**Admin Account:**
- Username: `admin`
- Password: `admin123`
- Akses: Full access (upload manual + Dropbox)

**User Account:**
- Username: `user`
- Password: `user123`
- Akses: Dropbox only

⚠️ **PENTING**: Ganti password default setelah login pertama!

## 📁 Struktur File CSV

File CSV harus memiliki format berikut:

```csv
bulan,Tahun,jumlah_produksi_air_m3
Januari,2020,150000
Februari,2020,155000
Maret,2020,160000
...
```

**Kolom yang diperlukan:**
- `bulan`: Nama bulan (Januari, Februari, dst.)
- `Tahun`: Tahun (format: 2020, 2021, dst.)
- `jumlah_produksi_air_m3`: Jumlah produksi air dalam m³ (integer)

## 🎯 Cara Penggunaan

### 1. Login
- Akses `http://localhost:5000`
- Masukkan username dan password
- Klik **Login**

### 1.a Registrasi
- Fitur pendaftaran akun tersedia di halaman login (klik **Daftar**). Akun baru otomatis berperan sebagai `user` dan hanya dapat melihat hasil prediksi yang sudah dijalankan admin.

### 2. Input Data

#### Opsi A: Dropbox (Admin & User)
1. Klik **Mulai Prediksi**
2. Pilih **Dropbox** sebagai sumber data
3. Pilih file CSV dari dropdown
4. Pilih parameter smoothing (α & β)
5. Pilih tahun prediksi
6. Klik **Proses Prediksi**

#### Opsi B: Upload Manual (Admin Only)
1. Klik **Mulai Prediksi**
2. Pilih **Upload Manual**
3. Upload file CSV dari komputer
4. (Opsional) Centang **Upload ke Dropbox** untuk backup
5. Pilih parameter smoothing (α & β)
6. Pilih tahun prediksi
7. Klik **Proses Prediksi**

- ### 3. Lihat Hasil
- Grafik prediksi vs aktual
- Tabel perhitungan DES (L, T, F)
- Nilai MAPE (Mean Absolute Percentage Error)
- Prediksi untuk periode mendatang

Note: Hanya admin yang dapat menjalankan prediksi (upload/processing). Pengguna biasa hanya dapat melihat hasil prediksi terakhir yang disimpan oleh admin.

### 4. Kelola Data
- Menu **Data** untuk melihat file yang sudah diupload
- Download atau hapus file CSV
- Lihat history upload

## 🔐 Keamanan

- Password di-hash menggunakan `werkzeug.security`
- Session management dengan Flask sessions
- Role-based access control (RBAC)
- Secret key untuk session encryption
- Token Dropbox aman

⚠️ **Ganti secret key di `app.py`:**
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

## 📊 Parameter Smoothing

### Alpha (α)
- Mengontrol seberapa responsif model terhadap data terbaru
- Nilai tinggi (0.7-0.9): Lebih responsif, cocok untuk data yang berfluktuasi
- Nilai rendah (0.1-0.3): Lebih stabil, cocok untuk data yang konsisten

### Beta (β)
- Mengontrol seberapa responsif model terhadap perubahan tren
- Nilai tinggi: Lebih cepat menangkap perubahan tren
- Nilai rendah: Tren lebih smooth dan stabil

## 🛠️ Troubleshooting

### Dropbox tidak menampilkan file
- Pastikan file CSV ada di folder aplikasi Dropbox
- Cek koneksi internet

### Error database connection
- Pastikan MySQL/MariaDB sudah running
- Cek konfigurasi database di `app.py` dan `auth.py`
- Pastikan database `data_air` sudah dibuat

### Error login
- Pastikan user sudah dibuat dengan `create_users.py`
- Cek apakah tabel `users` ada di database
- Verifikasi password yang diinput

## 📝 Catatan Pengembangan

### File Baru yang Ditambahkan:
- `auth.py`: Modul autentikasi dan authorization
- `dropbox_integration.py`: Integrasi Dropbox API
- `create_users.py`: Script manajemen user
- `database_setup.sql`: Setup database
- `templates/login.html`: Halaman login

### File yang Dimodifikasi:
- `app.py`: Tambah session, login routes, Dropbox integration
- `templates/home.html`: Tambah user info dan logout button
- `templates/dashboard/input.html`: Tambah opsi Dropbox dan parameter preset

## 📞 Support

Untuk pertanyaan atau masalah, silakan hubungi administrator sistem.

---

**PDAM TIRTA MON PASE**  
Sistem Prediksi Kebutuhan Air v2.0
