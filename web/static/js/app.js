/* ─── Global App JS ──────────────────────────────────────────────────────────── */

// Sidebar toggle
const sidebar = document.getElementById("sidebar");
const mainWrapper = document.getElementById("mainWrapper");
const sidebarToggle = document.getElementById("sidebarToggle");
const topbarToggle = document.getElementById("topbarToggle");

function toggleSidebar() {
  const isMobile = window.innerWidth <= 900;
  if (isMobile) {
    sidebar.classList.toggle("mobile-open");
  } else {
    sidebar.classList.toggle("collapsed");
    mainWrapper.classList.toggle("sidebar-collapsed");
  }
}
if (sidebarToggle) sidebarToggle.addEventListener("click", toggleSidebar);
if (topbarToggle) topbarToggle.addEventListener("click", toggleSidebar);

// Tabs
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    const group = tab.dataset.group || tab.closest(".tabs")?.dataset.group;
    const target = tab.dataset.tab;
    const container = tab.closest(".card, .page-content, main") || document;
    container.querySelectorAll(".tab").forEach(t => {
      if ((t.dataset.group || t.closest(".tabs")?.dataset.group) === group) t.classList.remove("active");
    });
    container.querySelectorAll(".tab-panel").forEach(p => {
      if (p.dataset.panel && p.closest(".card, .page-content, main") === container.closest(".card, .page-content, main")) {
        p.classList.remove("active");
      }
    });
    tab.classList.add("active");
    const panel = document.querySelector(`[data-panel="${target}"]`);
    if (panel) panel.classList.add("active");
  });
});

// Toast system
window.toast = function(msg, type="info", duration=3500) {
  const icons = { success: "✓", error: "✗", info: "ℹ" };
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${icons[type]||"•"}</span><span>${msg}</span>`;
  const container = document.getElementById("toastContainer");
  if (container) {
    container.appendChild(el);
    setTimeout(() => el.remove(), duration);
  }
};

// Plotly renderer
window.renderChart = function(containerId, figData) {
  const el = document.getElementById(containerId);
  if (!el || !figData) return;
  const config = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["sendDataToCloud"] };
  Plotly.react(el, figData.data, figData.layout, config);
};

// Fetch helper
window.api = async function(url, opts={}) {
  try {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    const data = await res.json();
    if (!res.ok) {
      toast(data.error || "Server error", "error");
      return null;
    }
    return data;
  } catch (e) {
    toast("Network error: " + e.message, "error");
    return null;
  }
};

// Loading state on button
window.withLoading = async function(btn, asyncFn) {
  const orig = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="width:14px;height:14px"></span> Loading…`;
  try { await asyncFn(); } finally {
    btn.disabled = false;
    btn.innerHTML = orig;
  }
};

// Format numbers
window.fmt = function(n, decimals=2) {
  if (n === null || n === undefined || isNaN(n)) return "—";
  if (typeof n === "number") {
    if (Math.abs(n) >= 1e6) return (n/1e6).toFixed(1)+"M";
    if (Math.abs(n) >= 1e3) return (n/1e3).toFixed(1)+"K";
    return n.toFixed(decimals).replace(/\.?0+$/, "");
  }
  return n;
};

// Render a simple table from array of objects
window.renderTable = function(containerId, rows, cols, opts={}) {
  const el = document.getElementById(containerId);
  if (!el || !rows) return;
  const maxRows = opts.maxRows || 200;
  const displayRows = rows.slice(0, maxRows);
  const headers = cols || (rows.length ? Object.keys(rows[0]) : []);
  let html = `<div class="table-wrap"><table><thead><tr>`;
  headers.forEach(h => { html += `<th>${h}</th>`; });
  html += `</tr></thead><tbody>`;
  displayRows.forEach((row, i) => {
    const ann = row._ann;
    const style = ann ? `style="border-left:3px solid ${ann.color||'#00D4FF'}"` : "";
    html += `<tr ${style}>`;
    headers.forEach(h => {
      if (h.startsWith("_")) return;
      let val = row[h];
      if (val === null || val === undefined) val = `<span class="text-muted">—</span>`;
      else if (typeof val === "number") val = fmt(val, 4);
      html += `<td>${val}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table></div>`;
  if (rows.length > maxRows) {
    html += `<div class="text-muted text-sm mt-1">Showing ${maxRows} of ${rows.length} rows</div>`;
  }
  el.innerHTML = html;
};

// Dataset info refresh
window.refreshDatasetInfo = async function() {
  const data = await api("/api/dataset-info");
  return data;
};

// Guard: check if dataset loaded, redirect if not
window.requireDataset = async function(onLoaded) {
  const data = await api("/api/dataset-info");
  if (!data || !data.loaded) {
    document.getElementById("noDataMsg")?.classList.remove("hidden");
    document.getElementById("mainArea")?.classList.add("hidden");
    return null;
  }
  document.getElementById("noDataMsg")?.classList.add("hidden");
  document.getElementById("mainArea")?.classList.remove("hidden");
  if (onLoaded) onLoaded(data);
  return data;
};

// Populate a select element with options
window.populateSelect = function(selectId, options, placeholder="Select…") {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = `<option value="">${placeholder}</option>`;
  options.forEach(opt => {
    const val = typeof opt === "string" ? opt : opt.value;
    const label = typeof opt === "string" ? opt : (opt.label || opt.value);
    sel.innerHTML += `<option value="${val}">${label}</option>`;
  });
};

// Column selector utilities
window.populateColSelects = function(data, ...ids) {
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const current = el.value;
    const type = el.dataset.type;
    let cols = data.columns;
    if (type === "numeric") cols = data.numeric_cols;
    else if (type === "categorical") cols = data.cat_cols;
    else if (type === "datetime") cols = data.date_cols;
    el.innerHTML = `<option value="">— Select —</option>`;
    cols.forEach(c => el.innerHTML += `<option value="${c}"${c===current?" selected":""}>${c}</option>`);
  });
};
