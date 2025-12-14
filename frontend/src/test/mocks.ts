import { vi } from 'vitest'
import type { AxiosResponse } from 'axios'

export function createMockApiClient() {
  return {
    // Auth
    login: vi.fn(),
    register: vi.fn(),
    sendMagicLink: vi.fn(),
    verifyMagicLink: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn(),

    // User
    getMe: vi.fn(),
    updateUser: vi.fn(),
    getFriends: vi.fn(),
    getUserDetails: vi.fn(),
    hideFriend: vi.fn(),
    inviteFriend: vi.fn(),
    submitFeedback: vi.fn(),
    exportData: vi.fn(),

    // Expense
    getBalances: vi.fn(),
    getExpenses: vi.fn(),
    getExpenseDetails: vi.fn(),
    createExpense: vi.fn(),
    updateExpense: vi.fn(),
    deleteExpense: vi.fn(),
    getRecurringExpenses: vi.fn(),
    getUploadUrl: vi.fn(),
    getCurrencyRate: vi.fn(),
    createCurrencyConversion: vi.fn(),
    getExpensesWithFriend: vi.fn(),
    getGroupExpenses: vi.fn(),

    // Group
    getGroups: vi.fn(),
    getGroupsWithBalances: vi.fn(),
    getGroupDetails: vi.fn(),
    createGroup: vi.fn(),
    updateGroup: vi.fn(),
    deleteGroup: vi.fn(),
    addGroupMembers: vi.fn(),
    removeGroupMember: vi.fn(),
    joinGroup: vi.fn(),
    leaveGroup: vi.fn(),
    simplifyDebts: vi.fn(),
    archiveGroup: vi.fn(),
    recalculateBalances: vi.fn(),

    // Bank
    getBankInstitutions: vi.fn(),
    connectBank: vi.fn(),
    exchangeBankToken: vi.fn(),
    getBankTransactions: vi.fn(),
    importBankTransaction: vi.fn()
  }
}

export function mockApiResponse<T>(data: T): Promise<T> {
  return Promise.resolve(data)
}

export function mockApiError(status: number, message: string) {
  return Promise.reject({
    response: {
      status,
      data: { detail: message }
    }
  })
}

// Test data factories
export const mockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  currency: 'USD',
  preferredLanguage: 'en',
  ...overrides
})

export const mockExpense = (overrides = {}) => ({
  id: '1',
  name: 'Test Expense',
  amount: 5000, // $50.00 in cents
  currency: 'USD',
  category: 'food',
  date: new Date().toISOString(),
  paidBy: { id: 1, name: 'Test User' },
  groupId: null,
  groupName: null,
  participants: [
    { userId: 1, userName: 'Test User', amount: 2500 },
    { userId: 2, userName: 'Friend', amount: 2500 }
  ],
  ...overrides
})

export const mockGroup = (overrides = {}) => ({
  id: 1,
  name: 'Test Group',
  publicId: 'abc123',
  defaultCurrency: 'USD',
  simplifyDebts: false,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  members: [
    { id: 1, name: 'Test User', email: 'test@example.com' },
    { id: 2, name: 'Friend', email: 'friend@example.com' }
  ],
  balances: [],
  ...overrides
})

export const mockFriend = (overrides = {}) => ({
  user: mockUser({ id: 2, name: 'Friend', email: 'friend@example.com' }),
  totalBalance: 2500,
  balances: [{ currency: 'USD', amount: 2500 }],
  ...overrides
})

export const mockBalance = (overrides = {}) => ({
  youOwe: [{ currency: 'USD', amount: 0 }],
  youGet: [{ currency: 'USD', amount: 2500 }],
  balances: [mockFriend()],
  ...overrides
})

