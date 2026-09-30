<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { api } from '@/lib/api'
import '@/styles/theme.css'

let heartbeatTimer: number | undefined

function sendHeartbeat() {
  if (sessionStorage.getItem('token')) api.post('/auth/heartbeat').catch(() => {})
}

onMounted(() => {
  sendHeartbeat()
  heartbeatTimer = window.setInterval(sendHeartbeat, 30000)
})
onBeforeUnmount(() => window.clearInterval(heartbeatTimer))
</script>

<template>
  <RouterView v-slot="{ Component }">
    <transition name="page-fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </RouterView>
</template>

<style>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.18s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
</style>
