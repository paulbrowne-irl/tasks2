// Browser-side task controls, API requests, and status rendering.

const status = document.querySelector("#status");
const taskList = document.querySelector("#task-list");

function showStatus(message, error = false) {
  // Display the latest success or error message for assistive technology and users.
  status.textContent = message;
  status.dataset.error = error ? "true" : "false";
}

function renderTasks(tasks) {
  // Replace the visible task list with the rows returned by the backend.
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
  // Escape spreadsheet values before inserting them into the page.
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
}

async function request(path, options = {}) {
  // Send an authenticated JSON request using the Firebase ID token in session storage.
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = sessionStorage.getItem("firebase_id_token");
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(path, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || "The request failed");
  return body;
}

async function refreshTasks() {
  // Fetch current rows and render them in the task list.
  const body = await request("/api/tasks");
  renderTasks(body.tasks || []);
  showStatus("Tasks refreshed.");
}

document.querySelector("#task-form").addEventListener("submit", async (event) => {
  // Submit a new category/task pair and refresh the displayed rows.
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
// Sort tasks by colour and then reload the visible data.
document.querySelector("#sort-colour").addEventListener("click", async () => {
  try { await request("/api/tasks/sort", { method: "POST" }); await refreshTasks(); showStatus("Tasks sorted by colour."); }
  catch (error) { showStatus(error.message, true); }
});
// Run task-sheet triage and show the returned operation status.
document.querySelector("#triage-sheets").addEventListener("click", async () => {
  try { const body = await request("/api/task-sheets/triage", { method: "POST" }); showStatus(body.status || "Task sheets organised."); }
  catch (error) { showStatus(error.message, true); }
});
