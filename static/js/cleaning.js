/* ─── Cleaning page ───────────────────────────────────────────────────────── */
let dsInfo = null;

async function init() {
  dsInfo = await requireDataset(onLoaded);
}

async function onLoaded(info) {
  dsInfo = info;
  updateKpis(info);
  populateSelects(info.columns, info.numeric_cols);
  await loadPreview();
}

function updateKpis(info) {
  document.getElementById("statusKpis").innerHTML = [
    { label: "Rows", val: info.rows.toLocaleString(), cls: "cyan" },
    { label: "Columns", val: info.cols, cls: "purple" },
    { label: "Missing", val: Object.values(info.missing||{}).reduce((a,b)=>a+b,0).toLocaleString(), cls: "pink" },
    { label: "Numeric", val: (info.numeric_cols||[]).length, cls: "green" },
  ].map(k => `<div class="kpi-card ${k.cls}"><div class="kpi-value">${k.val}</div><div class="kpi-label">${k.label}</div></div>`).join("");
}

function populateSelects(cols, numCols) {
  const allOpt = cols.map(c => `<option value="${c}">${c}</option>`).join("");
  const numOpt = numCols.map(c => `<option value="${c}">${c}</option>`).join("");
  ["dropColSel","renameOldSel","castColSel","filterColSel"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = `<option value="">— Select —</option>` + allOpt;
  });
  ["fillCol","dropMissCol","outlierColSel"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = (id === "fillCol" ? `<option value="">All numeric cols</option>` : `<option value="">— Select —</option>`) + numOpt;
  });
}

async function loadPreview() {
  const info = await api("/api/dataset-info");
  if (!info || !info.loaded) return;
  updateKpis(info);
  populateSelects(info.columns, info.numeric_cols);
  document.getElementById("previewStats").textContent = `${info.rows.toLocaleString()} rows · ${info.cols} cols`;
  const preview = await api("/api/preview?n=100");
  if (preview) renderTable("previewTable", preview.rows, preview.columns);
}

async function doClean(op, extra = {}) {
  const data = await api("/api/clean", {
    method: "POST",
    body: JSON.stringify({ op, ...extra }),
  });
  if (data && data.ok) {
    toast(data.msg || "Done", "success");
    await loadPreview();
  }
}

// Button handlers
document.getElementById("dedupeBtn").addEventListener("click", () => doClean("drop_duplicates"));

document.getElementById("fillBtn").addEventListener("click", () => {
  const col = document.getElementById("fillCol").value || null;
  const method = document.getElementById("fillMethod").value;
  const value = method === "value" ? document.getElementById("customValue").value : undefined;
  doClean("fill_missing", { col, method, value });
});

document.getElementById("fillMethod").addEventListener("change", () => {
  document.getElementById("customValueGroup").classList.toggle("hidden",
    document.getElementById("fillMethod").value !== "value");
});

document.getElementById("dropMissBtn").addEventListener("click", () => {
  const col = document.getElementById("dropMissCol").value || null;
  doClean("drop_missing", { col });
});

document.getElementById("dropColBtn").addEventListener("click", () => {
  const col = document.getElementById("dropColSel").value;
  if (!col) return toast("Select a column", "error");
  doClean("drop_col", { col });
});

document.getElementById("renameBtn").addEventListener("click", () => {
  const old = document.getElementById("renameOldSel").value;
  const newName = document.getElementById("renameNewVal").value.trim();
  if (!old || !newName) return toast("Select column and enter new name", "error");
  doClean("rename_col", { old, new: newName });
});

document.getElementById("castBtn").addEventListener("click", () => {
  const col = document.getElementById("castColSel").value;
  const dtype = document.getElementById("castTypeSel").value;
  if (!col) return toast("Select a column", "error");
  doClean("cast_col", { col, dtype });
});

document.getElementById("stripWsBtn").addEventListener("click", () => doClean("strip_whitespace"));
document.getElementById("lowerColsBtn").addEventListener("click", () => doClean("lowercase_cols"));

document.getElementById("removeOutliersBtn").addEventListener("click", () => {
  const col = document.getElementById("outlierColSel").value;
  const method = document.getElementById("outlierMethodSel").value;
  if (!col) return toast("Select a column", "error");
  doClean("remove_outliers", { col, method });
});

document.getElementById("filterRowsBtn").addEventListener("click", () => {
  const col = document.getElementById("filterColSel").value;
  const filter_op = document.getElementById("filterOpSel").value;
  const val = document.getElementById("filterVal").value;
  if (!col || !val) return toast("Select column and enter a value", "error");
  doClean("filter_rows", { col, filter_op, val });
});

document.getElementById("resetBtn").addEventListener("click", () => {
  if (!confirm("Reset to original uploaded data? All cleaning steps will be lost.")) return;
  doClean("reset");
});

init();
