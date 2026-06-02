<script setup>
import { ref, onMounted, computed } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, Users, Ticket, Search, X, LogOut, Bell,
  LayoutDashboard, Building2, Settings, Trash2, Wrench
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

const tickets = ref([])
const technicians = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref(0)
const showAssignModal = ref(false)
const selectedTicket = ref(null)
const assignTechId = ref(null)
const showDeleteModal = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

const fetchTickets = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({ per_page: '100' })
    if (statusFilter.value) params.set('status_id', statusFilter.value)
    const res = await fetch(`${API}/tickets/?${params}`, { headers })
    const data = await res.json()
    tickets.value = data.tickets || []
  } catch { tickets.value = [] }
  finally { loading.value = false }
}

const fetchTechnicians = async () => {
  try {
    const res = await fetch(`${API}/users/technicians`, { headers })
    technicians.value = await res.json()
  } catch { technicians.value = [] }
}

const statuses = [
  { id: 0, label: 'Tous', color: 'text-muted' },
  { id: 1, label: 'Soumis', color: 'text-yellow-600 bg-yellow-50' },
  { id: 2, label: 'En cours', color: 'text-blue-600 bg-blue-50' },
  { id: 3, label: 'En attente', color: 'text-indigo-600 bg-indigo-50' },
  { id: 4, label: 'En vérification', color: 'text-orange-600 bg-orange-50' },
  { id: 5, label: 'Résolu', color: 'text-accent-dark bg-accent/20' },
]

const filteredTickets = computed(() => {
  let result = tickets.value
  if (!search.value) return result
  const q = search.value.toLowerCase()
  return result.filter(t =>
    t.ticket_number.toLowerCase().includes(q) ||
    t.user_name.toLowerCase().includes(q) ||
    t.category_name.toLowerCase().includes(q)
  )
})

const openAssign = (ticket) => {
  selectedTicket.value = ticket
  assignTechId.value = ticket.assigned_to || ''
  showAssignModal.value = true
}

const confirmAssign = async () => {
  if (!selectedTicket.value || !assignTechId.value) return
  try {
    const res = await fetch(`${API}/tickets/${selectedTicket.value.id}/assign`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ technician_id: assignTechId.value })
    })
    if (!res.ok) return
    showAssignModal.value = false
    selectedTicket.value = null
    await fetchTickets()
    await fetchTechnicians()
  } catch {}
}

const openDelete = (ticket) => {
  deleteTarget.value = ticket
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await fetch(`${API}/tickets/${deleteTarget.value.id}`, {
      method: 'DELETE', headers
    })
    showDeleteModal.value = false
    deleteTarget.value = null
    await fetchTickets()
  } catch {}
  finally { deleting.value = false }
}

const statusColor = (s) => {
  const m = { 1: 'text-yellow-600 bg-yellow-50', 2: 'text-blue-600 bg-blue-50', 3: 'text-indigo-600 bg-indigo-50', 4: 'text-orange-600 bg-orange-50', 5: 'text-green-600 bg-green-50' }
  return m[s] || 'bg-gray-100'
}
const priorityClass = (p) => {
  const map = { low: 'text-gray-500 bg-gray-100', medium: 'text-yellow-600 bg-yellow-50', high: 'text-orange-600 bg-orange-50', critical: 'text-danger bg-danger/10' }
  return map[p] || 'text-gray-500 bg-gray-100'
}
const techStatusColor = (s) => {
  const m = { disponible: 'text-green-600 bg-green-50', occupe: 'text-orange-600 bg-orange-50', sature: 'text-red-600 bg-red-50' }
  return m[s] || 'bg-gray-100'
}
const techLoadColor = (p) => p < 50 ? 'bg-green-500' : (p < 80 ? 'bg-orange-500' : 'bg-red-500')

const { unreadNotifs } = useNotifications()

