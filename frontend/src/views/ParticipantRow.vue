<template>
  <div class="flex items-center justify-between p-3 bg-accent/30 rounded-lg">
    <div class="flex items-center gap-3">
      <Avatar :name="participant.user_name" size="sm" />
      <div>
        <p class="font-medium text-sm">
          {{ participant.user_name }}
          <span v-if="isCurrentUser" class="text-muted-foreground">(you)</span>
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <!-- Amount Input (for EXACT split) -->
      <div v-if="splitType === 'EXACT'" class="w-24">
        <Input
          type="number"
          :model-value="displayAmount"
          @update:model-value="handleAmountChange"
          step="0.01"
          min="0"
          placeholder="0.00"
        />
      </div>

      <!-- Percentage Input -->
      <div v-else-if="splitType === 'PERCENTAGE'" class="flex items-center gap-1 w-20">
        <Input
          type="number"
          :model-value="participant.percentage"
          @update:model-value="handlePercentageChange"
          min="0"
          max="100"
          step="1"
        />
        <span class="text-sm">%</span>
      </div>

      <!-- Shares Input -->
      <div v-else-if="splitType === 'SHARE'" class="w-16">
        <Input
          type="number"
          :model-value="participant.shares"
          @update:model-value="handleSharesChange"
          min="0"
          step="1"
        />
      </div>

      <!-- Equal split display -->
      <div v-else class="text-sm font-medium text-muted-foreground">
        {{ formatCurrency(calculatedAmount, 'USD') }}
      </div>

      <!-- Remove button -->
      <Button
        v-if="!isCurrentUser"
        variant="ghost"
        size="icon"
        type="button"
        @click="$emit('remove', participant.user_id)"
      >
        <XIcon class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { XIcon } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import { formatCurrency } from '@/utils/numbers'
import type { SplitType } from '@/types'

interface Participant {
  user_id: number
  user_name: string
  amount: number
  percentage: number
  shares: number
  selected: boolean
}

interface Props {
  participant: Participant
  splitType: SplitType
  totalAmount: number
  isCurrentUser: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [userId: number, updates: Partial<Participant>]
  remove: [userId: number]
}>()

const displayAmount = computed(() => {
  if (props.participant.amount === 0) return ''
  return (props.participant.amount / 100).toFixed(2)
})

const calculatedAmount = computed(() => {
  return props.participant.amount
})

function handleAmountChange(value: string) {
  const num = parseFloat(value) || 0
  emit('update', props.participant.user_id, { amount: Math.round(num * 100) })
}

function handlePercentageChange(value: string) {
  const percentage = parseFloat(value) || 0
  const amount = Math.round((props.totalAmount * percentage) / 100)
  emit('update', props.participant.user_id, { percentage, amount })
}

function handleSharesChange(value: string) {
  const shares = parseInt(value) || 0
  emit('update', props.participant.user_id, { shares })
}
</script>

