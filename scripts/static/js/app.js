// =========================================================
// Prompt Injection Detector — Dashboard logic
//
// Matches the real API shapes:
//
// POST /scan  body: { text }
//   -> { flagged, category, confidence, method, atlas: { id, name, url } }
//
// GET /history
//   -> [ { id, text, flagged (0/1), category, atlas_id, atlas_name,
//          confidence, method, timestamp }, ... ]
//
// GET /stats
//   -> { total_scans, total_flagged, by_category: [ { category, count }, ... ] }
//   (no confidence histogram from the backend — built client-side from /history below)
// =========================================================

const API_BASE = ""; // same-origin, since FastAPI serves the static files too

const promptInput = document.getElementById("promptInput");
const scanBtn = document.getElementById("scanBtn");
const ollamaToggle = document.getElementById("ollamaToggle");
const resultCard = document.getElementById("resultCard");
const ollamaPane = document.getElementById("ollamaPane");
const scanCountEl = document.getElementById("scanCount");
const clockEl = document.getElementById("clock");

let categoryChart, confidenceChart;

// --- Clock ---
function tickClock() {
  clockEl.textContent = new Date().toLocaleTimeString();
}
setInterval(tickClock, 1000);
tickClock();

// --- Scan action ---
scanBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  scanBtn.disabled = true;
  scanBtn.textContent = "Scanning...";

  try {
    const res = await fetch(`${API_BASE}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: prompt })
    });
    const data = await res.json();
    renderResult(data);

    if (ollamaToggle.checked) {
      await runOllamaComparison(prompt);
    } else {
      ollamaPane.classList.add("hidden");
    }

    await refreshHistory();
    await refreshStats();
  } catch (err) {
    console.error("Scan failed:", err);
    alert("Scan request failed — check the API is running on this origin/port.");
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = "Scan Prompt";
  }
});

function renderResult(data) {
  resultCard.classList.remove("hidden");

  const verdictEl = document.getElementById("resultVerdict");
  const isMalicious = !!data.flagged;
  verdictEl.textContent = isMalicious ? "Malicious" : "Benign";
  verdictEl.className = "verdict " + (isMalicious ? "malicious" : "benign");

  document.getElementById("resultConfidence").textContent =
    data.confidence != null ? `${(data.confidence * 100).toFixed(1)}% confidence` : "--";
  document.getElementById("resultCategory").textContent = data.category || "n/a";

  const atlas = data.atlas || {};
  const atlasEl = document.getElementById("resultAtlas");
  if (atlas.id) {
    atlasEl.innerHTML = `<a href="${atlas.url}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;">${atlas.id} — ${atlas.name}</a>`;
  } else {
    atlasEl.textContent = "n/a";
  }

  document.getElementById("resultSource").textContent = data.method || "n/a";
}

// --- Ollama side-by-side (stubbed until backend route exists) ---
async function runOllamaComparison(prompt) {
  ollamaPane.classList.remove("hidden");
  document.getElementById("ollamaInput").textContent = prompt;
  const outputEl = document.getElementById("ollamaOutput");
  outputEl.textContent = "Querying local model...";

  try {
    // ADJUST: this endpoint doesn't exist yet — you'll build it in the Ollama integration step.
    const res = await fetch(`${API_BASE}/ollama-query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    if (!res.ok) throw new Error("not implemented yet");
    const data = await res.json();
    outputEl.textContent = data.response || "(empty response)";
  } catch (err) {
    outputEl.textContent = "/ollama-query endpoint not implemented yet.";
  }
}

// --- History table ---
let lastHistory = []; // cached for building the confidence histogram

async function refreshHistory() {
  try {
    const res = await fetch(`${API_BASE}/history`);
    const rows = await res.json();
    lastHistory = Array.isArray(rows) ? rows : [];

    const tbody = document.getElementById("historyBody");
    tbody.innerHTML = "";

    lastHistory.slice(0, 25).forEach(row => {
      const tr = document.createElement("tr");
      const isMalicious = !!row.flagged;
      const atlasLabel = row.atlas_id ? `${row.atlas_id}` : "--";
      tr.innerHTML = `
        <td>${row.timestamp ? new Date(row.timestamp).toLocaleTimeString() : "--"}</td>
        <td class="${isMalicious ? "tag-malicious" : "tag-benign"}">${isMalicious ? "Malicious" : "Benign"}</td>
        <td>${row.category || "--"}</td>
        <td title="${row.atlas_name || ""}">${atlasLabel}</td>
        <td>${row.confidence != null ? (row.confidence * 100).toFixed(0) + "%" : "--"}</td>
        <td>${row.method || "--"}</td>
      `;
      tbody.appendChild(tr);
    });

    renderConfidenceChart(lastHistory);
  } catch (err) {
    console.error("History fetch failed:", err);
  }
}

// --- Stats charts ---
async function refreshStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    const stats = await res.json();
    renderCategoryChart(stats.by_category || []);
    if (stats.total_scans != null) {
      scanCountEl.textContent = `${stats.total_scans} scans (${stats.total_flagged || 0} flagged)`;
    }
  } catch (err) {
    console.error("Stats fetch failed:", err);
  }
}

function renderCategoryChart(byCategory) {
  const ctx = document.getElementById("categoryChart");
  const labels = byCategory.map(c => c.category);
  const values = byCategory.map(c => c.count);

  if (categoryChart) categoryChart.destroy();
  categoryChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: "#00e0a4",
        borderRadius: 3
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#6b7785" }, grid: { color: "#1f2733" } },
        y: { ticks: { color: "#6b7785" }, grid: { color: "#1f2733" }, beginAtZero: true }
      }
    }
  });
}

// Confidence histogram is built client-side from /history since /stats
// doesn't return one directly. Buckets: 0-20, 20-40, 40-60, 60-80, 80-100%
function renderConfidenceChart(history) {
  const ctx = document.getElementById("confidenceChart");
  const bucketLabels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"];
  const bucketCounts = [0, 0, 0, 0, 0];

  history.forEach(row => {
    const c = row.confidence != null ? row.confidence : 0;
    const idx = Math.min(4, Math.floor(c * 5));
    bucketCounts[idx]++;
  });

  if (confidenceChart) confidenceChart.destroy();
  confidenceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: bucketLabels,
      datasets: [{
        data: bucketCounts,
        borderColor: "#ffb020",
        backgroundColor: "#ffb02022",
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#6b7785" }, grid: { color: "#1f2733" } },
        y: { ticks: { color: "#6b7785", precision: 0 }, grid: { color: "#1f2733" }, beginAtZero: true }
      }
    }
  });
}

// --- Init ---
refreshHistory();
refreshStats();
