const API_URL = 'http://127.0.0.1:5000/latest';

let globalDataLog = []; // Stores history for CSV export

// --- SPA NAVIGATION LOGIC ---
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();

        // Remove active class from all navs
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        // Add to clicked
        this.classList.add('active');

        // Hide all views
        document.querySelectorAll('.view-section').forEach(view => view.classList.remove('active'));

        // Show target view
        const targetId = this.getAttribute('data-target');
        document.getElementById(targetId).classList.add('active');

        // Update header dynamically
        const titleMap = {
            'view-dashboard': { title: 'Real-time Analytics', sub: 'Live telemetry from Jellyfish Sensor Node 01' },
            'view-nodes': { title: 'Hardware Nodes', sub: 'Fleet management and network topology' },
            'view-actuation': { title: 'Actuation & Treatments', sub: 'Decision engine outputs and overrides' },
            'view-ai-models': { title: 'AI & Inference Models', sub: 'Cloud-trained statistical matrices running locally' },
            'view-settings': { title: 'System Configuration', sub: 'Environment variables and thresholds' }
        };

        document.getElementById('page-title').innerText = titleMap[targetId].title;
        document.getElementById('page-subtitle').innerText = titleMap[targetId].sub;
    });
});

// --- CSV EXPORT LOGIC ---
document.getElementById('btn-export').addEventListener('click', function () {
    if (globalDataLog.length === 0) {
        alert("No data collected yet to export.");
        return;
    }

    // Create CSV Header
    const headers = ["Timestamp", "pH", "TDS_ppm", "Turbidity_NTU", "Temp_C", "Spike_Prob", "Classification", "Action", "Anomaly"];
    let csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n";

    globalDataLog.forEach(row => {
        const rowData = [
            row.time, row.ph, row.tds, row.turbidity, row.temperature,
            row.spike_probability,
            `"${row.classification}"`, // Wrap in quotes in case of spaces
            `"${row.treatment_action}"`,
            row.anomaly
        ];
        csvContent += rowData.join(",") + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    const dateStr = new Date().toISOString().replace(/:/g, '-').slice(0, 19);
    link.setAttribute("download", `SensiFluid_Telemetry_Export_${dateStr}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// --- CHART THEME ---
Chart.defaults.color = '#a1a1aa';
Chart.defaults.font.family = "'JetBrains Mono', monospace";
Chart.defaults.font.size = 11;

const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.03)', drawBorder: false }, ticks: { maxTicksLimit: 8, padding: 10 } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)', borderDash: [5, 5], drawBorder: false }, ticks: { padding: 10, precision: 1 } }
    },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: 'rgba(24, 24, 27, 0.9)',
            titleFont: { family: "'Outfit', sans-serif", size: 13 },
            bodyFont: { family: "'JetBrains Mono', monospace", size: 12 },
            padding: 12, cornerRadius: 8, borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1
        }
    },
    animation: { duration: 1000, easing: 'easeOutExpo' },
    elements: { line: { tension: 0.4, borderWidth: 3 }, point: { radius: 0, hitRadius: 10, hoverRadius: 6, hoverBorderWidth: 3 } }
};

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
        datasets: [{ label: 'Turbidity (NTU)', data: [], borderColor: '#3b82f6', backgroundColor: turbGradient, pointBackgroundColor: '#09090b', pointBorderColor: '#3b82f6', fill: true }]
    },
    options: commonOptions
});

const tdsCtx = document.getElementById('tdsChart').getContext('2d');
const tdsGradient = createGradient(tdsCtx, 'rgba(16, 185, 129, 0.4)', 'rgba(16, 185, 129, 0.0)');

const tdsChart = new Chart(tdsCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{ label: 'TDS (ppm)', data: [], borderColor: '#10b981', backgroundColor: tdsGradient, pointBackgroundColor: '#09090b', pointBorderColor: '#10b981', fill: true }]
    },
    options: commonOptions
});

const maxDataPoints = 30;

// --- DATA POLLING LOGIC ---
function updateDashboard(data) {
    const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // Log for Export
    let logEntry = { ...data, time: nowStr };
    globalDataLog.push(logEntry);
    if (globalDataLog.length > 500) globalDataLog.shift(); // keep memory sane

    document.getElementById('last-updated').innerText = `Last Sync: ${nowStr}`;

    // Sensor Grid Updates
    document.getElementById('val-ph').innerText = data.ph.toFixed(2);
    document.getElementById('val-tds').innerText = data.tds.toFixed(1);
    document.getElementById('val-turb').innerText = data.turbidity.toFixed(1);
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

    // Treatment Dashboard Card Update
    const treatEl = document.getElementById('treatment-action');
    const userFriendlyActions = {
        "system_off": "System Offline",
        "pump_on": "Pumping Standard Water",
        "uv_led_on": "UV Treatment Active",
        "electrolysis_on": "Electrolysis Active",
        "pump_and_pretreat": "Pre-treatment Active"
    };
    treatEl.innerText = userFriendlyActions[data.treatment_action] || data.treatment_action;
    treatEl.className = (data.treatment_action !== "system_off") ? 'status-reading highlight' : 'status-reading';
    if (data.treatment_action === "system_off") treatEl.style.color = 'var(--text-secondary)';

    // --- Updates to Actuation Tab Checkboxes ---
    document.getElementById('chk-pump').checked = (data.treatment_action === "pump_on" || data.treatment_action === "pump_and_pretreat");
    document.getElementById('chk-uv').checked = (data.treatment_action === "uv_led_on");
    document.getElementById('chk-elec').checked = (data.treatment_action === "electrolysis_on");
    document.getElementById('chk-pre').checked = (data.treatment_action === "pump_and_pretreat");

    // Spike Prediction Update
    const prob = (data.spike_probability * 100).toFixed(1);
    const probEl = document.getElementById('spike-prob');
    probEl.innerText = `${prob}%`;
    probEl.className = 'status-reading ' + (prob > 50 ? 'danger' : 'normal');

    // Chart Appends
    turbidityChart.data.labels.push(nowStr);
    turbidityChart.data.datasets[0].data.push(data.turbidity);
    if (turbidityChart.data.labels.length > maxDataPoints) {
        turbidityChart.data.labels.shift();
        turbidityChart.data.datasets[0].data.shift();
    }
    turbidityChart.update();

    tdsChart.data.labels.push(nowStr);
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
        } else {
            document.getElementById('global-status-text').innerText = "System Offline - API Error";
            document.querySelector('.pulse-indicator').style.backgroundColor = "var(--accent-red)";
            document.querySelector('.pulse-indicator').style.boxShadow = "none";
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        document.getElementById('global-status-text').innerText = "System Offline - Backend Down";
        document.querySelector('.pulse-indicator').style.backgroundColor = "var(--accent-red)";
        document.querySelector('.pulse-indicator').style.animation = "none";
    }
}

// Initial fetch and set interval loop
fetchData();
setInterval(fetchData, 2000);
