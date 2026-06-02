<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { authService } from '../../services/auth.js'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications.js'
import { onWs } from '../../services/websocket.js'
import {
  MessageSquare, LayoutDashboard, Ticket, Bell, Settings, LogOut,
  Plus, Search, X, AlertCircle, Clock, CheckCircle, Send,
  Paperclip, Download, Star, FileText, Image, User, Wrench,
  Mic, MicOff, Trash2, Phone, MoreVertical, Play, Pause
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

const allTickets = ref([])
const categories = ref([])
const rooms = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref(0)
const technicians = ref([])

const showCreate = ref(false)
const showDetail = ref(false)
const selectedTicket = ref(null)

const form = ref({ category_id: '', subcategory_id: '', room_id: '', workstation: '', description: '', priority: 'medium' })
const formFiles = ref([])
const fileError = ref('')
const creating = ref(false)
const createError = ref('')

const detailMessages = ref([])
const detailAttachments = ref([])
const detailEval = ref(null)
const messageText = ref('')
const sendingMessage = ref(false)

const evalRating = ref(0)
const evalComment = ref('')
const showEvalForm = ref(false)
const submittingEval = ref(false)

const recording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const recordingTime = ref(0)
const recordingTimer = ref(null)
const recordingStream = ref(null)

const deletingMsgId = ref(null)
const showConfirmDelete = ref(false)
const showConfirmConvDelete = ref(false)
const deleteTargetId = ref(null)
const confirmConvTicketId = ref(null)

const playingAudio = ref(null)
const audioElement = ref(null)
const audioProgress = ref(0)
const audioDuration = ref(0)

const chatUploading = ref(false)

const showFilePreview = ref(false)
const previewFile = ref(null)
const previewUrl = ref('')
const previewFileInput = ref(null)

const { unreadNotifs } = useNotifications()

const sliderEl = ref(null)
const sliderDragging = ref(false)
const slideStartX = ref(0)
const slideCancelThreshold = 80

const fetchData = async () => {
  loading.value = true
  try {
    const [t, c, r, techRes] = await Promise.all([
      fetch(`${API}/tickets?per_page=100`, { headers }).then(r => r.json()),
      fetch(`${API}/categories/`, { headers }).then(r => r.json()),
      fetch(`${API}/rooms/`, { headers }).then(r => r.json()),
      fetch(`${API}/users/technicians`, { headers }).then(r => r.json()).catch(() => []),
    ])
    allTickets.value = t.tickets || t
    categories.value = c
    rooms.value = r
    technicians.value = techRes
  } catch {}
  finally { loading.value = false }
}

const stats = computed(() => {
  const list = allTickets.value
  if (!Array.isArray(list)) return { total: 0, encours: 0, resolus: 0 }
  const total = list.length
  const encours = list.filter(t => [2, 3, 4].includes(t.status_id)).length
  const resolus = list.filter(t => t.status_id === 5).length
  return { total, encours, resolus }
})

const filteredTickets = computed(() => {
  let result = allTickets.value
  if (!Array.isArray(result)) return []
  if (statusFilter.value > 0) result = result.filter(t => t.status_id === statusFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    result = result.filter(t => t.ticket_number?.toLowerCase().includes(q) || t.description?.toLowerCase().includes(q) || t.category_name?.toLowerCase().includes(q) || t.technician_name?.toLowerCase().includes(q))
  }
  return result
})

const subcategories = computed(() => {
  const cat = categories.value.find(c => c.id === form.value.category_id)
  return cat?.subcategories || []
})

const statusLabel = (s) => ({ 1: 'Soumis', 2: 'En cours', 3: 'En attente', 4: 'En vérification', 5: 'Résolu' }[s] || s)
const statusColor = (s) => ({ 1: 'text-blue-600 bg-blue-50', 2: 'text-orange-600 bg-orange-50', 3: 'text-yellow-600 bg-yellow-50', 4: 'text-purple-600 bg-purple-50', 5: 'text-green-600 bg-green-50' }[s] || '')
const priorityLabel = (p) => ({ low: 'Basse', medium: 'Moyenne', high: 'Haute', critical: 'Critique' }[p] || p)
const priorityColor = (p) => ({ low: 'text-gray-600 bg-gray-100', medium: 'text-blue-600 bg-blue-50', high: 'text-orange-600 bg-orange-50', critical: 'text-red-600 bg-red-50' }[p] || '')

const handleFiles = (e) => {
  fileError.value = ''
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
  const maxSize = 2 * 1024 * 1024
  formFiles.value = []
  for (const f of e.target.files) {
    if (!allowed.includes(f.type)) { fileError.value = `Type "${f.type}" non autorise`; continue }
    if (f.size > maxSize) { fileError.value = `"${f.name}" depasse 2 Mo`; continue }
    formFiles.value.push(f)
  }
}

const createTicket = async () => {
  createError.value = ''
  creating.value = true
  try {
    const res = await fetch(`${API}/tickets/`, {
      method: 'POST', headers,
      body: JSON.stringify({
        category_id: form.value.category_id,
        subcategory_id: form.value.subcategory_id || null,
        room_id: form.value.room_id,
        workstation_number: form.value.workstation || null,
        description: form.value.description,
        priority: form.value.priority,
      })
    })
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Erreur') }
    const ticket = await res.json()

    if (formFiles.value.length > 0) {
      for (const file of formFiles.value) {
        const fd = new FormData()
        fd.append('file', file)
        await fetch(`${API}/uploads/tickets/${ticket.id}`, {
          method: 'POST', headers: { Authorization: `Bearer ${token}` },
          body: fd
        })
      }
    }

    showCreate.value = false
    form.value = { category_id: '', subcategory_id: '', room_id: '', workstation: '', description: '', priority: 'medium' }
    formFiles.value = []
    await fetchData()
  } catch (e) { createError.value = e.message }
  finally { creating.value = false }
}

const openDetail = async (t) => {
  selectedTicket.value = t
  detailMessages.value = []
  detailAttachments.value = []
  detailEval.value = null
  showEvalForm.value = false
  showDetail.value = true

  try {
    const [msgs, atts, ev] = await Promise.all([
      fetch(`${API}/tickets/${t.id}/messages`, { headers }).then(r => r.json()),
      fetch(`${API}/uploads/tickets/${t.id}`, { headers }).then(r => r.json()),
      fetch(`${API}/tickets/${t.id}/evaluation`, { headers }).then(r => r.ok ? r.json() : null),
    ])
    detailMessages.value = msgs.map(m => ({
      ...m,
      attachment_url: m.attachment_url ? `${API}${m.attachment_url}` : null,
      public_url: m.attachment_id ? publicUrl(m.attachment_id) : null,
    }))
    detailAttachments.value = atts
    detailEval.value = ev
    if (ev) showEvalForm.value = false
    else if (t.status_id === 5) showEvalForm.value = true
    await scrollChat()
  } catch {}
}

const scrollChat = async () => {
  await nextTick()
  const chatArea = document.querySelector('.chat-messages')
  if (chatArea) chatArea.scrollTop = chatArea.scrollHeight
}

const sendMessage = async () => {
  if (!messageText.value.trim()) return
  sendingMessage.value = true
  try {
    const res = await fetch(`${API}/tickets/${selectedTicket.value.id}/messages`, {
      method: 'POST', headers,
      body: JSON.stringify({ message: messageText.value })
    })
    if (!res.ok) return
    const msg = await res.json()
    detailMessages.value.push(msg)
    messageText.value = ''
    await scrollChat()
  } finally { sendingMessage.value = false }
}

let micStream = null
let recordedMime = ''

const formatRecordingTime = (s) => {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}

const toggleRecording = async () => {
  if (recording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
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
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    const mime = recordedMime
    mediaRecorder.value.onstop = () => {
      const blob = new Blob(audioChunks.value, { type: mime })
      if (blob.size < 100) {
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
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
  audioChunks.value = []
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.ondataavailable = null
    mediaRecorder.value.onstop = null
    mediaRecorder.value.stop()
  }
  if (micStream) {
    micStream.getTracks().forEach(t => t.stop())
    micStream = null
  }
}

const uploadAudio = async (blob, mime) => {
  chatUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', blob, `voice-${Date.now()}.webm`)
    fd.append('message_type', 'audio')
    const res = await fetch(`${API}/uploads/tickets/${selectedTicket.value.id}`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` },
      body: fd
    })
    if (!res.ok) return
    const result = await res.json()
    detailMessages.value.push({
      id: result.message_id,
      ticket_id: selectedTicket.value.id,
      sender_id: user?.id,
      sender_name: user?.nom || 'Vous',
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

const chatFileSelected = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  previewFile.value = file
  if (file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = (ev) => { previewUrl.value = ev.target.result }
    reader.readAsDataURL(file)
  } else {
    previewUrl.value = ''
  }
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
      method: 'POST', headers: { Authorization: `Bearer ${token}` },
      body: fd
    })
    if (!res.ok) return
    const result = await res.json()
    detailMessages.value.push({
      id: result.message_id,
      ticket_id: selectedTicket.value.id,
      sender_id: user?.id,
      sender_name: user?.nom || 'Vous',
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

const confirmDeleteMessage = (msgId) => {
  deleteTargetId.value = msgId
  showConfirmDelete.value = true
}

const deleteMessage = async () => {
  if (!deleteTargetId.value) return
  try {
    await fetch(`${API}/tickets/${selectedTicket.value.id}/messages/${deleteTargetId.value}`, {
      method: 'DELETE', headers
    })
    const msg = detailMessages.value.find(m => m.id === deleteTargetId.value)
    if (msg) {
      msg.is_deleted = true
      msg.message = 'Ce message a ete supprime'
    }
  } catch {}
  showConfirmDelete.value = false
  deleteTargetId.value = null
}

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
    detailMessages.value.forEach(m => {
      m.is_deleted = true
      m.message = 'Ce message a ete supprime'
    })
  } catch {}
  showConfirmConvDelete.value = false
  confirmConvTicketId.value = null
}

const toggleAudio = (msg) => {
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
    return
  }
  playingAudio.value = msg.id
  audioElement.value.src = attachmentUrl(msg)
  audioElement.value.play().catch(() => {
    playingAudio.value = null
  })
}

const formatAudioTime = (s) => {
  if (!s || !isFinite(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

const downloadFile = async (a) => {
  const res = await fetch(`${API}/uploads/files/${a.id}`, { headers: { Authorization: `Bearer ${token}` } })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url; link.download = a.file_name
  link.click(); URL.revokeObjectURL(url)
}

const downloadFromMsg = async (msg) => {
  if (!msg.attachment_id) return
  const res = await fetch(`${API}/uploads/files/${msg.attachment_id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const ext = msg.attachment_name?.split('.').pop() || 'webm'
  const link = document.createElement('a')
  link.href = url
  link.download = msg.attachment_name || `fichier.${ext}`
  link.click()
  URL.revokeObjectURL(url)
}

const submitEval = async () => {
  if (evalRating.value === 0) return
  submittingEval.value = true
  try {
    const res = await fetch(`${API}/tickets/${selectedTicket.value.id}/evaluation`, {
      method: 'POST', headers,
      body: JSON.stringify({ rating: evalRating.value, comment: evalComment.value || null })
    })
    if (!res.ok) return
    detailEval.value = { rating: evalRating.value, comment: evalComment.value }
    showEvalForm.value = false
  } finally { submittingEval.value = false }
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
  fetchData()
  onWs('new_message', (data) => {
    if (!showDetail.value || !selectedTicket.value) return
    const m = data.message
    if (m && m.ticket_id === selectedTicket.value.id && m.sender_id !== user?.id) {
      messages.value.push(m)
      scrollChat()
    }
  })
})
onUnmounted(() => {
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
          <div><span class="text-lg font-bold text-dark leading-tight">TICK'IN</span><span class="text-xs text-muted leading-tight -mt-0.5 block">Etudiant</span></div>
        </div>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/etudiant/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><LayoutDashboard class="w-4 h-4" /> Dashboard</router-link>
        <router-link to="/etudiant/tickets" class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/10 text-primary text-sm font-semibold"><Ticket class="w-4 h-4" /> Mes tickets</router-link>
        <router-link to="/etudiant/notifications" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm relative">
          <Bell class="w-4 h-4" /> Notifications
          <span class="absolute right-3 top-1/2 -translate-y-1/2 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1">{{ unreadNotifs > 99 ? '99+' : unreadNotifs }}</span>
        </router-link>
        <router-link to="/etudiant/parametres" class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition text-sm"><Settings class="w-4 h-4" /> Parametres</router-link>
      </nav>
      <div class="p-4 border-t border-primary/5">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-sm font-bold text-white">{{ user?.nom?.[0] || 'E' }}</div>
          <div class="flex-1 min-w-0"><p class="text-sm font-semibold text-dark truncate">{{ user?.nom || 'Etudiant' }}</p><p class="text-xs text-muted truncate">{{ user?.email }}</p></div>
        </div>
        <button @click="logout" class="flex items-center gap-2 w-full px-4 py-2 rounded-xl text-muted hover:bg-danger/5 hover:text-danger transition text-sm"><LogOut class="w-4 h-4" /> Deconnexion</button>
      </div>
    </aside>

    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/40 z-30 lg:hidden"></div>

    <div class="flex-1 flex flex-col min-h-screen">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-dark/5">
        <div class="flex items-center justify-between px-4 lg:px-8 h-16">
          <button @click="sidebarOpen = true" class="lg:hidden p-2 rounded-lg hover:bg-dark/5"><svg class="w-5 h-5 text-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
          <h1 class="text-lg font-bold text-dark">Mes tickets</h1>
          <button @click="showCreate = true" class="gradient-bg text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition hover:shadow-lg"><Plus class="w-4 h-4" /> Nouveau signalement</button>
        </div>
      </header>

      <main class="flex-1 p-4 lg:p-8 space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-white rounded-xl p-4 border border-primary/5"><div class="flex items-center gap-3"><div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center"><Ticket class="w-4 h-4" /></div><div><p class="text-xs text-muted">Total</p><p class="text-xl font-bold text-dark">{{ stats.total }}</p></div></div></div>
          <div class="bg-white rounded-xl p-4 border border-primary/5"><div class="flex items-center gap-3"><div class="w-9 h-9 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center"><Clock class="w-4 h-4" /></div><div><p class="text-xs text-muted">En cours</p><p class="text-xl font-bold text-dark">{{ stats.encours }}</p></div></div></div>
          <div class="bg-white rounded-xl p-4 border border-primary/5"><div class="flex items-center gap-3"><div class="w-9 h-9 rounded-xl bg-green-50 text-green-600 flex items-center justify-center"><CheckCircle class="w-4 h-4" /></div><div><p class="text-xs text-muted">Resolus</p><p class="text-xl font-bold text-dark">{{ stats.resolus }}</p></div></div></div>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div class="relative flex-1 max-w-xs">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input v-model="search" type="text" placeholder="Rechercher un ticket..." class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition" />
          </div>
          <div class="flex flex-wrap gap-2">
            <button @click="statusFilter = 0" :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition', statusFilter === 0 ? 'bg-primary text-white' : 'bg-white border border-dark/10 text-muted hover:border-primary']">Tous</button>
            <button v-for="(l, s) in {1:'Soumis',2:'En cours',3:'En attente',4:'En verification',5:'Resolu'}" :key="s" @click="statusFilter = (statusFilter === s ? 0 : s)" :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition', statusFilter === s ? 'bg-primary text-white' : 'bg-white border border-dark/10 text-muted hover:border-primary']">{{ l }}</button>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-primary/5 overflow-hidden">
          <div v-if="loading" class="p-12 text-center"><div class="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div><p class="text-sm text-muted mt-3">Chargement...</p></div>
          <div v-else-if="filteredTickets.length === 0" class="p-12 text-center text-muted text-sm">Aucun ticket trouve</div>
          <div v-else class="divide-y divide-primary/5">
            <div v-for="t in filteredTickets" :key="t.id" @click="openDetail(t)" class="px-5 py-4 hover:bg-primary/[0.02] transition cursor-pointer">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-dark text-sm">{{ t.ticket_number }}</span>
                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', statusColor(t.status_id)]">{{ statusLabel(t.status_id) }}</span>
                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', priorityColor(t.priority)]">{{ priorityLabel(t.priority) }}</span>
                  </div>
                  <p class="text-sm text-dark/80 mb-1">{{ t.description?.substring(0, 100) }}{{ t.description?.length > 100 ? '...' : '' }}</p>
                  <div class="flex items-center gap-3 text-xs text-muted">
                    <span>{{ t.category_name || '' }}</span>
                    <span>•</span>
                    <span>{{ t.room_name || `Salle #${t.room_id}` }}</span>
                    <span v-if="t.technician_name" class="flex items-center gap-1"><Wrench class="w-3 h-3" /> {{ t.technician_name }}</span>
                  </div>
                </div>
                <div class="text-xs text-muted text-right flex-shrink-0">
                  <div>{{ formatDate(t.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <teleport to="body">
      <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showCreate = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl p-6 lg:p-8 w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto" data-aos="fade-up">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-dark">Nouveau signalement</h2>
            <button @click="showCreate = false" class="p-2 rounded-lg hover:bg-dark/5 transition"><X class="w-5 h-5 text-muted" /></button>
          </div>
          <form @submit.prevent="createTicket" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Categorie *</label>
                <select v-model="form.category_id" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30">
                  <option value="" disabled>Selectionner</option>
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div v-if="subcategories.length > 0">
                <label class="block text-sm font-semibold text-dark mb-1">Sous-categorie</label>
                <select v-model="form.subcategory_id" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30">
                  <option value="">—</option>
                  <option v-for="s in subcategories" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Salle *</label>
                <select v-model="form.room_id" required class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30">
                  <option value="" disabled>Selectionner</option>
                  <option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.building_name ? `${r.building_name} — ` : '' }}{{ r.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold text-dark mb-1">Poste de travail</label>
                <input v-model="form.workstation" type="text" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" placeholder="Ex: PC-12" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Priorite</label>
              <div class="grid grid-cols-4 gap-2">
                <button type="button" v-for="(l, v) in {low:'Basse',medium:'Moyenne',high:'Haute',critical:'Critique'}" :key="v" @click="form.priority = v" :class="['px-3 py-2 rounded-lg text-xs font-semibold border-2 transition', form.priority === v ? 'border-primary bg-primary/10 text-primary' : 'border-dark/10 text-muted hover:border-primary/30']">{{ l }}</button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Description</label>
              <textarea v-model="form.description" rows="3" class="w-full px-3.5 py-2.5 rounded-xl border border-dark/10 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none" placeholder="Decrivez le probleme..."></textarea>
            </div>

            <div>
              <label class="block text-sm font-semibold text-dark mb-1">Pieces jointes <span class="text-muted font-normal">(images, PDF max 2 Mo)</span></label>
              <label class="flex items-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-dark/10 bg-secondary/50 cursor-pointer hover:border-primary/30 transition text-sm text-muted">
                <Paperclip class="w-4 h-4" />
                <span>{{ formFiles.length > 0 ? `${formFiles.length} fichier(s) selectionne(s)` : 'Cliquez pour ajouter des fichiers' }}</span>
                <input type="file" multiple accept="image/jpeg,image/png,image/gif,application/pdf" @change="handleFiles" class="hidden" />
              </label>
              <div v-if="fileError" class="mt-1 text-xs text-danger">{{ fileError }}</div>
              <div v-if="formFiles.length > 0" class="mt-2 space-y-1">
                <div v-for="(f, i) in formFiles" :key="i" class="flex items-center justify-between text-xs text-muted bg-secondary/50 px-3 py-1.5 rounded-lg">
                  <span>{{ f.name }} ({{ (f.size / 1024).toFixed(1) }} Ko)</span>
                  <button @click="formFiles.splice(i, 1)" class="text-danger hover:underline">Retirer</button>
                </div>
              </div>
            </div>

            <div v-if="createError" class="p-3 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm"><AlertCircle class="w-4 h-4 inline mr-1" /> {{ createError }}</div>

            <div class="flex gap-3 pt-2">
              <button type="button" @click="showCreate = false" class="flex-1 py-2.5 rounded-xl border-2 border-dark/10 text-sm font-semibold text-muted hover:bg-dark/5 transition">Annuler</button>
              <button type="submit" :disabled="creating" class="flex-1 gradient-bg text-white py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-lg disabled:opacity-50">
                <span v-if="creating" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block"></span>
                <span v-else>Envoyer</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showDetail && selectedTicket" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showDetail = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl w-full max-w-6xl h-[85vh] shadow-2xl flex overflow-hidden" data-aos="fade-up">
          
          <!-- WhatsApp-like Left Sidebar of Tickets inside Modal -->
          <div class="w-80 border-r border-primary/5 flex flex-col bg-secondary/30 flex-shrink-0 hidden md:flex">
            <div class="p-4 border-b border-primary/5 bg-white">
              <h3 class="text-sm font-bold text-dark mb-2">Mes discussions</h3>
              <div class="relative">
                <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted" />
                <input v-model="search" type="text" placeholder="Rechercher..." class="w-full pl-8 pr-3 py-1.5 rounded-lg border border-dark/10 bg-secondary/50 text-xs focus:outline-none focus:ring-1 focus:ring-primary/30" />
              </div>
            </div>
            <div class="flex-1 overflow-y-auto divide-y divide-primary/5 bg-white">
              <div v-for="t in filteredTickets" :key="t.id" @click="openDetail(t)" :class="['p-3.5 cursor-pointer transition hover:bg-primary/[0.02]', selectedTicket.id === t.id ? 'bg-primary/5 border-l-4 border-primary' : '']">
                <div class="flex justify-between items-start gap-2 mb-1">
                  <span class="font-semibold text-xs text-dark">{{ t.ticket_number }}</span>
                  <span class="text-[10px] text-muted">{{ formatTime(t.created_at) }}</span>
                </div>
                <p class="text-xs text-dark/70 truncate mb-1">{{ t.description }}</p>
                <div class="flex items-center justify-between">
                  <span :class="['inline-flex px-1.5 py-0.5 rounded text-[9px] font-medium', statusColor(t.status_id)]">{{ statusLabel(t.status_id) }}</span>
                  <span :class="['inline-flex px-1.5 py-0.5 rounded text-[9px] font-medium', priorityColor(t.priority)]">{{ priorityLabel(t.priority) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Chat Window Content (Right Panel) -->
          <div class="flex-1 flex flex-col h-full bg-secondary/10 min-w-0">
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-3 bg-white border-b border-primary/5 flex-shrink-0">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-10 h-10 rounded-full gradient-bg flex items-center justify-center text-sm font-bold text-white flex-shrink-0">
                  {{ selectedTicket.technician_name?.[0] || 'T' }}
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <h2 class="text-sm font-bold text-dark truncate">{{ selectedTicket.ticket_number }}</h2>
                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium', statusColor(selectedTicket.status_id)]">{{ statusLabel(selectedTicket.status_id) }}</span>
                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium', priorityColor(selectedTicket.priority)]">{{ priorityLabel(selectedTicket.priority) }}</span>
                  </div>
                  <p class="text-xs text-muted truncate mt-0.5">Technicien : {{ selectedTicket.technician_name || 'Non assigné' }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button @click="showDetail = false" class="p-2 rounded-lg hover:bg-dark/5 transition"><X class="w-5 h-5 text-muted" /></button>
              </div>
            </div>

            <!-- Context Info Sub-header -->
            <div class="px-6 py-2 border-b border-primary/5 flex-shrink-0 bg-secondary/50 text-xs text-muted flex flex-wrap gap-x-4 gap-y-1">
              <span>Catégorie : <strong class="text-dark font-medium">{{ selectedTicket.category_name || '' }}</strong></span>
              <span>•</span>
              <span>Salle : <strong class="text-dark font-medium">{{ selectedTicket.room_name || `Salle #${selectedTicket.room_id}` }}</strong></span>
              <span>•</span>
              <span>Poste : <strong class="text-dark font-medium">{{ selectedTicket.workstation_number || 'N/A' }}</strong></span>
            </div>

            <!-- Messages (WhatsApp styled with textured background) -->
            <div class="flex-1 overflow-y-auto px-6 py-4 space-y-3 bg-[#e5ddd5] chat-messages flex flex-col" style="background-image: url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23d4cfc6\' fill-opacity=\'0.25\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')">
              <div v-for="m in detailMessages" :key="m.id" :class="['flex w-full mb-1', m.is_deleted ? 'justify-center' : (m.sender_id === user?.id ? 'justify-end' : 'justify-start')]">
                <div v-if="m.is_deleted" class="text-xs text-gray-400 italic py-1 bg-white/60 px-3 rounded-lg shadow-sm">Ce message a été supprimé</div>

                <div v-else :class="['max-w-[85%] sm:max-w-[70%] px-3 py-2 rounded-xl text-sm shadow-sm relative group', m.sender_id === user?.id ? 'bg-[#dcf8c6] text-dark rounded-tr-none ml-12' : 'bg-white text-dark rounded-tl-none mr-12']">
                  <p class="text-[10px] font-bold text-primary/80 mb-0.5">{{ m.sender_id === user?.id ? 'Moi' : m.sender_name }}</p>

                  <div v-if="m.message_type === 'image' && m.attachment_url" class="py-1 -mx-1 -mt-1 mb-1">
                    <img :src="attachmentUrl(m)" :alt="m.attachment_name || 'Image'"
                      class="w-full rounded-lg max-h-72 object-cover cursor-pointer hover:opacity-90"
                      @click="downloadFromMsg(m)" loading="lazy" />
                  </div>

                  <div v-else-if="m.message_type === 'video' && m.attachment_url" class="py-1 -mx-1 -mt-1 mb-1">
                    <div class="relative rounded-lg overflow-hidden bg-black/5">
                        <video :src="attachmentUrl(m)" controls class="w-full max-h-72" preload="metadata" @click.stop></video>
                    </div>
                  </div>

                  <div v-else-if="m.message_type === 'audio' && m.attachment_url" class="flex items-center gap-2 py-1 min-w-[200px]">
                    <button @click="toggleAudio(m)" :class="['w-8 h-8 rounded-full flex items-center justify-center transition flex-shrink-0', playingAudio === m.id ? 'bg-primary/20 text-primary' : 'bg-primary/10 text-primary hover:bg-primary/20']">
                      <Play v-if="playingAudio !== m.id" class="w-4 h-4" />
                      <Pause v-else class="w-4 h-4" />
                    </button>
                    <div class="flex-1 h-1 bg-dark/10 rounded-full overflow-hidden relative">
                      <div class="h-full bg-primary rounded-full transition-all duration-200" :style="{ width: (playingAudio === m.id && audioDuration > 0 ? (audioProgress / audioDuration) * 100 : 0) + '%' }"></div>
                    </div>
                    <span class="text-[10px] text-muted w-10 text-right tabular-nums">{{ playingAudio === m.id ? formatAudioTime(audioProgress) : 'Vocal' }}</span>
                  </div>

                  <div v-else-if="m.message_type === 'file' && m.attachment_url" class="flex items-center gap-3 py-1">
                    <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <FileText class="w-5 h-5 text-primary" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs font-semibold text-dark truncate">{{ m.attachment_name || 'Fichier' }}</p>
                      <button @click="downloadFromMsg(m)" class="text-xs text-primary hover:underline flex items-center gap-1"><Download class="w-3 h-3" />Télécharger</button>
                    </div>
                  </div>

                  <p v-else class="text-sm whitespace-pre-wrap break-words">{{ m.message }}</p>

                  <div class="flex items-center justify-end gap-1 mt-1 text-[9px] text-gray-500">
                    <span>{{ formatTime(m.created_at) }}</span>
                    <button v-if="m.sender_id === user?.id" @click.stop="confirmDeleteMessage(m.id)" class="opacity-0 group-hover:opacity-100 transition text-danger hover:underline ml-1"><Trash2 class="w-2.5 h-2.5" /></button>
                  </div>
                </div>
              </div>
              <p v-if="detailMessages.length === 0" class="text-center text-muted text-sm py-8 bg-white/50 rounded-xl my-auto mx-auto px-6">Aucun message. Entamez la discussion avec votre technicien.</p>
            </div>

            <!-- Footer / Input bar -->
            <div class="p-4 bg-white border-t border-primary/5 flex-shrink-0 flex flex-col gap-2">
              <div v-if="recording" class="flex items-center gap-3 p-2 bg-danger/5 rounded-xl border border-danger/10">
                <div class="w-2.5 h-2.5 bg-danger rounded-full animate-pulse"></div>
                <span class="text-xs font-semibold text-danger">Enregistrement...</span>
                <span class="text-xs text-muted font-mono">{{ formatRecordingTime(recordingTime) }}</span>
                <div class="flex-1"></div>
                <button @click="cancelRecording" class="text-xs text-muted hover:text-danger transition flex items-center gap-1"><X class="w-3.5 h-3.5" /> Annuler</button>
              </div>

              <div class="flex gap-2 items-center">
                <label class="p-2.5 rounded-xl text-muted hover:bg-primary/5 hover:text-primary transition cursor-pointer flex-shrink-0" title="Joindre un fichier">
                  <Paperclip class="w-4 h-4" />
                  <input ref="previewFileInput" type="file" accept="image/jpeg,image/png,image/gif,application/pdf,audio/webm,audio/ogg,video/mp4,video/webm" @change="chatFileSelected" class="hidden" :disabled="chatUploading || recording" />
                </label>
                <button
                  @click="toggleRecording"
                  :class="['p-2.5 rounded-xl select-none transition flex-shrink-0', recording ? 'bg-danger text-white shadow-lg animate-pulse' : 'text-muted hover:bg-primary/5 hover:text-primary']"
                  :title="recording ? 'Arrêter et envoyer' : 'Enregistrer un vocal'"
                >
                  <Mic class="w-4 h-4" />
                </button>
                <input v-model="messageText" @keyup.enter="sendMessage" type="text" placeholder="Tapez votre message..." class="flex-1 px-4 py-2 rounded-xl border border-dark/10 bg-secondary/30 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" :disabled="recording" />
                <button @click="sendMessage" :disabled="sendingMessage || !messageText.trim() || recording" class="gradient-bg text-white p-2.5 rounded-xl disabled:opacity-50 transition hover:shadow-lg flex-shrink-0"><Send class="w-4 h-4" /></button>
              </div>

              <!-- Attachments / Options row -->
              <div v-if="detailAttachments.length > 0 || showEvalForm || detailEval" class="mt-2 border-t border-primary/5 pt-2 flex flex-wrap gap-2 items-center justify-between">
                <div v-if="detailAttachments.length > 0" class="flex flex-wrap gap-1">
                  <button v-for="a in detailAttachments" :key="a.id" @click="downloadFile(a)" class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-secondary text-[10px] text-muted hover:bg-primary/10 hover:text-primary border border-dark/5 transition">
                    <component :is="a.mime_type?.startsWith('image/') ? Image : FileText" class="w-3 h-3" />
                    <span class="truncate max-w-[120px]">{{ a.file_name }}</span>
                    <Download class="w-2.5 h-2.5 flex-shrink-0" />
                  </button>
                </div>
                
                <div v-if="showEvalForm" class="w-full mt-2">
                  <div class="bg-accent/10 border border-accent/20 rounded-xl p-3 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div>
                      <h4 class="text-xs font-bold text-dark">Résolution de l'incident</h4>
                      <p class="text-[10px] text-muted">Évaluez la prise en charge de ce ticket :</p>
                    </div>
                    <div class="flex items-center gap-2">
                      <div class="flex gap-1">
                        <button v-for="n in 3" :key="n" @click="evalRating = n" :class="['p-1 rounded transition', evalRating >= n ? 'text-yellow-500 bg-yellow-50' : 'text-gray-300 bg-gray-50']">
                          <Star class="w-5 h-5" :fill="evalRating >= n ? 'currentColor' : 'none'" />
                        </button>
                      </div>
                      <button @click="submitEval" :disabled="submittingEval || evalRating === 0" class="gradient-bg text-white px-3 py-1 rounded text-xs font-semibold disabled:opacity-50 transition">Évaluer</button>
                    </div>
                  </div>
                </div>

                <div v-if="detailEval" class="bg-accent/5 border border-accent/15 rounded-lg px-3 py-1.5 text-xs text-muted flex items-center gap-2">
                  <span>Votre évaluation :</span>
                  <span class="flex text-yellow-500">{{ [1,2,3].map(n => n <= detailEval.rating ? '★' : '☆').join('') }}</span>
                </div>
              </div>
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
