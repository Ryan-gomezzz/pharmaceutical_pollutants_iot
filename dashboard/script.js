const API_URL = 'http://127.0.0.1:5000/latest';

// Modern Chart.js Theming
Chart.defaults.color = '#a1a1aa';
Chart.defaults.font.family = "'JetBrains Mono', monospace";
Chart.defaults.font.size = 11;

const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        mode: 'index',
        intersect: false,
    },
    scales: {
        x: {
            grid: { color: 'rgba(255, 255, 255, 0.03)', drawBorder: false },
            ticks: { maxTicksLimit: 8, padding: 10 }
        },
        y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)', borderDash: [5, 5], drawBorder: false },
            ticks: { padding: 10, precision: 1 }
        }
    },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: 'rgba(24, 24, 27, 0.9)',
            titleFont: { family: "'Outfit', sans-serif", size: 13 },
            bodyFont: { family: "'JetBrains Mono', monospace", size: 12 },
            padding: 12,
            cornerRadius: 8,
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1
        }
    },
    animation: { duration: 1000, easing: 'easeOutExpo' },
    elements: {
        line: { tension: 0.4, borderWidth: 3 },
        point: { radius: 0, hitRadius: 10, hoverRadius: 6, hoverBorderWidth: 3 }
    }
};

// Create Gradients
function createGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
}

const turbidityCtx = document.getElementById('turbidityChart').getContext('2d');
const turbGradient = createGradient(turbidityCtx, 'rgba(59, 130, 246, 0.4)', 'rgba(59, 130, 246, 0.0)');

const turbidityChart = new Chart(turbidityCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Turbidity (NTU)',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: turbGradient,
            pointBackgroundColor: '#09090b',
            pointBorderColor: '#3b82f6',
            fill: true
        }]
    },
    options: commonOptions
});

const tdsCtx = document.getElementById('tdsChart').getContext('2d');
const tdsGradient = createGradient(tdsCtx, 'rgba(16, 185, 129, 0.4)', 'rgba(16, 185, 129, 0.0)');

const tdsChart = new Chart(tdsCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'TDS (ppm)',
            data: [],
            borderColor: '#10b981',
            backgroundColor: tdsGradient,
            pointBackgroundColor: '#09090b',
            pointBorderColor: '#10b981',
            fill: true
        }]
    },
    options: commonOptions
});

const maxDataPoints = 30;

function updateDashboard(data) {
    // Top Right Header Time
    document.getElementById('last-updated').innerText = `Last Sync: ${new Date().toLocaleTimeString()}`;

    // Sensor Grid Updates
    document.getElementById('val-ph').innerText = data.ph.toFixed(2);
    document.getElementById('val-tds').innerText = data.tds.toFixed(1);
    document.getElementById('val-turb').innerText = data.turbidity.toFixed(1);
    document.getElementById('val-orp').innerText = data.orp.toFixed(1);
    document.getElementById('val-temp').innerText = data.temperature.toFixed(1);

    // Classification Update
    const classEl = document.getElementById('ai-classification');
    const subEl = document.getElementById('ai-subtitle');

    if (data.anomaly) {
        classEl.innerText = "System Anomaly";
        classEl.className = 'status-reading danger blink';
        subEl.innerText = "Hardware Fault / Extreme Out-of-bounds";
    } else {
        classEl.innerText = data.classification;
        classEl.className = 'status-reading ' + (
            data.classification === 'Normal Water' ? 'normal' :
                data.classification === 'Packaging Residue' ? 'warning' : 'danger'
        );
        subEl.innerText = "Random Forest Classification active";
    }

    // Treatment Update
    const treatEl = document.getElementById('treatment-action');
    const userFriendlyActions = {
        "system_off": "System Offline",
        "pump_on": "Pumping Standard Water",
        "uv_led_on": "UV Treatment Active",
        "electrolysis_on": "Electrolysis Active",
        "pump_and_pretreat": "Pre-treatment Active"
    };
    treatEl.innerText = userFriendlyActions[data.treatment_action] || data.treatment_action;

    // Add glowing effect if active treatment running
    if (data.treatment_action !== "system_off") {
        treatEl.className = 'status-reading highlight';
    } else {
        treatEl.className = 'status-reading';
        treatEl.style.color = 'var(--text-secondary)';
    }

    // Spike Prediction
    const prob = (data.spike_probability * 100).toFixed(1);
    const probEl = document.getElementById('spike-prob');
    probEl.innerText = `${prob}%`;
    probEl.className = 'status-reading ' + (prob > 50 ? 'danger' : 'normal');

    // Chart Appends
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // Turbidity
    turbidityChart.data.labels.push(now);
    turbidityChart.data.datasets[0].data.push(data.turbidity);
    if (turbidityChart.data.labels.length > maxDataPoints) {
        turbidityChart.data.labels.shift();
        turbidityChart.data.datasets[0].data.shift();
    }
    turbidityChart.update();

    // TDS
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

// Initial fetch and set interval loop
fetchData();
setInterval(fetchData, 2000);
