<template>
  <Dialog v-model:open="isOpen" title="Settle Up">
    <div v-if="group" class="space-y-4">
      <p class="text-sm text-muted-foreground">
        Record a payment to settle your balance in {{ group.name }}.
      </p>

      <!-- Select who is paying -->
      <div class="space-y-2">
        <label class="block text-sm font-medium">Who is paying?</label>
        <Select v-model="form.payer">
          <option :value="authStore.user?.id">{{ authStore.user?.name }} (you)</option>
          <option v-for="member in otherMembers" :key="member.id" :value="member.id">
            {{ member.name }}
          </option>
        </Select>
      </div>

      <!-- Select who is receiving -->
      <div class="space-y-2">
        <label class="block text-sm font-medium">Who is receiving?</label>
        <Select v-model="form.receiver">
          <option v-for="member in receiverOptions" :key="member.id" :value="member.id">
            {{ member.name }}
          </option>
        </Select>
      </div>

      <!-- Amount -->
      <CurrencyInput
        v-model="form.amount"
        :currency="form.currency"
        label="Amount"
        required
      />

      <!-- Currency -->
      <CurrencyPicker
        v-model="form.currency"
        label="Currency"
      />

      <div class="flex justify-end gap-2 pt-4">
        <Button variant="outline" @click="isOpen = false">
          Cancel
        </Button>
        <Button @click="handleSubmit" :loading="loading" :disabled="!isValid">
          Record Payment
        </Button>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { toast } from 'vue-sonner'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Select from '@/components/ui/Select.vue'
import CurrencyInput from '@/components/Common/CurrencyInput.vue'
import CurrencyPicker from '@/components/Common/CurrencyPicker.vue'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { GroupDetail } from '@/types'

interface Props {
  group: GroupDetail | null
}

const props = defineProps<Props>()

const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
  settled: []
}>()

const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  payer: authStore.user?.id || 0,
  receiver: 0,
  amount: 0,
  currency: 'USD'
})

const otherMembers = computed(() => {
  if (!props.group?.members) return []
  return props.group.members.filter(m => m.id !== authStore.user?.id)
})

const receiverOptions = computed(() => {
  if (!props.group?.members) return []
  return props.group.members.filter(m => m.id !== form.payer)
})

const isValid = computed(() => {
  return form.payer > 0 && form.receiver > 0 && form.amount > 0
})

watch(() => props.group, (newGroup) => {
  if (newGroup) {
    form.currency = newGroup.default_currency
    if (otherMembers.value.length > 0) {
      form.receiver = otherMembers.value[0].id
    }
  }
}, { immediate: true })

watch(() => form.payer, () => {
  if (form.receiver === form.payer && receiverOptions.value.length > 0) {
    form.receiver = receiverOptions.value[0].id
  }
})

async function handleSubmit() {
  if (!props.group || !isValid.value) return

  loading.value = true
  try {
    await apiClient.createExpense({
      name: 'Settlement',
      amount: form.amount,
      currency: form.currency,
      category: 'settlement',
      split_type: 'SETTLEMENT',
      paid_by: form.payer,
      group_id: props.group.id,
      participants: [
        { user_id: form.payer, amount: 0 },
        { user_id: form.receiver, amount: form.amount }
      ]
    })

    toast.success('Payment recorded')
    emit('settled')
    isOpen.value = false
  } catch (error) {
    toast.error('Failed to record payment')
  } finally {
    loading.value = false
  }
}
</script>

