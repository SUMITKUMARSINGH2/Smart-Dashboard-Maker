/* ─── EDA page ────────────────────────────────────────────────────────────── */
async function init() {
  const info = await requireDataset(onLoaded);
}

function onLoaded(info) {
  populateColSelects(info, "distCol", "scatterX", "scatterY", "hypCol1", "hypCol2", "scatterColor");
  const boxCols = document.getElementById("boxCols");
  if (boxCols) {
    info.numeric_cols.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c; opt.textContent = c;
      boxCols.appendChild(opt);
    });
  }
  // Auto-run correlation
  runCorr();
}

async function runCorr() {
  const method = document.getElementById("corrMethod").value;
  const data = await api(`/api/eda/correlation?method=${method}`);
  if (data && data.fig) renderChart("corrChart", data.fig);
}

async function runDist() {
  const col = document.getElementById("distCol").value;
  const bins = document.getElementById("distBins").value;
  if (!col) return toast("Select a column", "error");
  const data = await api(`/api/eda/distribution?col=${encodeURIComponent(col)}&bins=${bins}`);
  if (data && data.fig) renderChart("distChart", data.fig);
}

async function runBox() {
  const boxCols = document.getElementById("boxCols");
  const selected = [...boxCols.selectedOptions].map(o => o.value);
  const qs = selected.map(c => `cols[]=${encodeURIComponent(c)}`).join("&");
  const data = await api(`/api/eda/boxplot${qs ? "?" + qs : ""}`);
  if (data && data.fig) renderChart("boxChart", data.fig);
}

async function runScatter() {
  const x = document.getElementById("scatterX").value;
  const y = document.getElementById("scatterY").value;
  const color = document.getElementById("scatterColor").value;
  if (!x || !y) return toast("Select X and Y columns", "error");
  let url = `/api/eda/scatter?x=${encodeURIComponent(x)}&y=${encodeURIComponent(y)}`;
  if (color) url += `&color=${encodeURIComponent(color)}`;
  const data = await api(url);
  if (data && data.fig) renderChart("scatterChart", data.fig);
}

async function runHyp() {
  const col1 = document.getElementById("hypCol1").value;
  const col2 = document.getElementById("hypCol2").value;
  const test = document.getElementById("hypTest").value;
  if (!col1 || !col2) return toast("Select both columns", "error");
  const data = await api(`/api/eda/hypothesis?col1=${encodeURIComponent(col1)}&col2=${encodeURIComponent(col2)}&test=${test}`);
  if (!data) return;
  const el = document.getElementById("hypResult");
  el.classList.remove("hidden");
  const cls = data.significant ? "alert-success" : "alert-warn";
  el.innerHTML = `<div class="alert ${cls}">
    <strong>${data.test}</strong> — stat=${data.stat.toFixed(4)}, p=${data.pval.toFixed(6)}<br>
    ${data.interpretation}
  </div>`;
}

// Tab switching
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    const panel = document.querySelector(`[data-panel="${tab.dataset.tab}"]`);
    if (panel) panel.classList.add("active");
  });
});

document.getElementById("corrBtn").addEventListener("click", () =>
  withLoading(document.getElementById("corrBtn"), runCorr));
document.getElementById("distBtn").addEventListener("click", () =>
  withLoading(document.getElementById("distBtn"), runDist));
document.getElementById("boxBtn").addEventListener("click", () =>
  withLoading(document.getElementById("boxBtn"), runBox));
document.getElementById("scatterBtn").addEventListener("click", () =>
  withLoading(document.getElementById("scatterBtn"), runScatter));
document.getElementById("hypBtn").addEventListener("click", () =>
  withLoading(document.getElementById("hypBtn"), runHyp));

init();
