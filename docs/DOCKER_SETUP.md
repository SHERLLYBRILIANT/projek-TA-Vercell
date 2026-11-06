# 🐳 Docker Setup untuk Gizi Balita

Panduan lengkap untuk menjalankan aplikasi Gizi Balita menggunakan Docker.

## 📋 Prerequisites

Pastikan Anda sudah menginstall:
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (untuk Windows/Mac)
- atau Docker Engine + Docker Compose (untuk Linux)

Verifikasi instalasi:
```bash
docker --version
docker-compose --version
```

## 🚀 Cara Cepat Setup (Windows)

### 1. Jalankan Script Setup
Buka PowerShell pada folder project dan jalankan:
```powershell
# Pastikan execution policy memungkinkan scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Jalankan script
.\docker-setup.ps1
```

Atau jalankan langsung dengan `docker-compose`:
```powershell
docker-compose up -d
```

### 2. Tunggu hingga semua service siap
MySQL membutuhkan waktu ±10-15 detik untuk siap.

### 3. Inisialisasi Database
```powershell
docker-compose exec flask_app python setup_db.py
```

## 🚀 Cara Manual Setup (Untuk semua OS)

### Step 1: Start Services
```bash
docker-compose up -d
```

Output yang diharapkan:
```
[+] Running 4/4
 ✔ Network gizi_network Created
 ✔ Container gizi_balita_mysql Created
 ✔ Container gizi_balita_phpmyadmin Created
 ✔ Container gizi_balita_flask Created
```

### Step 2: Tunggu MySQL Ready
```bash
# Lihat status kesehatan MySQL
docker-compose ps

# Atau lihat logs
docker-compose logs mysql
```

Cari indikasi:
```
mysql ready for connections
```

### Step 3: Setup Database
```bash
docker-compose exec flask_app python setup_db.py
```

Output yang diharapkan:
```
✅ Database 'gizi_balita' siap.
✅ Table 'petugas' siap.
✅ Table 'balita' siap.
... (dan tabel lainnya)
✅ Admin default sudah dibuat
   Username: admin
   Password: admin123
```

## 📍 Akses Aplikasi

Setelah setup selesai, akses:

| Layanan | URL | Keterangan |
|---------|-----|-----------|
| **Flask App** | http://localhost:5000 | Aplikasi utama |
| **phpMyAdmin** | http://localhost:8080 | Management database |

### Login ke Flask App
- **Username**: admin
- **Password**: admin123

### Login ke phpMyAdmin
- **Username**: root
- **Password**: root

## 📝 Konfigurasi

File `.env` sudah dikonfigurasi untuk Docker:

```env
MYSQL_HOST=mysql          # Nama service MySQL dalam Docker
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=gizi_balita
```

**Penting**: Jangan ubah `MYSQL_HOST` dari `mysql` saat menggunakan Docker, karena itu adalah nama service yang didefinisikan di `docker-compose.yml`.

## 🔍 Troubleshooting

### 1. Port sudah digunakan
Jika melihat error:
```
Bind for 0.0.0.0:5000 failed: port is already allocated
```

Solusi: Ubah port di `docker-compose.yml`:
```yaml
services:
  flask_app:
    ports:
      - "5001:5000"  # Ubah port eksternal
```

### 2. MySQL Connection Failed
```
ERROR: Can't connect to MySQL server
```

Solusi:
- Pastikan MySQL container sudah running: `docker-compose ps`
- Tunggu lebih lama (±20 detik): `docker-compose logs mysql`
- Restart MySQL: `docker-compose restart mysql`

### 3. Database belum terinisialisasi
Jika aplikasi error saat diakses, jalankan:
```bash
docker-compose exec flask_app python setup_db.py
```

### 4. Lihat Logs
Untuk debugging:
```bash
# Semua service
docker-compose logs -f

# Hanya Flask app
docker-compose logs -f flask_app

# Hanya MySQL
docker-compose logs -f mysql

# Hanya phpMyAdmin
docker-compose logs -f phpmyadmin
```

## 🛑 Menghentikan Services

### Stop semua service
```bash
docker-compose stop
```

### Stop dan hapus container
```bash
docker-compose down
```

### Stop, hapus container, dan hapus data MySQL
```bash
docker-compose down -v
```

## 🔄 Restart Services

```bash
# Restart semua
docker-compose restart

# Restart spesifik
docker-compose restart flask_app
docker-compose restart mysql
```

## 📊 Monitoring

### Lihat resource usage
```bash
docker stats
```

### Lihat container yang running
```bash
docker-compose ps
```

### Lihat detail container
```bash
docker inspect gizi_balita_flask
docker inspect gizi_balita_mysql
```

## 🔐 Security Notes

⚠️ **Untuk Production**, ubah password default:

1. Di `docker-compose.yml`:
```yaml
environment:
  MYSQL_ROOT_PASSWORD: your_strong_password_here
```

2. Di `.env`:
```env
MYSQL_PASSWORD=your_strong_password_here
```

3. Generate SECRET_KEY yang kuat:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

4. Update di `.env`:
```env
SECRET_KEY=your_generated_key_here
```

## 📦 Versi Image

- **MySQL**: 8.0 (latest)
- **Python**: 3.11-slim
- **phpMyAdmin**: latest

## 🔗 Sumber Konfigurasi

- `docker-compose.yml` - Definisi services
- `Dockerfile` - Build configuration Flask app
- `.env` - Environment variables
- `.dockerignore` - File yang dikecualikan dari Docker build

## ✅ Checklist Verifikasi

Setelah setup, pastikan:
- [ ] Docker Desktop/Engine sedang berjalan
- [ ] `docker-compose ps` menunjukkan 3 container running
- [ ] Flask app bisa diakses di http://localhost:5000
- [ ] phpMyAdmin bisa diakses di http://localhost:8080
- [ ] Login ke Flask app berhasil dengan admin/admin123
- [ ] Database tidak ada error saat diakses

## 🆘 Butuh Bantuan?

Jika mengalami masalah:

1. Lihat logs: `docker-compose logs -f`
2. Check MySQL status: `docker-compose logs mysql`
3. Verify network: `docker network inspect gizi_network`
4. Restart all: `docker-compose down && docker-compose up -d`

---

**Created**: 2024
**Last Updated**: May 2026
