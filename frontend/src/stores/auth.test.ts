import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { mockUser, mockApiResponse, mockApiError } from '@/test/mocks'

// Mock the API client
const mockLogin = vi.fn()
const mockRegister = vi.fn()
const mockGetMe = vi.fn()
const mockUpdateUser = vi.fn()
const mockSendMagicLink = vi.fn()

vi.mock('@/services/api', () => ({
  apiClient: {
    login: () => mockLogin(),
    register: () => mockRegister(),
    getMe: () => mockGetMe(),
    updateUser: (data: any) => mockUpdateUser(data),
    sendMagicLink: () => mockSendMagicLink()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have null user and token initially', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('login', () => {
    it('should login successfully and store token', async () => {
      const store = useAuthStore()
      const user = mockUser()

      mockLogin.mockResolvedValue({
        access_token: 'test-token',
        refresh_token: 'refresh-token',
        user
      })

      const result = await store.login('test@example.com', 'password123')

      expect(result).toBe(true)
      expect(store.token).toBe('test-token')
      expect(store.user).toEqual(user)
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'test-token')
    })

    it('should handle login failure', async () => {
      const store = useAuthStore()

      mockLogin.mockRejectedValue(new Error('Invalid credentials'))

      const result = await store.login('test@example.com', 'wrongpassword')

      expect(result).toBe(false)
      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('register', () => {
    it('should register successfully', async () => {
      const store = useAuthStore()
      const user = mockUser()

      mockRegister.mockResolvedValue({
        access_token: 'test-token',
        refresh_token: 'refresh-token',
        user
      })

      const result = await store.register('test@example.com', 'password123', 'Test User')

      expect(result).toBe(true)
      expect(store.token).toBe('test-token')
      expect(store.user).toEqual(user)
    })

    it('should handle registration failure', async () => {
      const store = useAuthStore()

      mockRegister.mockRejectedValue(new Error('Email already exists'))

      const result = await store.register('test@example.com', 'password123', 'Test User')

      expect(result).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear user and token on logout', async () => {
      const store = useAuthStore()

      // First login
      mockLogin.mockResolvedValue({
        access_token: 'test-token',
        user: mockUser()
      })
      await store.login('test@example.com', 'password123')

      expect(store.isAuthenticated).toBe(true)

      // Then logout
      store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
    })
  })

  describe('checkAuth', () => {
    it('should restore session from stored token', async () => {
      const store = useAuthStore()
      const user = mockUser()

      // Simulate stored token
      vi.mocked(localStorage.getItem).mockReturnValue('stored-token')
      mockGetMe.mockResolvedValue(user)

      await store.checkAuth()

      expect(store.token).toBe('stored-token')
      expect(store.user).toEqual(user)
      expect(store.isAuthenticated).toBe(true)
    })

    it('should logout if stored token is invalid', async () => {
      const store = useAuthStore()

      vi.mocked(localStorage.getItem).mockReturnValue('invalid-token')
      mockGetMe.mockRejectedValue(new Error('Unauthorized'))

      await store.checkAuth()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('updateUser', () => {
    it('should update user preferences', async () => {
      const store = useAuthStore()
      const user = mockUser()
      const updatedUser = { ...user, currency: 'EUR' }

      // Setup initial state
      store.user = user
      store.token = 'test-token'

      mockUpdateUser.mockResolvedValue(updatedUser)

      const result = await store.updateUser({ currency: 'EUR' })

      expect(result).toEqual(updatedUser)
      expect(store.user?.currency).toBe('EUR')
    })
  })

  describe('sendMagicLink', () => {
    it('should send magic link successfully', async () => {
      const store = useAuthStore()

      mockSendMagicLink.mockResolvedValue({ message: 'Magic link sent' })

      const result = await store.sendMagicLink('test@example.com')

      expect(result).toBe(true)
    })

    it('should handle magic link failure', async () => {
      const store = useAuthStore()

      mockSendMagicLink.mockRejectedValue(new Error('Failed to send'))

      const result = await store.sendMagicLink('test@example.com')

      expect(result).toBe(false)
    })
  })
})

