<template>
  <div :class="['rounded-lg border bg-card text-card-foreground shadow-sm', className]">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  className?: string
}>()
</script>

