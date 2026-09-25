<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/lib/api'
import { useAuth } from '@/composables/useAuth'

const { logout } = useAuth()
const isAdmin = localStorage.getItem('userRole') === 'admin'
const name = ref('')
const avatarUrl = ref<string | null>(null)
const isOpen = ref(false)
let closeTimer: number | undefined

onMounted(async () => {
  try {
    const response = await api.get('/auth/me')
    name.value = response.data.name
    avatarUrl.value = response.data.avatar_url
  } catch {
    // Inte inloggad eller kunde inte hämta profilen - visa tomt fallback
  }
})

function open() {
  window.clearTimeout(closeTimer)
  isOpen.value = true
}
function scheduleClose() {
  closeTimer = window.setTimeout(() => { isOpen.value = false }, 180)
}
function toggle() {
  isOpen.value = !isOpen.value
}
</script>

<template>
  <div class="nav-profile" @mouseenter="open" @mouseleave="scheduleClose">
    <button class="avatar-btn" type="button" @click="toggle" :aria-label="`Meny för ${name || 'din profil'}`">
      <img v-if="avatarUrl" :src="avatarUrl" :alt="name" />
      <span v-else>{{ (name || '?').charAt(0).toUpperCase() }}</span>
    </button>
    <transition name="dropdown">
      <div v-if="isOpen" class="dropdown" @mouseenter="open" @mouseleave="scheduleClose">
        <p class="dropdown-name">{{ name || 'Ditt konto' }}</p>
        <router-link to="/profile" @click="isOpen = false">Min profil</router-link>
        <router-link v-if="isAdmin" to="/admin" @click="isOpen = false">Adminpanel</router-link>
        <button type="button" class="logout" @click="logout">Logga ut</button>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.nav-profile { position: relative; }
.avatar-btn { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; border: 1px solid #e5d8cf; background: #d58a68; color: white; font: 700 .85rem Arial, sans-serif; cursor: pointer; overflow: hidden; padding: 0; }
.avatar-btn img { width: 100%; height: 100%; object-fit: cover; }
.dropdown { position: absolute; right: 0; top: calc(100% + 12px); width: 190px; background: white; border: 1px solid #eee6df; border-radius: 10px; box-shadow: 0 12px 28px rgba(40, 25, 15, 0.14); padding: .5rem; z-index: 30; }
.dropdown-name { margin: .2rem .6rem .5rem; color: #a79b95; font: .62rem Arial, sans-serif; word-break: break-word; }
.dropdown a, .dropdown button.logout { display: block; width: 100%; text-align: left; padding: .55rem .6rem; border-radius: 6px; border: none; background: none; color: #554f4a; font: .76rem Arial, sans-serif; text-decoration: none; cursor: pointer; }
.dropdown a:hover, .dropdown button.logout:hover { background: #fbf1ea; color: #bc6d4f; }
.dropdown-enter-active, .dropdown-leave-active { transition: opacity .16s ease, transform .16s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px); }
</style>