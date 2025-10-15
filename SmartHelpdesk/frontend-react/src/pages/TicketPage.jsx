import React from "react";
import { useAuth } from "../context/AuthContext";
import Chatbot from "../components/Chatbot";
import TicketForm from "../components/TicketForm";
import { Navigate } from "react-router-dom";

export default function TicketPage() {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" />; // Only accessible if logged in

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-8 gap-6">
      <h1 className="text-3xl md:text-5xl font-bold text-[#03045e]">
        🎫 Support Tickets
      </h1>
      <div className="w-full max-w-4xl flex flex-col md:flex-row gap-6">
        <div className="flex-1">
          <Chatbot onTicketCreated={() => {}} />
        </div>
        <div className="flex-1">
          <TicketForm onCreated={() => {}} email={user.email} />
        </div>
      </div>
    </div>
  );
}
