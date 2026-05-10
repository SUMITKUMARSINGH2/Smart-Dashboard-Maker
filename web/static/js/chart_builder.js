/* ─── Chart Builder page ──────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const allCols = info.columns;
  ["chartX","chartY","chartColor","chartSize"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = `<option value="">— None —</option>` +
      allCols.map(c => `<option value="${c}">${c}</option>`).join("");
  });
}

async function buildChart() {
  const body = {
    type: document.getElementById("chartType").value,
    x: document.getElementById("chartX").value || null,
    y: document.getElementById("chartY").value || null,
    color: document.getElementById("chartColor").value || null,
    size: document.getElementById("chartSize").value || null,
    agg: document.getElementById("chartAgg").value,
    bins: parseInt(document.getElementById("chartBins").value) || 20,
    title: document.getElementById("chartTitle").value || "",
  };
  const data = await api("/api/chart/build", { method: "POST", body: JSON.stringify(body) });
  if (data && data.fig) {
    document.getElementById("chartPreview").innerHTML = "";
    renderChart("chartPreview", data.fig);
  }
}

document.getElementById("buildBtn").addEventListener("click", () =>
  withLoading(document.getElementById("buildBtn"), buildChart));

init();
