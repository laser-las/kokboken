<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AppLogo from '@/components/AppLogo.vue'
import { refreshFavorites } from '@/composables/useFavorites'

const router = useRouter()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
const googleReady = ref(false)
const googleButton = ref(null)

const step = ref('credentials') // 'credentials' | 'code'
const twoFactorMethod = ref('email')
const code = ref('')
const isVerifying = ref(false)
const isResending = ref(false)
const resendNotice = ref('')
const developmentCode = ref('')
const codeInput = ref(null)

const finishLogin = (data) => {
  sessionStorage.setItem('token', data.access_token)
  sessionStorage.setItem('userEmail', data.email)
  sessionStorage.setItem('userRole', data.role)
  if (data.sessionId) sessionStorage.setItem('sessionId', data.sessionId)
  refreshFavorites()
  router.push(data.role === 'admin' ? '/admin' : '/recipes')
}

const handleGoogleCredential = async (googleResponse) => {
  try {
    const response = await axios.post('http://localhost:8001/api/auth/google', { credential: googleResponse.credential })
    finishLogin(response.data)
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
        type: 'standard', theme: 'outline', size: 'large', text: 'signin_with',
        shape: 'rectangular', logo_alignment: 'left', width: 320,
      })
    })
  }
  script.onerror = () => { errorMessage.value = 'Kunde inte ladda Google-inloggning. Kontrollera din internetanslutning.' }
  document.head.appendChild(script)
})

const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true
  try {
    const response = await axios.post('http://localhost:8001/api/auth/login', {
      email: email.value,
      password: password.value
    })
    if (response.data.requires_2fa) {
      step.value = 'code'
      code.value = ''
      twoFactorMethod.value = response.data.two_factor_method || 'email'
      developmentCode.value = response.data.development_code || ''
      await nextTick()
      codeInput.value?.focus()
    } else {
      finishLogin(response.data)
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Inloggningen misslyckades. Kontrollera dina uppgifter.'
  } finally {
    isLoading.value = false
  }
}

const backToCredentials = () => {
  step.value = 'credentials'
  code.value = ''
  errorMessage.value = ''
  resendNotice.value = ''
  developmentCode.value = ''
}

const verifyCode = async () => {
  errorMessage.value = ''
  isVerifying.value = true
  try {
    const response = await axios.post('http://localhost:8001/api/auth/verify-2fa', {
      email: email.value,
      code: code.value.trim()
    })
    finishLogin(response.data)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Kunde inte verifiera koden.'
  } finally {
    isVerifying.value = false
  }
}

