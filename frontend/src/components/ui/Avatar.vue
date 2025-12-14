<template>
  <div class="h-10 w-10 rounded-full flex items-center justify-center overflow-hidden" :class="sizeClasses">
    <img
      v-if="src"
      :src="src"
      :alt="name || 'Avatar'"
      class="h-full w-full object-cover"
      @error="handleImageError"
    />
    <div
      v-else
      class="h-full w-full flex items-center justify-center text-primary-foreground font-semibold"
      :style="{ backgroundColor: bgColor }"
    >
      {{ initials }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  src?: string | null
  name?: string | null
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const imageFailed = ref(false)

const sizeClasses = computed(() => ({
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
  xl: 'h-16 w-16 text-lg'
}[props.size]))

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .split(' ')
    .map(part => part[0])
    .join('')
    .substring(0, 2)
    .toUpperCase()
})

const bgColor = computed(() => {
  if (!props.name) return '#6366f1'

  // Generate consistent color from name
  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = props.name.charCodeAt(i) + ((hash << 5) - hash)
  }

  const colors = [
    '#ef4444', '#f97316', '#f59e0b', '#84cc16', '#22c55e',
    '#14b8a6', '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6',
    '#a855f7', '#d946ef', '#ec4899', '#f43f5e'
  ]

  return colors[Math.abs(hash) % colors.length]
})

function handleImageError() {
  imageFailed.value = true
}
</script>

