<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import { onWs } from '../../services/websocket.js'
import {
  MessageSquare, Ticket, Search, X, LogOut, Bell,
  LayoutDashboard, Settings, Clock, AlertCircle,
  Wrench, Send, Mic, Paperclip, FileText, Image, Download,
  Trash2, Play, Pause, ChevronRight, CheckCircle, Star
} from 'lucide-vue-next'

const router = useRouter()
const user = authService.getUser()
const sidebarOpen = ref(false)
const logout = () => { authService.logout(); router.push('/login') }

const API = 'http://localhost:8000/api'
const token = authService.getToken()
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
const publicUrl = (attachmentId) => `${API}/uploads/public/${attachmentId}?token=${token}`
const attachmentUrl = (msg) => msg.attachment_id ? publicUrl(msg.attachment_id) : msg.attachment_url

const tickets = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref(0)

const { unreadNotifs } = useNotifications()

const statuses = [
  { id: 0, label: 'Tous' },
  { id: 1, label: 'Soumis' },
  { id: 2, label: 'En cours' },
  { id: 3, label: 'En attente' },
  { id: 4, label: 'En vérification' },
  { id: 5, label: 'Résolu' },
]
const statusOpts = [
  { id: 2, label: 'En cours' },
  { id: 3, label: 'En attente' },
  { id: 4, label: 'En vérification' },
  { id: 5, label: 'Résolu' },
]

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

const filteredTickets = computed(() => {
  let result = tickets.value
  if (!search.value) return result
  const q = search.value.toLowerCase()
  return result.filter(t =>
    t.ticket_number?.toLowerCase().includes(q) ||
    t.user_name?.toLowerCase().includes(q) ||
    t.category_name?.toLowerCase().includes(q)
  )
})

const statusColor = (sid) => {
  const map = { 1: 'text-yellow-600 bg-yellow-50', 2: 'text-blue-600 bg-blue-50', 3: 'text-indigo-600 bg-indigo-50', 4: 'text-orange-600 bg-orange-50', 5: 'text-green-600 bg-green-50' }
  return map[sid] || 'bg-gray-100'
}
const statusLabel = (sid) => statuses.find(s => s.id === sid)?.label || ''

// Status change modal
const showStatusModal = ref(false)
const selectedTicket = ref(null)
const newStatusId = ref(null)
const resolutionNotes = ref('')

const openStatus = (ticket) => {
  selectedTicket.value = ticket
  newStatusId.value = ticket.status_id
  resolutionNotes.value = ticket.resolution_notes || ''
  showStatusModal.value = true
}

const confirmStatus = async () => {
  if (!selectedTicket.value || !newStatusId.value) return
  try {
    const body = { status_id: newStatusId.value, resolution_notes: resolutionNotes.value || null }
    const res = await fetch(`${API}/tickets/${selectedTicket.value.id}/status`, {
      method: 'PATCH', headers, body: JSON.stringify(body)
    })
    if (!res.ok) return
    showStatusModal.value = false
    selectedTicket.value = null
    await fetchTickets()
  } catch {}
}

// Chat
const showChatModal = ref(false)
const messages = ref([])
const messageText = ref('')
const sendingMessage = ref(false)

const recording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const recordingTime = ref(0)
const recordingTimer = ref(null)
const recordingStream = ref(null)
let micStream = null
let recordedMime = ''

const chatUploading = ref(false)

const showFilePreview = ref(false)
const previewFile = ref(null)
const previewUrl = ref('')
const previewFileInput = ref(null)

const deletingMsgId = ref(null)
const showConfirmDelete = ref(false)
const showConfirmConvDelete = ref(false)
const confirmConvTicketId = ref(null)

const playingAudio = ref(null)
const audioElement = ref(null)
const audioProgress = ref(0)
const audioDuration = ref(0)

const openChat = async (ticket) => {
  selectedTicket.value = ticket
  messages.value = []
  messageText.value = ''
  showChatModal.value = true
  try {
    const res = await fetch(`${API}/tickets/${ticket.id}/messages`, { headers })
    messages.value = (await res.json()).map(m => ({
      ...m,
      attachment_url: m.attachment_url ? `${API}${m.attachment_url}` : null,
      public_url: m.attachment_id ? publicUrl(m.attachment_id) : null,
    }))
    await scrollChat()
  } catch {}
}

