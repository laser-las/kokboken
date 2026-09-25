<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/lib/api'
import AppLogo from '@/components/AppLogo.vue'
import AppNavProfile from '@/components/AppNavProfile.vue'

const isLoggedIn = !!localStorage.getItem('token')

const name = ref('')
const email = ref('')
const message = ref('')
const website = ref('') // Honeypot - ska ALLTID vara tomt, döljs med CSS

const isSending = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

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
        <label>E-post<input v-model="email" type="email" required placeholder="din@epost.se" /></label>
        <label>Meddelande<textarea v-model="message" rows="6" required placeholder="Skriv ditt meddelande här..."></textarea></label>

        <!-- Honeypot: osynligt för människor, men spam-robotar fyller ofta i det -->
        <div class="honeypot" aria-hidden="true">
          <label>Webbplats<input v-model="website" type="text" tabindex="-1" autocomplete="off" /></label>
        </div>

        <button type="submit" class="btn-primary" :disabled="isSending">{{ isSending ? 'Skickar...' : 'Skicka meddelande' }}</button>
      </form>
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
.contact-form input, .contact-form textarea { border: 1px solid #e2ddd5; border-radius: 8px; padding: .65rem .8rem; font: .85rem Arial, sans-serif; outline: none; resize: vertical; }
.contact-form input:focus, .contact-form textarea:focus { border-color: #c87a57; }
.honeypot { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
.btn-primary { background-color: #c87a57; color: white; border: none; padding: .8rem; border-radius: 25px; font-size: .9rem; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: .7; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background-color: #b36846; }
.error-banner { background-color: #fde8e8; color: #9b1c1c; padding: .75rem; border-radius: 8px; font-size: .85rem; }
.success-banner { background-color: #e8f5ea; color: #2a6b39; padding: 1rem; border-radius: 8px; font-size: .9rem; }
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; } .fade-enter-from, .fade-leave-to { opacity: 0; }
footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }
</style>