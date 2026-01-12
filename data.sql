-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.6-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.14.0.7165
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table data_air.data_produksi
CREATE TABLE IF NOT EXISTS `data_produksi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bulan` varchar(20) DEFAULT NULL,
  `Tahun` int(11) DEFAULT NULL,
  `jumlah_produksi_air_m3` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3313 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table data_air.data_produksi: ~36 rows (approximately)
INSERT INTO `data_produksi` (`id`, `bulan`, `Tahun`, `jumlah_produksi_air_m3`) VALUES
	(3277, 'Januari', 2022, 1015598.00),
	(3278, 'Februari', 2022, 959947.00),
	(3279, 'Maret', 2022, 1044687.00),
	(3280, 'April', 2022, 1045833.00),
	(3281, 'Mei', 2022, 1076586.00),
	(3282, 'Juni', 2022, 1028071.00),
	(3283, 'Juli', 2022, 1059276.00),
	(3284, 'Agustus', 2022, 1054569.00),
	(3285, 'September', 2022, 1029813.00),
	(3286, 'Oktober', 2022, 1059191.00),
	(3287, 'November', 2022, 1002966.00),
	(3288, 'Desember', 2022, 1037533.00),
	(3289, 'Januari', 2023, 1046365.00),
	(3290, 'Februari', 2023, 950333.00),
	(3291, 'Maret', 2023, 1003551.00),
	(3292, 'April', 2023, 1003806.00),
	(3293, 'Mei', 2023, 992756.00),
	(3294, 'Juni', 2023, 988591.00),
	(3295, 'Juli', 2023, 1009001.00),
	(3296, 'Agustus', 2023, 983299.00),
	(3297, 'September', 2023, 1101960.00),
	(3298, 'Oktober', 2023, 1176543.00),
	(3299, 'November', 2023, 1147269.00),
	(3300, 'Desember', 2023, 1202087.00),
	(3301, 'Januari', 2024, 1192381.00),
	(3302, 'Februari', 2024, 1209955.00),
	(3303, 'Maret', 2024, 1288805.00),
	(3304, 'April', 2024, 1284367.00),
	(3305, 'Mei', 2024, 1297426.00),
	(3306, 'Juni', 2024, 1320367.00),
	(3307, 'Juli', 2024, 1343308.00),
	(3308, 'Agustus', 2024, 1349550.00),
	(3309, 'September', 2024, 1272828.00),
	(3310, 'Oktober', 2024, 1260063.00),
	(3311, 'November', 2024, 1318009.00),
	(3312, 'Desember', 2024, 1251311.00);

