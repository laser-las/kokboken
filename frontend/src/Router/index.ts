import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/view/LoginView.vue'
import RegisterView from '@/view/RegisterView.vue'
import RecipesView from '@/view/RecipesView.vue'
import RecipeDetailView from '@/view/RecipeDetailView.vue'
import ProfileView from '@/view/ProfileView.vue'
import AdminView from '@/view/AdminView.vue'

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
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAdmin: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView
    },
    {
      path: '/recipes/:slug',
      name: 'recipe-detail',
      component: RecipeDetailView
    },
    {
      path: '/recipes',
      name: 'recipes',
      component: RecipesView
    },
    {
      path: '/',
      redirect: '/recipes'
    }
  ]
})

router.beforeEach((to) => {
  if (to.meta.requiresAdmin && localStorage.getItem('userRole') !== 'admin') return '/recipes'
})

export default router
