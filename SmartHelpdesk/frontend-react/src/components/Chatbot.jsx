import React, { useState } from 'react'
import { chatMessage } from './apiClient'

export default function Chatbot({ onTicketCreated }) {
  const [log, setLog] = useState([
    { role: 'bot', text: 'Hi! Ask about password reset, VPN, Outlook, printer… or type "create ticket".' }
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')

  async function send() {
    const text = input.trim()
    if (!text) return
    setLog(l => [...l, { role: 'user', text }])
    setInput('')
    setSending(true)
    try {
      const data = await chatMessage(text, email || null, phone || null)
      let reply = data.response
      if (data.ticket) {
        reply += ` Ticket #${data.ticket.id} created.`
        onTicketCreated?.()
      }
      setLog(l => [...l, { role: 'bot', text: reply }])
    } catch (err) {
      console.error(err)
      setLog(l => [...l, { role: 'bot', text: 'Error contacting server.' }])
    } finally {
      setSending(false)
    }
  }

  function onKey(e) { if (e.key === 'Enter') send() }

  return (
    <div className="chat-area">
      <div className="small-inputs">
        <input
          placeholder="Email (optional)"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          placeholder="Phone (optional)"
            value={phone}
            onChange={e => setPhone(e.target.value)}
        />
      </div>
      <div className="chat-log">
        {log.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>{m.text}</div>
        ))}
      </div>
      <div className="chat-controls">
        <input
          placeholder="Type your message"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKey}
          disabled={sending}
        />
        <button onClick={send} disabled={sending}>{sending ? '...' : 'Send'}</button>
      </div>
    </div>
  )
}