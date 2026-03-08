const API_URL = 'http://127.0.0.1:5000/latest';

Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";

const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { maxTicksLimit: 10 } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    plugins: { legend: { display: false } },
    animation: { duration: 800, easing: 'easeOutQuart' },
    elements: { line: { tension: 0.4 }, point: { radius: 2, hoverRadius: 6 } }
};

const turbidityCtx = document.getElementById('turbidityChart').getContext('2d');
const turbidityChart = new Chart(turbidityCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Turbidity (NTU)', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', fill: true, borderWidth: 2 }] },
    options: commonOptions
});

const tdsCtx = document.getElementById('tdsChart').getContext('2d');
const tdsChart = new Chart(tdsCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'TDS (ppm)', data: [], borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, borderWidth: 2 }] },
    options: commonOptions
});

const maxDataPoints = 30;

function updateDashboard(data) {
    document.getElementById('val-ph').innerText = data.ph.toFixed(2);
    document.getElementById('val-tds').innerText = data.tds.toFixed(1);
    document.getElementById('val-turb').innerText = data.turbidity.toFixed(1);
    document.getElementById('val-orp').innerText = data.orp.toFixed(1);
    document.getElementById('val-temp').innerText = data.temperature.toFixed(1);

    const classEl = document.getElementById('ai-classification');
    const subEl = document.getElementById('ai-subtitle');

    if (data.anomaly) {
        classEl.innerText = "System Anomaly";
        classEl.className = 'status-value danger blink';
        subEl.innerText = "Extreme out-of-bounds metrics";
    } else {
        classEl.innerText = data.classification;
        classEl.className = 'status-value ' + (
            data.classification === 'Normal Water' ? 'normal' :
                data.classification === 'Packaging Residue' ? 'warning' : 'danger'
        );
        subEl.innerText = "Random Forest Classification";
    }

    const treatEl = document.getElementById('treatment-action');
    const userFriendlyActions = {
        "system_off": "System Offline",
        "pump_on": "Pumping Standard Water",
        "uv_led_on": "UV Treatment Active",
        "electrolysis_on": "Electrolysis Active",
        "pump_and_pretreat": "Pre-treatment Active"
    };
    treatEl.innerText = userFriendlyActions[data.treatment_action] || data.treatment_action;

    const prob = (data.spike_probability * 100).toFixed(1);
    const probEl = document.getElementById('spike-prob');
    probEl.innerText = `${prob}%`;
    probEl.style.color = prob > 50 ? 'var(--accent-red)' : 'var(--text-main)';

    const now = new Date().toLocaleTimeString();

    turbidityChart.data.labels.push(now);
    turbidityChart.data.datasets[0].data.push(data.turbidity);
    if (turbidityChart.data.labels.length > maxDataPoints) {
        turbidityChart.data.labels.shift();
        turbidityChart.data.datasets[0].data.shift();
    }
    turbidityChart.update();

    tdsChart.data.labels.push(now);
    tdsChart.data.datasets[0].data.push(data.tds);
    if (tdsChart.data.labels.length > maxDataPoints) {
        tdsChart.data.labels.shift();
        tdsChart.data.datasets[0].data.shift();
    }
    tdsChart.update();
}

async function fetchData() {
    try {
        const response = await fetch(API_URL);
        if (response.ok) {
            const data = await response.json();
            updateDashboard(data);
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

setInterval(fetchData, 2000);
fetchData();
