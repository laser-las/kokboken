<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { useAuth } from '@/composables/useAuth'
import AppLogo from '@/components/AppLogo.vue'

const route = useRoute()
const router = useRouter()
const { logout } = useAuth()
const isAdmin = localStorage.getItem('userRole') === 'admin'

const editingSlug = computed(() => route.params.slug as string | undefined)
const isEditMode = computed(() => !!editingSlug.value)

const title = ref('')
const category = ref('')
const time = ref('')
const image = ref('')
const description = ref('')
const ingredientsText = ref('')
const stepsText = ref('')

const isLoading = ref(false)
const isSaving = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  if (!editingSlug.value) return
  isLoading.value = true
  try {
    const response = await api.get(`/recipes/${editingSlug.value}`)
    const r = response.data
    title.value = r.title
    category.value = r.category
    time.value = r.time
    image.value = r.image
    description.value = r.description
    ingredientsText.value = (r.ingredients || []).join('\n')
    stepsText.value = (r.steps || []).join('\n')
  } catch {
    errorMessage.value = 'Kunde inte ladda receptet för redigering.'
  } finally {
    isLoading.value = false
  }
})

function linesFrom(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

async function save() {
  errorMessage.value = ''
  if (!title.value.trim()) {
    errorMessage.value = 'Titel krävs.'
    return
  }
  isSaving.value = true
  const payload = {
    title: title.value.trim(),
    category: category.value.trim() || 'Övrigt',
    time: time.value.trim(),
    image: image.value.trim(),
    description: description.value.trim(),
    ingredients: linesFrom(ingredientsText.value),
    steps: linesFrom(stepsText.value),
  }
  try {
    if (isEditMode.value) {
      const response = await api.put(`/recipes/${editingSlug.value}`, payload)
      router.push(`/recipes/${response.data.slug}`)
    } else {
      const response = await api.post('/recipes/', payload)
      router.push(`/recipes/${response.data.slug}`)
    }
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Kunde inte spara receptet.'
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <header class="navbar">
      <AppLogo />
      <nav>
        <router-link to="/recipes">Alla recept</router-link>
        <router-link to="/profile">Min profil</router-link>
        <router-link v-if="isAdmin" to="/admin" class="admin-link">Adminpanel</router-link>
        <button class="logout" type="button" @click="logout">Logga ut</button>
      </nav>
    </header>

    <main>
      <router-link to="/recipes" class="back-link">← Tillbaka till alla recept</router-link>
      <h1>{{ isEditMode ? 'Redigera recept' : 'Nytt recept' }}</h1>

      <p v-if="isLoading">Laddar...</p>
      <form v-else class="recipe-form" @submit.prevent="save">
        <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

        <label>Titel<input v-model="title" type="text" required placeholder="T.ex. Köttbullar med potatismos" /></label>
        <div class="row">
          <label>Kategori<input v-model="category" type="text" placeholder="T.ex. Klassiker" /></label>
          <label>Tid<input v-model="time" type="text" placeholder="T.ex. 45 min" /></label>
        </div>
        <label>Bild-URL<input v-model="image" type="url" placeholder="https://..." /></label>
        <label>Beskrivning<textarea v-model="description" rows="3" placeholder="Kort presentation av receptet"></textarea></label>
        <label>Ingredienser <span>(en per rad)</span><textarea v-model="ingredientsText" rows="6" placeholder="500 g nötfärs&#10;1 st gul lök"></textarea></label>
        <label>Gör så här <span>(ett steg per rad)</span><textarea v-model="stepsText" rows="6" placeholder="Skala och koka potatisen...&#10;Blanda färsen..."></textarea></label>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="isSaving">{{ isSaving ? 'Sparar...' : 'Spara recept' }}</button>
          <router-link to="/recipes" class="btn-cancel">Avbryt</router-link>
        </div>
      </form>
    </main>
    <footer><span>Smaklig måltid!</span></footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #faf8f4; color: #382e2a; font-family: Georgia, 'Times New Roman', serif; }
.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }
nav { display: flex; gap: 1.5rem; align-items: center; } nav a { color: #756862; font: .78rem Arial, sans-serif; text-decoration: none; }
.admin-link { color: #b86648 !important; font-weight: 700; }
.logout { border: 1px solid #e5d8cf; border-radius: 999px; background: transparent; padding: .35rem .65rem; color: #756862; font: .78rem Arial, sans-serif; cursor: pointer; }
main { width: min(760px, calc(100% - 3rem)); margin: 0 auto; padding: 2rem 0 4rem; }
.back-link { display: inline-block; margin-bottom: 1.5rem; color: #b46649; font: .73rem Arial, sans-serif; text-decoration: none; }
h1 { margin: 0 0 1.5rem; font-size: 2rem; }
.recipe-form { display: flex; flex-direction: column; gap: 1.1rem; background: white; border: 1px solid #eee5de; border-radius: 10px; padding: 1.75rem; }
.recipe-form label { display: flex; flex-direction: column; gap: .4rem; font: 600 .78rem Arial, sans-serif; color: #443e39; }
.recipe-form label span { font-weight: 400; color: #93867e; font-size: .68rem; }
.recipe-form input, .recipe-form textarea { border: 1px solid #e2ddd5; border-radius: 8px; padding: .65rem .8rem; font: .85rem Arial, sans-serif; outline: none; resize: vertical; }
.recipe-form input:focus, .recipe-form textarea:focus { border-color: #c87a57; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.error-banner { background-color: #fde8e8; color: #9b1c1c; padding: .75rem; border-radius: 8px; font-size: .85rem; }
.form-actions { display: flex; gap: .8rem; align-items: center; margin-top: .5rem; }
.btn-primary { background-color: #c87a57; color: white; border: none; padding: .75rem 1.3rem; border-radius: 25px; font-size: .85rem; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: .7; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background-color: #b36846; }
.btn-cancel { color: #78716a; font: .78rem Arial, sans-serif; text-decoration: none; }
footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }
@media (max-width: 620px) { .row { grid-template-columns: 1fr; } }
</style>