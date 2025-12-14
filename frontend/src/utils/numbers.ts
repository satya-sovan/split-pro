/**
 * BigInt utilities for financial calculations
 * All amounts are stored as cents (e.g., $12.50 = 1250)
 */

export class BigMath {
  static abs(n: number): number {
    return Math.abs(n)
  }

  static sign(n: number): number {
    return Math.sign(n)
  }

  static min(...args: number[]): number {
    return Math.min(...args)
  }

  static max(...args: number[]): number {
    return Math.max(...args)
  }

  static roundDiv(dividend: number, divisor: number): number {
    return Math.round(dividend / divisor)
  }
}

export interface CurrencyHelpers {
  toUIString: (value: number) => string
  toSafeBigInt: (input: string | number) => number
  format: (value: number) => string
}

export function getCurrencyHelpers(options: {
  currency: string
  locale?: string
}): CurrencyHelpers {
  const { currency, locale = 'en-US' } = options

  const formatter = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })

  return {
    toUIString(value: number): string {
      // Convert cents to dollars
      return formatter.format(value / 100)
    },
    toSafeBigInt(input: string | number): number {
      if (typeof input === 'number') {
        return Math.round(input * 100)
      }
      // Parse string input and convert to cents
      const num = parseFloat(input)
      if (isNaN(num)) return 0
      return Math.round(num * 100)
    },
    format(value: number): string {
      return formatter.format(value / 100)
    }
  }
}

export function formatCurrency(amount: number, currency: string): string {
  const helpers = getCurrencyHelpers({ currency })
  return helpers.toUIString(amount)
}

export function parseCurrencyInput(input: string): number {
  const num = parseFloat(input.replace(/[^0-9.-]/g, ''))
  if (isNaN(num)) return 0
  return Math.round(num * 100)
}

export function calculateEqualSplit(total: number, numParticipants: number): number[] {
  const baseShare = Math.floor(total / numParticipants)
  const remainder = total % numParticipants

  const shares: number[] = Array(numParticipants).fill(baseShare)

  // Distribute remainder
  for (let i = 0; i < remainder; i++) {
    shares[i]++
  }

  return shares
}

export function calculatePercentageSplit(
  total: number,
  percentages: number[]
): number[] {
  const shares = percentages.map(p => Math.round((total * p) / 100))

  // Adjust for rounding errors
  const sum = shares.reduce((a, b) => a + b, 0)
  const diff = total - sum

  if (diff !== 0) {
    shares[0] += diff
  }

  return shares
}

