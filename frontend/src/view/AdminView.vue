<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, type Recipe } from '@/lib/api'
import { useAuth } from '@/composables/useAuth'

type User = { email: string; role: 'user' | 'admin' }
const users = ref<User[]>([])
const error = ref('')
const { logout } = useAuth()
const userEmail = localStorage.getItem('userEmail') || 'administratör'
const displayName = (userEmail.split('@')[0] || 'administratör').replace(/[._-]/g, ' ')

const activeTab = ref<'overview' | 'recipes'>('overview')
const recipes = ref<Recipe[]>([])
const recipesError = ref('')

async function loadUsers() {
  try { users.value = (await api.get('/auth/users')).data }
  catch { error.value = 'Kunde inte läsa användare. Kontrollera att du är administratör.' }
}
async function changeRole(user: User) {
  const role = user.role === 'admin' ? 'user' : 'admin'
  await api.patch(`/auth/users/${encodeURIComponent(user.email)}/role`, { role })
  await loadUsers()
}

async function loadRecipes() {
  recipesError.value = ''
  try { recipes.value = (await api.get<Recipe[]>('/recipes/')).data }
  catch { recipesError.value = 'Kunde inte läsa recept.' }
}
async function deleteRecipe(recipe: Recipe) {
  if (!confirm(`Ta bort "${recipe.title}"?`)) return
  await api.delete(`/recipes/${recipe.slug}`)
  await loadRecipes()
}
function openRecipesTab() {
  activeTab.value = 'recipes'
  if (!recipes.value.length) loadRecipes()
}

onMounted(loadUsers)
</script>

<template>
  <div class="admin-shell">
    <aside>
      <router-link to="/recipes" class="brand"><b>▦</b> Köksboken</router-link>
      <p>STUDIO / ADMIN</p>
      <a href="#" :class="{ active: activeTab === 'overview' }" @click.prevent="activeTab = 'overview'">▦ Översikt</a>
      <a href="#" :class="{ active: activeTab === 'recipes' }" @click.prevent="openRecipesTab">▤ Recept</a>
      <router-link to="/profile">♙ Min profil</router-link>
      <small>{{ displayName }}<br /><span>{{ userEmail }}</span></small>
      <button class="logout" type="button" @click="logout">Logga ut</button>
    </aside>
    <main>
      <header><div><p>ADMIN / {{ activeTab === 'overview' ? 'ÖVERSIKT' : 'RECEPT' }}</p><h1>Välkommen tillbaka, {{ displayName }}.</h1></div><router-link to="/recipes">Visa webbplatsen →</router-link></header>

      <template v-if="activeTab === 'overview'">
        <section class="metrics"><div><span>RECEPT</span><strong>{{ recipes.length || '–' }}</strong><small>Publicerade recept</small></div><div><span>ANVÄNDARE</span><strong>{{ users.length }}</strong><small>Registrerade konton</small></div><div><span>ADMINISTRATÖRER</span><strong>{{ users.filter(u => u.role === 'admin').length }}</strong><small>Med full behörighet</small></div><div><span>FAVORITER</span><strong>–</strong><small>Sparas per konto</small></div></section>
        <section class="dashboard-grid">
          <article class="panel wide">
            <div class="panel-head"><div><p>ANVÄNDARHANTERING</p><h2>Konton</h2></div><button @click="loadUsers">Uppdatera</button></div>
            <p v-if="error" class="error">{{ error }}</p>
            <div v-else class="users">
              <div v-for="user in users" :key="user.email"><span>{{ user.email }}</span><em :class="user.role">{{ user.role }}</em><button @click="changeRole(user)">Gör till {{ user.role === 'admin' ? 'användare' : 'admin' }}</button></div>
              <p v-if="!users.length">Inga användare hittades ännu.</p>
            </div>
          </article>
        </section>
      </template>

      <template v-else>
        <section class="dashboard-grid">
          <article class="panel wide">
            <div class="panel-head"><div><p>RECEPTHANTERING</p><h2>Alla recept</h2></div><button @click="loadRecipes">Uppdatera</button></div>
            <p v-if="recipesError" class="error">{{ recipesError }}</p>
            <div v-else class="users">
              <div v-for="recipe in recipes" :key="recipe.slug">
                <span>{{ recipe.title }} <em class="user">{{ recipe.createdBy || 'okänd' }}</em></span>
                <router-link :to="`/recipes/${recipe.slug}`" class="link-btn">Visa</router-link>
                <router-link :to="`/recipes/${recipe.slug}/edit`" class="link-btn">Redigera</router-link>
                <button @click="deleteRecipe(recipe)">Ta bort</button>
              </div>
              <p v-if="!recipes.length">Inga recept hittades ännu.</p>
            </div>
          </article>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
.admin-shell{min-height:100vh;display:grid;grid-template-columns:225px 1fr;background:#fcfbf9;color:#322923;font-family:Arial,sans-serif}.admin-shell aside{display:flex;flex-direction:column;padding:28px 18px;border-right:1px solid #eee6df;background:#fffdfa}.brand{color:#40332d;text-decoration:none;font:700 15px Georgia}.brand b{color:#c87554}.admin-shell aside p{margin:42px 10px 11px;color:#b6a8a0;font-size:9px;letter-spacing:.12em}.admin-shell aside>a{padding:10px 12px;border-radius:6px;color:#786a63;text-decoration:none;font-size:12px;cursor:pointer}.admin-shell aside .active{background:#fff0e9;color:#be6d50}.admin-shell aside small{margin-top:auto;color:#978981;font-size:10px;line-height:1.5}main{padding:36px 5%;max-width:1200px}header{display:flex;justify-content:space-between;align-items:start}header p,.panel p{margin:0 0 5px;color:#bc7153;font-size:9px;letter-spacing:.1em}h1{margin:0;font:700 27px Georgia}h2{margin:0;font:700 15px Georgia}header a{border:1px solid #e6d8d0;border-radius:5px;padding:9px 11px;color:#805c4d;font-size:11px;text-decoration:none}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:28px 0}.metrics div,.panel{border:1px solid #eee6df;border-radius:8px;background:#fff;padding:17px}.metrics span{display:block;color:#aa9b93;font-size:9px}.metrics strong{display:block;margin:10px 0 4px;font-size:27px}.metrics small{color:#aa9b93;font-size:10px}.dashboard-grid{display:grid;grid-template-columns:1fr;gap:14px}.panel.wide{min-height:180px}.panel-head{display:flex;justify-content:space-between}.panel-head>span,.panel button{border:1px solid #e9ddd5;border-radius:4px;background:white;padding:5px;color:#88786f;font-size:10px;cursor:pointer}.users{margin-top:14px}.users>div{display:flex;align-items:center;gap:12px;padding:9px 0;border-top:1px solid #f1e9e3;font-size:11px}.users>div span{flex:1}.users em{border-radius:999px;padding:4px 7px;font-style:normal;font-size:9px;margin-left:6px}.users em.admin{background:#fff0e9;color:#b96545}.users em.user{background:#f2efeb;color:#786a63}.link-btn{border:1px solid #e9ddd5;border-radius:4px;background:white;padding:5px;color:#88786f;font-size:10px;text-decoration:none}.error{color:#b64535}@media(max-width:760px){.admin-shell{grid-template-columns:1fr}.admin-shell aside{display:none}.metrics{grid-template-columns:repeat(2,1fr)}main{padding:25px 5%}}
.logout{margin-top:12px;border:1px solid #eaded6;border-radius:6px;background:#fff;padding:8px;color:#786a63;font-size:11px;cursor:pointer;text-align:left}.logout:hover{border-color:#d49a83;color:#b86648}
</style>