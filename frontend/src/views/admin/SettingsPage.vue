<script setup>
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, LayoutDashboard, Users, Ticket, Settings, LogOut, Bell,
  BarChart3, Building2, Save, Check, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

const configs = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

const fetchConfig = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API}/config/`, { headers })
    configs.value = await res.json()
  } catch { configs.value = [] }
  finally { loading.value = false }
}

const updateConfig = async (key) => {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    const cfg = configs.value.find(c => c.key === key)
    if (!cfg) return
    const res = await fetch(`${API}/config/${key}`, {
      method: 'PUT', headers, body: JSON.stringify({ value: cfg.value })
    })
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail) }
    success.value = 'Configuration mise à jour'
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}

const configLabel = (key) => ({
  sla_hours_low: 'Délai résolution - Priorité basse',
  sla_hours_medium: 'Délai résolution - Priorité moyenne',
  sla_hours_high: 'Délai résolution - Priorité haute',
  sla_hours_critical: 'Délai résolution - Priorité critique',
  reminder_hours: 'Rappel ticket non pris en charge',
  max_login_attempts: 'Tentatives de connexion max',
  lockout_minutes: 'Durée de verrouillage',
  ticket_prefix: 'Préfixe des tickets',
  max_photo_size_mb: 'Taille max photo',
  allowed_mime_types: 'Types MIME autorisés',
}[key] || key)

const configDesc = (key) => ({
  sla_hours_low: 'Heures avant expiration SLA pour les tickets à priorité basse',
  sla_hours_medium: 'Heures avant expiration SLA pour les tickets à priorité moyenne',
  sla_hours_high: 'Heures avant expiration SLA pour les tickets à priorité haute',
  sla_hours_critical: 'Heures avant expiration SLA pour les tickets à priorité critique',
  reminder_hours: 'Nombre d\'heures avant d\'envoyer un rappel pour un ticket non pris en charge',
  max_login_attempts: 'Nombre maximum de tentatives de connexion échouées avant verrouillage du compte',
  lockout_minutes: 'Durée en minutes pendant laquelle le compte reste verrouillé après trop d\'échecs',
  ticket_prefix: 'Préfixe utilisé dans les numéros de ticket (ex: TKT-00001)',
  max_photo_size_mb: 'Taille maximale autorisée pour les photos jointes aux tickets',
  allowed_mime_types: 'Types de fichiers acceptés pour les pièces jointes',
}[key] || '')

const configGroup = (key) => {
  if (key.startsWith('sla_')) return 'SLA — Délais de résolution'
  if (['reminder_hours', 'max_login_attempts', 'lockout_minutes'].includes(key)) return 'Sécurité & Rappels'
  if (['ticket_prefix', 'max_photo_size_mb', 'allowed_mime_types'].includes(key)) return 'Paramètres généraux'
  return 'Autres'
}

const groups = computed(() => {
  const g = {}
  configs.value.forEach(c => {
    const grp = configGroup(c.key)
    if (!g[grp]) g[grp] = []
    g[grp].push(c)
  })
  return g
})

import { computed } from 'vue'

const { unreadNotifs } = useNotifications()

onMounted(() => {
  fetchConfig()
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
        <router-link to="/admin/salles" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Building2 class="w-4 h-4" /> Salles</router-link>
        <router-link to="/admin/parametres" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Settings class="w-4 h-4" /> Paramètres</router-link>
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
          <h1 class="text-lg font-bold text-dark">Paramètres système</h1>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="bg-accent/10 border border-accent/20 rounded-xl p-4 text-sm text-accent-dark">
          <strong>À quoi servent ces paramètres ?</strong>
          <ul class="mt-2 space-y-1 text-muted">
            <li><strong>SLA</strong> → Définissez le délai maximum pour résoudre un ticket selon sa priorité (critique : 4h, haute : 24h, etc.)</li>
            <li><strong>Sécurité</strong> → Limitez les tentatives de connexion et la durée de verrouillage après échecs</li>
            <li><strong>Général</strong> → Personnalisez le préfixe des tickets et les limites de fichiers</li>
          </ul>
        </div>

        <div v-if="success" class="p-3 rounded-xl bg-accent/20 border border-accent/30 text-accent-dark text-sm flex items-center gap-2"><Check class="w-4 h-4" /> {{ success }}</div>
        <div v-if="error" class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm flex items-center gap-2"><AlertCircle class="w-4 h-4" /> {{ error }}</div>

        <div v-for="(cfgs, grp) in groups" :key="grp" class="bg-white rounded-xl border border-primary/5 overflow-hidden">
          <div class="p-5 border-b border-primary/5 bg-secondary/50">
            <h2 class="font-bold text-dark">{{ grp }}</h2>
          </div>
          <div class="divide-y divide-primary/5">
            <div v-for="cfg in cfgs" :key="cfg.key" class="flex items-center justify-between px-6 py-4 hover:bg-primary/[0.02] transition">
              <div class="flex-1 min-w-0 mr-4">
                <p class="text-sm font-semibold text-dark">{{ configLabel(cfg.key) }}</p>
                <p class="text-xs text-muted mt-0.5">{{ configDesc(cfg.key) }}</p>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <input v-model="cfg.value" class="w-24 px-3 py-2 rounded-lg border border-dark/10 bg-white text-sm text-right focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
                <button @click="updateConfig(cfg.key)" :disabled="saving" class="gradient-bg text-white px-3 py-2 rounded-lg text-xs font-semibold transition hover:shadow-lg disabled:opacity-50 flex items-center gap-1"><Save class="w-3.5 h-3.5" /> OK</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-center py-12 text-muted text-sm"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></div>
      </main>
    </div>
  </div>
</template>
