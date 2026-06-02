<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Menu, X, ChevronRight, MessageSquare, MapPin, Clock, Bell,
  Monitor, ArrowRight, CheckCircle, Users, Star,
  Shield, Send, Phone, Mail, GraduationCap, Building2,
  ChevronDown, Play, Sparkles, Ticket
} from 'lucide-vue-next'

const router = useRouter()
const API = 'http://localhost:8000/api'

const testimonials = ref([])
const faqs = ref([])

// Navbar scroll effect
const scrolled = ref(false)
const mobileOpen = ref(false)

const handleScroll = () => {
  scrolled.value = window.scrollY > 50
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  fetch(`${API}/testimonials/`).then(r => r.json()).then(d => testimonials.value = d).catch(() => {})
  fetch(`${API}/faqs/`).then(r => r.json()).then(d => faqs.value = d).catch(() => {})
})
onBeforeUnmount(() => window.removeEventListener('scroll', handleScroll))

// Stats counter animation
const stats = [
  { icon: Ticket, value: 1250, suffix: '+', label: 'Signalements traités' },
  { icon: Users, value: 580, suffix: '+', label: 'Utilisateurs actifs' },
  { icon: Star, value: 4.8, suffix: '/5', label: 'Satisfaction moyenne' },
  { icon: Clock, value: 24, suffix: 'h', label: 'Délai moyen de réponse' },
]
const statsVisible = ref(false)
const animatedValues = ref(stats.map(() => 0))
let statsAnimated = false

const observeStats = (entries) => {
  if (entries[0].isIntersecting && !statsAnimated) {
    statsAnimated = true
    stats.forEach((s, i) => {
      const duration = 2000
      const start = performance.now()
      const animate = (now) => {
        const elapsed = now - start
        const progress = Math.min(elapsed / duration, 1)
        const eased = 1 - Math.pow(1 - progress, 3)
        animatedValues.value[i] = Math.floor(eased * s.value)
        if (progress < 1) requestAnimationFrame(animate)
      }
      requestAnimationFrame(animate)
    })
  }
}

onMounted(() => {
  const observer = new IntersectionObserver(observeStats, { threshold: 0.3 })
  const el = document.getElementById('stats')
  if (el) observer.observe(el)
})

// FAQ accordion
const openFaq = ref(null)
</script>

