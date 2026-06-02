<script setup>
import { ref, computed, onMounted } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, LayoutDashboard, Users, Ticket, Settings, LogOut, Bell,
  Building2, Plus, Search, X, Check, AlertCircle, Edit3, Trash2
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

const rooms = ref([])
const loading = ref(true)
const search = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const editingRoom = ref(null)
const form = ref({ building_name: '', name: '', floor: '', room_type: 'lab' })
const saving = ref(false)
const error = ref('')
const success = ref('')

const fetchRooms = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API}/rooms/`, { headers })
    rooms.value = await res.json()
  } catch { rooms.value = [] }
  finally { loading.value = false }
}

const openCreate = () => {
  editingRoom.value = null
  form.value = { building_name: '', name: '', floor: '', room_type: 'lab' }
  error.value = ''
  showModal.value = true
}

const openEdit = (r) => {
  editingRoom.value = r.id
  form.value = { building_name: r.building_name || '', name: r.name, floor: r.floor ?? '', room_type: r.room_type }
  error.value = ''
  showModal.value = true
}

const save = async () => {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    const body = {
      name: form.value.name,
      building_name: form.value.building_name || null,
      floor: form.value.floor ? parseInt(form.value.floor) : null,
      room_type: form.value.room_type,
    }
    let res
    if (editingRoom.value) {
      res = await fetch(`${API}/rooms/${editingRoom.value}`, { method: 'PUT', headers, body: JSON.stringify(body) })
    } else {
      res = await fetch(`${API}/rooms/`, { method: 'POST', headers, body: JSON.stringify(body) })
    }
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail) }
    success.value = editingRoom.value ? 'Salle modifiée' : 'Salle créée'
    showModal.value = false
    await fetchRooms()
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}

const askDelete = (r) => {
  deleteTarget.value = r
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  if (!deleteTarget.value) return
  try {
    const res = await fetch(`${API}/rooms/${deleteTarget.value.id}`, { method: 'DELETE', headers })
    if (!res.ok) return
    success.value = `Salle ${deleteTarget.value.name} supprimée`
    showDeleteConfirm.value = false
    deleteTarget.value = null
    await fetchRooms()
  } catch {}
}

const roomTypeLabel = (t) => ({ lab: 'Lab', classroom: 'Salle de cours', office: 'Bureau', multimedia: 'Multimédia', other: 'Autre' }[t] || t)

const roomTypeColor = (t) => ({ lab: 'text-blue-600 bg-blue-50', classroom: 'text-green-600 bg-green-50', office: 'text-purple-600 bg-purple-50', multimedia: 'text-orange-600 bg-orange-50', other: 'text-gray-600 bg-gray-100' }[t] || '')

const filteredRooms = computed(() => {
  if (!search.value) return rooms.value
  const q = search.value.toLowerCase()
  return rooms.value.filter(r => r.name.toLowerCase().includes(q) || (r.building_name || '').toLowerCase().includes(q))
})

const { unreadNotifs } = useNotifications()

onMounted(() => {
  fetchRooms()
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
        <router-link to="/admin/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm relative"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
        <router-link to="/admin/salles" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Building2 class="w-4 h-4" /> Salles</router-link>
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
          <h1 class="text-lg font-bold text-dark">Gestion des salles</h1>
          <button @click="openCreate" class="gradient-bg text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition hover:shadow-lg"><Plus class="w-4 h-4" /> Nouvelle salle</button>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="relative flex-1 max-w-xs">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input v-model="search" type="text" placeholder="Rechercher une salle..." class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
        </div>

        <div v-if="success" class="p-3 rounded-xl bg-accent/20 border border-accent/30 text-accent-dark text-sm"><Check class="w-4 h-4 inline mr-1" /> {{ success }}</div>

        <div class="bg-white rounded-xl border border-primary/5 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-primary/5 bg-secondary/50">
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Salle</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Bâtiment</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Étage</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Type</th>
                  <th class="text-right px-5 py-3.5 font-semibold text-dark">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in filteredRooms" :key="r.id" class="border-b border-primary/5 hover:bg-primary/[0.02] transition">
                  <td class="px-5 py-4"><span class="font-semibold text-dark">{{ r.name }}</span></td>
                  <td class="px-5 py-4 text-muted">{{ r.building_name || '—' }}</td>
                  <td class="px-5 py-4 text-muted">{{ r.floor != null ? `Étage ${r.floor}` : '—' }}</td>
                  <td class="px-5 py-4"><span :class="['inline-flex px-2.5 py-1 rounded-full text-xs font-medium', roomTypeColor(r.room_type)]">{{ roomTypeLabel(r.room_type) }}</span></td>
                  <td class="px-5 py-4 text-right">
                    <div class="flex items-center justify-end gap-1.5">
                      <button @click="openEdit(r)" class="p-2 rounded-lg text-muted hover:bg-primary/5 hover:text-primary transition" title="Modifier"><Edit3 class="w-4 h-4" /></button>
                      <button @click="askDelete(r)" class="p-2 rounded-lg text-muted hover:bg-danger/5 hover:text-danger transition" title="Supprimer"><Trash2 class="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!loading && filteredRooms.length === 0">
                  <td colspan="5" class="px-5 py-12 text-center text-muted text-sm">Aucune salle trouvée</td>
                </tr>
                <tr v-if="loading">
                  <td colspan="5" class="px-5 py-12 text-center text-muted text-sm"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>

    <teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-md shadow-2xl" data-aos="fade-up">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-dark">{{ editingRoom ? 'Modifier' : 'Nouvelle' }} salle</h2>
            <button @click="showModal = false" class="p-2 rounded-lg hover:bg-dark/5 transition"><X class="w-5 h-5 text-muted" /></button>
          </div>
          <form @submit.prevent="save" class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Nom *</label>
              <input v-model="form.name" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Ex: Salle TP 1" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Bâtiment <span class="text-muted font-normal">(facultatif)</span></label>
              <input v-model="form.building_name" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Ex: Bâtiment A" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Étage <span class="text-muted font-normal">(facultatif)</span></label>
                <input v-model="form.floor" type="number" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Ex: 0" />
              </div>
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Type *</label>
                <select v-model="form.room_type" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition">
                  <option value="lab">Laboratoire / TP</option>
                  <option value="classroom">Salle de cours</option>
                  <option value="office">Bureau</option>
                  <option value="multimedia">Multimédia</option>
                  <option value="other">Autre</option>
                </select>
              </div>
            </div>
            <div v-if="error" class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm"><AlertCircle class="w-4 h-4 inline mr-1" /> {{ error }}</div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
              <button type="submit" :disabled="saving" class="flex-1 gradient-bg text-white py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50">
                <span v-if="saving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block"></span>
                <span v-else>{{ editingRoom ? 'Enregistrer' : 'Créer' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showDeleteConfirm = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-sm shadow-2xl text-center" data-aos="fade-up">
          <div class="w-14 h-14 rounded-full bg-danger/10 flex items-center justify-center mx-auto mb-4"><Trash2 class="w-7 h-7 text-danger" /></div>
          <h2 class="text-lg font-bold text-dark mb-2">Supprimer la salle</h2>
          <p class="text-sm text-muted mb-6">Êtes-vous sûr de vouloir supprimer <strong class="text-dark">{{ deleteTarget?.name }}</strong> ?</p>
          <div class="flex gap-3">
            <button @click="showDeleteConfirm = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="confirmDelete" class="flex-1 py-2.5 rounded-xl bg-danger text-white text-sm font-semibold transition hover:shadow-lg">Supprimer</button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>
