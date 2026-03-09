import { useEffect, useState } from "react";
import {
  createChat,
  listChats,
  listMessages,
  streamMessage,
  uploadDocument,
} from "../lib/api";

export function useChatApp() {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    (async () => {
      const allChats = await listChats();
      setChats(allChats);

      if (allChats.length > 0) {
        setCurrentChatId(allChats[0].id);
      } else {
        const chat = await createChat();
        setChats([chat]);
        setCurrentChatId(chat.id);
      }
    })().catch((err) => setStatus(err.message));
  }, []);

  useEffect(() => {
    if (!currentChatId) return;
    listMessages(currentChatId)
      .then(setMessages)
      .catch((err) => setStatus(err.message));
  }, [currentChatId]);

  const handleNewChat = async () => {
    const chat = await createChat();
    setChats((prev) => [chat, ...prev]);
    setCurrentChatId(chat.id);
    setMessages([]);
  };

  const handleSend = async () => {
    if (!input.trim() || !currentChatId || loading) return;

    const userText = input.trim();
    setInput("");
    setLoading(true);

    const tempUser = { id: `u-${Date.now()}`, role: "user", content: userText };
    const tempAssistantId = `a-${Date.now()}`;

    setMessages((prev) => [...prev, tempUser, { id: tempAssistantId, role: "assistant", content: "" }]);

    try {
      await streamMessage(
        currentChatId,
        userText,
        (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempAssistantId ? { ...m, content: `${m.content}${token}` } : m
            )
          );
        },
        async () => {
          const fresh = await listMessages(currentChatId);
          setMessages(fresh);
          const allChats = await listChats();
          setChats(allChats);
        }
      );
    } catch (err) {
      setStatus(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setStatus("");
    try {
      const result = await uploadDocument(file);
      setStatus(`Uploaded ${result.filename} (${result.chunks_added} chunks)`);
    } catch (err) {
      setStatus(err.message);
    } finally {
      setUploading(false);
    }
  };

  return {
    chats,
    currentChatId,
    setCurrentChatId,
    messages,
    input,
    setInput,
    loading,
    uploading,
    status,
    handleNewChat,
    handleSend,
    handleUpload,
  };
}
