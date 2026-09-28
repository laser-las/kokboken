import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8001/api',
})

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface Recipe {
  slug: string
  title: string
  category: string
  time: string
  image: string
  description: string
  ingredients: string[]
  steps: string[]
  createdBy: string
  authorName: string
  isPublic: boolean
}

export const avatarUrl = (email: string) =>
  `http://localhost:8001/api/auth/avatar/${encodeURIComponent(email)}`

// Utgången/ogiltig inloggning -> rensa sessionen och skicka till login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url: string = error.config?.url || ''
    if (error.response?.status === 401 && sessionStorage.getItem('token') && !url.includes('/auth/login')) {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('userEmail')
      sessionStorage.removeItem('userRole')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
