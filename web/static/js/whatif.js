/* ─── What-If Simulator page ──────────────────────────────────────────────── */
let colsInfo = [];

async function init() {
  await requireDataset(onLoaded);
}

async function onLoaded(info) {
  const data = await api("/api/whatif/info");
  if (!data) return;
  colsInfo = data.cols;
  buildSliders(data.cols);
}

function buildSliders(cols) {
  const container = document.getElementById("sliderContainer");
  container.innerHTML = cols.slice(0, 12).map(c => `
    <div style="margin-bottom:1rem">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.25rem">
        <span style="font-weight:600;font-size:.88rem">${c.col}</span>
        <span class="mono text-sm text-cyan" id="val_${c.col.replace(/\W/g,'_')}">×1.00</span>
      </div>
      <input type="range" id="slider_${c.col.replace(/\W/g,'_')}"
        min="0.1" max="3.0" step="0.05" value="1.0"
        data-col="${c.col}"
        style="width:100%;accent-color:var(--cyan)"
        oninput="onSliderChange(this)">
      <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--text-dim)">
        <span>0.1×</span>
        <span>Mean: <span class="mono">${fmt(c.mean)}</span></span>
        <span>3.0×</span>
      </div>
    </div>
  `).join("");
}

function onSliderChange(el) {
  const colKey = el.dataset.col.replace(/\W/g, '_');
  document.getElementById(`val_${colKey}`).textContent = `×${parseFloat(el.value).toFixed(2)}`;
}

function getAdjustments() {
  const adjustments = {};
  document.querySelectorAll("[id^='slider_']").forEach(el => {
    const col = el.dataset.col;
    const val = parseFloat(el.value);
    if (val !== 1.0) adjustments[col] = val;
  });
  return adjustments;
}

async function simulate() {
  const adjustments = getAdjustments();
  const data = await api("/api/whatif/simulate", {
    method: "POST",
    body: JSON.stringify({ adjustments })
  });
  if (!data) return;
  // Impact table
  const changed = data.stats.filter(s => Math.abs(s.delta_pct) > 0.001);
  document.getElementById("impactTable").innerHTML = changed.length ? `
    <div class="table-wrap"><table>
      <thead><tr><th>Column</th><th>Original Mean</th><th>Simulated Mean</th><th>Δ%</th><th>Sim. Sum</th></tr></thead>
      <tbody>${changed.map(s => `
        <tr>
          <td><strong>${s.col}</strong></td>
          <td class="mono">${fmt(s.orig_mean, 4)}</td>
          <td class="mono" style="color:var(--cyan)">${fmt(s.sim_mean, 4)}</td>
          <td class="mono" style="color:${s.delta_pct >= 0 ? 'var(--green)' : 'var(--red)'}">
            ${s.delta_pct >= 0 ? '+' : ''}${s.delta_pct}%
          </td>
          <td class="mono">${fmt(s.sim_sum, 2)}</td>
        </tr>
      `).join("")}</tbody>
    </table></div>
  ` : `<div class="alert alert-info">Move sliders away from 1.0 to see changes</div>`;
  if (data.fig) {
    document.getElementById("whatifChart").innerHTML = "";
    renderChart("whatifChart", data.fig);
  }
}

function resetAll() {
  document.querySelectorAll("[id^='slider_']").forEach(el => {
    el.value = "1.0";
    onSliderChange(el);
  });
  document.getElementById("impactTable").innerHTML = `<div class="text-muted text-sm">Run simulation to see results</div>`;
}

document.getElementById("simulateBtn").addEventListener("click", () =>
  withLoading(document.getElementById("simulateBtn"), simulate));
document.getElementById("resetSimBtn").addEventListener("click", resetAll);

init();
