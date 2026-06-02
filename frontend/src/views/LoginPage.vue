<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth.js'
import { MessageSquare, Eye, EyeOff, Lock, User, ArrowRight, Sparkles } from 'lucide-vue-next'
import { UserPlus } from 'lucide-vue-next'

const router = useRouter()
const login = ref('')
const password = ref('')
const showPwd = ref(false)
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    const data = await authService.login(login.value, password.value)
    const route = authService.getDashboardRoute()
    router.push(route)
  } catch (e) {
    error.value = e.message || 'Identifiant ou mot de passe incorrect'
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <div class="min-h-screen bg-secondary flex">
    <!-- Left panel - brand -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden gradient-bg items-center justify-center p-12">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent_60%)]"></div>
      <div class="absolute top-10 left-10 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
      <div class="absolute bottom-10 right-10 w-48 h-48 bg-accent/10 rounded-full blur-3xl"></div>

      <div class="relative text-center max-w-md">
        <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 backdrop-blur-sm">
          <MessageSquare class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-4xl font-bold text-white mb-4">TICK'IN</h1>
        <p class="text-white/70 text-lg leading-relaxed">
          Plateforme de signalement des incidents informatiques. Connectez-vous pour accéder à votre espace.
        </p>
      </div>
    </div>

    <!-- Right panel - form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12">
      <div class="w-full max-w-md">
        <div data-aos="fade-up">
          <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
            <Sparkles class="w-4 h-4" />
            <span>Plateforme de signalement</span>
          </div>
          <h1 class="text-3xl font-bold text-dark mb-2">Connexion</h1>
          <p class="text-muted mb-8">Utilisez vos identifiants fournis par l'administration.</p>

          <form @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="block text-sm font-semibold text-dark mb-1.5">Identifiant / Email</label>
              <div class="relative">
                <User class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                <input v-model="login" required
                       class="w-full pl-10 pr-4 py-3 rounded-xl border border-dark/10 bg-white text-dark text-sm
                              focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
                              transition-all duration-200 placeholder:text-muted/50"
                       placeholder="Votre nom d'utilisateur ou email" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-dark mb-1.5">Mot de passe</label>
              <div class="relative">
                <Lock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                <input v-model="password" :type="showPwd ? 'text' : 'password'" required
                       class="w-full pl-10 pr-12 py-3 rounded-xl border border-dark/10 bg-white text-dark text-sm
                              focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
                              transition-all duration-200 placeholder:text-muted/50"
                       placeholder="••••••••" />
                <button type="button" @click="showPwd = !showPwd"
                        class="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted hover:text-dark transition">
                  <Eye v-if="!showPwd" class="w-4 h-4" />
                  <EyeOff v-else class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div v-if="error"
                 class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm"
                 data-aos="fade-up">
              {{ error }}
            </div>

            <button type="submit" :disabled="loading"
                    class="w-full gradient-bg text-white py-3 rounded-xl text-base font-semibold
                           transition-all duration-300 hover:shadow-lg hover:shadow-primary/25
                           disabled:opacity-50 disabled:cursor-not-allowed
                           flex items-center justify-center gap-2 group">
              <span v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span v-else>Se connecter</span>
              <ArrowRight v-if="!loading" class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
            </button>
          </form>

        </div>

        <!-- Register & Back links -->
        <p class="text-center mt-5 text-sm text-muted">
          Pas encore de compte ?
          <router-link to="/register" class="text-primary hover:text-primary-dark font-semibold">S'inscrire</router-link>
        </p>
        <p class="text-center mt-2 text-sm text-muted">
          <router-link to="/" class="text-primary hover:text-primary-dark transition font-medium">← Retour à l'accueil</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
