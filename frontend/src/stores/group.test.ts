import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useGroupStore } from '@/stores/group'
import { mockGroup } from '@/test/mocks'

// Mock the API client
const mockGetGroups = vi.fn()
const mockGetGroupsWithBalances = vi.fn()
const mockGetGroupDetails = vi.fn()
const mockCreateGroup = vi.fn()
const mockLeaveGroup = vi.fn()
const mockDeleteGroup = vi.fn()

vi.mock('@/services/api', () => ({
  apiClient: {
    getGroups: () => mockGetGroups(),
    getGroupsWithBalances: () => mockGetGroupsWithBalances(),
    getGroupDetails: (id: string) => mockGetGroupDetails(id),
    createGroup: (name: string, memberIds: string[]) => mockCreateGroup(name, memberIds),
    leaveGroup: (id: string) => mockLeaveGroup(id),
    deleteGroup: (id: string) => mockDeleteGroup(id)
  }
}))

describe('Group Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have empty groups initially', () => {
      const store = useGroupStore()
      expect(store.groups).toEqual([])
      expect(store.currentGroup).toBeNull()
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchGroups', () => {
    it('should fetch and store groups', async () => {
      const store = useGroupStore()
      const groups = [mockGroup(), mockGroup({ id: 2, name: 'Group 2' })]

      mockGetGroups.mockResolvedValue(groups)

      const result = await store.fetchGroups()

      expect(result).toEqual(groups)
      expect(store.groups).toEqual(groups)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch errors', async () => {
      const store = useGroupStore()

      mockGetGroups.mockRejectedValue(new Error('Network error'))

      await expect(store.fetchGroups()).rejects.toThrow('Network error')
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchGroupsWithBalances', () => {
    it('should fetch groups with balance info', async () => {
      const store = useGroupStore()
      const groups = [
        { ...mockGroup(), balances: { USD: 1000 } }
      ]

      mockGetGroupsWithBalances.mockResolvedValue(groups)

      const result = await store.fetchGroupsWithBalances()

      expect(result).toEqual(groups)
      expect(store.groups).toEqual(groups)
    })
  })

  describe('fetchGroupDetails', () => {
    it('should fetch group details and set currentGroup', async () => {
      const store = useGroupStore()
      const group = mockGroup()

      mockGetGroupDetails.mockResolvedValue(group)

      const result = await store.fetchGroupDetails('1')

      expect(result).toEqual(group)
      expect(store.currentGroup).toEqual(group)
    })
  })

  describe('createGroup', () => {
    it('should create group and add to list', async () => {
      const store = useGroupStore()
      const newGroup = mockGroup()

      mockCreateGroup.mockResolvedValue(newGroup)

      const result = await store.createGroup('New Group', [])

      expect(result).toEqual(newGroup)
      expect(store.groups).toContainEqual(newGroup)
    })
  })

  describe('leaveGroup', () => {
    it('should remove group from store after leaving', async () => {
      const store = useGroupStore()
      const group = mockGroup()

      store.groups = [group]
      mockLeaveGroup.mockResolvedValue(undefined)

      await store.leaveGroup('1')

      expect(store.groups).toEqual([])
    })

    it('should clear currentGroup if it was the left group', async () => {
      const store = useGroupStore()
      const group = mockGroup()

      store.groups = [group]
      store.currentGroup = group
      mockLeaveGroup.mockResolvedValue(undefined)

      await store.leaveGroup('1')

      expect(store.currentGroup).toBeNull()
    })
  })

  describe('deleteGroup', () => {
    it('should remove group from store after deleting', async () => {
      const store = useGroupStore()
      const group = mockGroup()

      store.groups = [group]
      mockDeleteGroup.mockResolvedValue(undefined)

      await store.deleteGroup('1')

      expect(store.groups).toEqual([])
    })
  })

  describe('local mutations', () => {
    it('should set groups', () => {
      const store = useGroupStore()
      const groups = [mockGroup()]

      store.setGroups(groups)

      expect(store.groups).toEqual(groups)
    })

    it('should add group to beginning of list', () => {
      const store = useGroupStore()
      const existingGroup = mockGroup({ id: 1 })
      const newGroup = mockGroup({ id: 2 })

      store.groups = [existingGroup]
      store.addGroup(newGroup)

      expect(store.groups[0]).toEqual(newGroup)
    })

    it('should update group in list', () => {
      const store = useGroupStore()
      const group = mockGroup()

      store.groups = [group]
      store.updateGroup(1, { name: 'Updated Name' })

      expect(store.groups[0].name).toBe('Updated Name')
    })

    it('should update currentGroup if it matches', () => {
      const store = useGroupStore()
      const group = mockGroup()

      store.groups = [group]
      store.currentGroup = group
      store.updateGroup(1, { name: 'Updated Name' })

      expect(store.currentGroup?.name).toBe('Updated Name')
    })

    it('should remove group from list', () => {
      const store = useGroupStore()
      const group = mockGroup()

      store.groups = [group]
      store.removeGroup(1)

      expect(store.groups).toEqual([])
    })
  })
})

