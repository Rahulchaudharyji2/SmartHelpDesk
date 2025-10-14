import React, { useEffect, useState } from 'react'
import { listTickets } from './apiClient'

export default function TicketList({ refreshFlag }) {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const data = await listTickets(100)
      setTickets(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [refreshFlag])

  return (
    <div>
      <button onClick={load} disabled={loading} style={{ marginBottom: 8 }}>
        {loading ? 'Loading...' : 'Refresh'}
      </button>
      <div className="ticket-list">
        {tickets.map(t => (
          <div key={t.id} className="ticket-row">
            <span className="id">#{t.id}</span>
            <span className="pri badge">{t.priority}</span>
            <span className="subj">{t.subject}</span>
            <span className="cat badge">{t.category}</span>
            <span className="team">{t.assignee_team}</span>
            {t.assignee_user && <span className="badge">{t.assignee_user}</span>}
            <span className="status badge">{t.status}</span>
          </div>
        ))}
        {tickets.length === 0 && !loading && <p>No tickets yet.</p>}
      </div>
    </div>
  )
}