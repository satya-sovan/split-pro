import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Input from '@/components/ui/Input.vue'

describe('Input', () => {
  it('renders with default type text', () => {
    const wrapper = mount(Input, {
      props: { modelValue: '' }
    })
    expect(wrapper.find('input').attributes('type')).toBe('text')
  })

  it('renders with specified type', () => {
    const wrapper = mount(Input, {
      props: { modelValue: '', type: 'email' }
    })
    expect(wrapper.find('input').attributes('type')).toBe('email')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(Input, {
      props: { modelValue: '' }
    })

    await wrapper.find('input').setValue('test value')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['test value'])
  })

  it('displays placeholder', () => {
    const wrapper = mount(Input, {
      props: { modelValue: '', placeholder: 'Enter text...' }
    })
    expect(wrapper.find('input').attributes('placeholder')).toBe('Enter text...')
  })

  it('disables input when disabled prop is true', () => {
    const wrapper = mount(Input, {
      props: { modelValue: '', disabled: true }
    })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('marks as required when required prop is true', () => {
    const wrapper = mount(Input, {
      props: { modelValue: '', required: true }
    })
    expect(wrapper.find('input').attributes('required')).toBeDefined()
  })

  it('applies error styling when error prop is true', () => {
    const wrapper = mount(Input, {
      props: { modelValue: '', error: true }
    })
    expect(wrapper.find('input').classes()).toContain('border-destructive')
  })
})

