import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'

// Types matching backend schemas
export interface User {
  id: number
  email: string | null
  name: string | null
  image: string | null
  currency: string
  preferred_language: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface ExpenseParticipant {
  user_id: number
  amount: number
}

export interface ExpenseCreate {
  expense_id?: string
  group_id?: number
  paid_by: number
  name: string
  category: string
  amount: number
  split_type: 'EQUAL' | 'PERCENTAGE' | 'SHARE' | 'EXACT' | 'ADJUSTMENT' | 'SETTLEMENT' | 'CURRENCY_CONVERSION'
  currency: string
  participants: ExpenseParticipant[]
  expense_date?: string
  file_key?: string
}

export interface Expense {
  id: string
  group_id: number | null
  paid_by: number
  name: string
  category: string
  amount: number
  split_type: string
  currency: string
  expense_date: string
  created_at: string
  updated_at: string
  file_key: string | null
  deleted_at: string | null
}

export interface ExpenseDetail extends Expense {
  participants: ExpenseParticipant[]
}

export interface Balance {
  user_id: number
  friend_id: number
  group_id: number | null
  currency: string
  amount: number
}

export interface Friend {
  user: User
  total_balance: number
  balances: Array<{ currency: string; amount: number }>
}

export interface Group {
  id: number
  public_id: string
  name: string
  user_id: number
  default_currency: string
  simplify_debts: boolean
  created_at: string
  updated_at: string
  archived_at: string | null
}

export interface GroupDetail extends Group {
  members: User[]
  recent_expenses: Expense[]
}

export interface GroupWithBalance {
  id: number
  name: string
  public_id: string
  default_currency: string
  balances: Record<string, number>
  archived_at: string | null
}

export interface BankInstitution {
  id: string
  name: string
  logo?: string
  country: string
}

export interface BankTransaction {
  id: string
  amount: number
  currency: string
  description: string
  date: string
  merchant_name?: string
  category?: string
}

// Splitwise Import Types (CSV-based import)
export interface SplitwiseImportStats {
  groups_imported: number
  friends_imported: number
  balances_imported: number
  expenses_imported: number
  rows_processed: number
  errors: string[]
}

export interface SplitwiseImportResult {
  success: boolean
  message?: string
  statistics: SplitwiseImportStats
}

export interface NotificationPreferences {
  email_expense_added: boolean
  email_expense_updated: boolean
  email_payment_received: boolean
  email_weekly_summary: boolean
  push_expense_added: boolean
  push_expense_updated: boolean
  push_payment_received: boolean
  push_reminders: boolean
}

export interface ExpenseNote {
  id: string
  note: string
  created_by_id: number
  created_by_name: string
  created_by_image: string | null
  created_at: string
  expense_id: string
}

class ApiClient {
  private client: AxiosInstance
  private isRefreshing = false
  private refreshSubscribers: ((token: string) => void)[] = []

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json'
      },
      withCredentials: true
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling with automatic token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as typeof error.config & { _retry?: boolean }

