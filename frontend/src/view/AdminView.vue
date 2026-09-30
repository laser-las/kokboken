<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { api, type Recipe } from '@/lib/api'
import { useAuth } from '@/composables/useAuth'

type User = { email: string; role: 'user' | 'admin' }
type OnlineUser = { email: string; name: string; role: string; lastSeen: string }
type LoginLog = { id: string; email: string; loginTime: string; logoutTime: string | null; durationSeconds: number }
type ContactMessage = { id: string; name: string; email: string; message: string; createdAt: string; archivedAt?: string }
type ChatConversation = { id: string; userEmail: string; userName: string; lastMessage: string; lastSender: string; updatedAt: string; unreadForAdmin: number; status: 'open' | 'archived'; closedAt?: string | null }
type ChatMessage = { id: string; message: string; sender: 'user' | 'admin'; senderName: string; createdAt: string }
const users = ref<User[]>([])
const error = ref('')
const { logout } = useAuth()
const userEmail = sessionStorage.getItem('userEmail') || 'administratör'
const displayName = (userEmail.split('@')[0] || 'administratör').replace(/[._-]/g, ' ')

const activeTab = ref<'overview' | 'recipes' | 'categories' | 'live' | 'support' | 'letters' | 'letterArchive' | 'archive'>('overview')
const recipes = ref<Recipe[]>([])
const recipesError = ref('')
const recipeSearch = ref('')
const recipeStatus = ref<'all' | 'public' | 'draft'>('all')
const recipeCategory = ref('all')
const recipeSort = ref<'newest' | 'title' | 'time'>('newest')
const categories = ref<string[]>([])
const categoriesError = ref('')
const newCategory = ref('')
const isSavingCategory = ref(false)
const deletingEmail = ref('')
const contactMessages = ref<ContactMessage[]>([])
const archivedContactMessages = ref<ContactMessage[]>([])
const archivingLetterId = ref('')
const conversations = ref<ChatConversation[]>([])
const archivedConversations = ref<ChatConversation[]>([])
const selectedConversation = ref<ChatConversation | null>(null)
const selectedMessages = ref<ChatMessage[]>([])
const adminReply = ref('')
const supportError = ref('')
const isSendingReply = ref(false)
const isClosingConversation = ref(false)

const publicRecipes = computed(() => recipes.value.filter((recipe) => recipe.isPublic).length)
const draftRecipes = computed(() => recipes.value.filter((recipe) => !recipe.isPublic).length)
const recipeCategories = computed(() => [...new Set(recipes.value.map((recipe) => recipe.category).filter(Boolean))].sort())
const filteredRecipes = computed(() => {
  const query = recipeSearch.value.trim().toLocaleLowerCase('sv-SE')
  return [...recipes.value]
    .filter((recipe) => !query || `${recipe.title} ${recipe.category} ${recipe.createdBy}`.toLocaleLowerCase('sv-SE').includes(query))
    .filter((recipe) => recipeStatus.value === 'all' || (recipeStatus.value === 'public' ? recipe.isPublic : !recipe.isPublic))
    .filter((recipe) => recipeCategory.value === 'all' || recipe.category === recipeCategory.value)
    .sort((a, b) => recipeSort.value === 'title'
      ? a.title.localeCompare(b.title, 'sv-SE')
      : recipeSort.value === 'time'
        ? (parseDuration(a.time) - parseDuration(b.time))
        : String(b.updatedAt || b.createdAt || '').localeCompare(String(a.updatedAt || a.createdAt || '')))
})

const onlineUsers = ref<OnlineUser[]>([])
const onlineError = ref('')
const activityHours = ref<number[]>(Array(24).fill(0))
const activityPeak = ref(0)
const activityPeakHour = ref<number | null>(null)
const loginLogs = ref<LoginLog[]>([])
let pollTimer: number | undefined

async function loadUsers() {
  try { users.value = (await api.get('/auth/users')).data }
  catch { error.value = 'Kunde inte läsa användare. Kontrollera att du är administratör.' }
}
async function changeRole(user: User) {
  const role = user.role === 'admin' ? 'user' : 'admin'
  await api.patch(`/auth/users/${encodeURIComponent(user.email)}/role`, { role })
  await loadUsers()
}
async function deleteAccount(user: User) {
  if (!confirm(`Ta bort kontot ${user.email}? Det går inte att ångra.`)) return
  deletingEmail.value = user.email
  try {
    await api.delete(`/auth/users/${encodeURIComponent(user.email)}`)
    await loadUsers()
    await loadOnline()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kunde inte ta bort kontot.'
  } finally {
    deletingEmail.value = ''
  }
}

