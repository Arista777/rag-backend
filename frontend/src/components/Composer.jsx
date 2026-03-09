import React from "react";

export default function Composer({ input, setInput, onSend, disabled }) {
  return (
    <form
      className="border-t border-slate-700 p-4 md:p-6"
      onSubmit={(e) => {
        e.preventDefault();
        onSend();
      }}
    >
      <div className="flex gap-3">
        <textarea
          className="flex-1 resize-none rounded-xl border border-slate-600 bg-slate-900 p-3 text-slate-100 outline-none focus:border-accent"
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          placeholder="Send a message..."
          disabled={disabled}
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="rounded-xl px-5 py-3 font-semibold bg-accent text-slate-900 disabled:opacity-40"
        >
          Send
        </button>
      </div>
    </form>
  );
}
