<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '@/lib/api'
import AppLogo from '@/components/AppLogo.vue'
import AppNavProfile from '@/components/AppNavProfile.vue'

const isLoggedIn = !!sessionStorage.getItem('token')

const name = ref('')
const email = ref('')
const message = ref('')
const website = ref('') // Honeypot - ska ALLTID vara tomt, döljs med CSS

const isSending = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const chatMessages = ref<{ id: string; message: string; sender: 'user' | 'admin'; senderName: string; createdAt: string }[]>([])
const chatMessage = ref('')
const chatError = ref('')
const isSendingChat = ref(false)
const onlineAdmins = ref(0)
let chatTimer: number | undefined

async function loadChat() {
  if (!isLoggedIn) return
  try {
    const [chat, availability] = await Promise.all([api.get('/chat/mine'), api.get('/auth/chat/admins-online')])
    chatMessages.value = chat.data.messages
    onlineAdmins.value = availability.data.count
  }
  catch { chatError.value = 'Kunde inte ladda chatten just nu.' }
}
async function sendChat() {
  const text = chatMessage.value.trim()
  if (!text) return
  chatError.value = ''
  isSendingChat.value = true
  try {
    const response = await api.post('/chat/mine/messages', { message: text })
    chatMessages.value.push(response.data)
    chatMessage.value = ''
  } catch (error: any) {
    chatError.value = error.response?.data?.detail || 'Kunde inte skicka meddelandet.'
  } finally { isSendingChat.value = false }
}

onMounted(() => {
  if (!isLoggedIn) return
  email.value = sessionStorage.getItem('userEmail') || ''
  loadChat()
  chatTimer = window.setInterval(loadChat, 10000)
})
onBeforeUnmount(() => window.clearInterval(chatTimer))

