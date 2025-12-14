<template>
  <input
    :type="type"
    :value="modelValue"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    :class="[
      'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
      'ring-offset-background',
      'placeholder:text-muted-foreground',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
      'disabled:cursor-not-allowed disabled:opacity-50',
      error ? 'border-destructive focus-visible:ring-destructive' : ''
    ]"
    :placeholder="placeholder"
    :disabled="disabled"
    :required="required"
    :min="min"
    :max="max"
    :step="step"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue: string | number
  type?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  error?: boolean
  min?: string | number
  max?: string | number
  step?: string | number
}

withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false,
  error: false
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

