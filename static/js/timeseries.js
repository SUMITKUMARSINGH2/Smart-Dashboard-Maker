/* ─── Time Series page ────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const dateCol = document.getElementById("dateCol");
  const valCol  = document.getElementById("valCol");
  // All columns for date (user may have non-datetime strings that parse)
  dateCol.innerHTML = `<option value="">— Select —</option>` +
    info.columns.map(c => `<option value="${c}">${c}</option>`).join("");
  valCol.innerHTML = `<option value="">— Select —</option>` +
    info.numeric_cols.map(c => `<option value="${c}">${c}</option>`).join("");
}

function getParams() {
  return {
    date_col: document.getElementById("dateCol").value,
    val_col:  document.getElementById("valCol").value,
    window:   document.getElementById("rollingWindow").value,
  };
}

async function runTrend() {
  const p = getParams();
  if (!p.date_col || !p.val_col) return toast("Select date and value columns", "error");
  const qs = new URLSearchParams(p).toString();
  const data = await api(`/api/timeseries/trend?${qs}`);
  if (data && data.fig) renderChart("trendChart", data.fig);
}

async function runGrowth() {
  const p = getParams();
  if (!p.date_col || !p.val_col) return toast("Select date and value columns", "error");
  const qs = new URLSearchParams(p).toString();
  const data = await api(`/api/timeseries/growth?${qs}`);
  if (data && data.fig) renderChart("growthChart", data.fig);
}

async function runDecomp() {
  const p = getParams();
  if (!p.date_col || !p.val_col) return toast("Select date and value columns", "error");
  p.period = document.getElementById("decompPeriod").value;
  const qs = new URLSearchParams(p).toString();
  const data = await api(`/api/timeseries/decompose?${qs}`);
  if (data && data.fig) renderChart("decompChart", data.fig);
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

document.getElementById("trendBtn").addEventListener("click", () =>
  withLoading(document.getElementById("trendBtn"), runTrend));
document.getElementById("growthBtn").addEventListener("click", () =>
  withLoading(document.getElementById("growthBtn"), runGrowth));
document.getElementById("decompBtn").addEventListener("click", () =>
  withLoading(document.getElementById("decompBtn"), runDecomp));

init();