-- Dumping structure for table data_air.data_upload_history
CREATE TABLE IF NOT EXISTS `data_upload_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `periode` varchar(30) NOT NULL,
  `aktual` float DEFAULT NULL,
  `smoothed` float DEFAULT NULL,
  `prediksi` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20009 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table data_air.data_upload_history: ~60 rows (approximately)
INSERT INTO `data_upload_history` (`id`, `periode`, `aktual`, `smoothed`, `prediksi`) VALUES
	(19949, 'Januari 2022', 1015600, 1015600, NULL),
	(19950, 'Februari 2022', 959947, 959947, 959947),
	(19951, 'Maret 2022', 1044690, 974492, 904296),
	(19952, 'April 2022', 1045830, 992866, 939899),
	(19953, 'Mei 2022', 1076590, 1025370, 974164),
	(19954, 'Juni 2022', 1028070, 1025050, 1022040),
	(19955, 'Juli 2022', 1059280, 1040950, 1022620),
	(19956, 'Agustus 2022', 1054570, 1049290, 1044010),
	(19957, 'September 2022', 1029810, 1041880, 1053940),
	(19958, 'Oktober 2022', 1059190, 1051050, 1042910),
	(19959, 'November 2022', 1002970, 1028740, 1054520),
	(19960, 'Desember 2022', 1037530, 1031010, 1024480),
	(19961, 'Januari 2023', 1046360, 1037530, 1028700),
	(19962, 'Februari 2023', 950333, 994107, 1037880),
	(19963, 'Maret 2023', 1003550, 992436, 981320),
	(19964, 'April 2023', 1003810, 993395, 982984),
	(19965, 'Mei 2023', 992756, 989911, 987066),
	(19966, 'Juni 2023', 988591, 986514, 984436),
	(19967, 'Juli 2023', 1009000, 995331, 981662),
	(19968, 'Agustus 2023', 983299, 988940, 994580),
	(19969, 'September 2023', 1101960, 1044230, 986497),
	(19970, 'Oktober 2023', 1176540, 1117820, 1059100),
	(19971, 'November 2023', 1147270, 1148790, 1150320),
	(19972, 'Desember 2023', 1202090, 1191460, 1180830),
	(19973, 'Januari 2024', 1192380, 1209530, 1226680),
	(19974, 'Februari 2024', 1209960, 1224780, 1239610),
	(19975, 'Maret 2024', 1288800, 1269610, 1250410),
	(19976, 'April 2024', 1284370, 1292680, 1301000),
	(19977, 'Mei 2024', 1297430, 1309500, 1321580),
	(19978, 'Juni 2024', 1320370, 1327570, 1334770),
	(19979, 'Juli 2024', 1343310, 1346990, 1350680),
	(19980, 'Agustus 2024', 1349550, 1359270, 1369000),
	(19981, 'September 2024', 1272830, 1325600, 1378360),
	(19982, 'Oktober 2024', 1260060, 1294460, 1328850),
	(19983, 'November 2024', 1318010, 1302700, 1287400),
	(19984, 'Desember 2024', 1251310, 1275770, 1300230),
	(19985, 'Januari 2025', NULL, NULL, 1265960),
	(19986, 'Februari 2025', NULL, NULL, 1256160),
	(19987, 'Maret 2025', NULL, NULL, 1246350),
	(19988, 'April 2025', NULL, NULL, 1236540),
	(19989, 'Mei 2025', NULL, NULL, 1226730),
	(19990, 'Juni 2025', NULL, NULL, 1216930),
	(19991, 'Juli 2025', NULL, NULL, 1207120),
	(19992, 'Agustus 2025', NULL, NULL, 1197310),
	(19993, 'September 2025', NULL, NULL, 1187500),
	(19994, 'Oktober 2025', NULL, NULL, 1177700),
	(19995, 'November 2025', NULL, NULL, 1167890),
	(19996, 'Desember 2025', NULL, NULL, 1158080),
	(19997, 'Januari 2026', NULL, NULL, 1148270),
	(19998, 'Februari 2026', NULL, NULL, 1138470),
	(19999, 'Maret 2026', NULL, NULL, 1128660),
	(20000, 'April 2026', NULL, NULL, 1118850),
	(20001, 'Mei 2026', NULL, NULL, 1109040),
	(20002, 'Juni 2026', NULL, NULL, 1099240),
	(20003, 'Juli 2026', NULL, NULL, 1089430),
	(20004, 'Agustus 2026', NULL, NULL, 1079620),
	(20005, 'September 2026', NULL, NULL, 1069810),
	(20006, 'Oktober 2026', NULL, NULL, 1060000),
	(20007, 'November 2026', NULL, NULL, 1050200),
	(20008, 'Desember 2026', NULL, NULL, 1040390);

-- Dumping structure for table data_air.file_uploads
CREATE TABLE IF NOT EXISTS `file_uploads` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `stored_filename` varchar(255) DEFAULT NULL,
  `upload_time` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table data_air.file_uploads: ~11 rows (approximately)
INSERT INTO `file_uploads` (`id`, `filename`, `stored_filename`, `upload_time`) VALUES
	(58, 'produksi_air_2.csv', 'produksi_air_2_20250924145338_dd8a11.csv', '2025-09-24 07:53:38'),
	(59, 'produksi_air_2_-_Copy.csv', 'produksi_air_2_-_Copy_20250924145815_d4dd38.csv', '2025-09-24 07:58:15'),
	(60, 'produksi_air_2.csv', 'produksi_air_2_20250924150127_6faff0.csv', '2025-09-24 08:01:27'),
	(63, 'produksi_air_2_-_Copy.csv', 'produksi_air_2_-_Copy_20250924163057_7e1230.csv', '2025-09-24 09:30:57'),
	(65, 'produksi_air_2_-_Copy.csv', 'produksi_air_2_-_Copy_20250930152756_8e2678.csv', '2025-09-30 08:27:57'),
	(66, 'produksi_air_2_-_Copy.csv', 'produksi_air_2_-_Copy_20251008123052_3d7fb7.csv', '2025-10-08 05:30:52'),
	(67, 'produksi_air_2.csv', 'produksi_air_2_20251031144508_26353f.csv', '2025-10-31 07:45:09'),
	(69, 'produksi_air_2.csv', 'produksi_air_2_20251031171116_3880a0.csv', '2025-10-31 10:11:16'),
	(70, 'produksi_air_2.csv', 'produksi_air_2_20251031171214_68c4da.csv', '2025-10-31 10:12:14'),
	(71, 'produksi_air_2_-_Copy_2.csv', 'produksi_air_2_-_Copy_2_20251211214944_1c845a.csv', '2025-12-11 14:49:44'),
	(72, 'produksi_air_2.csv', 'produksi_air_2_20251222102341_dc0b2e.csv', '2025-12-22 03:23:41');

-- Dumping structure for table data_air.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','user') DEFAULT 'user',
  `full_name` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- Dumping data for table data_air.users: ~2 rows (approximately)
INSERT INTO `users` (`id`, `username`, `password`, `role`, `full_name`, `created_at`, `last_login`) VALUES
	(1, 'admin', '21232f297a57a5a743894a0e4a801fc3', 'admin', 'Administrator', '2026-01-11 10:18:01', NULL),
	(2, 'user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user', 'Regular User', '2026-01-11 10:18:02', NULL);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
