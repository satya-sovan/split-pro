import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBalanceStore } from '@/stores/balance'
import { mockBalance } from '@/test/mocks'

// Mock the API client
const mockGetBalances = vi.fn()

vi.mock('@/services/api', () => ({
  apiClient: {
    getBalances: () => mockGetBalances()
  }
}))

describe('Balance Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have null balances initially', () => {
      const store = useBalanceStore()
      expect(store.balances).toBeNull()
      expect(store.groupBalances).toEqual([])
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchBalances', () => {
    it('should fetch and store balances', async () => {
      const store = useBalanceStore()
      const balances = mockBalance()

      mockGetBalances.mockResolvedValue(balances)

      const result = await store.fetchBalances()

      expect(result).toEqual(balances)
      expect(store.balances).toEqual(balances)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch errors', async () => {
      const store = useBalanceStore()

      mockGetBalances.mockRejectedValue(new Error('Network error'))

      await expect(store.fetchBalances()).rejects.toThrow('Network error')
      expect(store.loading).toBe(false)
    })
  })

  describe('local mutations', () => {
    it('should set balances', () => {
      const store = useBalanceStore()
      const balances = mockBalance()

      store.setBalances(balances)

      expect(store.balances).toEqual(balances)
    })

    it('should set group balances', () => {
      const store = useBalanceStore()
      const groupBalances = [
        { groupId: 1, groupName: 'Test', balances: [], totalOwed: 0, totalOwing: 0 }
      ]

      store.setGroupBalances(groupBalances)

      expect(store.groupBalances).toEqual(groupBalances)
    })
  })
})

