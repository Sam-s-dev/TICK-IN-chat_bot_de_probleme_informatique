<script setup>
import { ref, onMounted } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, LayoutDashboard, Ticket, Bell, Settings, LogOut,
  Check, CheckCheck, AlertCircle, Info, Calendar, Star
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const headers = { Authorization: `Bearer ${authService.getToken()}`, 'Content-Type': 'application/json' }

const notifications = ref([])
const loading = ref(true)
const filterUnread = ref(false)
const { unreadNotifs, refreshNotifs } = useNotifications()

const fetchNotifs = async () => {
  loading.value = true
  try {
    const url = filterUnread.value ? `${API}/notifications?unread_only=true` : `${API}/notifications/`
    const res = await fetch(url, { headers })
    notifications.value = await res.json()
  } catch { notifications.value = [] }
  finally { loading.value = false }
}

const markRead = async (id) => {
  await fetch(`${API}/notifications/${id}/read`, { method: 'PATCH', headers })
  const n = notifications.value.find(n => n.id === id)
  if (n) n.is_read = true
  refreshNotifs()
}

const markAllRead = async () => {
  await fetch(`${API}/notifications/read-all`, { method: 'PATCH', headers })
  notifications.value.forEach(n => n.is_read = true)
  refreshNotifs()
}

const unreadCount = () => notifications.value.filter(n => !n.is_read).length

const notifIcon = (type) => ({ status_change: Info, assignment: AlertCircle, reminder: AlertCircle, new_ticket: Bell, evaluation: Star }[type] || Bell)
const notifColor = (type) => ({ status_change: 'text-blue-600 bg-blue-50', assignment: 'text-purple-600 bg-purple-50', reminder: 'text-orange-600 bg-orange-50', new_ticket: 'text-primary bg-primary/10', evaluation: 'text-yellow-600 bg-yellow-50' }[type] || '')

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
          <div><span class="text-lg font-bold text-dark leading-tight">TICK'IN</span><span class="text-xs text-muted leading-tight -mt-0.5 block">Étudiant</span></div>
        </div>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/etudiant/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/etudiant/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Ticket class="w-4 h-4" /> Mes tickets</router-link>
        <router-link to="/etudiant/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold relative"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
        <router-link to="/etudiant/parametres" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Settings class="w-4 h-4" /> Paramètres</router-link>
      </nav>
      <div class="p-4 border-t border-primary/5">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-sm font-bold text-white">{{ user?.nom?.[0] || 'E' }}</div>
          <div class="flex-1 min-w-0"><p class="text-sm font-semibold text-dark truncate">{{ user?.nom || 'Étudiant' }}</p><p class="text-xs text-muted truncate">{{ user?.email }}</p></div>
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
          <div class="flex items-center gap-2">
            <button @click="markAllRead" v-if="unreadCount() > 0" class="text-xs text-primary font-medium flex items-center gap-1 hover:underline"><CheckCheck class="w-3.5 h-3.5" /> Tout marquer lu</button>
          </div>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="flex items-center justify-between">
          <label class="flex items-center gap-2 text-sm text-muted cursor-pointer">
            <input type="checkbox" v-model="filterUnread" @change="fetchNotifs" class="rounded border-dark/20 text-primary focus:ring-primary/30" />
            Non lues seulement
          </label>
          <span class="text-xs text-muted">{{ notifications.length }} notification(s){{ unreadCount() > 0 ? ` (${unreadCount()} non lue(s))` : '' }}</span>
        </div>

        <div v-if="loading" class="text-center py-12"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></div>
        <div v-else-if="notifications.length === 0" class="text-center py-12 text-muted text-sm">Aucune notification</div>
        <div v-else class="space-y-2">
          <div v-for="n in notifications" :key="n.id" @click="markRead(n.id)" :class="['flex items-start gap-3 p-4 rounded-xl border transition cursor-pointer', n.is_read ? 'bg-white border-primary/5' : 'bg-primary/[0.02] border-primary/10']">
            <div :class="['w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0', notifColor(n.type)]">
              <component :is="notifIcon(n.type)" class="w-4 h-4" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <p class="text-sm font-semibold text-dark">{{ n.title }}</p>
                <div class="flex items-center gap-1.5 flex-shrink-0">
                  <span v-if="!n.is_read" class="w-2 h-2 rounded-full bg-primary"></span>
                  <Calendar class="w-3 h-3 text-muted" />
                  <span class="text-xs text-muted whitespace-nowrap">{{ new Date(n.created_at).toLocaleDateString('fr-FR') }}</span>
                </div>
              </div>
              <p class="text-xs text-muted mt-0.5">{{ n.message }}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
