<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  errorMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Lösenorden matchar inte.'
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('http://localhost:8000/api/auth/register', {
      email: email.value,
      password: password.value
    })

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    if (response.data.email) {
      localStorage.setItem('userEmail', response.data.email)
    }

    router.push('/login')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Det gick inte att skapa kontot.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <!-- Header / Navbar -->
    <header class="navbar">
      <div class="logo">
        <span class="logo-icon">📖</span>
        <span class="logo-text">Köksboken</span>
      </div>
      <nav class="nav-links">
        <router-link to="/explore" class="nav-link">Utforska recept</router-link>
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
          <h1 class="form-title">Skapa konto</h1>
          <p class="form-subtitle">Bli en del av Köksboken och spara dina matminnen.</p>

          <div v-if="errorMessage" class="error-banner">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleRegister" class="auth-form">
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
                <span class="input-icon">🔒</span>
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
                <span class="input-icon">🔒</span>
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

          <p class="switch-mode">
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

@media (max-width: 768px) {
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
</style>