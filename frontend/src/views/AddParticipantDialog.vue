<template>
  <Dialog v-model:open="isOpen" title="Add Participant">
    <div class="space-y-4">
      <div class="space-y-2">
        <label for="email" class="block text-sm font-medium">
          Search by email
        </label>
        <Input
          id="email"
          v-model="searchEmail"
          placeholder="Enter email address"
          type="email"
          @keyup.enter="searchUser"
        />
      </div>

      <Button @click="searchUser" :loading="searching" :disabled="!searchEmail.trim()">
        Search
      </Button>

      <!-- Search Results -->
      <div v-if="searchResult" class="p-3 bg-accent/30 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Avatar :name="searchResult.name" size="sm" />
            <div>
              <p class="font-medium">{{ searchResult.name }}</p>
              <p class="text-sm text-muted-foreground">{{ searchResult.email }}</p>
            </div>
          </div>
          <Button size="sm" @click="addUser">Add</Button>
        </div>
      </div>

      <div v-if="searchError" class="text-sm text-destructive">
        {{ searchError }}
      </div>

      <!-- Recent Friends -->
      <div v-if="recentFriends.length > 0" class="space-y-2">
        <p class="text-sm font-medium">Recent contacts</p>
        <div class="space-y-2 max-h-48 overflow-y-auto">
          <div
            v-for="friend in filteredFriends"
            :key="friend.user.id"
            class="flex items-center justify-between p-2 hover:bg-accent rounded cursor-pointer"
            @click="addFromFriend(friend)"
          >
            <div class="flex items-center gap-2">
              <Avatar :name="friend.user.name" size="sm" />
              <span class="text-sm">{{ friend.user.name }}</span>
            </div>
            <PlusIcon class="h-4 w-4 text-muted-foreground" />
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import { PlusIcon } from 'lucide-vue-next'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Avatar from '@/components/ui/Avatar.vue'
import { apiClient } from '@/services/api'
import type { Friend, User } from '@/types'

interface Props {
  existingIds: number[]
}

const props = defineProps<Props>()

const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
  add: [user: { id: number; name: string }]
}>()

const searchEmail = ref('')
const searching = ref(false)
const searchResult = ref<User | null>(null)
const searchError = ref('')
const recentFriends = ref<Friend[]>([])

const filteredFriends = computed(() => {
  return recentFriends.value.filter(f => !props.existingIds.includes(f.user.id))
})

onMounted(async () => {
  try {
    recentFriends.value = await apiClient.getFriends()
  } catch (error) {
    console.error('Failed to load friends:', error)
  }
})

async function searchUser() {
  if (!searchEmail.value.trim()) return

  searching.value = true
  searchResult.value = null
  searchError.value = ''

  try {
    // Use the dedicated search endpoint
    const user = await apiClient.searchUserByEmail(searchEmail.value.trim())

    if (props.existingIds.includes(user.id)) {
      searchError.value = 'User is already a participant'
    } else {
      searchResult.value = user
    }
  } catch (error: any) {
    if (error.response?.status === 404) {
      searchError.value = 'User not found. They may need to create an account first.'
    } else if (error.response?.status === 400) {
      searchError.value = error.response.data.detail || 'Cannot add this user'
    } else {
      searchError.value = 'Failed to search. Please try again.'
    }
  } finally {
    searching.value = false
  }
}

function addUser() {
  if (!searchResult.value) return

  emit('add', {
    id: searchResult.value.id,
    name: searchResult.value.name || searchResult.value.email || 'Unknown'
  })

  searchResult.value = null
  searchEmail.value = ''
  isOpen.value = false
}

function addFromFriend(friend: Friend) {
  emit('add', {
    id: friend.user.id,
    name: friend.user.name || friend.user.email || 'Unknown'
  })
  isOpen.value = false
}
</script>

