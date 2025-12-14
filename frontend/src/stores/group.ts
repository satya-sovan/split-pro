import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/services/api'

interface GroupMember {
  id: number
  name: string
  email: string
  image?: string
  currency?: string
  preferred_language?: string
}

interface GroupBalance {
  currency: string
  amount: number
}

interface Group {
  id: number
  name: string
  description?: string
  currency: string
  createdBy: number
  members: GroupMember[]
  balances?: GroupBalance[]
  createdAt: string
  updatedAt?: string
}

export const useGroupStore = defineStore('group', () => {
  const groups = ref<Group[]>([])
  const currentGroup = ref<Group | null>(null)
  const loading = ref(false)

  function setGroups(newGroups: Group[]) {
    groups.value = newGroups
  }

  function setCurrentGroup(group: Group | null) {
    currentGroup.value = group
  }

  function addGroup(group: Group) {
    groups.value.unshift(group)
  }

  function updateGroup(id: number, updates: Partial<Group>) {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value[index] = { ...groups.value[index], ...updates }
    }
    if (currentGroup.value?.id === id) {
      currentGroup.value = { ...currentGroup.value, ...updates }
    }
  }

  function removeGroup(id: number) {
    groups.value = groups.value.filter(g => g.id !== id)
    if (currentGroup.value?.id === id) {
      currentGroup.value = null
    }
  }

  async function fetchGroups() {
    loading.value = true
    try {
      const data = await apiClient.getGroups()
      groups.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchGroupsWithBalances() {
    loading.value = true
    try {
      const data = await apiClient.getGroupsWithBalances()
      groups.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchGroupDetails(groupId: string) {
    loading.value = true
    try {
      const data = await apiClient.getGroupDetails(groupId)
      currentGroup.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function createGroup(name: string, memberIds: string[]) {
    loading.value = true
    try {
      const data = await apiClient.createGroup(name, memberIds)
      addGroup(data)
      return data
    } finally {
      loading.value = false
    }
  }

  async function leaveGroup(groupId: string) {
    loading.value = true
    try {
      await apiClient.leaveGroup(groupId)
      removeGroup(parseInt(groupId))
    } finally {
      loading.value = false
    }
  }

  async function deleteGroup(groupId: string) {
    loading.value = true
    try {
      await apiClient.deleteGroup(groupId)
      removeGroup(parseInt(groupId))
    } finally {
      loading.value = false
    }
  }

  return {
    groups,
    currentGroup,
    loading,
    setGroups,
    setCurrentGroup,
    addGroup,
    updateGroup,
    removeGroup,
    fetchGroups,
    fetchGroupsWithBalances,
    fetchGroupDetails,
    createGroup,
    leaveGroup,
    deleteGroup
  }
})

