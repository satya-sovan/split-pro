<template>
  <div class="space-y-2">
    <label v-if="label" class="block text-sm font-medium">
      {{ label }}
    </label>
    <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
      <button
        v-for="cat in categories"
        :key="cat.id"
        type="button"
        @click="$emit('update:modelValue', cat.id)"
        :class="[
          'flex flex-col items-center justify-center p-3 rounded-lg border transition-colors',
          modelValue === cat.id
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-input hover:bg-accent hover:text-accent-foreground'
        ]"
      >
        <span class="text-2xl mb-1">{{ cat.icon }}</span>
        <span class="text-xs font-medium">{{ cat.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CATEGORIES } from '@/lib/category'

interface Props {
  modelValue: string
  label?: string
}

defineProps<Props>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const categories = CATEGORIES
</script>