const scrollChat = async () => {
  await nextTick()
  const el = document.querySelector('.chat-messages')
  if (el) el.scrollTop = el.scrollHeight
}

const sendMessage = async () => {
  if (!messageText.value.trim()) return
  sendingMessage.value = true
  try {
    const res = await fetch(`${API}/tickets/${selectedTicket.value.id}/messages`, {
      method: 'POST', headers, body: JSON.stringify({ message: messageText.value })
    })
    if (!res.ok) return
    const msg = await res.json()
    messages.value.push(msg)
    messageText.value = ''
    await scrollChat()
  } finally { sendingMessage.value = false }
}

// Recording
const formatRecordingTime = (s) => {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}

const toggleRecording = async () => {
  if (recording.value) { stopRecording() }
  else { await startRecording() }
}

const startRecording = async () => {
  try {
    if (!navigator.mediaDevices?.getUserMedia) {
      alert('Votre navigateur ne supporte pas l enregistrement audio')
      return
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    micStream = stream
    const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/aac', 'audio/ogg;codecs=opus', 'audio/ogg']
    const mimeType = types.find(t => MediaRecorder.isTypeSupported(t))
    if (!mimeType) { stream.getTracks().forEach(t => t.stop()); alert('Aucun format audio supporte'); return }
    recordedMime = mimeType
    mediaRecorder.value = new MediaRecorder(stream, { mimeType })
    audioChunks.value = []
    recordingTime.value = 0
    recording.value = true

    mediaRecorder.value.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.value.push(e.data)
    }
    mediaRecorder.value.onstop = () => {
      stream.getTracks().forEach(t => t.stop())
      micStream = null
    }
    mediaRecorder.value.start(250)
    recordingTimer.value = setInterval(() => { recordingTime.value++ }, 1000)
  } catch (err) {
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      alert('Autorisation du microphone requise. Veuillez autoriser l acces au microphone dans les parametres de votre navigateur.')
    } else {
      console.error('Mic error:', err)
      alert('Impossible d acceder au microphone')
    }
  }
}

const stopRecording = () => {
  if (!recording.value) return
  recording.value = false
  if (recordingTimer.value) { clearInterval(recordingTimer.value); recordingTimer.value = null }
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    const mime = recordedMime
    mediaRecorder.value.onstop = () => {
      const blob = new Blob(audioChunks.value, { type: mime })
      if (blob.size < 5000) {
        audioChunks.value = []
        if (micStream) { micStream.getTracks().forEach(t => t.stop()); micStream = null }
        return
      }
      uploadAudio(blob, mime)
      audioChunks.value = []
      if (micStream) { micStream.getTracks().forEach(t => t.stop()); micStream = null }
    }
    mediaRecorder.value.stop()
  }
}

const cancelRecording = () => {
  if (!recording.value) return
  recording.value = false
  if (recordingTimer.value) { clearInterval(recordingTimer.value); recordingTimer.value = null }
  audioChunks.value = []
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.ondataavailable = null
    mediaRecorder.value.onstop = null
    mediaRecorder.value.stop()
  }
  if (micStream) { micStream.getTracks().forEach(t => t.stop()); micStream = null }
}

const uploadAudio = async (blob, mime) => {
  chatUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', blob, `voice-${Date.now()}.webm`)
    fd.append('message_type', 'audio')
    const res = await fetch(`${API}/uploads/tickets/${selectedTicket.value.id}`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd
    })
    if (!res.ok) return
    const result = await res.json()
    messages.value.push({
      id: result.message_id,
      ticket_id: selectedTicket.value.id,
      sender_id: user?.id,
      sender_name: user?.nom || 'Moi',
      message: 'Message vocal',
      message_type: 'audio',
      is_deleted: false,
      attachment_id: result.id,
      attachment_url: `${API}/uploads/files/${result.id}`,
      public_url: publicUrl(result.id),
      attachment_name: result.file_name,
      attachment_type: mime,
      is_read: false,
      created_at: new Date().toISOString(),
    })
    await scrollChat()
  } finally { chatUploading.value = false }
}

// File sharing
const chatFileSelected = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  previewFile.value = file
  if (file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = (ev) => { previewUrl.value = ev.target.result }
    reader.readAsDataURL(file)
  } else { previewUrl.value = '' }
  showFilePreview.value = true
  if (e.target) e.target.value = ''
}

