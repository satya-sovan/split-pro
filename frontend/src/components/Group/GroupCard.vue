<template>
  <div
    class="p-4 bg-card rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between mb-2">
      <div>
        <h3 class="font-semibold text-lg">{{ group.name }}</h3>
        <p class="text-sm text-muted-foreground">
          {{ memberCount }} member{{ memberCount !== 1 ? 's' : '' }}
        </p>
      </div>
      <div v-if="group.archived_at" class="px-2 py-1 bg-muted rounded text-xs text-muted-foreground">
        Archived
      </div>
    </div>

    <div v-if="hasBalances" class="mt-3 pt-3 border-t">
      <p class="text-xs text-muted-foreground mb-1">Your balance</p>
      <div
        v-for="(amount, currency) in group.balances"
        :key="currency"
        :class="[
          'text-sm font-medium',
          amount > 0 ? 'text-green-600' : amount < 0 ? 'text-red-600' : 'text-muted-foreground'
        ]"
      >
        {{ formatBalance(amount, currency) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatCurrency } from '@/utils/numbers'
import type { GroupWithBalance } from '@/types'

interface Props {
  group: GroupWithBalance
  memberCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  memberCount: 0
})

defineEmits<{
  click: []
}>()

const hasBalances = computed(() => {
  if (!props.group.balances) return false
  return Object.keys(props.group.balances).length > 0
})

function formatBalance(amount: number, currency: string): string {
  const formatted = formatCurrency(Math.abs(amount), currency)
  if (amount > 0) return `you are owed ${formatted}`
  if (amount < 0) return `you owe ${formatted}`
  return 'settled up'
}
</script>

