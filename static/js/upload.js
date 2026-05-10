/* ─── Upload page ─────────────────────────────────────────────────────────── */
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const fileInfo  = document.getElementById("fileInfo");

let selectedFile = null;

// Drag & drop
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const f = e.dataTransfer.files[0];
  if (f) setFile(f);
});
fileInput.addEventListener("change", () => fileInput.files[0] && setFile(fileInput.files[0]));

function setFile(f) {
  selectedFile = f;
  uploadBtn.disabled = false;
  fileInfo.classList.remove("hidden");
  fileInfo.textContent = `Selected: ${f.name} (${(f.size/1024/1024).toFixed(2)} MB)`;
  dropZone.querySelector(".upload-zone-title").textContent = f.name;
}

uploadBtn.addEventListener("click", () => withLoading(uploadBtn, doUpload));

async function doUpload() {
  if (!selectedFile) return;
  const fd = new FormData();
  fd.append("file", selectedFile);
  const chosenSep = document.getElementById("sepSel").value;
  fd.append("sep", chosenSep);
  fd.append("encoding", document.getElementById("encSel").value);
  try {
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) { toast(data.error || "Upload failed", "error"); return; }

    // Notify user if separator was auto-detected as something different
    const sepNames = { ",": "comma", ";": "semicolon", "|": "pipe", "\t": "tab" };
    if (data.detected_sep && data.detected_sep !== chosenSep) {
      const detected = sepNames[data.detected_sep] || data.detected_sep;
      toast(`Auto-detected separator: ${detected} — parsed ${data.cols} columns`, "info", 5000);
      // Sync the dropdown to show what was actually used
      const sel = document.getElementById("sepSel");
      for (const opt of sel.options) { if (opt.value === data.detected_sep) { opt.selected = true; break; } }
    } else {
      toast(`Loaded: ${data.rows.toLocaleString()} rows × ${data.cols} cols`, "success");
    }
    showPreview(data);
  } catch (e) {
    toast("Upload error: " + e.message, "error");
  }
}

function showPreview(data) {
  document.getElementById("previewArea").classList.remove("hidden");
  document.getElementById("previewTitle").textContent = data.filename;
  document.getElementById("previewStats").textContent =
    `${data.rows.toLocaleString()} rows · ${data.cols} columns`;

  renderTable("previewTable", data.preview, data.columns);

  // Types
  const tl = document.getElementById("typesList");
  tl.innerHTML = data.columns.map(c => {
    const t = data.col_types[c];
    const badge = { numeric:"badge-cyan", categorical:"badge-purple", datetime:"badge-green", bool:"badge-amber" }[t] || "badge-gray";
    const miss = data.missing[c];
    return `<div class="stat-row">
      <span class="stat-key">${c}</span>
      <div style="display:flex;gap:.4rem;align-items:center">
        <span class="badge ${badge}">${t}</span>
        ${miss ? `<span class="badge badge-red">${miss} missing</span>` : ""}
        <span class="mono text-xs text-muted">${data.dtypes[c]}</span>
      </div>
    </div>`;
  }).join("");

  // Missing
  const ml = document.getElementById("missingList");
  const hasMiss = Object.values(data.missing).some(v => v > 0);
  if (!hasMiss) {
    ml.innerHTML = `<div class="alert alert-success">No missing values found!</div>`;
  } else {
    ml.innerHTML = Object.entries(data.missing)
      .filter(([,v]) => v > 0)
      .sort((a,b) => b[1]-a[1])
      .map(([c, v]) => {
        const pct = ((v/data.rows)*100).toFixed(1);
        return `<div class="stat-row">
          <span class="stat-key">${c}</span>
          <div style="display:flex;align-items:center;gap:.75rem">
            <div class="progress-bar" style="width:120px">
              <div class="progress-bar-fill pink" style="width:${pct}%"></div>
            </div>
            <span class="mono text-xs">${v} (${pct}%)</span>
          </div>
        </div>`;
      }).join("");
  }

  // tab activation: first tab active
  document.querySelectorAll(".tab").forEach((t,i) => t.classList.toggle("active", i===0));
  document.querySelectorAll(".tab-panel").forEach((p,i) => p.classList.toggle("active", i===0));
}

// Sample datasets via seaborn/built-in
async function loadSample(name) {
  const btn = event.target;
  await withLoading(btn, async () => {
    const res = await fetch(`/api/sample/${name}`);
    if (!res.ok) { toast("Sample not available", "error"); return; }
    const data = await res.json();
    toast(`Loaded sample: ${data.rows} rows × ${data.cols} cols`, "success");
    showPreview(data);
  });
}

// Tab switching
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    const panel = document.querySelector(`[data-panel="${tab.dataset.tab}"]`);
    if (panel) panel.classList.add("active");
  });
});
