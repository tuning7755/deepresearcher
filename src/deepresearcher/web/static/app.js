const chatLog = document.getElementById("chatLog");
const activityLog = document.getElementById("activityLog");
const reportContent = document.getElementById("reportContent");
const reportMeta = document.getElementById("reportMeta");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const tabs = document.querySelectorAll(".tab");

let threadId = null;
let eventSource = null;
const toolCallNodes = new Map();

function setStatus(state) {
  const mapping = {
    idle: ["Idle", "#c7bdb4"],
    queued: ["Queued", "#f0b429"],
    running: ["Running", "#1f7a63"],
    complete: ["Complete", "#3a7bd5"],
    error: ["Error", "#d64545"],
  };
  const [label, color] = mapping[state] || ["Idle", "#c7bdb4"];
  statusText.textContent = label;
  statusDot.style.background = color;
}

function appendChat(message, role) {
  const bubble = document.createElement("div");
  bubble.className = `chat-message ${role}`;
  bubble.textContent = message;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function appendActivity(message) {
  const item = document.createElement("li");
  item.className = "activity-item";
  item.textContent = message;
  activityLog.appendChild(item);
  activityLog.scrollTop = activityLog.scrollHeight;
}

function appendToolCall({ tool, args, tool_call_id }) {
  const item = document.createElement("li");
  item.className = "activity-item tool-call-item";

  const details = document.createElement("details");
  details.className = "tool-call";

  const summary = document.createElement("summary");
  summary.textContent = `Tool call: ${tool}`;
  details.appendChild(summary);

  const argsBlock = document.createElement("pre");
  argsBlock.className = "tool-block";
  argsBlock.textContent = JSON.stringify(args ?? {}, null, 2);
  details.appendChild(argsBlock);

  const resultBlock = document.createElement("pre");
  resultBlock.className = "tool-block tool-result";
  resultBlock.textContent = "Awaiting result...";
  details.appendChild(resultBlock);

  item.appendChild(details);
  activityLog.appendChild(item);
  activityLog.scrollTop = activityLog.scrollHeight;

  if (tool_call_id) {
    toolCallNodes.set(tool_call_id, resultBlock);
  }
}

function appendToolResult({ tool_call_id, tool, content }) {
  if (tool_call_id && toolCallNodes.has(tool_call_id)) {
    const node = toolCallNodes.get(tool_call_id);
    node.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
    return;
  }
  appendActivity(`Tool result: ${tool}`);
}

function setReport(content, path) {
  if (path) {
    reportMeta.textContent = `Report output: ${path}`;
  }
  if (content) {
    reportContent.textContent = content;
  }
}

async function createSession() {
  const response = await fetch("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const data = await response.json();
  threadId = data.thread_id;
  connectStream();
}

function connectStream() {
  if (!threadId) {
    return;
  }
  if (eventSource) {
    eventSource.close();
  }
  eventSource = new EventSource(`/api/sessions/${threadId}/stream`);
  eventSource.addEventListener("chat", (event) => {
    const data = JSON.parse(event.data);
    appendChat(data.message, "agent");
  });
  eventSource.addEventListener("activity", (event) => {
    const data = JSON.parse(event.data);
    appendActivity(data.message);
  });
  eventSource.addEventListener("tool_call", (event) => {
    const data = JSON.parse(event.data);
    appendToolCall(data);
  });
  eventSource.addEventListener("tool_result", (event) => {
    const data = JSON.parse(event.data);
    appendToolResult(data);
  });
  eventSource.addEventListener("file", (event) => {
    const data = JSON.parse(event.data);
    appendActivity(`File output: ${data.name}`);
    if (data.content && data.name === "research_report.md") {
      setReport(data.content, data.path);
    }
  });
  eventSource.addEventListener("report", (event) => {
    const data = JSON.parse(event.data);
    setReport(data.content, data.path);
  });
  eventSource.addEventListener("status", (event) => {
    const data = JSON.parse(event.data);
    setStatus(data.state);
  });
}

async function sendMessage(message) {
  if (!threadId) {
    await createSession();
  }
  const response = await fetch(`/api/sessions/${threadId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: message }),
  });
  if (!response.ok) {
    const payload = await response.json();
    appendActivity(`Error: ${payload.detail || "Failed to send message"}`);
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) {
    return;
  }
  appendChat(message, "user");
  chatInput.value = "";
  await sendMessage(message);
});

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const target = tab.dataset.tab;
    tabs.forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`${target}Panel`).classList.add("active");
  });
});

setStatus("idle");
