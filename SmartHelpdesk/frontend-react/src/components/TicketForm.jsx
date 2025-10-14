import React, { useState } from 'react'
import { createTicket } from './apiClient'

export default function TicketForm({ onCreated }) {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [urgency, setUrgency] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [kb, setKb] = useState([])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!subject || !body) {
      alert('Subject and description required')
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const payload = {
        subject,
        body,
        user_email: email || null,
        user_phone: phone || null,
        channel: 'web',
        urgency: urgency || null
      }
      const data = await createTicket(payload)
      setResult(data)
      setKb(data.kb_suggestions || [])
      onCreated?.()
      // reset some fields
      // setSubject('')
      // setBody('')
    } catch (err) {
      console.error(err)
      alert('Failed to create ticket')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Your email (optional)"
        value={email}
        onChange={e => setEmail(e.target.value)}
        type="email"
      />
      <input
        placeholder="Your phone (optional, +91...)"
        value={phone}
        onChange={e => setPhone(e.target.value)}
        type="tel"
      />
      <input
        placeholder="Subject"
        value={subject}
        onChange={e => setSubject(e.target.value)}
        required
      />
      <textarea
        rows={5}
        placeholder="Describe your issue"
        value={body}
        onChange={e => setBody(e.target.value)}
        required
      />
      <select value={urgency} onChange={e => setUrgency(e.target.value)}>
        <option value="">Urgency (optional)</option>
        <option value="low">low</option>
        <option value="medium">medium</option>
        <option value="high">high</option>
        <option value="critical">critical</option>
      </select>
      <button disabled={loading}>{loading ? 'Submitting...' : 'Submit'}</button>

      {result && (
        <div className="result">
          <p>
            Ticket #{result.ticket.id} created – Category:
            <span className="badge">{result.ticket.category}</span> Team:
            <span className="badge">{result.ticket.assignee_team}</span> Priority:
            <span className="badge">{result.ticket.priority}</span>
            {result.routing?.assignee_user && (
              <> Assignee: <span className="badge">{result.routing.assignee_user}</span></>
            )}
          </p>
          {kb.length > 0 && (
            <p className="kb">
              Suggestions: {kb.map(k => k.title).join(', ')}
            </p>
          )}
        </div>
      )}
    </form>
  )
}