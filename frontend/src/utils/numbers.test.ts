import { describe, it, expect } from 'vitest'
import {
  BigMath,
  getCurrencyHelpers,
  formatCurrency,
  parseCurrencyInput,
  calculateEqualSplit,
  calculatePercentageSplit
} from '@/utils/numbers'

describe('BigMath', () => {
  describe('abs', () => {
    it('should return absolute value', () => {
      expect(BigMath.abs(-100)).toBe(100)
      expect(BigMath.abs(100)).toBe(100)
      expect(BigMath.abs(0)).toBe(0)
    })
  })

  describe('sign', () => {
    it('should return sign of number', () => {
      expect(BigMath.sign(-100)).toBe(-1)
      expect(BigMath.sign(100)).toBe(1)
      expect(BigMath.sign(0)).toBe(0)
    })
  })

  describe('min', () => {
    it('should return minimum value', () => {
      expect(BigMath.min(1, 2, 3)).toBe(1)
      expect(BigMath.min(-5, 0, 5)).toBe(-5)
    })
  })

  describe('max', () => {
    it('should return maximum value', () => {
      expect(BigMath.max(1, 2, 3)).toBe(3)
      expect(BigMath.max(-5, 0, 5)).toBe(5)
    })
  })

  describe('roundDiv', () => {
    it('should divide and round correctly', () => {
      expect(BigMath.roundDiv(10, 3)).toBe(3)
      expect(BigMath.roundDiv(11, 3)).toBe(4)
      expect(BigMath.roundDiv(100, 4)).toBe(25)
    })
  })
})

describe('getCurrencyHelpers', () => {
  const usdHelpers = getCurrencyHelpers({ currency: 'USD', locale: 'en-US' })
  const eurHelpers = getCurrencyHelpers({ currency: 'EUR', locale: 'de-DE' })

  describe('toUIString', () => {
    it('should format cents to currency string', () => {
      expect(usdHelpers.toUIString(1000)).toContain('10')
      expect(usdHelpers.toUIString(0)).toContain('0')
      expect(usdHelpers.toUIString(9999)).toContain('99.99')
    })
  })

  describe('toSafeBigInt', () => {
    it('should convert string input to cents', () => {
      expect(usdHelpers.toSafeBigInt('10.00')).toBe(1000)
      expect(usdHelpers.toSafeBigInt('99.99')).toBe(9999)
      expect(usdHelpers.toSafeBigInt('0.01')).toBe(1)
    })

    it('should convert number input to cents', () => {
      expect(usdHelpers.toSafeBigInt(10)).toBe(1000)
      expect(usdHelpers.toSafeBigInt(99.99)).toBe(9999)
    })

    it('should handle invalid input', () => {
      expect(usdHelpers.toSafeBigInt('invalid')).toBe(0)
      expect(usdHelpers.toSafeBigInt('')).toBe(0)
    })
  })

  describe('format', () => {
    it('should format value with currency symbol', () => {
      expect(usdHelpers.format(1000)).toContain('10')
    })
  })
})

describe('formatCurrency', () => {
  it('should format amount with currency', () => {
    expect(formatCurrency(1000, 'USD')).toContain('10')
    expect(formatCurrency(5000, 'EUR')).toContain('50')
  })

  it('should handle zero amount', () => {
    expect(formatCurrency(0, 'USD')).toContain('0')
  })

  it('should handle negative amounts', () => {
    const result = formatCurrency(-1000, 'USD')
    expect(result).toContain('10')
  })
})

describe('parseCurrencyInput', () => {
  it('should parse string to cents', () => {
    expect(parseCurrencyInput('10.00')).toBe(1000)
    expect(parseCurrencyInput('99.99')).toBe(9999)
    expect(parseCurrencyInput('0.01')).toBe(1)
  })

  it('should handle input with currency symbols', () => {
    expect(parseCurrencyInput('$10.00')).toBe(1000)
    expect(parseCurrencyInput('€50.00')).toBe(5000)
  })

  it('should handle invalid input', () => {
    expect(parseCurrencyInput('')).toBe(0)
    expect(parseCurrencyInput('invalid')).toBe(0)
  })
})

describe('calculateEqualSplit', () => {
  it('should split evenly', () => {
    const result = calculateEqualSplit(1000, 2)
    expect(result).toEqual([500, 500])
  })

  it('should distribute remainder to first participants', () => {
    const result = calculateEqualSplit(1000, 3)
    expect(result).toEqual([334, 333, 333])
  })

  it('should handle single participant', () => {
    const result = calculateEqualSplit(1000, 1)
    expect(result).toEqual([1000])
  })

  it('should handle large number of participants', () => {
    const result = calculateEqualSplit(10, 3)
    expect(result.reduce((a, b) => a + b, 0)).toBe(10)
  })
})

describe('calculatePercentageSplit', () => {
  it('should split by percentage', () => {
    const result = calculatePercentageSplit(1000, [50, 50])
    expect(result).toEqual([500, 500])
  })

  it('should handle unequal percentages', () => {
    const result = calculatePercentageSplit(1000, [70, 30])
    expect(result).toEqual([700, 300])
  })
})

