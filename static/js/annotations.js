/* ─── Annotations page ────────────────────────────────────────────────────── */
async function init() {
  await requireDataset(onLoaded);
}

async function onLoaded(info) {
  document.getElementById("annDataStats").textContent = `${info.rows.toLocaleString()} rows · ${info.cols} cols`;
  document.getElementById("annRow").max = info.rows - 1;
  await loadAnnotatedData();
  await loadAnnotations();
}

async function loadAnnotatedData() {
  const data = await api("/api/annotated-data");
  if (!data) return;
  renderTable("annTable", data.rows, data.columns);
}

async function loadAnnotations() {
  const data = await api("/api/annotations");
  if (!data) return;
  const ann = data.annotations;
  const count = Object.keys(ann).length;
  document.getElementById("annCount").textContent = count;
  const list = document.getElementById("annList");
  if (!count) {
    list.innerHTML = `<div class="text-muted text-sm">No annotations yet.</div>`;
    return;
  }
  list.innerHTML = Object.entries(ann).map(([row, a]) =>
    `<div class="card" style="padding:.6rem;border-left:3px solid ${a.color}">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span class="mono text-xs text-muted">Row ${row}</span>
          <span class="badge badge-purple" style="margin-left:.4rem">${a.tag}</span>
          <div class="text-sm mt-1">${a.note}</div>
        </div>
        <button class="btn btn-danger btn-sm" onclick="deleteAnnotation(${row})">✕</button>
      </div>
    </div>`
  ).join("");
}

async function saveAnnotation() {
  const row = document.getElementById("annRow").value;
  const note = document.getElementById("annNote").value.trim();
  const tag  = document.getElementById("annTag").value;
  const color= document.getElementById("annColor").value;
  if (!note) return toast("Enter a note", "error");
  const data = await api("/api/annotations", {
    method: "POST", body: JSON.stringify({ row: parseInt(row), note, tag, color })
  });
  if (data && data.ok) {
    toast("Annotation saved", "success");
    document.getElementById("annNote").value = "";
    await loadAnnotations();
    await loadAnnotatedData();
  }
}

async function deleteAnnotation(row) {
  const data = await api("/api/annotations", {
    method: "DELETE", body: JSON.stringify({ row })
  });
  if (data && data.ok) {
    toast("Annotation removed", "info");
    await loadAnnotations();
    await loadAnnotatedData();
  }
}

document.getElementById("annSaveBtn").addEventListener("click", saveAnnotation);
init();
