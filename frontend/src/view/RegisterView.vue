<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const step = ref('register')
const setupToken = ref('')
const qrCode = ref('')
const manualCode = ref('')
const authenticatorCode = ref('')
const recoveryCodes = ref([])
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
const googleReady = ref(false)
const googleButton = ref(null)

const handleGoogleCredential = async (googleResponse) => {
  errorMessage.value = ''
  try {
    const response = await axios.post('http://localhost:8001/api/auth/google', { credential: googleResponse.credential })
    sessionStorage.setItem('token', response.data.access_token)
    sessionStorage.setItem('userEmail', response.data.email)
    sessionStorage.setItem('userRole', response.data.role)
    if (response.data.sessionId) sessionStorage.setItem('sessionId', response.data.sessionId)
    router.push(response.data.role === 'admin' ? '/admin' : '/recipes')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Google-inloggningen misslyckades.'
  }
}

onMounted(() => {
  if (!googleClientId) return
  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client?hl=sv'
  script.async = true
  script.onload = () => {
    window.google.accounts.id.initialize({ client_id: googleClientId, callback: handleGoogleCredential })
    googleReady.value = true
    nextTick(() => {
      if (!googleButton.value) return
      window.google.accounts.id.renderButton(googleButton.value, {
        type: 'standard', theme: 'outline', size: 'large', text: 'signup_with',
        shape: 'rectangular', logo_alignment: 'left', width: 320,
      })
    })
  }
  script.onerror = () => { errorMessage.value = 'Kunde inte ladda Google-inloggning. Kontrollera din internetanslutning.' }
  document.head.appendChild(script)
})

const handleRegister = async () => {
  errorMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Lösenorden matchar inte.'
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('http://localhost:8001/api/auth/register', {
      email: email.value,
      password: password.value
    })

    setupToken.value = response.data.setup_token
    const setup = await axios.post('http://localhost:8001/api/auth/2fa/setup', {}, {
      headers: { Authorization: `Bearer ${setupToken.value}` }
    })
    qrCode.value = setup.data.qrCode
    manualCode.value = setup.data.manualCode
    step.value = 'authenticator'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Det gick inte att skapa kontot.'
  } finally {
    isLoading.value = false
  }
}

const finishAuthenticatorSetup = async () => {
  errorMessage.value = ''
  isLoading.value = true
  try {
    const response = await axios.post('http://localhost:8001/api/auth/2fa/setup/verify', {
      code: authenticatorCode.value
    }, { headers: { Authorization: `Bearer ${setupToken.value}` } })
    recoveryCodes.value = response.data.recoveryCodes
    sessionStorage.setItem('token', response.data.access_token)
    sessionStorage.setItem('userEmail', response.data.email)
    sessionStorage.setItem('userRole', response.data.role)
    step.value = 'recovery'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Koden kunde inte verifieras.'
  } finally {
    isLoading.value = false
  }
}

const finishRegistration = () => router.push('/recipes')
</script>

