/* ─── Outliers page ───────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const sel = document.getElementById("outlierCol");
  sel.innerHTML = `<option value="">All numeric columns</option>` +
    info.numeric_cols.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function detect() {
  const method = document.getElementById("outlierMethod").value;
  const col    = document.getElementById("outlierCol").value;
  let url = `/api/outliers/detect?method=${method}`;
  if (col) url += `&col=${encodeURIComponent(col)}`;
  const data = await api(url);
  if (!data) return;
  if (data.fig) {
    document.getElementById("outlierChart").innerHTML = "";
    renderChart("outlierChart", data.fig);
  }
  const results = document.getElementById("outlierResults");
  results.innerHTML = `<div class="table-wrap"><table>
    <thead><tr><th>Column</th><th>Outliers</th><th>Percentage</th><th>Min</th><th>Max</th><th>Sample Outliers</th></tr></thead>
    <tbody>
    ${data.results.map(r => `
      <tr>
        <td>${r.col}</td>
        <td style="color:${r.n_outliers > 0 ? 'var(--pink)' : 'var(--green)'};font-weight:600">${r.n_outliers}</td>
        <td><span class="badge ${r.pct > 5 ? 'badge-red' : 'badge-green'}">${r.pct}%</span></td>
        <td class="mono">${fmt(r.lower, 4)}</td>
        <td class="mono">${fmt(r.upper, 4)}</td>
        <td class="mono text-xs text-muted">${r.sample.slice(0,5).map(v=>fmt(v,3)).join(", ")}</td>
      </tr>
    `).join("")}
    </tbody>
  </table></div>`;
}

document.getElementById("detectBtn").addEventListener("click", () =>
  withLoading(document.getElementById("detectBtn"), detect));

init();
