CREATE DATABASE IF NOT EXISTS zayona;
USE zayona;


-- Drop existing tables if needed (in reverse order of dependencies)
DROP TABLE IF EXISTS license_logs;
DROP TABLE IF EXISTS license_verifications;
DROP TABLE IF EXISTS licenses;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- ========================================
-- 1. users Table
-- ========================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ========================================
-- 2. products Table
-- ========================================
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    product_code VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ========================================
-- 3. licenses Table (Enhanced for Security)
-- ========================================
CREATE TABLE licenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    license_key VARCHAR(255) NOT NULL UNIQUE,  -- UNIQUE constraint added
    valid_till DATETIME NOT NULL,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at DATETIME NULL,
    revoked_reason VARCHAR(255) NULL,
    
    -- Hardware fingerprinting for anti-sharing
    hardware_fingerprint VARCHAR(255) NULL,  -- Machine-specific identifier
    max_installations INT DEFAULT 1,         -- How many machines can use this license
    current_installations INT DEFAULT 0,     -- Current number of installations
    
    -- Online verification settings
    requires_online_verification BOOLEAN DEFAULT TRUE,
    last_online_check DATETIME NULL,
    offline_grace_period_hours INT DEFAULT 48,  -- Hours allowed offline
    
    -- Rate limiting and security
    daily_verification_limit INT DEFAULT 10,    -- Max verifications per day
    verification_count_today INT DEFAULT 0,     -- Current day's verification count
    last_verification_reset DATE DEFAULT CURRENT_DATE,

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ========================================
-- 4. license_logs Table (Enhanced)
-- ========================================
CREATE TABLE license_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_id INT NOT NULL,
    status ENUM('VALID', 'EXPIRED', 'REJECTED', 'REVOKED', 'SHARING_DETECTED', 'RATE_LIMITED') NOT NULL,
    access_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(45),
    user_agent TEXT,
    hardware_fingerprint VARCHAR(255),
    verification_type ENUM('ONLINE', 'OFFLINE', 'PERIODIC') DEFAULT 'ONLINE',
    error_message TEXT,

    CONSTRAINT fk_license FOREIGN KEY (license_id) REFERENCES licenses(id) ON DELETE CASCADE
);

-- ========================================
-- 5. license_verifications Table (New - for periodic checks)
-- ========================================
CREATE TABLE license_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_id INT NOT NULL,
    verification_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    verification_type ENUM('DAILY', 'WEEKLY', 'MANUAL') DEFAULT 'DAILY',
    status ENUM('SUCCESS', 'FAILED', 'EXPIRED', 'REVOKED') NOT NULL,
    hardware_fingerprint VARCHAR(255),
    source_ip VARCHAR(45),
    response_time_ms INT,
    error_details TEXT,

    CONSTRAINT fk_license_verification FOREIGN KEY (license_id) REFERENCES licenses(id) ON DELETE CASCADE
);

-- ========================================
-- 6. security_settings Table (New - for system-wide security config)
-- ========================================
CREATE TABLE security_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default security settings
INSERT INTO security_settings (setting_name, setting_value, description) VALUES
('max_license_attempts_per_day', '10', 'Maximum license verification attempts per day per license'),
('offline_grace_period_hours', '48', 'Hours allowed offline before requiring online verification'),
('hardware_fingerprint_required', 'true', 'Whether hardware fingerprinting is required'),
('auto_revoke_on_sharing', 'true', 'Automatically revoke license if sharing is detected'),
('verification_interval_hours', '24', 'How often to require online verification');

-- ========================================
-- Indexes for Performance
-- ========================================
CREATE INDEX idx_license_key ON licenses(license_key);
CREATE INDEX idx_license_user ON licenses(user_id);
CREATE INDEX idx_license_product ON licenses(product_id);
CREATE INDEX idx_license_valid_till ON licenses(valid_till);
CREATE INDEX idx_license_hardware ON licenses(hardware_fingerprint);
CREATE INDEX idx_logs_license_time ON license_logs(license_id, access_time);
CREATE INDEX idx_logs_status ON license_logs(status);
CREATE INDEX idx_verifications_license_time ON license_verifications(license_id, verification_time);