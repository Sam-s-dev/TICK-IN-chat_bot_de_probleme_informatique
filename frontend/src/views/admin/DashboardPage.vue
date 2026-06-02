<script setup>
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, LayoutDashboard, Users, Ticket, Settings, LogOut, Bell,
  BarChart3, Building2, TrendingUp, Clock, CheckCircle, AlertCircle, Star
} from 'lucide-vue-next'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement,
  LineElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler)

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)

const loading = ref(true)
const stats = ref(null)

const statusChartData = ref(null)
const statusChartOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }

const categoryChartData = ref(null)
const categoryChartOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 12, font: { size: 11 } } } } }

const dailyChartData = ref(null)
const dailyChartOpts = { responsive: true, maintainAspectRatio: false, fill: true, tension: 0.4, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' } }, x: { grid: { display: false } } } }

const techChartData = ref(null)
const techChartOpts = { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' } }, y: { grid: { display: false } } } }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

const { unreadNotifs } = useNotifications()

const fetchStats = async () => {
  try {
    const token = authService.getToken()
    const res = await fetch('http://localhost:8000/api/stats/dashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Erreur chargement stats')
    const d = await res.json()
    stats.value = d

    statusChartData.value = {
      labels: d.tickets_by_status.map(s => s.name),
      datasets: [{ label: 'Tickets', data: d.tickets_by_status.map(s => s.count), backgroundColor: ['#7C6FE8', '#FBBF24', '#34D399', '#F472B6', '#60A5FA', '#F97316'], borderRadius: 6 }]
    }

    categoryChartData.value = {
      labels: d.tickets_by_category.map(c => c.name),
      datasets: [{ data: d.tickets_by_category.map(c => c.count), backgroundColor: ['#7C6FE8', '#AAF0D1', '#FBBF24', '#F472B6', '#60A5FA', '#F97316'], borderWidth: 0 }]
    }

    dailyChartData.value = {
      labels: d.tickets_per_day.map(p => { const [y, m, day] = p.day.split('-'); return `${day}/${m}` }),
      datasets: [{ label: 'Tickets', data: d.tickets_per_day.map(p => p.count), backgroundColor: 'rgba(124,111,232,0.1)', borderColor: '#7C6FE8', pointBackgroundColor: '#7C6FE8', pointRadius: 4, pointHoverRadius: 6 }]
    }

    techChartData.value = {
      labels: d.top_technicians.map(t => t.name.split(' ')[0]),
      datasets: [{ label: 'Résolus', data: d.top_technicians.map(t => t.resolved), backgroundColor: '#AAF0D1', borderRadius: 6 }]
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

let statsInterval

onMounted(() => {
  fetchStats()
  statsInterval = setInterval(fetchStats, 30000)
})

onBeforeUnmount(() => {
  clearInterval(statsInterval)
})

const logout = () => { authService.logout(); router.push('/login') }
</script>

<template>
  <div class="min-h-screen bg-secondary flex">
    <!-- Sidebar -->
    <aside :class="['fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-primary/5 flex flex-col transition-transform duration-300 lg:translate-x-0', sidebarOpen ? 'translate-x-0' : '-translate-x-full']">
      <div class="p-5 border-b border-primary/5">
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 gradient-bg rounded-lg flex items-center justify-center"><MessageSquare class="w-5 h-5 text-white" /></div>
          <div><span class="text-lg font-bold text-dark leading-tight">TICK'IN</span><span class="text-xs text-muted leading-tight -mt-0.5 block">Admin</span></div>
        </div>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/admin/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/admin/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Ticket class="w-4 h-4" /> Tickets</router-link>
        <router-link to="/admin/utilisateurs" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Users class="w-4 h-4" /> Utilisateurs</router-link>
        <router-link to="/admin/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm relative"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
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

    <!-- Main -->
    <div class="flex-1 flex flex-col min-h-screen">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-dark/5">
        <div class="flex items-center justify-between px-4 lg:px-8 h-16">
          <button @click="sidebarOpen = true" class="lg:hidden p-2 rounded-lg hover:bg-dark/5"><svg class="w-5 h-5 text-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
          <h1 class="text-lg font-bold text-dark">Dashboard — Administrateur</h1>
          <div class="relative"><Bell class="w-5 h-5 text-muted hover:text-dark cursor-pointer transition" /></div>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6" v-if="!loading && stats">
        <!-- KPI Cards -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          <div class="bg-white rounded-xl p-4 lg:p-5 border border-primary/5 card-hover">
            <div class="flex items-center justify-between mb-3"><span class="text-xs lg:text-sm text-muted font-medium">Tickets ouverts</span><div class="w-9 h-9 rounded-xl bg-warning/10 flex items-center justify-center"><Clock class="w-4 h-4 lg:w-5 lg:h-5 text-warning" /></div></div>
            <p class="text-xl lg:text-2xl font-bold text-dark">{{ stats.open_tickets }}</p>
          </div>
          <div class="bg-white rounded-xl p-4 lg:p-5 border border-primary/5 card-hover">
            <div class="flex items-center justify-between mb-3"><span class="text-xs lg:text-sm text-muted font-medium">Résolus</span><div class="w-9 h-9 rounded-xl bg-accent/20 flex items-center justify-center"><CheckCircle class="w-4 h-4 lg:w-5 lg:h-5 text-accent-dark" /></div></div>
            <p class="text-xl lg:text-2xl font-bold text-dark">{{ stats.resolved_tickets }}</p>
          </div>
          <div class="bg-white rounded-xl p-4 lg:p-5 border border-primary/5 card-hover">
            <div class="flex items-center justify-between mb-3"><span class="text-xs lg:text-sm text-muted font-medium">Utilisateurs</span><div class="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center"><Users class="w-4 h-4 lg:w-5 lg:h-5 text-primary" /></div></div>
            <p class="text-xl lg:text-2xl font-bold text-dark">{{ stats.total_users }}</p>
          </div>
          <div class="bg-white rounded-xl p-4 lg:p-5 border border-primary/5 card-hover">
            <div class="flex items-center justify-between mb-3"><span class="text-xs lg:text-sm text-muted font-medium">Note moyenne</span><div class="w-9 h-9 rounded-xl bg-danger/10 flex items-center justify-center"><Star class="w-4 h-4 lg:w-5 lg:h-5 text-danger" /></div></div>
            <p class="text-xl lg:text-2xl font-bold text-dark">{{ stats.average_rating }} <span class="text-sm text-muted font-normal">/ 5</span></p>
          </div>
        </div>

        <!-- Charts row 1 -->
        <div class="grid lg:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl p-5 border border-primary/5">
            <h3 class="font-bold text-dark mb-1">Tickets par statut</h3>
            <p class="text-xs text-muted mb-4">Répartition des tickets selon leur état</p>
            <div class="h-56"><Bar v-if="statusChartData" :data="statusChartData" :options="statusChartOpts" /></div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-primary/5">
            <h3 class="font-bold text-dark mb-1">Tickets par catégorie</h3>
            <p class="text-xs text-muted mb-4">Répartition par type de problème</p>
            <div class="h-56 flex items-center justify-center"><Doughnut v-if="categoryChartData" :data="categoryChartData" :options="categoryChartOpts" /></div>
          </div>
        </div>

        <!-- Charts row 2 -->
        <div class="grid lg:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl p-5 border border-primary/5">
            <h3 class="font-bold text-dark mb-1">Tickets (7 derniers jours)</h3>
            <p class="text-xs text-muted mb-4">Évolution quotidienne des signalements</p>
            <div class="h-56"><Line v-if="dailyChartData" :data="dailyChartData" :options="dailyChartOpts" /></div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-primary/5">
            <h3 class="font-bold text-dark mb-1">Top techniciens</h3>
            <p class="text-xs text-muted mb-4">Les plus de tickets résolus</p>
            <div class="h-56"><Bar v-if="techChartData" :data="techChartData" :options="techChartOpts" /></div>
          </div>
        </div>

        <!-- Welcome -->
        <div class="bg-white rounded-xl p-5 lg:p-6 border border-primary/5">
          <h2 class="text-lg lg:text-xl font-bold text-dark mb-1">Bienvenue, {{ user?.nom || 'Admin' }}</h2>
          <p class="text-sm text-muted">Vous êtes connecté en tant qu'<strong class="text-primary">administrateur</strong>. Toutes les données affichées proviennent de la base de données.</p>
        </div>
      </main>

      <!-- Loading state -->
      <main class="flex-1 flex items-center justify-center" v-else-if="loading">
        <div class="text-center">
          <div class="w-10 h-10 border-3 border-primary/30 border-t-primary rounded-full animate-spin mx-auto mb-4"></div>
          <p class="text-sm text-muted">Chargement des données...</p>
        </div>
      </main>
    </div>
  </div>
</template>
