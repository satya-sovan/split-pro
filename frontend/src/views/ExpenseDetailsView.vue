<template>
  <MainLayout :title="expense?.name || 'Expense Details'" :loading="expenseStore.loading">
    <div class="p-6 max-w-2xl mx-auto" v-if="expense">
      <div class="space-y-6">
        <!-- Expense Info -->
        <div class="p-6 bg-card rounded-lg border">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3">
              <span class="text-3xl">{{ getCategoryIcon(expense.category) }}</span>
              <div>
                <h2 class="text-2xl font-bold">{{ expense.name }}</h2>
                <p class="text-muted-foreground">{{ formatExpenseDate(expense) }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-2xl font-bold">{{ formatCurrency(expense.amount, expense.currency) }}</p>
            </div>
          </div>

          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Paid by</span>
              <span class="font-medium">{{ getPaidByName(expense) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Category</span>
              <span class="font-medium">{{ getCategoryLabel(expense.category) }}</span>
            </div>
            <div v-if="expense.groupName || expense.group_id" class="flex justify-between">
              <span class="text-muted-foreground">Group</span>
              <span class="font-medium">{{ expense.groupName || 'Group' }}</span>
            </div>
          </div>
        </div>

        <!-- Participants -->
        <div class="p-6 bg-card rounded-lg border">
          <h3 class="font-semibold mb-4">Split Details</h3>
          <div class="space-y-3">
            <div
              v-for="participant in getParticipants(expense)"
              :key="participant.user_id || participant.userId"
              class="flex justify-between items-center"
            >
              <span>{{ participant.displayName }}</span>
              <span class="font-medium">
                {{ formatCurrency(participant.amount, expense.currency) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3">
          <button
            @click="router.back()"
            class="flex-1 px-4 py-2 border rounded-md hover:bg-accent"
          >
            Back
          </button>
          <button
            @click="handleDelete"
            class="px-4 py-2 bg-destructive text-white rounded-md hover:bg-destructive/90"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import MainLayout from '@/components/Layout/MainLayout.vue'
import { useExpenseStore } from '@/stores/expense'
import { formatCurrency } from '@/utils/numbers'
import { getCategoryIcon, getCategoryLabel } from '@/lib/category'
import { format, isValid, parseISO } from 'date-fns'

const route = useRoute()
const router = useRouter()
const expenseStore = useExpenseStore()

const expenseId = computed(() => route.params.id as string)
const expense = computed(() => expenseStore.currentExpense)

onMounted(() => {
  expenseStore.fetchExpenseDetails(expenseId.value)
})

// Handle both API formats: expense_date and date
function formatExpenseDate(expense: any): string {
  const dateStr = expense.expense_date || expense.date
  if (!dateStr) return 'Unknown date'

  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : new Date(dateStr)
    if (!isValid(date)) return 'Unknown date'
    return format(date, 'MMMM d, yyyy')
  } catch {
    return 'Unknown date'
  }
}

// Handle both API formats for paid_by
function getPaidByName(expense: any): string {
  if (expense.paid_by_name) return expense.paid_by_name
  if (expense.paidBy?.name) return expense.paidBy.name
  if (expense.paid_by_user?.name) return expense.paid_by_user.name
  return 'Unknown'
}

// Handle both API formats for participants
function getParticipants(expense: any): any[] {
  return (expense.participants || []).map((p: any) => ({
    ...p,
    // Support both user_name and userName
    displayName: p.user_name || p.userName || 'Unknown'
  }))
}

async function handleDelete() {
  if (!confirm('Are you sure you want to delete this expense?')) return

  try {
    await expenseStore.deleteExpense(expenseId.value)
    toast.success('Expense deleted')
    router.push('/expenses')
  } catch (error) {
    toast.error('Failed to delete expense')
  }
}
</script>