const resendCode = async () => {
  errorMessage.value = ''
  resendNotice.value = ''
  isResending.value = true
  try {
    const response = await axios.post('http://localhost:8001/api/auth/resend-2fa', { email: email.value })
    developmentCode.value = response.data.development_code || ''
    resendNotice.value = response.data.email_delivered
      ? 'En ny kod har skickats till din e-post.'
      : 'E-post är inte konfigurerad i den lokala miljön.'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Kunde inte skicka en ny kod.'
  } finally {
    isResending.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <header class="navbar">
      <AppLogo />
      <nav class="nav-links">
        <router-link to="/recipes" class="nav-link">Utforska recept</router-link>
        <router-link to="/register" class="btn-outline">Skapa konto</router-link>
      </nav>
    </header>

    <main class="main-content">
      <div class="card-grid">
        <div class="hero-panel">
          <div class="hero-overlay">
            <h2 class="hero-quote">"Det doftar alltid hemma i Köksboken."</h2>
            <p class="hero-subtext">
              Spara dina favoritrecept, organisera veckans måltider och dela matglädjen med nära och kära.
            </p>
          </div>
        </div>

        <div class="form-panel">
          <template v-if="step === 'credentials'">
            <p class="form-eyebrow">DITT KONTO</p>
            <h1 class="form-title">Välkommen</h1>
            <p class="form-subtitle">Logga in för att komma åt din personliga digitala receptpärm.</p>

            <transition name="fade"><div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div></transition>

            <form @submit.prevent="handleLogin" class="auth-form">
              <div class="input-group">
                <label>E-postadress</label>
                <div class="input-wrapper">
                  <span class="input-icon">✉</span>
                  <input type="email" v-model="email" placeholder="exempel@köksboken.se" autocomplete="email" required />
                </div>
              </div>

              <div class="input-group">
                <label>Lösenord</label>
                <div class="input-wrapper">
                  <span class="input-icon lock-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg></span>
                  <input type="password" v-model="password" placeholder="Ditt säkra lösenord" autocomplete="current-password" required />
                </div>
              </div>

              <div class="form-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="rememberMe" />
                  <span>Kom ihåg mig</span>
                </label>
                <a href="#" class="forgot-link">Glömt lösenord?</a>
              </div>

              <button type="submit" class="btn-primary" :disabled="isLoading">
                {{ isLoading ? 'Loggar in...' : 'Logga in i Köksboken ➔' }}
              </button>
            </form>

            <div class="divider"><span>ELLER</span></div>

            <div v-if="googleClientId" ref="googleButton" class="google-button" :class="{ ready: googleReady }" aria-label="Logga in med Google"></div>
            <p v-else class="google-unavailable">Google-inloggning är inte konfigurerad ännu.</p>

            <p class="switch-mode">
              Ny hos Köksboken?
              <router-link to="/register">Skapa ett gratis konto</router-link>
            </p>
          </template>

          <template v-else>
            <h1 class="form-title">{{ twoFactorMethod === 'authenticator' ? 'Öppna din Authenticator-app' : 'Kontrollera din e-post' }}</h1>
            <p class="form-subtitle">{{ twoFactorMethod === 'authenticator' ? 'Skriv in den aktuella sexsiffriga koden från din Authenticator-app.' : `Vi har skickat en 6-siffrig kod till ${email}. Skriv in den nedan för att slutföra inloggningen.` }}</p>

            <transition name="fade"><div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div></transition>
            <transition name="fade"><div v-if="resendNotice" class="notice-banner">{{ resendNotice }}</div></transition>
            <div v-if="developmentCode" class="development-code">
              <strong>Utvecklingskod:</strong> {{ developmentCode }}
              <small>Visas bara lokalt när e-post inte är konfigurerad.</small>
            </div>

            <form @submit.prevent="verifyCode" class="auth-form">
              <div class="input-group">
                <label>Engångskod</label>
                <div class="input-wrapper">
                  <input ref="codeInput" v-model="code" type="text" inputmode="numeric" pattern="[0-9]*" maxlength="6" class="code-input" placeholder="123456" required autocomplete="one-time-code" />
                </div>
              </div>

              <button type="submit" class="btn-primary" :disabled="isVerifying || code.trim().length < 4">
                {{ isVerifying ? 'Verifierar...' : 'Bekräfta och logga in' }}
              </button>
            </form>

            <p v-if="twoFactorMethod !== 'authenticator'" class="switch-mode">
              <a href="#" @click.prevent="resendCode">{{ isResending ? 'Skickar...' : 'Skicka koden igen' }}</a>
              &nbsp;·&nbsp;
              <a href="#" @click.prevent="backToCredentials">Fel e-post? Gå tillbaka</a>
            </p>
          </template>
        </div>
      </div>
    </main>

    <footer class="footer">
      <div class="footer-box">
        <h3>Smaklig måltid!</h3>
        <p>Skapad med kärlek till den skandinaviska matkulturen.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: radial-gradient(circle at 12% 12%, #fffdf9 0, #f7f1e9 36%, #f4eee6 100%); display: flex; flex-direction: column; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #332d29; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 4rem; max-width: 1200px; width: 100%; margin: 0 auto; box-sizing: border-box; }
.nav-links { display: flex; align-items: center; gap: 1.5rem; }
.nav-link { color: #554f4a; text-decoration: none; font-size: 0.95rem; }
.btn-outline { border: 1px solid #d4cebc; padding: 0.5rem 1.2rem; border-radius: 20px; color: #332d29; text-decoration: none; font-size: 0.9rem; background: white; }
.main-content { flex: 1; display: flex; justify-content: center; align-items: center; padding: 1rem 2rem; }
.card-grid { display: grid; grid-template-columns: 1fr 1fr; max-width: 1000px; width: 100%; background: #ffffff; border: 1px solid rgba(226, 213, 201, .9); border-radius: 24px; overflow: hidden; box-shadow: 0 24px 65px rgba(74, 49, 35, .14), 0 3px 10px rgba(74, 49, 35, .05); }
.hero-panel { background-image: linear-gradient(0deg, rgb(39 25 18 / 72%), rgb(39 25 18 / 8%)), url('https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=85&w=1200'); background-size: cover; background-position: center; position: relative; display: flex; align-items: flex-end; padding: 3rem; min-height: 500px; }
.hero-overlay { color: white; text-shadow: 0 2px 8px rgba(0,0,0,0.6); }
.hero-quote { font-family: 'Georgia', serif; font-style: italic; font-size: 2rem; margin-bottom: 1rem; line-height: 1.2; }
.hero-subtext { font-size: 0.9rem; opacity: 0.9; line-height: 1.5; }
.form-panel { padding: clamp(2.5rem, 5vw, 4.5rem); display: flex; flex-direction: column; justify-content: center; background: linear-gradient(135deg, #fff 0%, #fffdfa 100%); }
.form-eyebrow { margin: 0 0 .55rem; color: #b96545; font: 700 .65rem Arial, sans-serif; letter-spacing: .14em; }
.form-title { font-family: 'Georgia', serif; font-size: 2rem; margin: 0 0 0.5rem 0; color: #221e1c; }
.form-subtitle { color: #78716a; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.5; }
.error-banner { background-color: #fde8e8; color: #9b1c1c; padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; }
.notice-banner { background-color: #e8f5ea; color: #2a6b39; padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; }
.development-code { display: flex; flex-direction: column; gap: .2rem; margin-bottom: 1rem; padding: .75rem; border: 1px solid #e7c884; border-radius: 8px; background: #fff8e6; color: #6d4b12; font-size: .9rem; }
.development-code small { font-size: .75rem; color: #85652b; }
.auth-form { display: flex; flex-direction: column; gap: 1.2rem; }
.input-group label { display: block; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.45rem; color: #443e39; }
.input-wrapper { position: relative; display: flex; align-items: center; border-radius: 12px; transition: transform .18s ease, box-shadow .18s ease; }
.input-icon { position: absolute; left: 1rem; z-index: 1; color: #9a7666; }
.lock-icon svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.input-wrapper input { width: 100%; min-height: 48px; padding: 0.75rem 1rem 0.75rem 2.7rem; border: 1px solid #d9cfc6; border-radius: 12px; background: #fff; color: #332d29; font-size: .92rem; outline: none; transition: border .18s ease, background .18s ease; box-sizing: border-box; }
.input-wrapper input::placeholder { color: #ab9e96; }
.input-wrapper:focus-within { transform: translateY(-1px); box-shadow: 0 0 0 4px rgba(196, 98, 63, .13); }
.input-wrapper input:focus { border-color: #bd694b; background: #fffdfa; }
.code-input { padding-left: 1rem !important; letter-spacing: .5em; font-size: 1.3rem !important; text-align: center; font-weight: 700; }
.form-options { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.45rem; color: #554f4a; cursor: pointer; }
.checkbox-label input { accent-color: #c4623f; width: 16px; height: 16px; }
.forgot-link { color: #b75d3e; text-decoration: none; font-weight: 600; }
.btn-primary { background-color: #c4623f; color: white; border: none; padding: .9rem; border-radius: 14px; font-size: .95rem; font-weight: 700; cursor: pointer; margin-top: .5rem; box-shadow: 0 8px 18px rgba(196,98,63,.24); transition: background-color .2s, transform .2s, box-shadow .2s; }
.btn-primary:hover:not(:disabled) { background-color: #b36846; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.divider { text-align: center; margin: 1.5rem 0 1rem 0; position: relative; }
.divider::before { content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background-color: #eee9e0; z-index: 1; }
.divider span { position: relative; z-index: 2; background-color: white; padding: 0 0.8rem; color: #a0988e; font-size: 0.75rem; font-weight: 600; }
.google-button { display: flex; justify-content: center; min-height: 44px; opacity: .55; transition: opacity .18s ease; }
.google-button.ready { opacity: 1; }
.google-unavailable { margin: 0; border: 1px dashed #dccdc3; border-radius: 12px; background: #fffaf7; padding: .8rem 1rem; color: #8b6d5e; font-size: .78rem; text-align: center; }
.switch-mode { text-align: center; font-size: 0.85rem; color: #78716a; margin-top: 1.5rem; }
.switch-mode a { color: #c87a57; text-decoration: none; font-weight: 600; cursor: pointer; }
.footer { padding: 2rem; text-align: center; }
.footer-box { display: inline-block; border: 1px dashed #d4cebc; padding: 1rem 2.5rem; border-radius: 8px; }
.footer-box h3 { font-family: 'Georgia', serif; font-style: italic; margin: 0 0 0.2rem 0; font-size: 1.2rem; }
.footer-box p { margin: 0; font-size: 0.8rem; color: #78716a; }
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@media (max-width: 560px) { .card-grid { grid-template-columns: 1fr; } .hero-panel { display: none; } .navbar { padding: 1rem; } }
.navbar { min-height: 90px; padding: 1rem clamp(2rem, 6vw, 8rem); }
</style>
