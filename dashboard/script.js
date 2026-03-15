const API_URL = 'http://127.0.0.1:5000/latest';
const API_BASE = 'http://127.0.0.1:5000';

let globalDataLog = []; // Stores history for CSV export

// Initialize Leaflet Map
let govMap = null;
let mapMarkers = [];
let sourceMarker = null;
let sourceCircle = null;

function initGovMap() {
    if (govMap) return; // already initialized

    // Default center (Bengaluru)
    govMap = L.map('hub-map').setView([12.9716, 77.5946], 12);

    // Add dark theme tile layer (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(govMap);

    // Force a resize calculation shortly after rendering
    setTimeout(() => {
        govMap.invalidateSize();
    }, 500);
}

// Navigation Tab Switching
function switchView(targetId) {
    document.querySelectorAll('.view-section').forEach(view => {
        view.classList.remove('active');
    });
    const target = document.getElementById(targetId);
    if (target) {
        target.classList.add('active');
        if (targetId === 'view-gov') {
            initGovMap();
        }
    }

    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-target') === targetId) {
            btn.classList.add('active');
        }
    });

    // Update active icon color
    document.querySelectorAll('.nav-item').forEach(btn => {
        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.remove('text-blue');
            if (btn.classList.contains('active')) icon.classList.add('text-blue');
        }
    });

    // Update header dynamically
    const titleMap = {
        'view-dashboard': { title: 'Real-time Analytics', sub: 'Live telemetry from Jellyfish Sensor Node 01' },
        'view-nodes': { title: 'Hardware Nodes', sub: 'Fleet management and network topology' },
        'view-actuation': { title: 'Actuation & Treatments', sub: 'Decision engine outputs and overrides' },
        'view-ai-models': { title: 'AI & Inference Models', sub: 'Cloud-trained statistical matrices running locally' },
        'view-settings': { title: 'System Configuration', sub: 'Environment variables and thresholds' },
        'view-gov': { title: 'Gov Coordination', sub: 'Regional contamination monitoring and response' }
    };

    document.getElementById('page-title').innerText = titleMap[targetId].title;
    document.getElementById('page-subtitle').innerText = titleMap[targetId].sub;
}

// --- SPA NAVIGATION LOGIC ---
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('data-target');
        switchView(targetId);
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
    link.setAttribute("download", `PokeLab_Telemetry_Export_${dateStr}.csv`);
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

const retrainBtn = document.getElementById('btn-trigger-retrain');
if (retrainBtn) {
    retrainBtn.addEventListener('click', async () => {
        retrainBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Retraining...';
        try {
            const res = await fetch(`${API_BASE}/retrain`, { method: 'POST' });
            if (res.ok) alert("Neural Nets and ML Classifiers successfully hot-swapped!");
            else alert("Failed to retrain models.");
        } catch (e) { console.error(e); }
        retrainBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Retrain Models';
    });
}

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
    elements: { line: { tension: 0.45, borderWidth: 2 }, point: { radius: 0, hitRadius: 10, hoverRadius: 4, hoverBorderWidth: 2 } }
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
    options: { ...commonOptions, scales: { ...commonOptions.scales, y: { ...commonOptions.scales.y, min: 0, max: 100 } } }
});

const tdsCtx = document.getElementById('tdsChart').getContext('2d');
const tdsGradient = createGradient(tdsCtx, 'rgba(5, 150, 105, 0.15)', 'rgba(5, 150, 105, 0.0)');

const tdsChart = new Chart(tdsCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{ label: 'TDS (ppm)', data: [], borderColor: '#059669', backgroundColor: tdsGradient, pointBackgroundColor: '#111113', pointBorderColor: '#059669', fill: true }]
    },
    options: { ...commonOptions, scales: { ...commonOptions.scales, y: { ...commonOptions.scales.y, min: 0, max: 800 } } }
});

const phCtx = document.getElementById('phChart').getContext('2d');
const phGradient = createGradient(phCtx, 'rgba(79, 70, 229, 0.15)', 'rgba(79, 70, 229, 0.0)');
const phChart = new Chart(phCtx, {
    type: 'line', data: { labels: [], datasets: [{ label: 'pH Level', data: [], borderColor: '#4f46e5', backgroundColor: phGradient, pointBackgroundColor: '#111113', pointBorderColor: '#4f46e5', fill: true }] },
    options: { ...commonOptions, scales: { ...commonOptions.scales, y: { ...commonOptions.scales.y, min: 0, max: 14 } } }
});

