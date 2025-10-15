import React, { useState, useEffect, useRef } from "react";
import { chatMessage } from "../api/apiClient";
import { useAuth } from "../context/AuthContext";

export default function Chatbot({ onTicketCreated }) {
  const { user } = useAuth();
  const [log, setLog] = useState([
    {
      role: "bot",
      text: "👋 Hi! Ask about password reset, VPN, Outlook, printer… or type “create ticket”.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const chatEndRef = useRef();

  // Autofill email from logged-in user
  useEffect(() => {
    if (user?.email) setEmail(user.email);
  }, [user]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  async function send() {
    const text = input.trim();
    if (!text) return;
    setLog((l) => [...l, { role: "user", text }]);
    setInput("");
    setSending(true);
    try {
      const data = await chatMessage(text, email || null, phone || null);
      let reply = data.response;
      if (data.ticket) {
        reply += ` 🎉 Ticket #${data.ticket.id} created.`;
        onTicketCreated?.();
      }
      setLog((l) => [...l, { role: "bot", text: reply }]);
    } catch (err) {
      console.error(err);
      setLog((l) => [...l, { role: "bot", text: "❌ Error contacting server." }]);
    } finally {
      setSending(false);
    }
  }

  function onKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="bg-white shadow-xl rounded-2xl p-6 max-w-lg mx-auto border border-gray-200 flex flex-col gap-4">
      <h2 className="text-2xl font-bold text-[#03045e] mb-2 text-center">
        Chat with Support
      </h2>

      {/* Email & Phone */}
      <div className="flex gap-2">
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 flex-1 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 flex-1 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition"
          placeholder="Phone (optional)"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
      </div>

      {/* Chat log */}
      <div className="bg-[#e0f7fa] rounded-xl p-3 h-60 overflow-y-auto flex flex-col gap-2 border border-gray-200">
        {log.map((m, i) => (
          <div
            key={i}
            className={`py-2 px-3 rounded-xl max-w-[85%] shadow-sm break-words
              ${m.role === "user"
                ? "bg-[#023e8a] text-white ml-auto"
                : "bg-[#03045e] text-white mr-auto"
              }`}
          >
            {m.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <textarea
          className="border border-gray-300 rounded-lg px-3 py-2 flex-1 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition resize-none"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          disabled={sending}
          rows={1}
        />
        <button
          onClick={send}
          disabled={sending}
          className="bg-gradient-to-r from-[#023e8a] to-[#03045e] text-white px-5 py-2 rounded-xl font-semibold shadow hover:brightness-110 transition disabled:opacity-50"
        >
          {sending ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