const sendFilePreview = async () => {
  if (!previewFile.value) return
  chatUploading.value = true
  showFilePreview.value = false
  try {
    const file = previewFile.value
    let msgType = 'file'
    if (file.type.startsWith('image/')) msgType = 'image'
    else if (file.type.startsWith('video/')) msgType = 'video'
    else if (file.type.startsWith('audio/')) msgType = 'audio'
    const fd = new FormData()
    fd.append('file', file)
    fd.append('message_type', msgType)
    const res = await fetch(`${API}/uploads/tickets/${selectedTicket.value.id}`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd
    })
    if (!res.ok) return
    const result = await res.json()
    messages.value.push({
      id: result.message_id,
      ticket_id: selectedTicket.value.id,
      sender_id: user?.id,
      sender_name: user?.nom || 'Moi',
      message: file.name,
      message_type: msgType,
      is_deleted: false,
      attachment_id: result.id,
      attachment_url: `${API}/uploads/files/${result.id}`,
      public_url: publicUrl(result.id),
      attachment_name: file.name,
      attachment_type: file.type,
      is_read: false,
      created_at: new Date().toISOString(),
    })
    await scrollChat()
  } finally {
    chatUploading.value = false
    previewFile.value = null
    previewUrl.value = ''
  }
}

const cancelFilePreview = () => {
  showFilePreview.value = false
  previewFile.value = null
  previewUrl.value = ''
}

// Delete message
const confirmDeleteMessage = (msgId) => {
  deletingMsgId.value = msgId
  showConfirmDelete.value = true
}

const deleteMessage = async () => {
  if (!deletingMsgId.value) return
  try {
    await fetch(`${API}/tickets/${selectedTicket.value.id}/messages/${deletingMsgId.value}`, {
      method: 'DELETE', headers
    })
    const msg = messages.value.find(m => m.id === deletingMsgId.value)
    if (msg) { msg.is_deleted = true; msg.message = 'Ce message a ete supprime' }
  } catch {}
  showConfirmDelete.value = false
  deletingMsgId.value = null
}

// Delete conversation
const confirmDeleteConversation = (ticketId) => {
  confirmConvTicketId.value = ticketId
  showConfirmConvDelete.value = true
}

const deleteConversation = async () => {
  if (!confirmConvTicketId.value) return
  try {
    await fetch(`${API}/tickets/${confirmConvTicketId.value}/messages/`, {
      method: 'DELETE', headers
    })
    messages.value.forEach(m => { m.is_deleted = true; m.message = 'Ce message a ete supprime' })
  } catch {}
  showConfirmConvDelete.value = false
  confirmConvTicketId.value = null
}

