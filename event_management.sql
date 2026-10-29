CREATE DATABASE IF NOT EXISTS event_management;
USE event_management;

CREATE TABLE IF NOT EXISTS app_users (
    username VARCHAR(50) PRIMARY KEY,
    password_salt CHAR(32) NOT NULL,
    password_hash CHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS event_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    person_count INT NOT NULL,
    location VARCHAR(150) NOT NULL,
    phone_number VARCHAR(16) NOT NULL,
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES app_users(username)
);

CREATE TABLE IF NOT EXISTS events (
    event_id INT PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_date DATE NOT NULL,
    venue VARCHAR(150) NOT NULL,
    budget DECIMAL(12,2) NOT NULL DEFAULT 0
);

INSERT IGNORE INTO events (event_id, event_name, event_type, event_date, venue, budget) VALUES
(1, 'Birthday Celebration', 'Birthday', '2026-11-10', 'Chennai Community Hall', 25000.00),
(2, 'Annual Day', 'Corporate', '2026-12-05', 'City Convention Centre', 150000.00);


