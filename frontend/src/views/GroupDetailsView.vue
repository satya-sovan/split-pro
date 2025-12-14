<template>
  <MainLayout :title="group?.name || 'Group'" :loading="loading">
    <div class="p-6" v-if="group">
      <!-- Group Header -->
      <div class="p-6 bg-card rounded-lg border mb-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold">{{ group.name }}</h2>
            <p class="text-muted-foreground text-sm">
              {{ group.members?.length || 0 }} members · {{ group.default_currency }}
            </p>
          </div>
          <Button variant="outline" size="icon" @click="showSettings = true">
            <SettingsIcon class="h-4 w-4" />
          </Button>
        </div>

        <!-- Share Link -->
        <div class="flex items-center gap-2 p-2 bg-muted rounded">
          <Input
            :model-value="shareLink"
            readonly
            class="flex-1 text-sm"
          />
          <Button variant="outline" size="sm" @click="copyShareLink">
            <CopyIcon class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <!-- Balance Summary -->
      <div v-if="hasBalances" class="p-4 bg-card rounded-lg border mb-6">
        <h3 class="font-medium mb-3">Your Balance</h3>
        <div class="space-y-1">
          <div
            v-for="(amount, currency) in groupBalances"
            :key="currency"
            :class="[
              'text-lg font-semibold',
              amount > 0 ? 'text-green-600' : amount < 0 ? 'text-red-600' : 'text-muted-foreground'
            ]"
          >
            {{ formatBalance(amount, currency as string) }}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <Button @click="addExpense">
          <PlusIcon class="h-4 w-4 mr-2" />
          Add Expense
        </Button>
        <Button variant="outline" @click="showSettleUp = true">
          <CheckIcon class="h-4 w-4 mr-2" />
          Settle Up
        </Button>
      </div>

      <!-- Tabs -->
      <div class="flex gap-4 border-b mb-4">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'pb-2 text-sm font-medium border-b-2 -mb-px transition-colors',
            activeTab === tab.value
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Expenses Tab -->
      <div v-if="activeTab === 'expenses'" class="space-y-3">
        <div v-if="loadingExpenses" class="text-center py-8">
          <Spinner />
        </div>
        <div v-else-if="expenses.length === 0" class="text-center py-8 text-muted-foreground">
          No expenses in this group yet
        </div>
        <ExpenseCard
          v-for="expense in expenses"
          :key="expense.id"
          :expense="transformExpense(expense)"
          @click="viewExpense(expense.id)"
        />
      </div>

      <!-- Members Tab -->
      <div v-if="activeTab === 'members'">
        <MemberList
          :members="group.members || []"
          :creator-id="group.user_id"
          :current-user-id="authStore.user?.id"
          :can-remove="isCreator"
          @remove="removeMember"
        />

        <Button variant="outline" class="w-full mt-4" @click="showAddMember = true">
          <PlusIcon class="h-4 w-4 mr-2" />
          Invite Member
        </Button>
      </div>

      <!-- Balances Tab -->
      <div v-if="activeTab === 'balances'" class="space-y-4">
        <div v-if="loadingBalances" class="text-center py-8">
          <Spinner />
        </div>
        <div v-else-if="memberBalances.length === 0" class="text-center py-8 text-muted-foreground">
          Everyone is settled up!
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="balance in memberBalances"
            :key="`${balance.from}-${balance.to}`"
            class="p-3 bg-accent/30 rounded-lg flex justify-between items-center"
          >
            <span class="text-sm">
              <span class="font-medium">{{ balance.fromName }}</span>
              owes
              <span class="font-medium">{{ balance.toName }}</span>
            </span>
            <span class="font-semibold">
              {{ formatCurrency(balance.amount, balance.currency) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Dialog -->
    <GroupSettingsDialog
      v-model:open="showSettings"
      :group="group"
      @updated="loadGroup"
      @deleted="handleDeleted"
    />

    <!-- Settle Up Dialog -->
    <GroupSettleUpDialog
      v-model:open="showSettleUp"
      :group="group"
      @settled="handleSettled"
    />

    <!-- Add Member Dialog -->
    <AddMemberDialog
      v-model:open="showAddMember"
      :group-id="groupId"
      @added="loadGroup"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { PlusIcon, CheckIcon, SettingsIcon, CopyIcon } from 'lucide-vue-next'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Spinner from '@/components/ui/Spinner.vue'
import ExpenseCard from '@/components/Expense/ExpenseCard.vue'
import MemberList from '@/components/Group/MemberList.vue'
import GroupSettingsDialog from './GroupSettingsDialog.vue'
import GroupSettleUpDialog from './GroupSettleUpDialog.vue'
import AddMemberDialog from './AddMemberDialog.vue'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatCurrency } from '@/utils/numbers'
import type { GroupDetail, ExpenseDetail, Expense } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const loadingExpenses = ref(true)
const loadingBalances = ref(false)
const group = ref<GroupDetail | null>(null)
const expenses = ref<ExpenseDetail[]>([])
const groupBalances = ref<Record<string, number>>({})
const memberBalances = ref<Array<{ from: number; to: number; fromName: string; toName: string; amount: number; currency: string }>>([])
const activeTab = ref('expenses')
const showSettings = ref(false)
const showSettleUp = ref(false)
const showAddMember = ref(false)

const tabs = [
  { value: 'expenses', label: 'Expenses' },
  { value: 'members', label: 'Members' },
  { value: 'balances', label: 'Balances' }
]

const groupId = computed(() => parseInt(route.params.id as string))
const isCreator = computed(() => group.value?.user_id === authStore.user?.id)
const hasBalances = computed(() => Object.keys(groupBalances.value).length > 0)

const shareLink = computed(() => {
  if (!group.value) return ''
  return `${window.location.origin}/groups/join/${group.value.public_id}`
})

onMounted(async () => {
  await loadGroup()
  await loadExpenses()
})

async function loadGroup() {
  loading.value = true
  try {
    group.value = await apiClient.getGroupDetails(groupId.value)

    // Load balances
    const groupsWithBalances = await apiClient.getGroupsWithBalances()
    const currentGroup = groupsWithBalances.find(g => g.id === groupId.value)
    if (currentGroup) {
      groupBalances.value = currentGroup.balances || {}
    }
  } catch (error) {
    toast.error('Failed to load group')
    router.push('/groups')
  } finally {
    loading.value = false
  }
}

async function loadExpenses() {
  loadingExpenses.value = true
  try {
    expenses.value = await apiClient.getGroupExpenseDetails(groupId.value)
  } catch (error) {
    console.error('Failed to load expenses:', error)
  } finally {
    loadingExpenses.value = false
  }
}

function transformExpense(expense: ExpenseDetail): Expense & { paidBy: any; participants: any[] } {
  const payer = group.value?.members?.find(m => m.id === expense.paid_by)
  return {
    ...expense,
    id: parseInt(expense.id),
    date: expense.expense_date,
    groupName: group.value?.name,
    paidBy: { id: expense.paid_by, name: payer?.name || 'Unknown' },
    participants: expense.participants.map(p => ({
      userId: p.user_id,
      amount: p.amount
    }))
  }
}

function formatBalance(amount: number, currency: string): string {
  const formatted = formatCurrency(Math.abs(amount), currency)
  if (amount > 0) return `you are owed ${formatted}`
  if (amount < 0) return `you owe ${formatted}`
  return 'settled up'
}

function addExpense() {
  router.push(`/add?group_id=${groupId.value}`)
}

function viewExpense(expenseId: string) {
  router.push(`/expenses/${expenseId}`)
}

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareLink.value)
    toast.success('Link copied to clipboard')
  } catch {
    toast.error('Failed to copy link')
  }
}

async function removeMember(userId: number) {
  if (!confirm('Are you sure you want to remove this member?')) return

  try {
    await apiClient.removeGroupMember(groupId.value, userId)
    toast.success('Member removed')
    await loadGroup()
  } catch (error) {
    toast.error('Failed to remove member')
  }
}

function handleDeleted() {
  router.push('/groups')
}

async function handleSettled() {
  await loadGroup()
  await loadExpenses()
}
</script>

