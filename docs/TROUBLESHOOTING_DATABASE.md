# 🔧 Database Connection Troubleshooting

Panduan untuk mengatasi masalah koneksi database di Docker.

## 🔍 Cara Cepat Diagnosa

### 1. Test Koneksi Database
Jalankan script test:
```powershell
docker-compose exec flask_app python test_db_connection.py
```

Expected output:
```
======================================================================
  DATABASE CONNECTION TEST
======================================================================

📋 Configuration
----------------------------------------------------------------------
  Host:     mysql
  User:     root
  Password: ****
  Database: gizi_balita
  Charset:  utf8mb4

📋 Test 1: Basic Connection
  ✅ Basic connection successful

📋 Test 2: Database Selection
  ✅ Successfully selected database 'gizi_balita'

📋 Test 3: Table Queries
  ✅ Found 6 tables:
     - petugas: 1 rows
     - balita: 0 rows
     - pemeriksaan: 0 rows
     - hasil_klasifikasi: 0 rows
     - ...

📋 Test 4: Flask-MySQLdb Integration
  ✅ Flask-MySQLdb connection successful

📋 SUMMARY
  ✅ All tests passed!
```

### 2. Lihat Status Container
```powershell
docker-compose ps
```

Pastikan semua container statusnya "Up":
```
CONTAINER ID   IMAGE            STATUS
abc123         mysql:8.0        Up 2 minutes (healthy)
def456         phpmyadmin       Up 2 minutes
ghi789         gizi_balita:latest Up 1 minute
```

### 3. Lihat Logs
```powershell
# Semua logs
docker-compose logs -f

# Hanya MySQL
docker-compose logs mysql

# Hanya Flask
docker-compose logs flask_app
```

---

## ❌ Error & Solusi

### Error 1: "Can't connect to MySQL server"

**Penyebab**: MySQL belum ready atau host salah

**Solusi**:

1. Cek status MySQL:
```powershell
docker-compose logs mysql
```

2. Tunggu MySQL ready (lihat message: "ready for connections"):
```powershell
docker-compose restart mysql
Start-Sleep -Seconds 20
```

3. Verifikasi hostname di `.env`:
```env
MYSQL_HOST=mysql  # Harus "mysql" untuk Docker, bukan "localhost"
```

4. Restart Flask app:
```powershell
docker-compose restart flask_app
```

---

### Error 2: "Access denied for user 'root'@'172.xxx.xxx.xxx'"

**Penyebab**: Password MySQL salah

**Verifikasi**:

1. Cek password di `docker-compose.yml`:
```yaml
environment:
  MYSQL_ROOT_PASSWORD: root
```

2. Cek di `.env`:
```env
MYSQL_PASSWORD=root
```

3. Pastikan keduanya cocok

4. Jika sudah pernah setup dengan password berbeda, hapus volume lama:
```powershell
docker-compose down -v
```

5. Restart:
```powershell
docker-compose up -d
Start-Sleep -Seconds 15
docker-compose exec flask_app python setup_db.py
```

---

### Error 3: "Unknown database 'gizi_balita'"

**Penyebab**: Database belum diinisialisasi

**Solusi**:

1. Inisialisasi database:
```powershell
docker-compose exec flask_app python setup_db.py
```

2. Jika masih error, lihat log MySQL:
```powershell
docker-compose logs mysql
```

3. Jika ada permission error, restart MySQL:
```powershell
docker-compose restart mysql
Start-Sleep -Seconds 10
docker-compose exec flask_app python setup_db.py
```

---

### Error 4: "Port already in use"

**Penyebab**: Port 3306, 5000, atau 8080 sudah digunakan

**Solusi**:

Ubah port di `docker-compose.yml`:

```yaml
services:
  mysql:
    ports:
      - "3307:3306"  # Ubah dari 3306 ke 3307

  flask_app:
    ports:
      - "5001:5000"  # Ubah dari 5000 ke 5001

  phpmyadmin:
    ports:
      - "8081:80"    # Ubah dari 8080 ke 8081
```

Kemudian restart:
```powershell
docker-compose restart
```

---

