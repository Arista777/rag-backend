import React from "react";

export default function UploadButton({ onUpload, uploading }) {
  return (
    <label className="cursor-pointer rounded-lg border border-slate-600 px-3 py-2 text-sm hover:bg-slate-800 transition">
      {uploading ? "Uploading..." : "Upload Document"}
      <input
        type="file"
        className="hidden"
        accept=".pdf,.txt,.md"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onUpload(file);
          e.target.value = "";
        }}
      />
    </label>
  );
}
