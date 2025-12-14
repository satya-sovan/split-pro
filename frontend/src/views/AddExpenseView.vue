<template>
  <MainLayout title="Add Expense">
    <div class="p-6 max-w-2xl mx-auto">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Description -->
        <div class="space-y-2">
          <label for="name" class="block text-sm font-medium">
            Description <span class="text-destructive">*</span>
          </label>
          <Input
            id="name"
            v-model="form.name"
            placeholder="What's this expense for?"
            required
          />
        </div>

        <!-- Amount and Currency -->
        <div class="grid grid-cols-3 gap-4">
          <div class="col-span-2">
            <CurrencyInput
              v-model="form.amount"
              :currency="form.currency"
              label="Amount"
              required
            />
          </div>
          <CurrencyPicker v-model="form.currency" label="Currency" />
        </div>

        <!-- Category -->
        <CategoryPicker v-model="form.category" label="Category" />

        <!-- Date -->
        <div class="space-y-2">
          <label for="date" class="block text-sm font-medium">Date</label>
          <Input
            id="date"
            v-model="form.date"
            type="date"
            required
          />
        </div>

        <!-- Paid By -->
        <div class="space-y-2">
          <label class="block text-sm font-medium">Paid by</label>
          <Select v-model="form.paid_by">
            <option :value="authStore.user?.id">{{ authStore.user?.name }} (you)</option>
            <option v-for="p in availableParticipants" :key="p.user_id" :value="p.user_id">
              {{ p.user_name }}
            </option>
          </Select>
        </div>

        <!-- Group Selection (Optional) -->
        <div v-if="groups.length > 0" class="space-y-2">
          <label class="block text-sm font-medium">Group (optional)</label>
          <Select v-model="form.group_id">
            <option :value="undefined">No group</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </Select>
        </div>

        <!-- Split Type -->
        <div class="space-y-2">
          <label class="block text-sm font-medium">Split type</label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button
              v-for="type in splitTypes"
              :key="type.value"
              type="button"
              @click="form.split_type = type.value"
              :class="[
                'p-3 rounded-lg border text-sm font-medium transition-colors',
                form.split_type === type.value
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-input hover:bg-accent'
              ]"
            >
              {{ type.label }}
            </button>
          </div>
        </div>

        <!-- Participants -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <label class="block text-sm font-medium">Split with</label>
            <Button variant="outline" size="sm" type="button" @click="showAddParticipant = true">
              <PlusIcon class="h-4 w-4 mr-1" />
              Add person
            </Button>
          </div>

          <div class="space-y-2">
            <!-- Current User -->
            <ParticipantRow
              :participant="currentUserParticipant"
              :split-type="form.split_type"
              :total-amount="form.amount"
              :is-current-user="true"
              @update="updateParticipant"
            />

            <!-- Other Participants -->
            <ParticipantRow
              v-for="participant in form.participants"
              :key="participant.user_id"
              :participant="participant"
              :split-type="form.split_type"
              :total-amount="form.amount"
              :is-current-user="false"
              @update="updateParticipant"
              @remove="removeParticipant"
            />
          </div>

          <div v-if="form.participants.length === 0" class="text-center py-4 text-muted-foreground text-sm">
            Add participants to split this expense
          </div>

          <!-- Split Summary -->
          <div v-if="form.participants.length > 0" class="p-3 bg-muted rounded-lg text-sm">
            <div class="flex justify-between">
              <span>Total</span>
              <span class="font-medium">{{ formatCurrency(form.amount, form.currency) }}</span>
            </div>
            <div class="flex justify-between text-muted-foreground">
              <span>Remaining to split</span>
              <span :class="remainingAmount !== 0 ? 'text-destructive' : ''">
                {{ formatCurrency(remainingAmount, form.currency) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="flex gap-3 pt-4">
          <Button variant="outline" type="button" @click="router.back()" class="flex-1">
            Cancel
          </Button>
          <Button type="submit" :loading="loading" :disabled="!isValid" class="flex-1">
            Save Expense
          </Button>
        </div>
      </form>
    </div>

    <!-- Add Participant Dialog -->
    <AddParticipantDialog
      v-model:open="showAddParticipant"
      :existing-ids="existingParticipantIds"
      @add="addParticipant"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import { PlusIcon } from 'lucide-vue-next'
import { format } from 'date-fns'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import CurrencyInput from '@/components/Common/CurrencyInput.vue'
import CurrencyPicker from '@/components/Common/CurrencyPicker.vue'
import CategoryPicker from '@/components/Common/CategoryPicker.vue'
import ParticipantRow from './ParticipantRow.vue'
import AddParticipantDialog from './AddParticipantDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useExpenseStore } from '@/stores/expense'
import { useGroupStore } from '@/stores/group'
import { apiClient } from '@/services/api'
import { formatCurrency, calculateEqualSplit } from '@/utils/numbers'
import type { SplitType, ParticipantFormData, Group } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const expenseStore = useExpenseStore()
const groupStore = useGroupStore()

const loading = ref(false)
const showAddParticipant = ref(false)
const groups = ref<Group[]>([])

const splitTypes = [
  { value: 'EQUAL' as SplitType, label: 'Equally' },
  { value: 'EXACT' as SplitType, label: 'Exact amounts' },
  { value: 'PERCENTAGE' as SplitType, label: 'By percentage' },
  { value: 'SHARE' as SplitType, label: 'By shares' }
]

interface FormParticipant {
  user_id: number
  user_name: string
  amount: number
  percentage: number
  shares: number
  selected: boolean
}

const form = reactive({
  name: '',
  amount: 0,
  currency: authStore.user?.currency || 'USD',
  category: 'other',
  date: format(new Date(), 'yyyy-MM-dd'),
  paid_by: authStore.user?.id || 0,
  group_id: undefined as number | undefined,
  split_type: 'EQUAL' as SplitType,
  participants: [] as FormParticipant[]
})

// Current user as participant
const currentUserParticipant = computed<FormParticipant>(() => ({
  user_id: authStore.user?.id || 0,
  user_name: authStore.user?.name || 'You',
  amount: 0,
  percentage: 0,
  shares: 1,
  selected: true
}))

const availableParticipants = computed(() => {
  return form.participants.filter(p => p.user_id !== authStore.user?.id)
})

const existingParticipantIds = computed(() => {
  const ids = form.participants.map(p => p.user_id)
  ids.push(authStore.user?.id || 0)
  return ids
})

// Calculate remaining amount to split
const remainingAmount = computed(() => {
  if (form.split_type === 'EQUAL') return 0

  const totalSplit = form.participants.reduce((sum, p) => sum + p.amount, 0)
  return form.amount - totalSplit
})

const isValid = computed(() => {
  if (!form.name.trim()) return false
  if (form.amount <= 0) return false
  if (form.participants.length === 0) return false
  if (form.split_type !== 'EQUAL' && remainingAmount.value !== 0) return false
  return true
})

// Recalculate splits when amount or type changes
watch([() => form.amount, () => form.split_type, () => form.participants.length], () => {
  if (form.split_type === 'EQUAL' && form.participants.length > 0) {
    const allParticipants = [currentUserParticipant.value, ...form.participants]
    const shares = calculateEqualSplit(form.amount, allParticipants.length)

    form.participants.forEach((p, i) => {
      p.amount = shares[i + 1] || 0
    })
  }
})

// Load groups when group_id is in query
onMounted(async () => {
  try {
    groups.value = await apiClient.getGroups()

    // Pre-select group from query param
    const groupId = route.query.group_id
    if (groupId) {
      form.group_id = parseInt(groupId as string)
      await loadGroupMembers(form.group_id)
    }
  } catch (error) {
    console.error('Failed to load groups:', error)
  }
})

// Load group members when group changes
watch(() => form.group_id, async (groupId) => {
  if (groupId) {
    await loadGroupMembers(groupId)
  }
})

async function loadGroupMembers(groupId: number) {
  try {
    const group = await apiClient.getGroupDetails(groupId)
    form.currency = group.default_currency

    // Add group members as participants
    form.participants = group.members
      .filter(m => m.id !== authStore.user?.id)
      .map(m => ({
        user_id: m.id,
        user_name: m.name || m.email || 'Unknown',
        amount: 0,
        percentage: 0,
        shares: 1,
        selected: true
      }))
  } catch (error) {
    console.error('Failed to load group members:', error)
  }
}

function addParticipant(user: { id: number; name: string }) {
  if (form.participants.some(p => p.user_id === user.id)) return

  form.participants.push({
    user_id: user.id,
    user_name: user.name,
    amount: 0,
    percentage: 0,
    shares: 1,
    selected: true
  })
}

function updateParticipant(userId: number, updates: Partial<FormParticipant>) {
  const participant = form.participants.find(p => p.user_id === userId)
  if (participant) {
    Object.assign(participant, updates)
  }
}

function removeParticipant(userId: number) {
  form.participants = form.participants.filter(p => p.user_id !== userId)
}

async function handleSubmit() {
  if (!isValid.value) return

  loading.value = true
  try {
    // Build participants array with amounts
    const allParticipants = [
      { user_id: authStore.user!.id, amount: 0 },
      ...form.participants.filter(p => p.selected).map(p => ({
        user_id: p.user_id,
        amount: p.amount
      }))
    ]

    // For equal split, calculate amounts
    if (form.split_type === 'EQUAL') {
      const shares = calculateEqualSplit(form.amount, allParticipants.length)
      allParticipants.forEach((p, i) => {
        p.amount = shares[i]
      })
    }

    await expenseStore.createExpense({
      name: form.name.trim(),
      amount: form.amount,
      currency: form.currency,
      category: form.category,
      expense_date: new Date(form.date).toISOString(),
      paid_by: form.paid_by,
      group_id: form.group_id,
      split_type: form.split_type,
      participants: allParticipants.filter(p => p.amount > 0)
    })

    toast.success('Expense added successfully')

    // Navigate back or to expenses
    if (form.group_id) {
      router.push(`/groups/${form.group_id}`)
    } else {
      router.push('/expenses')
    }
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to add expense'
    toast.error(message)
  } finally {
    loading.value = false
  }
}
</script>

