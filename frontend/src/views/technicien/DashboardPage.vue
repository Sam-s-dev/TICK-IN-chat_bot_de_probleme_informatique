<script setup>
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useNotifications } from '../../composables/useNotifications.js'
import { MessageSquare, Ticket, LogOut, Bell, CheckCircle, Clock, Wrench, ChevronRight } from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const logout = () => { authService.logout(); router.push('/login') }
const sidebarOpen = ref(false)

const API = 'http://localhost:8000/api'
const headers = { Authorization: `Bearer ${authService.getToken()}`, 'Content-Type': 'application/json' }

const loading = ref(true)
const stats = ref({ encours: 0, en_attente: 0, resolus_aujourdhui: 0, total_assignes: 0, tickets: [] })
const { unreadNotifs } = useNotifications()

const statusLabel = (sid) => ({ 1: 'Soumis', 2: 'Assigné', 3: 'En cours', 4: 'En attente', 5: 'Résolu' }[sid] || '')
const statusColor = (sid) => ({ 1: 'bg-yellow-50 text-yellow-600', 2: 'bg-blue-50 text-blue-600', 3: 'bg-indigo-50 text-indigo-600', 4: 'bg-orange-50 text-orange-600', 5: 'bg-accent/20 text-accent-dark' }[sid] || '')

const fetchStats = async () => {
  try {
    const res = await fetch(`${API}/tickets/my-stats`, { headers })
    if (res.ok) stats.value = await res.json()
  } catch {}
  finally { loading.value = false }
}

let statsInterval

onMounted(() => {
  fetchStats()
  statsInterval = setInterval(fetchStats, 30000)
})

onBeforeUnmount(() => {
  clearInterval(statsInterval)
})
</script>

<template>
  <div class="min-h-screen bg-secondary flex">
    <aside :class="['fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-primary/5 flex flex-col transition-transform duration-300 lg:translate-x-0', sidebarOpen ? 'translate-x-0' : '-translate-x-full']">
      <div class="p-5 border-b border-primary/5">
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 gradient-bg rounded-lg flex items-center justify-center"><MessageSquare class="w-5 h-5 text-white" /></div>
          <div><span class="text-lg font-bold text-dark leading-tight">TICK'IN</span><span class="text-xs text-muted leading-tight -mt-0.5 block">Technicien</span></div>
        </div>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/technicien/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Ticket class="w-4 h-4" /> Mes tickets</router-link>
        <router-link to="/technicien/notifications" class="relative flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Bell class="w-4 h-4" /> Notifications<span class="ml-auto w-5 h-5 bg-danger rounded-full text-[10px] text-white font-bold flex items-center justify-center">{{ unreadNotifs }}</span></router-link>
      </nav>
      <div class="p-4 border-t border-primary/5">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-sm font-bold text-white">{{ user?.nom?.[0] || 'T' }}</div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-dark truncate">{{ user?.nom || 'Technicien' }}</p>
            <p class="text-xs text-muted truncate">{{ user?.email }}</p>
          </div>
        </div>
        <button @click="logout" class="flex items-center gap-2 w-full px-4 py-2 rounded-xl text-muted hover:bg-danger/5 hover:text-danger transition text-sm"><LogOut class="w-4 h-4" /> Déconnexion</button>
      </div>
    </aside>
    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/40 z-30 lg:hidden"></div>

    <div class="flex-1 flex flex-col min-h-screen">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-dark/5">
        <div class="flex items-center justify-between px-4 lg:px-8 h-16">
          <button @click="sidebarOpen = true" class="lg:hidden p-2 rounded-lg hover:bg-dark/5"><svg class="w-5 h-5 text-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
          <h1 class="text-lg font-bold text-dark">Espace Technicien</h1>
          <div class="relative"><Bell class="w-5 h-5 text-muted hover:text-dark cursor-pointer transition" /><span class="absolute -top-1 -right-1 w-4 h-4 bg-danger rounded-full text-[10px] text-white font-bold flex items-center justify-center">{{ unreadNotifs }}</span></div>
        </div>
      </header>
      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div v-if="loading" class="text-center py-12"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></div>
        <template v-else>
          <div class="grid sm:grid-cols-3 gap-4 lg:gap-6">
            <div class="bg-white rounded-xl p-5 card-hover border border-primary/5">
              <div class="flex items-center justify-between mb-4">
                <span class="text-sm text-muted font-medium">En cours</span>
                <div class="w-10 h-10 rounded-xl bg-warning/10 flex items-center justify-center"><Wrench class="w-5 h-5 text-warning" /></div>
              </div>
              <p class="text-2xl font-bold text-dark">{{ stats.encours }}</p>
            </div>
            <div class="bg-white rounded-xl p-5 card-hover border border-primary/5">
              <div class="flex items-center justify-between mb-4">
                <span class="text-sm text-muted font-medium">En attente</span>
                <div class="w-10 h-10 rounded-xl bg-danger/10 flex items-center justify-center"><Clock class="w-5 h-5 text-danger" /></div>
              </div>
              <p class="text-2xl font-bold text-dark">{{ stats.en_attente }}</p>
            </div>
            <div class="bg-white rounded-xl p-5 card-hover border border-primary/5">
              <div class="flex items-center justify-between mb-4">
                <span class="text-sm text-muted font-medium">Résolus aujourd'hui</span>
                <div class="w-10 h-10 rounded-xl bg-accent/20 flex items-center justify-center"><CheckCircle class="w-5 h-5 text-accent-dark" /></div>
              </div>
              <p class="text-2xl font-bold text-dark">{{ stats.resolus_aujourdhui }}</p>
            </div>
          </div>
          <div class="bg-white rounded-xl p-6 lg:p-8 border border-primary/5" data-aos="fade-up">
            <h2 class="text-xl font-bold text-dark mb-2">Bienvenue, {{ user?.nom || 'Technicien' }}</h2>
            <p class="text-muted text-sm">Vous êtes connecté en tant que <strong class="text-primary">technicien</strong>. Consultez et gérez les tickets qui vous sont assignés.</p>
          </div>
          <div class="bg-white rounded-xl p-6 border border-primary/5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-dark">Tickets assignés</h3>
              <router-link to="/technicien/tickets" class="text-xs text-primary font-medium flex items-center gap-1 hover:underline">Voir tout <ChevronRight class="w-3 h-3" /></router-link>
            </div>
            <div v-if="stats.tickets.length === 0" class="text-center py-8 text-muted text-sm">Aucun ticket assigné pour le moment</div>
            <div v-else class="space-y-3">
              <div v-for="t in stats.tickets" :key="t.id" class="flex items-center gap-3 p-3 rounded-lg bg-secondary">
                <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center"><Ticket class="w-4 h-4 text-primary" /></div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-dark truncate">{{ t.ticket_number || '#' + t.id }} — {{ t.description ? t.description.slice(0, 40) + (t.description.length > 40 ? '...' : '') : 'Aucune description' }}</p>
                  <p class="text-xs text-muted">Étudiant : {{ t.user_name }}</p>
                </div>
                <span :class="['text-xs px-2 py-1 rounded-full font-medium', statusColor(t.status_id)]">{{ statusLabel(t.status_id) }}</span>
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>
