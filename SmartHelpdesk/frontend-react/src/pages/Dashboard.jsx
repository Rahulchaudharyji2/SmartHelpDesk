import { useState, useEffect } from "react";
import Chatbot from "../components/Chatbot";
import TicketForm from "../components/TicketForm";
import TicketList from "../components/TicketList";

export default function Dashboard() {
  const [refreshFlag, setRefreshFlag] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {}, 1000); // optional, can remove if not showing time
    return () => clearInterval(timer);
  }, []);

  const stats = [
    { label: 'My Tickets', value: '23' },
    { label: 'Late Tickets', value: '4' },
    { label: 'Incidents', value: '12' },
    { label: 'Assets', value: '156' }
  ];

  return (
    <div className="space-y-6 p-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="text-sm font-medium text-gray-500">{stat.label}</div>
            <div className="mt-1 text-2xl font-semibold text-gray-900">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium text-gray-900">Recent Tickets</h2>
                <p className="text-sm text-gray-500">Latest support requests</p>
              </div>
            </div>
            <div className="p-4">
              <TicketList refreshFlag={refreshFlag} />
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">AI Assistant</h2>
            </div>
            <Chatbot onTicketCreated={() => setRefreshFlag(f => f + 1)} />
          </div>
          <div className="bg-white rounded-lg shadow border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Quick Ticket</h2>
            </div>
            <div className="p-4">
              <TicketForm onCreated={() => setRefreshFlag(f => f + 1)} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
