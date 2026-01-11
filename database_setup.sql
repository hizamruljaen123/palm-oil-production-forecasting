-- Database setup for NISA (Water Prediction System)
-- Run this script to create all necessary tables

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS data_air;
USE data_air;

-- Table for users (authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Table for production data
CREATE TABLE IF NOT EXISTS data_produksi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bulan VARCHAR(20) NOT NULL,
    Tahun INT NOT NULL,
    jumlah_produksi_air_m3 INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for file uploads
CREATE TABLE IF NOT EXISTS file_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(50),
    FOREIGN KEY (uploaded_by) REFERENCES users(username) ON DELETE SET NULL
);

-- Table for upload history
CREATE TABLE IF NOT EXISTS data_upload_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    periode VARCHAR(50) NOT NULL,
    aktual INT NULL,
    smoothed DECIMAL(10,2) NULL,
    prediksi DECIMAL(10,2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user
-- Password: admin (MD5: 21232f297a57a5a743894a0e4a801fc3)
INSERT INTO users (username, password, role, full_name) VALUES
('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin', 'Administrator')
ON DUPLICATE KEY UPDATE username=username;

-- Insert default user
-- Password: user (MD5: ee11cbb19052e40b07aac0ca060c23ee)
INSERT INTO users (username, password, role, full_name) VALUES
('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user', 'Regular User')
ON DUPLICATE KEY UPDATE username=username;

-- Show tables
SHOW TABLES;
