import React from "react";
import Sidebar from "./components/Sidebar";
import MessageList from "./components/MessageList";
import Composer from "./components/Composer";
import UploadButton from "./components/UploadButton";
import { useChatApp } from "./hooks/useChatApp";

function App() {
  const {
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
  } = useChatApp();

  return (
    <div className="min-h-screen flex flex-col md:flex-row text-slate-100">
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onSelectChat={setCurrentChatId}
      />

      <main className="flex-1 flex flex-col bg-slate-950/70 backdrop-blur-sm">
        <header className="border-b border-slate-700 p-4 md:px-8 flex items-center justify-between">
          <h1 className="text-lg font-semibold">AI Assistant</h1>
          <UploadButton onUpload={handleUpload} uploading={uploading} />
        </header>

        {status && (
          <div className="px-8 py-2 text-sm text-sky-300 border-b border-slate-800">{status}</div>
        )}

        <MessageList messages={messages} />
        <Composer input={input} setInput={setInput} onSend={handleSend} disabled={loading} />
      </main>
    </div>
  );
}

export default App;
