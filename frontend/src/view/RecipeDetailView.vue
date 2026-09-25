<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, type Recipe } from '@/lib/api'
import { useFavorites } from '@/composables/useFavorites'
import AppLogo from '@/components/AppLogo.vue'
import AppNavProfile from '@/components/AppNavProfile.vue'

const route = useRoute()
const router = useRouter()
const { isFavorite, toggleFavorite } = useFavorites()
const isAdmin = localStorage.getItem('userRole') === 'admin'
const userEmail = localStorage.getItem('userEmail') || ''
const isLoggedIn = !!localStorage.getItem('token')

const recipe = ref<Recipe | null>(null)
const isLoading = ref(true)
const loadError = ref('')

async function loadRecipe() {
  isLoading.value = true
  loadError.value = ''
  recipe.value = null
  try {
    const slug = route.params.slug as string
    const response = await api.get<Recipe>(`/recipes/${slug}`)
    recipe.value = response.data
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
          </div>
          <div class="actions">
            <button class="heart" type="button" :aria-label="isFavorite(recipe.slug) ? 'Ta bort favorit' : 'Lägg till favorit'" @click="toggleFavorite(recipe.slug)">{{ isFavorite(recipe.slug) ? '♥' : '♡' }}</button>
            <router-link v-if="canEdit" :to="`/recipes/${recipe.slug}/edit`" class="edit-link">Redigera</router-link>
            <button v-if="canEdit" class="delete-link" type="button" @click="removeRecipe">Ta bort</button>
          </div>
        </div>
        <img v-if="recipe.image" :src="recipe.image" :alt="recipe.title" class="hero-image" />
        <p class="description">{{ recipe.description }}</p>
        <div v-if="recipe.time" class="facts"><span>◷ {{ recipe.time }}</span></div>

        <section class="content">
          <aside class="ingredients">
            <div class="section-heading"><h2>Ingredienser</h2></div>
            <ul>
              <li v-for="ingredient in recipe.ingredients" :key="ingredient">{{ ingredient }}</li>
              <li v-if="!recipe.ingredients.length" class="muted">Inga ingredienser tillagda ännu.</li>
            </ul>
          </aside>
          <section class="instructions">
            <h2>Gör så här</h2>
            <ol>
              <li v-for="(step, index) in recipe.steps" :key="step"><span>{{ index + 1 }}</span><p>{{ step }}</p></li>
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
.page-container { min-height: 100vh; background: #faf8f4; color: #382e2a; font-family: Georgia, 'Times New Roman', serif; }.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }nav { display: flex; align-items: center; gap: 1.5rem; }nav a { color: #756862; font: .78rem Arial, sans-serif; text-decoration: none; }.btn-outline { border: 1px solid #e5d8cf; border-radius: 999px; padding: .4rem .9rem; }main { width: min(1040px, calc(100% - 3rem)); margin: 0 auto; padding: 2rem 0 4rem; }.back-link { display: inline-block; margin-bottom: 2rem; color: #b46649; font: .73rem Arial, sans-serif; text-decoration: none; }.title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }.actions { display: flex; align-items: center; gap: .6rem; }.heart { border: 1px solid #eaded5; border-radius: 6px; background: white; color: #c87355; font-size: 1.1rem; padding: .3rem .6rem; cursor: pointer; }.edit-link, .delete-link { border: 1px solid #eaded5; border-radius: 6px; background: white; padding: .4rem .7rem; font: .68rem Arial, sans-serif; text-decoration: none; cursor: pointer; }.edit-link { color: #bc6d4f; }.delete-link { color: #b3453a; }.eyebrow { margin: 0 0 .55rem; color: #bf775a; font: bold .6rem Arial, sans-serif; letter-spacing: .1em; display: flex; align-items: center; gap: .5rem; }.private-badge { background: #f3e2da; color: #a55c3f; border-radius: 999px; padding: .15rem .5rem; letter-spacing: 0; font-weight: 700; }h1 { max-width: 900px; margin: 0; font-size: clamp(1.9rem, 4vw, 3rem); line-height: 1.1; }.hero-image { width: 100%; max-height: 420px; object-fit: cover; border-radius: 10px; margin: 1.5rem 0; background: #eee6df; }.description { max-width: 780px; color: #857a74; font: .85rem/1.6 Arial, sans-serif; }.facts { display: flex; flex-wrap: wrap; gap: .65rem; margin: 1.5rem 0 2rem; }.facts span { border: 1px solid #eaded5; border-radius: 4px; background: white; padding: .5rem .65rem; color: #7f7169; font: .67rem Arial, sans-serif; }.content { display: grid; grid-template-columns: 280px 1fr; gap: 2rem; align-items: start; }.ingredients, .instructions { background: white; border: 1px solid #eee5de; border-radius: 8px; padding: 1.25rem; }.section-heading { display: flex; align-items: center; justify-content: space-between; }h2 { margin: 0; font-size: 1.1rem; }.ingredients ul { margin: 1rem 0 0; padding: 0; list-style: none; }.ingredients li { padding: .5rem 0; border-bottom: 1px solid #f0e8e2; color: #746862; font: .73rem Arial, sans-serif; }.ingredients li::before { content: '•'; color: #cf8060; margin-right: .5rem; }.muted::before { content: none !important; }.instructions ol { margin: 1.2rem 0; padding: 0; list-style: none; }.instructions li { display: flex; gap: .8rem; padding: .55rem 0; }.instructions li > span { flex: 0 0 19px; width: 19px; height: 19px; border-radius: 50%; display: grid; place-items: center; background: #fcece5; color: #c77354; font: .62rem Arial, sans-serif; }.instructions p { margin: 0; color: #685d57; font: .74rem/1.55 Arial, sans-serif; }footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }footer small { display: block; margin-top: .45rem; color: #93857d; font: .58rem Arial, sans-serif; }footer span::after { content: ''; display: block; width: 20px; height: 1px; margin: .6rem auto 0; background: #c87554; }@media (max-width: 680px) { .navbar { padding-inline: 1.5rem; }.content { grid-template-columns: 1fr; }.facts { gap: .4rem; }main { width: min(100% - 2rem, 1040px); }nav { gap: .8rem; } }
</style>