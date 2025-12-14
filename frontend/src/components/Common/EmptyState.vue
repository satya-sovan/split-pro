<template>
  <div class="text-center py-12">
    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
      <component :is="icon" class="h-8 w-8 text-muted-foreground" />
    </div>
    <h3 class="text-lg font-semibold mb-2">{{ title }}</h3>
    <p class="text-muted-foreground mb-4">{{ description }}</p>
    <slot name="action" />
  </div>
</template>

<script setup lang="ts">
import { type Component } from 'vue'

interface Props {
  icon: Component
  title: string
  description: string
}

defineProps<Props>()
</script>

