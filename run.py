"""
Quick Launch Script for Smart Building Monitoring System Using AI
Usage:
    python run.py
"""

import os
import sys

# Ensure root directory is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 65)
    print("  SMART TOWER - SMART BUILDING MONITORING SYSTEM USING AI")
    print("=" * 65)
    print(f"  * Frontend:       Vanilla HTML5 + CSS3 + JavaScript")
    print(f"  * Backend:        Python Flask")
    print(f"  * Machine Learning: Random Forest Regressor (Energy Prediction)")
    print(f"  * Access at:      http://localhost:{port}")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
