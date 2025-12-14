<template>
  <div class="space-y-3">
    <div
      v-for="member in members"
      :key="member.id"
      class="flex items-center justify-between p-3 rounded-lg bg-accent/50"
    >
      <div class="flex items-center gap-3">
        <Avatar :name="member.name" :src="member.image" size="sm" />
        <div>
          <p class="font-medium text-sm">{{ member.name || 'Unknown' }}</p>
          <p class="text-xs text-muted-foreground">{{ member.email }}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Badge v-if="member.id === creatorId" variant="secondary">Owner</Badge>
        <Badge v-if="member.id === currentUserId" variant="outline">You</Badge>
        <Button
          v-if="canRemove && member.id !== creatorId && member.id !== currentUserId"
          variant="ghost"
          size="icon"
          @click="$emit('remove', member.id)"
        >
          <XIcon class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <div v-if="members.length === 0" class="text-center py-4 text-muted-foreground">
      No members in this group
    </div>
  </div>
</template>

<script setup lang="ts">
import { XIcon } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import type { User } from '@/types'

interface Props {
  members: User[]
  creatorId?: number
  currentUserId?: number
  canRemove?: boolean
}

withDefaults(defineProps<Props>(), {
  canRemove: false
})

defineEmits<{
  remove: [userId: number]
}>()
</script>

