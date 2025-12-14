<template>
  <Dialog v-model:open="isOpen" title="Settle Up" :description="`Settle your balance with ${friend?.user?.name}`">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <CurrencyInput
        v-model="amount"
        :currency="currency"
        label="Amount"
        required
      />

      <CurrencyPicker
        v-model="currency"
        label="Currency"
      />

      <div class="text-sm text-muted-foreground">
        <p v-if="totalOwed > 0">
          {{ friend?.user?.name }} owes you {{ formatCurrency(Math.abs(totalOwed), currency) }}
        </p>
        <p v-else-if="totalOwed < 0">
          You owe {{ friend?.user?.name }} {{ formatCurrency(Math.abs(totalOwed), currency) }}
        </p>
        <p v-else>
          You are settled up
        </p>
      </div>

      <div class="flex justify-end gap-2 pt-4">
        <Button variant="outline" type="button" @click="isOpen = false">
          Cancel
        </Button>
        <Button type="submit" :loading="loading">
          Record Payment
        </Button>
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { toast } from 'vue-sonner'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import CurrencyInput from '@/components/Common/CurrencyInput.vue'
import CurrencyPicker from '@/components/Common/CurrencyPicker.vue'
import { formatCurrency } from '@/utils/numbers'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Friend } from '@/types'

interface Props {
  friend: Friend | null
  groupId?: number
}

const props = defineProps<Props>()

const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
  settled: []
}>()

const authStore = useAuthStore()
const loading = ref(false)
const amount = ref(0)
const currency = ref('USD')

// Calculate total owed in current currency
const totalOwed = computed(() => {
  if (!props.friend) return 0
  const balance = props.friend.balances.find(b => b.currency === currency.value)
  return balance?.amount || 0
})

// Reset form when friend changes
watch(() => props.friend, (newFriend) => {
  if (newFriend) {
    const firstBalance = newFriend.balances[0]
    if (firstBalance) {
      currency.value = firstBalance.currency
      amount.value = Math.abs(firstBalance.amount)
    }
  }
})

async function handleSubmit() {
  if (!props.friend || amount.value <= 0) return

  loading.value = true
  try {
    const paidBy = totalOwed.value >= 0 ? props.friend.user.id : authStore.user!.id
    const otherUser = totalOwed.value >= 0 ? authStore.user!.id : props.friend.user.id

    await apiClient.createExpense({
      name: 'Settlement',
      amount: amount.value,
      currency: currency.value,
      category: 'settlement',
      split_type: 'SETTLEMENT',
      paid_by: paidBy,
      group_id: props.groupId,
      participants: [
        { user_id: paidBy, amount: 0 },
        { user_id: otherUser, amount: amount.value }
      ]
    })

    toast.success('Payment recorded successfully')
    emit('settled')
    isOpen.value = false
  } catch (error) {
    toast.error('Failed to record payment')
  } finally {
    loading.value = false
  }
}
</script>

