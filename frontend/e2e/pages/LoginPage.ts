import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { config } from '../config';

export class LoginPage extends BasePage {
  // Locators based on actual LoginView.vue
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly magicLinkButton: Locator;
  readonly registerLink: Locator;
  readonly errorMessage: Locator;
  readonly pageHeading: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.submitButton = page.locator('button[type="submit"]');
    this.magicLinkButton = page.getByRole('button', { name: /magic link/i });
    this.registerLink = page.getByRole('link', { name: /create a new account/i });
    this.errorMessage = page.locator('.text-red-600');
    this.pageHeading = page.getByRole('heading', { name: /sign in/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/auth/login');
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async loginAsTestUser(): Promise<void> {
    await this.login(config.testUser.email, config.testUser.password);
    // Wait for navigation to home
    await this.page.waitForURL(/\/home/, { timeout: 10000 });
  }

  async fillEmail(email: string): Promise<void> {
    await this.emailInput.fill(email);
  }

  async fillPassword(password: string): Promise<void> {
    await this.passwordInput.fill(password);
  }

  async clickSubmit(): Promise<void> {
    await this.submitButton.click();
  }

  // Alias for compatibility
  async submit(): Promise<void> {
    await this.clickSubmit();
  }

  async clickMagicLink(): Promise<void> {
    await this.magicLinkButton.click();
  }

  async requestMagicLink(email: string): Promise<void> {
    await this.fillEmail(email);
    await this.clickMagicLink();
  }

  async goToRegister(): Promise<void> {
    await this.registerLink.click();
  }

  async validateAccessibility(): Promise<void> {
    // Check labels are associated with inputs
    const emailLabel = this.page.locator('label[for="email"]');
    const passwordLabel = this.page.locator('label[for="password"]');

    // Labels exist (even if sr-only)
    await emailLabel.waitFor({ state: 'attached' });
    await passwordLabel.waitFor({ state: 'attached' });
  }

  async getErrorText(): Promise<string | null> {
    try {
      await this.errorMessage.waitFor({ state: 'visible', timeout: 3000 });
      return await this.errorMessage.textContent();
    } catch {
      return null;
    }
  }

  async isLoading(): Promise<boolean> {
    const buttonText = await this.submitButton.textContent();
    return buttonText?.includes('Signing in') || false;
  }

  async isDisplayed(): Promise<boolean> {
    return await this.pageHeading.isVisible();
  }
}
