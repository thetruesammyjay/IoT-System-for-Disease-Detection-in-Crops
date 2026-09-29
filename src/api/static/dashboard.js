"use strict";

const elements = Object.fromEntries(
  [
    "connection-dot", "connection-label", "error-banner", "monitoring-state",
    "monitoring-detail", "temperature", "humidity", "record-count", "cycle-count",
    "latest-disease", "latest-status", "latest-confidence", "latest-severity",
    "processing-time", "probabilities", "latest-time", "model-version",
    "detections-body", "monitor-toggle", "run-once", "last-updated",
    "temperature-line", "humidity-line", "temp-range", "humidity-range",
    "leaf-upload-form", "leaf-image", "leaf-dropzone", "leaf-placeholder",
    "leaf-preview", "leaf-file-name", "upload-status", "analyze-leaf",
    "upload-result", "upload-disease", "upload-confidence",
  ].map((id) => [id, document.getElementById(id)])
);

let monitoringRunning = false;
let monitoringAvailable = true;
let refreshing = false;
let selectedLeafFile = null;
let leafPreviewUrl = null;

const acceptedImageTypes = new Set(["image/jpeg", "image/png", "image/webp"]);
const maximumUploadBytes = Number(elements["leaf-image"].dataset.maxUploadBytes);
const maximumUploadMb = elements["leaf-image"].dataset.maxUploadMb;

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || `Request failed with status ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return payload;
}

function setConnection(connected) {
  elements["connection-dot"].className = `status-dot ${connected ? "connected" : "disconnected"}`;
  elements["connection-label"].textContent = connected ? "System online" : "System unavailable";
}

function showError(message) {
  elements["error-banner"].textContent = message;
  elements["error-banner"].hidden = !message;
}

function formatTime(value) {
  if (!value) return "--";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(new Date(value));
}

function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function rejectSelectedLeaf(message) {
  selectedLeafFile = null;
  elements["leaf-image"].value = "";
  if (leafPreviewUrl) URL.revokeObjectURL(leafPreviewUrl);
  leafPreviewUrl = null;
  elements["leaf-preview"].removeAttribute("src");
  elements["leaf-preview"].hidden = true;
  elements["leaf-placeholder"].hidden = false;
  elements["leaf-file-name"].textContent = "Choose a leaf photograph";
  elements["upload-status"].textContent = "No valid image selected";
  elements["analyze-leaf"].disabled = true;
  showError(message);
}

function setSelectedLeaf(file) {
  if (!acceptedImageTypes.has(file.type)) {
    rejectSelectedLeaf("Choose a JPEG, PNG, or WebP leaf image.");
    return;
  }
  if (file.size > maximumUploadBytes) {
    rejectSelectedLeaf(`Leaf images must not exceed ${maximumUploadMb} MB.`);
    return;
  }

  showError("");
  selectedLeafFile = file;
  if (leafPreviewUrl) URL.revokeObjectURL(leafPreviewUrl);
  leafPreviewUrl = URL.createObjectURL(file);
  elements["leaf-preview"].src = leafPreviewUrl;
  elements["leaf-preview"].hidden = false;
  elements["leaf-placeholder"].hidden = true;
  elements["leaf-file-name"].textContent = file.name;
  elements["upload-status"].textContent = "Ready for analysis";
  elements["analyze-leaf"].disabled = !monitoringAvailable;
  elements["upload-result"].className = "inspection-result";
  elements["upload-disease"].textContent = "Image selected";
  elements["upload-confidence"].textContent = "Run the model to inspect this leaf.";
}

function renderUploadResult(record) {
  const accepted = record.prediction_status === "accepted";
  elements["upload-result"].className = `inspection-result ${accepted ? "complete" : "uncertain"}`;
  elements["upload-disease"].textContent = record.disease_label;
  elements["upload-confidence"].textContent = accepted
    ? `${formatPercent(record.confidence)} confidence using ${record.model_version}.`
    : `Result below the acceptance threshold at ${formatPercent(record.confidence)} confidence.`;
}

function renderMonitoring(status) {
  monitoringAvailable = status !== null;
  if (!status) {
    monitoringRunning = false;
    elements["monitoring-state"].textContent = "Unavailable";
    elements["monitoring-detail"].textContent = "Monitoring is not configured";
    elements["cycle-count"].textContent = "No scheduler is available";
    elements["monitor-toggle"].disabled = true;
    elements["run-once"].disabled = true;
    elements["analyze-leaf"].disabled = true;
    return;
  }
  monitoringRunning = Boolean(status.running);
  elements["monitoring-state"].textContent = monitoringRunning ? "Running" : "Stopped";
  elements["monitoring-detail"].textContent = status.cycle_active
    ? "Classification cycle in progress"
    : `Every ${status.capture_interval_s}s`;
  elements["cycle-count"].textContent = `${status.cycles_completed} completed, ${status.cycles_failed} failed`;
  elements["monitor-toggle"].textContent = monitoringRunning ? "Stop monitoring" : "Start monitoring";
  elements["monitor-toggle"].className = `button ${monitoringRunning ? "button-danger" : "button-primary"}`;
}

function renderLatest(record) {
  if (!record) return;
  elements.temperature.textContent = `${Number(record.temperature_c).toFixed(1)} C`;
  elements.humidity.textContent = `${Number(record.humidity_pct).toFixed(1)}%`;
  elements["latest-disease"].textContent = record.disease_label;
  elements["latest-status"].textContent = record.prediction_status;
  elements["latest-status"].className = `pill pill-${record.prediction_status}`;
  elements["latest-confidence"].textContent = formatPercent(record.confidence);
  elements["latest-severity"].textContent = record.severity;
  elements["processing-time"].textContent = `${Number(record.processing_time_ms).toFixed(1)} ms`;
  elements["latest-time"].textContent = formatTime(record.captured_at);
  elements["model-version"].textContent = record.model_version;

  elements.probabilities.replaceChildren();
  Object.entries(record.probabilities)
    .sort((left, right) => right[1] - left[1])
    .forEach(([label, probability]) => {
      const row = document.createElement("div");
      row.className = "probability-item";
      const name = document.createElement("span");
      name.textContent = label;
      const track = document.createElement("div");
      track.className = "probability-track";
      const fill = document.createElement("div");
      fill.className = "probability-fill";
      fill.style.width = `${Math.max(0, Math.min(100, Number(probability) * 100))}%`;
      const value = document.createElement("span");
      value.className = "probability-value";
      value.textContent = formatPercent(probability);
      track.append(fill);
      row.append(name, track, value);
      elements.probabilities.append(row);
    });
}

function tableCell(value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  return cell;
}

function renderDetections(payload) {
  elements["record-count"].textContent = String(payload.pagination.total);
  elements["detections-body"].replaceChildren();
  if (!payload.items.length) {
    const row = document.createElement("tr");
    const cell = tableCell("No classifications have been stored yet");
    cell.colSpan = 6;
    cell.className = "empty-state";
    row.append(cell);
    elements["detections-body"].append(row);
    return;
  }
  payload.items.forEach((record) => {
    const row = document.createElement("tr");
    const statusCell = tableCell(record.prediction_status);
    statusCell.className = `table-status ${record.prediction_status}`;
    row.append(
      tableCell(formatTime(record.captured_at)),
      tableCell(record.disease_label),
      tableCell(formatPercent(record.confidence)),
      statusCell,
      tableCell(`${Number(record.temperature_c).toFixed(1)} C`),
      tableCell(`${Number(record.humidity_pct).toFixed(1)}%`)
    );
    elements["detections-body"].append(row);
  });
}

function renderLine(readings, key, lineId, rangeId, suffix) {
  const values = [...readings].reverse().map((item) => Number(item[key]));
  if (!values.length) {
    elements[lineId].setAttribute("points", "");
    elements[rangeId].textContent = "No readings";
    return;
  }
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const span = maximum - minimum || 1;
  const points = values.map((value, index) => {
    const x = values.length === 1 ? 150 : (index / (values.length - 1)) * 300;
    const y = 70 - ((value - minimum) / span) * 60;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  elements[lineId].setAttribute("points", points.join(" "));
  elements[rangeId].textContent = `${minimum.toFixed(1)}-${maximum.toFixed(1)}${suffix}`;
}

function renderSensors(payload) {
  renderLine(payload.items, "temperature_c", "temperature-line", "temp-range", " C");
  renderLine(payload.items, "humidity_pct", "humidity-line", "humidity-range", "%");
}

async function refreshDashboard() {
  if (refreshing) return;
  refreshing = true;
  try {
    const [health, monitoring, latest, detections, sensors] = await Promise.all([
      requestJson("/api/v1/system/health"),
      requestJson("/api/v1/monitoring/status").catch((error) => {
        if (error.status === 503) return null;
        throw error;
      }),
      requestJson("/api/v1/detections/latest").catch((error) => {
        if (error.status === 404) return null;
        throw error;
      }),
      requestJson("/api/v1/detections?limit=8"),
      requestJson("/api/v1/sensors/history?limit=20"),
    ]);
    setConnection(health.status === "ok");
    renderMonitoring(monitoring);
    renderLatest(latest);
    renderDetections(detections);
    renderSensors(sensors);
    elements["last-updated"].textContent = new Date().toLocaleTimeString();
    showError(monitoring?.last_error || "");
  } catch (error) {
    setConnection(false);
    showError(error instanceof Error ? error.message : "Dashboard refresh failed");
  } finally {
    refreshing = false;
  }
}

async function withDisabledButtons(action) {
  elements["monitor-toggle"].disabled = true;
  elements["run-once"].disabled = true;
  showError("");
  try {
    await action();
    await refreshDashboard();
  } catch (error) {
    showError(error instanceof Error ? error.message : "Action failed");
  } finally {
    elements["monitor-toggle"].disabled = !monitoringAvailable;
    elements["run-once"].disabled = !monitoringAvailable;
  }
}

elements["monitor-toggle"].addEventListener("click", () => withDisabledButtons(async () => {
  const endpoint = monitoringRunning ? "stop" : "start";
  await requestJson(`/api/v1/monitoring/${endpoint}`, { method: "POST" });
}));

elements["run-once"].addEventListener("click", () => withDisabledButtons(async () => {
  await requestJson("/api/v1/inference/trigger", { method: "POST" });
}));

elements["leaf-image"].addEventListener("change", (event) => {
  const [file] = event.target.files;
  if (file) setSelectedLeaf(file);
});

["dragenter", "dragover"].forEach((eventName) => {
  elements["leaf-dropzone"].addEventListener(eventName, (event) => {
    event.preventDefault();
    elements["leaf-dropzone"].classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  elements["leaf-dropzone"].addEventListener(eventName, (event) => {
    event.preventDefault();
    elements["leaf-dropzone"].classList.remove("dragging");
  });
});

elements["leaf-dropzone"].addEventListener("drop", (event) => {
  const [file] = event.dataTransfer.files;
  if (file) setSelectedLeaf(file);
});

elements["leaf-upload-form"].addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedLeafFile) {
    showError("Choose a leaf image before starting the analysis.");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedLeafFile, selectedLeafFile.name);
  elements["analyze-leaf"].disabled = true;
  elements["analyze-leaf"].textContent = "Analyzing...";
  elements["upload-status"].textContent = "Running the disease model";
  showError("");

  try {
    const result = await requestJson("/api/v1/inference/upload", {
      method: "POST",
      body: formData,
    });
    renderUploadResult(result);
    renderLatest(result);
    elements["upload-status"].textContent = "Analysis complete";
    await refreshDashboard();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Leaf analysis failed";
    showError(message);
    elements["upload-status"].textContent = "Analysis did not complete";
  } finally {
    elements["analyze-leaf"].disabled = !monitoringAvailable;
    elements["analyze-leaf"].textContent = "Analyze leaf";
  }
});

refreshDashboard();
window.setInterval(refreshDashboard, 3000);
