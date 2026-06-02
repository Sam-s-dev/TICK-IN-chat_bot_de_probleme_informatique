const WS_URL = 'ws://localhost:8000/api/ws'

let ws = null
let reconnectTimer = null
let listeners = {}
let authedToken = null

export function connectWs(token) {
  authedToken = token
  if (ws) disconnectWs()
  ws = new WebSocket(`${WS_URL}?token=${token}`)
  ws.onopen = () => {
    console.log('WS connected')
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
  }
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      const type = data.type
      if (listeners[type]) {
        listeners[type].forEach(fn => fn(data))
      }
      if (listeners['*']) {
        listeners['*'].forEach(fn => fn(data))
      }
    } catch { }
  }
  ws.onclose = () => {
    console.log('WS disconnected')
    ws = null
    if (authedToken) {
      reconnectTimer = setTimeout(() => connectWs(authedToken), 5000)
    }
  }
  ws.onerror = () => {
    ws?.close()
  }
}

export function disconnectWs() {
  authedToken = null
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
  if (ws) { ws.onclose = null; ws.close(); ws = null }
}

export function onWs(type, fn) {
  if (!listeners[type]) listeners[type] = []
  listeners[type].push(fn)
  return () => {
    listeners[type] = listeners[type].filter(f => f !== fn)
  }
}
