-- ============================================================================
-- SMART BUILDING MONITORING SYSTEM USING AI - MYSQL DATABASE SCHEMA
-- Apex Horizon Tower Digital Twin & Machine Learning Telemetry Database
-- ============================================================================

CREATE DATABASE IF NOT EXISTS smart_building_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_building_db;

-- 1. Users Table (Authentication & Role-Based Access)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL,
    role ENUM('Admin', 'Building Manager') NOT NULL DEFAULT 'Building Manager',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Buildings Table (Physical Structure Metadata)
CREATE TABLE IF NOT EXISTS buildings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    location VARCHAR(255),
    total_area_sqft INT DEFAULT 185000,
    total_floors INT DEFAULT 3,
    max_capacity INT DEFAULT 600,
    base_tariff DECIMAL(6, 4) DEFAULT 0.1600,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Floors Table
CREATE TABLE IF NOT EXISTS floors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    building_id INT NOT NULL,
    floor_number INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    energy_kw DECIMAL(8, 2) DEFAULT 0.00,
    occupancy INT DEFAULT 0,
    max_capacity INT DEFAULT 200,
    status VARCHAR(32) DEFAULT 'normal',
    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Rooms Table (Interactive Digital Twin Spatial Nodes)
CREATE TABLE IF NOT EXISTS rooms (
    id VARCHAR(32) PRIMARY KEY,
    floor_id INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    status ENUM('green', 'yellow', 'red') DEFAULT 'green',
    occupancy INT DEFAULT 0,
    capacity INT DEFAULT 50,
    temp_c DECIMAL(5, 2) DEFAULT 22.00,
    power_kw DECIMAL(6, 2) DEFAULT 15.00,
    lighting ENUM('ON', 'DIM', 'OFF') DEFAULT 'ON',
    hvac ENUM('ACTIVE', 'ECO', 'OFF', 'OVERLOAD') DEFAULT 'ACTIVE',
    health INT DEFAULT 95,
    FOREIGN KEY (floor_id) REFERENCES floors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Equipment Table (Subsystems & Assets)
CREATE TABLE IF NOT EXISTS equipment (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    category ENUM('HVAC', 'Elevator', 'Server/IT', 'Lighting', 'Generator', 'Air Conditioner') NOT NULL,
    floor_num INT DEFAULT 1,
    age_years DECIMAL(4, 1) DEFAULT 3.0,
    usage_percent DECIMAL(5, 2) DEFAULT 70.00,
    temp_c DECIMAL(5, 2) DEFAULT 45.00,
    status VARCHAR(64) DEFAULT 'Normal',
    health_score INT DEFAULT 90,
    risk_percent DECIMAL(5, 2) DEFAULT 15.00,
    run_hours INT DEFAULT 10000,
    prev_faults INT DEFAULT 0
) ENGINE=InnoDB;

-- 6. Energy Data Table (Submeter Time-Series)
CREATE TABLE IF NOT EXISTS energy_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_kw DECIMAL(8, 2) NOT NULL,
    floor_1_kw DECIMAL(8, 2) DEFAULT 0.00,
    floor_2_kw DECIMAL(8, 2) DEFAULT 0.00,
    floor_3_kw DECIMAL(8, 2) DEFAULT 0.00,
    daily_cost DECIMAL(10, 2) DEFAULT 0.00,
    INDEX idx_energy_time (timestamp)
) ENGINE=InnoDB;

-- 7. Occupancy Data Table
CREATE TABLE IF NOT EXISTS occupancy_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_occupancy INT NOT NULL,
    floor_1_occ INT DEFAULT 0,
    floor_2_occ INT DEFAULT 0,
    floor_3_occ INT DEFAULT 0,
    INDEX idx_occ_time (timestamp)
) ENGINE=InnoDB;

-- 8. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(32) PRIMARY KEY,
    alert_type VARCHAR(64) NOT NULL,
    severity ENUM('INFO', 'WARNING', 'CRITICAL') NOT NULL,
    title VARCHAR(128) NOT NULL,
    entity VARCHAR(128) NOT NULL,
    description TEXT,
    status ENUM('active', 'acknowledged', 'resolved') DEFAULT 'active',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 9. Predictions Table (ML Inferences Log)
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_type VARCHAR(64) NOT NULL,
    predicted_value DECIMAL(10, 2) NOT NULL,
    confidence_or_r2 DECIMAL(5, 4) DEFAULT 0.9400,
    features_json JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 10. Maintenance Records Table
CREATE TABLE IF NOT EXISTS maintenance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(32) NOT NULL,
    fault_type VARCHAR(128),
    action_taken TEXT,
    technician VARCHAR(128),
    resolved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- SAMPLE SEED DATA INSERTIONS
-- ============================================================================

INSERT INTO users (username, password_hash, full_name, email, role) VALUES
('admin', 'admin123', 'Dr. Alexander Vance', 'admin@apexbuilding.ai', 'Admin'),
('manager', 'manager123', 'Facility Mgr. Jordan', 'manager@apexbuilding.ai', 'Building Manager')
ON DUPLICATE KEY UPDATE username=username;

