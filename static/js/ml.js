/* ─── ML Insights page ────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  // Populate multi-select cols
  ["kCols","anomCols"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = info.numeric_cols.map(c => `<option value="${c}">${c}</option>`).join("");
  });
  // Feature target
  const ft = document.getElementById("featTarget");
  ft.innerHTML = `<option value="">— Select —</option>` +
    info.columns.map(c => `<option value="${c}">${c}</option>`).join("");
}

// Sliders
const kSlider = document.getElementById("kSlider");
const kVal = document.getElementById("kVal");
kSlider.addEventListener("input", () => kVal.textContent = kSlider.value);

const contamSlider = document.getElementById("contamSlider");
const contamVal = document.getElementById("contamVal");
contamSlider.addEventListener("input", () => contamVal.textContent = contamSlider.value + "%");

const pcaSlider = document.getElementById("pcaSlider");
const pcaVal = document.getElementById("pcaVal");
pcaSlider.addEventListener("input", () => pcaVal.textContent = pcaSlider.value);

// KMeans
document.getElementById("kmeansBtn").addEventListener("click", async () => {
  await withLoading(document.getElementById("kmeansBtn"), async () => {
    const k = parseInt(kSlider.value);
    const cols = [...document.getElementById("kCols").selectedOptions].map(o => o.value);
    const data = await api("/api/ml/kmeans", {
      method: "POST", body: JSON.stringify({ k, cols: cols.length ? cols : null })
    });
    if (!data) return;
    // Cluster sizes
    document.getElementById("kmeansResults").style.display = "block";
    document.getElementById("clusterSizes").innerHTML = Object.entries(data.sizes)
      .map(([k,v]) => `<div class="stat-row"><span class="stat-key">${k}</span><span class="stat-val">${v.toLocaleString()} rows</span></div>`)
      .join("");
    document.getElementById("pcaVar").textContent =
      `PCA explained variance: ${(data.explained_var[0]*100).toFixed(1)}% + ${(data.explained_var[1]*100).toFixed(1)}%`;
    if (data.fig) renderChart("kmeansChart", data.fig);
    if (data.fig_elbow) renderChart("elbowChart", data.fig_elbow);
  });
});

// Anomaly
document.getElementById("anomalyBtn").addEventListener("click", async () => {
  await withLoading(document.getElementById("anomalyBtn"), async () => {
    const contamination = parseInt(contamSlider.value) / 100;
    const cols = [...document.getElementById("anomCols").selectedOptions].map(o => o.value);
    const data = await api("/api/ml/anomaly", {
      method: "POST", body: JSON.stringify({ contamination, cols: cols.length ? cols : null })
    });
    if (!data) return;
    document.getElementById("anomalyStats").style.display = "block";
    document.getElementById("anomalyInfo").innerHTML = `
      <div class="stat-row"><span class="stat-key">Anomalies</span><span class="stat-val" style="color:var(--pink)">${data.n_anomalies.toLocaleString()}</span></div>
      <div class="stat-row"><span class="stat-key">Total Rows</span><span class="stat-val">${data.total.toLocaleString()}</span></div>
      <div class="stat-row"><span class="stat-key">Anomaly %</span><span class="stat-val">${data.pct}%</span></div>
    `;
    document.getElementById("anomalyChartCard").style.display = "block";
    if (data.fig) renderChart("anomalyChart", data.fig);
    if (data.fig_score) renderChart("scoreChart", data.fig_score);
    if (data.anomaly_rows && data.anomaly_rows.length) {
      document.getElementById("anomRowsCard").classList.remove("hidden");
      renderTable("anomRowsTable", data.anomaly_rows, data.cols);
    }
  });
});

// Feature Importance
document.getElementById("featBtn").addEventListener("click", async () => {
  await withLoading(document.getElementById("featBtn"), async () => {
    const target = document.getElementById("featTarget").value;
    const model  = document.getElementById("featModel").value;
    if (!target) return toast("Select a target column", "error");
    const data = await api("/api/ml/feature-importance", {
      method: "POST", body: JSON.stringify({ target, model })
    });
    if (!data) return;
    document.getElementById("featTable").style.display = "block";
    document.getElementById("featList").innerHTML = data.features.slice(0, 15).map(f =>
      `<div class="stat-row">
        <span class="stat-key">${f.feat}</span>
        <div style="display:flex;align-items:center;gap:.5rem">
          <div class="progress-bar" style="width:100px">
            <div class="progress-bar-fill" style="width:${(f.importance*100).toFixed(1)}%;background:var(--purple)"></div>
          </div>
          <span class="stat-val">${(f.importance*100).toFixed(2)}%</span>
        </div>
      </div>`
    ).join("");
    if (data.fig) renderChart("featChart", data.fig);
  });
});

// PCA
document.getElementById("pcaBtn").addEventListener("click", async () => {
  await withLoading(document.getElementById("pcaBtn"), async () => {
    const n_components = parseInt(pcaSlider.value);
    const data = await api("/api/ml/pca", { method: "POST", body: JSON.stringify({ n_components }) });
    if (!data) return;
    document.getElementById("pcaInfo").style.display = "block";
    document.getElementById("pcaComponents").innerHTML = data.components.map(c =>
      `<div class="stat-row"><span class="stat-key">${c.pc}</span>
       <span class="stat-val">${c.explained_var_pct}% variance</span></div>`
    ).join("") + `<div class="mt-1 text-muted text-sm">Total: ${data.total_var_pct}% explained</div>`;
    if (data.fig_scree) renderChart("pcaScree", data.fig_scree);
    if (data.fig_bi) renderChart("pcaBiplot", data.fig_bi);
  });
});

// Tabs
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`[data-panel="${tab.dataset.tab}"]`)?.classList.add("active");
  });
});

init();
