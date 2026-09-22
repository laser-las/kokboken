<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import AppLogo from '@/components/AppLogo.vue'

const route = useRoute()
const { logout } = useAuth()
const isAdmin = localStorage.getItem('userRole') === 'admin'

const recipe = computed(() => ({
  title: route.params.slug === 'kottbullar-med-potatismos'
    ? 'Köttbullar & potatismos med gräddsås och rårörda lingon'
    : 'Recept',
  category: 'NORRLÄNDSK MATKONST',
  description: 'En riktig svensk klassiker med saftiga köttbullar, krämig gräddsås, len potatismos och rårörda lingon.',
}))

const ingredients = ['500 g nötfärs', '1 st gul lök, finriven', '1 dl mjölk', '1 dl ströbröd', '1 ägg', '1 tsk salt', '1 krm svartpeppar, nymalen', '1 msk smör, till stekning', '8 st potatisar', '2 dl mjölk, uppvärmd', '50 g smör', '1 dl rårörda lingon']
const steps = [
  'Skala och koka potatisen mjuk i saltat vatten. Ställ åt sidan när den är klar och häll av vattnet.',
  'Riv löken och blanda den med mjölk, ströbröd, ägg, peppar och salt. Låt dra i cirka 5 minuter.',
  'Blanda ner färsen och rör ihop till en jämn smet. Rulla små köttbullar och stek dem gyllenbruna i smör.',
  'Sänk värmen, späd med grädde och smaka av. Låt såsen sjuda tills köttbullarna är genomstekta.',
  'Pressa potatisen och vispa den fluffig med varm mjölk och smör. Smaka av med salt och peppar.',
  'Servera köttbullarna med potatismos, gräddsås och rårörda lingon. Toppa gärna med färsk persilja.'
]
</script>

<template>
  <div class="page-container">
    <header class="navbar">
      <AppLogo />
      <nav><router-link to="/recipes">Alla recept</router-link><router-link to="/profile">Min profil</router-link><router-link v-if="isAdmin" to="/admin" class="admin-link">Adminpanel</router-link><button class="logout" type="button" @click="logout">Logga ut</button></nav>
    </header>

    <main>
      <router-link to="/recipes" class="back-link">← Tillbaka till alla recept</router-link>
      <p class="eyebrow">{{ recipe.category }}</p>
      <h1>{{ recipe.title }}</h1>
      <p class="description">{{ recipe.description }}</p>

      <div class="facts"><span>◷ Förberedelsetid: 25 min</span><span>◷ Tillagning: 35 min</span><span>♨ Portioner: 4 personer</span><span>♧ Svårighetsgrad: Lätt</span></div>

      <section class="content">
        <aside class="ingredients">
          <div class="section-heading"><h2>Ingredienser</h2><span>4 port</span></div>
          <ul><li v-for="ingredient in ingredients" :key="ingredient">{{ ingredient }}</li></ul>
        </aside>
        <section class="instructions">
          <h2>Gör så här</h2>
          <ol><li v-for="(step, index) in steps" :key="step"><span>{{ index + 1 }}</span><p>{{ step }}</p></li></ol>
          <div class="tip"><strong>KOCKENS TIPS</strong><p>Vill du ha en fylligare sås kan du tillsätta en skvätt soja eller lite fond. Servera gärna med pressgurka vid sidan om.</p></div>
        </section>
      </section>
    </main>
    <footer><span>Smaklig måltid!</span><small>Skapad med kärlek till den skandinaviska matkulturen.</small></footer>
  </div>
</template>

<style scoped>
.page-container { min-height: 100vh; background: #faf8f4; color: #382e2a; font-family: Georgia, 'Times New Roman', serif; }.navbar { height: 61px; padding: 0 8%; display: flex; align-items: center; justify-content: space-between; background: #fffdfa; border-bottom: 1px solid #eee6dd; }.logo { display: flex; gap: .4rem; align-items: center; color: #9d5138; font-size: 1rem; font-weight: bold; text-decoration: none; }.logo-mark { display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; background: #c86f4e; color: white; font-family: sans-serif; font-size: .75rem; }nav { display: flex; gap: 1.5rem; }nav a { color: #756862; font: .78rem Arial, sans-serif; text-decoration: none; }main { width: min(1040px, calc(100% - 3rem)); margin: 0 auto; padding: 2rem 0 4rem; }.back-link { display: inline-block; margin-bottom: 2rem; color: #b46649; font: .73rem Arial, sans-serif; text-decoration: none; }.eyebrow { margin: 0 0 .55rem; color: #bf775a; font: bold .6rem Arial, sans-serif; letter-spacing: .1em; }h1 { max-width: 900px; margin: 0; font-size: clamp(1.9rem, 4vw, 3rem); line-height: 1.1; }.description { max-width: 780px; color: #857a74; font: .85rem/1.6 Arial, sans-serif; }.facts { display: flex; flex-wrap: wrap; gap: .65rem; margin: 1.5rem 0 2rem; }.facts span { border: 1px solid #eaded5; border-radius: 4px; background: white; padding: .5rem .65rem; color: #7f7169; font: .67rem Arial, sans-serif; }.content { display: grid; grid-template-columns: 280px 1fr; gap: 2rem; align-items: start; }.ingredients, .instructions { background: white; border: 1px solid #eee5de; border-radius: 8px; padding: 1.25rem; }.section-heading { display: flex; align-items: center; justify-content: space-between; }.section-heading span { color: #c67859; font: .62rem Arial, sans-serif; }h2 { margin: 0; font-size: 1.1rem; }.ingredients ul { margin: 1rem 0 0; padding: 0; list-style: none; }.ingredients li { padding: .5rem 0; border-bottom: 1px solid #f0e8e2; color: #746862; font: .73rem Arial, sans-serif; }.ingredients li::before { content: '•'; color: #cf8060; margin-right: .5rem; }.instructions ol { margin: 1.2rem 0; padding: 0; list-style: none; }.instructions li { display: flex; gap: .8rem; padding: .55rem 0; }.instructions li > span { flex: 0 0 19px; width: 19px; height: 19px; border-radius: 50%; display: grid; place-items: center; background: #fcece5; color: #c77354; font: .62rem Arial, sans-serif; }.instructions p { margin: 0; color: #685d57; font: .74rem/1.55 Arial, sans-serif; }.tip { border-radius: 6px; background: #fbede7; padding: .9rem 1rem; }.tip strong { color: #bf7053; font: .62rem Arial, sans-serif; }.tip p { margin-top: .35rem; }footer { padding: 1.8rem; background: #f0e9e1; text-align: center; color: #453833; font-style: italic; font-weight: bold; }footer small { display: block; margin-top: .45rem; color: #93857d; font: .58rem Arial, sans-serif; }footer span::after { content: ''; display: block; width: 20px; height: 1px; margin: .6rem auto 0; background: #c87554; }@media (max-width: 680px) { .navbar { padding: 0 1.5rem; }.content { grid-template-columns: 1fr; }.facts { gap: .4rem; }main { width: min(100% - 2rem, 1040px); }nav { gap: .8rem; } }
.logout { border: 1px solid #e5d8cf; border-radius: 999px; background: transparent; padding: .35rem .65rem; color: #756862; font: .78rem Arial, sans-serif; cursor: pointer; }.logout:hover { color: #b86648; border-color: #d49a83; }
.admin-link { color: #b86648 !important; font-weight: 700; }
.navbar { height: 90px; padding-inline: clamp(2rem, 6vw, 8rem); }
</style>
