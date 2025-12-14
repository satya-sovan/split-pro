<template>
  <MainLayout title="Balances">
    <div class="p-6">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-8">
        <Spinner />
      </div>

      <div v-else class="space-y-6">
        <!-- Summary Cards -->
        <div class="grid gap-4 md:grid-cols-2">
          <Card class="p-6">
            <h3 class="text-sm font-medium text-muted-foreground mb-2">You owe</h3>
            <div class="space-y-1">
              <div
                v-for="balance in youOwe"
                :key="balance.currency"
                class="text-2xl font-bold text-red-600"
              >
                {{ formatCurrency(balance.amount, balance.currency) }}
              </div>
              <div v-if="youOwe.length === 0" class="text-2xl font-bold text-muted-foreground">
                $0.00
              </div>
            </div>
          </Card>

          <Card class="p-6">
            <h3 class="text-sm font-medium text-muted-foreground mb-2">You are owed</h3>
            <div class="space-y-1">
              <div
                v-for="balance in youGet"
                :key="balance.currency"
                class="text-2xl font-bold text-green-600"
              >
                {{ formatCurrency(balance.amount, balance.currency) }}
              </div>
              <div v-if="youGet.length === 0" class="text-2xl font-bold text-muted-foreground">
                $0.00
              </div>
            </div>
          </Card>
        </div>

        <!-- Friend Balances -->
        <div class="space-y-3">
          <h2 class="text-xl font-bold">Friends</h2>

          <EmptyState
            v-if="friends.length === 0"
            :icon="UsersIcon"
            title="No balances yet"
            description="Start adding expenses to see your balances with friends"
          >
            <template #action>
              <Button @click="router.push('/add')">Add an expense</Button>
            </template>
          </EmptyState>

          <FriendCard
            v-for="friend in friends"
            :key="friend.user.id"
            :friend="friend"
            @click="viewFriend(friend.user.id)"
          />
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UsersIcon } from 'lucide-vue-next'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/Common/EmptyState.vue'
import FriendCard from '@/components/Friend/FriendCard.vue'
import { apiClient } from '@/services/api'
import { formatCurrency } from '@/utils/numbers'
import type { Friend, CurrencyAmount } from '@/types'

const router = useRouter()

const loading = ref(true)
const friends = ref<Friend[]>([])

// Calculate summary
const youOwe = computed<CurrencyAmount[]>(() => {
  const totals: Record<string, number> = {}

  for (const friend of friends.value) {
    for (const balance of friend.balances) {
      if (balance.amount < 0) {
        if (!totals[balance.currency]) totals[balance.currency] = 0
        totals[balance.currency] += Math.abs(balance.amount)
      }
    }
  }

  return Object.entries(totals).map(([currency, amount]) => ({ currency, amount }))
})

const youGet = computed<CurrencyAmount[]>(() => {
  const totals: Record<string, number> = {}

  for (const friend of friends.value) {
    for (const balance of friend.balances) {
      if (balance.amount > 0) {
        if (!totals[balance.currency]) totals[balance.currency] = 0
        totals[balance.currency] += balance.amount
      }
    }
  }

  return Object.entries(totals).map(([currency, amount]) => ({ currency, amount }))
})

onMounted(async () => {
  await loadBalances()
})

async function loadBalances() {
  loading.value = true
  try {
    friends.value = await apiClient.getFriends()
  } catch (error) {
    console.error('Failed to load balances:', error)
  } finally {
    loading.value = false
  }
}

function viewFriend(friendId: number) {
  router.push(`/friends/${friendId}`)
}
</script>

