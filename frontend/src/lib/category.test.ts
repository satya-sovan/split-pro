import { describe, it, expect } from 'vitest'
import { CATEGORIES, getCategoryLabel, getCategoryIcon } from '@/lib/category'

describe('Category utils', () => {
  describe('CATEGORIES', () => {
    it('has required categories', () => {
      const ids = CATEGORIES.map(c => c.id)
      expect(ids).toContain('food')
      expect(ids).toContain('transport')
      expect(ids).toContain('shopping')
      expect(ids).toContain('entertainment')
      expect(ids).toContain('home')
      expect(ids).toContain('utilities')
      expect(ids).toContain('healthcare')
      expect(ids).toContain('education')
      expect(ids).toContain('travel')
      expect(ids).toContain('other')
    })

    it('each category has id, label, and icon', () => {
      for (const category of CATEGORIES) {
        expect(category.id).toBeDefined()
        expect(category.label).toBeDefined()
        expect(category.icon).toBeDefined()
      }
    })
  })

  describe('getCategoryLabel', () => {
    it('returns correct label for known category', () => {
      expect(getCategoryLabel('food')).toBe('Food & Drink')
      expect(getCategoryLabel('transport')).toBe('Transportation')
      expect(getCategoryLabel('travel')).toBe('Travel')
    })

    it('returns Other for unknown category', () => {
      expect(getCategoryLabel('unknown')).toBe('Other')
      expect(getCategoryLabel('')).toBe('Other')
    })
  })

  describe('getCategoryIcon', () => {
    it('returns correct icon for known category', () => {
      expect(getCategoryIcon('food')).toBe('🍔')
      expect(getCategoryIcon('transport')).toBe('🚗')
      expect(getCategoryIcon('travel')).toBe('✈️')
    })

    it('returns default icon for unknown category', () => {
      expect(getCategoryIcon('unknown')).toBe('📝')
      expect(getCategoryIcon('')).toBe('📝')
    })
  })
})

