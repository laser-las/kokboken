<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
const googleReady = ref(false)

const finishLogin = (data) => {
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('userEmail', data.email)
  localStorage.setItem('userRole', data.role)
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
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.onload = () => {
    window.google.accounts.id.initialize({ client_id: googleClientId, callback: handleGoogleCredential })
    googleReady.value = true
  }
  document.head.appendChild(script)
})

const startGoogleLogin = () => {
  if (!googleReady.value) {
    errorMessage.value = 'Google-inloggning är inte konfigurerad ännu.'
    return
  }
  window.google.accounts.id.prompt()
}

const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true
  try {
    const response = await axios.post('http://localhost:8001/api/auth/login', {
      email: email.value,
      password: password.value
    })
    
    // Spara JWT-token i localStorage
    finishLogin(response.data)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Inloggningen misslyckades. Kontrollera dina uppgifter.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <!-- Header / Navbar -->
    <header class="navbar">
      <AppLogo />
      <nav class="nav-links">
        <router-link to="/recipes" class="nav-link">Utforska recept</router-link>
        <router-link to="/register" class="btn-outline">Skapa konto</router-link>
      </nav>
    </header>

    <!-- Main Content Grid -->
    <main class="main-content">
      <div class="card-grid">
        
        <!-- Vänster sida: Hero-bild med text -->
        <div class="hero-panel">
          <div class="hero-overlay">
            <h2 class="hero-quote">"Det doftar alltid hemma i Köksboken."</h2>
            <p class="hero-subtext">
              Spara dina favoritrecept, organisera veckans måltider och dela matglädjen med nära och kära.
            </p>
          </div>
        </div>

        <!-- Höger sida: Inloggningsformulär -->
        <div class="form-panel">
          <h1 class="form-title">Välkommen</h1>
          <p class="form-subtitle">Logga in för att komma åt din personliga digitala receptpärm.</p>

          <div v-if="errorMessage" class="error-banner">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleLogin" class="auth-form">
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
                  placeholder="Ditt säkra lösenord" 
                  required 
                />
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

          <div class="divider">
            <span>ELLER</span>
          </div>

          <button class="btn-google" type="button" @click="startGoogleLogin">
            <span class="google-icon">G</span>
            Logga in med Google
          </button>

          <p class="switch-mode">
            Ny hos Köksboken? 
            <router-link to="/register">Skapa ett gratis konto</router-link>
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
/* Färger och grundstil */
.page-container {
  min-height: 100vh;
  background-color: #f7f4ef;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #332d29;
}

/* Navbar */
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

/* Huvudsektion */
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

/* Vänster hero-panel */
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

/* Höger formulärpanel */
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #554f4a;
  cursor: pointer;
}

.forgot-link {
  color: #c87a57;
  text-decoration: none;
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

.divider {
  text-align: center;
  margin: 1.5rem 0 1rem 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: #eee9e0;
  z-index: 1;
}

.divider span {
  position: relative;
  z-index: 2;
  background-color: white;
  padding: 0 0.8rem;
  color: #a0988e;
  font-size: 0.75rem;
  font-weight: 600;
}

.btn-google {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2ddd5;
  border-radius: 10px;
  background: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  color: #443e39;
}

.google-icon {
  font-weight: bold;
}

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

/* Footer */
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

/* Responsivitet för mindre skärmar */
@media (max-width: 560px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
  .hero-panel {
    display: none; /* Dölj bildpanelen på mobiler */
  }
  .navbar {
    padding: 1rem;
  }
}
.navbar { min-height: 90px; padding: 1rem clamp(2rem, 6vw, 8rem); }.navbar :deep(.app-logo) { flex-shrink: 0; }.hero-panel { background-image: linear-gradient(0deg, rgb(25 18 14 / 58%), rgb(25 18 14 / 5%)), url('https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=85&w=1200'); background-position: center; }.card-grid { max-width: 1180px; }.form-panel { padding: clamp(2.5rem, 5vw, 4.5rem); }.footer { padding-top: 2.2rem; }
</style>
