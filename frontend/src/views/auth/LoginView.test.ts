import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoginView from '@/views/auth/LoginView.vue'

// Mock vue-sonner
vi.mock('vue-sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn()
  }),
  useRoute: () => ({
    params: {},
    query: {},
    path: '/auth/login'
  }),
  RouterLink: {
    template: '<a><slot /></a>',
    props: ['to']
  }
}))

// Mock auth store
const mockLogin = vi.fn()
const mockSendMagicLink = vi.fn()

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    login: mockLogin,
    sendMagicLink: mockSendMagicLink,
    isAuthenticated: false,
    isLoading: false
  })
}))

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders login form', async () => {
    const wrapper = mount(LoginView, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('calls login with credentials', async () => {
    mockLogin.mockResolvedValue(true)

    const wrapper = mount(LoginView, {
      global: {
        stubs: {
          RouterLink: true
        }
      }
    })

    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('displays error on login failure', async () => {
    mockLogin.mockResolvedValue(false)

    const wrapper = mount(LoginView, {
      global: {
        stubs: {
          RouterLink: true
        }
      }
    })

    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('wrongpassword')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Invalid')
  })

  it('has link to register page', () => {
    const wrapper = mount(LoginView, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    // Check for "Or" text that links to registration
    expect(wrapper.text()).toContain('Or')
  })

  it('has magic link option', () => {
    const wrapper = mount(LoginView, {
      global: {
        stubs: {
          RouterLink: true
        }
      }
    })

    expect(wrapper.text()).toContain('magic link')
  })

  it('navigates to home on successful login', async () => {
    mockLogin.mockResolvedValue(true)

    const wrapper = mount(LoginView, {
      global: {
        stubs: {
          RouterLink: true
        }
      }
    })

    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(mockPush).toHaveBeenCalledWith('/home')
  })
})

