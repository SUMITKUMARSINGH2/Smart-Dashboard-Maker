/* ─── Regression Analysis page ────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const xSel = document.getElementById("regXCols");
  const ySel = document.getElementById("regYCol");
  xSel.innerHTML = info.numeric_cols.map(c => `<option value="${c}">${c}</option>`).join("");
  ySel.innerHTML = `<option value="">— Select Target —</option>` +
    info.numeric_cols.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function runRegression() {
  const xSel  = document.getElementById("regXCols");
  const x_cols = [...xSel.selectedOptions].map(o => o.value);
  const y_col  = document.getElementById("regYCol").value;
  const degree = parseInt(document.getElementById("regDegree").value);
  const model  = document.getElementById("regModel").value;
  if (!x_cols.length) return toast("Select at least one feature column", "error");
  if (!y_col) return toast("Select a target column", "error");
  const data = await api("/api/regression", {
    method: "POST",
    body: JSON.stringify({ x_cols, y_col, degree, model })
  });
  if (!data) return;
  // Metrics
  document.getElementById("regMetrics").style.display = "block";
  const r2Color = data.r2 >= 0.8 ? "var(--green)" : data.r2 >= 0.5 ? "var(--amber)" : "var(--red)";
  document.getElementById("regMetricsContent").innerHTML = `
    <div class="stat-row"><span class="stat-key">R² Score</span><span class="stat-val mono" style="color:${r2Color};font-size:1.1rem;font-weight:700">${data.r2}</span></div>
    <div class="stat-row"><span class="stat-key">Cross-Val R²</span><span class="stat-val mono">${data.cv_r2}</span></div>
    <div class="stat-row"><span class="stat-key">RMSE</span><span class="stat-val mono">${data.rmse}</span></div>
    <div class="stat-row"><span class="stat-key">MAE</span><span class="stat-val mono">${data.mae}</span></div>
    <div class="stat-row"><span class="stat-key">Intercept</span><span class="stat-val mono">${data.intercept}</span></div>
    <div class="stat-row"><span class="stat-key">N Samples</span><span class="stat-val mono">${data.n_samples}</span></div>
    <div class="stat-row"><span class="stat-key">Model</span><span class="stat-val"><span class="badge badge-cyan">${data.model} (deg=${data.degree})</span></span></div>
  `;
  // Coefficients
  document.getElementById("regCoeffs").innerHTML = data.coefficients.slice(0, 10).map(c => `
    <div class="stat-row">
      <span class="stat-key text-xs">${c.feature}</span>
      <div style="display:flex;align-items:center;gap:.5rem">
        <div class="progress-bar" style="width:80px">
          <div class="progress-bar-fill" style="width:${Math.min(100, Math.abs(c.coefficient) * 20)}%;background:${c.coefficient >= 0 ? 'var(--cyan)' : 'var(--pink)'}"></div>
        </div>
        <span class="mono text-xs">${c.coefficient}</span>
      </div>
    </div>
  `).join("");
  // Charts
  if (data.fig_fit) renderChart("regFitChart", data.fig_fit);
  if (data.fig_res) renderChart("regResChart", data.fig_res);
  if (data.fig_rhist) renderChart("regRhistChart", data.fig_rhist);
  if (data.fig_line) {
    renderChart("regLineChart", data.fig_line);
  } else {
    document.getElementById("regLineChart").innerHTML =
      `<div class="chart-placeholder">Select a single X column for a fit line</div>`;
  }
  toast(`R² = ${data.r2}`, data.r2 >= 0.5 ? "success" : "info");
}

// Tabs
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`[data-panel="${tab.dataset.tab}"]`)?.classList.add("active");
  });
});

document.getElementById("regBtn").addEventListener("click", () =>
  withLoading(document.getElementById("regBtn"), runRegression));

init();
