/**
 * Smart Building Monitoring System - Data Store & Simulation Engine
 * Manages virtual building digital twin state, dynamic telemetry,
 * real-time ticks, local storage persistence, and API bridges.
 */

(function () {
  const STORAGE_KEY = 'smart_tower_building_state_v4';
  const AUTH_KEY = 'smart_tower_building_auth_v4';

  // Initial Seed Building State
  const defaultBuildingData = {
    meta: {
      buildingName: "Smart Tower",
      totalAreaSqFt: 185000,
      totalFloors: 3,
      totalRooms: 12,
      baseEnergyRatePerKwh: 8.50, // ₹ / kWh
      lastUpdated: new Date().toISOString()
    },
    metrics: {
      totalEnergyKW: 248.5,
      energyAccumulatedKWh: 3840.2,
      currentOccupancy: 342,
      maxCapacity: 600,
      avgTemperature: 22.4, // Celsius
      estimatedDailyCost: 32641.70,
      overallHealthScore: 89,
      activeAlertsCount: 3,
      equipmentHealthAvg: 84
    },
    floors: [
      {
        id: 1,
        name: "Floor 1 - Public & Hub",
        energyKW: 78.4,
        occupancy: 145,
        maxCapacity: 220,
        avgTemp: 22.8,
        status: "normal",
        rooms: [
          { id: "101", name: "Grand Entrance Lobby", status: "green", occupancy: 42, capacity: 80, temp: 22.1, powerKW: 18.2, lighting: "ON", hvac: "ACTIVE", health: 96, alert: null },
          { id: "102", name: "Security & Operations Hub", status: "green", occupancy: 12, capacity: 20, temp: 21.5, powerKW: 14.8, lighting: "ON", hvac: "ACTIVE", health: 98, alert: null },
          { id: "103", name: "Cafeteria & Social Hall", status: "green", occupancy: 78, capacity: 100, temp: 23.4, powerKW: 34.5, lighting: "ON", hvac: "ACTIVE", health: 92, alert: null },
          { id: "104", name: "Visitor Conference A", status: "green", occupancy: 13, capacity: 20, temp: 22.0, powerKW: 10.9, lighting: "ON", hvac: "ACTIVE", health: 95, alert: null }
        ]
      },
      {
        id: 2,
        name: "Floor 2 - Engineering & R&D",
        energyKW: 102.6,
        occupancy: 128,
        maxCapacity: 200,
        avgTemp: 23.6,
        status: "warning",
        rooms: [
          { id: "201", name: "Open Workspace Alpha", status: "green", occupancy: 58, capacity: 80, temp: 22.4, powerKW: 26.2, lighting: "ON", hvac: "ACTIVE", health: 94, alert: null },
          { id: "202", name: "Software Eng Lab", status: "green", occupancy: 44, capacity: 60, temp: 22.8, powerKW: 24.1, lighting: "ON", hvac: "ACTIVE", health: 91, alert: null },
          { id: "203", name: "Enterprise Server Data Center", status: "red", occupancy: 4, capacity: 10, temp: 27.9, powerKW: 42.8, lighting: "ON", hvac: "OVERLOAD", health: 58, alert: "CRITICAL: Server room thermal dissipation exceeding safety thresholds (27.9°C)" },
          { id: "204", name: "Executive Meeting Room", status: "green", occupancy: 22, capacity: 50, temp: 22.0, powerKW: 9.5, lighting: "ON", hvac: "ACTIVE", health: 96, alert: null }
        ]
      },
      {
        id: 3,
        name: "Floor 3 - Executive & Boardroom",
        energyKW: 67.5,
        occupancy: 69,
        maxCapacity: 180,
        avgTemp: 21.9,
        status: "normal",
        rooms: [
          { id: "301", name: "Executive Boardroom", status: "green", occupancy: 18, capacity: 40, temp: 21.8, powerKW: 16.4, lighting: "ON", hvac: "ACTIVE", health: 95, alert: null },
          { id: "302", name: "Executive Suites", status: "green", occupancy: 14, capacity: 30, temp: 21.5, powerKW: 15.2, lighting: "ON", hvac: "ACTIVE", health: 97, alert: null },
          { id: "303", name: "Open Workspace Beta", status: "yellow", occupancy: 32, capacity: 70, temp: 24.2, powerKW: 28.1, lighting: "ON", hvac: "ECO", health: 74, alert: "WARNING: High HVAC power consumption relative to occupancy" },
          { id: "304", name: "AI Innovation Studio", status: "green", occupancy: 5, capacity: 40, temp: 21.6, powerKW: 7.8, lighting: "DIM", hvac: "ECO", health: 93, alert: null }
        ]
      }
    ],
    equipment: [
      { id: "EQ-101", name: "Main Chiller 1", category: "HVAC", floor: 1, ageYears: 4, usagePercent: 86, tempC: 62.4, status: "Normal", health: 93, riskPercent: 12, runHours: 12450, prevFaults: 1 },
      { id: "EQ-102", name: "Secondary Chiller 2", category: "HVAC", floor: 2, ageYears: 7, usagePercent: 94, tempC: 84.8, status: "Maintenance Required", health: 58, riskPercent: 78, runHours: 24890, prevFaults: 4 },
      { id: "EQ-103", name: "Air Handling Unit 1", category: "HVAC", floor: 1, ageYears: 3, usagePercent: 72, tempC: 45.2, status: "Normal", health: 89, riskPercent: 16, runHours: 8920, prevFaults: 0 },
      { id: "EQ-104", name: "Passenger Elevator A", category: "Elevator", floor: 1, ageYears: 5, usagePercent: 82, tempC: 52.0, status: "Normal", health: 84, riskPercent: 22, runHours: 16300, prevFaults: 2 },
      { id: "EQ-105", name: "Freight Elevator B", category: "Elevator", floor: 2, ageYears: 8, usagePercent: 68, tempC: 76.5, status: "Maintenance Required", health: 62, riskPercent: 69, runHours: 27100, prevFaults: 5 },
      { id: "EQ-106", name: "Server Room Air Conditioner", category: "Server/IT", floor: 2, ageYears: 2, usagePercent: 96, tempC: 39.1, status: "Normal", health: 95, riskPercent: 9, runHours: 17200, prevFaults: 0 },
      { id: "EQ-107", name: "Backup Power Generator 1", category: "Generator", floor: 1, ageYears: 6, usagePercent: 8, tempC: 28.0, status: "Normal", health: 92, riskPercent: 14, runHours: 420, prevFaults: 1 },
      { id: "EQ-108", name: "Smart Lighting System", category: "Lighting", floor: 3, ageYears: 1, usagePercent: 64, tempC: 31.4, status: "Normal", health: 99, riskPercent: 3, runHours: 7400, prevFaults: 0 }
    ],
    alerts: [
      { id: "ALT-901", type: "CRITICAL", title: "Thermal Limit Exceeded", entity: "Server Room 203", description: "Ambient temperature has surged to 27.9°C (normal threshold <= 23.5°C). Cooling cycle struggling.", timestamp: new Date(Date.now() - 14 * 60000).toISOString(), status: "active" },
      { id: "ALT-902", type: "WARNING", title: "Predictive Maintenance Alert", entity: "Secondary Chiller 2", description: "Machine health check flags 78% service need due to bearing friction vibration.", timestamp: new Date(Date.now() - 48 * 60000).toISOString(), status: "active" },
      { id: "ALT-903", type: "WARNING", title: "Energy Spikes Detected", entity: "Floor 3 Open Workspace", description: "HVAC drawing 28.1 kW with only 32 occupants. Potential sub-optimal thermostat configuration.", timestamp: new Date(Date.now() - 95 * 60000).toISOString(), status: "active" },
      { id: "ALT-904", type: "INFO", title: "Automated Energy Optimization", entity: "All Lighting Systems", description: "Off-peak energy curtailment schedule activated at 18:00.", timestamp: new Date(Date.now() - 140 * 60000).toISOString(), status: "resolved" }
    ],
    recommendations: [
      { id: "REC-1", priority: "HIGH", title: "Inspect Secondary Chiller 2 Bearing Assembly", impact: "Prevents unscheduled downtime of Floor 2 HVAC; estimated savings ₹35,000 in emergency repairs.", action: "Dispatch HVAC technician" },
      { id: "REC-2", priority: "MEDIUM", title: "Engage Server Room CRAC Auxiliary Booster", impact: "Drop server room temp from 27.9°C to nominal 21.5°C, eliminating hardware throttling risks.", action: "Engage auxiliary cooling" },
      { id: "REC-3", priority: "LOW", title: "Adjust Floor 3 Workspace Beta Thermostat Setpoint", impact: "Increasing target temp by 1.2°C during partial occupancy will save ~14.5 kWh daily.", action: "Apply eco-schedule" }
    ],
    history24h: generateInitial24hHistory()
  };

  function generateInitial24hHistory() {
    const hours = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 3600000);
      const hourVal = time.getHours();
      // Realistic diurnal building profile
      let baseOcc = 50;
      let baseKW = 120;
      if (hourVal >= 8 && hourVal <= 18) {
        baseOcc = 280 + Math.sin((hourVal - 8) / 10 * Math.PI) * 220;
        baseKW = 220 + Math.sin((hourVal - 8) / 10 * Math.PI) * 110;
      } else {
        baseOcc = 30 + Math.random() * 20;
        baseKW = 110 + Math.random() * 25;
      }
      hours.push({
        label: `${hourVal.toString().padStart(2, '0')}:00`,
        hour: hourVal,
        energyKW: Math.round(baseKW + (Math.random() * 16 - 8)),
        occupancy: Math.round(baseOcc + (Math.random() * 20 - 10)),
        avgTemp: +(21.5 + Math.sin(hourVal / 24 * Math.PI) * 2.2).toFixed(1)
      });
    }
    return hours;
  }

  // State Management Class
  class BuildingDataStore {
    constructor() {
      this.state = this.loadState();
      this.timer = null;
      this.backendAvailable = false;
      this.initAuth();
      this.startSimulation();
      this.checkBackendHealth();
    }

    loadState() {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (parsed && parsed.floors && parsed.equipment) {
            return parsed;
          }
        }
      } catch (e) {
        console.warn("Storage load error, falling back to default seed:", e);
      }
      return JSON.parse(JSON.stringify(defaultBuildingData));
    }

    saveState() {
      try {
        this.state.meta.lastUpdated = new Date().toISOString();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
        window.dispatchEvent(new CustomEvent('smartbuilding:update', { detail: this.state }));
      } catch (e) {
        console.error("Storage save failed:", e);
      }
    }

    initAuth() {
      let auth = this.getAuth();
      if (!auth) {
        // default user: Building Manager Jordan Smith
        auth = {
          isLoggedIn: true,
          username: "manager",
          name: "Jordan Smith",
          role: "Building Manager",
          email: "manager@smarttower.com"
        };
        this.setAuth(auth);
      }
    }

    getAuth() {
      try {
        const item = localStorage.getItem(AUTH_KEY);
        return item ? JSON.parse(item) : null;
      } catch (e) {
        return null;
      }
    }

    setAuth(authObj) {
      if (!authObj) {
        localStorage.removeItem(AUTH_KEY);
      } else {
        localStorage.setItem(AUTH_KEY, JSON.stringify(authObj));
      }
      window.dispatchEvent(new CustomEvent('smartbuilding:auth', { detail: authObj }));
    }

    login(username, password, role = "Building Manager") {
      const auth = {
        isLoggedIn: true,
        username: username || "manager",
        name: "Jordan Smith",
        role: "Building Manager",
        email: `${username || "manager"}@smarttower.com`,
        loginTime: new Date().toISOString()
      };
      this.setAuth(auth);
      return { success: true, user: auth };
    }

    logout() {
      this.setAuth(null);
      window.location.href = "index.html";
    }

    // Dynamic Simulation Loop (Ticks every 3.5s)
    startSimulation() {
      if (this.timer) clearInterval(this.timer);
      this.timer = setInterval(() => {
        this.simulationTick();
      }, 3500);
    }

    simulationTick() {
      // Apply micro-variations to simulate living IoT telemetry
      let totalKW = 0;
      let totalOcc = 0;
      let tempSum = 0;
      let roomCount = 0;

      this.state.floors.forEach(floor => {
        let floorKW = 0;
        let floorOcc = 0;

        floor.rooms.forEach(room => {
          roomCount++;
          // micro noise in occupancy
          const occNoise = (Math.random() > 0.6) ? (Math.random() > 0.5 ? 1 : -1) : 0;
          room.occupancy = Math.max(0, Math.min(room.capacity, room.occupancy + occNoise));

          // temperature jitter
          const tempDrift = +(Math.random() * 0.2 - 0.1).toFixed(2);
          room.temp = +(room.temp + tempDrift).toFixed(1);

          // power varies with occupancy and temperature
          const occFactor = (room.occupancy / (room.capacity || 1));
          let expectedKW = (room.capacity * 0.25) + (occFactor * 12.0) + ((room.temp > 23 ? (room.temp - 23) * 3 : 0));
          if (room.id === "203") expectedKW = 41.5 + (Math.random() * 4); // server room stays high
          room.powerKW = +(expectedKW + (Math.random() * 0.8 - 0.4)).toFixed(1);

          floorKW += room.powerKW;
          floorOcc += room.occupancy;
          tempSum += room.temp;
        });

        floor.energyKW = +floorKW.toFixed(1);
        floor.occupancy = floorOcc;
        totalKW += floorKW;
        totalOcc += floorOcc;
      });

      this.state.metrics.totalEnergyKW = +totalKW.toFixed(1);
      this.state.metrics.currentOccupancy = totalOcc;
      this.state.metrics.avgTemperature = +(tempSum / roomCount).toFixed(1);
      this.state.metrics.energyAccumulatedKWh = +(this.state.metrics.energyAccumulatedKWh + (totalKW * (3.5 / 3600))).toFixed(2);
      this.state.metrics.estimatedDailyCost = +(this.state.metrics.energyAccumulatedKWh * this.state.meta.baseEnergyRatePerKwh).toFixed(2);

      // Micro update on equipment
      this.state.equipment.forEach(eq => {
        eq.tempC = +(eq.tempC + (Math.random() * 0.4 - 0.2)).toFixed(1);
        if (eq.status === "Maintenance Required") {
          // slight risk variance
          eq.riskPercent = Math.min(99, Math.max(50, eq.riskPercent + (Math.random() > 0.5 ? 1 : -1)));
        }
      });

      // Update building health score
      const critAlerts = this.state.alerts.filter(a => a.status === 'active' && a.type === 'CRITICAL').length;
      const warnAlerts = this.state.alerts.filter(a => a.status === 'active' && a.type === 'WARNING').length;
      let calculatedHealth = 100 - (critAlerts * 8) - (warnAlerts * 3);
      this.state.metrics.overallHealthScore = Math.max(50, Math.min(99, calculatedHealth));
      this.state.metrics.activeAlertsCount = this.state.alerts.filter(a => a.status === 'active').length;

      this.saveState();
    }

    async checkBackendHealth() {
      try {
        const res = await fetch('/api/status', { method: 'GET', headers: { 'Accept': 'application/json' } });
        if (res.ok) {
          const data = await res.json();
          this.backendAvailable = true;
          console.log("[SmartBuilding] Connected to Flask Backend:", data);
        }
      } catch (e) {
        this.backendAvailable = false;
        // Running client-side standalone simulation
      }
    }

    // Method to simulate what-if scenarios
    simulateScenario(params) {
      // params: { occupancyPercent, ambientTemp, hvacUsage, lightingUsage, workingHours }
      const occ = Number(params.occupancyPercent) || 50;
      const temp = Number(params.ambientTemp) || 24;
      const hvac = Number(params.hvacUsage) || 70;
      const lighting = Number(params.lightingUsage) || 60;
      const hours = Number(params.workingHours) || 9;

      // Realistic non-linear energy physics model
      const baseLoad = 80; // Baseline server & critical systems (kW)
      const occLoad = (occ / 100) * 95; // Body heat & peripheral electronics
      const hvacThermalDelta = Math.max(0, Math.abs(temp - 21.0));
      const hvacLoad = (hvac / 100) * (65 + hvacThermalDelta * 8.5);
      const lightingLoad = (lighting / 100) * 45;

      const totalPredictedKW = +(baseLoad + occLoad + hvacLoad + lightingLoad).toFixed(1);
      const dailyKWh = +((totalPredictedKW * hours) + (baseLoad * 0.4 * (24 - hours))).toFixed(1);
      const dailyCost = +(dailyKWh * this.state.meta.baseEnergyRatePerKwh).toFixed(2);
      
      const baselineKWh = 3840;
      const deltaPercent = +(((dailyKWh - baselineKWh) / baselineKWh) * 100).toFixed(1);

      // Equipment stress index
      let equipmentRisk = "Low (14%)";
      let riskLevel = "low";
      if (hvac > 85 || temp > 30) {
        equipmentRisk = "High (82%) - Overheating risk";
        riskLevel = "critical";
      } else if (hvac > 75 || occ > 80) {
        equipmentRisk = "Moderate (54%) - Heavy motor load";
        riskLevel = "warning";
      }

      // Recommendations
      let recommendations = [];
      if (deltaPercent > 15) {
        recommendations.push("Turn off heavy AC chillers for 15 minutes each hour to save electricity.");
        recommendations.push("Cool the building early in the morning when power is cheaper.");
      }
      if (lighting > 70 && occ < 60) {
        recommendations.push("Turn off lights in empty rooms and use sunlight near windows.");
      }
      if (temp > 28) {
        recommendations.push("Warning: The server room is too hot. Lower the temperature to protect computers.");
      }
      if (recommendations.length === 0) {
        recommendations.push("All settings look great! Energy efficiency is optimal.");
      }

      return {
        predictedKW: totalPredictedKW,
        dailyKWh: dailyKWh,
        dailyCost: dailyCost,
        deltaPercent: deltaPercent,
        equipmentRisk: equipmentRisk,
        riskLevel: riskLevel,
        recommendations: recommendations
      };
    }

    // AI Chatbot Contextual Query Engine (works client-side & connects to backend /api/chatbot)
    async answerQuestion(query) {
      if (this.backendAvailable) {
        try {
          const res = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
          });
          if (res.ok) {
            const data = await res.json();
            return data.reply;
          }
        } catch (e) {
          console.warn("Backend chat failed, falling back to local reasoning:", e);
        }
      }

      const q = query.toLowerCase();
      const state = this.state;

      if (q.includes("floor 2") || q.includes("second floor")) {
        const f2 = state.floors.find(f => f.id === 2);
        return `**Floor 2 (Offices & R&D)** is currently using **${f2.energyKW} kW** with **${f2.occupancy} people inside** (${Math.round((f2.occupancy/f2.maxCapacity)*100)}% full). Average temperature is **${f2.avgTemp}°C**. Note: Server Room 203 is slightly warm at 27.9°C.`;
      }

      if (q.includes("floor 1") || q.includes("first floor")) {
        const f1 = state.floors.find(f => f.id === 1);
        return `**Floor 1 (Lobby & Cafeteria)** is using **${f1.energyKW} kW** with **${f1.occupancy} people inside**. All 4 rooms are running normally with an average temperature of **${f1.avgTemp}°C**.`;
      }

      if (q.includes("floor 3") || q.includes("third floor")) {
        const f3 = state.floors.find(f => f.id === 3);
        return `**Floor 3 (Executive Level)** is using **${f3.energyKW} kW** with **${f3.occupancy} people inside**. Room 303 is set to power saving mode.`;
      }

      if (q.includes("maintenance") || q.includes("equipment")) {
        const atRisk = state.equipment.filter(e => e.status.includes("Maintenance") || e.riskPercent > 50);
        if (atRisk.length > 0) {
          const list = atRisk.map(e => `• **${e.name}** (Breakdown Risk: ${e.riskPercent}%, Health: ${e.health}%, Temp: ${e.tempC}°C)`).join("\n");
          return `Based on AI checks, **${atRisk.length} machines need service soon**:\n\n${list}\n\nServicing them now will prevent unexpected machine breakdowns.`;
        }
        return `All ${state.equipment.length} machines are working in good condition!`;
      }

      if (q.includes("which floor") && (q.includes("most") || q.includes("highest"))) {
        const sortedFloors = [...state.floors].sort((a,b) => b.energyKW - a.energyKW);
        const top = sortedFloors[0];
        return `**${top.name}** is currently using the most electricity at **${top.energyKW} kW** (about ${Math.round((top.energyKW / state.metrics.totalEnergyKW) * 100)}% of total building power), mainly due to computer servers and air conditioning.`;
      }

      if (q.includes("anomaly") || q.includes("anomalies")) {
        const critAlerts = state.alerts.filter(a => a.status === 'active');
        return `The AI has found **${critAlerts.length} active warnings**:\n\n` +
          critAlerts.map(a => `• **[${a.type}] ${a.title}** in ${a.entity}: ${a.description}`).join('\n\n');
      }

      if (q.includes("occupancy") || q.includes("people")) {
        const pct = Math.round((state.metrics.currentOccupancy / state.metrics.maxCapacity) * 100);
        return `Total people in the building: **${state.metrics.currentOccupancy} people** out of ${state.metrics.maxCapacity} maximum spots (**${pct}% full**). The busiest time is usually around 2:00 PM.`;
      }

      if (q.includes("health score") || q.includes("building score")) {
        return `The Building Health Score is currently **${state.metrics.overallHealthScore}/100 (Good)**. This AI score considers machine condition, temperature comfort, and system warnings.`;
      }

      if (q.includes("why is energy") || q.includes("high energy") || q.includes("reduce")) {
        return `**AI Tips to Reduce Electricity:**\n1. **Secondary Chiller 2** is running at high speed because Floor 2 is warm.\n2. Server room cooling is drawing 42.8 kW.\n3. **Recommended Actions:**\n   - Raise thermostat temperature on Floor 3 by 1.5°C.\n   - Turn off ventilation fans in empty rooms.\n   - Service Chiller 2 to lower its electricity draw by ~8.5%.`;
      }

      return `Hello! I am your **AI Building Assistant**. I am monitoring **${state.meta.buildingName}**. You can ask me questions about electricity used by floor, machines that need service, active warnings, people count, or ways to save electricity.`;
    }
  }

  // Global Singleton
  window.SmartBuildingStore = new BuildingDataStore();
})();
