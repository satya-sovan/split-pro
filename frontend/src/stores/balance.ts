import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/services/api'

interface CurrencyAmount {
  currency: string
  amount: number
}

interface Friend {
  id: number
  name: string
  email: string
  image?: string
}

interface FriendBalance {
  friend: Friend
  currencies: CurrencyAmount[]
}

interface BalanceSummary {
  youOwe: CurrencyAmount[]
  youGet: CurrencyAmount[]
  balances: FriendBalance[]
}

interface GroupBalance {
  groupId: number
  groupName: string
  balances: CurrencyAmount[]
  totalOwed: number
  totalOwing: number
}

export const useBalanceStore = defineStore('balance', () => {
  const balances = ref<BalanceSummary | null>(null)
  const groupBalances = ref<GroupBalance[]>([])
  const loading = ref(false)

  function setBalances(newBalances: BalanceSummary) {
    balances.value = newBalances
  }

  function setGroupBalances(newGroupBalances: GroupBalance[]) {
    groupBalances.value = newGroupBalances
  }

  async function fetchBalances() {
    loading.value = true
    try {
      const data = await apiClient.getBalances()
      balances.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  return {
    balances,
    groupBalances,
    loading,
    setBalances,
    setGroupBalances,
    fetchBalances
  }
})

