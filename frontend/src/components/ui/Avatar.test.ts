import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Avatar from '@/components/ui/Avatar.vue'

describe('Avatar', () => {
  it('displays initials when no src provided', () => {
    const wrapper = mount(Avatar, {
      props: { name: 'John Doe' }
    })
    expect(wrapper.text()).toContain('JD')
  })

  it('displays single initial for single name', () => {
    const wrapper = mount(Avatar, {
      props: { name: 'John' }
    })
    expect(wrapper.text()).toContain('J')
  })

  it('displays ? when no name provided', () => {
    const wrapper = mount(Avatar)
    expect(wrapper.text()).toContain('?')
  })

  it('renders image when src provided', () => {
    const wrapper = mount(Avatar, {
      props: { src: 'https://example.com/avatar.jpg', name: 'John' }
    })
    expect(wrapper.find('img').exists()).toBe(true)
    expect(wrapper.find('img').attributes('src')).toBe('https://example.com/avatar.jpg')
  })

  it('applies correct size class for md', () => {
    const wrapper = mount(Avatar, {
      props: { name: 'John', size: 'md' }
    })
    expect(wrapper.classes()).toContain('h-10')
    expect(wrapper.classes()).toContain('w-10')
  })

  it('applies correct size class for lg', () => {
    const wrapper = mount(Avatar, {
      props: { name: 'John', size: 'lg' }
    })
    expect(wrapper.classes()).toContain('h-12')
    expect(wrapper.classes()).toContain('w-12')
  })

  it('generates consistent color from name', () => {
    const wrapper1 = mount(Avatar, {
      props: { name: 'John Doe' }
    })
    const wrapper2 = mount(Avatar, {
      props: { name: 'John Doe' }
    })

    const style1 = wrapper1.find('div > div').attributes('style')
    const style2 = wrapper2.find('div > div').attributes('style')

    expect(style1).toBe(style2)
  })
})

