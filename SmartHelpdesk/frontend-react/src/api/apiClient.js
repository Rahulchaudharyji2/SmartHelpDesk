import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const api = axios.create({
  baseURL: apiBase,
  timeout: 15000
})

export async function createTicket(payload) {
  const { data } = await api.post('/tickets/ingest', payload)
  return data
}

export async function listTickets(limit = 50) {
  const { data } = await api.get('/tickets', { params: { limit } })
  return data
}

export async function chatMessage(message, user_email, user_phone) {
  const { data } = await api.post('/chat', { message, user_email, user_phone })
  return data
}