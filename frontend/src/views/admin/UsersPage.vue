<script setup>
import { ref, onMounted, computed } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, Users, UserPlus, Search, X, Check, AlertCircle,
  Shield, Wrench, GraduationCap, LogOut, Bell, Lock, Unlock,
  LayoutDashboard, Ticket, BarChart3, Building2, Settings
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

const users = ref([])
const loading = ref(true)
const search = ref('')
const roleFilter = ref(0)
const showModal = ref(false)
const showConfirmBlock = ref(false)
const confirmTarget = ref(null)
const editingId = ref(null)
const form = ref({ role_id: 2, first_name: '', last_name: '', email: '', phone: '', password: '' })
const saving = ref(false)
const error = ref('')
const success = ref('')

const createRoles = [
  { id: 1, label: 'Administrateur', icon: Shield, color: 'text-primary bg-primary/10' },
  { id: 2, label: 'Technicien', icon: Wrench, color: 'text-accent-dark bg-accent/20' },
]

const roles = [
  ...createRoles,
  { id: 3, label: 'Étudiant', icon: GraduationCap, color: 'text-danger bg-danger/10' },
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API}/users/`, { headers })
    users.value = await res.json()
  } catch { users.value = [] }
  finally { loading.value = false }
}

const filteredUsers = computed(() => {
  let result = users.value
  if (roleFilter.value) {
    result = result.filter(u => u.role_id === roleFilter.value)
  }
  if (!search.value) return result
  const q = search.value.toLowerCase()
  return result.filter(u =>
    `${u.first_name} ${u.last_name}`.toLowerCase().includes(q) ||
    (u.email && u.email.toLowerCase().includes(q)) ||
    (u.student_id && u.student_id.toLowerCase().includes(q))
  )
})

const openCreate = () => {
  editingId.value = null
  form.value = { role_id: 2, first_name: '', last_name: '', email: '', phone: '', password: '' }
  error.value = ''
  showModal.value = true
}

const openEdit = (u) => {
  editingId.value = u.id
  form.value = { role_id: u.role_id, first_name: u.first_name, last_name: u.last_name, email: u.email || '', phone: u.phone || '', password: '' }
  error.value = ''
  showModal.value = true
}

const save = async () => {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    if (editingId.value) {
      const body = { first_name: form.value.first_name, last_name: form.value.last_name, email: form.value.email, phone: form.value.phone }
      const res = await fetch(`${API}/users/${editingId.value}`, { method: 'PUT', headers, body: JSON.stringify(body) })
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail) }
      success.value = 'Technicien modifié avec succès'
    } else {
      const body = { ...form.value }
      const res = await fetch(`${API}/users/`, { method: 'POST', headers, body: JSON.stringify(body) })
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail) }
      success.value = 'Technicien créé avec succès'
    }
    showModal.value = false
    await fetchUsers()
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}

const askBlock = (u) => {
  confirmTarget.value = u
  showConfirmBlock.value = true
}

const confirmBlock = async () => {
  if (!confirmTarget.value) return
  try {
    const u = confirmTarget.value
    await fetch(`${API}/users/${u.id}`, { method: 'PUT', headers, body: JSON.stringify({ is_active: !u.is_active }) })
    success.value = u.is_active
      ? `${u.first_name} ${u.last_name} a été bloqué`
      : `${u.first_name} ${u.last_name} a été débloqué`
    showConfirmBlock.value = false
    confirmTarget.value = null
    await fetchUsers()
  } catch {}
}

const { unreadNotifs } = useNotifications()

onMounted(() => {
  fetchUsers()
})

const roleIcon = (rid) => roles.find(r => r.id === rid)?.icon || Users
const roleColor = (rid) => roles.find(r => r.id === rid)?.color || 'bg-gray-100 text-gray-500'
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
        <router-link to="/admin/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/admin/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Ticket class="w-4 h-4" /> Tickets</router-link>
        <router-link to="/admin/utilisateurs" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Users class="w-4 h-4" /> Utilisateurs</router-link>
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
          <h1 class="text-lg font-bold text-dark">Gestion des utilisateurs</h1>
          <div class="flex items-center gap-3">
            <button @click="openCreate" class="gradient-bg text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition hover:shadow-lg hover:shadow-primary/25"><UserPlus class="w-4 h-4" /> Nouveau technicien</button>
          </div>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <!-- Filters -->
        <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div class="relative flex-1 max-w-xs">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input v-model="search" type="text" placeholder="Rechercher..." class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
          </div>
          <div class="flex gap-2">
            <button @click="roleFilter = 0" :class="['px-4 py-2 rounded-lg text-sm font-medium transition', roleFilter === 0 ? 'bg-primary/10 text-primary' : 'text-muted hover:text-dark']">Tous</button>
            <button v-for="r in roles" :key="r.id" @click="roleFilter = r.id" :class="['px-4 py-2 rounded-lg text-sm font-medium transition', roleFilter === r.id ? r.color : 'text-muted hover:text-dark']">{{ r.label }}</button>
          </div>
        </div>

        <!-- Success -->
        <div v-if="success" class="p-3 rounded-xl bg-accent/20 border border-accent/30 text-accent-dark text-sm flex items-center gap-2" data-aos="fade-up"><Check class="w-4 h-4" /> {{ success }}</div>

        <!-- Table -->
        <div class="bg-white rounded-xl border border-primary/5 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-primary/5 bg-secondary/50">
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Utilisateur</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Email</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Rôle</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Statut</th>
                  <th class="text-left px-5 py-3.5 font-semibold text-dark">Créé le</th>
                  <th class="text-right px-5 py-3.5 font-semibold text-dark">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in filteredUsers" :key="u.id" class="border-b border-primary/5 hover:bg-primary/[0.02] transition">
                  <td class="px-5 py-4">
                    <div class="flex items-center gap-3">
                      <div :class="['w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold ' + roleColor(u.role_id)]">{{ u.first_name[0] }}{{ u.last_name[0] }}</div>
                      <div>
                        <p class="font-semibold text-dark">{{ u.first_name }} {{ u.last_name }}</p>
                        <p v-if="u.student_id" class="text-xs text-muted">{{ u.student_id }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-5 py-4 text-muted">{{ u.email || '—' }}</td>
                  <td class="px-5 py-4">
                    <span :class="['inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ' + roleColor(u.role_id)]">
                      <component :is="roleIcon(u.role_id)" class="w-3.5 h-3.5" />
                      {{ u.role_name }}
                    </span>
                  </td>
                  <td class="px-5 py-4">
                    <span :class="['inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium', u.is_active ? 'bg-accent/20 text-accent-dark' : 'bg-danger/10 text-danger']">
                      <span :class="['w-1.5 h-1.5 rounded-full', u.is_active ? 'bg-accent-dark' : 'bg-danger']"></span>
                      {{ u.is_active ? 'Actif' : 'Inactif' }}
                    </span>
                  </td>
                  <td class="px-5 py-4 text-muted text-xs">{{ new Date(u.created_at).toLocaleDateString('fr-FR') }}</td>
                  <td class="px-5 py-4 text-right">
                    <div class="flex items-center justify-end gap-1.5">
                      <button v-if="u.role_id !== 3" @click="openEdit(u)" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-muted hover:bg-primary/5 hover:text-primary transition" title="Modifier">Modifier</button>
                      <button v-if="u.is_active" @click="askBlock(u)" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-danger hover:bg-danger/5 transition" title="Bloquer">Bloquer</button>
                      <button v-else @click="askBlock(u)" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-accent-dark hover:bg-accent/20 transition" title="Débloquer">Débloquer</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!loading && filteredUsers.length === 0">
                  <td colspan="6" class="px-5 py-12 text-center text-muted text-sm">Aucun utilisateur trouvé</td>
                </tr>
                <tr v-if="loading">
                  <td colspan="6" class="px-5 py-12 text-center text-muted text-sm">
                    <div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Summary -->
        <div class="grid grid-cols-3 gap-4 lg:gap-6">
          <div v-for="r in roles" :key="r.id" class="bg-white rounded-xl p-4 border border-primary/5 card-hover">
            <div class="flex items-center gap-3">
              <div :class="['w-10 h-10 rounded-xl flex items-center justify-center ' + r.color]"><component :is="r.icon" class="w-5 h-5" /></div>
              <div>
                <p class="text-xs text-muted">{{ r.label }}</p>
                <p class="text-xl font-bold text-dark">{{ users.filter(u => u.role_id === r.id).length }}</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Modal -->
    <teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-lg shadow-2xl" data-aos="fade-up">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-dark">{{ editingId ? 'Modifier' : 'Nouvel' }} utilisateur</h2>
            <button @click="showModal = false" class="p-2 rounded-lg hover:bg-dark/5 transition"><X class="w-5 h-5 text-muted" /></button>
          </div>

          <form @submit.prevent="save" class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Rôle</label>
              <div class="flex gap-2">
                <button v-for="r in createRoles" :key="r.id" type="button"
                  @click="form.role_id = r.id"
                  :class="['flex-1 py-2.5 rounded-xl text-sm font-semibold border-2 transition', form.role_id === r.id ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">
                  {{ r.label }}
                </button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Prénom</label>
                <input v-model="form.first_name" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
              </div>
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Nom</label>
                <input v-model="form.last_name" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Email</label>
              <input v-model="form.email" type="email" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Téléphone</label>
                <input v-model="form.phone" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
              </div>

            </div>
            <div v-if="!editingId">
              <label class="block text-sm font-semibold text-dark mb-1">Mot de passe</label>
              <input v-model="form.password" type="text" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
            </div>

            <div v-if="error" class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm flex items-center gap-2"><AlertCircle class="w-4 h-4" /> {{ error }}</div>

            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
              <button type="submit" :disabled="saving" class="flex-1 gradient-bg text-white py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2">
                <span v-if="saving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span v-else>{{ editingId ? 'Enregistrer' : 'Créer' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>

    <!-- Confirmation modal -->
    <teleport to="body">
      <div v-if="showConfirmBlock" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showConfirmBlock = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-sm shadow-2xl text-center" data-aos="fade-up">
          <div :class="['w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4', confirmTarget?.is_active ? 'bg-danger/10' : 'bg-accent/20']">
            <Lock v-if="confirmTarget?.is_active" class="w-7 h-7 text-danger" />
            <Unlock v-else class="w-7 h-7 text-accent-dark" />
          </div>
          <h2 class="text-lg font-bold text-dark mb-2">
            {{ confirmTarget?.is_active ? 'Bloquer' : 'Débloquer' }} l'utilisateur
          </h2>
          <p class="text-sm text-muted mb-6">
            Êtes-vous sûr de vouloir
            <strong>{{ confirmTarget?.is_active ? 'bloquer' : 'débloquer' }}</strong>
            <strong class="text-dark">{{ confirmTarget?.first_name }} {{ confirmTarget?.last_name }}</strong>
            {{ confirmTarget?.is_active ? ' ? Il ne pourra plus se connecter.' : ' ?' }}
          </p>
          <div class="flex gap-3">
            <button @click="showConfirmBlock = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="confirmBlock"
              :class="['flex-1 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:shadow-lg', confirmTarget?.is_active ? 'gradient-bg' : 'bg-accent-dark hover:bg-accent-dark/90']">
              {{ confirmTarget?.is_active ? 'Bloquer' : 'Débloquer' }}
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>
