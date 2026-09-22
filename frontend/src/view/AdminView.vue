<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useAuth } from '@/composables/useAuth'

type User = { email: string; role: 'user' | 'admin' }
const users = ref<User[]>([])
const error = ref('')
const { logout } = useAuth()
const userEmail = localStorage.getItem('userEmail') || 'administratör'
const displayName = (userEmail.split('@')[0] || 'administratör').replace(/[._-]/g, ' ')
const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` }

async function loadUsers() {
  try { users.value = (await axios.get('http://localhost:8001/api/auth/users', { headers })).data }
  catch { error.value = 'Kunde inte läsa användare. Kontrollera att du är administratör.' }
}
async function changeRole(user: User) {
  const role = user.role === 'admin' ? 'user' : 'admin'
  await axios.patch(`http://localhost:8001/api/auth/users/${encodeURIComponent(user.email)}/role`, { role }, { headers })
  await loadUsers()
}
onMounted(loadUsers)
</script>

<template>
  <div class="admin-shell">
    <aside><router-link to="/recipes" class="brand"><b>▦</b> Köksboken</router-link><p>STUDIO / ADMIN</p><router-link to="/admin" class="active">▦ Översikt</router-link><router-link to="/recipes">▤ Recept & Sidor</router-link><router-link to="/profile">♙ Användare</router-link><router-link to="/recipes">⌁ Trafikanalys</router-link><router-link to="/recipes">⚙ Inställningar</router-link><small>{{ displayName }}<br /><span>{{ userEmail }}</span></small><button class="logout" type="button" @click="logout">Logga ut</button></aside>
    <main><header><div><p>ADMIN / ÖVERSIKT</p><h1>Välkommen tillbaka, {{ displayName }}.</h1></div><router-link to="/recipes">Visa webbplatsen →</router-link></header>
      <section class="metrics"><div><span>RECEPT</span><strong>0</strong><small>Publicerade recept</small></div><div><span>ANVÄNDARE</span><strong>{{ users.length }}</strong><small>Registrerade konton</small></div><div><span>ADMINISTRATÖRER</span><strong>{{ users.filter(u => u.role === 'admin').length }}</strong><small>Med full behörighet</small></div><div><span>FAVORITER</span><strong>–</strong><small>Totalt sparade</small></div></section>
      <section class="dashboard-grid"><article class="panel wide"><div class="panel-head"><div><p>ÖVERSIKT</p><h2>Trendlinje</h2></div><span>Senaste 30 dagarna</span></div><div class="chart"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></article><article class="panel"><p>ADMIN</p><h2>Roller & behörigheter</h2><div class="legend"><span><b></b> Administratör</span><span><b></b> Användare</span></div></article><article class="panel wide"><div class="panel-head"><div><p>ANVÄNDARHANTERING</p><h2>Konton</h2></div><button @click="loadUsers">Uppdatera</button></div><p v-if="error" class="error">{{ error }}</p><div v-else class="users"><div v-for="user in users" :key="user.email"><span>{{ user.email }}</span><em :class="user.role">{{ user.role }}</em><button @click="changeRole(user)">Gör till {{ user.role === 'admin' ? 'användare' : 'admin' }}</button></div><p v-if="!users.length">Inga användare hittades ännu.</p></div></article></section>
    </main>
  </div>
</template>

<style scoped>
.admin-shell{min-height:100vh;display:grid;grid-template-columns:225px 1fr;background:#fcfbf9;color:#322923;font-family:Arial,sans-serif}.admin-shell aside{display:flex;flex-direction:column;padding:28px 18px;border-right:1px solid #eee6df;background:#fffdfa}.brand{color:#40332d;text-decoration:none;font:700 15px Georgia}.brand b{color:#c87554}.admin-shell aside p{margin:42px 10px 11px;color:#b6a8a0;font-size:9px;letter-spacing:.12em}.admin-shell aside>a:not(.brand){padding:10px 12px;border-radius:6px;color:#786a63;text-decoration:none;font-size:12px}.admin-shell aside .active{background:#fff0e9;color:#be6d50}.admin-shell aside small{margin-top:auto;color:#978981;font-size:10px;line-height:1.5}main{padding:36px 5%;max-width:1200px}header{display:flex;justify-content:space-between;align-items:start}header p,.panel p{margin:0 0 5px;color:#bc7153;font-size:9px;letter-spacing:.1em}h1{margin:0;font:700 27px Georgia}h2{margin:0;font:700 15px Georgia}header a{border:1px solid #e6d8d0;border-radius:5px;padding:9px 11px;color:#805c4d;font-size:11px;text-decoration:none}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:28px 0}.metrics div,.panel{border:1px solid #eee6df;border-radius:8px;background:#fff;padding:17px}.metrics span{display:block;color:#aa9b93;font-size:9px}.metrics strong{display:block;margin:10px 0 4px;font-size:27px}.metrics small{color:#aa9b93;font-size:10px}.dashboard-grid{display:grid;grid-template-columns:2fr 1fr;gap:14px}.panel.wide{min-height:180px}.panel-head{display:flex;justify-content:space-between}.panel-head>span,.panel button{border:1px solid #e9ddd5;border-radius:4px;background:white;padding:5px;color:#88786f;font-size:10px}.chart{height:110px;display:flex;align-items:end;gap:8px;margin-top:20px;border-bottom:1px solid #f1e9e3}.chart i{flex:1;background:#efc7b7;border-radius:3px 3px 0 0}.chart i:nth-child(1){height:22%}.chart i:nth-child(2){height:35%}.chart i:nth-child(3){height:28%}.chart i:nth-child(4){height:58%}.chart i:nth-child(5){height:42%}.chart i:nth-child(6){height:75%}.chart i:nth-child(7){height:65%}.legend{display:grid;gap:10px;margin-top:17px;color:#75665f;font-size:11px}.legend b{display:inline-block;width:8px;height:8px;border-radius:50%;background:#c87050}.legend span+span b{background:#dacbc2}.users{margin-top:14px}.users>div{display:flex;align-items:center;gap:12px;padding:9px 0;border-top:1px solid #f1e9e3;font-size:11px}.users>div span{flex:1}.users em{border-radius:999px;padding:4px 7px;font-style:normal;font-size:9px}.users em.admin{background:#fff0e9;color:#b96545}.users em.user{background:#f2efeb;color:#786a63}.error{color:#b64535}@media(max-width:760px){.admin-shell{grid-template-columns:1fr}.admin-shell aside{display:none}.metrics{grid-template-columns:repeat(2,1fr)}.dashboard-grid{grid-template-columns:1fr}main{padding:25px 5%}}
.logout{margin-top:12px;border:1px solid #eaded6;border-radius:6px;background:#fff;padding:8px;color:#786a63;font-size:11px;cursor:pointer;text-align:left}.logout:hover{border-color:#d49a83;color:#b86648}
</style>
