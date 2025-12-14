import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/api'

interface User {
  id: number
  email: string
  name: string
  currency: string
  preferredLanguage?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!user.value && !!token.value)

  function setUser(newUser: User | null) {
    user.value = newUser
  }

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('auth_token', newToken)
    } else {
      localStorage.removeItem('auth_token')
    }
  }

  function setRefreshToken(newRefreshToken: string | null) {
    refreshToken.value = newRefreshToken
    if (newRefreshToken) {
      localStorage.setItem('refresh_token', newRefreshToken)
    } else {
      localStorage.removeItem('refresh_token')
    }
  }

  async function checkAuth() {
    const storedToken = localStorage.getItem('auth_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    if (storedToken) {
      token.value = storedToken
      refreshToken.value = storedRefreshToken
      try {
        const userData = await apiClient.getMe()
        user.value = userData
      } catch (error) {
        // Token is invalid, clear it
        logout()
      }
    }
  }

  async function login(email: string, password: string) {
    try {
      isLoading.value = true
      const response = await apiClient.login(email, password)

      if (response.access_token) {
        setToken(response.access_token)
        setRefreshToken(response.refresh_token)
        user.value = response.user
        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function register(email: string, password: string, name: string, currency: string = 'INR') {
    try {
      isLoading.value = true
      const response = await apiClient.register(email, password, name, currency)

      if (response.access_token) {
        setToken(response.access_token)
        setRefreshToken(response.refresh_token)
        user.value = response.user
        return true
      }
      return false
    } catch (error) {
      console.error('Register error:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function sendMagicLink(email: string) {
    try {
      isLoading.value = true
      await apiClient.sendMagicLink(email)
      return true
    } catch (error) {
      console.error('Magic link error:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
  }

  async function updateUser(data: Partial<User>) {
    try {
      isLoading.value = true
      const updatedUser = await apiClient.updateUser(data)
      user.value = updatedUser
      return updatedUser
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    token,
    refreshToken,
    isLoading,
    isAuthenticated,
    setUser,
    setToken,
    setRefreshToken,
    checkAuth,
    login,
    register,
    sendMagicLink,
    logout,
    updateUser
  }
})

