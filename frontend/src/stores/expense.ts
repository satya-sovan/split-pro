import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/services/api'

export interface ExpenseParticipant {
  userId: number
  userName?: string
  amount: number
}

export interface ExpensePaidBy {
  id: number
  name: string
  email?: string
}

export interface Expense {
  id: number
  name: string
  description?: string
  amount: number
  currency: string
  paidBy: ExpensePaidBy
  category: string
  date: string
  groupId?: number
  groupName?: string
  participants: ExpenseParticipant[]
}

export const useExpenseStore = defineStore('expense', () => {
  const expenses = ref<Expense[]>([])
  const currentExpense = ref<Expense | null>(null)
  const loading = ref(false)

  function setExpenses(newExpenses: Expense[]) {
    expenses.value = newExpenses
  }

  function setCurrentExpense(expense: Expense | null) {
    currentExpense.value = expense
  }

  function addExpense(expense: Expense) {
    expenses.value.unshift(expense)
  }

  function updateExpenseInStore(id: number | string, updates: Partial<Expense>) {
    const strId = String(id)
    const index = expenses.value.findIndex(e => String(e.id) === strId)
    if (index !== -1) {
      expenses.value[index] = { ...expenses.value[index], ...updates }
    }
  }

  function removeExpense(id: number | string) {
    const strId = String(id)
    expenses.value = expenses.value.filter(e => String(e.id) !== strId)
  }

  async function fetchExpenses(params?: { group_id?: string; friend_id?: string }) {
    loading.value = true
    try {
      const data = await apiClient.getExpenses(params)
      expenses.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchExpenseDetails(expenseId: string) {
    loading.value = true
    try {
      const data = await apiClient.getExpenseDetails(expenseId)
      currentExpense.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function createExpense(expenseData: any) {
    loading.value = true
    try {
      const data = await apiClient.createExpense(expenseData)
      addExpense(data)
      return data
    } finally {
      loading.value = false
    }
  }

  async function updateExpense(expenseId: string, expenseData: any) {
    loading.value = true
    try {
      const data = await apiClient.updateExpense(expenseId, expenseData)
      updateExpenseInStore(parseInt(expenseId), data)
      return data
    } finally {
      loading.value = false
    }
  }

  async function deleteExpense(expenseId: string) {
    loading.value = true
    try {
      await apiClient.deleteExpense(expenseId)
      removeExpense(parseInt(expenseId))
    } finally {
      loading.value = false
    }
  }

  return {
    expenses,
    currentExpense,
    loading,
    setExpenses,
    setCurrentExpense,
    addExpense,
    updateExpenseInStore,
    removeExpense,
    fetchExpenses,
    fetchExpenseDetails,
    createExpense,
    updateExpense,
    deleteExpense
  }
})

