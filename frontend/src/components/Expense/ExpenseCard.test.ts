import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ExpenseCard from '@/components/Expense/ExpenseCard.vue'
import { mockExpense } from '@/test/mocks'

// Mock vue-sonner
vi.mock('vue-sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

describe('ExpenseCard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders expense name', () => {
    const expense = mockExpense({ name: 'Dinner at Restaurant' })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    expect(wrapper.text()).toContain('Dinner at Restaurant')
  })

  it('renders expense amount', () => {
    const expense = mockExpense({ amount: 5000, currency: 'USD' })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    // Amount should be displayed as $50.00 (5000 cents)
    expect(wrapper.text()).toContain('50')
  })

  it('renders category icon', () => {
    const expense = mockExpense({ category: 'food' })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    // Food category icon is 🍔
    expect(wrapper.text()).toContain('🍔')
  })

  it('renders paidBy name', () => {
    const expense = mockExpense({ paidBy: { id: 1, name: 'John Doe' } })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    expect(wrapper.text()).toContain('John Doe')
  })

  it('renders participant count', () => {
    const expense = mockExpense({
      participants: [
        { userId: 1, userName: 'User 1', amount: 1000 },
        { userId: 2, userName: 'User 2', amount: 1000 },
        { userId: 3, userName: 'User 3', amount: 1000 }
      ]
    })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    expect(wrapper.text()).toContain('3 participants')
  })

  it('renders singular participant text', () => {
    const expense = mockExpense({
      participants: [
        { userId: 1, userName: 'User 1', amount: 5000 }
      ]
    })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    expect(wrapper.text()).toContain('1 participant')
  })

  it('renders group name when in group', () => {
    const expense = mockExpense({ groupName: 'Trip to Paris' })

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    expect(wrapper.text()).toContain('Trip to Paris')
  })

  it('emits click event when clicked', async () => {
    const expense = mockExpense()

    const wrapper = mount(ExpenseCard, {
      props: { expense }
    })

    await wrapper.trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
  })
})

