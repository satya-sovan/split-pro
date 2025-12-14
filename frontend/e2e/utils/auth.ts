import { Page, BrowserContext } from '@playwright/test';
import { config } from '../config';
import { LoginPage } from '../pages/LoginPage';

/**
 * Authentication helper utilities
 */
export class AuthHelper {
  private page: Page;
  private context: BrowserContext;

  constructor(page: Page, context: BrowserContext) {
    this.page = page;
    this.context = context;
  }

  /**
   * Login with default test user
   */
  async loginAsTestUser(): Promise<void> {
    const loginPage = new LoginPage(this.page);
    await loginPage.goto();
    await loginPage.login(config.testUser.email, config.testUser.password);

    // Wait for navigation to complete - use longer timeout
    try {
      await this.page.waitForURL(/\/home/, { timeout: 15000 });
    } catch {
      // If home URL wasn't reached, check if we're on any authenticated page
      const url = this.page.url();
      if (url.includes('/auth/login')) {
        throw new Error('Login failed - still on login page');
      }
    }

    // Wait for the page to be fully loaded
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Login with custom credentials
   */
  async login(email: string, password: string): Promise<void> {
    const loginPage = new LoginPage(this.page);
    await loginPage.goto();
    await loginPage.login(email, password);
  }

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    await this.page.goto('/account');
    await this.page.getByRole('button', { name: /log ?out|sign ?out/i }).click();
    await this.page.waitForURL(/\/auth\/login/);
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    // Check for auth token in storage
    const localStorage = await this.page.evaluate(() => window.localStorage.getItem('auth_token'));
    return !!localStorage;
  }

  /**
   * Save auth state to file
   */
  async saveAuthState(path: string): Promise<void> {
    await this.context.storageState({ path });
  }

  /**
   * Clear auth state
   */
  async clearAuth(): Promise<void> {
    await this.context.clearCookies();
    await this.page.evaluate(() => {
      window.localStorage.clear();
      window.sessionStorage.clear();
    });
  }

  /**
   * Set auth token directly (for API-based auth)
   */
  async setAuthToken(token: string): Promise<void> {
    await this.page.evaluate((t) => {
      window.localStorage.setItem('auth_token', t);
    }, token);
  }
}

/**
 * Factory function to create auth helper
 */
export function createAuthHelper(page: Page, context: BrowserContext): AuthHelper {
  return new AuthHelper(page, context);
}
