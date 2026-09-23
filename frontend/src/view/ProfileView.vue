<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, type Recipe } from '@/lib/api'
import { useFavorites } from '@/composables/useFavorites'
import { useAuth } from '@/composables/useAuth'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
const { favoriteSlugs, toggleFavorite } = useFavorites()
const { logout } = useAuth()
const isAdmin = localStorage.getItem('userRole') === 'admin'

const email = ref(localStorage.getItem('userEmail') || 'minprofil@koksboken.se')
const name = ref((email.value.split('@')[0] || 'Köksvän').replace(/[._-]/g, ' '))
const avatarUrl = ref<string | null>(null)

const allRecipes = ref<Recipe[]>([])
const favoriteRecipes = computed(() => allRecipes.value.filter((recipe) => favoriteSlugs.value.includes(recipe.slug)))

const isEditingProfile = ref(false)
const editName = ref('')
const editAvatarUrl = ref('')
const isSavingProfile = ref(false)
const profileError = ref('')

async function loadProfile() {
  try {
    const response = await api.get('/auth/me')
    name.value = response.data.name
    avatarUrl.value = response.data.avatar_url
  } catch {
    // Behåll fallback-värdena om anropet misslyckas
  }
}

async function loadRecipes() {
  try {
    const response = await api.get<Recipe[]>('/recipes/')
    allRecipes.value = response.data
  } catch {
    allRecipes.value = []
  }
}

onMounted(() => {
  loadProfile()
  loadRecipes()
})

function openEditProfile() {
  editName.value = name.value
  editAvatarUrl.value = avatarUrl.value || ''
  profileError.value = ''
  isEditingProfile.value = true
}

async function saveProfile() {
  isSavingProfile.value = true
  profileError.value = ''
  try {
    const response = await api.patch('/auth/me', {
      name: editName.value.trim() || undefined,
      avatar_url: editAvatarUrl.value.trim() || undefined,
    })
    name.value = response.data.name
    avatarUrl.value = response.data.avatar_url
    isEditingProfile.value = false
  } catch {
    profileError.value = 'Kunde inte spara profilen.'
  } finally {
    isSavingProfile.value = false
  }
}

function goToNewRecipe() {
  router.push('/recipes/new')
}
</script>

