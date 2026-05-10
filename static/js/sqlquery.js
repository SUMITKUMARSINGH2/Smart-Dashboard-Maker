/* ─── SQL Query page ──────────────────────────────────────────────────────── */
let lastResult = null;
let queryHistory = JSON.parse(localStorage.getItem("dvp_sql_history") || "[]");
let showingChart = false;
let schemaInfo = null;

async function init() {
  await requireDataset(onLoaded);
}

async function onLoaded(info) {
  schemaInfo = info;
  buildSchema(info);
  buildQuickQueries(info);
  renderHistory();
  // Default query
  if (!document.getElementById("sqlEditor").value.trim()) {
    document.getElementById("sqlEditor").value = "SELECT *\nFROM data\nLIMIT 10";
  }
}

function buildSchema(info) {
  const cols = info.columns || [];
  const types = info.dtypes || {};
  document.getElementById("schemaList").innerHTML = `
    <div style="font-size:.78rem;color:var(--text-dim);margin-bottom:.4rem">${cols.length} columns</div>
    ${cols.map(c => {
      const dt = types[c] || "unknown";
      const isNum = dt.includes("int") || dt.includes("float");
      const isDate = dt.includes("datetime") || dt.includes("date");
      const badge = isNum ? "badge-cyan" : isDate ? "badge-purple" : "badge-amber";
      const short = isNum ? "num" : isDate ? "date" : "str";
      return `<div style="display:flex;justify-content:space-between;align-items:center;padding:.25rem 0;border-bottom:1px solid var(--border2);cursor:pointer"
                   onclick="insertCol('${c}')" title="Click to insert">
        <span style="font-size:.83rem;color:var(--text)">${c}</span>
        <span class="badge ${badge}" style="font-size:.65rem">${short}</span>
      </div>`;
    }).join("")}
  `;
}

function buildQuickQueries(info) {
  const cols = info.columns || [];
  const numCols = info.numeric_cols || [];
  const col1 = cols[0] || "col";
  const num1 = numCols[0] || col1;
  const num2 = numCols[1] || num1;
  const queries = [
    { label: "First 10 rows", sql: `SELECT *\nFROM data\nLIMIT 10` },
    { label: "Row count", sql: `SELECT COUNT(*) AS total_rows\nFROM data` },
    { label: "Column stats", sql: `SELECT\n  COUNT(*) AS n,\n  AVG(${num1}) AS mean,\n  MIN(${num1}) AS min,\n  MAX(${num1}) AS max\nFROM data` },
    { label: "Null counts", sql: cols.slice(0,5).map(c => `SELECT '${c}' AS col, COUNT(*) - COUNT(${c}) AS nulls FROM data`).join("\nUNION ALL\n") },
    { label: `Top 10 by ${num1}`, sql: `SELECT *\nFROM data\nORDER BY ${num1} DESC\nLIMIT 10` },
    { label: `Distinct ${col1}`, sql: `SELECT DISTINCT ${col1}, COUNT(*) AS count\nFROM data\nGROUP BY ${col1}\nORDER BY count DESC\nLIMIT 20` },
    { label: "Summary stats", sql: numCols.slice(0,4).map(c =>
        `SELECT '${c}' AS col, ROUND(AVG(${c}),4) AS mean, ROUND(STDDEV(${c}),4) AS std, MIN(${c}) AS min, MAX(${c}) AS max FROM data`
      ).join("\nUNION ALL\n") },
    { label: `Correlation`, sql: `SELECT\n  ROUND(CORR(${num1}, ${num2}), 4) AS corr_${num1}_${num2}\nFROM data` },
  ];
  document.getElementById("quickQueries").innerHTML = queries.map(q =>
    `<button class="btn btn-ghost btn-sm" style="text-align:left;font-size:.78rem"
       onclick="setQuery(${JSON.stringify(q.sql)})">${q.label}</button>`
  ).join("");
}

