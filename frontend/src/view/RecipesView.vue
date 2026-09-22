<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFavorites } from '@/composables/useFavorites'
import { useAuth } from '@/composables/useAuth'
import AppLogo from '@/components/AppLogo.vue'

const search = ref('')
const selectedCategory = ref('Alla recept')
const { isFavorite, toggleFavorite } = useFavorites()
const { logout } = useAuth()
const isAdmin = localStorage.getItem('userRole') === 'admin'

const categories = ['Alla recept', 'Fisk & Skaldjur', 'Maträtter', 'Sallader & Soppor', 'Klassiker', 'Smårätter']

const recipes = [
  {
    slug: 'kottbullar-med-potatismos',
    title: 'Köttbullar med potatismos',
    time: '45 min',
    category: 'Klassiker',
    image: 'https://images.unsplash.com/photo-1529042410759-befb1204b468?auto=format&fit=crop&w=900&q=85',
  },
  {
    slug: 'pasta-frutti-di-mare',
    title: 'Pasta frutti di mare',
    time: '30 min',
    category: 'Fisk & Skaldjur',
    image: 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=900&q=85',
  },
  {
    slug: 'pasta-carbonara',
    title: 'Pasta carbonara',
    time: '25 min',
    category: 'Maträtter',
    image: 'https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=900&q=85',
  },
  {
    slug: 'ortfile-med-rostad-potatis',
    title: 'Örtfilé med rostad potatis',
    time: '1 h 15 min',
    category: 'Maträtter',
    image: 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=85',
  },
]

const filteredRecipes = computed(() => {
  const query = search.value.trim().toLowerCase()
  return recipes.filter((recipe) => {
    const matchesCategory = selectedCategory.value === 'Alla recept' || recipe.category === selectedCategory.value
    return matchesCategory && recipe.title.toLowerCase().includes(query)
  })
})
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
      <section class="intro">
        <p class="eyebrow">DIN DIGITALA RECEPTPÄRM</p>
        <h1>Alla Recept</h1>
        <p>Den personliga digitala kokboken. Spara, planera och hitta nya favoritrecept här.</p>
      </section>

      <section class="tools" aria-label="Sök och filtrera recept">
        <label class="search-box">
          <span aria-hidden="true">⌕</span>
          <input v-model="search" type="search" placeholder="Sök efter recept, ingredienser eller kategori..." />
        </label>
        <button class="filter-button" type="button"><span aria-hidden="true">≡</span> Filter</button>
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

      <section class="recipe-grid" aria-label="Recept">
        <article v-for="recipe in filteredRecipes" :key="recipe.title" class="recipe-card">
          <router-link :to="`/recipes/${recipe.slug}`" class="recipe-link">
            <img :src="recipe.image" :alt="recipe.title" />
            <div class="recipe-details">
              <h2>{{ recipe.title }}</h2>
              <div class="card-footer">
                <span class="time">◷ {{ recipe.time }}</span>
                <button class="favorite" type="button" :aria-label="`Växla favorit för ${recipe.title}`" @click.prevent="toggleFavorite(recipe.slug)">{{ isFavorite(recipe.slug) ? '♥' : '♡' }}</button>
              </div>
            </div>
          </router-link>
        </article>
        <p v-if="filteredRecipes.length === 0" class="empty-state">Inga recept matchar din sökning.</p>
      </section>
    </main>

    <footer>
      <span>Smaklig måltid!</span>
    </footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #f9f7f3; color: #352c28; font-family: Georgia, 'Times New Roman', serif; }
