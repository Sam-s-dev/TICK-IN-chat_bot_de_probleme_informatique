<script setup>
import { ref, onMounted } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import {
  MessageSquare, LayoutDashboard, Ticket, Bell, Settings, LogOut,
  Wrench, User, Lock, Mail, Save, AlertCircle, Check, Eye, EyeOff
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const headers = { Authorization: `Bearer ${authService.getToken()}`, 'Content-Type': 'application/json' }

const profile = ref({ first_name: '', last_name: '', email: '', username: '' })
const loading = ref(true)
const { unreadNotifs } = useNotifications()
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const savingPwd = ref(false)
const pwdSuccess = ref('')
const pwdError = ref('')

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API}/auth/me`, { headers })
    profile.value = await res.json()
  } catch {}
  finally { loading.value = false }
}

const changePassword = async () => {
  pwdError.value = ''
  pwdSuccess.value = ''
  savingPwd.value = true
  try {
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
      throw new Error('Les mots de passe ne correspondent pas')
    }
    if (passwordForm.value.new_password.length < 6) {
      throw new Error('Le mot de passe doit contenir au moins 6 caracteres')
    }
    const res = await fetch(`${API}/auth/change-password`, {
      method: 'POST', headers,
      body: JSON.stringify({
        old_password: passwordForm.value.old_password,
        new_password: passwordForm.value.new_password,
      })
    })
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail) }
    pwdSuccess.value = 'Mot de passe modifie avec succes'
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (e) { pwdError.value = e.message }
  finally { savingPwd.value = false }
}

onMounted(() => {
  fetchProfile()
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
        <router-link to="/technicien/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/technicien/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Wrench class="w-4 h-4" /> Mes tickets</router-link>
        <router-link to="/technicien/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm relative"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
        <router-link to="/technicien/parametres" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Settings class="w-4 h-4" /> Paramètres</router-link>
      </nav>
      <div class="p-4 border-t border-primary/5">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-sm font-bold text-white">{{ user?.nom?.[0] || 'T' }}</div>
          <div class="flex-1 min-w-0"><p class="text-sm font-semibold text-dark truncate">{{ user?.nom || 'Technicien' }}</p><p class="text-xs text-muted truncate">{{ user?.email }}</p></div>
        </div>
        <button @click="logout" class="flex items-center gap-2 w-full px-4 py-2 rounded-xl text-muted hover:bg-danger/5 hover:text-danger transition text-sm"><LogOut class="w-4 h-4" /> Déconnexion</button>
      </div>
    </aside>

    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/40 z-30 lg:hidden"></div>

    <div class="flex-1 flex flex-col min-h-screen">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-dark/5">
        <div class="flex items-center justify-between px-4 lg:px-8 h-16">
          <button @click="sidebarOpen = true" class="lg:hidden p-2 rounded-lg hover:bg-dark/5"><svg class="w-5 h-5 text-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
          <h1 class="text-lg font-bold text-dark">Paramètres</h1>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6 max-w-2xl">
        <div v-if="loading" class="text-center py-12"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></div>

        <template v-else>
          <div class="bg-white rounded-xl border border-primary/5 p-6 lg:p-8">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-16 h-16 rounded-full gradient-bg flex items-center justify-center text-2xl font-bold text-white">{{ profile.first_name?.[0] || '' }}{{ profile.last_name?.[0] || '' }}</div>
              <div><h2 class="text-lg font-bold text-dark">{{ profile.first_name }} {{ profile.last_name }}</h2><p class="text-sm text-muted">{{ profile.email }}</p></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-dark mb-1">Prénom</label>
                <div class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-secondary/50 border border-dark/10 text-sm text-muted"><User class="w-4 h-4 text-muted" /> {{ profile.first_name }}</div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-dark mb-1">Nom</label>
                <div class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-secondary/50 border border-dark/10 text-sm text-muted"><User class="w-4 h-4 text-muted" /> {{ profile.last_name }}</div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-dark mb-1">Email</label>
                <div class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-secondary/50 border border-dark/10 text-sm text-muted"><Mail class="w-4 h-4 text-muted" /> {{ profile.email || 'Non renseigne' }}</div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-dark mb-1">Nom d'utilisateur</label>
                <div class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-secondary/50 border border-dark/10 text-sm text-muted"><User class="w-4 h-4 text-muted" /> {{ profile.username || 'Non renseigne' }}</div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-primary/5 p-6 lg:p-8">
            <h3 class="text-base font-bold text-dark mb-4 flex items-center gap-2"><Lock class="w-4 h-4" /> Changer le mot de passe</h3>
            <form @submit.prevent="changePassword" class="space-y-4 max-w-md">
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Mot de passe actuel</label>
                <div class="relative"><input :type="showOld ? 'text' : 'password'" v-model="passwordForm.old_password" required class="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" /><button type="button" @click="showOld = !showOld" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted"><component :is="showOld ? EyeOff : Eye" class="w-4 h-4" /></button></div>
              </div>
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Nouveau mot de passe</label>
                <div class="relative"><input :type="showNew ? 'text' : 'password'" v-model="passwordForm.new_password" required class="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" /><button type="button" @click="showNew = !showNew" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted"><component :is="showNew ? EyeOff : Eye" class="w-4 h-4" /></button></div>
              </div>
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Confirmer le nouveau mot de passe</label>
                <div class="relative"><input :type="showConfirm ? 'text' : 'password'" v-model="passwordForm.confirm_password" required class="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" /><button type="button" @click="showConfirm = !showConfirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted"><component :is="showConfirm ? EyeOff : Eye" class="w-4 h-4" /></button></div>
              </div>
              <div v-if="pwdSuccess" class="p-3 rounded-xl bg-accent/20 border border-accent/30 text-accent-dark text-sm"><Check class="w-4 h-4 inline mr-1" /> {{ pwdSuccess }}</div>
              <div v-if="pwdError" class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm"><AlertCircle class="w-4 h-4 inline mr-1" /> {{ pwdError }}</div>
              <button type="submit" :disabled="savingPwd" class="gradient-bg text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50">
                <span v-if="savingPwd" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block mr-1"></span>
                <span v-else><Save class="w-4 h-4 inline mr-1" /></span> Enregistrer
              </button>
            </form>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>
