import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8001/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
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
}