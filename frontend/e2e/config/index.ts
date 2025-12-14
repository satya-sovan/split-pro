export const config = {
  baseUrl: process.env.BASE_URL || 'http://localhost:8012',

  testUser: {
    email: process.env.TEST_USER_EMAIL || 'test@swaya.org',
    password: process.env.TEST_USER_PASSWORD || 'test12345',
    name: process.env.TEST_USER_NAME || 'Test User'
  },

  invalidUser: {
    email: 'invalid@example.com',
    password: 'wrongpassword'
  },

  timeouts: {
    short: 5000,
    medium: 10000,
    long: 30000
  },

  api: {
    baseUrl: process.env.API_URL || 'http://localhost:8000',
    endpoints: {
      login: '/api/v1/auth/login',
      register: '/api/v1/auth/register',
      expenses: '/api/v1/expenses',
      groups: '/api/v1/groups',
      balances: '/api/v1/balances',
      users: '/api/v1/users'
    }
  }
} as const;

