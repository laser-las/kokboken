<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { api } from '@/lib/api'
import { useProfile } from '@/composables/useProfile'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; saved: [] }>()
const { profile, setProfile } = useProfile()

const name = ref('')
const avatar = ref<string | null>(null)
const avatarChanged = ref(false)
const saving = ref(false)
const error = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const nameInput = ref<HTMLInputElement | null>(null)

const initial = computed(() => (name.value || profile.value.name || '?').charAt(0).toUpperCase())
const canSave = computed(() => !saving.value && !!name.value.trim() && (avatarChanged.value || name.value.trim() !== profile.value.name))

function onKey(e: KeyboardEvent) { if (e.key === 'Escape') emit('close') }
watch(() => props.open, async (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
  if (isOpen) {
    window.addEventListener('keydown', onKey)
    name.value = profile.value.name
    avatar.value = profile.value.avatar_url
    avatarChanged.value = false
    error.value = ''
    await nextTick()
    nameInput.value?.focus()
  } else {
    window.removeEventListener('keydown', onKey)
  }
})
onBeforeUnmount(() => { window.removeEventListener('keydown', onKey); document.body.style.overflow = '' })

function onFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (!file.type.startsWith('image/')) { error.value = 'Välj en bildfil (JPG eller PNG).'; return }
  error.value = ''
  const reader = new FileReader()
  reader.onload = () => {
    const img = new Image()
    img.onload = () => {
      const size = 256
      const side = Math.min(img.width, img.height)
      const canvas = document.createElement('canvas')
      canvas.width = size
      canvas.height = size
      canvas.getContext('2d')?.drawImage(img, (img.width - side) / 2, (img.height - side) / 2, side, side, 0, 0, size, size)
      avatar.value = canvas.toDataURL('image/jpeg', 0.85)
      avatarChanged.value = true
    }
    img.onerror = () => { error.value = 'Kunde inte läsa bilden.' }
    img.src = reader.result as string
  }
  reader.readAsDataURL(file)
}
function removeAvatar() { avatar.value = null; avatarChanged.value = true }
function adjustAvatar(rotation: number, zoom = 1, moveX = 0, moveY = 0) {
  if (!avatar.value) return
  const source = avatar.value
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    const size = 256
    canvas.width = size
    canvas.height = size
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, size, size)
    ctx.translate(size / 2 + moveX, size / 2 + moveY)
    ctx.rotate((rotation * Math.PI) / 180)
    const scaled = size * zoom
    ctx.drawImage(img, -scaled / 2, -scaled / 2, scaled, scaled)
    avatar.value = canvas.toDataURL('image/jpeg', 0.88)
    avatarChanged.value = true
  }
  img.src = source
}

