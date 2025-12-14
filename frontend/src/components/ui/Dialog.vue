<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-black/50 transition-opacity"
          @click="$emit('update:open', false)"
        />

        <!-- Dialog Content -->
        <div
          class="fixed z-50 w-full max-w-lg max-h-[85vh] overflow-auto bg-background rounded-lg shadow-lg p-6 animate-in fade-in-0 zoom-in-95"
          role="dialog"
          aria-modal="true"
        >
          <!-- Header -->
          <div v-if="title || $slots.header" class="mb-4">
            <slot name="header">
              <h2 class="text-lg font-semibold">{{ title }}</h2>
              <p v-if="description" class="text-sm text-muted-foreground mt-1">
                {{ description }}
              </p>
            </slot>
          </div>

          <!-- Content -->
          <div class="py-4">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="mt-4 flex justify-end gap-2">
            <slot name="footer" />
          </div>

          <!-- Close Button -->
          <button
            type="button"
            class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            @click="$emit('update:open', false)"
          >
            <XIcon class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { XIcon } from 'lucide-vue-next'

interface Props {
  open: boolean
  title?: string
  description?: string
}

defineProps<Props>()

defineEmits<{
  'update:open': [value: boolean]
}>()
</script>

<style scoped>
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}
</style>

