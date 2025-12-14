<template>
  <Dialog v-model:open="isOpen" title="Create Group">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="space-y-2">
        <label for="name" class="block text-sm font-medium">
          Group Name <span class="text-destructive">*</span>
        </label>
        <Input
          id="name"
          v-model="form.name"
          placeholder="e.g., Apartment, Trip to Paris"
          required
        />
      </div>

      <CurrencyPicker
        v-model="form.default_currency"
        label="Default Currency"
      />

      <div class="flex items-center gap-2">
        <input
          id="simplify"
          type="checkbox"
          v-model="form.simplify_debts"
          class="h-4 w-4 rounded border-input"
        />
        <label for="simplify" class="text-sm">
          Simplify group debts
        </label>
      </div>

      <p class="text-sm text-muted-foreground">
        When enabled, the group will automatically combine debts to minimize the number of transactions needed.
      </p>

      <div class="flex justify-end gap-2 pt-4">
        <Button variant="outline" type="button" @click="isOpen = false">
          Cancel
        </Button>
        <Button type="submit" :loading="loading">
          Create Group
        </Button>
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { toast } from 'vue-sonner'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import CurrencyPicker from '@/components/Common/CurrencyPicker.vue'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const isOpen = defineModel<boolean>('open', { default: false })

const emit = defineEmits<{
  created: [group: any]
}>()

const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  name: '',
  default_currency: authStore.user?.currency || 'USD',
  simplify_debts: false
})

// Reset form when dialog opens
watch(isOpen, (open) => {
  if (open) {
    form.name = ''
    form.default_currency = authStore.user?.currency || 'USD'
    form.simplify_debts = false
  }
})

async function handleSubmit() {
  if (!form.name.trim()) return

  loading.value = true
  try {
    const group = await apiClient.createGroup({
      name: form.name.trim(),
      default_currency: form.default_currency,
      simplify_debts: form.simplify_debts
    })

    toast.success('Group created successfully')
    emit('created', group)
    isOpen.value = false
  } catch (error) {
    toast.error('Failed to create group')
  } finally {
    loading.value = false
  }
}
</script>

