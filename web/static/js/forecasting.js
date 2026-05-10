/* ─── Forecasting page ────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const dateCol = document.getElementById("fcDateCol");
  dateCol.innerHTML = `<option value="">— Select —</option>` +
    info.columns.map(c => `<option value="${c}">${c}</option>`).join("");
  const valCol = document.getElementById("fcValCol");
  valCol.innerHTML = `<option value="">— Select —</option>` +
    info.numeric_cols.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function runForecast() {
  const body = {
    date_col: document.getElementById("fcDateCol").value,
    val_col:  document.getElementById("fcValCol").value,
    periods:  parseInt(document.getElementById("fcPeriods").value) || 30,
    freq:     document.getElementById("fcFreq").value,
    p: parseInt(document.getElementById("fcP").value) || 1,
    d: parseInt(document.getElementById("fcD").value) || 1,
    q: parseInt(document.getElementById("fcQ").value) || 1,
  };
  if (!body.date_col || !body.val_col) {
    return toast("Select date and value columns", "error");
  }
  const data = await api("/api/forecast", { method: "POST", body: JSON.stringify(body) });
  if (!data) return;
  // Chart
  document.getElementById("fcChart").innerHTML = "";
  renderChart("fcChart", data.fig);
  // Summary
  const card = document.getElementById("fcSummaryCard");
  card.style.display = "block";
  const s = data.summary;
  document.getElementById("fcSummary").innerHTML = `
    <div class="stat-row"><span class="stat-key">AIC</span><span class="stat-val">${s.aic}</span></div>
    <div class="stat-row"><span class="stat-key">BIC</span><span class="stat-val">${s.bic}</span></div>
    <div class="stat-row"><span class="stat-key">Observations</span><span class="stat-val">${s.n_obs}</span></div>
    <div class="stat-row"><span class="stat-key">Periods Forecast</span><span class="stat-val">${s.periods}</span></div>
    <div class="stat-row"><span class="stat-key">Forecast Mean</span><span class="stat-val mono">${fmt(s.forecast_mean, 4)}</span></div>
    <div class="stat-row"><span class="stat-key">Forecast Min</span><span class="stat-val mono">${fmt(s.forecast_min, 4)}</span></div>
    <div class="stat-row"><span class="stat-key">Forecast Max</span><span class="stat-val mono">${fmt(s.forecast_max, 4)}</span></div>
  `;
  toast("Forecast generated", "success");
}

document.getElementById("fcBtn").addEventListener("click", () =>
  withLoading(document.getElementById("fcBtn"), runForecast));

init();
