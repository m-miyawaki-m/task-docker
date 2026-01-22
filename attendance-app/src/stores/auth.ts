import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { storage } from '@/services/storage'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<User | null>(null)

  const isLoggedIn = computed(() => currentUser.value !== null)

  function init() {
    storage.init()
    currentUser.value = storage.getCurrentUser()
  }

  function login(email: string, password: string): boolean {
    const users = storage.getUsers()
    const user = users.find((u) => u.email === email && u.password === password)

    if (user) {
      currentUser.value = user
      storage.setCurrentUser(user)
      return true
    }
    return false
  }

  function logout() {
    currentUser.value = null
    storage.setCurrentUser(null)
  }

  return { currentUser, isLoggedIn, init, login, logout }
})
