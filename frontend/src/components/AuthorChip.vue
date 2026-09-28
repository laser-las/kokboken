<script setup lang="ts">
import { computed, ref } from 'vue'
import { avatarUrl } from '@/lib/api'

const props = defineProps<{ email: string; name?: string }>()
const failed = ref(false)
const label = computed(() => props.name || props.email.split('@')[0] || '?')
</script>

<template>
  <span v-if="email" class="author">
    <img v-if="!failed" :src="avatarUrl(email)" :alt="label" @error="failed = true" />
    <b v-else>{{ label.charAt(0).toUpperCase() }}</b>
    <span class="author-name">{{ label }}</span>
  </span>
</template>

<style scoped>
.author { display: inline-flex; align-items: center; gap: .5rem; max-width: 100%; }
.author img, .author b { width: 24px; height: 24px; border-radius: 50%; flex: 0 0 24px; object-fit: cover; }
.author b { display: grid; place-items: center; background: #d58a68; color: #fff; font-size: .65rem; font-weight: 700; }
.author-name { color: #7d6f68; font-size: .7rem; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