<template>
  <div class="page-container">
    <!-- Header / Navbar -->
    <header class="navbar">
      <AppLogo />
      <nav class="nav-links">
        <router-link to="/recipes" class="nav-link">Utforska recept</router-link>
        <router-link to="/login" class="btn-outline">Logga in</router-link>
      </nav>
    </header>

    <!-- Main Content Grid -->
    <main class="main-content">
      <div class="card-grid">

        <!-- Vänster sida: Hero-panel -->
        <div class="hero-panel">
          <div class="hero-overlay">
            <h2 class="hero-quote">"Samla dina bästa recept på ett ställe."</h2>
            <p class="hero-subtext">
              Skapa ett konto helt gratis och börja bygga din personliga receptsamling idag.
            </p>
          </div>
        </div>

        <!-- Höger sida: Formulär -->
        <div class="form-panel">
          <h1 class="form-title">{{ step === 'register' ? 'Skapa konto' : step === 'authenticator' ? 'Skydda ditt konto' : 'Spara återställningskoder' }}</h1>
          <p class="form-subtitle">Bli en del av Köksboken och spara dina matminnen.</p>

          <div v-if="errorMessage" class="error-banner">
            {{ errorMessage }}
          </div>

          <form v-if="step === 'register'" @submit.prevent="handleRegister" class="auth-form">
            <div class="input-group">
              <label>E-postadress</label>
              <div class="input-wrapper">
                <span class="input-icon">✉</span>
                <input
                  type="email"
                  v-model="email"
                  placeholder="exempel@koksboken.se"
                  required
                />
              </div>
            </div>

            <div class="input-group">
              <label>Lösenord</label>
              <div class="input-wrapper">
                <span class="input-icon lock-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg></span>
                <input
                  type="password"
                  v-model="password"
                  placeholder="Välj ett säkert lösenord"
                  required
                />
              </div>
            </div>

            <div class="input-group">
              <label>Bekräfta lösenord</label>
              <div class="input-wrapper">
                <span class="input-icon lock-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg></span>
                <input
                  type="password"
                  v-model="confirmPassword"
                  placeholder="Upprepa lösenord"
                  required
                />
              </div>
            </div>

            <button type="submit" class="btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Skapar konto...' : 'Skapa ditt konto ➔' }}
            </button>
          </form>

          <template v-if="step === 'register'">
            <div class="divider"><span>ELLER</span></div>
            <div v-if="googleClientId" ref="googleButton" class="google-button" :class="{ ready: googleReady }" aria-label="Skapa konto med Google"></div>
            <p v-else class="google-unavailable">Google-registrering är inte konfigurerad ännu.</p>
          </template>

          <section v-else-if="step === 'authenticator'" class="auth-form authenticator-setup">
            <p>Öppna Google Authenticator eller Microsoft Authenticator, lägg till ett konto och skanna QR-koden.</p>
            <img :src="qrCode" alt="QR-kod för Authenticator" class="totp-qr" />
            <details><summary>Kan du inte skanna QR-koden?</summary><code>{{ manualCode }}</code></details>
            <label class="input-group">Kod från Authenticator
              <input v-model="authenticatorCode" inputmode="numeric" maxlength="6" placeholder="123456" required />
            </label>
            <button type="button" class="btn-primary" :disabled="isLoading || authenticatorCode.length !== 6" @click="finishAuthenticatorSetup">{{ isLoading ? 'Bekräftar...' : 'Aktivera 2FA' }}</button>
          </section>

          <section v-else class="auth-form recovery-codes">
            <p>Spara dessa åtta engångskoder på ett säkert ställe. De visas bara nu.</p>
            <code v-for="recoveryCode in recoveryCodes" :key="recoveryCode">{{ recoveryCode }}</code>
            <button type="button" class="btn-primary" @click="finishRegistration">Jag har sparat koderna</button>
          </section>

          <p v-if="step === 'register'" class="switch-mode">
            Har du redan ett konto?
            <router-link to="/login">Logga in här</router-link>
          </p>
        </div>

      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-box">
        <h3>Smaklig måltid!</h3>
        <p>Skapad med kärlek till den skandinaviska matkulturen.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f7f4ef;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #332d29;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 4rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  background-color: #c87a57;
  color: white;
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  font-size: 1.1rem;
}

.logo-text {
  font-family: 'Georgia', serif;
  font-size: 1.4rem;
  font-weight: bold;
  font-style: italic;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #554f4a;
  text-decoration: none;
  font-size: 0.95rem;
}

.btn-outline {
  border: 1px solid #d4cebc;
  padding: 0.5rem 1.2rem;
  border-radius: 20px;
  color: #332d29;
  text-decoration: none;
  font-size: 0.9rem;
  background: white;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 2rem;
}

