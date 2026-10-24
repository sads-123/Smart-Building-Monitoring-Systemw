"""
AI Energy Prediction Module - Random Forest Regression
Predicts building energy consumption (kW) based on occupancy, temperature,
HVAC schedule, lighting usage, working hours, and historical lag values.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_FILE = os.path.join(MODEL_DIR, "energy_rf_model.pkl")
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_building_data.csv")

FEATURE_COLS = [
    "occupancy",
    "temperature",
    "hvac_usage",
    "lighting_usage",
    "working_hours",
    "historical_energy"
]
TARGET_COL = "energy_consumption"


class EnergyPredictionModel:
    def __init__(self):
        self.model = None
        self.metrics = {}
        self.feature_importances = {}
        self.load_or_train()

    def train(self, data_path=None):
        data_path = data_path or DATA_FILE
        if not os.path.exists(data_path):
            from data.generate_dataset import generate_building_energy_dataset
            print("[ML-Energy] Generating synthetic dataset...")
            df = generate_building_energy_dataset(data_path)
        else:
            df = pd.read_csv(data_path)

        X = df[FEATURE_COLS]
        y = df[TARGET_COL]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=1
        )
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        self.model = rf
        self.metrics = {
            "r2_score": round(float(r2), 4),
            "mae_kw": round(float(mae), 2),
            "rmse_kw": round(float(rmse), 2),
            "n_samples": len(df)
        }

        self.feature_importances = {
            col: round(float(imp), 4)
            for col, imp in zip(FEATURE_COLS, rf.feature_importances_)
        }

        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "metrics": self.metrics,
            "feature_importances": self.feature_importances
        }, MODEL_FILE)

        print(f"[ML-Energy] Trained Random Forest Regressor! R^2: {self.metrics['r2_score']} | MAE: {self.metrics['mae_kw']} kW")
        return self.metrics

    def load_or_train(self):
        if os.path.exists(MODEL_FILE):
            try:
                bundle = joblib.load(MODEL_FILE)
                self.model = bundle["model"]
                self.metrics = bundle.get("metrics", {})
                self.feature_importances = bundle.get("feature_importances", {})
                return
            except Exception as e:
                print(f"[ML-Energy] Retraining model due to cache error: {e}")
        self.train()

    def predict(self, occupancy, temperature, hvac_usage, lighting_usage, working_hours, historical_energy):
        if self.model is None:
            self.load_or_train()

        input_data = pd.DataFrame([{
            "occupancy": float(occupancy),
            "temperature": float(temperature),
            "hvac_usage": float(hvac_usage),
            "lighting_usage": float(lighting_usage),
            "working_hours": int(working_hours),
            "historical_energy": float(historical_energy)
        }])[FEATURE_COLS]

        pred_kw = float(self.model.predict(input_data)[0])
        est_daily_kwh = (pred_kw * (working_hours if working_hours > 0 else 8)) + (75.0 * 0.4 * 16)
        est_daily_cost = est_daily_kwh * 8.50

        return {
            "predicted_kw": round(pred_kw, 1),
            "estimated_daily_kwh": round(est_daily_kwh, 1),
            "predicted_cost": round(est_daily_cost, 2),
            "model_r2": self.metrics.get("r2_score", 0.94)
        }


_energy_predictor = None

def get_energy_predictor():
    global _energy_predictor
    if _energy_predictor is None:
        _energy_predictor = EnergyPredictionModel()
    return _energy_predictor


if __name__ == "__main__":
    predictor = EnergyPredictionModel()
    sample = predictor.predict(350, 24.5, 75.0, 65.0, 1, 240.0)
    print("Sample Energy Prediction Result:", sample)
