"""
Application Configuration
Configures MySQL database credentials, session secrets, and automatic database fallback.
"""

import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "smart-building-ai-super-secret-key-2026")
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "smart_building_db")
    
    # SQLite Fallback path (used if MySQL is not running)
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "database", "smart_building.db")
    
    # Simulation Tick Interval in seconds
    SIMULATION_INTERVAL = 4.0
