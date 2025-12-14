<template>
  <MainLayout title="Account">
    <div class="p-6 max-w-2xl mx-auto">
      <div class="space-y-6">
        <!-- User Info with Profile Picture -->
        <div class="p-6 bg-card rounded-lg border">
          <div class="flex items-center gap-4 mb-4">
            <!-- Profile Picture -->
            <div class="relative">
              <div
                class="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden cursor-pointer group"
                @click="triggerProfilePictureUpload"
              >
                <img
                  v-if="profilePictureUrl"
                  :src="profilePictureUrl"
                  class="h-full w-full object-cover"
                  alt="Profile"
                />
                <span v-else class="text-3xl font-semibold">
                  {{ authStore.user?.name?.charAt(0)?.toUpperCase() || '?' }}
                </span>
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <CameraIcon class="h-6 w-6 text-white" />
                </div>
              </div>
              <button
                v-if="profilePictureUrl"
                @click.stop="handleDeleteProfilePicture"
                class="absolute -bottom-1 -right-1 p-1 bg-destructive rounded-full text-white hover:bg-destructive/90"
                title="Remove picture"
              >
                <XIcon class="h-4 w-4" />
              </button>
            </div>
            <input
              ref="profilePictureInputRef"
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              @change="handleProfilePictureSelect"
              class="hidden"
            />
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <h2 v-if="!isEditingName" class="text-xl font-bold">{{ authStore.user?.name }}</h2>
                <input
                  v-else
                  v-model="editedName"
                  class="text-xl font-bold bg-transparent border-b border-primary focus:outline-none"
                  @keyup.enter="saveName"
                  @keyup.escape="cancelEditName"
                />
                <button
                  v-if="!isEditingName"
                  @click="startEditName"
                  class="p-1 hover:bg-accent rounded"
                >
                  <PencilIcon class="h-4 w-4 text-muted-foreground" />
                </button>
                <button
                  v-else
                  @click="saveName"
                  class="p-1 hover:bg-accent rounded text-green-600"
                >
                  <CheckIcon class="h-4 w-4" />
                </button>
              </div>
              <p class="text-muted-foreground">{{ authStore.user?.email }}</p>
              <p v-if="authStore.user?.created_at" class="text-xs text-muted-foreground mt-1">
                Member since {{ formatDate(authStore.user.created_at) }}
              </p>
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

        <!-- Security -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Security</h3>

          <!-- Change Password -->
          <div class="p-4 bg-card rounded-lg border">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="font-medium">Change Password</h4>
                <p class="text-sm text-muted-foreground">
                  Update your account password
                </p>
              </div>
              <LockIcon class="h-5 w-5 text-muted-foreground" />
            </div>

            <div v-if="showChangePassword" class="space-y-3">
              <input
                v-model="currentPassword"
                type="password"
                placeholder="Current password"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                v-model="newPassword"
                type="password"
                placeholder="New password (min 8 characters)"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                v-model="confirmNewPassword"
                type="password"
                placeholder="Confirm new password"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <div class="flex gap-2">
                <button
                  @click="handleChangePassword"
                  :disabled="isChangingPassword"
                  class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                >
                  {{ isChangingPassword ? 'Updating...' : 'Update Password' }}
                </button>
                <button
                  @click="showChangePassword = false"
                  class="px-4 py-2 border rounded-md hover:bg-accent"
                >
                  Cancel
                </button>
              </div>
            </div>
            <button
              v-else
              @click="showChangePassword = true"
              class="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Change Password
            </button>
          </div>
        </div>

        <!-- Notifications -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Notifications</h3>

          <div class="p-4 bg-card rounded-lg border space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-medium">Email Notifications</h4>
                <p class="text-sm text-muted-foreground">Receive updates via email</p>
              </div>
            </div>

            <div class="space-y-3 pl-4">
              <label class="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="notificationPrefs.email_expense_added"
                  @change="saveNotificationPrefs"
                  class="rounded"
                />
                <span class="text-sm">When someone adds an expense</span>
              </label>
              <label class="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="notificationPrefs.email_expense_updated"
                  @change="saveNotificationPrefs"
                  class="rounded"
                />
                <span class="text-sm">When an expense is updated</span>
              </label>
              <label class="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="notificationPrefs.email_payment_received"
                  @change="saveNotificationPrefs"
                  class="rounded"
                />
                <span class="text-sm">When you receive a payment</span>
              </label>
              <label class="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="notificationPrefs.email_weekly_summary"
                  @change="saveNotificationPrefs"
                  class="rounded"
                />
                <span class="text-sm">Weekly balance summary</span>
              </label>
            </div>

            <div class="border-t pt-4">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h4 class="font-medium">Push Notifications</h4>
                  <p class="text-sm text-muted-foreground">Receive push notifications</p>
                </div>
              </div>

              <div class="space-y-3 pl-4">
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="notificationPrefs.push_expense_added"
                    @change="saveNotificationPrefs"
                    class="rounded"
                  />
                  <span class="text-sm">When someone adds an expense</span>
                </label>
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="notificationPrefs.push_expense_updated"
                    @change="saveNotificationPrefs"
                    class="rounded"
                  />
                  <span class="text-sm">When an expense is updated</span>
                </label>
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="notificationPrefs.push_payment_received"
                    @change="saveNotificationPrefs"
                    class="rounded"
                  />
                  <span class="text-sm">When you receive a payment</span>
                </label>
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="notificationPrefs.push_reminders"
                    @change="saveNotificationPrefs"
                    class="rounded"
                  />
                  <span class="text-sm">Payment reminders</span>
                </label>
              </div>
            </div>
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
            class="w-full p-4 bg-card rounded-lg border hover:bg-accent text-left"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium">Logout</span>
              <LogOutIcon class="h-5 w-5" />
            </div>
          </button>

          <!-- Delete Account -->
          <div class="p-4 bg-destructive/10 rounded-lg border border-destructive">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="font-medium text-destructive">Delete Account</h4>
                <p class="text-sm text-destructive/70">
                  Permanently delete your account and all data
                </p>
              </div>
              <TrashIcon class="h-5 w-5 text-destructive" />
            </div>

            <div v-if="showDeleteAccount" class="space-y-3">
              <p class="text-sm text-destructive">
                This action cannot be undone. All your expenses, groups, and balances will be permanently deleted.
              </p>
              <input
                v-model="deleteConfirmation"
                type="text"
                placeholder="Type 'DELETE MY ACCOUNT' to confirm"
                class="w-full px-3 py-2 border border-destructive rounded-md focus:outline-none focus:ring-2 focus:ring-destructive"
              />
              <input
                v-model="deletePassword"
                type="password"
                placeholder="Enter your password"
                class="w-full px-3 py-2 border border-destructive rounded-md focus:outline-none focus:ring-2 focus:ring-destructive"
              />
              <div class="flex gap-2">
                <button
                  @click="handleDeleteAccount"
                  :disabled="isDeletingAccount || deleteConfirmation !== 'DELETE MY ACCOUNT'"
                  class="px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 disabled:opacity-50"
                >
                  {{ isDeletingAccount ? 'Deleting...' : 'Delete Account' }}
                </button>
                <button
                  @click="showDeleteAccount = false"
                  class="px-4 py-2 border rounded-md hover:bg-accent"
                >
                  Cancel
                </button>
              </div>
            </div>
            <button
              v-else
              @click="showDeleteAccount = true"
              class="w-full px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90"
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  DownloadIcon, LogOutIcon, UploadIcon, LockIcon, CameraIcon,
  XIcon, PencilIcon, CheckIcon, TrashIcon
} from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import MainLayout from '@/components/Layout/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { CURRENCIES } from '@/lib/currency'
import { apiClient, type NotificationPreferences } from '@/services/api'

