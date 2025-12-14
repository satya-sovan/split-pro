import { describe, it, expect } from 'vitest'
import { CURRENCIES, isCurrencyCode, getCurrencySymbol } from '@/lib/currency'

describe('Currency utils', () => {
  describe('CURRENCIES', () => {
    it('has major currencies', () => {
      expect(CURRENCIES).toContain('USD')
      expect(CURRENCIES).toContain('EUR')
      expect(CURRENCIES).toContain('GBP')
      expect(CURRENCIES).toContain('JPY')
      expect(CURRENCIES).toContain('AUD')
      expect(CURRENCIES).toContain('CAD')
    })

    it('has all currencies as 3-letter codes', () => {
      for (const currency of CURRENCIES) {
        expect(currency).toHaveLength(3)
        expect(currency).toBe(currency.toUpperCase())
      }
    })
  })

  describe('isCurrencyCode', () => {
    it('returns true for valid currency codes', () => {
      expect(isCurrencyCode('USD')).toBe(true)
      expect(isCurrencyCode('EUR')).toBe(true)
      expect(isCurrencyCode('GBP')).toBe(true)
    })

    it('returns false for invalid currency codes', () => {
      expect(isCurrencyCode('XXX')).toBe(false)
      expect(isCurrencyCode('USDD')).toBe(false)
      expect(isCurrencyCode('us')).toBe(false)
    })
  })

  describe('getCurrencySymbol', () => {
    it('returns correct symbols for major currencies', () => {
      expect(getCurrencySymbol('USD')).toBe('$')
      expect(getCurrencySymbol('EUR')).toBe('€')
      expect(getCurrencySymbol('GBP')).toBe('£')
      expect(getCurrencySymbol('JPY')).toBe('¥')
      expect(getCurrencySymbol('INR')).toBe('₹')
    })

    it('returns currency code for unknown currencies', () => {
      expect(getCurrencySymbol('MXN')).toBe('MXN')
    })
  })
})

