import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/view/LoginView.vue'
import RegisterView from '@/view/RegisterView.vue'
import RecipesView from '@/view/RecipesView.vue'
import RecipeDetailView from '@/view/RecipeDetailView.vue'
import RecipeEditorView from '@/view/RecipeEditorView.vue'
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
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/recipes/new',
      name: 'recipe-new',
      component: RecipeEditorView,
      meta: { requiresAuth: true }
    },
    {
      path: '/recipes/:slug/edit',
      name: 'recipe-edit',
      component: RecipeEditorView,
      meta: { requiresAuth: true }
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
  const isLoggedIn = !!localStorage.getItem('token')
  if (to.meta.requiresAuth && !isLoggedIn) return '/login'
  if (to.meta.requiresAdmin && localStorage.getItem('userRole') !== 'admin') return '/recipes'
})

export default router