// Audio player
const toggleAudio = async (msg) => {
  if (!audioElement.value) {
    audioElement.value = new Audio()
    audioElement.value.ontimeupdate = () => {
      audioProgress.value = audioElement.value.currentTime
      audioDuration.value = audioElement.value.duration || 0
    }
    audioElement.value.onerror = () => {
      playingAudio.value = null
    }
    audioElement.value.onended = () => {
      playingAudio.value = null
    }
  }
  if (playingAudio.value === msg.id) {
    audioElement.value.pause()
    playingAudio.value = null
    audioElement.value.src = ''
    return
  }
  playingAudio.value = msg.id
  try {
    const res = await fetch(`${API}/uploads/files/${msg.attachment_id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) { playingAudio.value = null; return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    audioElement.value.src = url
    audioElement.value.play().catch(() => { URL.revokeObjectURL(url); playingAudio.value = null })
  } catch {
    playingAudio.value = null
  }
}

const formatAudioTime = (s) => {
  if (!s || !isFinite(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

// Download
const downloadFromMsg = async (msg) => {
  if (!msg.attachment_id) return
  const res = await fetch(`${API}/uploads/files/${msg.attachment_id}`, { headers })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const ext = msg.attachment_name?.split('.').pop() || 'webm'
  const link = document.createElement('a')
  link.href = url; link.download = msg.attachment_name || `fichier.${ext}`
  link.click(); URL.revokeObjectURL(url)
}

const formatDate = (d) => {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
  catch { return '' }
}
const formatTime = (d) => {
  if (!d) return ''
  try { return new Date(d).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) }
  catch { return '' }
}

onMounted(() => {
  fetchTickets()
  onWs('new_message', (data) => {
    if (!showChatModal.value || !selectedTicket.value) return
    const m = data.message
    if (m && m.ticket_id === selectedTicket.value.id && m.sender_id !== user?.id) {
      messages.value.push(m)
      scrollChat()
    }
  })
})

onBeforeUnmount(() => {
  if (recordingTimer.value) clearInterval(recordingTimer.value)
  if (audioElement.value) { audioElement.value.pause(); audioElement.value = null }
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
        <router-link to="/technicien/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Ticket class="w-4 h-4" /> Tickets</router-link>
        <router-link to="/technicien/notifications" class="relative flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Bell class="w-4 h-4" /> Notifications<span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span></router-link>
        <router-link to="/technicien/parametres" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Settings class="w-4 h-4" /> Paramètres</router-link>
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
          <h1 class="text-lg font-bold text-dark">Mes tickets</h1>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div class="relative flex-1 max-w-xs">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input v-model="search" type="text" placeholder="Rechercher..." class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
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
                  <th class="text-right px-5 py-3.5 font-semibold text-dark">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in filteredTickets" :key="t.id" class="border-b border-primary/5 hover:bg-primary/[0.02] transition">
                  <td class="px-5 py-4">
                    <span class="font-mono font-semibold text-dark text-xs">{{ t.ticket_number }}</span>
                    <p class="text-xs text-muted mt-0.5">{{ formatDate(t.created_at) }}</p>
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
                  <td class="px-5 py-4 text-right">
                    <div class="flex items-center justify-end gap-1.5">
                      <button @click="openStatus(t)" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-primary hover:bg-primary/5 transition">Changer statut</button>
                      <button @click="openChat(t)" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-accent-dark hover:bg-accent/20 transition">Chat</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!loading && filteredTickets.length === 0">
                  <td colspan="6" class="px-5 py-12 text-center text-muted text-sm">Aucun ticket</td>
                </tr>
                <tr v-if="loading">
                  <td colspan="6" class="px-5 py-12 text-center"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>

    <teleport to="body">
      <div v-if="showStatusModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showStatusModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-sm shadow-2xl" data-aos="fade-up">
          <h2 class="text-lg font-bold text-dark mb-2">Changer le statut</h2>
          <p class="text-sm text-muted mb-4">Ticket <strong>{{ selectedTicket?.ticket_number }}</strong></p>
          <div class="space-y-2">
            <button v-for="opt in statusOpts" :key="opt.id" @click="newStatusId = opt.id"
              :class="['w-full text-left px-4 py-3 rounded-xl border-2 text-sm font-semibold transition', newStatusId === opt.id ? 'border-primary bg-primary/5 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">
              {{ opt.label }}
            </button>
          </div>
          <div v-if="newStatusId === 5" class="mt-4">
            <label class="block text-sm font-semibold text-dark mb-1">Notes de résolution</label>
            <textarea v-model="resolutionNotes" rows="3" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" placeholder="Décrivez la résolution..."></textarea>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="showStatusModal = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="confirmStatus" class="flex-1 gradient-bg text-white py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg">Confirmer</button>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showChatModal && selectedTicket" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showChatModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl w-full max-w-2xl shadow-2xl max-h-[90vh] flex flex-col" data-aos="fade-up">
          <div class="flex items-center justify-between px-6 py-4 border-b border-primary/5 flex-shrink-0">
            <div>
              <div class="flex items-center gap-2">
                <h2 class="text-lg font-bold text-dark">Chat</h2>
                <span :class="['inline-flex px-2.5 py-1 rounded-full text-xs font-medium', statusColor(selectedTicket.status_id)]">{{ selectedTicket.status_label }}</span>
              </div>
              <p class="text-xs text-muted mt-0.5">{{ selectedTicket.ticket_number }} — {{ selectedTicket.user_name }}</p>
            </div>
            <button @click="showChatModal = false" class="p-2 rounded-lg hover:bg-dark/5 transition"><X class="w-5 h-5 text-muted" /></button>
          </div>

          <div class="chat-messages flex-1 overflow-y-auto px-6 py-4 space-y-3 bg-[#e5ddd5] min-h-[300px] max-h-[500px]" style="background-image: url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23d4cfc6\' fill-opacity=\'0.25\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')">
            <div v-for="m in messages" :key="m.id" :class="['flex', m.is_deleted ? 'justify-center' : (m.sender_id === user?.id ? 'justify-end' : 'justify-start')]">
              <div v-if="m.is_deleted" class="text-xs text-gray-400 italic py-1">Ce message a ete supprime</div>
              <div v-else :class="['max-w-[80%] px-3 py-2 rounded-lg text-sm shadow-sm relative group', m.sender_id === user?.id ? 'bg-[#dcf8c6] text-dark rounded-br-sm ml-12' : 'bg-white text-dark rounded-bl-sm mr-12']">
                <p class="text-xs font-semibold opacity-60 mb-0.5">{{ m.sender_id === user?.id ? 'Moi' : m.sender_name }}</p>
                <div v-if="m.message_type === 'image' && m.attachment_url" class="py-1 -mx-3 -mt-2">
                  <img :src="attachmentUrl(m)" :alt="m.attachment_name || 'Image'"
                    class="w-full rounded-lg max-h-72 object-cover cursor-pointer"
                    @click="downloadFromMsg(m)" loading="lazy" />
                </div>
                <div v-else-if="m.message_type === 'video' && m.attachment_url" class="py-1 -mx-3 -mt-2">
                  <div class="relative rounded-lg overflow-hidden bg-black/5">
                    <video :src="attachmentUrl(m)" controls class="w-full max-h-72" preload="metadata" @click.stop></video>
                  </div>
                </div>
                <div v-else-if="m.message_type === 'audio' && m.attachment_url" class="flex items-center gap-2 py-1 min-w-[200px]">
                  <button @click="toggleAudio(m)" :class="['w-8 h-8 rounded-full flex items-center justify-center transition flex-shrink-0', playingAudio === m.id ? 'bg-primary/20 text-primary' : 'bg-primary/10 text-primary hover:bg-primary/20']">
                    <Play v-if="playingAudio !== m.id" class="w-4 h-4" />
                    <Pause v-else class="w-4 h-4" />
                  </button>
                  <div class="flex-1 h-1.5 bg-dark/10 rounded-full overflow-hidden relative">
                    <div class="h-full bg-primary rounded-full transition-all duration-200" :style="{ width: (playingAudio === m.id && audioDuration > 0 ? (audioProgress / audioDuration) * 100 : 0) + '%' }"></div>
                  </div>
                  <span class="text-xs text-muted w-10 text-right tabular-nums">{{ playingAudio === m.id ? formatAudioTime(audioProgress) : '' }}</span>
                </div>
                <div v-else-if="m.message_type === 'file' && m.attachment_url" class="flex items-center gap-3 py-1">
                  <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0"><FileText class="w-5 h-5 text-primary" /></div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-semibold text-dark truncate">{{ m.attachment_name || 'Fichier' }}</p>
                    <button @click="downloadFromMsg(m)" class="text-xs text-primary hover:underline flex items-center gap-1"><Download class="w-3 h-3" /> Télécharger</button>
                  </div>
                </div>
                <p v-else class="text-sm whitespace-pre-wrap break-words">{{ m.message }}</p>
                <div class="flex items-center justify-end gap-1 mt-0.5">
                  <span class="text-[10px] text-gray-500">{{ formatTime(m.created_at) }}</span>
                  <button v-if="m.sender_id === user?.id" @click.stop="confirmDeleteMessage(m.id)" class="opacity-0 group-hover:opacity-100 transition text-danger text-xs hover:underline"><Trash2 class="w-3 h-3" /></button>
                </div>
              </div>
            </div>
            <p v-if="messages.length === 0" class="text-center text-muted text-sm py-8">Aucun message. Soyez le premier à écrire.</p>
          </div>

          <div class="px-6 py-3 border-t border-primary/5 flex-shrink-0">
            <div v-if="recording" class="flex items-center gap-3 mb-3 p-3 bg-danger/5 rounded-xl">
              <div class="w-3 h-3 bg-danger rounded-full animate-pulse"></div>
              <span class="text-sm font-semibold text-danger">Enregistrement en cours</span>
              <span class="text-sm text-muted">{{ formatRecordingTime(recordingTime) }}</span>
              <div class="flex-1"></div>
              <button @click="cancelRecording" class="text-xs text-muted hover:text-danger transition flex items-center gap-1"><X class="w-3 h-3" /> Annuler</button>
            </div>
            <div class="flex gap-2 items-center">
              <label class="p-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition cursor-pointer" title="Joindre un fichier">
                <Paperclip class="w-4 h-4" />
                <input ref="previewFileInput" type="file" accept="image/jpeg,image/png,image/gif,application/pdf,audio/webm,audio/ogg,video/mp4,video/webm" @change="chatFileSelected" class="hidden" :disabled="chatUploading || recording" />
              </label>
              <button @click="toggleRecording"
                :class="['p-2.5 rounded-xl select-none transition', recording ? 'bg-danger text-white shadow-lg animate-pulse' : 'text-muted hover:bg-primary/5 hover:text-primary']"
                :title="recording ? 'Cliquez pour arreter' : 'Cliquez pour enregistrer un vocal'">
                <Mic class="w-4 h-4" />
              </button>
              <input v-model="messageText" @keyup.enter="sendMessage" type="text" placeholder="Écrivez votre message..." class="flex-1 px-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" :disabled="recording" />
              <button @click="sendMessage" :disabled="sendingMessage || !messageText.trim() || recording" class="gradient-bg text-white p-2.5 rounded-xl disabled:opacity-50 transition hover:shadow-lg"><Send class="w-4 h-4" /></button>
            </div>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showConfirmDelete" class="fixed inset-0 z-[60] flex items-center justify-center p-4" @click.self="showConfirmDelete = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl text-center" data-aos="fade-up">
          <Trash2 class="w-10 h-10 text-danger mx-auto mb-3" />
          <h3 class="text-lg font-bold text-dark mb-2">Supprimer le message ?</h3>
          <p class="text-sm text-muted mb-5">Cette action est irreversible.</p>
          <div class="flex gap-3">
            <button @click="showConfirmDelete = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="deleteMessage" class="flex-1 py-2.5 rounded-xl bg-danger text-white text-sm font-semibold hover:bg-danger/80 transition">Supprimer</button>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showConfirmConvDelete" class="fixed inset-0 z-[60] flex items-center justify-center p-4" @click.self="showConfirmConvDelete = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl text-center" data-aos="fade-up">
          <Trash2 class="w-10 h-10 text-danger mx-auto mb-3" />
          <h3 class="text-lg font-bold text-dark mb-2">Supprimer toute la discussion ?</h3>
          <p class="text-sm text-muted mb-5">Tous les messages de ce ticket seront supprimes.</p>
          <div class="flex gap-3">
            <button @click="showConfirmConvDelete = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
            <button @click="deleteConversation" class="flex-1 py-2.5 rounded-xl bg-danger text-white text-sm font-semibold hover:bg-danger/80 transition">Supprimer</button>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showFilePreview" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="cancelFilePreview">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden" data-aos="fade-up">
          <div class="flex items-center justify-between px-6 py-4 border-b border-primary/5">
            <h3 class="text-sm font-bold text-dark">Apercu du fichier</h3>
            <button @click="cancelFilePreview" class="p-1.5 rounded-lg hover:bg-dark/5 transition"><X class="w-4 h-4 text-muted" /></button>
          </div>
          <div class="p-6">
            <div v-if="previewFile?.type?.startsWith('image/')" class="mb-4 rounded-xl overflow-hidden bg-secondary/50">
              <img :src="previewUrl" :alt="previewFile?.name" class="w-full h-auto max-h-64 object-contain" />
            </div>
            <div v-else class="mb-4 flex flex-col items-center justify-center py-8 bg-secondary/50 rounded-xl">
              <component :is="previewFile?.type?.startsWith('video/') ? Play : (previewFile?.type?.startsWith('audio/') ? Mic : FileText)" class="w-12 h-12 text-primary mb-3" />
              <p class="text-sm font-semibold text-dark text-center px-4 break-words">{{ previewFile?.name }}</p>
              <p class="text-xs text-muted mt-1">{{ previewFile ? (previewFile.size / 1024).toFixed(1) + ' Ko' : '' }}</p>
            </div>
            <div class="flex gap-3">
              <button @click="cancelFilePreview" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
              <button @click="sendFilePreview" :disabled="chatUploading" class="flex-1 gradient-bg text-white py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2">
                <span v-if="chatUploading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span v-else><Send class="w-4 h-4 inline" /> Envoyer</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>
