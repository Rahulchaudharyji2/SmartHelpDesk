import React, { useEffect, useState } from "react";
import { listTickets } from "../api/apiClient";

export default function TicketList({ refreshFlag }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await listTickets(100);
      setTickets(data || []);
    } catch (err) {
      console.error(err);
      setTickets([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [refreshFlag]);

  return (
    <div className="flex flex-col gap-3">
      {tickets.map((t) => (
        <div
          key={t.id}
          className="flex items-center gap-2 p-3 rounded-xl bg-gradient-to-r from-blue-50 via-white to-purple-50 border border-blue-50 shadow-sm"
        >
          <span className="bg-blue-100 text-blue-700 rounded px-2 py-0.5 text-xs font-bold">#{t.id}</span>
          <span className={`rounded px-2 py-0.5 text-xs font-semibold ${t.priority === "high"
              ? "bg-red-200 text-red-700"
              : t.priority === "medium"
                ? "bg-yellow-100 text-yellow-700"
                : "bg-purple-100 text-purple-700"
            }`}>{t.priority}</span>
          <span className="flex-1 font-medium text-gray-700">{t.subject}</span>
          <span className="bg-green-100 text-green-700 rounded px-2 py-0.5 text-xs">{t.category}</span>
          <span className="text-xs text-purple-700">{t.assignee_team}</span>
          {t.assignee_user && (
            <span className="bg-gray-200 text-xs rounded px-1">{t.assignee_user}</span>
          )}
          <span className={`rounded px-2 py-0.5 text-xs font-semibold 
            ${t.status === "open"
              ? "bg-green-200 text-green-800"
              : "bg-gray-200 text-gray-800"
            }`}>
            {t.status}
          </span>
        </div>
      ))}
      {tickets.length === 0 && !loading && (
        <p className="text-gray-500">No tickets yet.</p>
      )}
    </div>
  );
}