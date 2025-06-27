-- Seed Data for License Management System
-- This file contains test data for development

USE zayona;

-- ========================================
-- 1. Insert Test Users
-- ========================================
INSERT INTO users (name, username, password_hash, email, is_active) VALUES
('John Doe', 'johnd123', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeG', 'john.doe@example.com', TRUE),
('Jane Smith', 'janes456', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeG', 'jane.smith@example.com', TRUE),
('Bob Wilson', 'bobw789', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeG', 'bob.wilson@example.com', TRUE),
('Alice Johnson', 'alicej101', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeG', 'alice.johnson@example.com', TRUE),
('Charlie Brown', 'charlieb202', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uOeG', 'charlie.brown@example.com', TRUE);

-- Note: All passwords are 'password123' (bcrypt hash)

-- ========================================
-- 2. Insert Test Products
-- ========================================
INSERT INTO products (name, product_code, version) VALUES
('ZAYONA Vulnerability Scanner', 'ZAYONA-PRO-9988', '2.1.0'),
('ZAYONA Network Monitor', 'ZAYONA-NET-5566', '1.5.2'),
('ZAYONA Security Suite', 'ZAYONA-SEC-3344', '3.0.1'),
('ZAYONA Penetration Testing Tool', 'ZAYONA-PEN-7788', '2.0.0'),
('ZAYONA Compliance Checker', 'ZAYONA-COM-1122', '1.2.1');

-- ========================================
-- 3. Insert Test Licenses
-- ========================================
INSERT INTO licenses (user_id, product_id, license_key, valid_till, hardware_fingerprint, max_installations, current_installations) VALUES
(1, 1, 'OSPL-VulnScan-20250626-134123-BYTU5JD', '2025-07-26 13:41:23', 'MAC:00:1B:44:11:3A:B7|CPU:BFEBFBFF000906EA|DISK:WD-WCC4E5XK1234', 1, 1),
(2, 2, 'OSPL-NetMon-20250626-145623-CDEF7GH', '2025-07-26 14:56:23', 'MAC:00:1B:44:11:3A:B8|CPU:BFEBFBFF000906EB|DISK:WD-WCC4E5XK5678', 1, 1),
(3, 3, 'OSPL-SecSuite-20250626-152345-HIJK9LM', '2025-08-26 15:23:45', 'MAC:00:1B:44:11:3A:B9|CPU:BFEBFBFF000906EC|DISK:WD-WCC4E5XK9012', 2, 1),
(4, 4, 'OSPL-PenTest-20250626-160012-NOPQ1RS', '2025-06-30 16:00:12', 'MAC:00:1B:44:11:3A:BA|CPU:BFEBFBFF000906ED|DISK:WD-WCC4E5XK3456', 1, 0),
(5, 5, 'OSPL-Compliance-20250626-163456-TUVW3XY', '2025-09-26 16:34:56', 'MAC:00:1B:44:11:3A:BB|CPU:BFEBFBFF000906EE|DISK:WD-WCC4E5XK7890', 1, 1);

-- ========================================
-- 4. Insert Some Test License Logs
-- ========================================
INSERT INTO license_logs (license_id, status, source_ip, user_agent, hardware_fingerprint, verification_type) VALUES
(1, 'VALID', '192.168.1.100', 'ZAYONA-Agent/2.1.0', 'MAC:00:1B:44:11:3A:B7|CPU:BFEBFBFF000906EA|DISK:WD-WCC4E5XK1234', 'ONLINE'),
(1, 'VALID', '192.168.1.100', 'ZAYONA-Agent/2.1.0', 'MAC:00:1B:44:11:3A:B7|CPU:BFEBFBFF000906EA|DISK:WD-WCC4E5XK1234', 'ONLINE'),
(2, 'VALID', '192.168.1.101', 'ZAYONA-Agent/1.5.2', 'MAC:00:1B:44:11:3A:B8|CPU:BFEBFBFF000906EB|DISK:WD-WCC4E5XK5678', 'ONLINE'),
(3, 'VALID', '192.168.1.102', 'ZAYONA-Agent/3.0.1', 'MAC:00:1B:44:11:3A:B9|CPU:BFEBFBFF000906EC|DISK:WD-WCC4E5XK9012', 'ONLINE'),
(5, 'VALID', '192.168.1.103', 'ZAYONA-Agent/1.2.1', 'MAC:00:1B:44:11:3A:BB|CPU:BFEBFBFF000906EE|DISK:WD-WCC4E5XK7890', 'ONLINE');

-- ========================================
-- 5. Insert Some Test License Verifications
-- ========================================
INSERT INTO license_verifications (license_id, verification_type, status, hardware_fingerprint, source_ip, response_time_ms) VALUES
(1, 'DAILY', 'SUCCESS', 'MAC:00:1B:44:11:3A:B7|CPU:BFEBFBFF000906EA|DISK:WD-WCC4E5XK1234', '192.168.1.100', 45),
(2, 'DAILY', 'SUCCESS', 'MAC:00:1B:44:11:3A:B8|CPU:BFEBFBFF000906EB|DISK:WD-WCC4E5XK5678', '192.168.1.101', 52),
(3, 'DAILY', 'SUCCESS', 'MAC:00:1B:44:11:3A:B9|CPU:BFEBFBFF000906EC|DISK:WD-WCC4E5XK9012', '192.168.1.102', 38),
(5, 'DAILY', 'SUCCESS', 'MAC:00:1B:44:11:3A:BB|CPU:BFEBFBFF000906EE|DISK:WD-WCC4E5XK7890', '192.168.1.103', 41);

-- ========================================
-- 6. Display Test Data Summary
-- ========================================
SELECT 'Test Data Summary' as info;
SELECT 'Users:' as category, COUNT(*) as count FROM users;
SELECT 'Products:' as category, COUNT(*) as count FROM products;
SELECT 'Licenses:' as category, COUNT(*) as count FROM licenses;
SELECT 'License Logs:' as category, COUNT(*) as count FROM license_logs;
SELECT 'Verifications:' as category, COUNT(*) as count FROM license_verifications;

-- ========================================
-- 7. Show Sample Data
-- ========================================
SELECT 'Sample Users:' as info;
SELECT id, name, username, email FROM users LIMIT 3;

SELECT 'Sample Products:' as info;
SELECT id, name, product_code, version FROM products LIMIT 3;

SELECT 'Sample Licenses:' as info;
SELECT l.id, u.username, p.name, l.license_key, l.valid_till 
FROM licenses l 
JOIN users u ON l.user_id = u.id 
JOIN products p ON l.product_id = p.id 
LIMIT 3; 