const tempCtx = document.getElementById('tempChart').getContext('2d');
const tempGradient = createGradient(tempCtx, 'rgba(220, 38, 38, 0.15)', 'rgba(220, 38, 38, 0.0)');
const tempChart = new Chart(tempCtx, {
    type: 'line', data: { labels: [], datasets: [{ label: 'Temperature (°C)', data: [], borderColor: '#dc2626', backgroundColor: tempGradient, pointBackgroundColor: '#111113', pointBorderColor: '#dc2626', fill: true }] },
    options: { ...commonOptions, scales: { ...commonOptions.scales, y: { ...commonOptions.scales.y, min: 10, max: 50 } } }
});

const spikeCtx = document.getElementById('spikeChart').getContext('2d');
const spikeGradient = createGradient(spikeCtx, 'rgba(217, 119, 6, 0.15)', 'rgba(217, 119, 6, 0.0)');
const spikeChart = new Chart(spikeCtx, {
    type: 'line', data: { labels: [], datasets: [{ label: 'Spike Risk (%)', data: [], borderColor: '#d97706', backgroundColor: spikeGradient, pointBackgroundColor: '#111113', pointBorderColor: '#d97706', fill: true }] },
    options: { ...commonOptions, scales: { ...commonOptions.scales, y: { ...commonOptions.scales.y, min: 0, max: 100 } } }
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

// --- BASELINE DATASETS ---
// We add baseline datasets to the existing charts to show the reference levels.
function addBaselineDataset(chart, label, color) {
    chart.data.datasets.push({
        label: `${label} Baseline`,
        data: [],
        borderColor: color,
        borderDash: [5, 5],
        borderWidth: 1.5,
        pointRadius: 0,
        fill: false,
        order: 1
    });
}

addBaselineDataset(turbidityChart, 'Turbidity', 'rgba(37, 99, 235, 0.6)');
addBaselineDataset(tdsChart, 'TDS', 'rgba(5, 150, 105, 0.6)');
addBaselineDataset(phChart, 'pH', 'rgba(79, 70, 229, 0.6)');
addBaselineDataset(tempChart, 'Temp', 'rgba(220, 38, 38, 0.6)');

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

    // --- Updates to Actuation Tab Checkboxes (only in auto mode) ---
    const isManualOverride = data.manual_override === true;
    const overrideBanner = document.getElementById('override-banner');
    const overrideBannerText = document.getElementById('override-banner-text');

    if (isManualOverride) {
        overrideBanner.style.display = 'flex';
        const cmdLabels = { pump_on: 'Standard Pump', uv_led_on: 'UV LED Module', electrolysis_on: 'Electrolysis Electrode', pump_and_pretreat: 'Heavy Pre-treatment' };
        overrideBannerText.innerText = `Manual Override Active → ${cmdLabels[data.override_command] || data.override_command}`;
        // Set checkboxes to match the override command
        document.getElementById('chk-pump').checked = (data.override_command === 'pump_on');
        document.getElementById('chk-uv').checked = (data.override_command === 'uv_led_on');
        document.getElementById('chk-elec').checked = (data.override_command === 'electrolysis_on');
        document.getElementById('chk-pre').checked = (data.override_command === 'pump_and_pretreat');
    } else {
        overrideBanner.style.display = 'none';
        document.getElementById('chk-pump').checked = (data.treatment_action === 'pump_on' || data.treatment_action === 'pump_and_pretreat');
        document.getElementById('chk-uv').checked = (data.treatment_action === 'uv_led_on');
        document.getElementById('chk-elec').checked = (data.treatment_action === 'electrolysis_on');
        document.getElementById('chk-pre').checked = (data.treatment_action === 'pump_and_pretreat');
    }

    // Spike Prediction Update
    const prob = (data.spike_probability * 100).toFixed(1);
    const probEl = document.getElementById('spike-prob');
    probEl.innerText = `${prob}%`;
    probEl.className = 'status-reading ' + (prob > 50 ? 'danger' : 'normal');

    // Contamination Alert Update (Upgrade 4)
    const alertEl = document.getElementById('contamination-alert');
    if (data.contamination_alert) {
        alertEl.style.display = 'flex';
    } else {
        alertEl.style.display = 'none';
    }

    // Baseline & Progress Update (Upgrade 1)
    if (data.calibration_progress !== -1) {
        document.getElementById('calibration-status').style.display = 'none';
        document.getElementById('calibration-progress-container').style.display = 'block';
        const progress = (data.calibration_progress / 20) * 100;
        document.getElementById('calibration-progress-bar').style.width = `${progress}%`;
        document.getElementById('calibration-step-text').innerText = `Collecting sample ${data.calibration_progress}/20...`;
    } else {
        document.getElementById('calibration-status').style.display = 'block';
        document.getElementById('calibration-progress-container').style.display = 'none';
    }

    if (data.baseline && data.baseline.ph !== null) {
        document.getElementById('base-ph').innerText = data.baseline.ph.toFixed(2);
        document.getElementById('base-tds').innerText = data.baseline.tds.toFixed(1);
        document.getElementById('base-turb').innerText = data.baseline.turbidity.toFixed(1);
        document.getElementById('base-temp').innerText = data.baseline.temperature.toFixed(1);
        document.getElementById('baseline-status-text').innerText = "Calibrated";
        document.getElementById('baseline-status-text').className = "text-indigo";
    }

    // Chart Appends
    const updateChartData = (chart, value, baseline) => {
        chart.data.labels.push(nowStr);
        chart.data.datasets[0].data.push(value);
        if (baseline !== null && baseline !== undefined) {
            chart.data.datasets[1].data.push(baseline);
        } else {
            chart.data.datasets[1].data.push(null);
        }

        if (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }
        chart.update();
    };

    updateChartData(turbidityChart, data.turbidity, data.baseline ? data.baseline.turbidity : null);
    updateChartData(tdsChart, data.tds, data.baseline ? data.baseline.tds : null);
    updateChartData(phChart, data.ph, data.baseline ? data.baseline.ph : null);
    updateChartData(tempChart, data.temperature, data.baseline ? data.baseline.temperature : null);

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

function updateConnectionUI(nodeType, isOnline, data) {
    const statusEl = document.getElementById(`status-${nodeType}-node`);
    const ipEl = document.getElementById(`ip-${nodeType}-node`);
    const readsEl = document.getElementById(`reads-${nodeType}-node`);

    if (statusEl) {
        statusEl.innerHTML = isOnline
            ? '<span class="badge badge-green"><i class="fa-solid fa-circle-check"></i> Active</span>'
            : '<span class="badge badge-red"><i class="fa-solid fa-circle-xmark"></i> Offline</span>';
    }
    if (ipEl) ipEl.innerText = isOnline ? data.ip : '-';
    if (readsEl) readsEl.innerText = isOnline ? data.readings + ' reqs' : '-';
}

async function fetchNodeStatus() {
    try {
        const response = await fetch(`${API_BASE}/node-status`);
        if (response.ok) {
            const statusData = await response.json();
            updateConnectionUI('sensor', statusData.sensor_node.online, statusData.sensor_node);
            updateConnectionUI('actuator', statusData.actuator_node.online, statusData.actuator_node);

            // Poll Gov Status
            const govRes = await fetch(`${API_BASE}/gov-status`);
            const govData = await govRes.json();
            updateGovCoordination(govData);

        } else {
            // API error, mark all nodes offline
            updateConnectionUI('sensor', false, {});
            updateConnectionUI('actuator', false, {});
        }
    } catch (e) {
        // Backend down, marking nodes offline
        updateConnectionUI('sensor', false, {});
        updateConnectionUI('actuator', false, {});
        console.error('Fetch error:', e);
    }
}

// Initial fetch and set interval loop
fetchData();
fetchNodeStatus();
setInterval(() => {
    fetchData();
    fetchNodeStatus();
}, 2000);

// --- MANUAL OVERRIDE TOGGLE LOGIC ---
const overrideToggles = ['chk-pump', 'chk-uv', 'chk-elec', 'chk-pre'];

overrideToggles.forEach(id => {
    document.getElementById(id).addEventListener('change', async function () {
        const command = this.dataset.command;

        if (this.checked) {
            // Uncheck all other toggles (radio-style: only one active at a time)
            overrideToggles.forEach(otherId => {
                if (otherId !== id) document.getElementById(otherId).checked = false;
            });

            // Send manual override command
            try {
                const res = await fetch(`${API_BASE}/manual-override`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                const result = await res.json();
                console.log('[Override]', result.message);
            } catch (e) {
                console.error('Override failed:', e);
                this.checked = false;
            }
        } else {
            // Unchecking = return to auto mode
            try {
                const res = await fetch(`${API_BASE}/manual-override`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: 'auto' })
                });
                const result = await res.json();
                console.log('[Override]', result.message);
            } catch (e) { console.error('Auto mode failed:', e); }
        }
    });
});

