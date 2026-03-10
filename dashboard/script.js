const API_URL = 'http://127.0.0.1:5000/latest';
const API_BASE = 'http://127.0.0.1:5000';

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

// --- CONTINUOUS LEARNING / FEEDBACK LOGIC ---
document.getElementById('btn-submit-feedback').addEventListener('click', async () => {
    if (globalDataLog.length === 0) return alert("System hasn't recorded any data yet to verify!");
    const currentData = globalDataLog[globalDataLog.length - 1];
    const lbl = document.getElementById('sel-feedback').value;

    const payload = {
        ph: currentData.ph,
        tds: currentData.tds,
        turbidity: currentData.turbidity,
        temperature: currentData.temperature,
        label: parseInt(lbl)
    };

    try {
        const res = await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) alert("Hit verified and saved to the persistent continuous learning buffer!");
        else alert("Failed to save feedback.");
    } catch (e) { console.error(e); }
});

document.getElementById('btn-trigger-retrain').addEventListener('click', async () => {
    const btn = document.getElementById('btn-trigger-retrain');
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Retraining...';
    try {
        const res = await fetch(`${API_BASE}/retrain`, { method: 'POST' });
        if (res.ok) alert("Neural Nets and ML Classifiers successfully hot-swapped!");
        else alert("Failed to retrain models.");
    } catch (e) { console.error(e); }
    btn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Retrain Models';
});

// --- CHART THEME ---
Chart.defaults.color = '#a1a1aa';
Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
Chart.defaults.font.size = 11;

const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.02)', drawBorder: false }, ticks: { maxTicksLimit: 8, padding: 10 } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.04)', borderDash: [4, 4], drawBorder: false }, ticks: { padding: 10, precision: 1 } }
    },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: 'rgba(24, 24, 27, 0.95)',
            titleFont: { family: "'Inter', sans-serif", size: 13, weight: '600' },
            bodyFont: { family: "'Inter', sans-serif", size: 12 },
            padding: 12, cornerRadius: 6, borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1
        }
    },
    animation: { duration: 1000, easing: 'easeOutExpo' },
    elements: { line: { tension: 0.2, borderWidth: 1.5 }, point: { radius: 0, hitRadius: 10, hoverRadius: 4, hoverBorderWidth: 2 } }
};

function createGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
}

const turbidityCtx = document.getElementById('turbidityChart').getContext('2d');
const turbGradient = createGradient(turbidityCtx, 'rgba(37, 99, 235, 0.15)', 'rgba(37, 99, 235, 0.0)');

const turbidityChart = new Chart(turbidityCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{ label: 'Turbidity (NTU)', data: [], borderColor: '#2563eb', backgroundColor: turbGradient, pointBackgroundColor: '#111113', pointBorderColor: '#2563eb', fill: true }]
    },
    options: commonOptions
});

const tdsCtx = document.getElementById('tdsChart').getContext('2d');
const tdsGradient = createGradient(tdsCtx, 'rgba(5, 150, 105, 0.15)', 'rgba(5, 150, 105, 0.0)');

const tdsChart = new Chart(tdsCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{ label: 'TDS (ppm)', data: [], borderColor: '#059669', backgroundColor: tdsGradient, pointBackgroundColor: '#111113', pointBorderColor: '#059669', fill: true }]
    },
    options: commonOptions
});

const phCtx = document.getElementById('phChart').getContext('2d');
const phGradient = createGradient(phCtx, 'rgba(79, 70, 229, 0.15)', 'rgba(79, 70, 229, 0.0)');
const phChart = new Chart(phCtx, {
    type: 'line', data: { labels: [], datasets: [{ label: 'pH Level', data: [], borderColor: '#4f46e5', backgroundColor: phGradient, pointBackgroundColor: '#111113', pointBorderColor: '#4f46e5', fill: true }] }, options: commonOptions
});

const tempCtx = document.getElementById('tempChart').getContext('2d');
const tempGradient = createGradient(tempCtx, 'rgba(220, 38, 38, 0.15)', 'rgba(220, 38, 38, 0.0)');
const tempChart = new Chart(tempCtx, {
    type: 'line', data: { labels: [], datasets: [{ label: 'Temperature (°C)', data: [], borderColor: '#dc2626', backgroundColor: tempGradient, pointBackgroundColor: '#111113', pointBorderColor: '#dc2626', fill: true }] }, options: commonOptions
});

const spikeCtx = document.getElementById('spikeChart').getContext('2d');
const spikeGradient = createGradient(spikeCtx, 'rgba(217, 119, 6, 0.15)', 'rgba(217, 119, 6, 0.0)');
const spikeChart = new Chart(spikeCtx, {
    type: 'line', data: { labels: [], datasets: [{ label: 'Spike Risk (%)', data: [], borderColor: '#d97706', backgroundColor: spikeGradient, pointBackgroundColor: '#111113', pointBorderColor: '#d97706', fill: true }] }, options: commonOptions
});

const pieCtx = document.getElementById('classPieChart').getContext('2d');
let classCounts = [0, 0, 0, 0];
const classPieChart = new Chart(pieCtx, {
    type: 'doughnut',
    data: {
        labels: ['Normal Water', 'Packaging Residue', 'Antibiotic Contamination', 'Anomaly'],
        datasets: [{
            data: classCounts,
            backgroundColor: ['#059669', '#d97706', '#4f46e5', '#dc2626'],
            borderWidth: 0,
            hoverOffset: 4
        }]
    },
    options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(24, 24, 27, 0.95)' } },
        cutout: '75%'
    }
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
    if (turbidityChart.data.labels.length > maxDataPoints) { turbidityChart.data.labels.shift(); turbidityChart.data.datasets[0].data.shift(); }
    turbidityChart.update();

    tdsChart.data.labels.push(nowStr);
    tdsChart.data.datasets[0].data.push(data.tds);
    if (tdsChart.data.labels.length > maxDataPoints) { tdsChart.data.labels.shift(); tdsChart.data.datasets[0].data.shift(); }
    tdsChart.update();

    phChart.data.labels.push(nowStr);
    phChart.data.datasets[0].data.push(data.ph);
    if (phChart.data.labels.length > maxDataPoints) { phChart.data.labels.shift(); phChart.data.datasets[0].data.shift(); }
    phChart.update();

    tempChart.data.labels.push(nowStr);
    tempChart.data.datasets[0].data.push(data.temperature);
    if (tempChart.data.labels.length > maxDataPoints) { tempChart.data.labels.shift(); tempChart.data.datasets[0].data.shift(); }
    tempChart.update();

    spikeChart.data.labels.push(nowStr);
    spikeChart.data.datasets[0].data.push(prob);
    if (spikeChart.data.labels.length > maxDataPoints) { spikeChart.data.labels.shift(); spikeChart.data.datasets[0].data.shift(); }
    spikeChart.update();

    // Pie Chart Appends
    if (data.classification !== "Waiting for data...") {
        let idx = 0;
        if (data.anomaly) idx = 3;
        else if (data.classification === 'Normal Water') idx = 0;
        else if (data.classification === 'Packaging Residue') idx = 1;
        else idx = 2;
        classCounts[idx]++;
        classPieChart.update();
    }
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

// --- STARTUP LOADER LOGIC ---
window.addEventListener('load', () => {
    // Give a 1.25 second artificial delay for the classy animation to play before hiding
    setTimeout(() => {
        const loader = document.getElementById('startup-loader');
        if (loader) loader.classList.add('loader-hidden');
    }, 1250);
});
