import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/view/LoginView.vue'
import RegisterView from '@/view/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/',
      redirect: '/login'
    }
  ]
})

export default router