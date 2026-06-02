<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth.js'
import { MessageSquare, Sparkles, ArrowRight, GraduationCap, User, Lock, Mail, UserCheck, BookOpen, ChevronDown } from 'lucide-vue-next'

const router = useRouter()
const API = 'http://localhost:8000/api'
const step = ref(1)
const loading = ref(false)
const error = ref('')

const form = ref({
  username: '',
  password: '',
  confirmPassword: '',
  first_name: '',
  last_name: '',
  genre: '',
  niveau_etude: '',
  programme: '',
  email: '',
})

const successMessage = ref('')

const submit = async () => {
  error.value = ''
  successMessage.value = ''
  if (form.value.password !== form.value.confirmPassword) {
    error.value = 'Les mots de passe ne correspondent pas'
    return
  }
  if (form.value.password.length < 6) {
    error.value = 'Le mot de passe doit contenir au moins 6 caractères'
    return
  }
  loading.value = true
  try {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.value.username,
        password: form.value.password,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        genre: form.value.genre,
        niveau_etude: form.value.niveau_etude,
        programme: form.value.programme,
        email: form.value.email || null,
      })
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Erreur lors de l\'inscription')
    }
    const data = await res.json()
    successMessage.value = data.message
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-secondary flex">
    <!-- Left brand panel -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center p-12"
         style="background-image: url('https://i.pinimg.com/1200x/5d/1b/63/5d1b6373d14b5564ac3ca1540d66ee0c.jpg'); background-size: cover; background-position: center;">
      <div class="absolute inset-0 bg-black/50"></div>
      <div class="relative text-center max-w-md">
        <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 backdrop-blur-sm">
          <GraduationCap class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-4xl font-bold text-white mb-4">Inscription Étudiant</h1>
        <p class="text-white/70 text-lg leading-relaxed">
          Créez votre compte pour signaler les incidents informatiques et suivre leurs résolutions.
        </p>
        <div class="mt-8 grid grid-cols-2 gap-3 text-left text-sm text-white/80">
          <div class="bg-white/10 rounded-xl p-3 backdrop-blur-sm">🔹 Choisissez votre programme</div>
          <div class="bg-white/10 rounded-xl p-3 backdrop-blur-sm">🔹 Indiquez votre niveau</div>
          <div class="bg-white/10 rounded-xl p-3 backdrop-blur-sm">🔹 Créez vos identifiants</div>
          <div class="bg-white/10 rounded-xl p-3 backdrop-blur-sm">🔹 Connectez-vous !</div>
        </div>
      </div>
    </div>

    <!-- Right panel -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12">
      <div class="w-full max-w-md">
        <div data-aos="fade-up">
          <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
            <Sparkles class="w-4 h-4" /><span>TICK'IN — Centre Informatique UGANC</span>
          </div>

          <template v-if="successMessage">
            <div class="text-center py-12" data-aos="fade-up">
              <div class="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mx-auto mb-4">
                <UserCheck class="w-8 h-8 text-accent-dark" />
              </div>
              <h1 class="text-2xl font-bold text-dark mb-3">Inscription réussie !</h1>
              <p class="text-muted mb-6">{{ successMessage }}</p>
              <router-link to="/login" class="inline-flex items-center gap-2 gradient-bg text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition">Se connecter <ArrowRight class="w-4 h-4" /></router-link>
            </div>
          </template>

          <template v-else>
            <!-- Form -->
            <h1 class="text-2xl lg:text-3xl font-bold text-dark mb-1">Inscription</h1>
            <p class="text-muted text-sm mb-6">Créez votre compte étudiant pour accéder à la plateforme.</p>

            <!-- Step indicator -->
            <div class="flex items-center gap-2 mb-6">
              <div v-for="s in 3" :key="s" :class="['flex items-center gap-2', s < 3 ? 'flex-1' : '']">
                <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all', step >= s ? 'gradient-bg text-white' : 'bg-dark/5 text-muted']">{{ s }}</div>
                <div v-if="s < 3" :class="['h-1 flex-1 rounded transition-all', step > s ? 'gradient-bg' : 'bg-dark/5']"></div>
              </div>
            </div>

            <form @submit.prevent="submit" class="space-y-4">
              <!-- Step 1: Identity -->
              <div v-if="step === 1">
                <p class="text-sm font-semibold text-dark mb-3">Informations personnelles</p>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-semibold text-dark mb-1">Prénom *</label>
                    <input v-model="form.first_name" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Votre prénom" />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-dark mb-1">Nom *</label>
                    <input v-model="form.last_name" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Votre nom" />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Genre *</label>
                  <div class="flex gap-3">
                    <label :class="['flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border-2 text-sm font-semibold cursor-pointer transition', form.genre === 'M' ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">
                      <input type="radio" v-model="form.genre" value="M" class="sr-only" /> Masculin
                    </label>
                    <label :class="['flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border-2 text-sm font-semibold cursor-pointer transition', form.genre === 'F' ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">
                      <input type="radio" v-model="form.genre" value="F" class="sr-only" /> Féminin
                    </label>
                  </div>
                </div>
                <div class="flex justify-end pt-2">
                  <button type="button" @click="step = 2" :disabled="!form.first_name || !form.last_name || !form.genre" class="gradient-bg text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50 flex items-center gap-2">Suivant <ArrowRight class="w-4 h-4" /></button>
                </div>
              </div>

              <!-- Step 2: Academic -->
              <div v-if="step === 2">
                <p class="text-sm font-semibold text-dark mb-3">Programme et niveau</p>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Programme *</label>
                  <div class="flex gap-3">
                    <label :class="['flex-1 flex flex-col items-center gap-1 py-3 rounded-xl border-2 text-sm font-semibold cursor-pointer transition', form.programme === 'Développement logiciel' ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">
                      <input type="radio" v-model="form.programme" value="Développement logiciel" class="sr-only" />
                      <BookOpen class="w-5 h-5" /> Développement logiciel
                    </label>
                    <label :class="['flex-1 flex flex-col items-center gap-1 py-3 rounded-xl border-2 text-sm font-semibold cursor-pointer transition', form.programme === 'NTIC' ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">
                      <input type="radio" v-model="form.programme" value="NTIC" class="sr-only" />
                      <GraduationCap class="w-5 h-5" /> NTIC
                    </label>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Niveau d'étude *</label>
                  <div class="grid grid-cols-5 gap-2">
                    <button v-for="n in ['L1', 'L2', 'L3', 'M1', 'M2']" :key="n" type="button" @click="form.niveau_etude = n" :class="['py-2.5 rounded-xl border-2 text-sm font-semibold transition', form.niveau_etude === n ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">{{ n }}</button>
                  </div>
                </div>
                <div class="flex justify-between pt-2">
                  <button type="button" @click="step = 1" class="px-5 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Retour</button>
                  <button type="button" @click="step = 3" :disabled="!form.programme || !form.niveau_etude" class="gradient-bg text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50 flex items-center gap-2">Suivant <ArrowRight class="w-4 h-4" /></button>
                </div>
              </div>

              <!-- Step 3: Credentials -->
              <div v-if="step === 3">
                <p class="text-sm font-semibold text-dark mb-3">Identifiants de connexion</p>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Nom d'utilisateur *</label>
                  <div class="relative">
                    <User class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <input v-model="form.username" required class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Choisissez un identifiant" />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Email (optionnel)</label>
                  <div class="relative">
                    <Mail class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <input v-model="form.email" type="email" class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="exemple@uganc.edu.gn" />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Mot de passe *</label>
                  <div class="relative">
                    <Lock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <input v-model="form.password" type="password" required class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Minimum 6 caractères" />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-dark mb-1">Confirmer le mot de passe *</label>
                  <div class="relative">
                    <Lock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <input v-model="form.confirmPassword" type="password" required class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Confirmez votre mot de passe" />
                  </div>
                </div>

                <div v-if="error" class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm">{{ error }}</div>

                <div class="flex justify-between pt-2">
                  <button type="button" @click="step = 2" class="px-5 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Retour</button>
                  <button type="submit" :disabled="loading || !form.username || !form.password || !form.confirmPassword" class="gradient-bg text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50 flex items-center gap-2">
                    <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span v-else>S'inscrire <ArrowRight class="w-4 h-4" /></span>
                  </button>
                </div>
              </div>
            </form>

          </template>

            <p class="text-center mt-6 text-sm text-muted">
              Déjà un compte ?
              <router-link to="/login" class="text-primary hover:text-primary-dark font-medium">Connectez-vous</router-link>
            </p>
            <p class="text-center mt-2 text-sm text-muted">
              <router-link to="/" class="text-primary hover:text-primary-dark transition font-medium">← Retour à l'accueil</router-link>
            </p>
        </div>
      </div>
    </div>
  </div>
</template>
