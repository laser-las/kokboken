import { computed, ref } from 'vue'
import { api } from '@/lib/api'

export interface Profile { email: string; role: string; name: string; avatar_url: string | null }
const empty: Profile = { email: '', role: '', name: '', avatar_url: null }
const stored = ref<Profile>({ ...empty })

// Delad profil för hela appen. Visas bara om den tillhör den som är inloggad
// i just den här fliken, så en annan användares profil kan aldrig "läcka".
export function useProfile() {
  const profile = computed(() =>
    stored.value.email && stored.value.email === (sessionStorage.getItem('userEmail') || '') ? stored.value : empty
  )
  async function loadProfile() {
    try {
      const { data } = await api.get<Profile>('/auth/me')
      setProfile(data)
    } catch { /* ej inloggad */ }
  }
  function setProfile(p: Profile) {
    stored.value = { ...p, avatar_url: p.avatar_url || null }
  }
  return { profile, loadProfile, setProfile }
}
