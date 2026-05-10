/* ─── Comparison page ─────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

async function onLoaded(info) {
  document.getElementById("dsAInfo").innerHTML =
    `<strong>${info.filename || "Dataset A"}</strong><br>
     ${info.rows.toLocaleString()} rows · ${info.cols} cols · ${info.numeric_cols.length} numeric columns`;
}

const dropZone = document.getElementById("cmpDropZone");
const fileInput = document.getElementById("cmpFileInput");

dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const f = e.dataTransfer.files[0];
  if (f) uploadB(f);
});
fileInput.addEventListener("change", () => fileInput.files[0] && uploadB(fileInput.files[0]));

async function uploadB(file) {
  const fd = new FormData();
  fd.append("file", file);
  try {
    const res = await fetch("/api/comparison/upload", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) return toast(data.error || "Upload failed", "error");
    document.getElementById("dsBInfo").classList.remove("hidden");
    document.getElementById("dsBInfo").innerHTML =
      `<strong>${data.filename}</strong> — ${data.rows.toLocaleString()} rows · ${data.cols} cols`;
    toast("Dataset B loaded", "success");
    await loadComparison();
  } catch (e) {
    toast("Upload error: " + e.message, "error");
  }
}

async function loadComparison() {
  const data = await api("/api/comparison/stats");
  if (!data) return;
  document.getElementById("cmpResultArea").classList.remove("hidden");
  // Stats table
  const rows = data.stats.map(s => `
    <tr>
      <td><strong>${s.col}</strong></td>
      <td class="mono">${fmt(s.mean_a)}</td><td class="mono">${fmt(s.mean_b)}</td>
      <td class="mono">${fmt(s.std_a)}</td><td class="mono">${fmt(s.std_b)}</td>
      <td class="mono">${fmt(s.min_a)}</td><td class="mono">${fmt(s.min_b)}</td>
      <td class="mono">${fmt(s.max_a)}</td><td class="mono">${fmt(s.max_b)}</td>
    </tr>
  `).join("");
  document.getElementById("cmpStatsTable").innerHTML = `
    <div class="table-wrap"><table>
      <thead><tr><th>Column</th><th>Mean A</th><th>Mean B</th><th>Std A</th><th>Std B</th><th>Min A</th><th>Min B</th><th>Max A</th><th>Max B</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>`;
  if (data.fig) renderChart("cmpChart", data.fig);
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

init();
