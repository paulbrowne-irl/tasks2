const status = document.querySelector("#status");
const taskList = document.querySelector("#task-list");

function showStatus(message, error = false) {
  status.textContent = message;
  status.dataset.error = error ? "true" : "false";
}

function renderTasks(tasks) {
  taskList.replaceChildren();
  if (!tasks.length) {
    taskList.innerHTML = "<p>No tasks found.</p>";
    return;
  }
  tasks.forEach((task) => {
    const row = document.createElement("div");
    row.className = "task";
    row.innerHTML = `<strong>${escapeHtml(task.category)}</strong><span>${escapeHtml(task.task_name)}</span><span>${escapeHtml(task.colour || "")}</span>`;
    taskList.append(row);
  });
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = sessionStorage.getItem("firebase_id_token");
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(path, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || "The request failed");
  return body;
}

async function refreshTasks() {
  const body = await request("/api/tasks");
  renderTasks(body.tasks || []);
  showStatus("Tasks refreshed.");
}

document.querySelector("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    await request("/api/tasks", { method: "POST", body: JSON.stringify({ category: form.get("category"), task_name: form.get("task_name") }) });
    event.currentTarget.reset();
    await refreshTasks();
    showStatus("Task added.");
  } catch (error) { showStatus(error.message, true); }
});

document.querySelector("#refresh-tasks").addEventListener("click", () => refreshTasks().catch((error) => showStatus(error.message, true)));
document.querySelector("#sort-colour").addEventListener("click", async () => {
  try { await request("/api/tasks/sort", { method: "POST" }); await refreshTasks(); showStatus("Tasks sorted by colour."); }
  catch (error) { showStatus(error.message, true); }
});
document.querySelector("#triage-sheets").addEventListener("click", async () => {
  try { const body = await request("/api/task-sheets/triage", { method: "POST" }); showStatus(body.status || "Task sheets organised."); }
  catch (error) { showStatus(error.message, true); }
});
