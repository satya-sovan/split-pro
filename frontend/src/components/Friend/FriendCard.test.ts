import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FriendCard from '@/components/Friend/FriendCard.vue'
import { mockFriend } from '@/test/mocks'

describe('FriendCard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders friend name', () => {
    const friend = mockFriend({ user: { id: 2, name: 'Jane Doe', email: 'jane@example.com' } })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('Jane Doe')
  })

  it('renders friend email', () => {
    const friend = mockFriend({ user: { id: 2, name: 'Jane', email: 'jane@example.com' } })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('jane@example.com')
  })

  it('shows positive balance as "owes you"', () => {
    const friend = mockFriend({
      balances: [{ currency: 'USD', amount: 2500 }]
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('owes you')
    expect(wrapper.text()).toContain('25')
  })

  it('shows negative balance as "you owe"', () => {
    const friend = mockFriend({
      balances: [{ currency: 'USD', amount: -1500 }]
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('you owe')
    expect(wrapper.text()).toContain('15')
  })

  it('shows zero balance as "settled"', () => {
    const friend = mockFriend({
      balances: [{ currency: 'USD', amount: 0 }]
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('settled')
  })

  it('shows "Settled up" when no balances', () => {
    const friend = mockFriend({
      balances: []
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('Settled up')
  })

  it('shows multiple currency balances', () => {
    const friend = mockFriend({
      balances: [
        { currency: 'USD', amount: 2500 },
        { currency: 'EUR', amount: 1000 }
      ]
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.text()).toContain('25')
    expect(wrapper.text()).toContain('10')
  })

  it('emits click event when clicked', async () => {
    const friend = mockFriend()

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    await wrapper.trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('applies correct color for positive balance', () => {
    const friend = mockFriend({
      balances: [{ currency: 'USD', amount: 2500 }]
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.find('.text-green-600').exists()).toBe(true)
  })

  it('applies correct color for negative balance', () => {
    const friend = mockFriend({
      balances: [{ currency: 'USD', amount: -2500 }]
    })

    const wrapper = mount(FriendCard, {
      props: { friend }
    })

    expect(wrapper.find('.text-red-600').exists()).toBe(true)
  })
})

