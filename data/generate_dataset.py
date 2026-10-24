"""
Synthetic Building Telemetry & Equipment Dataset Generator
Creates realistic historical building time-series and equipment telemetry for ML training.
"""

import os
import numpy as np
import pandas as pd

def generate_building_energy_dataset(output_path="data/sample_building_data.csv", n_samples=3000):
    np.random.seed(42)
    
    hours = np.tile(np.arange(24), int(np.ceil(n_samples / 24)))[:n_samples]
    day_of_week = (np.arange(n_samples) // 24) % 7 # 0=Mon, 6=Sun
    is_weekend = (day_of_week >= 5).astype(int)
    
    # 1. Occupancy simulation
    base_occ = np.where(
        is_weekend == 0,
        np.maximum(15, 380 * np.exp(-((hours - 14) ** 2) / 28) + np.random.normal(0, 18, n_samples)),
        np.maximum(5, 45 * np.exp(-((hours - 14) ** 2) / 36) + np.random.normal(0, 8, n_samples))
    )
    occupancy = np.clip(np.round(base_occ), 0, 600).astype(int)
    
    # 2. Ambient outdoor temperature (deg C)
    base_temp = 22.0 + 7.0 * np.sin((hours - 9) / 24 * 2 * np.pi) + np.random.normal(0, 2.0, n_samples)
    temperature = np.clip(np.round(base_temp, 1), 12.0, 42.0)
    
    # 3. HVAC usage percentage
    temp_delta = np.abs(temperature - 21.0)
    hvac_calc = 45.0 + (temp_delta * 4.2) + (occupancy / 600.0 * 30.0) + np.random.normal(0, 4.0, n_samples)
    hvac_usage = np.clip(np.round(hvac_calc, 1), 15.0, 100.0)
    
    # 4. Lighting usage percentage
    is_daylight = ((hours >= 7) & (hours <= 18)).astype(int)
    light_calc = np.where(
        is_weekend == 0,
        np.where(is_daylight == 1, 55.0 + (occupancy / 600.0 * 35.0), 20.0 + (occupancy / 600.0 * 20.0)),
        15.0 + (occupancy / 600.0 * 20.0)
    ) + np.random.normal(0, 3.0, n_samples)
    lighting_usage = np.clip(np.round(light_calc, 1), 10.0, 100.0)
    
    # 5. Working hours
    working_hours = np.where((hours >= 8) & (hours <= 18) & (is_weekend == 0), 1, 0)
    
    # 6. Historical energy consumption
    hist_energy = np.zeros(n_samples)
    for i in range(n_samples):
        if i == 0:
            hist_energy[i] = 180.0
        else:
            hist_energy[i] = 0.85 * hist_energy[i-1] + 0.15 * (120.0 + occupancy[i]*0.25) + np.random.normal(0, 5.0)
    historical_energy = np.clip(np.round(hist_energy, 1), 80.0, 380.0)
    
    # Target: Energy consumption (kW)
    base_load = 75.0
    occ_load = occupancy * 0.16
    hvac_load = (hvac_usage / 100.0) * (60.0 + temp_delta * 6.5)
    lighting_load = (lighting_usage / 100.0) * 42.0
    hist_component = historical_energy * 0.10
    
    energy_consumption = np.round(
        base_load + occ_load + hvac_load + lighting_load + hist_component + np.random.normal(0, 4.5, n_samples),
        1
    )
    
    df_energy = pd.DataFrame({
        "occupancy": occupancy,
        "temperature": temperature,
        "hvac_usage": hvac_usage,
        "lighting_usage": lighting_usage,
        "working_hours": working_hours,
        "historical_energy": historical_energy,
        "energy_consumption": energy_consumption
    })
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df_energy.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df_energy)} rows of energy telemetry data.")
    return df_energy


def generate_equipment_dataset(output_path="data/sample_equipment_data.csv", n_samples=2000):
    np.random.seed(42)
    
    equipment_age = np.random.uniform(1.0, 12.0, n_samples).round(1)
    usage_percent = np.random.uniform(30.0, 98.0, n_samples).round(1)
    operating_hours = (equipment_age * 3000 + np.random.normal(0, 1500, n_samples)).clip(500, 38000).round(0)
    
    base_temp = 35.0 + (usage_percent * 0.4) + (equipment_age * 1.5) + np.random.normal(0, 5.0, n_samples)
    temperature = np.clip(base_temp, 25.0, 95.0).round(1)
    
    fault_lambda = (equipment_age / 3.0) + (operating_hours / 10000.0)
    previous_faults = np.random.poisson(fault_lambda, n_samples).clip(0, 10)
    
    health_calc = 100.0 - (equipment_age * 3.5) - (previous_faults * 5.0) - ((temperature - 35.0) * 0.4) + np.random.normal(0, 4.0, n_samples)
    equipment_health = np.clip(health_calc, 30.0, 100.0).round(1)
    
    risk_score = (
        (equipment_age > 6.0).astype(int) * 25 +
        (temperature > 75.0).astype(int) * 30 +
        (usage_percent > 85.0).astype(int) * 20 +
        (previous_faults >= 3).astype(int) * 25 +
        (equipment_health < 65.0).astype(int) * 35 +
        np.random.normal(0, 10, n_samples)
    )
    
    maintenance_required = (risk_score >= 50).astype(int)
    
    df_equip = pd.DataFrame({
        "equipment_age": equipment_age,
        "usage_percent": usage_percent,
        "temperature": temperature,
        "previous_faults": previous_faults,
        "operating_hours": operating_hours,
        "equipment_health": equipment_health,
        "maintenance_required": maintenance_required
    })
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df_equip.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df_equip)} rows of equipment maintenance data.")
    return df_equip


if __name__ == "__main__":
    generate_building_energy_dataset()
    generate_equipment_dataset()
