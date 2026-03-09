const API_BASE =
  process.env.REACT_APP_API_URL ||
  `${window.location.origin.replace(/\/$/, "")}/api/v1`;

export async function createChat(title = "") {
  const response = await fetch(`${API_BASE}/chats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || null }),
  });
  if (!response.ok) throw new Error("Failed to create chat");
  return response.json();
}

export async function listChats() {
  const response = await fetch(`${API_BASE}/chats`);
  if (!response.ok) throw new Error("Failed to load chats");
  return response.json();
}

export async function listMessages(chatId) {
  const response = await fetch(`${API_BASE}/chats/${chatId}/messages`);
  if (!response.ok) throw new Error("Failed to load messages");
  return response.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Upload failed");
  }
  return response.json();
}

export async function streamMessage(chatId, content, onToken, onDone) {
  const response = await fetch(`${API_BASE}/chats/${chatId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, stream: true }),
  });

  if (!response.ok || !response.body) {
    throw new Error("Streaming request failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const event of events) {
      const line = event.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const payload = JSON.parse(line.replace("data: ", ""));
      if (payload.type === "token") onToken(payload.value);
      if (payload.type === "done") onDone(payload.sources || []);
    }
  }
}