function setQuery(sql) {
  document.getElementById("sqlEditor").value = sql;
  runQuery();
}

function insertCol(col) {
  const el = document.getElementById("sqlEditor");
  const pos = el.selectionStart;
  el.value = el.value.slice(0, pos) + col + el.value.slice(pos);
  el.focus();
  el.setSelectionRange(pos + col.length, pos + col.length);
}

async function runQuery() {
  const sql = document.getElementById("sqlEditor").value.trim();
  if (!sql) return toast("Enter a SQL query", "error");

  const errBox = document.getElementById("errBox");
  errBox.style.display = "none";
  document.getElementById("resultsCard").style.display = "none";

  const t0 = Date.now();
  const data = await api("/api/sql/query", {
    method: "POST",
    body: JSON.stringify({ sql })
  });
  const elapsed = Date.now() - t0;

  if (!data) return;

  if (data.error) {
    errBox.style.display = "block";
    errBox.innerHTML = `<strong>SQL Error:</strong> ${data.error}`;
    return;
  }

  lastResult = data;
  saveHistory(sql, data.rows?.length ?? 0, elapsed);

  // Row count + timing badges
  document.getElementById("rowCount").style.display = "inline";
  document.getElementById("rowCount").textContent = `${(data.rows?.length ?? 0).toLocaleString()} rows`;
  document.getElementById("execTime").style.display = "inline";
  document.getElementById("execTime").textContent = `${elapsed}ms`;

  renderResults(data);
}

function renderResults(data) {
  const card = document.getElementById("resultsCard");
  card.style.display = "block";

  if (!data.columns || !data.rows || data.rows.length === 0) {
    document.getElementById("resultsMsg").style.display = "block";
    document.getElementById("resultsMsg").textContent = "Query executed successfully — no rows returned.";
    document.getElementById("resultsTable").innerHTML = "";
    return;
  }

  document.getElementById("resultsMsg").style.display = "none";

  const cols = data.columns;
  const rows = data.rows;

  document.getElementById("resultsTable").innerHTML = `
    <table style="width:100%;border-collapse:collapse;font-size:.83rem">
      <thead>
        <tr>${cols.map(c => `<th style="padding:.4rem .6rem;text-align:left;background:var(--bg);color:var(--text-dim);font-weight:600;font-size:.75rem;border-bottom:1px solid var(--border);white-space:nowrap;position:sticky;top:0">${c}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${rows.map((r, i) => `<tr style="border-bottom:1px solid var(--border2);${i%2===0?'':'background:rgba(255,255,255,.02)'}">
          ${cols.map(c => `<td style="padding:.35rem .6rem;color:var(--text);white-space:nowrap;max-width:220px;overflow:hidden;text-overflow:ellipsis" title="${r[c] ?? ''}">${r[c] ?? '<span style="color:var(--text-dim);font-style:italic">null</span>'}</td>`).join("")}
        </tr>`).join("")}
      </tbody>
    </table>
  `;

  // Auto-chart if 2 columns and second is numeric
  if (cols.length === 2 && data.numeric_cols && data.numeric_cols.includes(cols[1])) {
    tryAutoChart(data);
  }
}

function tryAutoChart(data) {
  if (!data || !data.rows || data.rows.length < 2) return;
  const cols = data.columns;
  if (cols.length < 2) return;
  const xCol = cols[0];
  const yCol = cols[1];
  const xs = data.rows.map(r => r[xCol]);
  const ys = data.rows.map(r => parseFloat(r[yCol]));

  const fig = {
    data: [{ type: "bar", x: xs, y: ys, marker: { color: "#00D4FF" }, name: yCol }],
    layout: {
      paper_bgcolor: "#0D1528", plot_bgcolor: "#0D1528",
      font: { color: "#94A3B8", family: "Space Grotesk, sans-serif" },
      margin: { l: 40, r: 20, t: 30, b: 80 },
      xaxis: { gridcolor: "#1E293B", tickangle: -35 },
      yaxis: { gridcolor: "#1E293B" },
      title: { text: `${xCol} vs ${yCol}`, font: { color: "#E2E8F0", size: 14 } }
    }
  };
  document.getElementById("resultsChart").style.display = "block";
  document.getElementById("chartToggleBtn").textContent = "Hide Chart";
  showingChart = true;
  renderChart("resultsChart", fig);
}

// History
function saveHistory(sql, rows, elapsed) {
  const entry = { sql, rows, elapsed, ts: new Date().toLocaleTimeString() };
  queryHistory = [entry, ...queryHistory.filter(h => h.sql !== sql)].slice(0, 20);
  localStorage.setItem("dvp_sql_history", JSON.stringify(queryHistory));
  renderHistory();
}

function renderHistory() {
  if (!queryHistory.length) return;
  const card = document.getElementById("historyCard");
  card.style.display = "block";
  document.getElementById("historyList").innerHTML = queryHistory.map((h, i) => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:.3rem 0;border-bottom:1px solid var(--border2);cursor:pointer"
         onclick="loadFromHistory(${i})" title="${h.sql}">
      <span class="mono text-xs" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:340px;color:var(--text)">${h.sql.replace(/\n/g, " ")}</span>
      <span style="color:var(--text-dim);font-size:.7rem;white-space:nowrap;margin-left:.5rem">${h.rows} rows · ${h.ts}</span>
    </div>
  `).join("");
}