async function loadRecipes() {
  recipesError.value = ''
  try { recipes.value = (await api.get<Recipe[]>('/recipes/')).data }
  catch { recipesError.value = 'Kunde inte läsa recept.' }
}
async function deleteRecipe(recipe: Recipe) {
  if (!confirm(`Ta bort "${recipe.title}"?`)) return
  await api.delete(`/recipes/${recipe.slug}`)
  await loadRecipes()
}
function openRecipesTab() {
  activeTab.value = 'recipes'
  if (!recipes.value.length) loadRecipes()
}
function parseDuration(value: string) {
  const hours = Number(value.match(/(\d+)\s*h/i)?.[1] || 0)
  const minutes = Number(value.match(/(\d+)\s*min/i)?.[1] || (hours ? 0 : value.match(/\d+/)?.[0] || 0))
  return hours * 60 + minutes
}

async function loadCategories() {
  categoriesError.value = ''
  try { categories.value = (await api.get<string[]>('/categories/')).data }
  catch { categoriesError.value = 'Kunde inte läsa kategorier.' }
}
function openCategoriesTab() {
  activeTab.value = 'categories'
  if (!categories.value.length) loadCategories()
}
async function addCategory() {
  const name = newCategory.value.trim()
  if (!name) return
  isSavingCategory.value = true
  categoriesError.value = ''
  try {
    await api.post('/categories/', { name })
    newCategory.value = ''
    await loadCategories()
  } catch (e: any) {
    categoriesError.value = e.response?.data?.detail || 'Kunde inte lägga till kategorin.'
  } finally {
    isSavingCategory.value = false
  }
}
async function removeCategory(name: string) {
  if (!confirm(`Ta bort kategorin "${name}"?`)) return
  await api.delete(`/categories/${encodeURIComponent(name)}`)
  await loadCategories()
}

async function loadOnline() {
  onlineError.value = ''
  try { onlineUsers.value = (await api.get<OnlineUser[]>('/auth/admin/online')).data }
  catch { onlineError.value = 'Kunde inte läsa vilka som är inloggade.' }
}
async function loadActivity() {
  try {
    const data = (await api.get('/auth/admin/activity-today')).data
    activityHours.value = data.hours
    activityPeak.value = data.peak
    activityPeakHour.value = data.peakHour
  } catch { /* tyst - grafen är bara en bonus */ }
}
async function loadLoginLogs() { try { loginLogs.value = (await api.get<LoginLog[]>('/auth/admin/login-log')).data } catch { loginLogs.value = [] } }
function openLiveTab() {
  activeTab.value = 'live'
  loadOnline()
  loadActivity()
  loadLoginLogs()
}
async function loadSupport() {
  supportError.value = ''
  try {
    const chats = await api.get<ChatConversation[]>('/chat/admin/conversations')
    conversations.value = chats.data
    if (selectedConversation.value) {
      const fresh = chats.data.find((item) => item.id === selectedConversation.value?.id)
      if (fresh) selectedConversation.value = fresh
    }
  } catch { supportError.value = 'Kunde inte ladda inkorgen.' }
}
async function loadLetters() {
  supportError.value = ''
  try { contactMessages.value = (await api.get<ContactMessage[]>('/contact/admin')).data }
  catch { supportError.value = 'Kunde inte ladda breven.' }
}
async function loadLetterArchive() {
  supportError.value = ''
  try { archivedContactMessages.value = (await api.get<ContactMessage[]>('/contact/admin/archive')).data }
  catch { supportError.value = 'Kunde inte ladda brevarkivet.' }
}
async function archiveLetter(item: ContactMessage) {
  if (!confirm(`Arkivera brevet från ${item.name}?`)) return
  archivingLetterId.value = item.id
  supportError.value = ''
  try {
    await api.post(`/contact/admin/${item.id}/archive`)
    await Promise.all([loadLetters(), loadLetterArchive()])
  } catch (error: any) { supportError.value = error.response?.data?.detail || 'Kunde inte arkivera brevet.' }
  finally { archivingLetterId.value = '' }
}
async function selectConversation(conversation: ChatConversation) {
  selectedConversation.value = conversation
  adminReply.value = ''
  try {
    const response = await api.get(`/chat/admin/conversations/${conversation.id}`)
    selectedMessages.value = response.data.messages
    await loadSupport()
  } catch { supportError.value = 'Kunde inte ladda konversationen.' }
}
async function sendAdminReply() {
  if (!selectedConversation.value || !adminReply.value.trim()) return
  isSendingReply.value = true
  try {
    const response = await api.post(`/chat/admin/conversations/${selectedConversation.value.id}/messages`, { message: adminReply.value.trim() })
    selectedMessages.value.push(response.data)
    adminReply.value = ''
    await loadSupport()
  } catch (error: any) { supportError.value = error.response?.data?.detail || 'Kunde inte skicka svaret.' }
  finally { isSendingReply.value = false }
}
function openSupportTab() { activeTab.value = 'support'; loadSupport() }
function openLettersTab() { activeTab.value = 'letters'; loadLetters() }
function openLetterArchiveTab() { activeTab.value = 'letterArchive'; loadLetterArchive() }
async function loadArchive() {
  supportError.value = ''
  try { archivedConversations.value = (await api.get<ChatConversation[]>('/chat/admin/conversations/archive')).data }
  catch { supportError.value = 'Kunde inte ladda chattarkivet.' }
}
function openArchiveTab() {
  activeTab.value = 'archive'
  selectedConversation.value = null
  selectedMessages.value = []
  loadArchive()
}
async function closeConversation() {
  if (!selectedConversation.value || !confirm(`Avsluta chatten med ${selectedConversation.value.userName}? Den flyttas till arkivet.`)) return
  isClosingConversation.value = true
  supportError.value = ''
  try {
    await api.post(`/chat/admin/conversations/${selectedConversation.value.id}/close`)
    selectedConversation.value = null
    selectedMessages.value = []
    activeTab.value = 'archive'
    await Promise.all([loadSupport(), loadArchive()])
  } catch (error: any) { supportError.value = error.response?.data?.detail || 'Kunde inte avsluta chatten.' }
  finally { isClosingConversation.value = false }
}
function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z').getTime()
  const mins = Math.max(0, Math.round(diffMs / 60000))
  if (mins < 1) return 'just nu'
  if (mins === 1) return '1 min sedan'
  return `${mins} min sedan`
}
function duration(seconds: number) { const m = Math.floor(seconds / 60); return m >= 60 ? `${Math.floor(m / 60)} h ${m % 60} min` : `${m} min` }

