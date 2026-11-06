"""
setup_db.py
─────────────────────────────
Script untuk:
1. Membuat database MySQL
2. Membuat tabel-tabel yang diperlukan
3. Membuat akun admin default

Jalankan sekali sebelum menjalankan aplikasi:
    python setup_db.py

atau dalam Docker:
    docker-compose exec flask_app python setup_db.py
"""

import bcrypt
import pymysql
import sys
import os

# ─── Konfigurasi koneksi MySQL ───────────────────────────────────────────────
# Ambil dari environment variable atau gunakan default untuk Docker
DB_CONFIG = {
    'host':     os.environ.get('MYSQL_HOST', 'localhost'),
    'user':     os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'root'),
    'charset':  'utf8mb4'
}
DB_NAME = os.environ.get('MYSQL_DB', 'gizi_balita')

def create_database():
    conn = pymysql.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print(f"✅ Database '{DB_NAME}' siap.")
    cur.close()
    conn.close()

def create_tables():
    conn = pymysql.connect(database=DB_NAME, **DB_CONFIG)
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS petugas (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nama        VARCHAR(100) NOT NULL,
            username    VARCHAR(50)  NOT NULL UNIQUE,
            password    VARCHAR(255) NOT NULL,
            jabatan     VARCHAR(100) DEFAULT 'Petugas Gizi',
            puskesmas   VARCHAR(150) DEFAULT '',
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS balita (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            nama            VARCHAR(100)  NOT NULL,
            nik             VARCHAR(20)   DEFAULT NULL,
            jenis_kelamin   ENUM('L','P') NOT NULL,
            tanggal_lahir   DATE          NOT NULL,
            nama_ibu        VARCHAR(100)  DEFAULT '',
            alamat          TEXT          DEFAULT NULL,
            created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP,
            updated_at      DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pemeriksaan (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            balita_id       INT          NOT NULL,
            petugas_id      INT          NOT NULL,
            tanggal_periksa DATETIME     DEFAULT CURRENT_TIMESTAMP,
            umur_bulan      INT          NOT NULL,
            berat_badan     DECIMAL(5,2) NOT NULL,
            tinggi_badan    DECIMAL(5,2) NOT NULL,
            catatan         TEXT         DEFAULT NULL,
            FOREIGN KEY (balita_id)  REFERENCES balita(id)  ON DELETE CASCADE,
            FOREIGN KEY (petugas_id) REFERENCES petugas(id) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hasil_klasifikasi (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            pemeriksaan_id  INT         NOT NULL UNIQUE,
            bbu_label       VARCHAR(30) NOT NULL,
            tbu_label       VARCHAR(30) NOT NULL,
            bbtb_label      VARCHAR(30) NOT NULL,
            bbu_kode        TINYINT     NOT NULL,
            tbu_kode        TINYINT     NOT NULL,
            bbtb_kode       TINYINT     NOT NULL,
            model_digunakan VARCHAR(20) DEFAULT 'TabNet',
            created_at      DATETIME    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pemeriksaan_id) REFERENCES pemeriksaan(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    print("✅ Semua tabel berhasil dibuat.")
    cur.close()
    conn.close()

def create_admin():
    conn = pymysql.connect(database=DB_NAME, **DB_CONFIG)
    cur  = conn.cursor()

    # Cek apakah admin sudah ada
    cur.execute("SELECT id FROM petugas WHERE username='admin'")
    if cur.fetchone():
        print("ℹ️  Akun admin sudah ada, skip.")
        cur.close()
        conn.close()
        return

    password_hash = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
    cur.execute("""
        INSERT INTO petugas (nama, username, password, jabatan, puskesmas)
        VALUES (%s, %s, %s, %s, %s)
    """, ('Administrator', 'admin', password_hash, 'Admin Sistem', 'Puskesmas Jeneponto'))

    password_hash2 = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
    cur.execute("""
        INSERT INTO petugas (nama, username, password, jabatan, puskesmas)
        VALUES (%s, %s, %s, %s, %s)
    """, ('Petugas Gizi 1', 'petugas1', password_hash2, 'Petugas Gizi', 'Puskesmas Jeneponto'))

    # Contoh data balita
    cur.execute("""
        INSERT INTO balita (nama, nik, jenis_kelamin, tanggal_lahir, nama_ibu, alamat)
        VALUES
        ('Ahmad Faiz',    '7301010101210001','L','2021-01-15','Siti Rahmah','Jl. Mawar No.1, Jeneponto'),
        ('Bunga Cantika', '7301020202210002','P','2021-06-10','Nur Aisyah', 'Jl. Melati No.5, Jeneponto'),
        ('Dika Pratama',  '7301030303220003','L','2022-03-20','Hartini',    'Jl. Kenanga No.3, Jeneponto')
    """)

    conn.commit()
    print("✅ Akun admin dan data contoh berhasil dibuat.")
    print("   Username: admin | Password: admin123")
    print("   Username: petugas1 | Password: admin123")
    cur.close()
    conn.close()

if __name__ == '__main__':
    print("=== Setup Database SiGizi ===")
    try:
        create_database()
        create_tables()
        create_admin()
        print("\n✅ Setup selesai! Jalankan: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Pastikan MySQL berjalan dan konfigurasi DB_CONFIG benar.")
        sys.exit(1)