<template>
  <div class="page-container">
    <header class="navbar">
      <AppLogo />
      <nav><router-link to="/recipes">Utforska</router-link><router-link to="/recipes">Mina recept</router-link><router-link to="/profile" class="current">Min profil</router-link><router-link v-if="isAdmin" to="/admin" class="admin-link">Adminpanel</router-link><button class="logout" type="button" @click="logout">Logga ut</button></nav>
    </header>

    <section class="cover"></section>
    <main>
      <section class="profile-intro">
        <div class="avatar">
          <img v-if="avatarUrl" :src="avatarUrl" :alt="name" />
          <span v-else>{{ name.charAt(0).toUpperCase() }}</span>
        </div>
        <div><p class="eyebrow">MIN PROFIL</p><h1>{{ name }}</h1><p class="location">Hemmakock i Sverige</p></div>
        <button class="edit" type="button" @click="openEditProfile">Redigera profil</button>
        <button class="new-recipe" type="button" @click="goToNewRecipe">+ Nytt recept</button>
      </section>

      <div v-if="isEditingProfile" class="edit-panel">
        <div v-if="profileError" class="error-banner">{{ profileError }}</div>
        <label>Namn<input v-model="editName" type="text" placeholder="Ditt namn" /></label>
        <label>Profilbild (URL)<input v-model="editAvatarUrl" type="url" placeholder="https://..." /></label>
        <div class="edit-actions">
          <button type="button" class="save" :disabled="isSavingProfile" @click="saveProfile">{{ isSavingProfile ? 'Sparar...' : 'Spara' }}</button>
          <button type="button" class="cancel" @click="isEditingProfile = false">Avbryt</button>
        </div>
      </div>

      <p class="bio">Välkommen till min personliga receptsamling! Här sparar jag mina favoriter, provar nya idéer och delar matglädjen med andra.</p>

      <section class="stats"><div><strong>{{ favoriteRecipes.length }}</strong><span>Favoriter</span></div><div><strong>{{ allRecipes.length }}</strong><span>Recept att prova</span></div><div><strong>1</strong><span>Veckomeny</span></div></section>

      <div class="layout">
        <aside>
          <h2>Inställningar</h2>
          <button class="menu-item active">♡ Favoritrecept <span>{{ favoriteRecipes.length }}</span></button>
          <div class="tip"><strong>MIN KÖKSBOK</strong><p>Dina sparade recept syns här. Klicka på hjärtat för att lägga till eller ta bort en favorit.</p></div>
        </aside>
        <section class="favorites">
          <div class="section-top"><div><p class="eyebrow">DIN SAMLING</p><h2>Sparade favoriter</h2></div><router-link to="/recipes">Visa alla recept →</router-link></div>
          <div v-if="favoriteRecipes.length" class="recipe-grid">
            <article v-for="recipe in favoriteRecipes" :key="recipe.slug" class="recipe-card">
              <router-link :to="`/recipes/${recipe.slug}`" class="recipe-link"><img :src="recipe.image" :alt="recipe.title" /><div><p>{{ recipe.category }}</p><h3>{{ recipe.title }}</h3><span>◷ {{ recipe.time }}</span></div></router-link>
              <button class="heart" type="button" :aria-label="`Ta bort ${recipe.title} från favoriter`" @click="toggleFavorite(recipe.slug)">♥</button>
            </article>
          </div>
          <div v-else class="empty"><span>♡</span><h3>Inga favoriter ännu</h3><p>Utforska recept och tryck på hjärtat för att spara dem här.</p><router-link to="/recipes">Utforska recept</router-link></div>
        </section>
      </div>
    </main>
    <footer><span>Smaklig måltid!</span><small>Skapad med kärlek till den skandinaviska matkulturen.</small></footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #faf8f4; color: #382e2a; font-family: Georgia, 'Times New Roman', serif; }.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }nav { display: flex; gap: 1.4rem; }nav a { color: #756862; font: .75rem Arial, sans-serif; text-decoration: none; }nav .current { color: #be6d50; font-weight: bold; }.cover { height: 180px; background: linear-gradient(90deg, rgb(52 33 22 / 16%), transparent), url('https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=1600&q=85') center 52% / cover; }main { width: min(1040px, calc(100% - 3rem)); margin: 0 auto; padding: 0 0 4rem; }.profile-intro { position: relative; display: flex; align-items: end; gap: 1rem; margin-top: -35px; }.avatar { display: grid; place-items: center; width: 78px; height: 78px; border: 4px solid #faf8f4; border-radius: 50%; background: #d58a68; color: white; font-size: 2rem; text-transform: uppercase; overflow: hidden; }.avatar img { width: 100%; height: 100%; object-fit: cover; }.eyebrow { margin: 0 0 .3rem; color: #bd7255; font: bold .58rem Arial, sans-serif; letter-spacing: .1em; }h1 { margin: 0; font-size: 1.75rem; text-transform: capitalize; }.location { margin: .2rem 0 0; color: #81736c; font: .7rem Arial, sans-serif; }.edit, .new-recipe { align-self: center; border-radius: 5px; padding: .55rem .8rem; font: .68rem Arial, sans-serif; cursor: pointer; }.edit { margin-left: auto; border: 1px solid #e5d7ce; background: white; color: #655a54; }.new-recipe { border: 1px solid #c87050; background: #c87050; color: white; }
