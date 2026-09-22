import { computed, ref } from 'vue'

const storageKey = 'favoriteRecipes'
const stored = typeof window === 'undefined' ? [] : JSON.parse(localStorage.getItem(storageKey) || '[]')
const favoriteSlugs = ref<string[]>(Array.isArray(stored) ? stored : [])

export function useFavorites() {
  const isFavorite = (slug: string) => favoriteSlugs.value.includes(slug)
  const toggleFavorite = (slug: string) => {
    favoriteSlugs.value = isFavorite(slug) ? favoriteSlugs.value.filter((item) => item !== slug) : [...favoriteSlugs.value, slug]
    localStorage.setItem(storageKey, JSON.stringify(favoriteSlugs.value))
  }
  return { favoriteSlugs: computed(() => favoriteSlugs.value), isFavorite, toggleFavorite }
}
