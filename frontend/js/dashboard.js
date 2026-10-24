/**
 * Smart Building Monitoring System - Dashboard Controller
 * Updates KPI cards, renders Chart.js visualizations, reacts to telemetry ticks.
 */

(function () {
  let energyOccupancyChartInstance = null;
  let floorDistributionChartInstance = null;
  let currentChartRange = '24h';

  document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    renderDashboardUI();

    // Listen for simulation state updates
    window.addEventListener('smartbuilding:update', () => {
      renderDashboardUI();
      updateChartsRealtime();
    });
  });

  function renderDashboardUI() {
    const store = window.SmartBuildingStore;
    if (!store || !store.state) return;
    const state = store.state;

    // 1. KPI Cards
    const elTotalEnergy = document.getElementById('kpi-total-energy');
    const elAccumKwh = document.getElementById('kpi-accumulated-kwh');
    const elOccupancy = document.getElementById('kpi-occupancy');
    const elAvgTemp = document.getElementById('kpi-avg-temp');
    const elEnergyCost = document.getElementById('kpi-energy-cost');
    const elEquipHealth = document.getElementById('kpi-equip-health');
    const elAlertsCount = document.getElementById('kpi-alerts-count');
    const elHealthScore = document.getElementById('kpi-health-score');
    const elHealthBadge = document.getElementById('kpi-health-badge');
    const elHealthRing = document.getElementById('dash-health-ring');
    if (elTotalEnergy) elTotalEnergy.innerHTML = `${state.metrics.totalEnergyKW.toFixed(1)} <small>kW</small>`;
    if (elOccupancy) elOccupancy.innerHTML = `${state.metrics.currentOccupancy} <small>/ ${state.metrics.maxCapacity} max</small>`;
    if (elAvgTemp) elAvgTemp.innerHTML = `${state.metrics.avgTemperature.toFixed(1)} <small>°C</small>`;
    if (elEnergyCost) elEnergyCost.textContent = `₹${Math.round(state.metrics.estimatedDailyCost).toLocaleString('en-IN')}`;
    
    // Equipment health
    if (elEquipHealth) elEquipHealth.innerHTML = `${state.metrics.equipmentHealthAvg}% <small>Avg</small>`;

    // Alerts count
    const activeAlerts = state.alerts.filter(a => a.status === 'active');
    if (elAlertsCount) elAlertsCount.innerHTML = `${activeAlerts.length} <small>Active</small>`;

    // Building health score
    const score = state.metrics.overallHealthScore;
    if (elHealthScore) elHealthScore.innerHTML = `${score} <small>/ 100</small>`;
  }

  function renderFloorsSnapshot(floors) {
    const container = document.getElementById('dashboard-floors-list');
    if (!container) return;

    container.innerHTML = floors.map(floor => {
      const roomPills = floor.rooms.map(room => {
        let statusClass = 'status-green';
        let icon = 'fa-check';
        if (room.status === 'yellow') {
          statusClass = 'status-yellow';
          icon = 'fa-triangle-exclamation';
        } else if (room.status === 'red') {
          statusClass = 'status-red';
          icon = 'fa-circle-exclamation';
        }

        return `
          <div class="room-node ${statusClass}" title="${room.name}: ${room.temp}°C, ${room.powerKW} kW, ${room.occupancy}/${room.capacity} occ" style="padding: 0.5rem 0.65rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.78rem;">
              <strong style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;">${room.name}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); margin-top: 3px;">
              <span>${room.occupancy} occ</span>
              <span style="color: var(--accent-cyan); font-weight: 600;">${room.powerKW} kW</span>
            </div>
          </div>
        `;
      }).join('');

      return `
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 0.85rem;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span style="font-weight: 700; font-size: 0.88rem; color: var(--text-primary);">${floor.name}</span>
              <span class="badge ${floor.status === 'normal' ? 'badge-normal' : 'badge-warning'}">${floor.status}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">
              <strong>${floor.energyKW} kW</strong> • <strong>${floor.occupancy}</strong> / ${floor.maxCapacity} people • <strong>${floor.avgTemp}°C</strong>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem;">
            ${roomPills}
          </div>
        </div>
      `;
    }).join('');
  }

  function renderEquipmentTable(equipment) {
    const tbody = document.getElementById('dashboard-equipment-tbody');
    if (!tbody) return;

    // Show top 5 sorted by risk
    const sorted = [...equipment].sort((a,b) => b.riskPercent - a.riskPercent).slice(0, 5);

    tbody.innerHTML = sorted.map(eq => {
      const isRisk = eq.riskPercent > 50;
      const badgeClass = isRisk ? 'badge-critical' : 'badge-normal';
      return `
        <tr>
          <td><strong>${eq.name}</strong></td>
          <td><span style="color: var(--text-muted);">${eq.category}</span></td>
          <td>${eq.tempC}°C</td>
          <td>${eq.health}%</td>
          <td>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <div style="width: 50px; background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; overflow: hidden;">
                <div style="width: ${eq.riskPercent}%; height: 100%; background: ${isRisk ? 'var(--status-critical)' : 'var(--status-normal)'};"></div>
              </div>
              <span style="font-weight: 700; font-size: 0.78rem; color: ${isRisk ? 'var(--status-critical)' : 'var(--text-secondary)'};">${eq.riskPercent}%</span>
            </div>
          </td>
          <td><span class="badge ${badgeClass}">${eq.status}</span></td>
        </tr>
      `;
    }).join('');
  }

  function renderRecommendations(recommendations) {
    const container = document.getElementById('dashboard-recommendations');
    if (!container) return;

    container.innerHTML = recommendations.map(rec => {
      let badge = 'badge-info';
      if (rec.priority === 'HIGH') badge = 'badge-critical';
      if (rec.priority === 'MEDIUM') badge = 'badge-warning';

      return `
        <div style="padding: 0.85rem; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-color); border-radius: var(--radius-sm); display: flex; flex-direction: column; gap: 0.35rem;">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <strong style="font-size: 0.85rem; color: var(--text-primary);">${rec.title}</strong>
            <span class="badge ${badge}">${rec.priority}</span>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-secondary); margin: 0;">${rec.impact}</p>
          <div style="margin-top: 0.25rem;">
            <button class="btn btn-secondary btn-sm" onclick="alert('Action Dispatched: ${rec.action}')" style="padding: 0.2rem 0.6rem; font-size: 0.72rem;">
              ${rec.action}
            </button>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderRecentAlerts(alerts) {
    const container = document.getElementById('dashboard-recent-alerts');
    if (!container) return;

    const active = alerts.slice(0, 3);
    container.innerHTML = active.map(a => {
      const isCrit = a.type === 'CRITICAL';
      const badgeClass = isCrit ? 'badge-critical' : (a.type === 'WARNING' ? 'badge-warning' : 'badge-info');

      return `
        <div style="padding: 0.85rem; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-color); border-radius: var(--radius-sm); display: flex; flex-direction: column; gap: 0.35rem;">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span class="badge ${badgeClass}">${a.type}</span>
              <strong style="font-size: 0.85rem;">${a.title}</strong>
            </div>
            <small style="color: var(--text-muted); font-size: 0.7rem;">${a.entity}</small>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-secondary); margin: 0;">${a.description}</p>
        </div>
      `;
    }).join('');
  }

  function renderFloorLegend(floors, totalKW) {
    const container = document.getElementById('floor-breakdown-legend');
    if (!container) return;

    const colors = ['#00e5ff', '#3b82f6', '#8b5cf6'];
    container.innerHTML = floors.map((f, idx) => {
      const pct = Math.round((f.energyKW / (totalKW || 1)) * 100);
      return `
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: ${colors[idx % colors.length]}; display: inline-block;"></span>
            <span>${f.name}</span>
          </div>
          <strong>${f.energyKW} kW (${pct}%)</strong>
        </div>
      `;
    }).join('');
  }

  function initCharts() {
    const store = window.SmartBuildingStore;
    if (!store || !store.state) return;
    const history = store.state.history24h;

    // 1. Energy vs Occupancy Chart
    const ctx1 = document.getElementById('energyOccupancyChart');
    if (ctx1) {
      const labels = history.map(h => h.label);
      const energyData = history.map(h => h.energyKW);
      const occData = history.map(h => h.occupancy);

      energyOccupancyChartInstance = new Chart(ctx1, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Electricity Used (kW)',
              data: energyData,
              borderColor: '#00e5ff',
              backgroundColor: 'rgba(0, 229, 255, 0.12)',
              borderWidth: 2.5,
              tension: 0.35,
              fill: true,
              yAxisID: 'y'
            },
            {
              label: 'People Inside',
              data: occData,
              borderColor: '#8b5cf6',
              backgroundColor: 'rgba(139, 92, 246, 0.08)',
              borderWidth: 2,
              borderDash: [4, 4],
              tension: 0.35,
              fill: true,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          scales: {
            x: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8', font: { size: 11 } }
            },
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#00e5ff', font: { size: 11 } },
              title: { display: true, text: 'Power (kW)', color: '#00e5ff' }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              grid: { drawOnChartArea: false },
              ticks: { color: '#8b5cf6', font: { size: 11 } },
              title: { display: true, text: 'People', color: '#8b5cf6' }
            }
          },
          plugins: {
            legend: {
              labels: { color: '#f8fafc', font: { size: 12, family: 'Inter' } }
            }
          }
        }
      });
    }

    // 2. Floor Distribution Doughnut Chart
    const ctx2 = document.getElementById('floorDistributionChart');
    if (ctx2) {
      const floors = store.state.floors;
      const labels = floors.map(f => f.name.split(' - ')[0]);
      const data = floors.map(f => f.energyKW);

      floorDistributionChartInstance = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: ['#00e5ff', '#3b82f6', '#8b5cf6'],
            borderColor: '#0f172a',
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          cutout: '72%'
        }
      });
    }
  }

  function updateChartsRealtime() {
    const store = window.SmartBuildingStore;
    if (!store || !store.state) return;

    if (floorDistributionChartInstance) {
      floorDistributionChartInstance.data.datasets[0].data = store.state.floors.map(f => f.energyKW);
      floorDistributionChartInstance.update('none');
    }

    if (energyOccupancyChartInstance && currentChartRange === '24h') {
      // subtly adjust last datapoint to match live total
      const len = energyOccupancyChartInstance.data.datasets[0].data.length;
      if (len > 0) {
        energyOccupancyChartInstance.data.datasets[0].data[len - 1] = store.state.metrics.totalEnergyKW;
        energyOccupancyChartInstance.data.datasets[1].data[len - 1] = store.state.metrics.currentOccupancy;
        energyOccupancyChartInstance.update('none');
      }
    }
  }

  window.switchDashboardChart = function(range) {
    currentChartRange = range;
    const tabs = document.querySelectorAll('.card-header .btn-tab');
    tabs.forEach(t => t.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');

    if (!energyOccupancyChartInstance) return;

    if (range === '24h') {
      const history = window.SmartBuildingStore.state.history24h;
      energyOccupancyChartInstance.data.labels = history.map(h => h.label);
      energyOccupancyChartInstance.data.datasets[0].data = history.map(h => h.energyKW);
      energyOccupancyChartInstance.data.datasets[1].data = history.map(h => h.occupancy);
    } else if (range === '7d') {
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      energyOccupancyChartInstance.data.labels = days;
      energyOccupancyChartInstance.data.datasets[0].data = [245, 260, 275, 268, 280, 140, 120];
      energyOccupancyChartInstance.data.datasets[1].data = [350, 390, 410, 395, 420, 95, 60];
    } else if (range === '30d') {
      const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
      energyOccupancyChartInstance.data.labels = weeks;
      energyOccupancyChartInstance.data.datasets[0].data = [255, 268, 272, 261];
      energyOccupancyChartInstance.data.datasets[1].data = [370, 385, 405, 390];
    }
    energyOccupancyChartInstance.update();
  };

})();
