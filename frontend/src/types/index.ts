// All types used throughout the frontend, matching backend schemas

export interface User {
  id: number
  email: string | null
  name: string | null
  image: string | null
  currency: string
  preferred_language: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export type SplitType = 'EQUAL' | 'PERCENTAGE' | 'SHARE' | 'EXACT' | 'ADJUSTMENT' | 'SETTLEMENT' | 'CURRENCY_CONVERSION'

export interface ExpenseParticipant {
  user_id: number
  amount: number
  user_name?: string
}

export interface ExpenseCreate {
  expense_id?: string
  group_id?: number
  paid_by: number
  name: string
  category: string
  amount: number
  split_type: SplitType
  currency: string
  participants: ExpenseParticipant[]
  expense_date?: string
  file_key?: string
  transaction_id?: string
  recurrence_id?: number
}

export interface Expense {
  id: string
  group_id: number | null
  paid_by: number
  name: string
  category: string
  amount: number
  split_type: SplitType
  currency: string
  expense_date: string
  created_at: string
  updated_at: string
  file_key: string | null
  deleted_at: string | null
  conversion_to_id: string | null
}

export interface ExpenseDetail extends Expense {
  participants: ExpenseParticipant[]
  paid_by_user?: User
}

export interface Balance {
  user_id: number
  friend_id: number
  group_id: number | null
  currency: string
  amount: number
}

export interface CurrencyAmount {
  currency: string
  amount: number
}

export interface Friend {
  user: User
  total_balance: number
  balances: CurrencyAmount[]
}

export interface BalanceSummary {
  youOwe: CurrencyAmount[]
  youGet: CurrencyAmount[]
  balances: Friend[]
}

export interface Group {
  id: number
  public_id: string
  name: string
  user_id: number
  default_currency: string
  simplify_debts: boolean
  created_at: string
  updated_at: string
  archived_at: string | null
}

export interface GroupMember extends User {}

export interface GroupDetail extends Group {
  members: GroupMember[]
  recent_expenses: Expense[]
}

export interface GroupWithBalance {
  id: number
  name: string
  public_id: string
  default_currency: string
  balances: Record<string, number>
  archived_at: string | null
}

export interface GroupBalance {
  user_id: number
  friend_id: number
  currency: string
  amount: number
}

export interface BankInstitution {
  id: string
  name: string
  logo?: string
  country: string
}

export interface BankTransaction {
  id: string
  amount: number
  currency: string
  description: string
  date: string
  merchant_name?: string
  category?: string
  imported?: boolean
}

export interface RecurringExpense {
  id: number
  expense_id: string
  job_id: string | null
  schedule: string | null
}

export interface CurrencyRate {
  rate: number
  from: string
  to: string
  date: string
}

// Form types for UI components
export interface ExpenseFormData {
  name: string
  amount: string
  currency: string
  category: string
  date: string
  paid_by: number
  split_type: SplitType
  participants: ParticipantFormData[]
  group_id?: number
  file_key?: string
}

export interface ParticipantFormData {
  user_id: number
  user_name: string
  amount: string
  percentage?: string
  shares?: number
  selected: boolean
}

export interface GroupFormData {
  name: string
  default_currency: string
  simplify_debts: boolean
}

export interface SettleUpFormData {
  friend_id: number
  amount: string
  currency: string
  group_id?: number
}

export interface SearchFriendResult {
  id: number
  name: string
  email: string
  image?: string
}

// Splitwise Import Types (CSV-based import)
export interface SplitwiseImportStats {
  groups_imported: number
  friends_imported: number
  balances_imported: number
  expenses_imported: number
  rows_processed: number
  errors: string[]
}

export interface SplitwiseImportResult {
  success: boolean
  message?: string
  statistics: SplitwiseImportStats
}