watch(activeTab, (tab) => {
  window.clearInterval(pollTimer)
  if (tab === 'live' || tab === 'support' || tab === 'letters' || tab === 'letterArchive' || tab === 'archive') {
    pollTimer = window.setInterval(() => { if (tab === 'live') { loadOnline(); loadActivity(); loadLoginLogs() } else if (tab === 'support') loadSupport(); else if (tab === 'letters') loadLetters(); else if (tab === 'letterArchive') loadLetterArchive(); else loadArchive() }, 15000)
  }
})
onMounted(async () => {
  await Promise.all([loadUsers(), loadRecipes(), loadCategories(), loadLoginLogs()])
})
onBeforeUnmount(() => window.clearInterval(pollTimer))
</script>

<template>
  <div class="admin-shell">
    <aside>
      <router-link to="/recipes" class="brand"><b>▦</b> Köksboken</router-link>
      <p>STUDIO / ADMIN</p>
      <a href="#" :class="{ active: activeTab === 'overview' }" @click.prevent="activeTab = 'overview'">▦ Översikt</a>
      <a href="#" :class="{ active: activeTab === 'live' }" @click.prevent="openLiveTab">◉ Live</a>
      <a href="#" :class="{ active: activeTab === 'recipes' }" @click.prevent="openRecipesTab">▤ Recept</a>
      <a href="#" :class="{ active: activeTab === 'categories' }" @click.prevent="openCategoriesTab">◫ Kategorier</a>
      <a href="#" :class="{ active: activeTab === 'support' }" @click.prevent="openSupportTab">◉ Livechattar</a>
      <a href="#" :class="{ active: activeTab === 'letters' }" @click.prevent="openLettersTab">✉ Brev</a>
      <a href="#" :class="{ active: activeTab === 'letterArchive' }" @click.prevent="openLetterArchiveTab">▤ Brevarkiv</a>
      <a href="#" :class="{ active: activeTab === 'archive' }" @click.prevent="openArchiveTab">▤ Chattarkiv</a>
      <router-link to="/profile">♙ Min profil</router-link>
      <small>{{ displayName }}<br /><span>{{ userEmail }}</span></small>
      <button class="logout" type="button" @click="logout">Logga ut</button>
    </aside>
    <main>
      <header>
        <div><p>ADMIN / {{ ({overview:'ÖVERSIKT', live:'LIVE', recipes:'RECEPT', categories:'KATEGORIER', support:'LIVECHATTER', letters:'BREV', letterArchive:'BREVARKIV', archive:'CHATTARKIV'} as const)[activeTab] }}</p><h1>Välkommen tillbaka, {{ displayName }}.</h1></div>
        <router-link to="/recipes">Visa webbplatsen →</router-link>
      </header>

      <transition name="fade" mode="out-in">
      <template v-if="activeTab === 'overview'" key="overview">
        <div>
          <section class="metrics"><div><span>RECEPT</span><strong>{{ recipes.length || '–' }}</strong><small>Publicerade recept</small></div><div><span>ANVÄNDARE</span><strong>{{ users.length }}</strong><small>Registrerade konton</small></div><div><span>ADMINISTRATÖRER</span><strong>{{ users.filter(u => u.role === 'admin').length }}</strong><small>Med full behörighet</small></div><div><span>KATEGORIER</span><strong>{{ categories.length || '–' }}</strong><small>Tillgängliga att välja</small></div></section>
          <section class="dashboard-grid">
            <article class="panel wide">
              <div class="panel-head"><div><p>ANVÄNDARHANTERING</p><h2>Konton</h2></div><button @click="loadUsers">Uppdatera</button></div>
              <p v-if="error" class="error">{{ error }}</p>
              <div v-else class="users">
                <div v-for="user in users" :key="user.email">
                  <span>{{ user.email }}</span>
                  <em :class="user.role">{{ user.role }}</em>
                  <button @click="changeRole(user)">Gör till {{ user.role === 'admin' ? 'användare' : 'admin' }}</button>
                  <button class="danger" :disabled="deletingEmail === user.email" @click="deleteAccount(user)">{{ deletingEmail === user.email ? 'Tar bort...' : 'Ta bort konto' }}</button>
                </div>
                <p v-if="!users.length">Inga användare hittades ännu.</p>
              </div>
            </article>
            <article class="panel wide">
              <div class="panel-head"><div><p>INLOGGNINGSHISTORIK</p><h2>Senaste sessionerna</h2></div><button @click="loadLoginLogs">Uppdatera</button></div>
              <div class="login-log"><div v-for="entry in loginLogs" :key="entry.id"><span>{{ entry.email }}</span><span>{{ new Date(entry.loginTime).toLocaleString('sv-SE') }}</span><span>{{ entry.logoutTime ? 'Utloggad' : 'Inloggad nu' }}</span><strong>{{ duration(entry.durationSeconds) }}</strong></div><p v-if="!loginLogs.length">Inga registrerade sessioner ännu.</p></div>
            </article>
          </section>
        </div>
      </template>

      <template v-else-if="activeTab === 'live'" key="live">
        <div>
          <section class="dashboard-grid">
            <article class="panel wide">
              <div class="panel-head"><div><p>INLOGGADE JUST NU</p><h2>Online ({{ onlineUsers.length }})</h2></div><button @click="loadOnline">Uppdatera</button></div>
              <p v-if="onlineError" class="error">{{ onlineError }}</p>
              <div v-else class="online-list">
                <div v-for="u in onlineUsers" :key="u.email" class="online-row">
                  <span class="dot" /> <span class="who">{{ u.name }} <em class="user-email">{{ u.email }}</em></span> <em :class="u.role">{{ u.role }}</em> <span class="ago">{{ timeAgo(u.lastSeen) }}</span>
                </div>
                <p v-if="!onlineUsers.length">Ingen är inloggad just nu.</p>
              </div>
            </article>
            <article class="panel wide">
              <div class="panel-head"><div><p>AKTIVITET IDAG</p><h2>Aktiva konton per timme</h2></div><span v-if="activityPeakHour !== null" class="peak-label">Flest samtidigt: {{ activityPeak }} kl. {{ activityPeakHour }}–{{ activityPeakHour + 1 }}</span></div>
              <div class="bar-chart">
                <div v-for="(count, hour) in activityHours" :key="hour" class="bar-col" :title="`${hour}:00 – ${count} konto${count === 1 ? '' : 'n'}`">
                  <div class="bar" :style="{ height: (Math.max(...activityHours, 1) ? (count / Math.max(...activityHours, 1)) * 100 : 0) + '%' }" :class="{ filled: count > 0 }" />
                  <span v-if="hour % 3 === 0" class="bar-label">{{ hour }}</span>
                </div>
              </div>
            </article>
          </section>
        </div>
      </template>

      <template v-else-if="activeTab === 'support'" key="support">
        <section class="support-grid">
          <article class="panel inbox-panel">
            <div class="panel-head"><div><p>LIVECHATT</p><h2>Privata konversationer</h2></div><button @click="loadSupport">Uppdatera</button></div>
            <p v-if="supportError" class="error">{{ supportError }}</p>
            <button v-for="conversation in conversations" :key="conversation.id" type="button" class="conversation-row" :class="{ active: selectedConversation?.id === conversation.id }" @click="selectConversation(conversation)">
              <strong>{{ conversation.userName }}</strong><span>{{ conversation.userEmail }}</span><p>{{ conversation.lastMessage || 'Ingen text ännu' }}</p><em v-if="conversation.unreadForAdmin">{{ conversation.unreadForAdmin }} nya</em>
            </button>
            <p v-if="!conversations.length" class="empty-state">Inga chattsamtal ännu.</p>
          </article>
          <article class="panel chat-admin-panel">
            <template v-if="selectedConversation">
              <div class="panel-head"><div><p>CHATTA MED</p><h2>{{ selectedConversation.userName }}</h2></div><span class="chat-email">{{ selectedConversation.userEmail }}</span></div>
              <div class="admin-chat-messages"><div v-for="item in selectedMessages" :key="item.id" class="admin-bubble" :class="item.sender"><small>{{ item.sender === 'admin' ? item.senderName || 'Admin' : selectedConversation.userName }}</small><p>{{ item.message }}</p></div></div>
              <div class="admin-chat-actions"><button type="button" class="close-chat" :disabled="isClosingConversation" @click="closeConversation">{{ isClosingConversation ? 'Avslutar...' : 'Avsluta chatt' }}</button></div>
              <form class="admin-chat-compose" @submit.prevent="sendAdminReply"><textarea v-model="adminReply" rows="3" maxlength="2000" placeholder="Skriv ett svar..."></textarea><button type="submit" :disabled="isSendingReply || !adminReply.trim()">{{ isSendingReply ? 'Skickar...' : 'Skicka svar' }}</button></form>
            </template>
            <p v-else class="empty-state">Välj en konversation för att svara.</p>
          </article>
        </section>
      </template>

      <template v-else-if="activeTab === 'letters'" key="letters">
        <section class="dashboard-grid">
          <article class="panel wide support-contacts">
            <div class="panel-head"><div><p>KONTAKTA OSS</p><h2>Skickade brev</h2></div><button @click="loadLetters">Uppdatera</button></div>
            <p v-if="supportError" class="error">{{ supportError }}</p>
            <div v-for="item in contactMessages" :key="item.id" class="contact-row"><div><strong>{{ item.name }}</strong><span class="readonly-email" title="E-postadressen kan inte ändras">{{ item.email }} · {{ new Date(item.createdAt).toLocaleString('sv-SE') }}</span></div><p>{{ item.message }}</p><button class="archive-letter" :disabled="archivingLetterId === item.id" @click="archiveLetter(item)">{{ archivingLetterId === item.id ? 'Arkiverar...' : 'Arkivera' }}</button></div>
            <p v-if="!contactMessages.length" class="empty-state">Inga brev ännu.</p>
          </article>
        </section>
      </template>

      <template v-else-if="activeTab === 'letterArchive'" key="letter-archive">
        <section class="dashboard-grid">
          <article class="panel wide support-contacts">
            <div class="panel-head"><div><p>ARKIVERADE BREV</p><h2>Brevarkiv</h2></div><button @click="loadLetterArchive">Uppdatera</button></div>
            <p v-if="supportError" class="error">{{ supportError }}</p>
            <div v-for="item in archivedContactMessages" :key="item.id" class="contact-row"><div><strong>{{ item.name }}</strong><span class="readonly-email">{{ item.email }} · Arkiverat {{ new Date(item.archivedAt || item.createdAt).toLocaleString('sv-SE') }}</span></div><p>{{ item.message }}</p></div>
            <p v-if="!archivedContactMessages.length" class="empty-state">Inga arkiverade brev ännu.</p>
          </article>
        </section>
      </template>

      <template v-else-if="activeTab === 'archive'" key="archive">
        <section class="support-grid">
          <article class="panel inbox-panel">
            <div class="panel-head"><div><p>AVSLUTADE CHATTER</p><h2>Chattarkiv</h2></div><button @click="loadArchive">Uppdatera</button></div>
            <p v-if="supportError" class="error">{{ supportError }}</p>
            <button v-for="conversation in archivedConversations" :key="conversation.id" type="button" class="conversation-row" :class="{ active: selectedConversation?.id === conversation.id }" @click="selectConversation(conversation)">
              <strong>{{ conversation.userName }}</strong><span>{{ conversation.userEmail }}</span><p>{{ conversation.lastMessage || 'Ingen text ännu' }}</p><small class="archived-date">Avslutad {{ new Date(conversation.closedAt || conversation.updatedAt).toLocaleString('sv-SE') }}</small>
            </button>
            <p v-if="!archivedConversations.length" class="empty-state">Inga avslutade chattar ännu.</p>
          </article>
          <article class="panel chat-admin-panel">
            <template v-if="selectedConversation">
              <div class="panel-head"><div><p>ARKIVERAD CHATT</p><h2>{{ selectedConversation.userName }}</h2></div><span class="chat-email">{{ selectedConversation.userEmail }}</span></div>
              <div class="admin-chat-messages"><div v-for="item in selectedMessages" :key="item.id" class="admin-bubble" :class="item.sender"><small>{{ item.sender === 'admin' ? item.senderName || 'Admin' : selectedConversation.userName }}</small><p>{{ item.message }}</p></div></div>
              <p class="archive-readonly">Chatten är avslutad och skrivskyddad.</p>
            </template>
            <p v-else class="empty-state">Välj en arkiverad konversation för att läsa den.</p>
          </article>
        </section>
      </template>

      <template v-else-if="activeTab === 'recipes'" key="recipes">
        <section class="dashboard-grid">
          <article class="panel wide">
            <div class="panel-head"><div><p>RECEPTHANTERING</p><h2>Alla recept</h2></div><button @click="loadRecipes">Uppdatera</button></div>
            <div class="recipe-toolbar">
              <input v-model="recipeSearch" type="search" placeholder="Sök titel, kategori eller skapare" aria-label="Sök bland recept" />
              <select v-model="recipeStatus" aria-label="Filtrera på status"><option value="all">Alla statusar</option><option value="public">Publicerade</option><option value="draft">Utkast</option></select>
              <select v-model="recipeCategory" aria-label="Filtrera på kategori"><option value="all">Alla kategorier</option><option v-for="item in recipeCategories" :key="item" :value="item">{{ item }}</option></select>
              <select v-model="recipeSort" aria-label="Sortera recept"><option value="newest">Senast ändrad</option><option value="title">Namn A–Ö</option><option value="time">Kortast tid</option></select>
              <router-link to="/recipes/new" class="create-recipe">+ Nytt recept</router-link>
            </div>
            <p class="filter-summary">Visar {{ filteredRecipes.length }} av {{ recipes.length }} recept · {{ publicRecipes }} publicerade · {{ draftRecipes }} utkast</p>
            <p v-if="recipesError" class="error">{{ recipesError }}</p>
            <div v-else class="users">
              <div v-for="recipe in filteredRecipes" :key="recipe.slug" class="recipe-row">
                <span>{{ recipe.title }} <em class="user">{{ recipe.createdBy || 'okänd' }}</em> <em v-if="!recipe.isPublic" class="private">privat</em></span>
                <router-link :to="`/recipes/${recipe.slug}`" class="link-btn">Visa</router-link>
                <router-link :to="`/recipes/${recipe.slug}/edit`" class="link-btn">Redigera</router-link>
                <button @click="deleteRecipe(recipe)">Ta bort</button>
              </div>
              <p v-if="recipes.length && !filteredRecipes.length" class="empty-state">Inga recept matchar din filtrering.</p>
              <p v-if="!recipes.length">Inga recept hittades ännu.</p>
            </div>
          </article>
        </section>
      </template>

      <template v-else key="categories">
        <section class="dashboard-grid">
          <article class="panel wide">
            <div class="panel-head"><div><p>KATEGORIHANTERING</p><h2>Kategorier</h2></div><button @click="loadCategories">Uppdatera</button></div>
            <form class="add-category" @submit.prevent="addCategory">
              <input v-model="newCategory" type="text" placeholder="Ny kategori, t.ex. Vegetariskt" />
              <button type="submit" :disabled="isSavingCategory">{{ isSavingCategory ? 'Lägger till...' : 'Lägg till' }}</button>
            </form>
            <p v-if="categoriesError" class="error">{{ categoriesError }}</p>
            <div v-else class="users">
              <div v-for="cat in categories" :key="cat"><span>{{ cat }}</span><button @click="removeCategory(cat)">Ta bort</button></div>
              <p v-if="!categories.length">Inga kategorier tillagda ännu.</p>
            </div>
          </article>
        </section>
      </template>
      </transition>
    </main>
  </div>
