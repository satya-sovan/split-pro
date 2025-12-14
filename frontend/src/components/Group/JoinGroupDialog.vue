<template>
  <Dialog v-model:open="isOpen" title="Join Group">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="space-y-2">
        <label for="code" class="block text-sm font-medium">
          Group Invite Code <span class="text-destructive">*</span>
        </label>
        <Input
          id="code"
          v-model="inviteCode"
          placeholder="Enter invite code or link"
          required
        />
      </div>

      <p class="text-sm text-muted-foreground">
        Ask a group member to share the invite link or code with you.
      </p>

      <div class="flex justify-end gap-2 pt-4">
        <Button variant="outline" type="button" @click="isOpen = false">
          Cancel
        </Button>
        <Button type="submit" :loading="loading">
          Join Group
        </Button>
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import { apiClient } from '@/services/api'

const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
  joined: [group: any]
}>()

const loading = ref(false)
const inviteCode = ref('')

// Reset when dialog opens
watch(isOpen, (open) => {
  if (open) {
    inviteCode.value = ''
  }
})

async function handleSubmit() {
  if (!inviteCode.value.trim()) return

  // Extract public_id from URL if full link is pasted
  let publicId = inviteCode.value.trim()
  if (publicId.includes('/')) {
    const parts = publicId.split('/')
    publicId = parts[parts.length - 1] || publicId
  }

  loading.value = true
  try {
    const group = await apiClient.joinGroup(publicId)

    toast.success(`Joined "${group.name}" successfully`)
    emit('joined', group)
    isOpen.value = false
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to join group'
    toast.error(message)
  } finally {
    loading.value = false
  }
}
</script>