.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1000px;
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.hero-panel {
  background-image: url('https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=80&w=800');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: 3rem;
  min-height: 480px;
}

.hero-overlay {
  color: white;
  text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}

.hero-quote {
  font-family: 'Georgia', serif;
  font-style: italic;
  font-size: 2rem;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.hero-subtext {
  font-size: 0.9rem;
  opacity: 0.9;
  line-height: 1.5;
}

.form-panel {
  padding: 3rem 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  font-family: 'Georgia', serif;
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  color: #221e1c;
}

.form-subtitle {
  color: #78716a;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.error-banner {
  background-color: #fde8e8;
  color: #9b1c1c;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.authenticator-setup p, .recovery-codes p { color: #78716a; font-size: .85rem; line-height: 1.5; }
.totp-qr { width: 190px; height: 190px; align-self: center; image-rendering: pixelated; }
.authenticator-setup details { font-size: .8rem; color: #665d57; }
.authenticator-setup code { display: block; margin-top: .45rem; overflow-wrap: anywhere; }
.authenticator-setup .input-group input { width: 100%; box-sizing: border-box; padding: .75rem; border: 1px solid #e2ddd5; border-radius: 10px; font: 700 1rem monospace; letter-spacing: .25em; }
.recovery-codes code { display: inline-block; padding: .45rem .55rem; margin: .15rem; border-radius: 5px; background: #f7f2ed; color: #493c35; font: 700 .82rem monospace; }

.input-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: #443e39;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: #a0988e;
}
.lock-icon svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

.input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e2ddd5;
  border-radius: 10px;
  font-size: 0.9rem;
  outline: none;
  transition: border 0.2s;
}

.input-wrapper input:focus {
  border-color: #c87a57;
}

.btn-primary {
  background-color: #c87a57;
  color: white;
  border: none;
  padding: 0.85rem;
  border-radius: 25px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #b36846;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.divider { text-align: center; margin: 1.5rem 0 1rem; position: relative; }
.divider::before { content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: #eee9e0; }
.divider span { position: relative; z-index: 1; padding: 0 .8rem; background: #fff; color: #a0988e; font: 700 .72rem Arial, sans-serif; }
.google-button { display: flex; justify-content: center; min-height: 44px; opacity: .55; transition: opacity .18s ease; }
.google-button.ready { opacity: 1; }
.google-unavailable { margin: 0; border: 1px dashed #dccdc3; border-radius: 12px; background: #fffaf7; padding: .8rem 1rem; color: #8b6d5e; font-size: .78rem; text-align: center; }

.switch-mode {
  text-align: center;
  font-size: 0.85rem;
  color: #78716a;
  margin-top: 1.5rem;
}

.switch-mode a {
  color: #c87a57;
  text-decoration: none;
  font-weight: 600;
}

.footer {
  padding: 2rem;
  text-align: center;
}

.footer-box {
  display: inline-block;
  border: 1px dashed #d4cebc;
  padding: 1rem 2.5rem;
  border-radius: 8px;
}

.footer-box h3 {
  font-family: 'Georgia', serif;
  font-style: italic;
  margin: 0 0 0.2rem 0;
  font-size: 1.2rem;
}

.footer-box p {
  margin: 0;
  font-size: 0.8rem;
  color: #78716a;
}

@media (max-width: 560px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
  .hero-panel {
    display: none;
  }
  .navbar {
    padding: 1rem;
  }
}
.navbar { min-height: 90px; padding: 1rem clamp(2rem, 6vw, 8rem); }.navbar :deep(.app-logo) { flex-shrink: 0; }.hero-panel { background-image: linear-gradient(0deg, rgb(25 18 14 / 58%), rgb(25 18 14 / 5%)), url('https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=85&w=1200'); background-position: center; }.card-grid { max-width: 1180px; }.form-panel { padding: clamp(2.5rem, 5vw, 4.5rem); }.footer { padding-top: 2.2rem; }
</style>