async function submit() {
  errorMessage.value = ''
  successMessage.value = ''
  isSending.value = true
  try {
    const response = await api.post('/contact/', {
      name: name.value,
      email: email.value,
      message: message.value,
      website: website.value,
    })
    successMessage.value = response.data.message
    name.value = ''
    email.value = ''
    message.value = ''
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Kunde inte skicka meddelandet just nu.'
  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <header class="navbar">
      <AppLogo />
      <nav>
        <router-link to="/recipes">Alla recept</router-link>
        <router-link to="/contact" class="current">Kontakta oss</router-link>
        <template v-if="isLoggedIn"><AppNavProfile /></template>
        <router-link v-else to="/login" class="btn-outline">Logga in</router-link>
      </nav>
    </header>

    <main>
      <p class="eyebrow">HÖR AV DIG</p>
      <h1>Kontakta oss</h1>
      <p class="lead">Har du en fråga, en idé eller vill bara säga hej? Skriv till oss så svarar vi så snart vi kan.</p>

      <transition name="fade">
        <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
      </transition>

      <form v-if="!successMessage" class="contact-form" @submit.prevent="submit">
        <transition name="fade"><div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div></transition>

        <label>Namn<input v-model="name" type="text" required placeholder="Ditt namn" /></label>
        <label>E-post<input v-model="email" type="email" required placeholder="din@epost.se" :readonly="isLoggedIn" /><small v-if="isLoggedIn">E-postadressen hämtas från ditt inloggade konto.</small></label>
        <label>Meddelande<textarea v-model="message" rows="6" required placeholder="Skriv ditt meddelande här..."></textarea></label>

        <!-- Honeypot: osynligt för människor, men spam-robotar fyller ofta i det -->
        <div class="honeypot" aria-hidden="true">
          <label>Webbplats<input v-model="website" type="text" tabindex="-1" autocomplete="off" /></label>
        </div>

        <button type="submit" class="btn-primary" :disabled="isSending">{{ isSending ? 'Skickar...' : 'Skicka meddelande' }}</button>
      </form>

      <section v-if="isLoggedIn" class="chat-panel">
        <div class="chat-head"><div><p class="eyebrow">LIVECHATT</p><h2>Prata med en administratör</h2></div><span :class="{ offline: !onlineAdmins }">● {{ onlineAdmins ? `${onlineAdmins} admin${onlineAdmins === 1 ? '' : 's'} aktiv${onlineAdmins === 1 ? '' : 'a'}` : 'Ingen admin aktiv just nu' }}</span></div>
        <p v-if="chatError" class="error-banner">{{ chatError }}</p>
        <div class="chat-messages" aria-live="polite">
          <p v-if="!chatMessages.length" class="chat-empty">Starta en privat konversation med vårt team.</p>
          <div v-for="item in chatMessages" :key="item.id" class="chat-bubble" :class="item.sender">
            <small>{{ item.sender === 'admin' ? item.senderName || 'Administratör' : 'Du' }} · {{ new Date(item.createdAt).toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' }) }}</small>
            <p>{{ item.message }}</p>
          </div>
        </div>
        <form class="chat-compose" @submit.prevent="sendChat"><textarea v-model="chatMessage" rows="2" maxlength="2000" placeholder="Skriv ett meddelande till administratören..."></textarea><button type="submit" class="btn-primary" :disabled="isSendingChat || !chatMessage.trim()">{{ isSendingChat ? 'Skickar...' : 'Skicka' }}</button></form>
      </section>
    </main>
    <footer><span>Smaklig måltid!</span></footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #faf8f4; color: #382e2a; font-family: Georgia, 'Times New Roman', serif; }
.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }
nav { display: flex; align-items: center; gap: 1.5rem; } nav a { color: #756862; font: .78rem Arial, sans-serif; text-decoration: none; }
nav a.current { color: #bc6d4f; font-weight: 700; }
.btn-outline { border: 1px solid #e5d8cf; border-radius: 999px; padding: .4rem .9rem; }
main { width: min(640px, calc(100% - 3rem)); margin: 0 auto; padding: 3rem 0 4rem; text-align: center; }
.eyebrow { margin: 0 0 .5rem; color: #b6785b; font-family: Arial, sans-serif; font-size: .6rem; font-weight: bold; letter-spacing: .12em; }
h1 { margin: 0; font-size: clamp(1.9rem, 4vw, 2.6rem); }
.lead { max-width: 460px; margin: .9rem auto 2rem; color: #8c817b; font-family: Arial, sans-serif; font-size: .8rem; line-height: 1.6; }
.contact-form { display: flex; flex-direction: column; gap: 1.1rem; background: white; border: 1px solid #eee5de; border-radius: 10px; padding: 1.75rem; text-align: left; }
.contact-form label { display: flex; flex-direction: column; gap: .4rem; font: 600 .78rem Arial, sans-serif; color: #443e39; }
.contact-form label small { color: #96877f; font: 400 .68rem Arial, sans-serif; }
.contact-form input, .contact-form textarea { border: 1px solid #e2ddd5; border-radius: 8px; padding: .65rem .8rem; font: .85rem Arial, sans-serif; outline: none; resize: vertical; }
.contact-form input:focus, .contact-form textarea:focus { border-color: #c87a57; }
.honeypot { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
.btn-primary { background-color: #c87a57; color: white; border: none; padding: .8rem; border-radius: 25px; font-size: .9rem; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: .7; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background-color: #b36846; }
.error-banner { background-color: #fde8e8; color: #9b1c1c; padding: .75rem; border-radius: 8px; font-size: .85rem; }
.success-banner { background-color: #e8f5ea; color: #2a6b39; padding: 1rem; border-radius: 8px; font-size: .9rem; }
.chat-panel { margin-top: 1.5rem; border: 1px solid #eaded5; border-radius: 16px; background: #fffdfa; padding: 1rem; text-align: left; box-shadow: 0 8px 24px rgba(60,35,20,.06); }
.chat-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; padding: .2rem .2rem .85rem; border-bottom: 1px solid #eee3dc; }.chat-head .eyebrow { margin-bottom: .25rem; }.chat-head h2 { margin: 0; font-size: 1.05rem; }.chat-head span { color: #52835d; font: .67rem Arial, sans-serif; }.chat-head span.offline { color: #9a7c6d; }
.chat-messages { display: flex; flex-direction: column; gap: .55rem; min-height: 120px; max-height: 300px; overflow-y: auto; padding: .9rem .2rem; }.chat-empty { margin: auto; color: #978881; font: .76rem Arial, sans-serif; text-align: center; }.chat-bubble { max-width: 78%; padding: .6rem .75rem; border-radius: 12px; background: #f2ede8; color: #493d37; }.chat-bubble.user { align-self: flex-end; background: #c4623f; color: #fff; border-bottom-right-radius: 3px; }.chat-bubble.admin { align-self: flex-start; border-bottom-left-radius: 3px; }.chat-bubble small { display: block; margin-bottom: .2rem; opacity: .72; font: .61rem Arial, sans-serif; }.chat-bubble p { margin: 0; white-space: pre-wrap; font: .77rem/1.45 Arial, sans-serif; }.chat-compose { display: flex; gap: .6rem; align-items: flex-end; border-top: 1px solid #eee3dc; padding-top: .85rem; }.chat-compose textarea { flex: 1; border: 1px solid #dfd3ca; border-radius: 10px; padding: .6rem .7rem; resize: vertical; font: .78rem Arial, sans-serif; }.chat-compose .btn-primary { padding: .65rem .95rem; font-size: .75rem; }
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; } .fade-enter-from, .fade-leave-to { opacity: 0; }
footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }
</style>
