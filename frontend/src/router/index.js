import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '../services/auth.js'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('../views/LandingPage.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterPage.vue'),
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/DashboardPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/utilisateurs',
    name: 'AdminUsers',
    component: () => import('../views/admin/UsersPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/tickets',
    name: 'AdminTickets',
    component: () => import('../views/admin/TicketsPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/parametres',
    name: 'AdminSettings',
    component: () => import('../views/admin/SettingsPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/notifications',
    name: 'AdminNotifications',
    component: () => import('../views/admin/NotificationsPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/salles',
    name: 'AdminRooms',
    component: () => import('../views/admin/RoomsPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/technicien/tickets',
    name: 'TechnicienTickets',
    component: () => import('../views/technicien/TicketsPage.vue'),
    meta: { requiresAuth: true, role: 'technicien' },
  },
  {
    path: '/etudiant/tickets',
    name: 'EtudiantTickets',
    component: () => import('../views/etudiant/TicketsPage.vue'),
    meta: { requiresAuth: true, role: 'etudiant' },
  },
  {
    path: '/technicien/dashboard',
    name: 'TechnicienDashboard',
    component: () => import('../views/technicien/DashboardPage.vue'),
    meta: { requiresAuth: true, role: 'technicien' },
  },
  {
    path: '/technicien/notifications',
    name: 'TechnicienNotifications',
    component: () => import('../views/technicien/NotificationsPage.vue'),
    meta: { requiresAuth: true, role: 'technicien' },
  },
  {
    path: '/technicien/parametres',
    name: 'TechnicienSettings',
    component: () => import('../views/technicien/SettingsPage.vue'),
    meta: { requiresAuth: true, role: 'technicien' },
  },
  {
    path: '/etudiant/dashboard',
    name: 'EtudiantDashboard',
    component: () => import('../views/etudiant/DashboardPage.vue'),
    meta: { requiresAuth: true, role: 'etudiant' },
  },
  {
    path: '/etudiant/notifications',
    name: 'EtudiantNotifications',
    component: () => import('../views/etudiant/NotificationsPage.vue'),
    meta: { requiresAuth: true, role: 'etudiant' },
  },
  {
    path: '/etudiant/parametres',
    name: 'EtudiantSettings',
    component: () => import('../views/etudiant/SettingsPage.vue'),
    meta: { requiresAuth: true, role: 'etudiant' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const isAuth = authService.isAuthenticated()
  const user = authService.getUser()
  const corrupted = isAuth && !user

  if (corrupted) {
    authService.logout()
    return to.path === '/login' ? next() : next('/login')
  }

  if (to.meta.requiresAuth) {
    if (!isAuth) return next('/login')
    if (to.meta.role && user.role !== to.meta.role) {
      return next(authService.getDashboardRoute())
    }
    return next()
  }

  if (to.path === '/login' && isAuth) {
    return next()
  }

  next()
})

export default router
