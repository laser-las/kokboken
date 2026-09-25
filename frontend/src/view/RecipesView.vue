<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, type Recipe } from '@/lib/api'
import { useFavorites } from '@/composables/useFavorites'
import AppLogo from '@/components/AppLogo.vue'
import AppNavProfile from '@/components/AppNavProfile.vue'

const router = useRouter()
const search = ref('')
const selectedCategory = ref('Alla recept')
const { isFavorite, toggleFavorite } = useFavorites()
const isLoggedIn = !!localStorage.getItem('token')

const recipes = ref<Recipe[]>([])
const suggestedCategories = ref<string[]>([])
const isLoading = ref(true)
const loadError = ref('')

async function loadRecipes() {
  isLoading.value = true
  loadError.value = ''
  try {
    const response = await api.get<Recipe[]>('/recipes/')
    recipes.value = response.data
  } catch {
    loadError.value = 'Kunde inte hämta recept just nu.'
  } finally {
    isLoading.value = false
  }
}
async function loadCategories() {
  try {
    suggestedCategories.value = (await api.get<string[]>('/categories/')).data
  } catch {
    suggestedCategories.value = []
  }
}
onMounted(() => {
  loadRecipes()
  loadCategories()
})

const categories = computed(() => {
  const fromData = recipes.value.map((r) => r.category).filter(Boolean)
  const merged = Array.from(new Set([...suggestedCategories.value, ...fromData]))
  return ['Alla recept', ...merged]
})

const filteredRecipes = computed(() => {
  const query = search.value.trim().toLowerCase()
  return recipes.value.filter((recipe) => {
    const matchesCategory = selectedCategory.value === 'Alla recept' || recipe.category === selectedCategory.value
    return matchesCategory && recipe.title.toLowerCase().includes(query)
  })
})

