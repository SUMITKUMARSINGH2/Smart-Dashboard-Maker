/* ─── Export page ─────────────────────────────────────────────────────────── */
async function init() {
  const info = await requireDataset();
  if (!info) return;
  document.getElementById("exportStats").textContent =
    `${info.filename} · ${info.rows.toLocaleString()} rows · ${info.cols} columns · ${info.numeric_cols.length} numeric cols`;
}

init();
