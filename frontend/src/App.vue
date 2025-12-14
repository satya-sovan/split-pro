<template>
  <div id="app" class="min-h-screen bg-background text-foreground">
    <RouterView />
    <Toaster />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Toaster } from 'vue-sonner'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Check authentication status on app mount
  authStore.checkAuth()
})
</script>