const authStore = useAuthStore()
const router = useRouter()

const userCurrency = ref(authStore.user?.currency || 'USD')
const userLanguage = ref(authStore.user?.preferredLanguage || 'en')

// Profile picture state
const profilePictureInputRef = ref<HTMLInputElement | null>(null)
const profilePictureUrl = ref<string | null>(null)
const isUploadingPicture = ref(false)

// Name editing state
const isEditingName = ref(false)
const editedName = ref('')

// Password change state
const showChangePassword = ref(false)
const currentPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const isChangingPassword = ref(false)

// Notification preferences state
const notificationPrefs = ref<NotificationPreferences>({
  email_expense_added: true,
  email_expense_updated: true,
  email_payment_received: true,
  email_weekly_summary: false,
  push_expense_added: true,
  push_expense_updated: true,
  push_payment_received: true,
  push_reminders: true
})

// Delete account state
const showDeleteAccount = ref(false)
const deleteConfirmation = ref('')
const deletePassword = ref('')
const isDeletingAccount = ref(false)

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

onMounted(async () => {
  // Load profile picture
  try {
    const { url } = await apiClient.getProfilePictureUrl()
    if (url) {
      profilePictureUrl.value = url
    }
  } catch (error) {
    console.log('No profile picture')
  }

  // Load notification preferences
  try {
    const prefs = await apiClient.getNotificationPreferences()
    notificationPrefs.value = prefs
  } catch (error) {
    console.log('Using default notification preferences')
  }
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Profile Picture Functions
function triggerProfilePictureUpload() {
  profilePictureInputRef.value?.click()
}

async function handleProfilePictureSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    toast.error('Please select a valid image file (JPEG, PNG, GIF, or WebP)')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    toast.error('Image must be smaller than 5MB')
    return
  }

  isUploadingPicture.value = true
  try {
    // Get presigned upload URL
    const { upload_url, key } = await apiClient.getProfilePictureUploadUrl(file.type)

    // Upload directly to S3/R2
    await fetch(upload_url, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type
      }
    })

    // Update user record with new key
    const user = await apiClient.updateProfilePicture(key)
    authStore.setUser(user)

    // Get the download URL
    const { url } = await apiClient.getProfilePictureUrl()
    profilePictureUrl.value = url

    toast.success('Profile picture updated!')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to upload profile picture')
  } finally {
    isUploadingPicture.value = false
    if (target) target.value = ''
  }
}

