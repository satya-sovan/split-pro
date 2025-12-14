<template>
  <div
    class="p-4 bg-card rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-start justify-between mb-2">
      <div class="flex items-center gap-2">
        <span class="text-2xl">{{ getCategoryIcon(expense.category) }}</span>
        <div>
          <p class="font-medium">{{ expense.name }}</p>
          <p class="text-sm text-muted-foreground">
            {{ formatExpenseDate(expense) }}
          </p>
        </div>
      </div>
      <div class="text-right">
        <p class="font-semibold">{{ formatCurrency(expense.amount, expense.currency) }}</p>
        <p class="text-xs text-muted-foreground">{{ getPaidByName(expense) }}</p>
      </div>
    </div>

    <div v-if="expense.groupName" class="flex items-center gap-1 text-xs text-muted-foreground">
      <UserGroupIcon class="h-3 w-3" />
      <span>{{ expense.groupName }}</span>
    </div>

    <div class="mt-2 text-xs text-muted-foreground">
      {{ getParticipantCount(expense) }} participant{{ getParticipantCount(expense) !== 1 ? 's' : '' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { UserGroupIcon } from '@heroicons/vue/24/outline'
import { formatCurrency } from '@/utils/numbers'
import { getCategoryIcon } from '@/lib/category'
import { format, isValid, parseISO } from 'date-fns'

defineProps<{
  expense: any
}>()

defineEmits<{
  click: []
}>()

function formatExpenseDate(expense: any): string {
  const dateStr = expense.expense_date || expense.date
  if (!dateStr) return ''

  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : new Date(dateStr)
    if (!isValid(date)) return ''
    return format(date, 'MMM d, yyyy')
  } catch {
    return ''
  }
}

function getPaidByName(expense: any): string {
  if (expense.paid_by_name) return expense.paid_by_name
  if (expense.paidBy?.name) return expense.paidBy.name
  if (expense.paid_by_user?.name) return expense.paid_by_user.name
  return 'Unknown'
}

function getParticipantCount(expense: any): number {
  return (expense.participants || []).length
}
</script>

