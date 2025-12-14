<template>
  <MainLayout :title="friend?.user?.name || 'Friend'" :loading="loading">
    <div class="p-6 max-w-2xl mx-auto" v-if="friend">
      <!-- Friend Info -->
      <div class="p-6 bg-card rounded-lg border mb-6">
        <div class="flex items-center gap-4">
          <Avatar :name="friend.user.name" :src="friend.user.image" size="xl" />
          <div class="flex-1">
            <h2 class="text-2xl font-bold">{{ friend.user.name }}</h2>
            <p class="text-muted-foreground">{{ friend.user.email }}</p>
          </div>
        </div>

        <!-- Balance Summary -->
        <div class="mt-6 pt-6 border-t">
          <h3 class="text-sm font-medium text-muted-foreground mb-3">Balance</h3>
          <div class="space-y-2">
            <div
              v-for="balance in friend.balances"
              :key="balance.currency"
              :class="[
                'text-lg font-semibold',
                balance.amount > 0 ? 'text-green-600' : balance.amount < 0 ? 'text-red-600' : 'text-muted-foreground'
              ]"
            >
              <span v-if="balance.amount > 0">owes you </span>
              <span v-else-if="balance.amount < 0">you owe </span>
              {{ formatCurrency(Math.abs(balance.amount), balance.currency) }}
            </div>
            <div v-if="friend.balances.length === 0" class="text-muted-foreground">
              All settled up!
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <Button @click="showSettleUp = true" :disabled="friend.total_balance === 0">
          <CheckIcon class="h-4 w-4 mr-2" />
          Settle Up
        </Button>
        <Button variant="outline" @click="addExpense">
          <PlusIcon class="h-4 w-4 mr-2" />
          Add Expense
        </Button>
      </div>

      <!-- Expense History -->
      <div class="space-y-4">
        <h3 class="text-lg font-semibold">Expense History</h3>

        <div v-if="loadingExpenses" class="text-center py-8">
          <Spinner />
        </div>

        <div v-else-if="expenses.length === 0" class="text-center py-8 text-muted-foreground">
          No expenses with this friend yet
        </div>

        <div v-else class="space-y-3">
          <ExpenseCard
            v-for="expense in expenses"
            :key="expense.id"
            :expense="transformExpense(expense)"
            @click="viewExpense(expense.id)"
          />
        </div>
      </div>
    </div>

    <!-- Settle Up Dialog -->
    <SettleUpDialog
      v-model:open="showSettleUp"
      :friend="friend"
      @settled="handleSettled"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckIcon, PlusIcon } from 'lucide-vue-next'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Button from '@/components/ui/Button.vue'
import Avatar from '@/components/ui/Avatar.vue'
import Spinner from '@/components/ui/Spinner.vue'
import ExpenseCard from '@/components/Expense/ExpenseCard.vue'
import SettleUpDialog from '@/components/Friend/SettleUpDialog.vue'
import { apiClient } from '@/services/api'
import { formatCurrency } from '@/utils/numbers'
import type { Friend, ExpenseDetail, Expense } from '@/types'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const loadingExpenses = ref(true)
const friend = ref<Friend | null>(null)
const expenses = ref<ExpenseDetail[]>([])
const showSettleUp = ref(false)

const friendId = computed(() => parseInt(route.params.id as string))

onMounted(async () => {
  await loadFriend()
  await loadExpenses()
})

async function loadFriend() {
  loading.value = true
  try {
    const friends = await apiClient.getFriends()
    friend.value = friends.find(f => f.user.id === friendId.value) || null

    if (!friend.value) {
      // Try to get user details directly
      const user = await apiClient.getUserDetails(friendId.value)
      friend.value = {
        user,
        total_balance: 0,
        balances: []
      }
    }
  } catch (error) {
    console.error('Failed to load friend:', error)
  } finally {
    loading.value = false
  }
}

async function loadExpenses() {
  loadingExpenses.value = true
  try {
    expenses.value = await apiClient.getExpensesWithFriend(friendId.value)
  } catch (error) {
    console.error('Failed to load expenses:', error)
  } finally {
    loadingExpenses.value = false
  }
}

function transformExpense(expense: ExpenseDetail): Expense & { paidBy: any; participants: any[] } {
  return {
    ...expense,
    id: parseInt(expense.id),
    date: expense.expense_date,
    paidBy: { id: expense.paid_by, name: 'Unknown' },
    participants: expense.participants.map(p => ({
      userId: p.user_id,
      amount: p.amount
    }))
  }
}

function addExpense() {
  router.push(`/add?friend_id=${friendId.value}`)
}

function viewExpense(expenseId: string) {
  router.push(`/expenses/${expenseId}`)
}

async function handleSettled() {
  await loadFriend()
  await loadExpenses()
}
</script>