.navbar { height: 61px; padding: 0 8%; display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }
.logo { display: flex; align-items: center; gap: .4rem; color: #9d5138; font-size: 1rem; font-weight: bold; text-decoration: none; }
.logo-mark { display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; background: #c86f4e; color: white; font-family: sans-serif; font-size: .75rem; }
nav { display: flex; gap: 1.5rem; } nav a { color: #756862; font-family: Arial, sans-serif; font-size: .78rem; text-decoration: none; }
.logout { border: 1px solid #e5d8cf; border-radius: 999px; background: transparent; padding: .35rem .65rem; color: #756862; font: .78rem Arial, sans-serif; cursor: pointer; }.logout:hover { color: #b86648; border-color: #d49a83; }
.admin-link { color: #b86648 !important; font-weight: 700; }
main { width: min(940px, calc(100% - 3rem)); margin: 0 auto; padding: 3.5rem 0 4.5rem; }
.intro { text-align: center; } .eyebrow { margin: 0 0 .5rem; color: #b6785b; font-family: Arial, sans-serif; font-size: .6rem; font-weight: bold; letter-spacing: .12em; }
h1 { margin: 0; font-size: clamp(2rem, 5vw, 3.1rem); } .intro > p:last-child { max-width: 510px; margin: .85rem auto 1.8rem; color: #8c817b; font-family: Arial, sans-serif; font-size: .78rem; line-height: 1.6; }
.tools { display: flex; justify-content: center; gap: .5rem; }.search-box { width: min(500px, 100%); display: flex; align-items: center; gap: .55rem; padding: .65rem .85rem; background: white; border: 1px solid #e7ddd4; border-radius: 5px; color: #c4866a; }.search-box input { width: 100%; border: 0; outline: 0; color: #443b37; font: .76rem Arial, sans-serif; }.search-box input::placeholder { color: #b6aaa3; }.filter-button { border: 1px solid #e7ddd4; border-radius: 5px; background: white; color: #756862; padding: 0 .85rem; font: .72rem Arial, sans-serif; }
.category-list { display: flex; justify-content: center; flex-wrap: wrap; gap: .45rem; margin: 1rem 0 2.8rem; }.category-list button { cursor: pointer; border: 1px solid #e2d7cf; border-radius: 999px; background: #fffdfa; color: #736763; padding: .4rem .72rem; font: .65rem Arial, sans-serif; }.category-list button.active { border-color: #c87554; background: #c87554; color: white; }
.recipe-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2rem 2.6rem; }.recipe-card { overflow: hidden; background: white; border: 1px solid #eee6df; box-shadow: 0 2px 6px rgb(64 40 26 / 6%); transition: transform .18s, box-shadow .18s; }.recipe-card:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgb(64 40 26 / 12%); }.recipe-link { display: block; color: inherit; text-decoration: none; }.recipe-card img { display: block; width: 100%; height: 210px; object-fit: cover; }.recipe-details { padding: .7rem .85rem .8rem; }.recipe-card h2 { margin: 0 0 .65rem; font-size: 1.03rem; font-style: italic; }.card-footer { display: flex; align-items: center; justify-content: space-between; }.time { color: #a79b95; font: .66rem Arial, sans-serif; }.favorite { display: grid; place-items: center; width: 25px; height: 20px; border: 1px solid #ecdcd2; border-radius: 4px; background: white; color: #cb8064; cursor: pointer; }.empty-state { grid-column: 1 / -1; text-align: center; color: #8c817b; font-family: Arial, sans-serif; }
footer { padding: 2rem; text-align: center; background: #f0e9e1; color: #453833; font-size: .9rem; font-style: italic; font-weight: bold; } footer span::after { content: ''; display: block; width: 20px; height: 1px; margin: .6rem auto 0; background: #c87554; }
@media (max-width: 620px) { .navbar { padding: 0 1.5rem; } nav { gap: .8rem; } main { width: min(100% - 2rem, 940px); padding-top: 2.5rem; }.recipe-grid { grid-template-columns: 1fr; gap: 1.5rem; }.recipe-card img { height: 220px; } }
.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); }.navbar :deep(.app-logo) { flex-shrink: 0; } main { width: min(1440px, calc(100% - 5rem)); }.recipe-grid { max-width: 1120px; margin-inline: auto; gap: 2.4rem 3.5rem; }
</style>
