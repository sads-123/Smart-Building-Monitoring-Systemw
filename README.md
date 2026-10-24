# Smart Tower - Smart Building Monitoring System Using AI

A clean, user-friendly, and fully software-based smart building monitoring web application for **Smart Tower**. Built using **Python Flask**, **MySQL (with automatic SQLite fallback)**, **Scikit-Learn Machine Learning (Random Forest Regression)**, and **HTML5 / CSS3 / Vanilla JavaScript**.

> **Note**: This application is 100% software-based and simulated. It does **not** require physical Arduino, ESP32, or IoT hardware.

---

## Key Modules & Features

1. **Simple Authentication**:
   - Clean login with demo credentials provided right on the login screen.
   - Session management and theme selection.

2. **Main Dashboard**:
   - 8 Real-time KPI Cards: Total kW, accumulated kWh, people inside, average temperature, estimated electricity cost, equipment condition, active warnings, and Building Health Score.
   - Clean single overview chart: Real-time electricity used by floor.
   - Virtual building room snapshot and machine health watchlist.
   - Quick electricity-saving AI tips and recent warnings.

3. **Virtual 3D Building**:
   - Interactive 3-floor visualizer with 12 monitored rooms.
   - Color-coded room status (**Normal**, **Attention**, **Warning**).
   - Real-time room metrics: occupancy, temperature, and power draw.

4. **Electricity & Power Usage**:
   - Clear electrical load breakdown by floor and room.
   - Real-time power draw (kW), accumulated daily units (kWh), and cost estimates ($).

5. **People & Room Crowding**:
   - Room-by-room occupancy counter and density status.
   - Real-time count of people on each floor.

6. **Equipment Status**:
   - Clear asset tracking for cooling chillers, ventilation fans, elevators, and generators.
   - Shows machine temperature, health percentage, risk level, and operational status.

7. **AI Energy Predictions (Single ML Component)**:
   - Uses **Random Forest Regression** trained on 3,000 historical building records.
   - Predicts future electricity consumption (kW, daily kWh, and cost) based on expected occupancy, temperature, AC usage, and lighting.
   - Simplified user-friendly presentation without intimidating technical jargon.

8. **AI Electricity Tips**:
   - Easy, practical, everyday recommendations to reduce the electricity bill.
   - Interactive savings calculator: adjust AC temperature or dim window lights to see immediate dollar savings.

9. **Building Alerts & Warnings**:
   - Simplified warning cards showing which machine or room is in an alert state, where it is located, and recommended action.

10. **Summary Reports**:
    - Clean on-screen status reports for electricity usage, occupancy, machine health, and warning history.
    - Single summary comparison chart of electricity usage by floor.

11. **System Settings**:
    - Profile management, electricity tariff configuration ($0.16/kWh), and alert sensitivity controls.

---

## Project Structure

```text
Smart-Building-Monitoring-System/
├── frontend/
│   ├── index.html            # Login Page
│   ├── dashboard.html        # Main Overview Dashboard
│   ├── digital-twin.html     # Virtual Multi-Floor 3D View
│   ├── energy.html           # Electricity & Power Usage
│   ├── occupancy.html        # People & Room Crowding
│   ├── equipment.html        # Equipment Status
│   ├── predictions.html      # AI Energy Predictions (Random Forest)
│   ├── tips.html             # AI Electricity Saving Tips & Calculator
│   ├── alerts.html           # Building Alerts & Warnings
│   ├── reports.html          # On-Screen Summary Reports
│   ├── settings.html         # System Settings
│   ├── css/
│   │   └── style.css         # Modern, clean stylesheet
│   └── js/
│       ├── data-store.js     # Simulation engine & telemetry store
│       ├── navigation.js     # Navigation & authentication guard
│       └── dashboard.js      # Dashboard controller & charts
│
├── backend/
│   ├── app.py                # Main Flask application & background telemetry
│   ├── config.py             # App configuration (MySQL & SQLite fallback)
│   ├── routes/
│   │   └── api.py            # REST API endpoints
│   └── database/
│       ├── db.py             # Database connector (MySQL / SQLite)
│       └── schema.sql        # Database schema definition
│
├── ml/
│   ├── energy_prediction.py  # Random Forest Regression energy predictor
│   └── models/               # Saved trained model artifacts
│
├── data/
│   └── sample_building_data.csv # 3,000 historical training records
│
├── requirements.txt          # Python dependencies
├── run.py                    # One-command project launcher
└── README.md                 # Project documentation
```

---

## Quick Setup & Execution

### 1. Requirements
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13 supported)
- MySQL Server (optional; if MySQL is not running, the system automatically uses SQLite fallback without any configuration needed)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python run.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

### 4. Demo Login Credentials
- **Role**: Administrator
- **Username**: `admin`
- **Password**: `admin123`
- *(Or click the "1-Click Demo Login" button directly on the login page)*
