import React, { useState } from 'react'
import TicketForm from './components/TicketForm'
import TicketList from './components/TicketList'
import Chatbot from './components/Chatbot'

export default function App() {
  const [refreshFlag, setRefreshFlag] = useState(0)

  const onTicketCreated = () => {
    setRefreshFlag(f => f + 1)
  }

  return (
    <div className="layout">
      <header className="header">
        <h1>Smart Helpdesk (React)</h1>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Raise a Ticket</h2>
            <TicketForm onCreated={onTicketCreated} />
        </section>

        <section className="card">
          <h2>Self-Service Chatbot</h2>
          <Chatbot onTicketCreated={onTicketCreated} />
        </section>

        <section className="card wide">
          <h2>Recent Tickets</h2>
          <TicketList refreshFlag={refreshFlag} />
        </section>
      </main>
    </div>
  )
}