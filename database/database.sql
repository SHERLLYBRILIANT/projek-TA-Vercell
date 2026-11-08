-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Generation Time: Nov 08, 2026 at 11:06 AM
-- Server version: 9.7.0
-- PHP Version: 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `gizi_balita`
--
CREATE DATABASE IF NOT EXISTS `gizi_balita` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `gizi_balita`;

-- --------------------------------------------------------

--
-- Table structure for table `balita`
--

CREATE TABLE `balita` (
  `id` int NOT NULL,
  `nama` varchar(100) NOT NULL,
  `nik` varchar(20) DEFAULT NULL,
  `jenis_kelamin` enum('L','P') NOT NULL,
  `tanggal_lahir` date NOT NULL,
  `nama_ibu` varchar(100) DEFAULT '',
  `alamat` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `balita`
--

INSERT INTO `balita` (`id`, `nama`, `nik`, `jenis_kelamin`, `tanggal_lahir`, `nama_ibu`, `alamat`, `created_at`, `updated_at`) VALUES
(9, 'Sherlly', '1234567891234567', 'P', '2023-09-15', 'Ibu', 'Bandung', '2026-07-08 12:27:00', '2026-07-08 12:27:00'),
(10, 'Davis', '1234567891234567', 'L', '2022-10-18', 'Ibu', 'Purwokerto', '2026-07-08 12:27:39', '2026-07-08 12:27:39'),
(11, 'Syibilla', '1234567891234567', 'P', '2025-02-04', 'Ibu', 'Bantul', '2026-07-08 12:28:16', '2026-07-08 12:28:16'),
(12, 'Intan', '1234567891234567', 'P', '2025-08-05', 'Ibu', 'Bandung', '2026-07-08 12:28:48', '2026-07-08 12:28:48');

-- --------------------------------------------------------

--
-- Table structure for table `hasil_klasifikasi`
--

CREATE TABLE `hasil_klasifikasi` (
  `id` int NOT NULL,
  `pemeriksaan_id` int NOT NULL,
  `bbu_label` varchar(30) NOT NULL,
  `tbu_label` varchar(30) NOT NULL,
  `bbtb_label` varchar(30) NOT NULL,
  `bbu_kode` tinyint NOT NULL,
  `tbu_kode` tinyint NOT NULL,
  `bbtb_kode` tinyint NOT NULL,
  `model_digunakan` varchar(20) DEFAULT 'TabNet',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `hasil_klasifikasi`
--

INSERT INTO `hasil_klasifikasi` (`id`, `pemeriksaan_id`, `bbu_label`, `tbu_label`, `bbtb_label`, `bbu_kode`, `tbu_kode`, `bbtb_kode`, `model_digunakan`, `created_at`) VALUES
(59, 59, 'Normal', 'Not Stunted', 'Normal', 1, 0, 2, 'TabNet', '2026-07-08 12:30:45'),
(60, 60, 'Normal', 'Not Stunted', 'Normal', 1, 0, 2, 'TabNet', '2026-07-08 12:31:04'),
(61, 61, 'Normal', 'Stunted', 'Normal', 1, 1, 2, 'TabNet', '2026-07-08 12:31:17'),
(62, 62, 'Normal', 'Not Stunted', 'Thin', 1, 0, 1, 'TabNet', '2026-07-08 12:31:31'),
(63, 63, 'Normal', 'Not Stunted', 'Very Thin', 1, 0, 0, 'TabNet', '2026-10-06 14:12:28'),
(64, 64, 'Normal', 'Not Stunted', 'Normal', 1, 0, 2, 'TabNet', '2026-10-06 14:46:47'),
(65, 65, 'Normal', 'Not Stunted', 'Normal', 1, 0, 2, 'TabNet', '2026-10-29 17:19:04');

-- --------------------------------------------------------

--
-- Table structure for table `pemeriksaan`
--

CREATE TABLE `pemeriksaan` (
  `id` int NOT NULL,
  `balita_id` int NOT NULL,
  `petugas_id` int DEFAULT NULL,
  `tanggal_periksa` datetime DEFAULT CURRENT_TIMESTAMP,
  `umur_bulan` int NOT NULL,
  `berat_badan` decimal(5,2) NOT NULL,
  `tinggi_badan` decimal(5,2) NOT NULL,
  `catatan` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `pemeriksaan`
--

INSERT INTO `pemeriksaan` (`id`, `balita_id`, `petugas_id`, `tanggal_periksa`, `umur_bulan`, `berat_badan`, `tinggi_badan`, `catatan`) VALUES
(59, 10, 1, '2026-07-08 12:30:45', 44, 15.00, 100.00, ''),
(60, 9, 1, '2026-07-08 12:31:04', 33, 14.00, 100.00, ''),
(61, 11, 1, '2026-07-08 12:31:17', 17, 10.00, 74.00, ''),
(62, 12, 1, '2026-07-08 12:31:31', 11, 7.00, 74.00, ''),
(63, 9, 1, '2026-10-06 14:12:28', 36, 15.00, 120.00, ''),
(64, 11, 1, '2026-10-06 14:46:47', 20, 11.00, 85.00, ''),
(65, 11, 1, '2026-10-29 17:19:04', 20, 11.50, 85.00, '');

-- --------------------------------------------------------

--
-- Table structure for table `petugas`
--

CREATE TABLE `petugas` (
  `id` int NOT NULL,
  `nama` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `jabatan` varchar(100) DEFAULT 'Petugas Gizi',
  `puskesmas` varchar(150) DEFAULT '',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `petugas`
--

INSERT INTO `petugas` (`id`, `nama`, `username`, `password`, `jabatan`, `puskesmas`, `created_at`, `updated_at`) VALUES
(1, 'Kepala Kesehatan', 'Kepala Kesehatan', '$2b$12$6SW1DaaCorAgVzKtFKmxKO1MWerqVAkcR.9UlM6xlLRuelSq7XHRK', 'Kepala Kesehatan', 'Puskesmas Jeneponto', '2026-05-13 07:59:00', '2026-05-14 03:04:16'),
(11, 'Sherlly', 'Sherlly', '$2b$12$mbEkO1S018P9r6Wd2.8o7.tfXuf7xhS5a.RDPt1rc06MRHXA091Um', 'Petugas', 'Puskesmas Jeneponto', '2026-05-27 13:44:40', '2026-10-29 17:12:43');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `balita`
--
ALTER TABLE `balita`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hasil_klasifikasi`
--
ALTER TABLE `hasil_klasifikasi`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `pemeriksaan_id` (`pemeriksaan_id`);

--
-- Indexes for table `pemeriksaan`
--
ALTER TABLE `pemeriksaan`
  ADD PRIMARY KEY (`id`),
  ADD KEY `balita_id` (`balita_id`),
  ADD KEY `fk_pemeriksaan_petugas` (`petugas_id`);

--
-- Indexes for table `petugas`
--
ALTER TABLE `petugas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `balita`
--
ALTER TABLE `balita`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `hasil_klasifikasi`
--
ALTER TABLE `hasil_klasifikasi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- AUTO_INCREMENT for table `pemeriksaan`
--
ALTER TABLE `pemeriksaan`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- AUTO_INCREMENT for table `petugas`
--
ALTER TABLE `petugas`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `hasil_klasifikasi`
--
ALTER TABLE `hasil_klasifikasi`
  ADD CONSTRAINT `hasil_klasifikasi_ibfk_1` FOREIGN KEY (`pemeriksaan_id`) REFERENCES `pemeriksaan` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `pemeriksaan`
--
ALTER TABLE `pemeriksaan`
  ADD CONSTRAINT `fk_pemeriksaan_petugas` FOREIGN KEY (`petugas_id`) REFERENCES `petugas` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `pemeriksaan_ibfk_1` FOREIGN KEY (`balita_id`) REFERENCES `balita` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
