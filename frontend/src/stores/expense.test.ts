import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useExpenseStore } from '@/stores/expense'
import { mockExpense } from '@/test/mocks'

// Mock the API client
const mockGetExpenses = vi.fn()
const mockGetExpenseDetails = vi.fn()
const mockCreateExpense = vi.fn()
const mockUpdateExpense = vi.fn()
const mockDeleteExpense = vi.fn()

vi.mock('@/services/api', () => ({
  apiClient: {
    getExpenses: () => mockGetExpenses(),
    getExpenseDetails: (id: string) => mockGetExpenseDetails(id),
    createExpense: (data: any) => mockCreateExpense(data),
    updateExpense: (id: string, data: any) => mockUpdateExpense(id, data),
    deleteExpense: (id: string) => mockDeleteExpense(id)
  }
}))

describe('Expense Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have empty expenses initially', () => {
      const store = useExpenseStore()
      expect(store.expenses).toEqual([])
      expect(store.currentExpense).toBeNull()
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchExpenses', () => {
    it('should fetch and store expenses', async () => {
      const store = useExpenseStore()
      const expenses = [mockExpense(), mockExpense({ id: '2', name: 'Another Expense' })]

      mockGetExpenses.mockResolvedValue(expenses)

      const result = await store.fetchExpenses()

      expect(result).toEqual(expenses)
      expect(store.expenses).toEqual(expenses)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch errors', async () => {
      const store = useExpenseStore()

      mockGetExpenses.mockRejectedValue(new Error('Network error'))

      await expect(store.fetchExpenses()).rejects.toThrow('Network error')
      expect(store.loading).toBe(false)
    })

    it('should filter by group_id', async () => {
      const store = useExpenseStore()
      const expenses = [mockExpense({ groupId: 1 })]

      mockGetExpenses.mockResolvedValue(expenses)

      await store.fetchExpenses({ group_id: '1' })

      expect(mockGetExpenses).toHaveBeenCalled()
    })
  })

  describe('fetchExpenseDetails', () => {
    it('should fetch expense details and set currentExpense', async () => {
      const store = useExpenseStore()
      const expense = mockExpense()

      mockGetExpenseDetails.mockResolvedValue(expense)

      const result = await store.fetchExpenseDetails('1')

      expect(result).toEqual(expense)
      expect(store.currentExpense).toEqual(expense)
    })
  })

  describe('createExpense', () => {
    it('should create expense and add to list', async () => {
      const store = useExpenseStore()
      const newExpense = mockExpense()

      mockCreateExpense.mockResolvedValue(newExpense)

      const result = await store.createExpense({
        name: 'Test Expense',
        amount: 5000,
        currency: 'USD',
        category: 'food',
        paid_by: 1,
        participants: [],
        split_type: 'EQUAL'
      })

      expect(result).toEqual(newExpense)
      expect(store.expenses).toContainEqual(newExpense)
    })
  })

  describe('updateExpense', () => {
    it('should update expense in store', async () => {
      const store = useExpenseStore()
      const originalExpense = mockExpense()
      const updatedExpense = { ...originalExpense, name: 'Updated Name' }

      store.expenses = [originalExpense]
      mockUpdateExpense.mockResolvedValue(updatedExpense)

      await store.updateExpense('1', { name: 'Updated Name' })

      expect(store.expenses[0].name).toBe('Updated Name')
    })
  })

  describe('deleteExpense', () => {
    it('should remove expense from store', async () => {
      const store = useExpenseStore()
      const expense = mockExpense()

      store.expenses = [expense]
      mockDeleteExpense.mockResolvedValue(undefined)

      await store.deleteExpense('1')

      expect(store.expenses).toEqual([])
    })
  })

  describe('local mutations', () => {
    it('should set expenses', () => {
      const store = useExpenseStore()
      const expenses = [mockExpense()]

      store.setExpenses(expenses)

      expect(store.expenses).toEqual(expenses)
    })

    it('should add expense to beginning of list', () => {
      const store = useExpenseStore()
      const existingExpense = mockExpense({ id: '1' })
      const newExpense = mockExpense({ id: '2' })

      store.expenses = [existingExpense]
      store.addExpense(newExpense)

      expect(store.expenses[0]).toEqual(newExpense)
      expect(store.expenses[1]).toEqual(existingExpense)
    })

    it('should update expense in list', () => {
      const store = useExpenseStore()
      const expense = mockExpense()

      store.expenses = [expense]
      store.updateExpenseInStore(1, { name: 'Updated' })

      expect(store.expenses[0].name).toBe('Updated')
    })

    it('should remove expense from list', () => {
      const store = useExpenseStore()
      const expense = mockExpense()

      store.expenses = [expense]
      store.removeExpense(1)

      expect(store.expenses).toEqual([])
    })
  })
})