function createRecipe() {
  if (!isLoggedIn) {
    router.push('/login')
    return
  }
  router.push('/recipes/new')
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
      <section class="intro">
        <p class="eyebrow">DIN DIGITALA RECEPTPÄRM</p>
        <h1>Alla Recept</h1>
        <p>Den personliga digitala kokboken. Spara, planera och hitta nya favoritrecept här.</p>
        <button class="new-recipe" type="button" @click="createRecipe">+ Nytt recept</button>
      </section>

      <section class="tools" aria-label="Sök och filtrera recept">
        <label class="search-box">
          <span aria-hidden="true">⌕</span>
          <input v-model="search" type="search" placeholder="Sök efter recept, ingredienser eller kategori..." />
        </label>
      </section>

      <div class="category-list" aria-label="Receptkategorier">
        <button
          v-for="category in categories"
          :key="category"
          type="button"
          :class="{ active: selectedCategory === category }"
          @click="selectedCategory = category"
        >
          {{ category }}
        </button>
      </div>

      <p v-if="isLoading" class="empty-state">Laddar recept...</p>
      <p v-else-if="loadError" class="empty-state">{{ loadError }}</p>
      <transition-group v-else name="card-fade" tag="section" class="recipe-grid" aria-label="Recept">
        <article v-for="recipe in filteredRecipes" :key="recipe.slug" class="recipe-card">
          <router-link :to="`/recipes/${recipe.slug}`" class="recipe-link">
            <img :src="recipe.image || 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?auto=format&fit=crop&w=900&q=85'" :alt="recipe.title" />
            <div class="recipe-details">
              <h2>{{ recipe.title }}</h2>
              <div class="card-footer">
                <span class="time">◷ {{ recipe.time }}</span>
                <button class="favorite" type="button" :aria-label="`Växla favorit för ${recipe.title}`" @click.prevent="toggleFavorite(recipe.slug)">{{ isFavorite(recipe.slug) ? '♥' : '♡' }}</button>
              </div>
            </div>
          </router-link>
        </article>
        <p v-if="filteredRecipes.length === 0" key="empty" class="empty-state">Inga recept matchar din sökning.</p>
      </transition-group>
    </main>

    <footer>
      <span>Smaklig måltid!</span>
    </footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #f9f7f3; color: #352c28; font-family: Georgia, 'Times New Roman', serif; }
.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }
.logo { display: flex; align-items: center; gap: .4rem; color: #9d5138; font-size: 1rem; font-weight: bold; text-decoration: none; }
nav { display: flex; align-items: center; gap: 1.5rem; } nav a { color: #756862; font-family: Arial, sans-serif; font-size: .78rem; text-decoration: none; }
.btn-outline { border: 1px solid #e5d8cf; border-radius: 999px; padding: .4rem .9rem; }
main { width: min(1440px, calc(100% - 5rem)); margin: 0 auto; padding: 3.5rem 0 4.5rem; }
.intro { text-align: center; } .eyebrow { margin: 0 0 .5rem; color: #b6785b; font-family: Arial, sans-serif; font-size: .6rem; font-weight: bold; letter-spacing: .12em; }
h1 { margin: 0; font-size: clamp(2rem, 5vw, 3.1rem); } .intro > p:nth-of-type(2) { max-width: 510px; margin: .85rem auto 1.8rem; color: #8c817b; font-family: Arial, sans-serif; font-size: .78rem; line-height: 1.6; }
.new-recipe { border: 1px solid #c87050; background: #c87050; color: white; border-radius: 999px; padding: .6rem 1.2rem; font: .72rem Arial, sans-serif; cursor: pointer; margin-bottom: 1.5rem; transition: background-color .15s; }
.new-recipe:hover { background: #b3603f; }
.tools { display: flex; justify-content: center; gap: .5rem; }.search-box { width: min(500px, 100%); display: flex; align-items: center; gap: .55rem; padding: .65rem .85rem; background: white; border: 1px solid #e7ddd4; border-radius: 5px; color: #c4866a; }.search-box input { width: 100%; border: 0; outline: 0; color: #443b37; font: .76rem Arial, sans-serif; }.search-box input::placeholder { color: #b6aaa3; }
.category-list { display: flex; justify-content: center; flex-wrap: wrap; gap: .45rem; margin: 1rem 0 2.8rem; }.category-list button { cursor: pointer; border: 1px solid #e2d7cf; border-radius: 999px; background: #fffdfa; color: #736763; padding: .4rem .72rem; font: .65rem Arial, sans-serif; transition: background-color .15s, color .15s; }.category-list button.active { border-color: #c87554; background: #c87554; color: white; }
.recipe-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 2.4rem 3rem; max-width: 1120px; margin-inline: auto; }.recipe-card { overflow: hidden; background: white; border: 1px solid #eee6df; box-shadow: 0 2px 6px rgb(64 40 26 / 6%); transition: transform .18s, box-shadow .18s; }.recipe-card:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgb(64 40 26 / 12%); }.recipe-link { display: block; color: inherit; text-decoration: none; }.recipe-card img { display: block; width: 100%; height: 210px; object-fit: cover; background: #eee6df; }.recipe-details { padding: .7rem .85rem .8rem; }.recipe-card h2 { margin: 0 0 .65rem; font-size: 1.03rem; font-style: italic; }.card-footer { display: flex; align-items: center; justify-content: space-between; }.time { color: #a79b95; font: .66rem Arial, sans-serif; }.favorite { display: grid; place-items: center; width: 25px; height: 20px; border: 1px solid #ecdcd2; border-radius: 4px; background: white; color: #cb8064; cursor: pointer; }.empty-state { grid-column: 1 / -1; text-align: center; color: #8c817b; font-family: Arial, sans-serif; }
.card-fade-enter-active { transition: opacity .3s ease, transform .3s ease; } .card-fade-enter-from { opacity: 0; transform: translateY(8px); }
footer { padding: 2rem; text-align: center; background: #f0e9e1; color: #453833; font-size: .9rem; font-style: italic; font-weight: bold; } footer span::after { content: ''; display: block; width: 20px; height: 1px; margin: .6rem auto 0; background: #c87554; }
@media (max-width: 620px) { .navbar { padding-inline: 1.5rem; } nav { gap: .8rem; } main { width: min(100% - 2rem, 940px); padding-top: 2.5rem; }.recipe-grid { grid-template-columns: 1fr; gap: 1.5rem; }.recipe-card img { height: 220px; } }
</style>