onMounted(() => {
  fetchTickets()
  fetchTechnicians()
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
        <router-link to="/admin/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Ticket class="w-4 h-4" /> Tickets</router-link>
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

    <div class="flex-1 flex flex-col min-h-screen">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-dark/5">
        <div class="flex items-center justify-between px-4 lg:px-8 h-16">
          <button @click="sidebarOpen = true" class="lg:hidden p-2 rounded-lg hover:bg-dark/5"><svg class="w-5 h-5 text-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
          <h1 class="text-lg font-bold text-dark">Tickets</h1>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div class="relative flex-1 max-w-xs">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input v-model="search" type="text" placeholder="Rechercher un ticket..." class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
          </div>
          <div class="flex flex-wrap gap-2">
            <button v-for="s in statuses" :key="s.id" @click="statusFilter = s.id; fetchTickets()" :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition', statusFilter === s.id ? 'bg-primary/10 text-primary' : 'text-muted hover:text-dark']">{{ s.label }}</button>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-primary/5 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-primary/5 bg-secondary/50">
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Ticket</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Étudiant</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Catégorie</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Salle</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Statut</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Priorité</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Technicien</th>
                  <th class="text-right px-5 py-3.5 font-semibold text-dark">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in filteredTickets" :key="t.id" class="border-b border-primary/5 hover:bg-primary/[0.02] transition">
                  <td class="px-5 py-4">
                    <span class="font-mono font-semibold text-dark text-xs">{{ t.ticket_number }}</span>
                    <p class="text-xs text-muted mt-0.5">{{ new Date(t.created_at).toLocaleDateString('fr-FR') }}</p>
                  </td>
                  <td class="px-5 py-4">
                    <div class="flex items-center gap-2">
                      <div class="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">{{ t.user_name?.[0] || '?' }}</div>
                      <span class="text-dark text-sm">{{ t.user_name }}</span>
                    </div>
                  </td>
                  <td class="px-5 py-4 text-muted text-sm">{{ t.category_name }}</td>
                  <td class="px-5 py-4 text-muted text-sm">{{ t.room_name || t.building_name }}</td>
                  <td class="px-5 py-4">
                    <span :class="['inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium', statusColor(t.status_id)]">{{ t.status_label }}</span>
                  </td>
                  <td class="px-5 py-4">
                    <span :class="['inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium', priorityClass(t.priority)]">{{ t.priority }}</span>
                  </td>
                  <td class="px-5 py-4 text-sm">
                    <span v-if="t.technician_name" class="text-dark">{{ t.technician_name }}</span>
                    <span v-else class="text-muted italic">—</span>
                  </td>
                  <td class="px-5 py-4 text-right">
                    <div class="flex items-center justify-end gap-1">
                      <button @click="openAssign(t)" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-primary hover:bg-primary/5 transition">
                        {{ t.assigned_to ? 'Réassigner' : 'Assigner' }}
                      </button>
                      <button v-if="t.status_id !== 5" @click="openDelete(t)" class="p-1.5 rounded-lg text-xs text-danger hover:bg-danger/5 transition" title="Supprimer le ticket">
                        <Trash2 class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!loading && filteredTickets.length === 0">
                  <td colspan="8" class="px-5 py-12 text-center text-muted text-sm">Aucun ticket trouvé</td>
                </tr>
                <tr v-if="loading">
                  <td colspan="8" class="px-5 py-12 text-center text-muted text-sm">
                    <div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>

    <teleport to="body">
      <div v-if="showAssignModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showAssignModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-md shadow-2xl" data-aos="fade-up">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-dark">Assigner un technicien</h2>
            <button @click="showAssignModal = false" class="p-2 rounded-lg hover:bg-dark/5 transition"><X class="w-5 h-5 text-muted" /></button>
          </div>
          <p class="text-sm text-muted mb-4">Ticket : <strong class="text-dark">{{ selectedTicket?.ticket_number }}</strong></p>
          <div>
            <label class="block text-sm font-semibold text-dark mb-3">Technicien</label>
            <div class="space-y-2 max-h-64 overflow-y-auto">
              <label v-for="tech in technicians" :key="tech.id"
                :class="['flex items-start gap-3 p-3 rounded-xl border-2 cursor-pointer transition',
                  assignTechId === tech.id ? 'border-primary bg-primary/5' : 'border-dark/10 hover:border-primary/30']">
                <input type="radio" :value="tech.id" v-model="assignTechId" class="mt-1 accent-primary" />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-semibold text-dark">{{ tech.first_name }} {{ tech.last_name }}</span>
                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', techStatusColor(tech.status)]">{{ tech.status }}</span>
                  </div>
                  <div class="mt-2">
                    <div class="flex items-center justify-between text-xs text-muted mb-1">
                      <span>{{ tech.open_tickets }} ticket(s) ouvert(s)</span>
                      <span>{{ tech.load_pct }}%</span>
                    </div>
                    <div class="w-full h-2 bg-dark/5 rounded-full overflow-hidden">
                      <div :class="['h-full rounded-full transition-all', techLoadColor(tech.load_pct)]" :style="{ width: tech.load_pct + '%' }"></div>
                    </div>
                  </div>
                </div>
              </label>
              <p v-if="technicians.length === 0" class="text-sm text-muted text-center py-4">Aucun technicien disponible</p>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="showAssignModal = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="confirmAssign" :disabled="!assignTechId" class="flex-1 gradient-bg text-white py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50">Confirmer</button>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showDeleteModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl text-center" data-aos="fade-up">
          <Trash2 class="w-10 h-10 text-danger mx-auto mb-3" />
          <h3 class="text-lg font-bold text-dark mb-2">Supprimer le ticket ?</h3>
          <p class="text-sm text-muted mb-2">Ticket : <strong>{{ deleteTarget?.ticket_number }}</strong></p>
          <p class="text-xs text-muted mb-5">Cette action est irreversible. Tous les messages et fichiers joints seront supprimés.</p>
          <div class="flex gap-3">
            <button @click="showDeleteModal = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2.5 rounded-xl bg-danger text-white text-sm font-semibold hover:bg-danger/80 transition disabled:opacity-50">
              <span v-if="deleting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block"></span>
              <span v-else>Supprimer</span>
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>
