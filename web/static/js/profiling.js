/* ─── Profiling page ──────────────────────────────────────────────────────── */
let profileData = null;

async function loadProfile() {
  const info = await requireDataset();
  if (!info) return;
  const data = await api("/api/profile");
  if (!data) return;
  profileData = data;
  renderOverview(data);
  renderProfileGrid(data.profile);
}

function renderOverview(data) {
  const kpis = [
    { label: "Total Rows", val: data.total_rows.toLocaleString(), cls: "cyan" },
    { label: "Total Columns", val: data.total_cols, cls: "purple" },
    { label: "Duplicates", val: `${data.duplicates} (${data.dup_pct}%)`, cls: "pink" },
    { label: "Memory (MB)", val: data.memory_mb, cls: "green" },
  ];
  document.getElementById("overviewKpis").innerHTML = kpis.map(k =>
    `<div class="kpi-card ${k.cls}">
      <div class="kpi-value">${k.val}</div>
      <div class="kpi-label">${k.label}</div>
    </div>`
  ).join("");
}

function renderProfileGrid(profile) {
  const grid = document.getElementById("profileGrid");
  const search = document.getElementById("colSearch").value.toLowerCase();
  const typeFilter = document.getElementById("typeFilter").value;

  let filtered = profile;
  if (search) filtered = filtered.filter(p => p.col.toLowerCase().includes(search));
  if (typeFilter) {
    filtered = filtered.filter(p => {
      const dt = p.dtype;
      if (typeFilter === "numeric") return dt.includes("int") || dt.includes("float");
      if (typeFilter === "datetime") return dt.includes("datetime");
      if (typeFilter === "categorical") return dt.includes("object") || dt.includes("bool");
      return true;
    });
  }

  grid.innerHTML = filtered.map(p => {
    const isNum = p.mean !== undefined;
    const badge = isNum ? "badge-cyan" : p.dtype.includes("datetime") ? "badge-green" : "badge-purple";
    const typeLabel = isNum ? "numeric" : p.dtype.includes("datetime") ? "datetime" : "categorical";
    const missPct = p.missing_pct;

    return `<div class="profile-col" onclick="showDetail('${p.col}')">
      <div class="profile-col-header">
        <span class="profile-col-name">${p.col}</span>
        <span class="badge ${badge}">${typeLabel}</span>
        ${missPct > 0 ? `<span class="badge badge-red">${missPct}% missing</span>` : ""}
      </div>
      <div class="profile-col-stats">
        <div class="profile-stat">
          <span class="profile-stat-val">${p.unique.toLocaleString()}</span>
          <span class="profile-stat-lbl">Unique</span>
        </div>
        <div class="profile-stat">
          <span class="profile-stat-val">${p.missing.toLocaleString()}</span>
          <span class="profile-stat-lbl">Missing</span>
        </div>
        ${isNum ? `
        <div class="profile-stat">
          <span class="profile-stat-val">${fmt(p.mean)}</span>
          <span class="profile-stat-lbl">Mean</span>
        </div>
        <div class="profile-stat">
          <span class="profile-stat-val">${fmt(p.std)}</span>
          <span class="profile-stat-lbl">Std</span>
        </div>
        <div class="profile-stat">
          <span class="profile-stat-val">${fmt(p.min)}</span>
          <span class="profile-stat-lbl">Min</span>
        </div>
        <div class="profile-stat">
          <span class="profile-stat-val">${fmt(p.max)}</span>
          <span class="profile-stat-lbl">Max</span>
        </div>` : ""}
      </div>
      <div class="profile-mini-bar">
        <div class="profile-mini-bar-fill" style="width:${100-missPct}%"></div>
      </div>
    </div>`;
  }).join("");
}

function showDetail(colName) {
  if (!profileData) return;
  const p = profileData.profile.find(x => x.col === colName);
  if (!p) return;
  const card = document.getElementById("detailCard");
  card.classList.remove("hidden");
  document.getElementById("detailTitle").textContent = colName;
  const isNum = p.mean !== undefined;
  const stats = document.getElementById("detailStats");
  if (isNum) {
    stats.innerHTML = `
      <div class="stat-row"><span class="stat-key">Min</span><span class="stat-val">${fmt(p.min, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Max</span><span class="stat-val">${fmt(p.max, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Mean</span><span class="stat-val">${fmt(p.mean, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Median</span><span class="stat-val">${fmt(p.median, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Std Dev</span><span class="stat-val">${fmt(p.std, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Q25</span><span class="stat-val">${fmt(p.q25, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Q75</span><span class="stat-val">${fmt(p.q75, 6)}</span></div>
      <div class="stat-row"><span class="stat-key">Skewness</span><span class="stat-val">${fmt(p.skew, 4)}</span></div>
      <div class="stat-row"><span class="stat-key">Kurtosis</span><span class="stat-val">${fmt(p.kurt, 4)}</span></div>
      <div class="stat-row"><span class="stat-key">Zeros</span><span class="stat-val">${p.zeros}</span></div>
      <div class="stat-row"><span class="stat-key">Missing</span><span class="stat-val">${p.missing} (${p.missing_pct}%)</span></div>
      <div class="stat-row"><span class="stat-key">Unique</span><span class="stat-val">${p.unique}</span></div>
    `;
    if (p.hist) {
      const fig = {
        data: [{ type: "bar", x: p.hist.edges.slice(0,-1).map((v,i) => ((v+p.hist.edges[i+1])/2).toFixed(2)),
                 y: p.hist.counts, marker: { color: "#00D4FF" }, name: colName }],
        layout: { paper_bgcolor:"#0D1528", plot_bgcolor:"#0D1528",
                  font:{color:"#94A3B8"}, margin:{l:40,r:10,t:20,b:40},
                  xaxis:{gridcolor:"#1E293B"}, yaxis:{gridcolor:"#1E293B"} }
      };
      Plotly.react("detailChart", fig.data, fig.layout, { responsive: true, displaylogo: false });
    }
  } else {
    const rows = (p.top_values||[]).map(v =>
      `<div class="stat-row"><span class="stat-key">${v.value}</span><span class="stat-val">${v.count.toLocaleString()}</span></div>`
    ).join("");
    stats.innerHTML = `
      <div class="stat-row"><span class="stat-key">Missing</span><span class="stat-val">${p.missing} (${p.missing_pct}%)</span></div>
      <div class="stat-row"><span class="stat-key">Unique</span><span class="stat-val">${p.unique}</span></div>
      <div class="mt-1"><div class="text-muted text-xs mb-1">TOP VALUES</div>${rows}</div>
    `;
    if (p.top_values) {
      const fig = {
        data: [{ type: "bar", x: p.top_values.map(v=>v.value), y: p.top_values.map(v=>v.count),
                 marker: { color: "#7C3AED" } }],
        layout: { paper_bgcolor:"#0D1528", plot_bgcolor:"#0D1528",
                  font:{color:"#94A3B8"}, margin:{l:40,r:10,t:20,b:80},
                  xaxis:{gridcolor:"#1E293B"}, yaxis:{gridcolor:"#1E293B"} }
      };
      Plotly.react("detailChart", fig.data, fig.layout, { responsive: true, displaylogo: false });
    }
  }
  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

document.getElementById("colSearch").addEventListener("input", () => profileData && renderProfileGrid(profileData.profile));
document.getElementById("typeFilter").addEventListener("change", () => profileData && renderProfileGrid(profileData.profile));

loadProfile();
