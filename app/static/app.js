const state = {
  sessionId: null,
  sessions: [],
  isSending: false,
};

const sessionsEl = document.querySelector("#sessions");
const messagesEl = document.querySelector("#messages");
const chatTitleEl = document.querySelector("#chat-title");
const formEl = document.querySelector("#chat-form");
const inputEl = document.querySelector("#message-input");
const sendButtonEl = document.querySelector("#send-button");
const newChatButtonEl = document.querySelector("#new-chat");
const refreshButtonEl = document.querySelector("#refresh-sessions");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString();
}

function shortSessionId(sessionId) {
  return sessionId ? sessionId.slice(0, 8) : "New chat";
}

function setSending(isSending) {
  state.isSending = isSending;
  inputEl.disabled = isSending;
  sendButtonEl.disabled = isSending;
  sendButtonEl.textContent = isSending ? "Sending" : "Send";
}

function renderSessions() {
  if (!state.sessions.length) {
    sessionsEl.innerHTML = '<p class="session-meta">No sessions yet.</p>';
    return;
  }

  sessionsEl.innerHTML = state.sessions
    .map((session) => {
      const isActive = session.session_id === state.sessionId;
      const title = session.last_user_message || session.session_id;
      const count = session.message_count ?? 0;
      const date = formatDate(session.last_activity);

      return `
        <button class="session ${isActive ? "active" : ""}" type="button" data-session-id="${escapeHtml(session.session_id)}">
          <span class="session-title">${escapeHtml(title)}</span>
          <span class="session-meta">${count} messages${date ? ` · ${escapeHtml(date)}` : ""}</span>
        </button>
      `;
    })
    .join("");
}

function renderMessages(messages) {
  if (!messages.length) {
    messagesEl.innerHTML = `
      <div class="empty-state">
        <h3>Ask the agent something.</h3>
        <p>Previous sessions appear on the left after messages are saved.</p>
      </div>
    `;
    return;
  }

  messagesEl.innerHTML = messages.map(renderMessage).join("");
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderMessage(message) {
  const role = message.role === "assistant" ? "assistant" : "user";
  const content = message.content ?? message.answer ?? "";
  const toolInfo = role === "assistant" ? renderToolInfo(message) : "";

  return `
    <article class="message ${role}">
      <div class="bubble">
        <span class="role">${role}</span>
        ${escapeHtml(content)}
        ${toolInfo}
      </div>
    </article>
  `;
}

function renderToolInfo(message) {
  const hasToolInfo =
    message.tool_used || message.tool_input || message.tool_output || message.tool_error;

  if (!hasToolInfo) {
    return "";
  }

  const rows = [
    ["Tool", message.tool_used],
    ["Input", message.tool_input],
    ["Output", message.tool_output],
    ["Error", message.tool_error],
  ].filter(([, value]) => value !== null && value !== undefined && value !== "");

  return `
    <div class="tool-info">
      <strong>Tool info</strong>
      ${rows
        .map(([label, value]) => {
          const className = label === "Error" ? ' class="tool-error"' : "";
          return `
            <details open>
              <summary${className}>${escapeHtml(label)}</summary>
              <pre>${escapeHtml(value)}</pre>
            </details>
          `;
        })
        .join("")}
    </div>
  `;
}

function showNotice(message) {
  const notice = document.createElement("div");
  notice.className = "notice";
  notice.textContent = message;
  messagesEl.appendChild(notice);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function loadSessions() {
  state.sessions = await fetchJson("/api/sessions");
  renderSessions();
}

async function loadSession(sessionId) {
  const history = await fetchJson(`/api/sessions/${encodeURIComponent(sessionId)}`);
  state.sessionId = history.session_id;
  chatTitleEl.textContent = `Session ${shortSessionId(state.sessionId)}`;
  renderMessages(history.messages || []);
  renderSessions();
}

function startNewChat() {
  state.sessionId = null;
  chatTitleEl.textContent = "New chat";
  renderMessages([]);
  renderSessions();
  inputEl.focus();
}

async function sendMessage(message) {
  const optimisticMessages = [{ role: "user", content: message }];
  if (state.sessionId) {
    const currentMessages = [...messagesEl.querySelectorAll(".message")];
    if (currentMessages.length) {
      messagesEl.insertAdjacentHTML("beforeend", renderMessage(optimisticMessages[0]));
    } else {
      renderMessages(optimisticMessages);
    }
  } else {
    renderMessages(optimisticMessages);
  }

  const payload = {
    message,
    session_id: state.sessionId,
  };

  const result = await fetchJson("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  state.sessionId = result.session_id;
  chatTitleEl.textContent = `Session ${shortSessionId(state.sessionId)}`;

  await loadSession(state.sessionId);
  await loadSessions();
}

sessionsEl.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-session-id]");
  if (!button) {
    return;
  }

  try {
    await loadSession(button.dataset.sessionId);
  } catch (error) {
    showNotice(`Could not load session: ${error.message}`);
  }
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = inputEl.value.trim();
  if (!message || state.isSending) {
    return;
  }

  inputEl.value = "";
  setSending(true);

  try {
    await sendMessage(message);
  } catch (error) {
    showNotice(`Message failed: ${error.message}`);
  } finally {
    setSending(false);
    inputEl.focus();
  }
});

newChatButtonEl.addEventListener("click", startNewChat);

refreshButtonEl.addEventListener("click", async () => {
  try {
    await loadSessions();
  } catch (error) {
    showNotice(`Could not refresh sessions: ${error.message}`);
  }
});

loadSessions().catch((error) => {
  showNotice(`Could not load sessions: ${error.message}`);
});
