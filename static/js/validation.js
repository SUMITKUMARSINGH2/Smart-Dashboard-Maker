/* ─── Data Validation page ────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

function onLoaded(info) {
  const sel = document.getElementById("valCol");
  sel.innerHTML = info.columns.map(c => `<option value="${c}">${c}</option>`).join("");
  loadRules();
}

function toggleRuleFields() {
  const type = document.getElementById("valRuleType").value;
  document.getElementById("rangeFields").classList.toggle("hidden", type !== "range");
  document.getElementById("patternFields").classList.toggle("hidden", type !== "pattern");
  document.getElementById("allowedFields").classList.toggle("hidden", type !== "allowed_values");
}

async function loadRules() {
  const data = await api("/api/validation/rules");
  if (!data) return;
  renderRules(data.rules);
}

function renderRules(rules) {
  document.getElementById("ruleCount").textContent = `${rules.length} rule${rules.length !== 1 ? 's' : ''}`;
  const checkBtn = document.getElementById("checkBtn");
  checkBtn.disabled = rules.length === 0;
  if (!rules.length) {
    document.getElementById("ruleList").innerHTML = `<div class="text-muted text-sm">No rules added yet.</div>`;
    return;
  }
  document.getElementById("ruleList").innerHTML = rules.map(r => `
    <div class="card mb-1" style="padding:.6rem;background:var(--bg);border-color:var(--border2)">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div>
          <div style="font-weight:600;font-size:.88rem">${r.label || r.col}</div>
          <div class="text-muted text-xs mt-1">
            <span class="badge badge-purple">${r.col}</span>
            <span class="badge badge-cyan" style="margin-left:.3rem">${r.rule_type}</span>
            ${r.not_null ? '<span class="badge badge-amber" style="margin-left:.3rem">not null</span>' : ''}
            ${r.rule_type === 'range' ? `<span class="text-muted" style="margin-left:.4rem">${r.min_val ?? '−∞'} → ${r.max_val ?? '+∞'}</span>` : ''}
            ${r.rule_type === 'pattern' ? `<span class="mono text-xs" style="margin-left:.4rem">${r.pattern}</span>` : ''}
            ${r.rule_type === 'allowed_values' ? `<span class="text-muted" style="margin-left:.4rem">[${(r.allowed_values||[]).join(', ')}]</span>` : ''}
          </div>
        </div>
        <button class="btn btn-danger btn-sm" onclick="deleteRule(${r.id})">✕</button>
      </div>
    </div>
  `).join("");
}

async function addRule() {
  const type = document.getElementById("valRuleType").value;
  const body = {
    col:       document.getElementById("valCol").value,
    rule_type: type,
    label:     document.getElementById("valLabel").value.trim(),
    not_null:  document.getElementById("valNotNull").checked,
    min_val:   type === "range" ? document.getElementById("valMin").value || null : null,
    max_val:   type === "range" ? document.getElementById("valMax").value || null : null,
    pattern:   type === "pattern" ? document.getElementById("valPattern").value : "",
    allowed_values: type === "allowed_values"
      ? document.getElementById("valAllowed").value.split(",").map(s => s.trim()).filter(Boolean)
      : [],
  };
  if (!body.col) return toast("Select a column", "error");
  const data = await api("/api/validation/rules", { method: "POST", body: JSON.stringify(body) });
  if (data && data.ok) {
    toast("Rule added", "success");
    document.getElementById("valLabel").value = "";
    document.getElementById("valMin").value = "";
    document.getElementById("valMax").value = "";
    document.getElementById("valPattern").value = "";
    document.getElementById("valAllowed").value = "";
    document.getElementById("valNotNull").checked = false;
    await loadRules();
  }
}

async function deleteRule(id) {
  const data = await api("/api/validation/rules", { method: "DELETE", body: JSON.stringify({ id }) });
  if (data && data.ok) { toast("Rule removed", "info"); await loadRules(); }
}

async function runCheck() {
  const data = await api("/api/validation/check", { method: "POST", body: "{}" });
  if (!data) return;
  document.getElementById("validationResults").classList.remove("hidden");
  // KPIs
  const passColor = data.total_violations === 0 ? "var(--green)" : "var(--pink)";
  document.getElementById("valSummaryKpis").innerHTML = `
    <div class="kpi-card ${data.total_violations === 0 ? 'green' : 'pink'}">
      <div class="kpi-value">${data.total_violations.toLocaleString()}</div>
      <div class="kpi-label">Total Violations</div>
    </div>
    <div class="kpi-card cyan">
      <div class="kpi-value">${data.rows_checked.toLocaleString()}</div>
      <div class="kpi-label">Rows Checked</div>
    </div>
  `;
  if (data.fig) renderChart("valChart", data.fig);
  // Detail table
  document.getElementById("valDetailTable").innerHTML = data.summary.map(s => `
    <div class="card mb-1" style="padding:.75rem;background:var(--bg);border-left:3px solid ${s.violations > 0 ? 'var(--red)' : 'var(--green)'}">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div style="font-weight:600">${s.rule}</div>
          <div class="text-muted text-xs">${s.col} · ${s.rule_type || ''}</div>
        </div>
        <div style="text-align:right">
          <span class="badge ${s.violations > 0 ? 'badge-red' : 'badge-green'}">${s.violations} violation${s.violations !== 1 ? 's' : ''}</span>
          <div class="text-xs text-muted mt-1">${s.pct}% of rows</div>
        </div>
      </div>
      ${s.error ? `<div class="alert alert-warn mt-1 text-xs">${s.error}</div>` : ''}
    </div>
  `).join("");
  if (data.total_violations === 0) {
    toast("All checks passed!", "success");
  } else {
    toast(`${data.total_violations} violation(s) found`, "error");
  }
}

document.getElementById("addRuleBtn").addEventListener("click", addRule);
document.getElementById("checkBtn").addEventListener("click", () =>
  withLoading(document.getElementById("checkBtn"), runCheck));

init();
