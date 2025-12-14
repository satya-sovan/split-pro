<template>
  <MainLayout title="Groups">
    <div class="p-6">
      <!-- Actions -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <Button @click="showCreate = true">
          <PlusIcon class="h-4 w-4 mr-2" />
          Create Group
        </Button>
        <Button variant="outline" @click="showJoin = true">
          <UsersIcon class="h-4 w-4 mr-2" />
          Join Group
        </Button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-8">
        <Spinner />
      </div>

      <!-- Empty State -->
      <EmptyState
        v-else-if="groups.length === 0"
        :icon="UserGroupIcon"
        title="No groups yet"
        description="Create a group to start splitting expenses with friends"
      >
        <template #action>
          <Button @click="showCreate = true">Create your first group</Button>
        </template>
      </EmptyState>

      <!-- Groups List -->
      <div v-else class="space-y-3">
        <GroupCard
          v-for="group in groups"
          :key="group.id"
          :group="group"
          :member-count="memberCounts[group.id] || 0"
          @click="viewGroup(group.id)"
        />
      </div>
    </div>

    <!-- Create Dialog -->
    <CreateGroupDialog
      v-model:open="showCreate"
      @created="handleCreated"
    />

    <!-- Join Dialog -->
    <JoinGroupDialog
      v-model:open="showJoin"
      @joined="handleJoined"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PlusIcon, UsersIcon } from 'lucide-vue-next'
import { UserGroupIcon } from '@heroicons/vue/24/outline'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Button from '@/components/ui/Button.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/Common/EmptyState.vue'
import GroupCard from '@/components/Group/GroupCard.vue'
import CreateGroupDialog from '@/components/Group/CreateGroupDialog.vue'
import JoinGroupDialog from '@/components/Group/JoinGroupDialog.vue'
import { apiClient } from '@/services/api'
import type { GroupWithBalance } from '@/types'

const router = useRouter()

const loading = ref(true)
const groups = ref<GroupWithBalance[]>([])
const memberCounts = ref<Record<number, number>>({})
const showCreate = ref(false)
const showJoin = ref(false)

onMounted(async () => {
  await loadGroups()
})

async function loadGroups() {
  loading.value = true
  try {
    groups.value = await apiClient.getGroupsWithBalances()

    // Load member counts
    for (const group of groups.value) {
      try {
        const details = await apiClient.getGroupDetails(group.id)
        memberCounts.value[group.id] = details.members?.length || 0
      } catch {
        memberCounts.value[group.id] = 0
      }
    }
  } catch (error) {
    console.error('Failed to load groups:', error)
  } finally {
    loading.value = false
  }
}

function viewGroup(groupId: number) {
  router.push(`/groups/${groupId}`)
}

async function handleCreated(group: any) {
  await loadGroups()
  router.push(`/groups/${group.id}`)
}

async function handleJoined(group: any) {
  await loadGroups()
  router.push(`/groups/${group.id}`)
}
</script>

