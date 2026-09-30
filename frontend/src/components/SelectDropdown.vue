<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{ modelValue: string; options: string[]; placeholder?: string }>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const isOpen = ref(false)
const root = ref<HTMLElement | null>(null)

function select(option: string) {
  emit('update:modelValue', option)
  isOpen.value = false
}
function onOutsideClick(event: MouseEvent) {
  if (root.value && !root.value.contains(event.target as Node)) isOpen.value = false
}
onMounted(() => document.addEventListener('mousedown', onOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onOutsideClick))
</script>

<template>
  <div ref="root" class="select-dropdown" :class="{ open: isOpen }">
    <button type="button" class="trigger" @click="isOpen = !isOpen">
      <span :class="{ placeholder: !modelValue }">{{ modelValue || placeholder || 'Välj...' }}</span>
      <svg viewBox="0 0 24 24" class="chevron"><path d="M6 9l6 6 6-6" /></svg>
    </button>
    <transition name="pop">
      <ul v-if="isOpen" class="menu" role="listbox">
        <li
          v-for="option in options"
          :key="option"
          role="option"
          :class="{ active: option === modelValue }"
          @click="select(option)"
        >
          {{ option }}
        </li>
        <li v-if="!options.length" class="empty">Inga alternativ ännu</li>
      </ul>
    </transition>
  </div>
</template>

<style scoped>
.select-dropdown { position: relative; font-family: 'Inter', system-ui, sans-serif; }
.trigger { display: flex; align-items: center; justify-content: space-between; gap: .6rem; width: 100%; box-sizing: border-box; padding: .7rem .9rem; border: 1px solid #e3d6cb; border-radius: 12px; background: #fffdfb; color: #2b211c; font-size: .88rem; cursor: pointer; transition: border-color .15s, box-shadow .15s; }
.trigger .placeholder { color: #b3a49a; }
.select-dropdown.open .trigger { border-color: #c4623f; box-shadow: 0 0 0 4px rgba(196, 98, 63, .14); }
.chevron { width: 16px; height: 16px; flex-shrink: 0; fill: none; stroke: #9a8c84; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; transition: transform .18s; }
.select-dropdown.open .chevron { transform: rotate(180deg); }
.menu { position: absolute; z-index: 25; top: calc(100% + 8px); left: 0; right: 0; max-height: 240px; overflow-y: auto; margin: 0; padding: .4rem; list-style: none; background: #fff; border: 1px solid #eee5de; border-radius: 14px; box-shadow: 0 16px 36px rgba(43, 33, 28, .18); }
.menu li { padding: .6rem .7rem; border-radius: 9px; font-size: .86rem; color: #4a3d36; cursor: pointer; }
.menu li:hover { background: #fbeee7; color: #a94e2f; }
.menu li.active { background: #c4623f; color: #fff; font-weight: 600; }
.menu li.empty { color: #b3a49a; cursor: default; }
.menu li.empty:hover { background: none; }
.pop-enter-active, .pop-leave-active { transition: opacity .14s ease, transform .14s ease; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