.edit-panel { margin-top: 1.2rem; border: 1px solid #eee1d8; border-radius: 8px; background: white; padding: 1.2rem; display: flex; flex-direction: column; gap: .8rem; }
.edit-panel label { display: flex; flex-direction: column; gap: .35rem; font: 600 .7rem Arial, sans-serif; color: #443e39; }
.edit-panel input { border: 1px solid #e2ddd5; border-radius: 6px; padding: .55rem .7rem; font: .78rem Arial, sans-serif; }
.edit-actions { display: flex; gap: .6rem; }
.edit-actions .save { border: none; background: #c87050; color: white; border-radius: 5px; padding: .5rem .9rem; font: .7rem Arial, sans-serif; cursor: pointer; }
.edit-actions .cancel { border: 1px solid #e5d7ce; background: white; color: #655a54; border-radius: 5px; padding: .5rem .9rem; font: .7rem Arial, sans-serif; cursor: pointer; }
.error-banner { background-color: #fde8e8; color: #9b1c1c; padding: .6rem; border-radius: 6px; font-size: .75rem; }
.bio { max-width: 650px; margin: 1rem 0; color: #83756e; font: .73rem/1.6 Arial, sans-serif; }.stats { display: flex; gap: .7rem; margin: 1.4rem 0 2rem; }.stats div { min-width: 95px; padding: .6rem .9rem; border: 1px solid #eee1d8; border-radius: 5px; background: white; text-align: center; }.stats strong { display: block; color: #bd704f; font-size: 1.1rem; }.stats span { color: #8c7e76; font: .58rem Arial, sans-serif; }.layout { display: grid; grid-template-columns: 235px 1fr; gap: 2.5rem; }aside h2, .favorites h2 { margin: 0; font-size: 1.1rem; }.menu-item { display: flex; justify-content: space-between; width: 100%; margin-top: .55rem; border: 1px solid #eee3dc; border-radius: 5px; background: white; padding: .68rem .75rem; color: #70635d; font: .68rem Arial, sans-serif; text-align: left; cursor: pointer; }.menu-item.active { border-color: #d98a69; background: #fff6f1; color: #bc6d4f; }.tip { margin-top: 1rem; border-radius: 6px; background: #fbede7; padding: .8rem; }.tip strong { color: #bf7053; font: .58rem Arial, sans-serif; }.tip p { margin: .35rem 0 0; color: #796b64; font: .62rem/1.45 Arial, sans-serif; }.section-top { display: flex; justify-content: space-between; align-items: end; margin-bottom: 1rem; }.section-top a { color: #bd6d50; font: .65rem Arial, sans-serif; text-decoration: none; }.recipe-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.2rem; }.recipe-card { position: relative; overflow: hidden; border: 1px solid #eee4dc; border-radius: 7px; background: white; box-shadow: 0 2px 7px rgb(56 32 20 / 6%); }.recipe-link { color: inherit; text-decoration: none; }.recipe-card img { display: block; width: 100%; height: 135px; object-fit: cover; }.recipe-card div { padding: .7rem; }.recipe-card p { margin: 0 0 .3rem; color: #c0785b; font: .56rem Arial, sans-serif; }.recipe-card h3 { margin: 0 0 .45rem; font-size: .88rem; font-style: italic; }.recipe-card span { color: #9f9189; font: .6rem Arial, sans-serif; }.heart { position: absolute; right: .6rem; bottom: .6rem; border: 0; background: none; color: #c87355; font-size: 1rem; cursor: pointer; }.empty { border: 1px dashed #dfcfc5; border-radius: 8px; padding: 3.5rem 1.5rem; text-align: center; }.empty > span { color: #ce7c5d; font-size: 2rem; }.empty h3 { margin: .5rem 0; }.empty p { color: #81736c; font: .73rem Arial, sans-serif; }.empty a { color: #bd6d50; font: .72rem Arial, sans-serif; }footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }footer small { display: block; margin-top: .45rem; color: #93857d; font: .58rem Arial, sans-serif; }footer span::after { content: ''; display: block; width: 20px; height: 1px; margin: .6rem auto 0; background: #c87554; }@media (max-width: 720px) { .navbar { padding: 0 1.5rem; }nav { gap: .7rem; }.cover { height: 130px; }main { width: min(100% - 2rem, 1040px); }.layout { grid-template-columns: 1fr; }.recipe-grid { grid-template-columns: 1fr; }.profile-intro { flex-wrap: wrap; }.edit { margin-left: 0; }.new-recipe { margin-right: auto; } }
.logout { border: 1px solid #e5d8cf; border-radius: 999px; background: transparent; padding: .35rem .65rem; color: #756862; font: .75rem Arial, sans-serif; cursor: pointer; }.logout:hover { color: #b86648; border-color: #d49a83; }
.admin-link { color: #b86648 !important; font-weight: 700; }
</style>