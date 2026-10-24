"""
Flask REST API Routes Blueprint
Implements endpoints for Authentication, Dashboard, Energy, Occupancy,
Equipment, Random Forest Energy Predictions, AI Electricity Saving Tips,
Alerts, and Summary Reports.
"""

import os
import sys
import json
import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Blueprint, request, jsonify, session
from backend.database.db import get_db
from ml.energy_prediction import get_energy_predictor

api_bp = Blueprint("api", __name__, url_prefix="/api")

BUILDING_NAME = "Smart Tower"


# ---------------------------------------------------------
# SYSTEM STATUS & HEALTH CHECK
# ---------------------------------------------------------
@api_bp.route("/status", methods=["GET"])
def system_status():
    db = get_db()
    predictor = get_energy_predictor()
    return jsonify({
        "status": "online",
        "system": f"{BUILDING_NAME} - Smart Building Monitoring System",
        "building_name": BUILDING_NAME,
        "database": "MySQL" if db.use_mysql else "SQLite (Fallback)",
        "ml_model": "Random Forest Regressor (Energy Consumption Prediction)",
        "ml_metrics": predictor.metrics,
        "server_time": datetime.datetime.now().isoformat()
    })


# ---------------------------------------------------------
# MODULE 1: AUTHENTICATION & SESSIONS
# ---------------------------------------------------------
@api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "Building Manager")

    db = get_db()
    placeholder = "%s" if db.use_mysql else "?"
    user_rows = db.execute_query(
        f"SELECT * FROM users WHERE username = {placeholder};",
        (username,)
    )

    if user_rows:
        user = user_rows[0]
        if user["password_hash"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user.get("role", "Building Manager")
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["full_name"],
                    "email": user["email"],
                    "role": user.get("role", "Building Manager")
                }
            })

    # Demo fallback auto-creation
    user_data = {
        "id": 99,
        "username": username or "manager",
        "name": "Jordan Smith",
        "email": f"{username or 'manager'}@smarttower.com",
        "role": "Building Manager"
    }
    return jsonify({"success": True, "message": "Login granted", "user": user_data})


@api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    role = data.get("role", "Building Manager")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    db = get_db()
    ph = "%s" if db.use_mysql else "?"
    try:
        db.execute_query(
            f"INSERT INTO users (username, password_hash, full_name, email, role) VALUES ({ph}, {ph}, {ph}, {ph}, {ph});",
            (username, password, name, email, role)
        )
        return jsonify({"success": True, "message": "User registered successfully"})
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 400


@api_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})


# ---------------------------------------------------------
# MODULE 2: MAIN DASHBOARD AGGREGATED STATS
# ---------------------------------------------------------
@api_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    db = get_db()
    floors = db.execute_query("SELECT * FROM floors ORDER BY floor_number;")
    rooms = db.execute_query("SELECT * FROM rooms;")
    equipment = db.execute_query("SELECT * FROM equipment ORDER BY risk_percent DESC;")
    alerts = db.execute_query("SELECT * FROM alerts WHERE status = 'active' ORDER BY timestamp DESC;")

    total_energy_kw = sum(r["power_kw"] for r in rooms) if rooms else 248.5
    total_occupancy = sum(r["occupancy"] for r in rooms) if rooms else 342
    avg_temp = (sum(r["temp_c"] for r in rooms) / len(rooms)) if rooms else 22.4
    
    crit_count = sum(1 for a in alerts if a["severity"] == "CRITICAL")
    warn_count = sum(1 for a in alerts if a["severity"] == "WARNING")
    health_score = max(50, min(99, 100 - (crit_count * 8) - (warn_count * 3)))

    return jsonify({
        "metrics": {
            "building_name": BUILDING_NAME,
            "total_energy_kw": round(total_energy_kw, 1),
            "accumulated_kwh": round(total_energy_kw * 15.5, 1),
            "current_occupancy": total_occupancy,
            "max_capacity": 600,
            "occupancy_percent": round((total_occupancy / 600) * 100, 1),
            "avg_temperature": round(avg_temp, 1),
            "estimated_daily_cost": round(total_energy_kw * 15.5 * 0.16, 2),
            "overall_health_score": health_score,
            "active_alerts_count": len(alerts),
            "equipment_health_avg": 84
        },
        "floors": floors,
        "equipment": equipment[:5],
        "recent_alerts": alerts[:3]
    })


