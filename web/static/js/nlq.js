/* ─── NLQ page ────────────────────────────────────────────────────────────── */
const EXAMPLE_QUERIES = [
  "show top 10 by first numeric column",
  "average of all numeric columns",
  "correlation between columns",
  "how many rows are there?",
  "show missing values",
  "distribution of first column",
  "minimum and maximum values",
  "count rows",
  "group by first categorical column",
];

async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const chips = document.getElementById("nlqChips");
  chips.innerHTML = EXAMPLE_QUERIES.map(q =>
    `<span class="nlq-chip" onclick="setQuery('${q}')">${q}</span>`
  ).join("");
}

function setQuery(q) {
  document.getElementById("nlqInput").value = q;
}

async function runQuery() {
  const q = document.getElementById("nlqInput").value.trim();
  if (!q) return toast("Enter a query", "error");
  const data = await api("/api/nlq/query", {
    method: "POST", body: JSON.stringify({ query: q })
  });
  if (!data) return;
  addToHistory(q, data);
  document.getElementById("nlqInput").value = "";
}

function addToHistory(query, result) {
  const history = document.getElementById("nlqHistory");
  const card = document.createElement("div");
  card.className = "card";

  let content = "";
  if (result.type === "scalar") {
    content = `<div class="kpi-card cyan" style="display:inline-block;margin:.5rem 0">
      <div class="kpi-value">${typeof result.value === "number" ? fmt(result.value, 6) : result.value}</div>
      <div class="kpi-label">${result.answer}</div>
    </div>`;
  } else if (result.type === "table") {
    content = `<p class="text-muted text-sm mb-1">${result.answer}</p>`;
    const tableDiv = document.createElement("div");
    tableDiv.id = `nlq-table-${Date.now()}`;
    card.innerHTML = `<div class="flex justify-between items-center mb-1">
      <span class="text-muted text-sm">❓ ${query}</span>
      <span class="badge badge-cyan">${result.type}</span>
    </div>` + content;
    card.appendChild(tableDiv);
    history.prepend(card);
    renderTable(tableDiv.id, result.data, result.cols);
    return;
  } else if (result.type === "chart") {
    const chartId = `nlq-chart-${Date.now()}`;
    content = `<p class="text-muted text-sm mb-1">${result.answer}</p><div id="${chartId}" style="min-height:300px"></div>`;
    card.innerHTML = `<div class="flex justify-between items-center mb-1">
      <span class="text-muted text-sm">❓ ${query}</span>
      <span class="badge badge-purple">chart</span>
    </div>` + content;
    history.prepend(card);
    if (result.fig) renderChart(chartId, result.fig);
    return;
  } else if (result.type === "correlation") {
    content = `<p class="text-muted text-sm mb-1">${result.answer}</p>` +
      result.pairs.map(p =>
        `<div class="stat-row"><span class="stat-key">${p.col1} × ${p.col2}</span>
         <span class="stat-val" style="color:${Math.abs(p.r) > 0.7 ? '#00D4FF' : '#94A3B8'}">${p.r}</span></div>`
      ).join("");
  } else if (result.type === "list") {
    content = `<p class="text-muted text-sm mb-1">${result.answer}</p>
      <div style="display:flex;flex-wrap:wrap;gap:.3rem">${result.values.map(v =>
        `<span class="badge badge-gray">${v}</span>`
      ).join("")}</div>`;
  } else {
    content = `<div class="alert alert-warn">${result.answer || result.error || "No result"}</div>`;
  }

  card.innerHTML = `<div class="flex justify-between items-center mb-1">
    <span class="text-muted text-sm">❓ ${query}</span>
    <span class="badge badge-${result.type === 'scalar' ? 'cyan' : 'purple'}">${result.type}</span>
  </div>` + content;
  history.prepend(card);
}

document.getElementById("nlqBtn").addEventListener("click", () =>
  withLoading(document.getElementById("nlqBtn"), runQuery));
document.getElementById("nlqInput").addEventListener("keydown", e => {
  if (e.key === "Enter") runQuery();
});

init();