async function handleDeleteProfilePicture() {
  try {
    const user = await apiClient.deleteProfilePicture()
    authStore.setUser(user)
    profilePictureUrl.value = null
    toast.success('Profile picture removed')
  } catch (error) {
    toast.error('Failed to remove profile picture')
  }
}

// Name Edit Functions
function startEditName() {
  editedName.value = authStore.user?.name || ''
  isEditingName.value = true
}

function cancelEditName() {
  isEditingName.value = false
  editedName.value = ''
}

async function saveName() {
  if (!editedName.value.trim()) {
    toast.error('Name cannot be empty')
    return
  }
  try {
    await authStore.updateUser({ name: editedName.value.trim() })
    isEditingName.value = false
    toast.success('Name updated')
  } catch (error) {
    toast.error('Failed to update name')
  }
}

// Password Change Functions
async function handleChangePassword() {
  if (newPassword.value.length < 8) {
    toast.error('New password must be at least 8 characters')
    return
  }
  if (newPassword.value !== confirmNewPassword.value) {
    toast.error('Passwords do not match')
    return
  }

  isChangingPassword.value = true
  try {
    await apiClient.changePassword(currentPassword.value, newPassword.value)
    toast.success('Password updated successfully')
    showChangePassword.value = false
    currentPassword.value = ''
    newPassword.value = ''
    confirmNewPassword.value = ''
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to change password')
  } finally {
    isChangingPassword.value = false
  }
}

// Notification Preferences Functions
async function saveNotificationPrefs() {
  try {
    await apiClient.updateNotificationPreferences(notificationPrefs.value)
    toast.success('Notification preferences saved')
  } catch (error) {
    toast.error('Failed to save notification preferences')
  }
}

// Currency Update
async function updateCurrency() {
  try {
    await authStore.updateUser({ currency: userCurrency.value })
    toast.success('Currency updated')
  } catch (error) {
    toast.error('Failed to update currency')
  }
}

// Delete Account Functions
async function handleDeleteAccount() {
  if (deleteConfirmation.value !== 'DELETE MY ACCOUNT') {
    toast.error("Please type 'DELETE MY ACCOUNT' to confirm")
    return
  }

  isDeletingAccount.value = true
  try {
    await apiClient.deleteAccount(deleteConfirmation.value, deletePassword.value || undefined)
    toast.success('Account deleted')
    authStore.logout()
    router.push({ name: 'login' })
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to delete account')
  } finally {
    isDeletingAccount.value = false
  }
}

// Import/Export Functions
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
    a.download = `sahasplit-export-${new Date().toISOString()}.json`
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

