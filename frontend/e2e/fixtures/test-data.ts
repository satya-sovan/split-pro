/**
 * Test data fixtures for E2E tests
 */

export const testExpenses = [
  {
    id: 1,
    name: 'Dinner at Restaurant',
    amount: 12500, // $125.00 in cents
    currency: 'USD',
    category: 'food',
    date: '2024-12-10',
    paid_by: 1,
    split_type: 'EQUAL'
  },
  {
    id: 2,
    name: 'Uber Ride',
    amount: 2350,
    currency: 'USD',
    category: 'transport',
    date: '2024-12-09',
    paid_by: 1,
    split_type: 'EQUAL'
  },
  {
    id: 3,
    name: 'Groceries',
    amount: 8799,
    currency: 'USD',
    category: 'groceries',
    date: '2024-12-08',
    paid_by: 2,
    split_type: 'EXACT'
  }
];

export const testGroups = [
  {
    id: 1,
    name: 'Roommates',
    member_count: 3,
    created_at: '2024-01-01',
    balances: [
      { currency: 'USD', amount: 5000 }
    ]
  },
  {
    id: 2,
    name: 'Trip to Paris',
    member_count: 4,
    created_at: '2024-06-15',
    balances: [
      { currency: 'EUR', amount: -2500 }
    ]
  }
];

export const testUsers = [
  {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    currency: 'USD'
  },
  {
    id: 2,
    name: 'Jane Doe',
    email: 'jane@example.com',
    currency: 'USD'
  },
  {
    id: 3,
    name: 'John Smith',
    email: 'john@example.com',
    currency: 'EUR'
  }
];

export const testBalances = [
  {
    friend_id: 2,
    friend_name: 'Jane Doe',
    currency: 'USD',
    amount: 2500 // User is owed $25.00
  },
  {
    friend_id: 3,
    friend_name: 'John Smith',
    currency: 'USD',
    amount: -1500 // User owes $15.00
  }
];

export const categories = [
  { id: 'food', name: 'Food & Drink', icon: '🍔' },
  { id: 'transport', name: 'Transport', icon: '🚗' },
  { id: 'groceries', name: 'Groceries', icon: '🛒' },
  { id: 'entertainment', name: 'Entertainment', icon: '🎬' },
  { id: 'utilities', name: 'Utilities', icon: '💡' },
  { id: 'rent', name: 'Rent', icon: '🏠' },
  { id: 'other', name: 'Other', icon: '📦' }
];

export const currencies = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' }
];

/**
 * Generate mock API response for expenses
 */
export function mockExpensesResponse(expenses = testExpenses) {
  return {
    data: expenses,
    total: expenses.length,
    page: 1,
    per_page: 20
  };
}

/**
 * Generate mock API response for groups
 */
export function mockGroupsResponse(groups = testGroups) {
  return {
    data: groups,
    total: groups.length
  };
}

/**
 * Generate mock API response for balances
 */
export function mockBalancesResponse(balances = testBalances) {
  return {
    data: balances,
    total_owed: balances.filter((b) => b.amount > 0).reduce((sum, b) => sum + b.amount, 0),
    total_owe: balances.filter((b) => b.amount < 0).reduce((sum, b) => sum + Math.abs(b.amount), 0)
  };
}

/**
 * Generate mock user data
 */
export function mockUserResponse(user = testUsers[0]) {
  return {
    ...user,
    created_at: '2024-01-01',
    updated_at: '2024-12-01'
  };
}

