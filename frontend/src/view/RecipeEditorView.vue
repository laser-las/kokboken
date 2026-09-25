<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import AppLogo from '@/components/AppLogo.vue'
import AppNavProfile from '@/components/AppNavProfile.vue'

const route = useRoute()
const router = useRouter()

const editingSlug = computed(() => route.params.slug as string | undefined)
const isEditMode = computed(() => !!editingSlug.value)

const title = ref('')
const category = ref('')
const time = ref('')
const image = ref('')
const description = ref('')
const ingredients = ref<string[]>([''])
const steps = ref<string[]>([''])
const isPublic = ref(true)

const categories = ref<string[]>([])
const isLoading = ref(false)
const isSaving = ref(false)
const isProcessingImage = ref(false)
const errorMessage = ref('')
const imageInput = ref<HTMLInputElement | null>(null)

async function loadCategories() {
  try {
    categories.value = (await api.get<string[]>('/categories/')).data
  } catch {
    categories.value = []
  }
}

onMounted(async () => {
  loadCategories()
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
    ingredients.value = r.ingredients?.length ? [...r.ingredients] : ['']
    steps.value = r.steps?.length ? [...r.steps] : ['']
    isPublic.value = r.isPublic !== false
  } catch {
    errorMessage.value = 'Kunde inte ladda receptet för redigering.'
  } finally {
    isLoading.value = false
  }
})

function addIngredient() { ingredients.value.push('') }
function removeIngredient(index: number) { ingredients.value.splice(index, 1) }
function addStep() { steps.value.push('') }
function removeStep(index: number) { steps.value.splice(index, 1) }

// Skalar ner och komprimerar bilden i webbläsaren innan den skickas till
// servern, så att stora foton (många MB rakt från mobilkameran) inte gör
// sparningen instabil eller för långsam.
function resizeImage(file: File, maxDim = 1200, quality = 0.82): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const img = new Image()
      img.onload = () => {
        let { width, height } = img
        if (width > maxDim || height > maxDim) {
          if (width > height) { height = Math.round(height * (maxDim / width)); width = maxDim }
          else { width = Math.round(width * (maxDim / height)); height = maxDim }
        }
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        if (!ctx) { reject(new Error('Kunde inte bearbeta bilden.')); return }
        ctx.drawImage(img, 0, 0, width, height)
        resolve(canvas.toDataURL('image/jpeg', quality))
      }
      img.onerror = () => reject(new Error('Kunde inte läsa bilden.'))
      img.src = reader.result as string
    }
    reader.onerror = () => reject(new Error('Kunde inte läsa filen.'))
    reader.readAsDataURL(file)
  })
}

