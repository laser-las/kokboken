import { useRouter } from 'vue-router'
import { refreshFavorites } from './useFavorites'

export function useAuth() {
  const router = useRouter()
  const logout = () => {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userEmail')
    sessionStorage.removeItem('userRole')
    refreshFavorites()
    router.push('/login')
  }
  return { logout }
}
