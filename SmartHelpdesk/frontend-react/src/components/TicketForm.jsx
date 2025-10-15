import React, { useState, useEffect } from "react";
import { createTicket } from "../api/apiClient";
import { useAuth } from "../context/AuthContext";

export default function TicketForm({ onCreated }) {
  const { user } = useAuth();
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [urgency, setUrgency] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [kb, setKb] = useState([]);

  useEffect(() => {
    if (user?.email) setEmail(user.email);
  }, [user]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!subject || !body) {
      alert("Subject and description required");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const payload = {
        subject,
        body,
        user_email: email || null,
        user_phone: phone || null,
        channel: "web",
        urgency: urgency || null,
      };
      const data = await createTicket(payload);
      setResult(data);
      setKb(data.kb_suggestions || []);
      onCreated?.();
    } catch (err) {
      console.error(err);
      alert("Failed to create ticket");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white shadow-xl rounded-2xl p-6 max-w-lg mx-auto border border-gray-200">
      <h2 className="text-2xl font-bold text-[#03045e] mb-4 text-center">Create a Ticket</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition"
          placeholder="Your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          type="email"
          required
        />
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition"
          placeholder="Your phone (optional, +91...)"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          type="tel"
        />
        <input
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition"
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
        />
        <textarea
          rows={4}
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition resize-none"
          placeholder="Describe your issue"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          required
        />
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#023e8a] focus:outline-none transition"
          value={urgency}
          onChange={(e) => setUrgency(e.target.value)}
        >
          <option value="">Urgency (optional)</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        <button
          disabled={loading}
          className="bg-gradient-to-r from-[#023e8a] to-[#03045e] text-white px-5 py-2 rounded-xl font-semibold shadow hover:brightness-110 transition disabled:opacity-50"
        >
          {loading ? "Submitting..." : "Submit Ticket"}
        </button>
      </form>

      {result && (
        <div className="mt-6 bg-[#e0f7fa] border-l-4 border-[#03045e] p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-[#03045e]">
            🎉 Ticket <span className="font-bold">#{result.ticket.id}</span> created
          </p>
          <p className="text-xs text-gray-700 mt-1">
            Category: <span className="font-medium">{result.ticket.category}</span> | 
            Team: <span className="font-medium">{result.ticket.assignee_team}</span> | 
            Priority: <span className="font-medium">{result.ticket.priority}</span>
            {result.routing?.assignee_user && (
              <> | Assignee: <span className="font-medium">{result.routing.assignee_user}</span></>
            )}
          </p>
          {kb.length > 0 && (
            <p className="text-gray-600 mt-2 text-sm">
              💡 Suggestions: {kb.map(k => k.title).join(", ")}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
