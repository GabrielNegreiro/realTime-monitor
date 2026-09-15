const cpuValue = document.getElementById("cpu-value");
const ramValue = document.getElementById("ram-value");
const ramUsed = document.getElementById("ram-used");
const lastUpdate = document.getElementById("last-update");
const connectionStatus = document.getElementById("connection-status");
const statusDot = document.getElementById("status-dot");
const historyBody = document.getElementById("history-body");
const cpuCanvas = document.getElementById("cpu-chart");
const ramCanvas = document.getElementById("ram-chart");

const history = [];
const maxHistoryItems = 12;
const cpuPoints = [];
const ramPoints = [];

const charts = {
  cpu: {
    canvas: cpuCanvas,
    points: cpuPoints,
    color: "#246bfe",
    fill: "rgba(36, 107, 254, 0.12)",
  },
  ram: {
    canvas: ramCanvas,
    points: ramPoints,
    color: "#12876f",
    fill: "rgba(18, 135, 111, 0.12)",
  },
};

function formatBytes(value) {
  const gib = value / 1024 / 1024 / 1024;
  return `${gib.toFixed(2)} GB`;
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString("pt-BR");
}

function setConnected(connected) {
  connectionStatus.textContent = connected ? "Conectado" : "Desconectado";
  statusDot.classList.toggle("connected", connected);
  statusDot.classList.toggle("disconnected", !connected);
}

function resizeCanvas(canvas) {
  const pixelRatio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  canvas.width = width * pixelRatio;
  canvas.height = height * pixelRatio;

  const context = canvas.getContext("2d");
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  return { context, width, height };
}

function drawChart(chart) {
  const { context, width, height } = resizeCanvas(chart.canvas);
  const padding = 28;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  context.clearRect(0, 0, width, height);
  context.strokeStyle = "#d8e0ec";
  context.lineWidth = 1;
  context.font = "12px Arial";
  context.fillStyle = "#5d6b82";

  for (let i = 0; i <= 4; i += 1) {
    const y = padding + (chartHeight / 4) * i;
    const label = `${100 - i * 25}%`;
    context.beginPath();
    context.moveTo(padding, y);
    context.lineTo(width - padding, y);
    context.stroke();
    context.fillText(label, 4, y + 4);
  }

  if (chart.points.length === 0) {
    return;
  }

  const coordinates = chart.points.map((value, index) => {
    const x =
      chart.points.length === 1
        ? padding
        : padding + (chartWidth / (chart.points.length - 1)) * index;
    const y = padding + chartHeight - (Math.min(value, 100) / 100) * chartHeight;
    return { x, y };
  });

  context.beginPath();
  context.moveTo(coordinates[0].x, height - padding);
  for (const point of coordinates) {
    context.lineTo(point.x, point.y);
  }
  context.lineTo(coordinates[coordinates.length - 1].x, height - padding);
  context.closePath();
  context.fillStyle = chart.fill;
  context.fill();

  context.beginPath();
  coordinates.forEach((point, index) => {
    if (index === 0) {
      context.moveTo(point.x, point.y);
    } else {
      context.lineTo(point.x, point.y);
    }
  });
  context.strokeStyle = chart.color;
  context.lineWidth = 2;
  context.stroke();
}

function appendChartPoint(chart, value) {
  chart.points.push(value);

  if (chart.points.length > maxHistoryItems) {
    chart.points.shift();
  }

  drawChart(chart);
}

function updateHistoryTable() {
  historyBody.innerHTML = "";

  for (const item of history) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.time}</td>
      <td>${item.cpu.toFixed(1)}%</td>
      <td>${item.ram.toFixed(1)}%</td>
    `;
    historyBody.appendChild(row);
  }
}

function updateDashboard(metric) {
  const time = formatTime(metric.timestamp);

  cpuValue.textContent = `${metric.cpu_percent.toFixed(1)}%`;
  ramValue.textContent = `${metric.ram_percent.toFixed(1)}%`;
  ramUsed.textContent = `${formatBytes(metric.ram_used)} / ${formatBytes(metric.ram_total)}`;
  lastUpdate.textContent = time;

  history.unshift({
    time,
    cpu: metric.cpu_percent,
    ram: metric.ram_percent,
  });

  if (history.length > maxHistoryItems) {
    history.pop();
  }

  updateHistoryTable();
  appendChartPoint(charts.cpu, metric.cpu_percent);
  appendChartPoint(charts.ram, metric.ram_percent);
}

function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/metrics`);

  socket.addEventListener("open", () => setConnected(true));

  socket.addEventListener("message", (event) => {
    const metric = JSON.parse(event.data);
    updateDashboard(metric);
  });

  socket.addEventListener("close", () => {
    setConnected(false);
    setTimeout(connectWebSocket, 2000);
  });

  socket.addEventListener("error", () => {
    socket.close();
  });
}

setConnected(false);
drawChart(charts.cpu);
drawChart(charts.ram);
connectWebSocket();

window.addEventListener("resize", () => {
  drawChart(charts.cpu);
  drawChart(charts.ram);
});
