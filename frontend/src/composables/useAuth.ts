import { useRouter } from 'vue-router'
import { refreshFavorites } from './useFavorites'

export function useAuth() {
  const router = useRouter()
  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userRole')
    refreshFavorites()
    router.push('/login')
  }
  return { logout }
}