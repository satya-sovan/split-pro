<template>
  <div class="p-6 bg-card rounded-lg border">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold">Notes & Comments</h3>
      <span class="text-sm text-muted-foreground">{{ notes.length }} note{{ notes.length !== 1 ? 's' : '' }}</span>
    </div>

    <!-- Add Note Input -->
    <div class="mb-4">
      <div class="flex gap-2">
        <input
          v-model="newNote"
          type="text"
          placeholder="Add a note..."
          class="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          @keyup.enter="addNote"
          :disabled="isAdding"
        />
        <button
          @click="addNote"
          :disabled="!newNote.trim() || isAdding"
          class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          <SendIcon v-if="!isAdding" class="h-4 w-4" />
          <span v-else class="text-xs">...</span>
        </button>
      </div>
      <p class="text-xs text-muted-foreground mt-1">
        {{ 1000 - newNote.length }} characters remaining
      </p>
    </div>

    <!-- Notes List -->
    <div v-if="isLoading" class="text-center py-4 text-muted-foreground">
      Loading notes...
    </div>

    <div v-else-if="notes.length === 0" class="text-center py-4 text-muted-foreground">
      No notes yet. Add one above!
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="note in notes"
        :key="note.id"
        class="p-3 bg-muted/50 rounded-md"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-2">
            <div class="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden">
              <img
                v-if="note.created_by_image"
                :src="note.created_by_image"
                class="h-full w-full object-cover"
                alt=""
              />
              <span v-else class="text-sm font-medium">
                {{ note.created_by_name?.charAt(0)?.toUpperCase() || '?' }}
              </span>
            </div>
            <div>
              <span class="text-sm font-medium">{{ note.created_by_name }}</span>
              <span class="text-xs text-muted-foreground ml-2">
                {{ formatNoteDate(note.created_at) }}
              </span>
            </div>
          </div>
          <button
            v-if="canDelete(note)"
            @click="deleteNote(note.id)"
            class="p-1 hover:bg-destructive/10 rounded text-muted-foreground hover:text-destructive"
            title="Delete note"
          >
            <TrashIcon class="h-4 w-4" />
          </button>
        </div>
        <p class="mt-2 text-sm whitespace-pre-wrap">{{ note.note }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { SendIcon, TrashIcon } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { apiClient, type ExpenseNote } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatDistanceToNow, parseISO } from 'date-fns'

const props = defineProps<{
  expenseId: string
}>()

const authStore = useAuthStore()
const notes = ref<ExpenseNote[]>([])
const newNote = ref('')
const isLoading = ref(true)
const isAdding = ref(false)

onMounted(async () => {
  await loadNotes()
})

async function loadNotes() {
  isLoading.value = true
  try {
    notes.value = await apiClient.getExpenseNotes(props.expenseId)
  } catch (error) {
    console.error('Failed to load notes:', error)
  } finally {
    isLoading.value = false
  }
}

async function addNote() {
  if (!newNote.value.trim()) return

  if (newNote.value.length > 1000) {
    toast.error('Note is too long (max 1000 characters)')
    return
  }

  isAdding.value = true
  try {
    const note = await apiClient.addExpenseNote(props.expenseId, newNote.value.trim())
    notes.value.unshift(note)
    newNote.value = ''
    toast.success('Note added')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to add note')
  } finally {
    isAdding.value = false
  }
}

async function deleteNote(noteId: string) {
  if (!confirm('Delete this note?')) return

  try {
    await apiClient.deleteExpenseNote(props.expenseId, noteId)
    notes.value = notes.value.filter(n => n.id !== noteId)
    toast.success('Note deleted')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to delete note')
  }
}

function canDelete(note: ExpenseNote): boolean {
  return note.created_by_id === authStore.user?.id
}

function formatNoteDate(dateStr: string): string {
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true })
  } catch {
    return dateStr
  }
}
</script>

