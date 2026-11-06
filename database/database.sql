-- =============================================================
-- DATABASE: gizi_balita
-- Sistem Prediksi Status Gizi Balita Berbasis Web
-- Model: TabNet Multi-Output Classification
-- =============================================================

CREATE DATABASE IF NOT EXISTS gizi_balita
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE gizi_balita;

-- ─────────────────────────────────────────────
-- TABEL 1: petugas
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS petugas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nama        VARCHAR(100)        NOT NULL,
    username    VARCHAR(50)         NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,
    jabatan     VARCHAR(100)        DEFAULT 'Petugas Gizi',
    puskesmas   VARCHAR(150)        DEFAULT '',
    created_at  DATETIME            DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME            DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─────────────────────────────────────────────
-- TABEL 2: balita
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS balita (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nama            VARCHAR(100)    NOT NULL,
    nik             VARCHAR(20)     DEFAULT NULL,
    jenis_kelamin   ENUM('L','P')   NOT NULL,
    tanggal_lahir   DATE            NOT NULL,
    nama_ibu        VARCHAR(100)    DEFAULT '',
    alamat          TEXT            DEFAULT NULL,
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─────────────────────────────────────────────
-- TABEL 3: pemeriksaan
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pemeriksaan (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    balita_id       INT             NOT NULL,
    petugas_id      INT             DEFAULT NULL,
    tanggal_periksa DATETIME        DEFAULT CURRENT_TIMESTAMP,
    umur_bulan      INT             NOT NULL COMMENT 'Umur dalam bulan saat pemeriksaan',
    berat_badan     DECIMAL(5,2)    NOT NULL COMMENT 'Berat badan dalam kg',
    tinggi_badan    DECIMAL(5,2)    NOT NULL COMMENT 'Tinggi badan dalam cm',
    catatan         TEXT            DEFAULT NULL,
    FOREIGN KEY (balita_id)  REFERENCES balita(id)  ON DELETE CASCADE  ON UPDATE CASCADE,
    FOREIGN KEY (petugas_id) REFERENCES petugas(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─────────────────────────────────────────────
-- TABEL 4: hasil_klasifikasi
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hasil_klasifikasi (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    pemeriksaan_id      INT             NOT NULL UNIQUE,
    -- Prediksi TabNet
    bbu_label           VARCHAR(30)     NOT NULL COMMENT 'BB/U: Underfed/Normal/Malnutrition/Overnutrition',
    tbu_label           VARCHAR(30)     NOT NULL COMMENT 'TB/U: Not Stunted/Stunted',
    bbtb_label          VARCHAR(30)     NOT NULL COMMENT 'BB/TB: Very Thin/Thin/Normal/Obese',
    -- Nilai numerik prediksi
    bbu_kode            TINYINT         NOT NULL,
    tbu_kode            TINYINT         NOT NULL,
    bbtb_kode           TINYINT         NOT NULL,
    -- Metadata
    model_digunakan     VARCHAR(20)     DEFAULT 'TabNet',
    created_at          DATETIME        DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pemeriksaan_id) REFERENCES pemeriksaan(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─────────────────────────────────────────────
-- INDEX untuk performa query
-- ─────────────────────────────────────────────
CREATE INDEX idx_pemeriksaan_balita  ON pemeriksaan(balita_id);
CREATE INDEX idx_pemeriksaan_tanggal ON pemeriksaan(tanggal_periksa);
CREATE INDEX idx_hasil_pemeriksaan   ON hasil_klasifikasi(pemeriksaan_id);
CREATE INDEX idx_balita_gender       ON balita(jenis_kelamin);

-- ─────────────────────────────────────────────
-- DATA AWAL: akun admin default
-- Password: admin123 (bcrypt hash)
-- ─────────────────────────────────────────────
INSERT INTO petugas (nama, username, password, jabatan, puskesmas) VALUES
('Administrator', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMTVDJJO8Q.9f9qLh9v8OFY7q6', 'Admin Sistem', 'Puskesmas Jeneponto'),
('Petugas Gizi 1', 'petugas1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMTVDJJO8Q.9f9qLh9v8OFY7q6', 'Petugas Gizi', 'Puskesmas Jeneponto');

-- ─────────────────────────────────────────────
-- DATA CONTOH: balita
-- ─────────────────────────────────────────────
INSERT INTO balita (nama, nik, jenis_kelamin, tanggal_lahir, nama_ibu, alamat) VALUES
('Ahmad Faiz',     '7301010101210001', 'L', '2021-01-15', 'Siti Rahmah',   'Jl. Mawar No.1, Jeneponto'),
('Bunga Cantika',  '7301020202210002', 'P', '2021-06-10', 'Nur Aisyah',    'Jl. Melati No.5, Jeneponto'),
('Dika Pratama',   '7301030303220003', 'L', '2022-03-20', 'Hartini',       'Jl. Kenanga No.3, Jeneponto');
