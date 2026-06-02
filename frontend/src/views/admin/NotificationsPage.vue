<script setup>
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, LayoutDashboard, Users, Ticket, Settings, LogOut, Bell,
  BarChart3, Building2, Check, X, CheckCheck, AlertCircle, Info, Calendar, Star
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

const notifs = ref([])
const loading = ref(true)
const unreadOnly = ref(false)

const fetchNotifs = async () => {
  loading.value = true
  try {
    const url = unreadOnly.value ? `${API}/notifications/?unread_only=true` : `${API}/notifications/`
    const res = await fetch(url, { headers })
    notifs.value = await res.json()
  } catch { notifs.value = [] }
  finally { loading.value = false }
}

const markRead = async (id) => {
  await fetch(`${API}/notifications/${id}/read`, { method: 'PATCH', headers })
  await fetchNotifs()
  refreshNotifs()
}

const markAllRead = async () => {
  await fetch(`${API}/notifications/read-all`, { method: 'PATCH', headers })
  await fetchNotifs()
  refreshNotifs()
}

const notifIcon = (type) => {
  const map = { new_ticket: 'text-primary bg-primary/10', status_change: 'text-accent-dark bg-accent/20', assignment: 'text-blue-600 bg-blue-50', reminder: 'text-warning bg-warning/10', feedback_request: 'text-star bg-star/10', evaluation: 'text-yellow-600 bg-yellow-50' }
  return map[type] || 'text-muted bg-gray-100'
}
const notifBg = (type) => {
  const map = { new_ticket: Ticket, status_change: AlertCircle, assignment: Users, reminder: Bell, feedback_request: MessageSquare, evaluation: Star }
  return map[type] || Bell
}

const unreadCount = () => notifs.value.filter(n => !n.is_read).length

const { unreadNotifs, refreshNotifs } = useNotifications()

onMounted(() => {
  fetchNotifs()
})
</script>

<template>
  <div class="min-h-screen bg-secondary flex">
    <aside :class="['fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-primary/5 flex flex-col transition-transform duration-300 lg:translate-x-0', sidebarOpen ? 'translate-x-0' : '-translate-x-full']">
      <div class="p-5 border-b border-primary/5">
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 gradient-bg rounded-lg flex items-center justify-center"><MessageSquare class="w-5 h-5 text-white" /></div>
          <div><span class="text-lg font-bold text-dark leading-tight">TICK'IN</span><span class="text-xs text-muted leading-tight -mt-0.5 block">Admin</span></div>
        </div>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/admin/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/admin/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Ticket class="w-4 h-4" /> Tickets</router-link>
        <router-link to="/admin/utilisateurs" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Users class="w-4 h-4" /> Utilisateurs</router-link>
        <router-link to="/admin/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold relative"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
        <router-link to="/admin/salles" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Building2 class="w-4 h-4" /> Salles</router-link>
        <router-link to="/admin/parametres" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Settings class="w-4 h-4" /> Paramètres</router-link>
      </nav>
      <div class="p-4 border-t border-primary/5">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-sm font-bold text-white">{{ user?.nom?.[0] || 'A' }}</div>
          <div class="flex-1 min-w-0"><p class="text-sm font-semibold text-dark truncate">{{ user?.nom || 'Admin' }}</p><p class="text-xs text-muted truncate">{{ user?.email }}</p></div>
        </div>
        <button @click="logout" class="flex items-center gap-2 w-full px-4 py-2 rounded-xl text-muted hover:bg-danger/5 hover:text-danger transition text-sm"><LogOut class="w-4 h-4" /> Déconnexion</button>
      </div>
    </aside>

    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/40 z-30 lg:hidden"></div>

    <div class="flex-1 flex flex-col min-h-screen">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-dark/5">
        <div class="flex items-center justify-between px-4 lg:px-8 h-16">
          <button @click="sidebarOpen = true" class="lg:hidden p-2 rounded-lg hover:bg-dark/5"><svg class="w-5 h-5 text-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
          <h1 class="text-lg font-bold text-dark">Notifications</h1>
          <div class="flex items-center gap-3">
            <button v-if="unreadCount() > 0" @click="markAllRead" class="text-xs text-primary hover:text-primary-dark font-semibold flex items-center gap-1"><CheckCheck class="w-3.5 h-3.5" /> Tout marquer lu</button>
          </div>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="flex justify-between items-center">
          <label class="flex items-center gap-2 text-sm text-muted cursor-pointer">
            <input type="checkbox" v-model="unreadOnly" @change="fetchNotifs" class="rounded border-dark/20 text-primary focus:ring-primary/30" />
            Non lues seulement
          </label>
          <span class="text-xs text-muted">{{ notifs.filter(n => !n.is_read).length }} non lue(s)</span>
        </div>

        <div class="space-y-3">
          <div v-for="n in notifs" :key="n.id" :class="['bg-white rounded-xl border p-4 flex items-start gap-4 transition card-hover', n.is_read ? 'border-primary/5' : 'border-primary/20 bg-primary/[0.02]']">
            <div :class="['w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center', notifIcon(n.type)]">
              <component :is="notifBg(n.type)" class="w-5 h-5" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p :class="['text-sm', n.is_read ? 'text-dark' : 'text-dark font-semibold']">{{ n.title }}</p>
                  <p v-if="n.message" class="text-xs text-muted mt-0.5">{{ n.message }}</p>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                  <span class="text-xs text-muted whitespace-nowrap">{{ new Date(n.created_at).toLocaleDateString('fr-FR') }}</span>
                  <button v-if="!n.is_read" @click="markRead(n.id)" class="p-1.5 rounded-lg text-muted hover:bg-primary/5 hover:text-primary transition" title="Marquer comme lue"><Check class="w-3.5 h-3.5" /></button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!loading && notifs.length === 0" class="text-center py-12 text-muted text-sm">Aucune notification</div>
          <div v-if="loading" class="text-center py-12"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></div>
        </div>
      </main>
    </div>
  </div>
</template>
