import React, { useEffect, useRef } from "react";

export default function MessageList({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-slate-400 mt-24">
          Upload documents and ask your first question.
        </div>
      )}

      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`max-w-3xl rounded-2xl px-4 py-3 whitespace-pre-wrap leading-relaxed ${
            msg.role === "user"
              ? "ml-auto bg-accent text-slate-900"
              : "bg-slate-800 text-slate-100"
          }`}
        >
          {msg.content}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
