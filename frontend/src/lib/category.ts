export const CATEGORIES = [
  { id: 'food', label: 'Food & Drink', icon: '🍔' },
  { id: 'transport', label: 'Transportation', icon: '🚗' },
  { id: 'shopping', label: 'Shopping', icon: '🛍️' },
  { id: 'entertainment', label: 'Entertainment', icon: '🎬' },
  { id: 'home', label: 'Home', icon: '🏠' },
  { id: 'utilities', label: 'Utilities', icon: '💡' },
  { id: 'healthcare', label: 'Healthcare', icon: '⚕️' },
  { id: 'education', label: 'Education', icon: '📚' },
  { id: 'travel', label: 'Travel', icon: '✈️' },
  { id: 'other', label: 'Other', icon: '📝' }
] as const

export type CategoryId = typeof CATEGORIES[number]['id']

export function getCategoryLabel(id: string): string {
  const category = CATEGORIES.find(c => c.id === id)
  return category?.label || 'Other'
}

export function getCategoryIcon(id: string): string {
  const category = CATEGORIES.find(c => c.id === id)
  return category?.icon || '📝'
}

