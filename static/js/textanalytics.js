/* ─── Text Analytics page ─────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const sel = document.getElementById("textCol");
  const textCols = info.cat_cols.length ? info.cat_cols : info.columns;
  sel.innerHTML = `<option value="">— Select —</option>` +
    textCols.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function analyze() {
  const col = document.getElementById("textCol").value;
  if (!col) return toast("Select a text column", "error");
  const data = await api(`/api/text/analyze?col=${encodeURIComponent(col)}`);
  if (!data) return;
  document.getElementById("resultsArea").classList.remove("hidden");
  document.getElementById("textColStats").textContent =
    `${data.n_texts.toLocaleString()} texts · ${data.total_words.toLocaleString()} words · ${data.unique_words.toLocaleString()} unique`;
  // KPIs
  document.getElementById("textKpis").innerHTML = [
    { label: "Total Texts", val: data.n_texts.toLocaleString(), cls: "cyan" },
    { label: "Unique Words", val: data.unique_words.toLocaleString(), cls: "purple" },
    { label: "Avg Words/Text", val: data.avg_words, cls: "pink" },
    { label: "Avg Sentiment", val: `${data.sentiment.avg_polarity >= 0 ? '+' : ''}${data.sentiment.avg_polarity}`,
      cls: data.sentiment.avg_polarity >= 0.05 ? "green" : data.sentiment.avg_polarity <= -0.05 ? "pink" : "amber" },
  ].map(k => `<div class="kpi-card ${k.cls}"><div class="kpi-value">${k.val}</div><div class="kpi-label">${k.label}</div></div>`).join("");
  // Charts
  if (data.fig_freq) renderChart("freqChart", data.fig_freq);
  if (data.fig_sent) renderChart("sentHistChart", data.fig_sent);
  if (data.fig_pie) renderChart("sentPieChart", data.fig_pie);
  // Sentiment text
  const s = data.sentiment;
  document.getElementById("sentStats").innerHTML = `
    <div class="stat-row"><span class="stat-key">Positive texts</span><span class="stat-val" style="color:var(--green)">${s.positive} (${Math.round(s.positive/data.n_texts*100)}%)</span></div>
    <div class="stat-row"><span class="stat-key">Negative texts</span><span class="stat-val" style="color:var(--red)">${s.negative} (${Math.round(s.negative/data.n_texts*100)}%)</span></div>
    <div class="stat-row"><span class="stat-key">Neutral texts</span><span class="stat-val">${s.neutral} (${Math.round(s.neutral/data.n_texts*100)}%)</span></div>
    <div class="stat-row"><span class="stat-key">Avg Polarity</span><span class="stat-val mono">${s.avg_polarity} (−1=very negative, +1=very positive)</span></div>
    <div class="stat-row"><span class="stat-key">Avg Subjectivity</span><span class="stat-val mono">${s.avg_subjectivity} (0=objective, 1=subjective)</span></div>
  `;
  // Word cloud (separate call)
  loadWordCloud(col);
}

async function loadWordCloud(col) {
  document.getElementById("wordcloudContainer").innerHTML =
    `<div class="chart-placeholder"><span class="spinner"></span> Generating word cloud…</div>`;
  const data = await api(`/api/text/wordcloud?col=${encodeURIComponent(col)}`);
  if (data && data.image) {
    document.getElementById("wordcloudContainer").innerHTML =
      `<img src="${data.image}" style="max-width:100%;border-radius:8px;border:1px solid var(--border)">`;
  } else {
    document.getElementById("wordcloudContainer").innerHTML =
      `<div class="alert alert-warn">Word cloud unavailable (install wordcloud package)</div>`;
  }
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

document.getElementById("analyzeBtn").addEventListener("click", () =>
  withLoading(document.getElementById("analyzeBtn"), analyze));

init();
