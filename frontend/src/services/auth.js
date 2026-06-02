const API_URL = 'http://localhost:8000/api'

let wsDisconnectFn = null
export function setWsDisconnect(fn) { wsDisconnectFn = fn }

export const authService = {
  async login(login, password) {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password })
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Erreur de connexion')
    }
    const data = await res.json()
    const user = {
      id: data.user_id,
      role: data.role,
      nom: `${data.first_name} ${data.last_name}`,
      prenom: data.first_name,
      email: data.email,
    }
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(user))
    return data
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    if (wsDisconnectFn) wsDisconnectFn()
  },

  getToken() {
    return localStorage.getItem('token')
  },

  getUser() {
    try {
      const raw = localStorage.getItem('user')
      if (!raw || raw === 'undefined') return null
      return JSON.parse(raw)
    } catch {
      localStorage.removeItem('user')
      return null
    }
  },

  isAuthenticated() {
    return !!this.getToken()
  },

  getDashboardRoute() {
    const user = this.getUser()
    if (!user) return '/login'
    switch (user.role) {
      case 'admin': return '/admin/dashboard'
      case 'technicien': return '/technicien/dashboard'
      case 'etudiant': return '/etudiant/dashboard'
      default: return '/login'
    }
  }
}
