"""
Main Application Server - Flask
Serves the Vanilla JS / HTML5 frontend and provides the REST API endpoints
for the Smart Building Monitoring System Using AI.
Includes a background telemetry simulation thread for dynamic IoT updates.
"""

import os
import sys
import time
import random
import threading

# Ensure project root is in sys.path so 'backend.*' and 'ml.*' imports always succeed
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, send_from_directory, redirect
from backend.config import Config
from backend.database.db import get_db
from backend.routes.api import api_bp

# Define frontend static directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR)
app.config.from_object(Config)

# Register API Blueprint
app.register_blueprint(api_bp)


# ---------------------------------------------------------
# FRONTEND STATIC ROUTING
# ---------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
        return send_from_directory(FRONTEND_DIR, filename)
    # Default fallback
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------------------------------------------------------
# BACKGROUND TELEMETRY SIMULATION WORKER
# ---------------------------------------------------------
def background_telemetry_loop():
    """Simulates real-time sensor updates in the database every 4 seconds."""
    time.sleep(2)
    print("[Simulator Worker] Background IoT telemetry thread started.")
    db = get_db()
    ph = "%s" if db.use_mysql else "?"

    while True:
        try:
            rooms = db.execute_query("SELECT id, occupancy, capacity, temp_c, power_kw FROM rooms;")
            if rooms:
                total_kw = 0
                for r in rooms:
                    # Minor random walk
                    occ_drift = random.choice([-1, 0, 0, 1])
                    new_occ = max(0, min(r["capacity"], r["occupancy"] + occ_drift))
                    
                    temp_drift = round(random.uniform(-0.1, 0.1), 1)
                    new_temp = round(r["temp_c"] + temp_drift, 1)
                    
                    occ_factor = (new_occ / (r["capacity"] or 1))
                    base = 15.0 if r["id"] != "203" else 42.0
                    new_kw = round(base + (occ_factor * 10.0) + random.uniform(-0.5, 0.5), 1)
                    total_kw += new_kw

                    db.execute_query(
                        f"UPDATE rooms SET occupancy = {ph}, temp_c = {ph}, power_kw = {ph} WHERE id = {ph};",
                        (new_occ, new_temp, new_kw, r["id"])
                    )

                # Update floor energy sums
                db.execute_query(
                    f"UPDATE floors SET energy_kw = (SELECT SUM(power_kw) FROM rooms WHERE floor_id = floors.id);"
                )

            # Equipment temperature jitter
            equip = db.execute_query("SELECT id, temp_c FROM equipment;")
            for e in equip:
                e_temp = round(e["temp_c"] + random.uniform(-0.2, 0.2), 1)
                db.execute_query(
                    f"UPDATE equipment SET temp_c = {ph} WHERE id = {ph};",
                    (e_temp, e["id"])
                )

        except Exception as err:
            # Silent catch to keep thread alive
            pass

        time.sleep(Config.SIMULATION_INTERVAL)


# Start background worker daemon
sim_thread = threading.Thread(target=background_telemetry_loop, daemon=True)
sim_thread.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 65)
    print("  Smart Tower - SMART BUILDING MONITORING SYSTEM USING AI")
    print("=" * 65)
    print(f"  * Frontend:       Vanilla HTML5 + CSS3 + JavaScript")
    print(f"  * Backend:        Python Flask")
    print(f"  * Database:       {'MySQL' if get_db().use_mysql else 'SQLite (Fallback)'}")
    print(f"  * Machine Learning: Random Forest Regressor (Energy Prediction)")
    print(f"  * Running on:     http://localhost:{port}")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
