<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div class="container flex h-14 items-center">
        <div class="flex-1 flex items-center gap-2">
          <img src="/icons/icon-512x512.svg" alt="SAHA Split" class="h-8 w-8" />
          <h1 class="text-lg font-semibold">{{ title }}</h1>
        </div>
        <div class="flex items-center gap-2">
          <slot name="actions"></slot>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto pb-20">
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
      </div>
      <slot v-else></slot>
    </main>

    <!-- Bottom Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 z-50 bg-background border-t">
      <div class="container flex justify-around items-center h-16">
        <router-link
          to="/home"
          class="flex flex-col items-center gap-1 px-3 py-2 text-sm"
          :class="isActive('/home') ? 'text-primary' : 'text-muted-foreground'"
        >
          <HomeIcon class="h-6 w-6" />
          <span>Home</span>
        </router-link>

        <router-link
          to="/balances"
          class="flex flex-col items-center gap-1 px-3 py-2 text-sm"
          :class="isActive('/balances') ? 'text-primary' : 'text-muted-foreground'"
        >
          <ScaleIcon class="h-6 w-6" />
          <span>Balances</span>
        </router-link>

        <router-link
          to="/add"
          class="flex flex-col items-center gap-1 px-3 py-2 text-sm"
          :class="isActive('/add') ? 'text-primary' : 'text-muted-foreground'"
        >
          <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center -mt-3">
            <PlusIcon class="h-6 w-6 text-white" />
          </div>
        </router-link>

        <router-link
          to="/groups"
          class="flex flex-col items-center gap-1 px-3 py-2 text-sm"
          :class="isActive('/groups') ? 'text-primary' : 'text-muted-foreground'"
        >
          <UserGroupIcon class="h-6 w-6" />
          <span>Groups</span>
        </router-link>

        <router-link
          to="/account"
          class="flex flex-col items-center gap-1 px-3 py-2 text-sm"
          :class="isActive('/account') ? 'text-primary' : 'text-muted-foreground'"
        >
          <UserIcon class="h-6 w-6" />
          <span>Account</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { HomeIcon, ScaleIcon, PlusIcon, UserIcon } from 'lucide-vue-next'
import { UserGroupIcon } from '@heroicons/vue/24/outline'

defineProps<{
  title: string
  loading?: boolean
}>()

const route = useRoute()

const isActive = (path: string) => {
  return route.path === path
}
</script>

