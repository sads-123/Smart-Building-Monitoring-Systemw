"""
Database Manager Module
Handles schema creation for all 10 required tables:
- users, buildings, floors, rooms, equipment, energy_data,
  occupancy_data, alerts, predictions, maintenance_records.
Supports MySQL with automatic SQLite fallback for immediate testing.
"""

import os
import sys
import sqlite3
import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import Config

# Check if PyMySQL is available
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


class DatabaseManager:
    def __init__(self):
        self.use_mysql = False
        self.connection = None
        self.test_connection()
        self.init_schema()
        self.seed_demo_data()

    def test_connection(self):
        if PYMYSQL_AVAILABLE:
            try:
                # Test MySQL connection
                conn = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    connect_timeout=2
                )
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB};")
                conn.select_db(Config.MYSQL_DB)
                conn.close()
                self.use_mysql = True
                print(f"[Database] Successfully connected to MySQL server ({Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB})")
                return
            except Exception as e:
                print(f"[Database] MySQL not reachable ({e}). Engaging zero-config SQLite fallback...")
        else:
            print("[Database] PyMySQL driver not installed. Using SQLite fallback...")

        self.use_mysql = False
        os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True)
        print("[Database] Using SQLite local database fallback engine.")

    def get_connection(self):
        if self.use_mysql:
            return pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        else:
            conn = sqlite3.connect(Config.SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            return conn

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if not self.use_mysql:
                conn.commit()
            
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                if not self.use_mysql:
                    # Convert sqlite3.Row to dict
                    return [dict(row) for row in rows]
                return rows
            return cursor.lastrowid
        finally:
            conn.close()

    def init_schema(self):
        """Creates the 10 required database tables."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Common datatypes
            pk_type = "INT AUTO_INCREMENT PRIMARY KEY" if self.use_mysql else "INTEGER PRIMARY KEY AUTOINCREMENT"
            ts_type = "DATETIME DEFAULT CURRENT_TIMESTAMP"

            queries = [
                # 1. users table
                f"""
                CREATE TABLE IF NOT EXISTS users (
                    id {pk_type},
                    username VARCHAR(64) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(128) NOT NULL,
                    email VARCHAR(128) NOT NULL,
                    role VARCHAR(32) NOT NULL,
                    created_at {ts_type}
                );
                """,
                # 2. buildings table
                f"""
                CREATE TABLE IF NOT EXISTS buildings (
                    id {pk_type},
                    name VARCHAR(128) NOT NULL,
                    location VARCHAR(255),
                    total_area_sqft INT DEFAULT 185000,
                    total_floors INT DEFAULT 3,
                    max_capacity INT DEFAULT 600,
                    base_tariff FLOAT DEFAULT 0.16,
                    created_at {ts_type}
                );
                """,
                # 3. floors table
                f"""
                CREATE TABLE IF NOT EXISTS floors (
                    id {pk_type},
                    building_id INT DEFAULT 1,
                    floor_number INT NOT NULL,
                    name VARCHAR(128) NOT NULL,
                    energy_kw FLOAT DEFAULT 0.0,
                    occupancy INT DEFAULT 0,
                    max_capacity INT DEFAULT 200,
                    status VARCHAR(32) DEFAULT 'normal'
                );
                """,
                # 4. rooms table
                f"""
                CREATE TABLE IF NOT EXISTS rooms (
                    id VARCHAR(32) PRIMARY KEY,
                    floor_id INT NOT NULL,
                    name VARCHAR(128) NOT NULL,
                    status VARCHAR(32) DEFAULT 'green',
                    occupancy INT DEFAULT 0,
                    capacity INT DEFAULT 50,
                    temp_c FLOAT DEFAULT 22.0,
                    power_kw FLOAT DEFAULT 15.0,
                    lighting VARCHAR(16) DEFAULT 'ON',
                    hvac VARCHAR(16) DEFAULT 'ACTIVE',
                    health INT DEFAULT 95
                );
                """,
                # 5. equipment table
                f"""
                CREATE TABLE IF NOT EXISTS equipment (
                    id VARCHAR(32) PRIMARY KEY,
                    name VARCHAR(128) NOT NULL,
                    category VARCHAR(64) NOT NULL,
                    floor_num INT DEFAULT 1,
                    age_years FLOAT DEFAULT 3.0,
                    usage_percent FLOAT DEFAULT 70.0,
                    temp_c FLOAT DEFAULT 45.0,
                    status VARCHAR(64) DEFAULT 'Normal',
                    health_score INT DEFAULT 90,
                    risk_percent FLOAT DEFAULT 15.0,
                    run_hours INT DEFAULT 10000,
                    prev_faults INT DEFAULT 0
                );
                """,
                # 6. energy_data table (time-series)
                f"""
                CREATE TABLE IF NOT EXISTS energy_data (
                    id {pk_type},
                    timestamp {ts_type},
                    total_kw FLOAT NOT NULL,
                    floor_1_kw FLOAT DEFAULT 0,
                    floor_2_kw FLOAT DEFAULT 0,
                    floor_3_kw FLOAT DEFAULT 0,
                    daily_cost FLOAT DEFAULT 0
                );
                """,
                # 7. occupancy_data table
                f"""
                CREATE TABLE IF NOT EXISTS occupancy_data (
                    id {pk_type},
                    timestamp {ts_type},
                    total_occupancy INT NOT NULL,
                    floor_1_occ INT DEFAULT 0,
                    floor_2_occ INT DEFAULT 0,
                    floor_3_occ INT DEFAULT 0
                );
                """,
                # 8. alerts table
                f"""
                CREATE TABLE IF NOT EXISTS alerts (
                    id VARCHAR(32) PRIMARY KEY,
                    alert_type VARCHAR(32) NOT NULL,
                    severity VARCHAR(16) NOT NULL,
                    title VARCHAR(128) NOT NULL,
                    entity VARCHAR(128) NOT NULL,
                    description TEXT,
                    status VARCHAR(16) DEFAULT 'active',
                    timestamp {ts_type}
                );
                """,
                # 9. predictions table
                f"""
                CREATE TABLE IF NOT EXISTS predictions (
                    id {pk_type},
                    prediction_type VARCHAR(64) NOT NULL,
                    predicted_value FLOAT NOT NULL,
                    confidence_or_r2 FLOAT DEFAULT 0.94,
                    features_json TEXT,
                    timestamp {ts_type}
                );
                """,
                # 10. maintenance_records table
                f"""
                CREATE TABLE IF NOT EXISTS maintenance_records (
                    id {pk_type},
                    equipment_id VARCHAR(32) NOT NULL,
                    fault_type VARCHAR(128),
                    action_taken TEXT,
                    technician VARCHAR(128),
                    resolved_at {ts_type}
                );
                """
            ]

            for q in queries:
                cursor.execute(q)

            if not self.use_mysql:
                conn.commit()
            print("[Database] Initialized all 10 schema tables successfully.")
        finally:
            conn.close()

    def seed_demo_data(self):
        """Populates sample building rows if tables are empty."""
        users = self.execute_query("SELECT id FROM users LIMIT 1;")
        if users:
            return  # Already seeded

        print("[Database] Seeding initial demo building data...")

        # 1. Users
        self.execute_query(
            "INSERT INTO users (username, password_hash, full_name, email, role) VALUES (%s, %s, %s, %s, %s);" if self.use_mysql
            else "INSERT INTO users (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?);",
            ("admin", "admin123", "Dr. Alexander Vance", "admin@apexbuilding.ai", "Admin")
        )
        self.execute_query(
            "INSERT INTO users (username, password_hash, full_name, email, role) VALUES (%s, %s, %s, %s, %s);" if self.use_mysql
            else "INSERT INTO users (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?);",
            ("manager", "manager123", "Facility Mgr. Jordan", "manager@apexbuilding.ai", "Building Manager")
        )

        # 2. Building
        self.execute_query(
            "INSERT INTO buildings (name, location, total_area_sqft, total_floors, max_capacity, base_tariff) VALUES (%s, %s, %s, %s, %s, %s);" if self.use_mysql
            else "INSERT INTO buildings (name, location, total_area_sqft, total_floors, max_capacity, base_tariff) VALUES (?, ?, ?, ?, ?, ?);",
            ("Smart Tower", "Metro Innovation District", 185000, 3, 600, 0.16)
        )

        # 3. Floors
        floors = [
            (1, 1, 1, "Floor 1 - Public & Hub", 78.4, 145, 220, "normal"),
            (2, 1, 2, "Floor 2 - Engineering & R&D", 102.6, 128, 200, "warning"),
            (3, 1, 3, "Floor 3 - Executive & Boardroom", 67.5, 69, 180, "normal")
        ]
        for f in floors:
            self.execute_query(
                "INSERT INTO floors (id, building_id, floor_number, name, energy_kw, occupancy, max_capacity, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);" if self.use_mysql
                else "INSERT INTO floors (id, building_id, floor_number, name, energy_kw, occupancy, max_capacity, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                f
            )

        # 4. Rooms
        rooms = [
            ("101", 1, "Grand Entrance Lobby", "green", 42, 80, 22.1, 18.2, "ON", "ACTIVE", 96),
            ("102", 1, "Security & Operations Hub", "green", 12, 20, 21.5, 14.8, "ON", "ACTIVE", 98),
            ("103", 1, "Cafeteria & Social Hall", "green", 78, 100, 23.4, 34.5, "ON", "ACTIVE", 92),
            ("104", 1, "Visitor Conference A", "green", 13, 20, 22.0, 10.9, "ON", "ACTIVE", 95),
            ("201", 2, "Open Workspace Alpha", "green", 58, 80, 22.4, 26.2, "ON", "ACTIVE", 94),
            ("202", 2, "Software Eng Lab", "green", 44, 60, 22.8, 24.1, "ON", "ACTIVE", 91),
            ("203", 2, "Enterprise Server Data Center", "red", 4, 10, 27.9, 42.8, "ON", "OVERLOAD", 58),
            ("204", 2, "Executive Meeting Room", "green", 22, 50, 22.0, 9.5, "ON", "ACTIVE", 96),
            ("301", 3, "Executive Boardroom", "green", 18, 40, 21.8, 16.4, "ON", "ACTIVE", 95),
            ("302", 3, "Executive Suites", "green", 14, 30, 21.5, 15.2, "ON", "ACTIVE", 97),
            ("303", 3, "Open Workspace Beta", "yellow", 32, 70, 24.2, 28.1, "ON", "ECO", 74),
            ("304", 3, "AI Innovation Studio", "green", 5, 40, 21.6, 7.8, "DIM", "ECO", 93)
        ]
        for r in rooms:
            self.execute_query(
                "INSERT INTO rooms (id, floor_id, name, status, occupancy, capacity, temp_c, power_kw, lighting, hvac, health) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);" if self.use_mysql
                else "INSERT INTO rooms (id, floor_id, name, status, occupancy, capacity, temp_c, power_kw, lighting, hvac, health) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                r
            )

        # 5. Equipment
        equip = [
            ("EQ-101", "Main Chiller Unit 1", "HVAC", 1, 4.0, 86.0, 62.4, "Normal", 93, 12.0, 12450, 1),
            ("EQ-102", "Secondary Chiller Unit 2", "HVAC", 2, 7.0, 94.0, 84.8, "Maintenance Required", 58, 78.0, 24890, 4),
            ("EQ-103", "Central AHU-1 (Air Handler)", "HVAC", 1, 3.0, 72.0, 45.2, "Normal", 89, 16.0, 8920, 0),
            ("EQ-104", "Passenger Elevator Lift-A", "Elevator", 1, 5.0, 82.0, 52.0, "Normal", 84, 22.0, 16300, 2),
            ("EQ-105", "High-Capacity Freight Lift-B", "Elevator", 2, 8.0, 68.0, 76.5, "Maintenance Required", 62, 69.0, 27100, 5),
            ("EQ-106", "Data Center CRAC Cooling System", "Server/IT", 2, 2.0, 96.0, 39.1, "Normal", 95, 9.0, 17200, 0),
            ("EQ-107", "Emergency Diesel Generator", "Generator", 1, 6.0, 8.0, 28.0, "Normal", 92, 14.0, 420, 1),
            ("EQ-108", "Building LED Smart Matrix Controller", "Lighting", 3, 1.0, 64.0, 31.4, "Normal", 99, 3.0, 7400, 0)
        ]
        for e in equip:
            self.execute_query(
                "INSERT INTO equipment (id, name, category, floor_num, age_years, usage_percent, temp_c, status, health_score, risk_percent, run_hours, prev_faults) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);" if self.use_mysql
                else "INSERT INTO equipment (id, name, category, floor_num, age_years, usage_percent, temp_c, status, health_score, risk_percent, run_hours, prev_faults) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                e
            )

        # 6. Alerts
        alerts = [
            ("ALT-901", "CRITICAL", "CRITICAL", "Thermal Limit Exceeded", "Server Room 203", "Ambient temperature surged to 27.9°C (normal <= 23.5°C). Cooling cycle struggling.", "active"),
            ("ALT-902", "WARNING", "WARNING", "Predictive Maintenance Alert", "Secondary Chiller Unit 2", "Random Forest flags 78% failure risk within next 120 operating hours due to bearing friction.", "active"),
            ("ALT-903", "WARNING", "WARNING", "Energy Spikes Detected", "Floor 3 Open Workspace", "HVAC drawing 28.1 kW with only 32 occupants. Sub-optimal deadband.", "active"),
            ("ALT-904", "INFO", "INFO", "Automated Energy Optimization", "All Lighting Systems", "Off-peak energy curtailment schedule activated at 18:00.", "resolved")
        ]
        for a in alerts:
            self.execute_query(
                "INSERT INTO alerts (id, alert_type, severity, title, entity, description, status) VALUES (%s, %s, %s, %s, %s, %s, %s);" if self.use_mysql
                else "INSERT INTO alerts (id, alert_type, severity, title, entity, description, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
                a
            )

        print("[Database] Initial seeding completed successfully!")


# Global Database Singleton
_db_manager = None

def get_db():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
