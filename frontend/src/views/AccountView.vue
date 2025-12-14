<template>
  <MainLayout title="Account">
    <div class="p-6 max-w-2xl mx-auto">
      <div class="space-y-6">
        <!-- User Info -->
        <div class="p-6 bg-card rounded-lg border">
          <div class="flex items-center gap-4 mb-4">
            <div class="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <span class="text-2xl font-semibold">
                {{ authStore.user?.name?.charAt(0)?.toUpperCase() || '?' }}
              </span>
            </div>
            <div>
              <h2 class="text-xl font-bold">{{ authStore.user?.name }}</h2>
              <p class="text-muted-foreground">{{ authStore.user?.email }}</p>
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Settings</h3>

          <div class="p-4 bg-card rounded-lg border">
            <label for="currency" class="block text-sm font-medium mb-2">
              Default Currency
            </label>
            <select
              id="currency"
              v-model="userCurrency"
              @change="updateCurrency"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option v-for="curr in CURRENCIES" :key="curr" :value="curr">
                {{ curr }}
              </option>
            </select>
          </div>

          <div class="p-4 bg-card rounded-lg border">
            <label for="language" class="block text-sm font-medium mb-2">
              Language
            </label>
            <select
              id="language"
              v-model="userLanguage"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
        </div>

        <!-- Import/Export Section -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Data Management</h3>

          <!-- Import from Splitwise -->
          <div class="p-4 bg-card rounded-lg border">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="font-medium">Import from Splitwise</h4>
                <p class="text-sm text-muted-foreground">
                  Import your expenses from Splitwise CSV export
                </p>
              </div>
              <UploadIcon class="h-5 w-5 text-muted-foreground" />
            </div>

            <div class="space-y-3">
              <input
                ref="fileInputRef"
                type="file"
                accept=".csv"
                @change="handleFileSelect"
                class="hidden"
              />

              <button
                @click="triggerFileSelect"
                :disabled="isImporting"
                class="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
              >
                <span v-if="!selectedFile">Select CSV File</span>
                <span v-else>{{ selectedFile.name }}</span>
              </button>

              <button
                v-if="selectedFile"
                @click="handleImportSplitwise"
                :disabled="isImporting"
                class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                <span v-if="isImporting">Importing...</span>
                <span v-else>Import Data</span>
              </button>

              <!-- Import Results -->
              <div v-if="importStats" class="p-3 bg-green-50 dark:bg-green-900/20 rounded-md">
                <h5 class="font-medium text-green-800 dark:text-green-200 mb-2">Import Complete!</h5>
                <ul class="text-sm text-green-700 dark:text-green-300 space-y-1">
                  <li>Expenses imported: {{ importStats.expenses_imported }}</li>
                  <li>Friends imported: {{ importStats.friends_imported }}</li>
                  <li>Rows processed: {{ importStats.rows_processed }}</li>
                </ul>
                <div v-if="importStats.errors?.length > 0" class="mt-2 text-sm text-amber-700 dark:text-amber-300">
                  <p>{{ importStats.errors.length }} warnings:</p>
                  <ul class="list-disc list-inside">
                    <li v-for="(error, index) in importStats.errors.slice(0, 5)" :key="index">
                      {{ error }}
                    </li>
                    <li v-if="importStats.errors.length > 5">
                      ...and {{ importStats.errors.length - 5 }} more
                    </li>
                  </ul>
                </div>
              </div>

              <p class="text-xs text-muted-foreground">
                To export from Splitwise: Go to Splitwise → Account Settings → Export my data → Export as CSV
              </p>
            </div>
          </div>

          <!-- Export Data -->
          <button
            @click="handleExportData"
            class="w-full p-4 bg-card rounded-lg border hover:bg-accent text-left"
          >
            <div class="flex items-center justify-between">
              <div>
                <span class="font-medium">Export Data</span>
                <p class="text-sm text-muted-foreground">Download all your SAHA Split data</p>
              </div>
              <DownloadIcon class="h-5 w-5 text-muted-foreground" />
            </div>
          </button>
        </div>

        <!-- Account Actions -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Account</h3>

          <button
            @click="handleLogout"
            class="w-full p-4 bg-destructive/10 rounded-lg border border-destructive text-destructive hover:bg-destructive/20 text-left"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium">Logout</span>
              <LogOutIcon class="h-5 w-5" />
            </div>
          </button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DownloadIcon, LogOutIcon, UploadIcon } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import MainLayout from '@/components/Layout/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { CURRENCIES } from '@/lib/currency'
import { apiClient } from '@/services/api'

const authStore = useAuthStore()
const router = useRouter()

const userCurrency = ref(authStore.user?.currency || 'USD')
const userLanguage = ref(authStore.user?.preferredLanguage || 'en')

// Splitwise import state
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isImporting = ref(false)
const importStats = ref<{
  groups_imported: number
  friends_imported: number
  balances_imported: number
  expenses_imported: number
  rows_processed: number
  errors: string[]
} | null>(null)

async function updateCurrency() {
  try {
    await authStore.updateUser({ currency: userCurrency.value })
    toast.success('Currency updated')
  } catch (error) {
    toast.error('Failed to update currency')
  }
}

function triggerFileSelect() {
  fileInputRef.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    if (!file.name.endsWith('.csv')) {
      toast.error('Please select a CSV file')
      return
    }
    selectedFile.value = file
    importStats.value = null
  }
}

async function handleImportSplitwise() {
  if (!selectedFile.value) {
    toast.error('Please select a file first')
    return
  }

  isImporting.value = true
  importStats.value = null

  try {
    const result = await apiClient.importFromSplitwise(selectedFile.value)

    if (result.success) {
      importStats.value = result.statistics
      toast.success('Import completed successfully!')
      selectedFile.value = null
      if (fileInputRef.value) {
        fileInputRef.value.value = ''
      }
    } else {
      toast.error('Import failed')
    }
  } catch (error: any) {
    console.error('Import error:', error)
    toast.error(error.response?.data?.detail || error.message || 'Failed to import data')
  } finally {
    isImporting.value = false
  }
}

async function handleExportData() {
  try {
    const data = await apiClient.exportData()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `splitpro-export-${new Date().toISOString()}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    toast.success('Data exported successfully')
  } catch (error) {
    toast.error('Failed to export data')
  }
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

