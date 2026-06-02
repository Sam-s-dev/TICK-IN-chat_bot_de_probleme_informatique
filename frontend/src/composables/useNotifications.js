import { ref } from 'vue'
import { connectWs, disconnectWs, onWs } from '../services/websocket.js'
import { setWsDisconnect } from '../services/auth.js'

const API = 'http://localhost:8000/api'
const unreadNotifs = ref(0)
let initialized = false

function getToken() {
  try {
    const stored = localStorage.getItem('user')
    if (stored) {
      const u = JSON.parse(stored)
      return u.access_token || null
    }
  } catch {}
  return null
}

async function fetchUnreadCount() {
  const tok = getToken()
  if (!tok) return
  try {
    const res = await fetch(`${API}/notifications?unread_only=true`, {
      headers: { Authorization: `Bearer ${tok}` }
    })
    const data = await res.json()
    unreadNotifs.value = Array.isArray(data) ? data.length : 0
  } catch {}
}

export function useNotifications() {
  if (!initialized) {
    initialized = true
    setWsDisconnect(disconnectWs)
    const tok = getToken()
    if (tok) connectWs(tok)
    onWs('notification', () => fetchUnreadCount())
    onWs('new_message', () => fetchUnreadCount())
    fetchUnreadCount()
  }

  return { unreadNotifs, refreshNotifs: fetchUnreadCount }
}
