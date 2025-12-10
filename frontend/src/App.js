import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  // Poner el link de ngrok o localhost
  const BACKEND_URL = "https://unimprisonable-matteo-demurely.ngrok-free.dev";

  const sendMessage = async () => {
    if (!input) return;

    setMessages([...messages, { sender: "user", text: input }]);

    try {
      const res = await axios.post(`${BACKEND_URL}/chat`, { query: input });

      const botText = res.data.results.map(r => r.text).join("\n");

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: botText || "No hay respuesta" },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error al conectar con el backend" },
      ]);
      console.error(error);
    }

    setInput("");
  };

  return (
    <div className="App">
      <h1>RAG Chat Demo</h1>
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={msg.sender}>
            <b>{msg.sender === "user" ? "Tú" : "Bot"}:</b> {msg.text}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        placeholder="Escribe tu mensaje..."
      />
      <button onClick={sendMessage}>Enviar</button>
    </div>
  );
}

export default App;