function loadFromHistory(i) {
  document.getElementById("sqlEditor").value = queryHistory[i].sql;
}

function clearHistory() {
  queryHistory = [];
  localStorage.removeItem("dvp_sql_history");
  document.getElementById("historyCard").style.display = "none";
}

// CSV download
function downloadCsv() {
  if (!lastResult || !lastResult.rows) return;
  const cols = lastResult.columns;
  const rows = lastResult.rows;
  const csv = [cols.join(","), ...rows.map(r => cols.map(c => {
    const v = r[c] ?? "";
    return String(v).includes(",") ? `"${v}"` : v;
  }).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "query_result.csv"; a.click();
  URL.revokeObjectURL(url);
}

// Format SQL (simple beautifier)
function formatSql() {
  const el = document.getElementById("sqlEditor");
  let sql = el.value.trim();
  const keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
                    "LIMIT", "OFFSET", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
                    "ON", "AND", "OR", "UNION ALL", "UNION", "WITH", "AS"];
  keywords.forEach(kw => {
    sql = sql.replace(new RegExp(`\\b${kw}\\b`, "gi"), "\n" + kw);
  });
  sql = sql.replace(/\n+/g, "\n").replace(/^\n/, "").trim();
  el.value = sql;
}

// Chart toggle
document.getElementById("chartToggleBtn").addEventListener("click", () => {
  const chart = document.getElementById("resultsChart");
  showingChart = !showingChart;
  chart.style.display = showingChart ? "block" : "none";
  document.getElementById("chartToggleBtn").textContent = showingChart ? "Hide Chart" : "Show Chart";
  if (showingChart && lastResult) tryAutoChart(lastResult);
});

document.getElementById("downloadCsvBtn").addEventListener("click", downloadCsv);
document.getElementById("clearBtn").addEventListener("click", () => {
  document.getElementById("sqlEditor").value = "";
  document.getElementById("resultsCard").style.display = "none";
  document.getElementById("errBox").style.display = "none";
  document.getElementById("rowCount").style.display = "none";
  document.getElementById("execTime").style.display = "none";
  lastResult = null;
});
document.getElementById("formatBtn").addEventListener("click", formatSql);
document.getElementById("runBtn").addEventListener("click", () =>
  withLoading(document.getElementById("runBtn"), runQuery));

// Ctrl+Enter shortcut
document.getElementById("sqlEditor").addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    withLoading(document.getElementById("runBtn"), runQuery);
  }
});

init();
