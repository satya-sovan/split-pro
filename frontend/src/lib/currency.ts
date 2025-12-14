export const CURRENCIES = [
  'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
  'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'RUB', 'INR', 'BRL', 'ZAR'
] as const

export type CurrencyCode = typeof CURRENCIES[number]

export function isCurrencyCode(code: string): code is CurrencyCode {
  return CURRENCIES.includes(code as CurrencyCode)
}

export function getCurrencySymbol(currency: CurrencyCode): string {
  const symbols: Record<string, string> = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    AUD: 'A$',
    CAD: 'C$',
    CHF: 'Fr',
    CNY: '¥',
    SEK: 'kr',
    NZD: 'NZ$',
    INR: '₹',
    BRL: 'R$'
  }
  return symbols[currency] || currency
}