async function onImageSelected(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  errorMessage.value = ''
  if (!file.type.startsWith('image/')) {
    errorMessage.value = 'Filen måste vara en bild.'
    return
  }
  if (file.size > 15 * 1024 * 1024) {
    errorMessage.value = 'Bilden är för stor (max 15 MB innan komprimering).'
    return
  }
  isProcessingImage.value = true
  try {
    image.value = await resizeImage(file)
  } catch {
    errorMessage.value = 'Kunde inte bearbeta bilden. Försök med en annan fil.'
  } finally {
    isProcessingImage.value = false
  }
}
function removeImage() {
  image.value = ''
  if (imageInput.value) imageInput.value.value = ''
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
    image: image.value,
    description: description.value.trim(),
    ingredients: ingredients.value.map((i) => i.trim()).filter(Boolean),
    steps: steps.value.map((s) => s.trim()).filter(Boolean),
    is_public: isPublic.value,
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
        <AppNavProfile />
      </nav>
    </header>

    <main>
      <router-link to="/recipes" class="back-link">← Tillbaka till alla recept</router-link>
      <h1>{{ isEditMode ? 'Redigera recept' : 'Nytt recept' }}</h1>

      <p v-if="isLoading">Laddar...</p>
      <form v-else class="recipe-form" @submit.prevent="save">
        <transition name="fade"><div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div></transition>

        <label>Titel<input v-model="title" type="text" required placeholder="T.ex. Köttbullar med potatismos" /></label>

        <div class="row">
          <label>Kategori
            <input v-model="category" type="text" list="category-options" placeholder="T.ex. Middag" />
            <datalist id="category-options">
              <option v-for="cat in categories" :key="cat" :value="cat" />
            </datalist>
          </label>
          <label>Tid<input v-model="time" type="text" placeholder="T.ex. 45 min" /></label>
        </div>

        <label>Bild
          <div class="image-uploader">
            <div class="preview" :class="{ empty: !image }">
              <img v-if="image" :src="image" alt="Förhandsvisning av receptbilden" />
              <span v-else-if="isProcessingImage">Bearbetar bild...</span>
              <span v-else>Ingen bild vald</span>
            </div>
            <div class="image-actions">
              <input ref="imageInput" type="file" accept="image/*" @change="onImageSelected" />
              <button v-if="image" type="button" class="remove-image" @click="removeImage">Ta bort bild</button>
            </div>
          </div>
        </label>

        <label>Beskrivning<textarea v-model="description" rows="3" placeholder="Kort presentation av receptet"></textarea></label>

        <div class="dynamic-list">
          <span class="list-label">Ingredienser</span>
          <div v-for="(ingredient, index) in ingredients" :key="index" class="dynamic-row">
            <input v-model="ingredients[index]" type="text" :placeholder="`Ingrediens ${index + 1}, t.ex. 500 g nötfärs`" />
            <button v-if="ingredients.length > 1" type="button" class="remove-row" @click="removeIngredient(index)" aria-label="Ta bort ingrediens">✕</button>
          </div>
          <button type="button" class="add-row" @click="addIngredient">+ Lägg till ingrediens</button>
        </div>

        <div class="dynamic-list">
          <span class="list-label">Gör så här</span>
          <div v-for="(step, index) in steps" :key="index" class="dynamic-row">
            <span class="step-number">{{ index + 1 }}</span>
            <textarea v-model="steps[index]" rows="2" :placeholder="`Steg ${index + 1}...`"></textarea>
            <button v-if="steps.length > 1" type="button" class="remove-row" @click="removeStep(index)" aria-label="Ta bort steg">✕</button>
          </div>
          <button type="button" class="add-row" @click="addStep">+ Lägg till steg</button>
        </div>

        <fieldset class="visibility">
          <legend>Synlighet</legend>
          <label class="radio"><input type="radio" :value="true" v-model="isPublic" /> Publikt <span>Syns för alla besökare</span></label>
          <label class="radio"><input type="radio" :value="false" v-model="isPublic" /> Privat <span>Bara du (och admin) kan se det</span></label>
        </fieldset>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="isSaving || isProcessingImage">{{ isSaving ? 'Sparar...' : 'Spara recept' }}</button>
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
main { width: min(760px, calc(100% - 3rem)); margin: 0 auto; padding: 2rem 0 4rem; }
.back-link { display: inline-block; margin-bottom: 1.5rem; color: #b46649; font: .73rem Arial, sans-serif; text-decoration: none; }
h1 { margin: 0 0 1.5rem; font-size: 2rem; }
.recipe-form { display: flex; flex-direction: column; gap: 1.1rem; background: white; border: 1px solid #eee5de; border-radius: 10px; padding: 1.75rem; }
.recipe-form > label { display: flex; flex-direction: column; gap: .4rem; font: 600 .78rem Arial, sans-serif; color: #443e39; }
.recipe-form input[type="text"], .recipe-form textarea { border: 1px solid #e2ddd5; border-radius: 8px; padding: .65rem .8rem; font: .85rem Arial, sans-serif; outline: none; resize: vertical; width: 100%; box-sizing: border-box; }
.recipe-form input:focus, .recipe-form textarea:focus { border-color: #c87a57; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.image-uploader { display: flex; gap: 1rem; align-items: center; }
.preview { width: 140px; height: 100px; flex-shrink: 0; border-radius: 8px; border: 1px dashed #dfd2c8; display: grid; place-items: center; overflow: hidden; background: #faf5f0; }
.preview img { width: 100%; height: 100%; object-fit: cover; }
.preview.empty span { color: #b3a49a; font: .65rem Arial, sans-serif; text-align: center; padding: 0 .5rem; }
.image-actions { display: flex; flex-direction: column; gap: .5rem; }
.image-actions input[type="file"] { font: .72rem Arial, sans-serif; }
.remove-image { align-self: flex-start; border: 1px solid #e9ddd5; border-radius: 6px; background: white; padding: .35rem .6rem; font: .68rem Arial, sans-serif; color: #b3453a; cursor: pointer; }
.dynamic-list { display: flex; flex-direction: column; gap: .5rem; }
.list-label { font: 600 .78rem Arial, sans-serif; color: #443e39; }
.dynamic-row { display: flex; align-items: flex-start; gap: .5rem; }
.step-number { flex: 0 0 22px; height: 22px; margin-top: .4rem; border-radius: 50%; background: #fcece5; color: #c77354; display: grid; place-items: center; font: 700 .68rem Arial, sans-serif; }
.remove-row { flex: 0 0 auto; border: 1px solid #e9ddd5; border-radius: 6px; background: white; width: 32px; height: 32px; color: #b3453a; cursor: pointer; }
.add-row { align-self: flex-start; border: 1px dashed #d9a889; border-radius: 8px; background: #fffaf6; color: #bc6d4f; padding: .5rem .9rem; font: 600 .72rem Arial, sans-serif; cursor: pointer; }
.add-row:hover { background: #fff1e8; }
.visibility { border: 1px solid #e2ddd5; border-radius: 8px; padding: .9rem 1rem 1.1rem; display: flex; flex-direction: column; gap: .6rem; }
.visibility legend { padding: 0 .4rem; font: 600 .72rem Arial, sans-serif; color: #443e39; }
.radio { flex-direction: row !important; align-items: center; gap: .5rem !important; font-weight: 400 !important; }
.radio input { width: auto; }
.radio span { margin-left: .3rem; }
.error-banner { background-color: #fde8e8; color: #9b1c1c; padding: .75rem; border-radius: 8px; font-size: .85rem; }
.form-actions { display: flex; gap: .8rem; align-items: center; margin-top: .5rem; }
.btn-primary { background-color: #c87a57; color: white; border: none; padding: .75rem 1.3rem; border-radius: 25px; font-size: .85rem; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: .7; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background-color: #b36846; }
.btn-cancel { color: #78716a; font: .78rem Arial, sans-serif; text-decoration: none; }
footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@media (max-width: 620px) { .row { grid-template-columns: 1fr; } .image-uploader { flex-direction: column; align-items: flex-start; } }
</style>