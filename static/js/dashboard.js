/* ─── Dashboard page ──────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(loadDashboard);
}

async function loadDashboard(info) {
  await Promise.all([loadKPIs(), loadCharts()]);
}

async function loadKPIs() {
  const data = await api("/api/dashboard/kpis");
  if (!data || !data.kpis) return;
  const colors = ["cyan","purple","pink","green","amber","cyan","purple","pink"];
  const kpiRow = document.getElementById("kpiRow");
  kpiRow.innerHTML = [
    { label: "Total Rows", val: data.rows.toLocaleString(), cls: "cyan" },
    { label: "Total Columns", val: data.cols, cls: "purple" },
    ...data.kpis.map((k,i) => ({
      label: `Avg ${k.col}`, val: fmt(k.mean), cls: colors[i % colors.length]
    }))
  ].slice(0, 8).map(k =>
    `<div class="kpi-card ${k.cls}">
      <div class="kpi-value">${k.val}</div>
      <div class="kpi-label">${k.label}</div>
    </div>`
  ).join("");
}

async function loadCharts() {
  const data = await api("/api/dashboard/charts");
  if (!data || !data.charts) return;
  const grid = document.getElementById("chartsGrid");
  grid.innerHTML = data.charts.map((c, i) =>
    `<div class="card"><div class="card-title mb-1">${c.title}</div><div id="dash-chart-${i}" style="min-height:300px"></div></div>`
  ).join("");
  data.charts.forEach((c, i) => {
    if (c.fig) renderChart(`dash-chart-${i}`, c.fig);
  });
}

document.getElementById("refreshBtn").addEventListener("click", async () => {
  const btn = document.getElementById("refreshBtn");
  await withLoading(btn, async () => {
    await Promise.all([loadKPIs(), loadCharts()]);
  });
});

init();
