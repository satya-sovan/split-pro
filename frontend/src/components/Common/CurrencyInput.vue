<template>
  <div class="space-y-2">
    <label v-if="label" :for="id" class="block text-sm font-medium">
      {{ label }}
      <span v-if="required" class="text-destructive">*</span>
    </label>
    <div class="relative">
      <Input
        :id="id"
        type="text"
        inputmode="number"
        :model-value="displayValue"
        @update:model-value="handleInput"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        class="pr-12"
      />
      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">
        {{ currency }}
      </span>
    </div>
    <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm text-muted-foreground">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Input from '@/components/ui/Input.vue'

interface Props {
  modelValue: number // Value in cents
  currency: string
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  error?: string
  hint?: string
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '0.00',
  disabled: false,
  required: false
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

// Convert cents to display value (e.g., 1000 -> "10.00")
const displayValue = computed(() => {
  if (props.modelValue === 0) return ''
  return (props.modelValue / 100).toFixed(2)
})

// Convert display value back to cents - handles string input with commas, spaces, etc.
function handleInput(value: string) {
  // Remove non-numeric characters except decimal point
  const cleaned = value.replace(/[^\d.]/g, '')
  // Handle multiple decimal points - keep only first
  const parts = cleaned.split('.')
  const normalized = parts.length > 1
    ? parts[0] + '.' + parts.slice(1).join('')
    : cleaned

  const num = parseFloat(normalized) || 0
  emit('update:modelValue', Math.round(num * 100))
}
</script>

