<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, type Recipe } from '@/lib/api'
import { useFavorites } from '@/composables/useFavorites'
import AppLogo from '@/components/AppLogo.vue'
import AppNavProfile from '@/components/AppNavProfile.vue'
import AuthorChip from '@/components/AuthorChip.vue'

const route = useRoute()
const router = useRouter()
const { isFavorite, toggleFavorite } = useFavorites()
const isAdmin = sessionStorage.getItem('userRole') === 'admin'
const userEmail = sessionStorage.getItem('userEmail') || ''
const isLoggedIn = !!sessionStorage.getItem('token')

const recipe = ref<Recipe | null>(null)
const isLoading = ref(true)
const loadError = ref('')
const checkedSteps = ref<boolean[]>([])

function progressKey(slug: string) { return `recipe-progress:${slug}` }
function loadProgress(slug: string, stepCount: number) {
  try {
    const raw = localStorage.getItem(progressKey(slug))
    const saved = raw ? (JSON.parse(raw) as boolean[]) : []
    checkedSteps.value = Array.from({ length: stepCount }, (_, i) => !!saved[i])
  } catch {
    checkedSteps.value = Array(stepCount).fill(false)
  }
}
function toggleStep(index: number) {
  checkedSteps.value[index] = !checkedSteps.value[index]
  if (recipe.value) localStorage.setItem(progressKey(recipe.value.slug), JSON.stringify(checkedSteps.value))
}
function resetProgress() {
  if (!recipe.value) return
  checkedSteps.value = checkedSteps.value.map(() => false)
  localStorage.removeItem(progressKey(recipe.value.slug))
}
const doneCount = computed(() => checkedSteps.value.filter(Boolean).length)

async function loadRecipe() {
  isLoading.value = true
  loadError.value = ''
  recipe.value = null
  try {
    const slug = route.params.slug as string
    const response = await api.get<Recipe>(`/recipes/${slug}`)
    recipe.value = response.data
    loadProgress(slug, response.data.steps.length)
  } catch (error: any) {
    loadError.value = error.response?.status === 403
      ? 'Det här receptet är privat.'
      : 'Vi hittade inte det receptet.'
  } finally {
    isLoading.value = false
  }
}
onMounted(loadRecipe)
watch(() => route.params.slug, loadRecipe)

const canEdit = computed(() => !!recipe.value && (isAdmin || recipe.value.createdBy === userEmail))

async function removeRecipe() {
  if (!recipe.value) return
  if (!confirm(`Vill du verkligen ta bort "${recipe.value.title}"?`)) return
  await api.delete(`/recipes/${recipe.value.slug}`)
  router.push('/recipes')
}
</script>

