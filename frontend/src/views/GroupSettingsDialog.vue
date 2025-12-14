<template>
  <Dialog v-model:open="isOpen" title="Group Settings">
    <div v-if="group" class="space-y-6">
      <!-- Name -->
      <div class="space-y-2">
        <label for="name" class="block text-sm font-medium">Group Name</label>
        <Input
          id="name"
          v-model="form.name"
          :disabled="!isOwner"
        />
      </div>

      <!-- Currency -->
      <CurrencyPicker
        v-model="form.default_currency"
        label="Default Currency"
        :disabled="!isOwner"
      />

      <!-- Simplify Debts -->
      <div class="flex items-center gap-2">
        <input
          id="simplify"
          type="checkbox"
          v-model="form.simplify_debts"
          :disabled="!isOwner"
          class="h-4 w-4 rounded border-input"
        />
        <label for="simplify" class="text-sm">
          Simplify group debts
        </label>
      </div>

      <!-- Danger Zone -->
      <div class="pt-4 border-t">
        <h4 class="text-sm font-medium text-destructive mb-3">Danger Zone</h4>

        <div class="space-y-2">
          <Button
            variant="outline"
            class="w-full"
            @click="handleRecalculate"
            :loading="recalculating"
          >
            <RefreshCwIcon class="h-4 w-4 mr-2" />
            Recalculate Balances
          </Button>

          <Button
            variant="outline"
            class="w-full"
            @click="handleLeave"
            :disabled="isOwner"
          >
            <LogOutIcon class="h-4 w-4 mr-2" />
            Leave Group
          </Button>

          <Button
            v-if="isOwner"
            variant="destructive"
            class="w-full"
            @click="handleDelete"
          >
            <Trash2Icon class="h-4 w-4 mr-2" />
            Delete Group
          </Button>
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-4">
        <Button variant="outline" @click="isOpen = false">
          Cancel
        </Button>
        <Button @click="handleSave" :loading="saving" :disabled="!isOwner">
          Save Changes
        </Button>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { toast } from 'vue-sonner'
import { RefreshCwIcon, LogOutIcon, Trash2Icon } from 'lucide-vue-next'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
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
  updated: []
  deleted: []
}>()

const authStore = useAuthStore()
const saving = ref(false)
const recalculating = ref(false)

const form = reactive({
  name: '',
  default_currency: 'USD',
  simplify_debts: false
})

const isOwner = computed(() => props.group?.user_id === authStore.user?.id)

watch(() => props.group, (newGroup) => {
  if (newGroup) {
    form.name = newGroup.name
    form.default_currency = newGroup.default_currency
    form.simplify_debts = newGroup.simplify_debts
  }
}, { immediate: true })

async function handleSave() {
  if (!props.group) return

  saving.value = true
  try {
    await apiClient.updateGroup(props.group.id, {
      name: form.name,
      default_currency: form.default_currency,
      simplify_debts: form.simplify_debts
    })
    toast.success('Group updated')
    emit('updated')
    isOpen.value = false
  } catch (error) {
    toast.error('Failed to update group')
  } finally {
    saving.value = false
  }
}

async function handleRecalculate() {
  if (!props.group) return

  recalculating.value = true
  try {
    await apiClient.recalculateGroupBalances(props.group.id)
    toast.success('Balances recalculated')
    emit('updated')
  } catch (error) {
    toast.error('Failed to recalculate')
  } finally {
    recalculating.value = false
  }
}

async function handleLeave() {
  if (!props.group) return
  if (!confirm('Are you sure you want to leave this group?')) return

  try {
    await apiClient.leaveGroup(props.group.id)
    toast.success('Left group')
    emit('deleted')
    isOpen.value = false
  } catch (error) {
    toast.error('Failed to leave group')
  }
}

async function handleDelete() {
  if (!props.group) return
  if (!confirm('Are you sure you want to delete this group? This cannot be undone.')) return

  try {
    await apiClient.deleteGroup(props.group.id)
    toast.success('Group deleted')
    emit('deleted')
    isOpen.value = false
  } catch (error) {
    toast.error('Failed to delete group')
  }
}
</script>