### Error 5: "COLLATION 'utf8mb4_unicode_ci' doesn't exist"

**Penyebab**: MySQL version mismatch

**Solusi**:

1. Cek MySQL version di `docker-compose.yml`:
```yaml
services:
  mysql:
    image: mysql:8.0  # Pastikan versi yang tepat
```

2. Jika perlu, update ke versi terbaru:
```powershell
docker-compose down -v
# Edit docker-compose.yml
docker-compose up -d
```

---

### Error 6: Container Flask tidak bisa connect ke MySQL

**Penyebab**: Network atau DNS resolution problem

**Verifikasi**:

1. Pastikan kedua container di network yang sama:
```powershell
docker-compose ps
```

2. Test DNS resolution dalam container:
```powershell
docker-compose exec flask_app ping mysql
```

Output yang diharapkan:
```
PING mysql (172.xxx.xxx.xxx) 56(84) bytes of data.
64 bytes from mysql.gizi_network (172.xxx.xxx.xxx): ...
```

3. Jika error, rebuild network:
```powershell
docker-compose down
docker-compose up -d
```

---

## 🧪 Advanced Testing

### Test Connection dari Container Langsung

```powershell
# MySQL CLI
docker-compose exec mysql mysql -h localhost -u root -p gizi_balita -e "SELECT COUNT(*) FROM petugas;"

# Enter password: root
```

### Test dari Flask Container

```powershell
docker-compose exec flask_app python -c "
import pymysql
conn = pymysql.connect(
    host='mysql',
    user='root', 
    password='root',
    database='gizi_balita'
)
print('✅ Connection OK')
conn.close()
"
```

### Check MySQL Version

```powershell
docker-compose exec mysql mysql --version
```

### Check Available Databases

```powershell
docker-compose exec mysql mysql -u root -proot -e "SHOW DATABASES;"
```

### Check Tables di Database

```powershell
docker-compose exec mysql mysql -u root -proot gizi_balita -e "SHOW TABLES;"
```

---

## 🆘 Last Resort Solutions

### Opsi 1: Rebuild Dari Awal

```powershell
# Stop dan hapus semua
docker-compose down -v

# Rebuild image
docker-compose build --no-cache

# Start kembali
docker-compose up -d

# Wait
Start-Sleep -Seconds 20

# Setup database
docker-compose exec flask_app python setup_db.py
```

### Opsi 2: Reset MySQL Volume

```powershell
# Stop services
docker-compose stop

# Remove MySQL volume
docker volume rm gizi_balita_project_gizi_balita_mysql_data

# Atau dengan docker-compose:
docker-compose down -v

# Start kembali
docker-compose up -d
```

### Opsi 3: Manual Connection Test

```powershell
# Masuk ke Flask container
docker-compose exec -it flask_app bash

# Di dalam container, jalankan Python
python

# Di Python shell:
import pymysql
conn = pymysql.connect(
    host='mysql',
    user='root',
    password='root',
    database='gizi_balita'
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM petugas")
print(cur.fetchone())
cur.close()
conn.close()
```

---

## 📝 Checklist Debugging

Ketika ada masalah koneksi database:

- [ ] Docker Desktop sedang running
- [ ] Semua container statusnya "Up" (`docker-compose ps`)
- [ ] MySQL tidak ada error di logs (`docker-compose logs mysql`)
- [ ] Password di `.env` cocok dengan `docker-compose.yml`
- [ ] MYSQL_HOST = `mysql` (bukan localhost)
- [ ] Database sudah diinisialisasi (`test_db_connection.py`)
- [ ] Flask app bisa ping ke MySQL (`docker-compose exec flask_app ping mysql`)
- [ ] Port tidak bentrok (`docker-compose logs flask_app`)

---

## 📞 Getting Help

Kumpulkan informasi berikut sebelum asking for help:

1. Output dari `docker-compose ps`
2. Output dari `docker-compose logs` (last 50 lines)
3. Output dari `test_db_connection.py`
4. Error message yang spesifik (jika ada)
5. Langkah apa yang sudah dicoba

---

**Last Updated**: May 2026