</template>

<style scoped>
.admin-shell{min-height:100vh;display:grid;grid-template-columns:225px 1fr;background:#fcfbf9;color:#322923;font-family:Arial,sans-serif}.admin-shell aside{display:flex;flex-direction:column;padding:28px 18px;border-right:1px solid #eee6df;background:#fffdfa}.brand{color:#40332d;text-decoration:none;font:700 18px Georgia}.brand b{color:#c87554}.admin-shell aside p{margin:42px 10px 11px;color:#b6a8a0;font-size:11px;letter-spacing:.12em}.admin-shell aside>a{padding:10px 12px;border-radius:6px;color:#786a63;text-decoration:none;font-size:13px;cursor:pointer}.admin-shell aside .active{background:#fff0e9;color:#be6d50}.admin-shell aside small{margin-top:auto;color:#978981;font-size:11px;line-height:1.5}main{padding:36px 5%;max-width:1200px}header{display:flex;justify-content:space-between;align-items:start}header p,.panel p{margin:0 0 5px;color:#bc7153;font-size:11px;letter-spacing:.1em}h1{margin:0;font:700 32px Georgia}h2{margin:0;font:700 15px Georgia}header a{border:1px solid #e6d8d0;border-radius:5px;padding:9px 11px;color:#805c4d;font-size:11px;text-decoration:none}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:28px 0}.metrics div,.panel{border:1px solid #eee6df;border-radius:8px;background:#fff;padding:17px}.metrics span{display:block;color:#aa9b93;font-size:11px}.metrics strong{display:block;margin:10px 0 4px;font-size:27px}.metrics small{color:#aa9b93;font-size:12px}.dashboard-grid{display:grid;grid-template-columns:1fr;gap:14px}.panel.wide{min-height:180px}.panel-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}.panel-head>span,.panel button{border:1px solid #e9ddd5;border-radius:4px;background:white;padding:5px 8px;color:#88786f;font-size:11px;cursor:pointer}.users{margin-top:14px}.users>div{display:flex;align-items:center;gap:12px;padding:9px 0;border-top:1px solid #f1e9e3;font-size:12px}.users>div span{flex:1}.users em{border-radius:999px;padding:4px 7px;font-style:normal;font-size:10px;margin-left:6px}.users em.admin{background:#fff0e9;color:#b96545}.users em.user{background:#f2efeb;color:#786a63}.users em.private{background:#f3e2da;color:#a55c3f}.link-btn{border:1px solid #e9ddd5;border-radius:4px;background:white;padding:5px 8px;color:#88786f;font-size:11px;text-decoration:none}.error{color:#b64535}.danger{color:#b3453a !important;border-color:#f0d4cf !important}
.add-category{display:flex;gap:8px;margin-top:14px}.add-category input{flex:1;border:1px solid #e2ddd5;border-radius:6px;padding:8px 10px;font-size:13px}.add-category button{border:none;background:#c87050;color:white;border-radius:6px;padding:8px 14px;font-size:12px;cursor:pointer}.add-category button:disabled{opacity:.7;cursor:not-allowed}
.online-list{margin-top:10px}.online-row{display:flex;align-items:center;gap:10px;padding:9px 0;border-top:1px solid #f1e9e3;font-size:12px}.online-row:first-child{border-top:none}.dot{width:8px;height:8px;border-radius:50%;background:#3a8a52;box-shadow:0 0 0 3px #e4f3e8;flex-shrink:0}.who{flex:1}.user-email{color:#9a8c84;font-style:normal;font-size:11px;margin-left:6px}.ago{color:#9a8c84;font-size:11px}.peak-label{color:#8c7c73;font-size:11px}
.login-log{margin-top:10px}.login-log>div{display:grid;grid-template-columns:1.5fr 1.5fr 1fr .6fr;gap:8px;padding:9px 0;border-top:1px solid #f1e9e3;font-size:11px}.login-log strong{font-weight:600;color:#665850}
.bar-chart{display:flex;align-items:flex-end;gap:4px;height:120px;margin-top:16px;padding-top:8px}.bar-col{flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end;gap:6px}.bar{width:100%;max-width:16px;border-radius:3px 3px 0 0;background:#f1e9e3;min-height:2px;transition:height .3s}.bar.filled{background:#c4623f}.bar-label{color:#b6a8a0;font-size:9px}
.fade-enter-active,.fade-leave-active{transition:opacity .16s ease}.fade-enter-from,.fade-leave-to{opacity:0}
.recipe-toolbar{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}.recipe-toolbar input,.recipe-toolbar select{min-height:34px;box-sizing:border-box;border:1px solid #e2ddd5;border-radius:7px;background:#fff;padding:0 9px;color:#665850;font:12px Arial,sans-serif}.recipe-toolbar input{flex:1 1 220px}.recipe-toolbar input:focus,.recipe-toolbar select:focus{border-color:#c4623f;box-shadow:0 0 0 3px rgba(196,98,63,.12);outline:none}.create-recipe{display:inline-flex;align-items:center;justify-content:center;border-radius:7px;background:#c4623f;padding:0 12px;color:#fff;font:600 12px Arial,sans-serif;text-decoration:none;box-shadow:0 4px 10px rgba(196,98,63,.2)}.create-recipe:hover{background:#a94e2f}.filter-summary{margin:12px 0 -2px !important;color:#9a8c84 !important;font-size:11px !important;letter-spacing:0 !important}.users>div.recipe-row{padding:11px 0}.empty-state{padding:18px 0;color:#88786f;font-size:12px}
.support-grid{display:grid;grid-template-columns:minmax(220px,.7fr) minmax(320px,1.3fr);gap:14px}.support-contacts{grid-column:1/-1}.conversation-row{position:relative;display:block;width:100%;padding:11px 9px;border:0;border-top:1px solid #f0e7e0;background:transparent;color:#554941;text-align:left;cursor:pointer}.conversation-row:hover,.conversation-row.active{background:#fff1ea}.conversation-row strong,.conversation-row span{display:block}.conversation-row strong{font-size:12px}.conversation-row span,.conversation-row p{color:#95857d;font-size:10px}.conversation-row p{overflow:hidden;margin:4px 0 0;text-overflow:ellipsis;white-space:nowrap}.conversation-row em{position:absolute;right:8px;top:10px;border-radius:999px;background:#c4623f;padding:3px 5px;color:#fff;font-size:9px;font-style:normal}.chat-admin-panel{display:flex;min-height:430px;flex-direction:column}.chat-email{color:#978881;font-size:10px}.admin-chat-messages{display:flex;flex:1;flex-direction:column;gap:7px;min-height:260px;max-height:380px;overflow-y:auto;margin:12px 0;padding:2px}.admin-bubble{max-width:78%;padding:8px 10px;border-radius:10px;background:#f1ece7;color:#493d37}.admin-bubble.admin{align-self:flex-end;background:#c4623f;color:#fff}.admin-bubble.admin p{color:#fff}.admin-bubble small{display:block;margin-bottom:3px;font-size:9px;opacity:.75}.admin-bubble p{margin:0;white-space:pre-wrap;font-size:12px;line-height:1.4}.admin-chat-actions{display:flex;justify-content:flex-end;margin:0 0 8px}.admin-chat-actions .close-chat{border-color:#edcfc4;color:#a7553e}.admin-chat-compose{display:flex;gap:8px;align-items:end}.admin-chat-compose textarea{flex:1;resize:vertical;border:1px solid #e2d7cf;border-radius:7px;padding:8px;font:12px Arial,sans-serif}.admin-chat-compose button{border:0;border-radius:7px;background:#c4623f;padding:9px 11px;color:#fff;font-size:11px;cursor:pointer}.archived-date,.archive-readonly{display:block;margin-top:7px;color:#978881;font-size:10px}.archive-readonly{border-top:1px solid #f0e7e0;padding-top:11px}.contact-row{padding:11px 0;border-top:1px solid #f0e7e0}.contact-row div{display:flex;justify-content:space-between;gap:10px}.contact-row strong{font-size:12px}.contact-row span{color:#978881;font-size:10px}.readonly-email{cursor:default}.contact-row p{margin:5px 0 0;color:#675950;font-size:12px;line-height:1.45;white-space:pre-wrap}.archive-letter{margin-top:8px;border:1px solid #e9ddd5;border-radius:4px;background:#fff;padding:5px 8px;color:#88786f;font-size:11px;cursor:pointer}.archive-letter:hover{border-color:#c87554;color:#a85f44}.archive-letter:disabled{cursor:wait;opacity:.6}
@media(max-width:760px){.admin-shell{grid-template-columns:1fr}.admin-shell aside{display:none}.metrics{grid-template-columns:repeat(2,1fr)}main{padding:25px 5%}.support-grid{grid-template-columns:1fr}.support-contacts{grid-column:auto}.contact-row div{display:block}.admin-chat-compose{flex-direction:column}.admin-chat-compose button{width:100%}}
.logout{margin-top:12px;border:1px solid #eaded6;border-radius:6px;background:#fff;padding:8px;color:#786a63;font-size:12px;cursor:pointer;text-align:left}.logout:hover{border-color:#d49a83;color:#b86648}
</style>
