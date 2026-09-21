import { createApp } from 'vue'
import App from './App.vue'
import router from './Router' // importerar från src/Router/index.ts

const app = createApp(App)

app.use(router)
app.mount('#app')