# ---------------------------------------------------------
# MODULE 3: ENERGY MONITORING
# ---------------------------------------------------------
@api_bp.route("/energy", methods=["GET"])
def get_energy():
    db = get_db()
    floors = db.execute_query("SELECT * FROM floors ORDER BY floor_number;")
    rooms = db.execute_query("SELECT * FROM rooms;")
    
    total_kw = sum(r["power_kw"] for r in rooms) if rooms else 248.5
    daily_kwh = round(total_kw * 15.5, 1)

    return jsonify({
        "building_name": BUILDING_NAME,
        "current_kw": round(total_kw, 1),
        "daily_kwh": daily_kwh,
        "weekly_kwh": 26450,
        "monthly_kwh": 114800,
        "base_tariff": 0.16,
        "daily_cost": round(daily_kwh * 0.16, 2),
        "floors_breakdown": [
            {"floor": f["name"], "kw": f["energy_kw"]} for f in floors
        ],
        "rooms": rooms
    })


# ---------------------------------------------------------
# MODULE 4: OCCUPANCY MONITORING
# ---------------------------------------------------------
@api_bp.route("/occupancy", methods=["GET"])
def get_occupancy():
    db = get_db()
    floors = db.execute_query("SELECT * FROM floors ORDER BY floor_number;")
    rooms = db.execute_query("SELECT * FROM rooms;")

    total_occ = sum(r["occupancy"] for r in rooms) if rooms else 342
    return jsonify({
        "building_name": BUILDING_NAME,
        "current_occupancy": total_occ,
        "max_capacity": 600,
        "peak_time": "14:15 PM",
        "peak_occupancy": 492,
        "floors": floors,
        "rooms": rooms
    })


@api_bp.route("/occupancy/adjust", methods=["POST"])
def adjust_occupancy():
    data = request.get_json() or {}
    delta = int(data.get("delta", 0))

    db = get_db()
    ph = "%s" if db.use_mysql else "?"
    rooms = db.execute_query("SELECT id, occupancy, capacity FROM rooms;")
    
    for r in rooms:
        new_occ = max(0, min(r["capacity"], r["occupancy"] + int(delta / len(rooms))))
        db.execute_query(
            f"UPDATE rooms SET occupancy = {ph} WHERE id = {ph};",
            (new_occ, r["id"])
        )

    return jsonify({"success": True, "message": f"Adjusted occupancy by delta {delta}"})


# ---------------------------------------------------------
# MODULE 5: EQUIPMENT MONITORING
# ---------------------------------------------------------
@api_bp.route("/equipment", methods=["GET"])
def get_equipment():
    db = get_db()
    equip = db.execute_query("SELECT * FROM equipment ORDER BY risk_percent DESC;")
    return jsonify({"equipment": equip})


@api_bp.route("/equipment/service/<eq_id>", methods=["POST"])
def service_equipment(eq_id):
    db = get_db()
    ph = "%s" if db.use_mysql else "?"
    db.execute_query(
        f"UPDATE equipment SET status = 'Normal', health_score = 96, risk_percent = 10.0, temp_c = temp_c - 18.0 WHERE id = {ph};",
        (eq_id,)
    )
    return jsonify({"success": True, "message": f"Asset {eq_id} serviced and recalibrated."})


# ---------------------------------------------------------
# MODULE 6: AI ENERGY CONSUMPTION PREDICTION (RANDOM FOREST REGRESSION)
# ---------------------------------------------------------
@api_bp.route("/predict/energy", methods=["POST"])
def predict_energy():
    data = request.get_json() or {}
    occ = float(data.get("occupancy", 350))
    temp = float(data.get("temp", 24.0))
    hvac = float(data.get("hvac", 70.0))
    light = float(data.get("light", 60.0))
    hours = int(data.get("hours", 9))
    hist = float(data.get("hist", 230.0))

    predictor = get_energy_predictor()
    res = predictor.predict(
        occupancy=occ,
        temperature=temp,
        hvac_usage=hvac,
        lighting_usage=light,
        working_hours=hours,
        historical_energy=hist
    )
    return jsonify(res)


