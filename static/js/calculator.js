/* ─── Column Calculator page ──────────────────────────────────────────────── */
let calcHistory = [];

const QUICK_EXPRS = [
  { label: "Log transform", expr: "log(col + 1)", hint: "Replace 'col' with column name" },
  { label: "Normalize (0–1)", expr: "(col - col.min()) / (col.max() - col.min())", hint: "Min-max scaling" },
  { label: "Z-score", expr: "(col - col.mean()) / col.std()", hint: "Standardize a column" },
  { label: "Multiply two cols", expr: "col_a * col_b", hint: "e.g. price * quantity" },
  { label: "Percentage ratio", expr: "col_a / col_b * 100", hint: "e.g. profit / revenue * 100" },
  { label: "Square root", expr: "sqrt(col)", hint: "Square root transform" },
  { label: "Absolute value", expr: "abs(col)", hint: "Make all values positive" },
  { label: "Round to 2dp", expr: "round(col, 2)", hint: "Round numeric column" },
  { label: "Flag high values", expr: "where(col > col.mean(), 1, 0)", hint: "Binary flag above mean" },
  { label: "Clip outliers", expr: "col.clip(col.quantile(0.05), col.quantile(0.95))", hint: "Winsorize at 5/95 percentiles" },
];

async function init() {
  await requireDataset(onLoaded);
}

async function onLoaded(info) {
  // Column chips
  document.getElementById("colChips").innerHTML = info.columns.map(c =>
    `<span class="nlq-chip" onclick="insertCol('${c}')" title="Insert column name">${c}</span>`
  ).join("");
  // Quick expression buttons
  document.getElementById("quickBtns").innerHTML = QUICK_EXPRS.map(q =>
    `<button class="btn btn-ghost btn-sm" style="text-align:left;justify-content:start" onclick="setExpr('${q.expr.replace(/'/g, "\\'")}')">
      <span>${q.label}</span>
      <span class="text-xs text-muted" style="margin-left:.5rem">${q.hint}</span>
    </button>`
  ).join("");
}

function insertCol(col) {
  const el = document.getElementById("calcExpr");
  const pos = el.selectionStart;
  const val = el.value;
  el.value = val.slice(0, pos) + col + val.slice(pos);
  el.focus();
  el.setSelectionRange(pos + col.length, pos + col.length);
}

function setExpr(expr) {
  document.getElementById("calcExpr").value = expr;
  document.getElementById("calcExpr").focus();
}

async function preview() {
  const expr    = document.getElementById("calcExpr").value.trim();
  const newCol  = document.getElementById("calcNewCol").value.trim() || "preview";
  if (!expr) return toast("Enter an expression", "error");
  const data = await api("/api/calculator/evaluate", {
    method: "POST",
    body: JSON.stringify({ expr, new_col: newCol, preview_only: true })
  });
  if (!data) return;
  showPreview(data, newCol);
}

async function addColumn() {
  const expr   = document.getElementById("calcExpr").value.trim();
  const newCol = document.getElementById("calcNewCol").value.trim();
  if (!expr)   return toast("Enter an expression", "error");
  if (!newCol) return toast("Enter a column name", "error");
  const data = await api("/api/calculator/evaluate", {
    method: "POST",
    body: JSON.stringify({ expr, new_col: newCol, preview_only: false })
  });
  if (!data) return;
  toast(`Column '${newCol}' added!`, "success");
  showPreview(data, newCol);
  addToHistory(expr, newCol, data);
  document.getElementById("calcExpr").value = "";
  document.getElementById("calcNewCol").value = "";
}

function showPreview(data, colName) {
  const card = document.getElementById("previewCard");
  card.style.display = "block";
  document.getElementById("previewColName").textContent = colName;
  const s = data.stats;
  document.getElementById("previewStats").innerHTML = s.mean !== undefined ? `
    <div class="stat-row"><span class="stat-key">Min</span><span class="stat-val mono">${fmt(s.min, 6)}</span></div>
    <div class="stat-row"><span class="stat-key">Max</span><span class="stat-val mono">${fmt(s.max, 6)}</span></div>
    <div class="stat-row"><span class="stat-key">Mean</span><span class="stat-val mono">${fmt(s.mean, 6)}</span></div>
    <div class="stat-row"><span class="stat-key">Std</span><span class="stat-val mono">${fmt(s.std, 6)}</span></div>
    <div class="stat-row"><span class="stat-key">Null values</span><span class="stat-val mono">${s.nulls}</span></div>
  ` : "";
  document.getElementById("previewValues").innerHTML = `
    <div class="text-muted text-xs mb-1">FIRST 20 VALUES</div>
    <div style="display:flex;flex-wrap:wrap;gap:.3rem">
      ${data.preview.map(v => `<span class="badge badge-cyan mono">${typeof v === 'number' ? fmt(v, 4) : v}</span>`).join("")}
    </div>`;
}

function addToHistory(expr, col, data) {
  calcHistory.push({ expr, col, ts: new Date().toLocaleTimeString() });
  document.getElementById("calcHistCount").textContent = `${calcHistory.length} added`;
  document.getElementById("calcHistory").innerHTML = calcHistory.slice().reverse().map(h => `
    <div class="card mb-1" style="padding:.6rem;background:var(--bg)">
      <div style="font-weight:600;font-size:.85rem;color:var(--cyan)">${h.col}</div>
      <div class="mono text-xs text-muted mt-1" style="word-break:break-all">${h.expr}</div>
      <div class="text-xs text-dim mt-1">${h.ts}</div>
    </div>
  `).join("");
}

document.getElementById("previewBtn").addEventListener("click", () =>
  withLoading(document.getElementById("previewBtn"), preview));
document.getElementById("addColBtn").addEventListener("click", () =>
  withLoading(document.getElementById("addColBtn"), addColumn));

// Allow Shift+Enter in textarea for newline, Enter alone triggers preview
document.getElementById("calcExpr").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); preview(); }
});

init();