// Return to Auto button
const autoBtn = document.getElementById('btn-auto-mode');
if (autoBtn) {
    autoBtn.addEventListener('click', async () => {
        try {
            await fetch(`${API_BASE}/manual-override`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'auto' })
            });
            overrideToggles.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.checked = false;
            });
            const banner = document.getElementById('override-banner');
            if (banner) banner.style.display = 'none';
        } catch (e) { console.error('Auto mode failed:', e); }
    });
}

// --- UI UPDATERS ---
function setDisplay(id, text, colorClass = null) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = text;
        if (colorClass) {
            el.className = 'font-bold ' + colorClass;
        }
    }
}

// Gov Coordination UI Updater
function updateGovCoordination(data) {
    if (!govMap) return;

    // Severity Badge
    const severityBadge = document.getElementById('gov-severity-badge');
    if (severityBadge) {
        severityBadge.innerText = data.severity.toUpperCase();
        severityBadge.className = 'badge';
        if (data.severity === 'Normal') severityBadge.classList.add('badge-green');
        else if (data.severity === 'Low') severityBadge.classList.add('badge-yellow');
        else if (data.severity === 'Moderate') severityBadge.classList.add('badge-orange');
        else if (data.severity === 'Severe') severityBadge.classList.add('badge-red');
    }

    // Map Markers
    mapMarkers.forEach(m => govMap.removeLayer(m));
    mapMarkers = [];

    data.hubs.forEach(hub => {
        const isAlert = hub.status === 'alert';
        const color = isAlert ? 'red' : 'green';

        // Use standard Leaflet marker with custom styling via CSS or simple circle markers
        const marker = L.circleMarker([hub.lat, hub.lng], {
            radius: isAlert ? 8 : 5,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).bindPopup(`<b>${hub.id}</b><br>Status: ${hub.status}<br>Intensity: ${hub.deviation_intensity}`);

        marker.addTo(govMap);
        mapMarkers.push(marker);
    });

    // Source Triangulation
    const idlePanel = document.getElementById('gov-source-idle');
    const dataPanel = document.getElementById('gov-source-panel');

    if (sourceMarker) govMap.removeLayer(sourceMarker);
    if (sourceCircle) govMap.removeLayer(sourceCircle);

    if (data.estimated_source) {
        if (idlePanel) idlePanel.style.display = 'none';
        if (dataPanel) dataPanel.style.display = 'block';

        document.getElementById('gov-source-coords').innerText = `${data.estimated_source.lat}, ${data.estimated_source.lng}`;
        document.getElementById('gov-source-conf').innerText = `${data.estimated_source.confidence}%`;
        document.getElementById('gov-source-rad').innerText = `${data.estimated_source.radius_km} km`;
        document.getElementById('gov-pollutant-type').innerText = data.pollutant_category;

        const activeCount = data.hubs.filter(h => h.status === 'alert').length;
        document.getElementById('gov-active-hubs').innerText = activeCount;

        // Draw source on map
        sourceMarker = L.marker([data.estimated_source.lat, data.estimated_source.lng]).addTo(govMap);
        sourceMarker.bindPopup(`<b>Estimated Contamination Source</b><br>Confidence: ${data.estimated_source.confidence}%`);

        sourceCircle = L.circle([data.estimated_source.lat, data.estimated_source.lng], {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.1,
            radius: data.estimated_source.radius_km * 1000 // Convert km to meters
        }).addTo(govMap);

    } else {
        if (idlePanel) idlePanel.style.display = 'block';
        if (dataPanel) dataPanel.style.display = 'none';

        document.getElementById('gov-source-coords').innerText = `--`;
        document.getElementById('gov-source-conf').innerText = `--`;
        document.getElementById('gov-pollutant-type').innerText = 'System Nominal';
        document.getElementById('gov-active-hubs').innerText = '0';
    }

    // Response Workflow
    const workflowList = document.getElementById('gov-workflow-list');
    if (workflowList) {
        workflowList.innerHTML = '';
        if (data.recommended_actions.length === 0) {
            workflowList.innerHTML = `
                <li><i class="fa-solid fa-check text-green"></i> <strong>System Nominal:</strong> No immediate action required.</li>
                <li><i class="fa-solid fa-check text-green"></i> <strong>Automated Monitoring:</strong> Active across 25 regional nodes.</li>
            `;
        } else {
            data.recommended_actions.forEach(action => {
                const li = document.createElement('li');
                const isTrigger = action.includes("TRIGGER:");
                li.innerHTML = `<i class="fa-solid fa-${isTrigger ? 'triangle-exclamation text-red' : 'arrow-right text-blue'}"></i> ${action}`;
                workflowList.appendChild(li);
            });

            // Add Gov Tab Alert to top header nav if not already there
            const govNavTab = document.querySelector('a[data-target="view-gov"]');
            if (govNavTab && !govNavTab.innerHTML.includes('fa-circle-exclamation')) {
                govNavTab.innerHTML += ' <i class="fa-solid fa-circle-exclamation text-red blink"></i>';
            }
        }

        // Remove alert from tab if normal
        if (data.severity === 'Normal') {
            const govNavTab = document.querySelector('a[data-target="view-gov"]');
            if (govNavTab && govNavTab.innerHTML.includes('fa-circle-exclamation')) {
                govNavTab.innerHTML = '<i class="fa-solid fa-building-columns text-green"></i> Gov Coordination';
            }
        }
    }
}

// Gov Coordination Simulation Trigger
const btnSimulateGov = document.getElementById('btn-simulate-gov');
if (btnSimulateGov) {
    btnSimulateGov.addEventListener('click', async () => {
        btnSimulateGov.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Triggering...';
        btnSimulateGov.disabled = true;
        try {
            const res = await fetch(`${API_BASE}/simulate-event`, { method: 'POST' });
            const data = await res.json();
            console.log(`Simulation Triggered! Epicenter roughly at: ${data.epicenter_roughly.lat}, ${data.epicenter_roughly.lng}`);
        } catch (e) { console.error('Simulation trigger failed:', e); }

        setTimeout(() => {
            btnSimulateGov.innerHTML = '<i class="fa-solid fa-biohazard"></i> Simulate Contamination Event';
            btnSimulateGov.disabled = false;
        }, 3000);
    });
}

// --- LIGHT / DARK THEME TOGGLE LOGIC ---
const allCharts = [turbidityChart, tdsChart, phChart, tempChart, spikeChart, classPieChart];

function applyChartTheme(isLight) {
    const textColor = isLight ? '#475569' : '#a1a1aa';
    const gridColorX = isLight ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.02)';
    const gridColorY = isLight ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.04)';
    const tooltipBg = isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(24, 24, 27, 0.95)';
    const tooltipTitle = isLight ? '#0f172a' : '#fff';
    const tooltipBody = isLight ? '#475569' : '#a1a1aa';
    const tooltipBorder = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.08)';

    Chart.defaults.color = textColor;

    allCharts.forEach(chart => {
        if (chart.options.scales) {
            if (chart.options.scales.x) {
                chart.options.scales.x.grid.color = gridColorX;
                chart.options.scales.x.ticks.color = textColor;
            }
            if (chart.options.scales.y) {
                chart.options.scales.y.grid.color = gridColorY;
                chart.options.scales.y.ticks.color = textColor;
            }
        }
        if (chart.options.plugins && chart.options.plugins.tooltip) {
            chart.options.plugins.tooltip.backgroundColor = tooltipBg;
            chart.options.plugins.tooltip.titleColor = tooltipTitle;
            chart.options.plugins.tooltip.bodyColor = tooltipBody;
            chart.options.plugins.tooltip.borderColor = tooltipBorder;
        }
        chart.update();
    });
}