INSERT INTO buildings (id, name, location, total_area_sqft, total_floors, max_capacity, base_tariff) VALUES
(1, 'EcoSmart Tower', 'Metro Innovation District', 185000, 3, 600, 0.1600)
ON DUPLICATE KEY UPDATE name=name;

INSERT INTO floors (id, building_id, floor_number, name, energy_kw, occupancy, max_capacity, status) VALUES
(1, 1, 1, 'Floor 1 - Public & Hub', 78.4, 145, 220, 'normal'),
(2, 1, 2, 'Floor 2 - Engineering & R&D', 102.6, 128, 200, 'warning'),
(3, 1, 3, 'Floor 3 - Executive & Boardroom', 67.5, 69, 180, 'normal')
ON DUPLICATE KEY UPDATE name=name;

INSERT INTO rooms (id, floor_id, name, status, occupancy, capacity, temp_c, power_kw, lighting, hvac, health) VALUES
('101', 1, 'Grand Entrance Lobby', 'green', 42, 80, 22.1, 18.2, 'ON', 'ACTIVE', 96),
('102', 1, 'Security & Operations Hub', 'green', 12, 20, 21.5, 14.8, 'ON', 'ACTIVE', 98),
('103', 1, 'Cafeteria & Social Hall', 'green', 78, 100, 23.4, 34.5, 'ON', 'ACTIVE', 92),
('104', 1, 'Visitor Conference A', 'green', 13, 20, 22.0, 10.9, 'ON', 'ACTIVE', 95),
('201', 2, 'Open Workspace Alpha', 'green', 58, 80, 22.4, 26.2, 'ON', 'ACTIVE', 94),
('202', 2, 'Software Eng Lab', 'green', 44, 60, 22.8, 24.1, 'ON', 'ACTIVE', 91),
('203', 2, 'Enterprise Server Data Center', 'red', 4, 10, 27.9, 42.8, 'ON', 'OVERLOAD', 58),
('204', 2, 'Executive Meeting Room', 'green', 22, 50, 22.0, 9.5, 'ON', 'ACTIVE', 96),
('301', 3, 'Executive Boardroom', 'green', 18, 40, 21.8, 16.4, 'ON', 'ACTIVE', 95),
('302', 3, 'Executive Suites', 'green', 14, 30, 21.5, 15.2, 'ON', 'ACTIVE', 97),
('303', 3, 'Open Workspace Beta', 'yellow', 32, 70, 24.2, 28.1, 'ON', 'ECO', 74),
('304', 3, 'AI Innovation Studio', 'green', 5, 40, 21.6, 7.8, 'DIM', 'ECO', 93)
ON DUPLICATE KEY UPDATE name=name;

INSERT INTO equipment (id, name, category, floor_num, age_years, usage_percent, temp_c, status, health_score, risk_percent, run_hours, prev_faults) VALUES
('EQ-101', 'Main Chiller Unit 1', 'HVAC', 1, 4.0, 86.0, 62.4, 'Normal', 93, 12.0, 12450, 1),
('EQ-102', 'Secondary Chiller Unit 2', 'HVAC', 2, 7.0, 94.0, 84.8, 'Maintenance Required', 58, 78.0, 24890, 4),
('EQ-103', 'Central AHU-1 (Air Handler)', 'HVAC', 1, 3.0, 72.0, 45.2, 'Normal', 89, 16.0, 8920, 0),
('EQ-104', 'Passenger Elevator Lift-A', 'Elevator', 1, 5.0, 82.0, 52.0, 'Normal', 84, 22.0, 16300, 2),
('EQ-105', 'High-Capacity Freight Lift-B', 'Elevator', 2, 8.0, 68.0, 76.5, 'Maintenance Required', 62, 69.0, 27100, 5),
('EQ-106', 'Data Center CRAC Cooling System', 'Server/IT', 2, 2.0, 96.0, 39.1, 'Normal', 95, 9.0, 17200, 0),
('EQ-107', 'Emergency Diesel Generator', 'Generator', 1, 6.0, 8.0, 28.0, 'Normal', 92, 14.0, 420, 1),
('EQ-108', 'Building LED Smart Matrix Controller', 'Lighting', 3, 1.0, 64.0, 31.4, 'Normal', 99, 3.0, 7400, 0)
ON DUPLICATE KEY UPDATE name=name;

INSERT INTO alerts (id, alert_type, severity, title, entity, description, status) VALUES
('ALT-901', 'CRITICAL', 'CRITICAL', 'Thermal Limit Exceeded', 'Server Room 203', 'Ambient temperature surged to 27.9°C (normal <= 23.5°C). Cooling cycle struggling.', 'active'),
('ALT-902', 'WARNING', 'WARNING', 'Predictive Maintenance Alert', 'Secondary Chiller Unit 2', 'Random Forest flags 78% failure risk within next 120 operating hours due to bearing friction.', 'active'),
('ALT-903', 'WARNING', 'WARNING', 'Energy Spikes Detected', 'Floor 3 Open Workspace', 'HVAC drawing 28.1 kW with only 32 occupants. Sub-optimal deadband.', 'active'),
('ALT-904', 'INFO', 'INFO', 'Automated Energy Optimization', 'All Lighting Systems', 'Off-peak energy curtailment schedule activated at 18:00.', 'resolved')
ON DUPLICATE KEY UPDATE id=id;
