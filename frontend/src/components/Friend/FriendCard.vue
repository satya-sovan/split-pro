<template>
  <div
    class="p-4 bg-card rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Avatar :name="friend.user.name" :src="friend.user.image" />
        <div>
          <p class="font-medium">{{ friend.user.name || 'Unknown' }}</p>
          <p class="text-sm text-muted-foreground">{{ friend.user.email || '' }}</p>
        </div>
      </div>
      <div class="text-right">
        <div
          v-for="balance in friend.balances"
          :key="balance.currency"
          :class="[
            'font-semibold',
            balance.amount > 0 ? 'text-green-600' : balance.amount < 0 ? 'text-red-600' : 'text-muted-foreground'
          ]"
        >
          <span class="text-xs mr-1">
            {{ balance.amount > 0 ? 'owes you' : balance.amount < 0 ? 'you owe' : 'settled' }}
          </span>
          {{ formatCurrency(Math.abs(balance.amount), balance.currency) }}
        </div>
        <p v-if="friend.balances.length === 0" class="text-muted-foreground text-sm">
          Settled up
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Avatar from '@/components/ui/Avatar.vue'
import { formatCurrency } from '@/utils/numbers'
import type { Friend } from '@/types'

defineProps<{
  friend: Friend
}>()

defineEmits<{
  click: []
}>()
</script>

