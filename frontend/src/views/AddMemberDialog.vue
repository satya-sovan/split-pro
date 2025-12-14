<template>
  <Dialog v-model:open="isOpen" title="Invite Member">
    <div class="space-y-4">
      <p class="text-sm text-muted-foreground">
        Search for an existing user by email to add them to this group.
      </p>

      <div class="space-y-2">
        <label for="email" class="block text-sm font-medium">Email Address</label>
        <Input
          id="email"
          v-model="email"
          type="email"
          placeholder="friend@example.com"
          @keyup.enter="searchAndAdd"
        />
      </div>

      <div v-if="error" class="text-sm text-destructive">
        {{ error }}
      </div>

      <div class="flex justify-end gap-2 pt-4">
        <Button variant="outline" @click="isOpen = false">
          Cancel
        </Button>
        <Button @click="searchAndAdd" :loading="loading" :disabled="!email.trim()">
          Add Member
        </Button>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import { apiClient } from '@/services/api'

interface Props {
  groupId: number
}

const props = defineProps<Props>()

const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
  added: []
}>()

const email = ref('')
const loading = ref(false)
const error = ref('')

watch(isOpen, (open) => {
  if (open) {
    email.value = ''
    error.value = ''
  }
})

async function searchAndAdd() {
  if (!email.value.trim()) return

  loading.value = true
  error.value = ''

  try {
    // First, find the user by email
    const friends = await apiClient.getFriends()
    const found = friends.find(f => f.user.email?.toLowerCase() === email.value.toLowerCase())

    if (!found) {
      error.value = 'User not found. They may need to create an account first.'
      return
    }

    // Add to group
    await apiClient.addGroupMember(props.groupId, found.user.id)

    toast.success(`${found.user.name} added to group`)
    emit('added')
    isOpen.value = false
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to add member'
  } finally {
    loading.value = false
  }
}
</script>