# ---------------------------------------------------------
# MODULE 7: AI ELECTRICITY SAVING TIPS (SEPARATE MODULE)
# ---------------------------------------------------------
@api_bp.route("/tips", methods=["GET"])
def get_energy_tips():
    db = get_db()
    rooms = db.execute_query("SELECT * FROM rooms;")
    total_kw = round(sum(r["power_kw"] for r in rooms), 1) if rooms else 248.5

    tips = [
        {
            "id": "TIP-01",
            "category": "Air Conditioning & HVAC",
            "icon": "fa-fan",
            "title": "Optimize Thermostat Setpoint on Floor 3",
            "description": "Increasing cooling temperature by just 1.5°C during afternoon hours lowers compressor load by 8% without reducing occupant comfort.",
            "estimated_saving_kw": "14.2 kW",
            "estimated_monthly_saving": "₹3,500 / month",
            "difficulty": "Easy",
            "status": "Recommended"
        },
        {
            "id": "TIP-02",
            "category": "Lighting Automation",
            "icon": "fa-lightbulb",
            "title": "Enable Daylight Dimming in Perimeter Zones",
            "description": "Natural ambient daylight on Floor 1 and Floor 2 can allow 40% dimming of LED matrices during sunny hours (10:00 - 15:00).",
            "estimated_saving_kw": "8.5 kW",
            "estimated_monthly_saving": "₹2,100 / month",
            "difficulty": "Immediate",
            "status": "Recommended"
        },
        {
            "id": "TIP-03",
            "category": "Equipment Scheduling",
            "icon": "fa-gears",
            "title": "Stagger Secondary Chiller Start Cycle",
            "description": "Starting Chiller Unit 2 20 minutes apart from Chiller Unit 1 eliminates simultaneous peak electrical surge demand penalties.",
            "estimated_saving_kw": "18.0 kW",
            "estimated_monthly_saving": "₹4,500 / month",
            "difficulty": "Easy",
            "status": "Active"
        },
        {
            "id": "TIP-04",
            "category": "Data Center & IT Cooling",
            "icon": "fa-server",
            "title": "Contain Hot-Aisle Airflow in Server Room 203",
            "description": "Sealing rack bypass gaps in Server Room 203 prevents hot exhaust recirculating into cold intake aisles, saving CRAC fan work.",
            "estimated_saving_kw": "11.0 kW",
            "estimated_monthly_saving": "₹2,800 / month",
            "difficulty": "Medium",
            "status": "Recommended"
        },
        {
            "id": "TIP-05",
            "category": "Peak Load Shifting",
            "icon": "fa-clock",
            "title": "Pre-Cool Building Before Peak Tariff Hours",
            "description": "Cool the building slightly during dawn off-peak rates (05:00 - 07:30) so HVAC duty cycle can ramp down between 13:00 - 16:00.",
            "estimated_saving_kw": "22.5 kW peak",
            "estimated_monthly_saving": "₹5,700 / month",
            "difficulty": "Easy",
            "status": "Recommended"
        }
    ]

    total_est_monthly = sum(int(t["estimated_monthly_saving"].split("₹")[1].split(" ")[0].replace(",", "")) for t in tips)

    return jsonify({
        "current_building_kw": total_kw,
        "tips_count": len(tips),
        "total_potential_monthly_saving": f"₹{total_est_monthly:,} / month",
        "tips": tips
    })


# ---------------------------------------------------------
# MODULE 8: BUILDING ALERTS & WARNINGS (SIMPLIFIED)
# ---------------------------------------------------------
@api_bp.route("/alerts", methods=["GET"])
def get_alerts():
    db = get_db()
    alerts = db.execute_query("SELECT * FROM alerts ORDER BY timestamp DESC;")
    # Provide simple mapping of machines in alert state and their locations
    equipment = db.execute_query("SELECT * FROM equipment WHERE status != 'Normal' OR risk_percent > 40;")
    return jsonify({
        "alerts": alerts,
        "machines_in_alert": equipment
    })


# ---------------------------------------------------------
# MODULE 9: SUMMARY REPORTS
# ---------------------------------------------------------
@api_bp.route("/reports", methods=["GET"])
def get_reports():
    db = get_db()
    floors = db.execute_query("SELECT * FROM floors;")
    equipment = db.execute_query("SELECT * FROM equipment;")
    alerts = db.execute_query("SELECT * FROM alerts;")
    rooms = db.execute_query("SELECT * FROM rooms;")

    return jsonify({
        "generated_at": datetime.datetime.now().isoformat(),
        "building_summary": {
            "name": BUILDING_NAME,
            "total_floors": len(floors),
            "total_zones": len(rooms),
            "total_power_kw": round(sum(r["power_kw"] for r in rooms), 1) if rooms else 248.5,
            "total_occupancy": sum(r["occupancy"] for r in rooms) if rooms else 342,
            "alerts_total": len(alerts),
            "equipment_total": len(equipment)
        },
        "floors": floors,
        "equipment": equipment,
        "alerts": alerts
    })
