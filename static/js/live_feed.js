/* ─── Live Feed page ──────────────────────────────────────────────────────── */
let fetchInterval = null;
let connected = false;

function setUrl(url) {
  document.getElementById("liveUrl").value = url;
}

function updateStatus(status, active) {
  document.getElementById("liveStatus").textContent = status;
  document.getElementById("liveDot").classList.toggle("active", active);
}

async function connect() {
  const url = document.getElementById("liveUrl").value.trim();
  const interval = parseInt(document.getElementById("liveInterval").value) || 30;
  if (!url) return toast("Enter a URL", "error");
  const data = await api("/api/live/connect", {
    method: "POST", body: JSON.stringify({ url, interval })
  });
  if (!data || !data.ok) return;
  connected = true;
  updateStatus("Connected", true);
  document.getElementById("connectBtn").disabled = true;
  document.getElementById("pauseBtn").disabled = false;
  document.getElementById("disconnectBtn").disabled = false;
  toast("Connected to live feed", "success");
  await doFetch();
  fetchInterval = setInterval(doFetch, interval * 1000);
}

async function doFetch() {
  const data = await api("/api/live/fetch");
  if (!data) return;
  if (data.paused) { updateStatus("Paused", false); return; }
  if (data.error) { updateStatus("Error: " + data.error, false); return; }
  document.getElementById("fetchCount").textContent = data.fetch_count;
  document.getElementById("rowCount").textContent = data.rows ? data.rows.length : 0;
  document.getElementById("lastFetch").textContent = "Last fetch: " + new Date(data.ts * 1000).toLocaleTimeString();
  updateStatus(`Live — fetch #${data.fetch_count}`, true);
  if (data.rows && data.rows.length) {
    const card = document.getElementById("liveDataCard");
    card.classList.remove("hidden");
    document.getElementById("liveDataStats").textContent = `${data.rows.length} rows · ${data.cols.length} cols`;
    renderTable("liveTable", data.rows, data.cols);
  }
}

async function togglePause() {
  const data = await api("/api/live/pause", { method: "POST", body: "{}" });
  if (!data) return;
  const btn = document.getElementById("pauseBtn");
  if (data.paused) {
    btn.textContent = "▶ Resume";
    updateStatus("Paused", false);
  } else {
    btn.textContent = "⏸ Pause";
    updateStatus("Live", true);
  }
}

async function disconnect() {
  clearInterval(fetchInterval);
  fetchInterval = null;
  connected = false;
  await api("/api/live/disconnect", { method: "POST", body: "{}" });
  updateStatus("Disconnected", false);
  document.getElementById("connectBtn").disabled = false;
  document.getElementById("pauseBtn").disabled = true;
  document.getElementById("disconnectBtn").disabled = true;
  document.getElementById("pauseBtn").textContent = "⏸ Pause";
  document.getElementById("fetchCount").textContent = "0";
  document.getElementById("rowCount").textContent = "—";
  document.getElementById("lastFetch").textContent = "Last fetch: —";
  document.getElementById("liveDataCard").classList.add("hidden");
  toast("Disconnected", "info");
}

document.getElementById("connectBtn").addEventListener("click", () =>
  withLoading(document.getElementById("connectBtn"), connect));
document.getElementById("pauseBtn").addEventListener("click", togglePause);
document.getElementById("disconnectBtn").addEventListener("click", disconnect);