        // If 401 and not already retrying, attempt token refresh
        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Wait for the refresh to complete
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`
                }
                resolve(this.client(originalRequest))
              })
            })
          }

          originalRequest._retry = true
          this.isRefreshing = true

          try {
            const authStore = useAuthStore()
            const currentRefreshToken = authStore.refreshToken || localStorage.getItem('refresh_token')

            if (!currentRefreshToken) {
              throw new Error('No refresh token available')
            }

            const response = await this.client.post(`/auth/refresh?refresh_token=${encodeURIComponent(currentRefreshToken)}`)
            const { access_token, refresh_token } = response.data

            authStore.setToken(access_token)
            authStore.setRefreshToken(refresh_token)

            // Notify all subscribers
            this.refreshSubscribers.forEach(callback => callback(access_token))
            this.refreshSubscribers = []

            // Retry the original request
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`
            }
            return this.client(originalRequest)
          } catch (refreshError) {
            // Refresh failed, logout user
            const authStore = useAuthStore()
            authStore.logout()
            return Promise.reject(refreshError)
          } finally {
            this.isRefreshing = false
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // ==========================================
  // AUTH ENDPOINTS
  // ==========================================

  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await this.client.post('/auth/login', { email, password })
    return response.data
  }

  async register(email: string, password: string, name: string, currency: string = 'INR'): Promise<TokenResponse> {
    const response = await this.client.post('/auth/register', { email, password, name, currency })
    return response.data
  }

  async sendMagicLink(email: string): Promise<{ message: string }> {
    const response = await this.client.post('/auth/magic-link', { email })
    return response.data
  }

  async verifyMagicLink(token: string): Promise<TokenResponse> {
    const response = await this.client.post('/auth/magic-link/verify', { token })
    return response.data
  }

  async getGoogleAuthUrl(): Promise<{ auth_url: string; redirect_uri: string }> {
    const response = await this.client.get('/auth/google')
    return response.data
  }

  async googleCallback(code: string): Promise<TokenResponse> {
    const response = await this.client.get('/auth/google/callback', { params: { code } })
    return response.data
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout')
  }

  async refreshToken(): Promise<TokenResponse> {
    const response = await this.client.post('/auth/refresh')
    return response.data
  }

  // ==========================================
  // USER ENDPOINTS
  // ==========================================

  async getMe(): Promise<User> {
    const response = await this.client.get('/users/me')
    return response.data
  }

  async updateUser(data: Partial<User>): Promise<User> {
    const response = await this.client.put('/users/me', data)
    return response.data
  }

  async getFriends(): Promise<Friend[]> {
    const response = await this.client.get('/users/friends')
    return response.data
  }

  async searchUserByEmail(email: string): Promise<User> {
    const response = await this.client.get('/users/search/email', { params: { email } })
    return response.data
  }

  async getUserDetails(userId: number): Promise<User> {
    const response = await this.client.get(`/users/${userId}`)
    return response.data
  }

  async hideFriend(friendId: number): Promise<void> {
    await this.client.post(`/users/hide-friend/${friendId}`)
  }

  async unhideFriend(friendId: number): Promise<void> {
    await this.client.post(`/users/unhide-friend/${friendId}`)
  }

  async inviteFriend(email: string): Promise<void> {
    await this.client.post('/users/invite', { email })
  }

  async submitFeedback(message: string): Promise<void> {
    await this.client.post('/users/feedback', { message })
  }

  async exportData(): Promise<any> {
    const response = await this.client.get('/users/data/export')
    return response.data
  }

  async importFromSplitwise(file: File): Promise<SplitwiseImportResult> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await this.client.post('/users/import/splitwise', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  async getOwnExpenses(): Promise<Expense[]> {
    const response = await this.client.get('/users/expenses/own')
    return response.data
  }

  // ==========================================
  // PROFILE PICTURE
  // ==========================================

  async getProfilePictureUploadUrl(contentType: string): Promise<{ upload_url: string; key: string }> {
    const response = await this.client.post('/users/profile-picture/upload-url', { content_type: contentType })
    return response.data
  }

  async updateProfilePicture(key: string): Promise<User> {
    const response = await this.client.post('/users/profile-picture', { key })
    return response.data
  }

  async deleteProfilePicture(): Promise<User> {
    const response = await this.client.delete('/users/profile-picture')
    return response.data
  }

  async getProfilePictureUrl(): Promise<{ url: string }> {
    const response = await this.client.get('/users/profile-picture-url')
    return response.data
  }

  // ==========================================
  // PASSWORD MANAGEMENT
  // ==========================================

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.client.post('/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  }

  // ==========================================
  // NOTIFICATION PREFERENCES
  // ==========================================

  async getNotificationPreferences(): Promise<NotificationPreferences> {
    const response = await this.client.get('/users/notification-preferences')
    return response.data
  }

  async updateNotificationPreferences(preferences: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
    const response = await this.client.put('/users/notification-preferences', preferences)
    return response.data
  }

  // ==========================================
  // ACCOUNT DELETION
  // ==========================================

  async deleteAccount(confirmation: string, password?: string): Promise<void> {
    await this.client.delete('/users/account', {
      data: { confirmation, password }
    })
  }

  // ==========================================
  // EXPENSE NOTES
  // ==========================================

  async getExpenseNotes(expenseId: string): Promise<ExpenseNote[]> {
    const response = await this.client.get(`/expenses/${expenseId}/notes`)
    return response.data
  }

  async addExpenseNote(expenseId: string, note: string): Promise<ExpenseNote> {
    const response = await this.client.post(`/expenses/${expenseId}/notes`, null, {
      params: { note }
    })
    return response.data
  }

  async deleteExpenseNote(expenseId: string, noteId: string): Promise<void> {
    await this.client.delete(`/expenses/${expenseId}/notes/${noteId}`)
  }

  // ==========================================
  // EXPENSE ENDPOINTS
  // ==========================================

  async getBalances(currency?: string): Promise<Balance[]> {
    const response = await this.client.get('/expenses/balances/all', {
      params: currency ? { currency } : undefined
    })
    return response.data
  }

  async getExpenses(params?: { group_id?: number; include_deleted?: boolean }): Promise<Expense[]> {
    const response = await this.client.get('/expenses', { params })
    return response.data
  }

  async getExpenseDetails(expenseId: string): Promise<ExpenseDetail> {
    const response = await this.client.get(`/expenses/${expenseId}`)
    return response.data
  }

  async createExpense(data: ExpenseCreate): Promise<Expense> {
    const response = await this.client.post('/expenses', data)
    return response.data
  }

  async updateExpense(expenseId: string, data: ExpenseCreate): Promise<Expense> {
    const response = await this.client.put(`/expenses/${expenseId}`, data)
    return response.data
  }

  async deleteExpense(expenseId: string): Promise<void> {
    await this.client.delete(`/expenses/${expenseId}`)
  }

  async getRecurringExpenses(): Promise<any[]> {
    const response = await this.client.get('/expenses/recurring')
    return response.data
  }

  async getUploadUrl(fileName: string, fileType: string, fileSize: number): Promise<{ upload_url: string; key: string }> {
    const response = await this.client.post('/expenses/upload-url', null, {
      params: { file_name: fileName, file_type: fileType, file_size: fileSize }
    })
    return response.data
  }

  async getCurrencyRate(fromCurrency: string, toCurrency: string, date?: string): Promise<{ rate: number; from: string; to: string; date: string }> {
    const response = await this.client.get('/expenses/currency-rate', {
      params: { from_currency: fromCurrency, to_currency: toCurrency, date }
    })
    return response.data
  }

  async getBatchCurrencyRates(fromCurrencies: string[], toCurrency: string, date?: string): Promise<{ rates: Record<string, number>; to: string; date: string }> {
    const response = await this.client.post('/expenses/currency-rates/batch', null, {
      params: { from_currencies: fromCurrencies, to_currency: toCurrency, date }
    })
    return response.data
  }

  async createCurrencyConversion(fromExpense: ExpenseCreate, toExpense: ExpenseCreate): Promise<Expense> {
    const response = await this.client.post('/expenses/currency-conversion', {
      from_expense: fromExpense,
      to_expense: toExpense
    })
    return response.data
  }

  async getGroupExpenseDetails(groupId: number, includeDeleted?: boolean): Promise<ExpenseDetail[]> {
    const response = await this.client.get(`/expenses/group/${groupId}/details`, {
      params: includeDeleted ? { include_deleted: true } : undefined
    })
    return response.data
  }

  async getExpensesWithFriend(friendId: number, includeDeleted?: boolean): Promise<ExpenseDetail[]> {
    const response = await this.client.get(`/expenses/friend/${friendId}`, {
      params: includeDeleted ? { include_deleted: true } : undefined
    })
    return response.data
  }

  // ==========================================
  // GROUP ENDPOINTS
  // ==========================================

  async getGroups(includeArchived?: boolean): Promise<Group[]> {
    const response = await this.client.get('/groups', {
      params: includeArchived ? { include_archived: true } : undefined
    })
    return response.data
  }

  async getGroupsWithBalances(includeArchived?: boolean): Promise<GroupWithBalance[]> {
    const response = await this.client.get('/groups/with-balances', {
      params: includeArchived ? { include_archived: true } : undefined
    })
    return response.data
  }

  async getGroupDetails(groupId: number): Promise<GroupDetail> {
    const response = await this.client.get(`/groups/${groupId}`)
    return response.data
  }

  async createGroup(data: { name: string; default_currency?: string; simplify_debts?: boolean }): Promise<Group> {
    const response = await this.client.post('/groups', data)
    return response.data
  }

  async updateGroup(groupId: number, data: { name?: string; default_currency?: string; simplify_debts?: boolean }): Promise<Group> {
    const response = await this.client.put(`/groups/${groupId}`, data)
    return response.data
  }

  async joinGroup(publicId: string): Promise<Group> {
    const response = await this.client.post('/groups/join', { public_id: publicId })
    return response.data
  }

  async addGroupMember(groupId: number, userId: number): Promise<{ message: string }> {
    const response = await this.client.post(`/groups/${groupId}/members`, null, {
      params: { user_id: userId }
    })
    return response.data
  }

  async removeGroupMember(groupId: number, userId: number): Promise<void> {
    await this.client.delete(`/groups/${groupId}/members/${userId}`)
  }

  async leaveGroup(groupId: number): Promise<void> {
    await this.client.post(`/groups/${groupId}/leave`)
  }

  async deleteGroup(groupId: number): Promise<void> {
    await this.client.delete(`/groups/${groupId}`)
  }

  async archiveGroup(groupId: number): Promise<Group> {
    const response = await this.client.post(`/groups/${groupId}/archive`)
    return response.data
  }

  async simplifyGroupDebts(groupId: number): Promise<any> {
    const response = await this.client.post(`/groups/${groupId}/simplify`)
    return response.data
  }

  async recalculateGroupBalances(groupId: number): Promise<void> {
    await this.client.post(`/groups/${groupId}/recalculate`)
  }

  async getGroupTotals(groupId: number): Promise<Record<string, number>> {
    const response = await this.client.get(`/groups/${groupId}/totals`)
    return response.data
  }

  async getGroupBalances(groupId: number): Promise<any[]> {
    const response = await this.client.get(`/groups/${groupId}/balances`)
    return response.data
  }

  // ==========================================
  // BANK ENDPOINTS
  // ==========================================

  async getBankInstitutions(countryCode: string = 'US'): Promise<BankInstitution[]> {
    const response = await this.client.get('/bank/institutions', {
      params: { country_code: countryCode }
    })
    return response.data
  }

  async connectBank(institutionId?: string): Promise<{ link_token?: string; auth_link?: string; requisition_id?: string }> {
    const response = await this.client.post('/bank/connect', null, {
      params: institutionId ? { institution_id: institutionId } : undefined
    })
    return response.data
  }

  async exchangeBankToken(publicToken: string): Promise<{ access_token: string; item_id: string }> {
    const response = await this.client.post('/bank/token/exchange', { public_token: publicToken })
    return response.data
  }

  async getBankTransactions(params?: { start_date?: string; end_date?: string; account_id?: string; use_cache?: boolean }): Promise<BankTransaction[]> {
    const response = await this.client.get('/bank/transactions', { params })
    return response.data
  }

  async importBankTransaction(transactionId: string, category: string, participants?: number[]): Promise<void> {
    await this.client.post(`/bank/transactions/${transactionId}/import`, null, {
      params: { category, participants }
    })
  }

  // ==========================================
  // HEALTH ENDPOINTS
  // ==========================================

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health')
    return response.data
  }
}

export const apiClient = new ApiClient()