function toggleTheme() {
    const html = document.documentElement;
    const isLight = html.getAttribute('data-theme') === 'light';
    const themeIcon = document.getElementById('theme-icon');

    if (isLight) {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        if (themeIcon) themeIcon.className = 'fa-solid fa-sun';
        applyChartTheme(false);
    } else {
        html.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        if (themeIcon) themeIcon.className = 'fa-solid fa-moon';
        applyChartTheme(true);
    }
}

const themeBtn = document.getElementById('btn-theme-toggle');
if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

// --- SET BASELINE TRIGGER ---
document.getElementById('btn-set-baseline').addEventListener('click', async () => {
    try {
        const res = await fetch(`${API_BASE}/set-baseline`, { method: 'POST' });
        if (res.ok) {
            console.log("Baseline calibration triggered.");
            document.getElementById('baseline-status-text').innerText = "Calibrating...";
            document.getElementById('baseline-status-text').className = "text-orange blink";
        }
    } catch (e) { console.error("Failed to trigger baseline:", e); }
});

// Initialize theme on load
if (localStorage.getItem('theme') === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) themeIcon.className = 'fa-solid fa-moon';
    applyChartTheme(true);
} else {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) themeIcon.className = 'fa-solid fa-sun';
}

// --- STARTUP LOADER LOGIC ---
window.addEventListener('load', () => {
    setTimeout(() => {
        const loader = document.getElementById('startup-loader');
        if (loader) loader.classList.add('loader-hidden');
    }, 1250);
});