async function save() {
  if (!canSave.value) return
  saving.value = true
  error.value = ''
  try {
    const body: Record<string, string> = { name: name.value.trim() }
    if (avatarChanged.value) body.avatar_url = avatar.value || ''
    const { data } = await api.patch('/auth/me', body)
    setProfile(data)
    emit('saved')
    emit('close')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kunde inte spara profilen.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="open" class="overlay" @mousedown.self="emit('close')">
        <form class="dialog" role="dialog" aria-modal="true" aria-labelledby="pe-title" @submit.prevent="save">
          <header>
            <h2 id="pe-title">Redigera profil</h2>
            <button type="button" class="x" aria-label="Stäng" @click="emit('close')">✕</button>
          </header>

          <div class="avatar-row">
            <button type="button" class="avatar" aria-label="Byt profilbild" @click="fileInput?.click()">
              <img v-if="avatar" :src="avatar" alt="" />
              <span v-else>{{ initial }}</span>
              <em>Ändra</em>
            </button>
            <div class="avatar-side">
              <button type="button" class="ghost" @click="fileInput?.click()">{{ avatar ? 'Byt bild' : 'Ladda upp bild' }}</button>
              <div v-if="avatar" class="image-adjustments" aria-label="Justera profilbild">
                <button type="button" @click="adjustAvatar(-90)">↺ Rotera</button><button type="button" @click="adjustAvatar(90)">Rotera ↻</button>
                <button type="button" @click="adjustAvatar(0, 1.15)">+ Zooma</button><button type="button" @click="adjustAvatar(0, .85)">− Zooma</button>
                <button type="button" @click="adjustAvatar(0, 1, -18)">← Flytta</button><button type="button" @click="adjustAvatar(0, 1, 18)">Flytta →</button><button type="button" @click="adjustAvatar(0, 1, 0, -18)">↑ Flytta</button><button type="button" @click="adjustAvatar(0, 1, 0, 18)">↓ Flytta</button>
              </div>
              <button v-if="avatar" type="button" class="link" @click="removeAvatar">Ta bort bild</button>
              <p>JPG eller PNG. Bilden beskärs till en kvadrat och kan justeras före sparning.</p>
            </div>
            <input ref="fileInput" type="file" accept="image/*" hidden @change="onFile" />
          </div>

          <label class="field">
            <span>Visningsnamn</span>
            <input ref="nameInput" v-model="name" type="text" maxlength="40" placeholder="Ditt namn" autocomplete="nickname" />
            <small>{{ name.length }}/40</small>
          </label>

          <p v-if="error" class="err" role="alert">{{ error }}</p>

          <footer>
            <button type="button" class="ghost" @click="emit('close')">Avbryt</button>
            <button type="submit" class="primary" :disabled="!canSave">{{ saving ? 'Sparar…' : 'Spara ändringar' }}</button>
          </footer>
        </form>
      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.overlay { position: fixed; inset: 0; z-index: 100; display: grid; place-items: center; padding: 1rem; background: rgba(43, 33, 28, .45); backdrop-filter: blur(4px); font-family: 'Inter', system-ui, sans-serif; }
.dialog { width: min(440px, 100%); display: grid; gap: 1.4rem; padding: 1.6rem; background: #fff; border-radius: 22px; box-shadow: 0 30px 80px rgba(43, 33, 28, .35); color: #2b211c; }
button, input { font: inherit; }
header { display: flex; align-items: center; justify-content: space-between; }
h2 { margin: 0; font: 700 1.35rem 'Fraunces', Georgia, serif; letter-spacing: -.01em; }
.x { width: 34px; height: 34px; border: 0; border-radius: 50%; background: #f5eee7; color: #7d6f68; cursor: pointer; transition: background .15s; }
.x:hover { background: #ecdfd3; }
.avatar-row { display: flex; align-items: center; gap: 1.2rem; }
.avatar { position: relative; flex: 0 0 96px; width: 96px; height: 96px; padding: 0; border: 3px solid #fff; border-radius: 50%; background: #d58a68; color: #fff; font-size: 2.2rem; font-weight: 700; overflow: hidden; cursor: pointer; box-shadow: 0 0 0 2px #ecdfd3, 0 8px 20px rgba(60, 35, 20, .18); display: grid; place-items: center; }
.avatar img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.avatar em { position: absolute; inset: auto 0 0; padding: .3rem 0 .4rem; background: linear-gradient(transparent, rgba(0, 0, 0, .6)); color: #fff; font-size: .68rem; font-style: normal; font-weight: 600; opacity: 0; transform: translateY(6px); transition: opacity .18s, transform .18s; }
.avatar:hover em, .avatar:focus-visible em { opacity: 1; transform: none; }
.avatar-side { display: grid; gap: .55rem; justify-items: start; }
.image-adjustments { display: flex; flex-wrap: wrap; gap: .35rem; }.image-adjustments button { border: 1px solid #e3d6cb; border-radius: 7px; background: #fffdfb; padding: .35rem .5rem; color: #6e5f57; font-size: .68rem; cursor: pointer; }.image-adjustments button:hover { border-color: #c4623f; color: #c4623f; }
.avatar-side p { margin: 0; color: #9a8c84; font-size: .72rem; line-height: 1.4; }
.ghost { padding: .55rem 1rem; border: 1px solid #e3d6cb; border-radius: 999px; background: #fff; color: #4a3d36; font-size: .82rem; font-weight: 600; cursor: pointer; transition: border-color .15s, color .15s, background .15s; }
.ghost:hover { border-color: #c4623f; color: #c4623f; background: #fffaf6; }
.link { padding: 0; border: 0; background: none; color: #b3453a; font-size: .78rem; font-weight: 500; cursor: pointer; }
.link:hover { text-decoration: underline; }
.field { display: grid; gap: .45rem; position: relative; }
.field span { font-size: .78rem; font-weight: 600; color: #4a3d36; }
.field input { width: 100%; box-sizing: border-box; padding: .8rem 3.2rem .8rem 1rem; border: 1px solid #e3d6cb; border-radius: 12px; background: #fffdfb; font-size: .95rem; color: #2b211c; outline: none; transition: border-color .15s, box-shadow .15s; }
.field input:focus { border-color: #c4623f; box-shadow: 0 0 0 4px rgba(196, 98, 63, .14); }
.field small { position: absolute; right: .9rem; bottom: .95rem; color: #b3a49a; font-size: .68rem; }
.err { margin: 0; padding: .7rem .9rem; border-radius: 10px; background: #fde8e8; color: #9b1c1c; font-size: .82rem; }
footer { display: flex; justify-content: flex-end; gap: .6rem; padding-top: .3rem; }
.primary { padding: .65rem 1.3rem; border: 0; border-radius: 999px; background: #c4623f; color: #fff; font-size: .85rem; font-weight: 600; cursor: pointer; box-shadow: 0 6px 16px rgba(196, 98, 63, .3); transition: background .15s, transform .15s, opacity .15s; }
.primary:hover:not(:disabled) { background: #a94e2f; transform: translateY(-1px); }
.primary:disabled { opacity: .45; cursor: not-allowed; box-shadow: none; }
.modal-enter-active, .modal-leave-active { transition: opacity .2s ease; }
.modal-enter-active .dialog, .modal-leave-active .dialog { transition: transform .22s cubic-bezier(.2, .8, .3, 1), opacity .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .dialog, .modal-leave-to .dialog { transform: translateY(14px) scale(.97); opacity: 0; }
@media (max-width: 420px) { .avatar-row { flex-direction: column; text-align: center; } .avatar-side { justify-items: center; } }
</style>
