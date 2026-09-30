import { useRouter } from 'vue-router'
import { refreshFavorites } from './useFavorites'
import { api } from '@/lib/api'

export function useAuth() {
  const router = useRouter()
  const logout = async () => {
    const sessionId = sessionStorage.getItem('sessionId')
    if (sessionId) {
      try { await api.post('/auth/logout', { sessionId }) } catch { /* logout should still succeed locally */ }
    }
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userEmail')
    sessionStorage.removeItem('userRole')
    sessionStorage.removeItem('sessionId')
    refreshFavorites()
    router.push('/login')
  }
  return { logout }
}
