<template>
  <MainLayout title="All Expenses">
    <div class="p-6">
      <div v-if="expenseStore.loading" class="text-center py-8">
        <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
      </div>

      <div v-else-if="expenseStore.expenses.length === 0" class="text-center py-12 text-muted-foreground">
        <p class="text-lg mb-4">No expenses yet</p>
        <router-link to="/add" class="text-primary hover:underline">
          Add your first expense
        </router-link>
      </div>

      <div v-else class="space-y-3">
        <ExpenseCard
          v-for="expense in expenseStore.expenses"
          :key="expense.id"
          :expense="expense"
          @click="router.push(`/expenses/${expense.id}`)"
        />
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/components/Layout/MainLayout.vue'
import ExpenseCard from '@/components/Expense/ExpenseCard.vue'
import { useExpenseStore } from '@/stores/expense'

const router = useRouter()
const expenseStore = useExpenseStore()

onMounted(() => {
  expenseStore.fetchExpenses()
})
</script>

