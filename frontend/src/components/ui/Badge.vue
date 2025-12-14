<template>
  <span :class="[baseClass, variantClasses[variant]]">
    <slot />
  </span>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'
}

withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const baseClass = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors'

const variantClasses = {
  default: 'bg-primary text-primary-foreground',
  secondary: 'bg-secondary text-secondary-foreground',
  destructive: 'bg-destructive text-destructive-foreground',
  outline: 'border border-input bg-background',
  success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
}
</script>

