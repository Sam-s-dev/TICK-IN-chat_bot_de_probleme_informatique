<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, Ticket, Bell, Settings, LogOut, LayoutDashboard,
  Plus, Clock, CheckCircle, AlertCircle, ArrowRight, ListChecks, Building2,
  Monitor, ChevronRight, Star, BarChart3
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const headers = { Authorization: `Bearer ${authService.getToken()}`, 'Content-Type': 'application/json' }

const tickets = ref([])
const loading = ref(true)
const { unreadNotifs } = useNotifications()

const fetchDashboard = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API}/tickets?per_page=5`, { headers })
    const data = await res.json()
    tickets.value = data.tickets || data
  } catch { tickets.value = [] }
  finally { loading.value = false }
}

const stats = computed(() => {
  const total = tickets.value.length
  const encours = tickets.value.filter(t => [2, 3, 4].includes(t.status_id)).length
  const resolus = tickets.value.filter(t => t.status_id === 5).length
  return { total, encours, resolus }
})

const recentTickets = computed(() => tickets.value.slice(0, 4))

const statusLabel = (s) => ({ 1: 'Soumis', 2: 'En cours', 3: 'En attente', 4: 'En vérification', 5: 'Résolu' }[s] || s)
const statusColor = (s) => ({ 1: 'text-blue-600 bg-blue-50', 2: 'text-orange-600 bg-orange-50', 3: 'text-yellow-600 bg-yellow-50', 4: 'text-purple-600 bg-purple-50', 5: 'text-green-600 bg-green-50' }[s] || '')

let dashInterval

onMounted(() => {
  fetchDashboard()
  dashInterval = setInterval(fetchDashboard, 30000)
})

onBeforeUnmount(() => {
  clearInterval(dashInterval)
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
        <router-link to="/etudiant/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/etudiant/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Ticket class="w-4 h-4" /> Mes tickets</router-link>
        <router-link to="/etudiant/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm relative"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
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
          <h1 class="text-lg font-bold text-dark">Mon Espace</h1>
          <router-link to="/etudiant/tickets" class="gradient-bg text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition hover:shadow-lg"><Plus class="w-4 h-4" /> Nouveau signalement</router-link>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="bg-gradient-to-r from-primary to-primary-dark rounded-2xl p-6 lg:p-8 text-white">
          <h2 class="text-xl lg:text-2xl font-bold mb-1">Bienvenue, {{ user?.prenom || user?.nom || 'Étudiant' }}</h2>
          <p class="text-white/70 text-sm">TICK'IN — Gérez vos tickets et suivez l'état de vos signalements.</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-white rounded-xl p-5 border border-primary/5 card-hover">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center"><ListChecks class="w-5 h-5" /></div>
              <div><p class="text-xs text-muted font-medium">Total tickets</p><p class="text-2xl font-bold text-dark">{{ loading ? '...' : stats.total }}</p></div>
            </div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-primary/5 card-hover">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center"><Clock class="w-5 h-5" /></div>
              <div><p class="text-xs text-muted font-medium">En cours</p><p class="text-2xl font-bold text-dark">{{ loading ? '...' : stats.encours }}</p></div>
            </div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-primary/5 card-hover">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-green-50 text-green-600 flex items-center justify-center"><CheckCircle class="w-5 h-5" /></div>
              <div><p class="text-xs text-muted font-medium">Résolus</p><p class="text-2xl font-bold text-dark">{{ loading ? '...' : stats.resolus }}</p></div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-primary/5 overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4 border-b border-primary/5">
            <h3 class="font-semibold text-dark">Tickets récents</h3>
            <router-link to="/etudiant/tickets" class="text-xs text-primary font-medium flex items-center gap-1 hover:underline">Voir tout <ChevronRight class="w-3 h-3" /></router-link>
          </div>
          <div v-if="loading" class="p-8 text-center"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></div>
          <div v-else-if="recentTickets.length === 0" class="p-8 text-center text-muted text-sm">Aucun ticket pour le moment.</div>
          <div v-else>
            <router-link v-for="t in recentTickets" :key="t.id" :to="`/etudiant/tickets`" class="flex items-center justify-between px-5 py-3.5 border-b border-primary/5 hover:bg-primary/[0.02] transition last:border-b-0">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-8 h-8 rounded-lg bg-primary/5 flex items-center justify-center flex-shrink-0"><Ticket class="w-4 h-4 text-primary" /></div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-dark truncate">{{ t.description?.substring(0, 50) }}{{ t.description?.length > 50 ? '...' : '' }}</p>
                  <p class="text-xs text-muted mt-0.5">{{ t.ticket_number }}</p>
                </div>
              </div>
              <span :class="['inline-flex px-2.5 py-1 rounded-full text-xs font-medium flex-shrink-0', statusColor(t.status_id)]">{{ statusLabel(t.status_id) }}</span>
            </router-link>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