<template>
  <div class="min-h-screen bg-secondary overflow-hidden">
    <!-- ===== NAVBAR ===== -->
    <nav :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-500',
      scrolled ? 'glass shadow-lg' : 'bg-transparent'
    ]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16 lg:h-20">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-2 group">
            <div class="w-9 h-9 gradient-bg rounded-lg flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
              <MessageSquare class="w-5 h-5 text-white" />
            </div>
            <div class="flex flex-col">
              <span class="text-lg font-bold text-dark leading-tight">TICK'IN</span>
              <span class="text-xs text-muted leading-tight -mt-0.5">Centre Info UGANC</span>
            </div>
          </router-link>

          <!-- Desktop nav -->
          <div class="hidden lg:flex items-center gap-8">
            <a v-for="item in ['Fonctionnalités', 'Comment ça marche', 'Statistiques', 'Témoignages', 'FAQ']"
               :key="item"
               :href="'#' + item.toLowerCase().replace(/\s/g, '-')"
               class="text-sm font-medium text-dark/70 hover:text-primary transition-colors duration-200 relative group cursor-pointer">
              {{ item }}
              <span class="absolute -bottom-1 left-0 w-0 h-0.5 gradient-bg rounded-full transition-all duration-300 group-hover:w-full"></span>
            </a>
            <button @click="router.push('/register')"
                    class="px-5 py-2 rounded-full text-sm font-semibold text-primary border-2 border-primary/30
                           hover:bg-primary/5 hover:border-primary transition-all duration-300">
              S'inscrire
            </button>
            <button @click="router.push('/login')"
                    class="gradient-bg text-white px-5 py-2 rounded-full text-sm font-semibold
                           transition-all duration-300 hover:shadow-lg hover:shadow-primary/30
                           hover:scale-105 active:scale-95">
              Connexion
            </button>
          </div>

          <!-- Mobile hamburger -->
          <button @click="mobileOpen = !mobileOpen" class="lg:hidden p-2 rounded-lg hover:bg-dark/5 transition">
            <Menu v-if="!mobileOpen" class="w-6 h-6 text-dark" />
            <X v-else class="w-6 h-6 text-dark" />
          </button>
        </div>

        <!-- Mobile menu -->
        <transition
          enter-active-class="transition-all duration-300 ease-out"
          leave-active-class="transition-all duration-200 ease-in"
          enter-from-class="max-h-0 opacity-0"
          enter-to-class="max-h-96 opacity-100"
          leave-from-class="max-h-96 opacity-100"
          leave-to-class="max-h-0 opacity-0"
        >
          <div v-if="mobileOpen" class="lg:hidden overflow-hidden border-t border-dark/5 pb-4">
            <div class="flex flex-col gap-2 pt-4">
              <a v-for="item in ['Fonctionnalités', 'Comment ça marche', 'Statistiques', 'Témoignages', 'FAQ']"
                 :key="item"
                 :href="'#' + item.toLowerCase().replace(/\s/g, '-')"
                 @click="mobileOpen = false"
                 class="px-3 py-2 rounded-lg text-sm font-medium text-dark/70 hover:text-primary hover:bg-primary/5 transition">
                {{ item }}
              </a>
              <button @click="router.push('/register'); mobileOpen = false"
                      class="mt-2 px-5 py-2.5 rounded-full text-sm font-semibold text-center border-2 border-primary/30 text-primary hover:bg-primary/5 transition">
                S'inscrire
              </button>
              <button @click="router.push('/login'); mobileOpen = false"
                      class="gradient-bg text-white px-5 py-2.5 rounded-full text-sm font-semibold text-center transition hover:shadow-lg">
                Connexion
              </button>
            </div>
          </div>
        </transition>
      </div>
    </nav>

    <!-- ===== HERO ===== -->
    <section class="relative min-h-screen flex items-center pt-20 overflow-hidden">
      <!-- Background decoration -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-40 w-96 h-96 bg-primary/10 rounded-full blur-3xl"></div>
        <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/20 rounded-full blur-3xl"></div>
        <div class="absolute top-1/3 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-2xl"></div>
      </div>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <!-- Left content -->
          <div data-aos="fade-up" data-aos-delay="100">
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Sparkles class="w-4 h-4" />
              <span>TICK'IN — Centre Informatique UGANC</span>
            </div>
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-dark leading-[1.1] mb-6">
              Signalez vos
              <span class="gradient-text">problèmes informatiques</span>
              en un clic
            </h1>
            <p class="text-lg text-muted leading-relaxed mb-8 max-w-lg">
              Une plateforme simple et rapide pour signaler vos incidents techniques,
              suivre leur traitement et évaluer la qualité du service.
            </p>
            <div class="flex flex-wrap gap-4">
              <button @click="router.push('/login')"
                      class="gradient-bg text-white px-7 py-3 rounded-full text-base font-semibold
                             transition-all duration-300 hover:shadow-xl hover:shadow-primary/25
                             hover:scale-105 active:scale-95 flex items-center gap-2 group">
                Connexion
                <ArrowRight class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
              </button>
              <button @click="router.push('/register')"
                      class="px-7 py-3 rounded-full text-base font-semibold text-primary border-2 border-primary/30
                             hover:bg-primary/5 hover:border-primary transition-all duration-300">
                S'inscrire
              </button>
              <a href="#fonctionnalités"
                 class="px-7 py-3 rounded-full text-base font-semibold text-dark/70 border-2 border-dark/10
                        hover:border-primary/30 hover:text-primary transition-all duration-300 flex items-center gap-2">
                En savoir plus
                <ChevronDown class="w-4 h-4" />
              </a>
            </div>

            <!-- Trust badges -->
            <div class="flex items-center gap-8 mt-12 pt-8 border-t border-dark/5">
              <div class="flex -space-x-2">
                <div v-for="color in ['bg-primary', 'bg-accent-dark', 'bg-danger', 'bg-warning']"
                     :key="color"
                     :class="['w-8 h-8 rounded-full border-2 border-white ' + color]"></div>
              </div>
              <div>
                <div class="flex items-center gap-1">
                  <Star v-for="i in 5" :key="i" class="w-4 h-4 text-warning fill-current" />
                </div>
                <p class="text-sm text-muted mt-0.5">Approuvé par <strong class="text-dark">580+</strong> utilisateurs</p>
              </div>
            </div>
          </div>

          <!-- Right illustration -->
          <div class="relative" data-aos="fade-up" data-aos-delay="300">
            <div class="relative bg-white rounded-2xl shadow-2xl shadow-primary/10 p-6 lg:p-8 border border-primary/5">
              <!-- Chat mockup -->
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 gradient-bg rounded-full flex items-center justify-center">
                    <Users class="w-4 h-4 text-white" />
                  </div>
                  <div class="flex-1">
                    <p class="text-xs text-muted font-medium">Technicien</p>
                    <div class="bg-primary/10 rounded-2xl rounded-tl-sm px-4 py-2.5 mt-1">
                      <p class="text-sm text-dark">Bonjour ! Décrivez votre problème informatique.</p>
                    </div>
                  </div>
                </div>
                <div class="flex items-start gap-3 flex-row-reverse">
                  <div class="w-8 h-8 bg-accent/30 rounded-full flex items-center justify-center">
                    <span class="text-xs font-bold text-dark">M</span>
                  </div>
                  <div class="flex-1 flex justify-end">
                    <p class="text-xs text-muted font-medium mb-1 text-right">Étudiant</p>
                    <div class="bg-accent/30 rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[80%]">
                      <p class="text-sm text-dark">L'écran de mon PC reste noir après la mise à jour.</p>
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <div class="h-8 w-8 rounded-full border-2 border-primary/30 flex items-center justify-center">
                    <div class="w-3 h-3 rounded-full bg-primary animate-pulse"></div>
                  </div>
                  <p class="text-xs text-muted italic">Un technicien vous répond dans quelques instants...</p>
                </div>
              </div>

              <!-- Decorative elements -->
              <div class="absolute -top-3 -right-3 w-16 h-16 bg-accent/10 rounded-full blur-xl"></div>
              <div class="absolute -bottom-4 -left-4 w-20 h-20 bg-primary/5 rounded-full blur-xl"></div>
            </div>

            <!-- Floating badge -->
            <div class="absolute -bottom-6 -right-6 bg-white rounded-xl shadow-lg p-4 hidden lg:flex items-center gap-3 border border-primary/5"
                 data-aos="fade-up" data-aos-delay="500">
              <div class="w-10 h-10 bg-accent/20 rounded-lg flex items-center justify-center">
                <CheckCircle class="w-5 h-5 text-accent-dark" />
              </div>
              <div>
                <p class="text-xs text-muted">Taux de résolution</p>
                <p class="text-lg font-bold text-dark">98.5%</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Scroll indicator -->
        <div class="flex justify-center mt-12 lg:mt-16 animate-bounce">
          <ChevronDown class="w-6 h-6 text-muted" />
        </div>
      </div>
    </section>

    <!-- ===== FEATURES ===== -->
    <section id="fonctionnalités" class="py-20 lg:py-28 relative">
      <div class="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center mb-16" data-aos="fade-up">
          <span class="text-primary font-semibold text-sm tracking-widest uppercase">Fonctionnalités</span>
          <h2 class="text-3xl sm:text-4xl font-bold text-dark mt-3 mb-4">Tout ce dont vous avez besoin</h2>
          <p class="text-muted max-w-xl mx-auto">Une plateforme complète pour gérer l'ensemble de vos incidents informatiques.</p>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          <div v-for="(f, i) in [
            { icon: Monitor, title: 'Signalement facile', desc: 'Décrivez votre problème en quelques clics avec localisation et catégorie.', color: 'bg-primary/10 text-primary' },
            { icon: MapPin, title: 'Localisation précise', desc: 'Indiquez le bâtiment, la salle et le poste concerné pour une intervention rapide.', color: 'bg-accent/20 text-accent-dark' },
            { icon: Clock, title: 'Suivi en temps réel', desc: 'Suivez l\'évolution de votre ticket à chaque étape : Ouvert → En cours → Résolu.', color: 'bg-danger/10 text-danger' },
            { icon: Bell, title: 'Notifications instantanées', desc: 'Recevez des alertes à chaque changement de statut ou nouveau message.', color: 'bg-warning/10 text-warning' },
          ]"
           :key="f.title"
           class="bg-white rounded-2xl p-6 card-hover border border-primary/5"
           :data-aos="'fade-up'" :data-aos-delay="i * 100">
            <div :class="['w-12 h-12 rounded-xl flex items-center justify-center mb-5 ' + f.color]">
              <component :is="f.icon" class="w-6 h-6" />
            </div>
            <h3 class="text-lg font-bold text-dark mb-2">{{ f.title }}</h3>
            <p class="text-sm text-muted leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== HOW IT WORKS ===== -->
    <section id="comment-ça-marche" class="py-20 lg:py-28 relative">
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/[0.02] rounded-full blur-3xl"></div>
      </div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center mb-16" data-aos="fade-up">
          <span class="text-primary font-semibold text-sm tracking-widest uppercase">Processus</span>
          <h2 class="text-3xl sm:text-4xl font-bold text-dark mt-3 mb-4">Comment ça marche ?</h2>
          <p class="text-muted max-w-xl mx-auto">Du signalement à la résolution, suivez chaque étape.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8 lg:gap-12 max-w-5xl mx-auto">
          <!-- Step 1-3 -->
          <div v-for="(step, i) in [
            { num: '01', title: 'Connectez-vous', desc: 'Administrateurs et techniciens : utilisez vos identifiants fournis par l\'administration. Étudiants : inscrivez-vous librement.', icon: GraduationCap },
            { num: '02', title: 'Créez un ticket', desc: 'Choisissez une catégorie, décrivez votre problème et indiquez votre localisation.', icon: Ticket },
            { num: '03', title: 'Suivez le traitement', desc: 'Un technicien prend en charge votre ticket. Échangez via la messagerie intégrée.', icon: MessageSquare },
          ]" :key="step.num"
           class="relative bg-white rounded-2xl p-6 card-hover border border-primary/5 text-center"
           :data-aos="'fade-up'" :data-aos-delay="i * 150">
            <div class="w-14 h-14 gradient-bg rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg shadow-primary/20">
              <component :is="step.icon" class="w-7 h-7 text-white" />
            </div>
            <span class="text-4xl font-black text-primary/10 absolute top-3 right-5">{{ step.num }}</span>
            <h3 class="text-lg font-bold text-dark mb-2">{{ step.title }}</h3>
            <p class="text-sm text-muted leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>

        <!-- Connector line (desktop) -->
        <div class="hidden md:flex justify-center mt-8">
          <div class="flex items-center gap-2 text-muted text-sm">
            <span class="w-2 h-2 rounded-full bg-primary"></span>
            <span class="w-16 h-px bg-gradient-to-r from-primary/30 to-accent/30"></span>
            <span class="w-2 h-2 rounded-full bg-accent"></span>
            <span class="w-16 h-px bg-gradient-to-r from-accent/30 to-primary/30"></span>
            <span class="w-2 h-2 rounded-full bg-primary"></span>
          </div>
        </div>

        <!-- Step 4-6 -->
        <div class="grid md:grid-cols-3 gap-8 lg:gap-12 max-w-5xl mx-auto mt-8">
          <div v-for="(step, i) in [
            { num: '04', title: 'Échangez en direct', desc: 'Discutez avec le technicien assigné via le chat intégré au ticket.', icon: Send },
            { num: '05', title: 'Problème résolu', desc: 'Le technicien marque le ticket comme résolu et vous en êtes notifié.', icon: CheckCircle },
            { num: '06', title: 'Évaluez le service', desc: 'Notez la qualité de la prise en charge et laissez un commentaire.', icon: Star },
          ]" :key="step.num"
           class="relative bg-white rounded-2xl p-6 card-hover border border-primary/5 text-center"
           :data-aos="'fade-up'" :data-aos-delay="300 + i * 150">
            <div class="w-14 h-14 gradient-bg rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg shadow-primary/20">
              <component :is="step.icon" class="w-7 h-7 text-white" />
            </div>
            <span class="text-4xl font-black text-primary/10 absolute top-3 right-5">{{ step.num }}</span>
            <h3 class="text-lg font-bold text-dark mb-2">{{ step.title }}</h3>
            <p class="text-sm text-muted leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== STATS ===== -->
    <section id="statistiques" class="py-20 lg:py-28 relative">
      <div class="absolute inset-0 gradient-bg"></div>
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent_50%)]"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center mb-16" data-aos="fade-up">
          <span class="text-white/60 font-semibold text-sm tracking-widest uppercase">Chiffres</span>
          <h2 class="text-3xl sm:text-4xl font-bold text-white mt-3 mb-4">En quelques chiffres</h2>
          <p class="text-white/70 max-w-xl mx-auto">Notre engagement pour un service informatique de qualité.</p>
        </div>

        <div id="stats" class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          <div v-for="(s, i) in stats" :key="s.label"
               class="text-center p-6 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/10"
               :data-aos="'fade-up'" :data-aos-delay="i * 100">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <component :is="s.icon" class="w-6 h-6 text-white" />
            </div>
            <div class="text-4xl font-bold text-white mb-1 tabular-nums">
              {{ animatedValues[i] }}<span class="text-accent">{{ s.suffix }}</span>
            </div>
            <p class="text-white/70 text-sm">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== TESTIMONIALS ===== -->
    <section id="témoignages" class="py-20 lg:py-28 relative">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16" data-aos="fade-up">
          <span class="text-primary font-semibold text-sm tracking-widest uppercase">Témoignages</span>
          <h2 class="text-3xl sm:text-4xl font-bold text-dark mt-3 mb-4">Ce qu'ils disent</h2>
          <p class="text-muted max-w-xl mx-auto">Découvrez les retours de nos utilisateurs.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-6 lg:gap-8">
          <div v-for="(t, i) in testimonials" :key="t.id"
           class="bg-white rounded-2xl p-6 card-hover border border-primary/5"
           :data-aos="'fade-up'" :data-aos-delay="i * 150">
            <div class="flex items-center gap-1 mb-4">
              <Star v-for="s in t.stars" :key="s" class="w-4 h-4 text-warning fill-current" />
              <Star v-for="s in 5 - t.stars" :key="'e' + s" class="w-4 h-4 text-dark/10 fill-current" />
            </div>
            <p class="text-sm text-muted leading-relaxed mb-5 italic">"{{ t.text }}"</p>
            <div class="flex items-center gap-3 pt-4 border-t border-dark/5">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold text-primary">
                {{ t.name[0] }}
              </div>
              <div>
                <p class="text-sm font-bold text-dark">{{ t.name }}</p>
                <p class="text-xs text-muted">{{ t.role }}</p>
              </div>
            </div>
          </div>
          <p v-if="testimonials.length === 0" class="col-span-3 text-center text-muted text-sm py-8">Aucun temoignage pour le moment</p>
        </div>
      </div>
    </section>

    <!-- ===== FAQ ===== -->
    <section id="faq" class="py-20 lg:py-28 bg-gradient-bg-light">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16" data-aos="fade-up">
          <span class="text-primary font-semibold text-sm tracking-widest uppercase">FAQ</span>
          <h2 class="text-3xl sm:text-4xl font-bold text-dark mt-3 mb-4">Questions fréquentes</h2>
        </div>

        <div class="space-y-3">
          <div v-for="(faq, i) in faqs" :key="i"
               class="bg-white rounded-xl overflow-hidden border border-primary/5 card-hover"
               :data-aos="'fade-up'" :data-aos-delay="i * 80">
            <button @click="openFaq = openFaq === i ? null : i"
                    class="w-full flex items-center justify-between p-5 text-left transition">
              <span class="font-semibold text-dark pr-4">{{ faq.question }}</span>
              <ChevronDown :class="[
                'w-5 h-5 text-muted transition-transform duration-300 flex-shrink-0',
                openFaq === i ? 'rotate-180 text-primary' : ''
              ]" />
            </button>
            <transition
              enter-active-class="transition-all duration-300 ease-out"
              leave-active-class="transition-all duration-200 ease-in"
              enter-from-class="max-h-0 opacity-0"
              enter-to-class="max-h-96 opacity-100"
              leave-from-class="max-h-96 opacity-100"
              leave-to-class="max-h-0 opacity-0"
            >
              <div v-if="openFaq === i" class="overflow-hidden">
                <p class="px-5 pb-5 text-sm text-muted leading-relaxed">{{ faq.answer }}</p>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== CTA ===== -->
    <section class="py-20 lg:py-28 relative">
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/5 to-transparent"></div>
      </div>
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
        <div data-aos="fade-up">
          <div class="w-16 h-16 gradient-bg rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary/20">
            <Building2 class="w-8 h-8 text-white" />
          </div>
          <h2 class="text-3xl sm:text-4xl font-bold text-dark mb-4">Prêt à signaler un problème ?</h2>
          <p class="text-muted max-w-lg mx-auto mb-8">
            Connectez-vous dès maintenant à votre espace pour créer un ticket et
            bénéficier d'une prise en charge rapide par notre équipe technique.
          </p>
          <div class="flex flex-wrap justify-center gap-4">
            <button @click="router.push('/login')"
                    class="gradient-bg text-white px-8 py-3.5 rounded-full text-base font-semibold
                           transition-all duration-300 hover:shadow-xl hover:shadow-primary/25
                           hover:scale-105 active:scale-95 flex items-center gap-2 group">
              Connexion
              <ArrowRight class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
            </button>
            <button @click="router.push('/register')"
                    class="px-8 py-3.5 rounded-full text-base font-semibold text-primary border-2 border-primary/30
                           hover:bg-primary/5 hover:border-primary transition-all duration-300">
              S'inscrire
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== FOOTER ===== -->
    <footer class="bg-dark text-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
          <div>
            <div class="flex items-center gap-2 mb-4">
              <div class="w-9 h-9 gradient-bg rounded-lg flex items-center justify-center">
                <MessageSquare class="w-5 h-5 text-white" />
              </div>
              <div class="flex flex-col">
                <span class="text-lg font-bold leading-tight">TICK'IN</span>
                <span class="text-xs text-white/50 leading-tight -mt-0.5">Centre Info UGANC</span>
              </div>
            </div>
            <p class="text-sm text-white/60 leading-relaxed">
              TICK'IN — Plateforme officielle de signalement des incidents informatiques du Centre Informatique de l'UGANC.
            </p>
          </div>
          <div>
            <h4 class="font-semibold mb-4">Liens rapides</h4>
            <div class="flex flex-col gap-2 text-sm text-white/60">
              <a href="#fonctionnalités" class="hover:text-accent transition-colors">Fonctionnalités</a>
              <a href="#comment-ça-marche" class="hover:text-accent transition-colors">Comment ça marche</a>
              <a href="#statistiques" class="hover:text-accent transition-colors">Statistiques</a>
              <a href="#faq" class="hover:text-accent transition-colors">FAQ</a>
            </div>
          </div>
          <div>
            <h4 class="font-semibold mb-4">Contact</h4>
            <div class="flex flex-col gap-3 text-sm text-white/60">
              <div class="flex items-center gap-2">
                <Mail class="w-4 h-4 text-accent" />
                <span>admin@centre-info.uganc.edu.gn</span>
              </div>
              <div class="flex items-center gap-2">
                <Phone class="w-4 h-4 text-accent" />
                <span>610 935 524</span>
              </div>
              <div class="flex items-start gap-2">
                <MapPin class="w-4 h-4 text-accent mt-0.5" />
                <span>Centre Informatique UGANC, Conakry</span>
              </div>
            </div>
          </div>
          <div>
            <h4 class="font-semibold mb-4">Rôles</h4>
            <div class="flex flex-col gap-2 text-sm text-white/60">
              <div class="flex items-center gap-2">
                <Shield class="w-4 h-4 text-accent" />
                <span>Administrateur</span>
              </div>
              <div class="flex items-center gap-2">
                <Monitor class="w-4 h-4 text-accent" />
                <span>Technicien</span>
              </div>
              <div class="flex items-center gap-2">
                <GraduationCap class="w-4 h-4 text-accent" />
                <span>Étudiant</span>
              </div>
            </div>
          </div>
        </div>
        <div class="pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-white/40">
          <p>&copy; 2026 UGANC Centre Informatique. Groupe 7 — Tous droits réservés.</p>
          <p>Contact : <span class="text-accent font-medium">610 935 524</span></p>
        </div>
      </div>
    </footer>
  </div>
</template>
