import { computed, ref } from 'vue'

function currentKey() {
  const email = localStorage.getItem('userEmail') || 'guest'
  return `favoriteRecipes:${email}`
}

function load(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = localStorage.getItem(currentKey())
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

const favoriteSlugs = ref<string[]>(load())

// Anropas efter inloggning/utloggning så listan byts till rätt användares favoriter
export function refreshFavorites() {
  favoriteSlugs.value = load()
}

export function useFavorites() {
  const isFavorite = (slug: string) => favoriteSlugs.value.includes(slug)
  const toggleFavorite = (slug: string) => {
    favoriteSlugs.value = isFavorite(slug)
      ? favoriteSlugs.value.filter((item) => item !== slug)
      : [...favoriteSlugs.value, slug]
    localStorage.setItem(currentKey(), JSON.stringify(favoriteSlugs.value))
  }
  return {
    favoriteSlugs: computed(() => favoriteSlugs.value),
    isFavorite,
    toggleFavorite,
  }
}