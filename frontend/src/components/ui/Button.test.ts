import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  it('renders slot content', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click me'
      }
    })
    expect(wrapper.text()).toContain('Click me')
  })

  it('applies default variant and size', () => {
    const wrapper = mount(Button)
    expect(wrapper.classes()).toContain('bg-primary')
    expect(wrapper.classes()).toContain('h-10')
  })

  it('applies destructive variant', () => {
    const wrapper = mount(Button, {
      props: { variant: 'destructive' }
    })
    expect(wrapper.classes()).toContain('bg-destructive')
  })

  it('applies outline variant', () => {
    const wrapper = mount(Button, {
      props: { variant: 'outline' }
    })
    expect(wrapper.classes()).toContain('border')
  })

  it('applies sm size', () => {
    const wrapper = mount(Button, {
      props: { size: 'sm' }
    })
    expect(wrapper.classes()).toContain('h-9')
  })

  it('applies lg size', () => {
    const wrapper = mount(Button, {
      props: { size: 'lg' }
    })
    expect(wrapper.classes()).toContain('h-11')
  })

  it('disables button when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('disables button when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true }
    })
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })
})

