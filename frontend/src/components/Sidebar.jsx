import React from "react";

export default function Sidebar({ chats, currentChatId, onNewChat, onSelectChat }) {
  return (
    <aside className="w-full md:w-80 bg-slate-900/90 border-r border-slate-700 p-4">
      <button
        className="w-full rounded-xl bg-accent px-4 py-3 text-slate-950 font-semibold hover:brightness-110 transition"
        onClick={onNewChat}
      >
        + New Chat
      </button>

      <div className="mt-4 space-y-2 overflow-y-auto max-h-[70vh]">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`w-full text-left rounded-lg px-3 py-2 transition ${
              currentChatId === chat.id
                ? "bg-slate-700 text-white"
                : "bg-slate-800/70 text-slate-300 hover:bg-slate-700"
            }`}
          >
            <p className="truncate text-sm font-medium">{chat.title}</p>
          </button>
        ))}
      </div>
    </aside>
  );
}