<template>
  <div class="page-container">
    <header class="navbar">
      <AppLogo />
      <nav>
        <router-link to="/recipes">Alla recept</router-link>
        <router-link to="/contact">Kontakta oss</router-link>
        <template v-if="isLoggedIn"><AppNavProfile /></template>
        <router-link v-else to="/login" class="btn-outline">Logga in</router-link>
      </nav>
    </header>

    <main>
      <router-link to="/recipes" class="back-link">← Tillbaka till alla recept</router-link>

      <p v-if="isLoading">Laddar recept...</p>
      <p v-else-if="loadError">{{ loadError }}</p>

      <template v-else-if="recipe">
        <div class="title-row">
          <div>
            <p class="eyebrow">{{ recipe.category }} <span v-if="!recipe.isPublic" class="private-badge">Privat</span></p>
            <h1>{{ recipe.title }}</h1>
            <AuthorChip class="by-author" :email="recipe.createdBy" :name="recipe.authorName" />
          </div>
          <div class="actions">
            <button class="heart" type="button" :aria-label="isFavorite(recipe.slug) ? 'Ta bort favorit' : 'Lägg till favorit'" @click="toggleFavorite(recipe.slug)">{{ isFavorite(recipe.slug) ? '♥' : '♡' }}</button>
            <router-link v-if="canEdit" :to="`/recipes/${recipe.slug}/edit`" class="edit-link">Redigera</router-link>
            <button v-if="canEdit" class="delete-link" type="button" @click="removeRecipe">Ta bort</button>
          </div>
        </div>
        <img v-if="recipe.image" :src="recipe.image" :alt="recipe.title" class="hero-image" />
        <p class="description">{{ recipe.description }}</p>
        <div class="facts">
          <span v-if="recipe.time">◷ {{ recipe.time }}</span>
          <span class="difficulty" :class="'diff-' + recipe.difficulty">● {{ recipe.difficulty }}</span>
          <span>🍽 {{ recipe.portions }} {{ recipe.portions === 1 ? 'portion' : 'portioner' }}</span>
        </div>

        <section class="content">
          <aside class="ingredients">
            <div class="section-heading"><h2>Ingredienser</h2></div>
            <div v-for="(group, groupIndex) in recipe.ingredientGroups" :key="groupIndex" class="ingredient-group">
              <h3 v-if="group.name && (recipe.ingredientGroups.length > 1 || group.name !== 'Ingredienser')">{{ group.name }}</h3>
              <ul>
                <li v-for="ingredient in group.items" :key="ingredient">{{ ingredient }}</li>
                <li v-if="!group.items.length" class="muted">Inga ingredienser tillagda ännu.</li>
              </ul>
            </div>
          </aside>
          <section class="instructions">
            <div class="section-heading">
              <h2>Gör så här</h2>
              <div v-if="doneCount" class="progress"><span>{{ doneCount }}/{{ recipe.steps.length }} klara</span><button type="button" @click="resetProgress">Återställ</button></div>
            </div>
            <ol>
              <li v-for="(step, index) in recipe.steps" :key="step + index" class="step" :class="{ done: checkedSteps[index] }">
                <button type="button" class="checkbox" :aria-pressed="checkedSteps[index]" :aria-label="checkedSteps[index] ? 'Markera steg som ogjort' : 'Markera steg som klart'" @click="toggleStep(index)">
                  <svg v-if="checkedSteps[index]" viewBox="0 0 24 24"><path d="M5 12l5 5 9-9" /></svg>
                  <span v-else>{{ index + 1 }}</span>
                </button>
                <p>{{ step }}</p>
              </li>
              <li v-if="!recipe.steps.length" class="muted"><p>Inga steg tillagda ännu.</p></li>
            </ol>
          </section>
        </section>
      </template>
    </main>
    <footer><span>Smaklig måltid!</span><small>Skapad med kärlek till den skandinaviska matkulturen.</small></footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #faf8f4; color: #382e2a; font-family: Georgia, 'Times New Roman', serif; }.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }nav { display: flex; align-items: center; gap: 1.5rem; }nav a { color: #756862; font: .78rem Arial, sans-serif; text-decoration: none; }.btn-outline { border: 1px solid #e5d8cf; border-radius: 999px; padding: .4rem .9rem; }main { width: min(1040px, calc(100% - 3rem)); margin: 0 auto; padding: 2rem 0 4rem; }.back-link { display: inline-block; margin-bottom: 2rem; color: #b46649; font: .73rem Arial, sans-serif; text-decoration: none; }.title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }.actions { display: flex; align-items: center; gap: .6rem; }.heart { border: 1px solid #eaded5; border-radius: 6px; background: white; color: #c87355; font-size: 1.1rem; padding: .3rem .6rem; cursor: pointer; }.edit-link, .delete-link { border: 1px solid #eaded5; border-radius: 6px; background: white; padding: .4rem .7rem; font: .68rem Arial, sans-serif; text-decoration: none; cursor: pointer; }.edit-link { color: #bc6d4f; }.delete-link { color: #b3453a; }.eyebrow { margin: 0 0 .55rem; color: #bf775a; font: bold .6rem Arial, sans-serif; letter-spacing: .1em; display: flex; align-items: center; gap: .5rem; }.private-badge { background: #f3e2da; color: #a55c3f; border-radius: 999px; padding: .15rem .5rem; letter-spacing: 0; font-weight: 700; }h1 { max-width: 900px; margin: 0; font-size: clamp(1.9rem, 4vw, 3rem); line-height: 1.1; }.by-author { margin-top: .9rem; }.hero-image { width: 100%; max-height: 420px; object-fit: cover; border-radius: 10px; margin: 1.5rem 0; background: #eee6df; }.description { max-width: 780px; color: #857a74; font: .85rem/1.6 Arial, sans-serif; }.facts { display: flex; flex-wrap: wrap; gap: .65rem; margin: 1.5rem 0 2rem; }.facts span { border: 1px solid #eaded5; border-radius: 4px; background: white; padding: .5rem .65rem; color: #7f7169; font: .67rem Arial, sans-serif; }.difficulty { font-weight: 600; }.diff-Lätt { color: #3a8a52; } .diff-Medel { color: #b3822f; } .diff-Svår { color: #b3453a; }.content { display: grid; grid-template-columns: 280px 1fr; gap: 2rem; align-items: start; }.ingredients, .instructions { background: white; border: 1px solid #eee5de; border-radius: 8px; padding: 1.25rem; }.section-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .5rem; }h2 { margin: 0; font-size: 1.1rem; }.group-tabs { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .9rem; }.tab { border: 1px solid #e2d7cf; border-radius: 999px; background: #fffdfa; color: #6b5e57; padding: .32rem .7rem; font: 600 .64rem Arial, sans-serif; cursor: pointer; }.tab.active { border-color: #c4623f; background: #c4623f; color: #fff; }.single-group-name { margin: .8rem 0 0; color: #9a8c84; font: 600 .68rem Arial, sans-serif; }.ingredients ul { margin: 1rem 0 0; padding: 0; list-style: none; }.ingredients li { padding: .5rem 0; border-bottom: 1px solid #f0e8e2; color: #746862; font: .73rem Arial, sans-serif; }.ingredients li::before { content: '•'; color: #cf8060; margin-right: .5rem; }.muted::before { content: none !important; }.progress { display: flex; align-items: center; gap: .6rem; color: #9a8c84; font: .66rem Arial, sans-serif; }.progress button { border: 1px solid #e9ddd5; border-radius: 6px; background: white; padding: .25rem .5rem; color: #88786f; font: .62rem Arial, sans-serif; cursor: pointer; }.instructions ol { margin: 1.2rem 0; padding: 0; list-style: none; }.step { display: flex; gap: .8rem; padding: .55rem 0; align-items: flex-start; }.checkbox { flex: 0 0 22px; width: 22px; height: 22px; margin-top: .1rem; border-radius: 50%; border: 1.5px solid #d9a889; background: #fcece5; color: #c77354; display: grid; place-items: center; font: 700 .62rem Arial, sans-serif; cursor: pointer; padding: 0; }.checkbox svg { width: 13px; height: 13px; fill: none; stroke: #fff; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }.step.done .checkbox { background: #3a8a52; border-color: #3a8a52; }.step p { margin: 0; color: #685d57; font: .74rem/1.55 Arial, sans-serif; transition: opacity .18s, color .18s; }.step.done p { opacity: .5; text-decoration: line-through; color: #9a8c84; }footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }footer small { display: block; margin-top: .45rem; color: #93857d; font: .58rem Arial, sans-serif; }footer span::after { content: ''; display: block; width: 20px; height: 1px; margin: .6rem auto 0; background: #c87554; }@media (max-width: 680px) { .navbar { padding-inline: 1.5rem; }.content { grid-template-columns: 1fr; }.facts { gap: .4rem; }main { width: min(100% - 2rem, 1040px); }nav { gap: .8rem; } }
</style>
