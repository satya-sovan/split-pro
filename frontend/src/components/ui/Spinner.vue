<template>
  <div class="flex justify-center items-center" :class="{ 'h-64': !inline }">
    <div class="inline-block animate-spin rounded-full border-4 border-solid border-current border-r-transparent" :class="sizeClasses" />
    <span v-if="text" class="ml-2 text-muted-foreground">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  inline?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  inline: false
})

const sizeClasses = computed(() => ({
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12'
}[props.size]))
</script>

