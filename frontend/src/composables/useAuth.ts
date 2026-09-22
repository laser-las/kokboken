import { useRouter } from 'vue-router'

export function useAuth() {
  const router = useRouter()
  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userRole')
    router.push('/login')
  }
  return { logout }
}
