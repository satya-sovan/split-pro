<template>
  <MainLayout title="Home">
    <div class="p-6">
      <!-- Logo -->
      <div class="mb-6 flex justify-center">
        <svg width="300" height="80" viewBox="0 0 900 240" xmlns="http://www.w3.org/2000/svg">
          <!-- ICON -->
          <g transform="translate(40, 20)">
            <!-- Background Circle -->
            <circle cx="100" cy="100" r="100" fill="#1F7A7A"/>
            <!-- Left Person -->
            <circle cx="65" cy="100" r="18" fill="#FFFFFF"/>
            <!-- Right Person -->
            <circle cx="135" cy="100" r="18" fill="#FFFFFF"/>
            <!-- Split Line -->
            <rect x="94" y="55" width="12" height="90" rx="6" fill="#FFFFFF"/>
          </g>
          <!-- TEXT -->
          <text x="280" y="140" font-family="Inter, Poppins, Roboto, sans-serif" font-size="96" font-weight="600" fill="#0F172A">SAHA</text>
          <text x="560" y="140" font-family="Inter, Poppins, Roboto, sans-serif" font-size="96" font-weight="400" fill="#475569">Split</text>
        </svg>
      </div>

      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">Welcome, {{ authStore.user?.name }}!</h1>
        <p class="text-muted-foreground">Track and split expenses with friends and groups</p>
      </div>

      <div class="grid gap-4 md:grid-cols-3 mb-8">
        <router-link
          to="/add"
          class="p-6 bg-card rounded-lg border hover:shadow-lg transition-shadow"
        >
          <div class="flex items-center gap-3">
            <div class="p-3 bg-primary/10 rounded-full">
              <PlusIcon class="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 class="font-semibold">Add Expense</h3>
              <p class="text-sm text-muted-foreground">Split a new expense</p>
            </div>
          </div>
        </router-link>

        <router-link
          to="/balances"
          class="p-6 bg-card rounded-lg border hover:shadow-lg transition-shadow"
        >
          <div class="flex items-center gap-3">
            <div class="p-3 bg-primary/10 rounded-full">
              <UsersIcon class="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 class="font-semibold">Balances</h3>
              <p class="text-sm text-muted-foreground">View who owes what</p>
            </div>
          </div>
        </router-link>

        <router-link
          to="/groups"
          class="p-6 bg-card rounded-lg border hover:shadow-lg transition-shadow"
        >
          <div class="flex items-center gap-3">
            <div class="p-3 bg-primary/10 rounded-full">
              <UserGroupIcon class="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 class="font-semibold">Groups</h3>
              <p class="text-sm text-muted-foreground">Manage your groups</p>
            </div>
          </div>
        </router-link>
      </div>

      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold">Recent Expenses</h2>
        <router-link to="/expenses" class="text-sm text-primary hover:underline">
          View all
        </router-link>
      </div>

      <div v-if="expenseStore.loading" class="text-center py-8">
        <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
      </div>

      <div v-else-if="expenseStore.expenses.length === 0" class="text-center py-8 text-muted-foreground">
        No expenses yet. Add your first expense to get started!
      </div>

      <div v-else class="space-y-3">
        <ExpenseCard
          v-for="expense in recentExpenses"
          :key="expense.id"
          :expense="expense"
        />
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { PlusIcon, UsersIcon } from 'lucide-vue-next'
import { UserGroupIcon } from '@heroicons/vue/24/outline'
import MainLayout from '@/components/Layout/MainLayout.vue'
import ExpenseCard from '@/components/Expense/ExpenseCard.vue'
import { useAuthStore } from '@/stores/auth'
import { useExpenseStore } from '@/stores/expense'

const authStore = useAuthStore()
const expenseStore = useExpenseStore()

const recentExpenses = computed(() => expenseStore.expenses.slice(0, 10))

onMounted(() => {
  expenseStore.fetchExpenses()
})
</script>

