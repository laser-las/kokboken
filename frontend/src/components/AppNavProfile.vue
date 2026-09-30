<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useProfile } from '@/composables/useProfile'

const { logout } = useAuth()
const { profile, loadProfile } = useProfile()
const isAdmin = sessionStorage.getItem('userRole') === 'admin'
const name = computed(() => profile.value.name)
const avatarUrl = computed(() => profile.value.avatar_url)
const isOpen = ref(false)
let closeTimer: number | undefined

onMounted(loadProfile)

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
.avatar-btn { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; border: 1px solid #e5d8cf; background: #d58a68; color: white; font: 700 .85rem Arial, sans-serif; cursor: pointer; overflow: hidden; padding: 0; transition: box-shadow .18s ease, transform .18s ease; }
.avatar-btn:hover, .avatar-btn:focus-visible { box-shadow: 0 0 0 4px rgba(196, 98, 63, .14); transform: translateY(-1px); }
.avatar-btn img { width: 100%; height: 100%; object-fit: cover; }
.dropdown { position: absolute; right: -8px; top: calc(100% + 10px); width: 224px; box-sizing: border-box; background: rgba(255, 253, 250, .96); backdrop-filter: blur(14px); border: 1px solid var(--line, #ede3da); border-radius: 16px; box-shadow: 0 14px 34px rgba(60, 35, 20, .14); padding: .55rem; z-index: 30; }
.dropdown::before { content: ''; position: absolute; right: 18px; top: -6px; width: 11px; height: 11px; background: rgba(255, 253, 250, .96); border-top: 1px solid var(--line, #ede3da); border-left: 1px solid var(--line, #ede3da); transform: rotate(45deg); }
.dropdown-name { position: relative; margin: .3rem .75rem .55rem; color: var(--muted, #7d6f68); font: 500 .68rem var(--font-body, Arial, sans-serif); word-break: break-word; }
.dropdown a, .dropdown button.logout { position: relative; display: block; width: 100%; text-align: left; padding: .62rem .75rem; border-radius: 10px; border: none; background: none; color: var(--ink, #2b211c); font: .82rem var(--font-body, Arial, sans-serif); text-decoration: none; cursor: pointer; }
.dropdown a:hover, .dropdown button.logout:hover, .dropdown a:focus-visible, .dropdown button.logout:focus-visible { background: var(--accent-soft, #fbeee7); color: var(--accent-dark, #a94e2f); outline: none; }
.dropdown button.logout { margin-top: .15rem; border-top: 1px solid var(--line, #ede3da); border-radius: 0 0 10px 10px; padding-top: .72rem; }
.dropdown-enter-active, .dropdown-leave-active { transition: opacity .18s ease, transform .18s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px) scale(.98); }
</style>
