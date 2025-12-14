import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class RegisterPage extends BasePage {
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly loginLink: Locator;
  readonly pageHeading: Locator;

  constructor(page: Page) {
    super(page);
    this.nameInput = page.getByLabel('Name');
    this.emailInput = page.getByLabel('Email address');
    this.passwordInput = page.getByLabel('Password', { exact: true });
    this.confirmPasswordInput = page.getByLabel('Confirm password');
    this.submitButton = page.getByRole('button', { name: /create account|sign up|register/i });
    this.errorMessage = page.locator('.text-red-600, .text-destructive');
    this.loginLink = page.getByRole('link', { name: /sign in|login/i });
    this.pageHeading = page.getByRole('heading', { name: /create.*account|register|sign up/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/auth/register');
    await this.waitForPageLoad();
  }

  async fillForm(name: string, email: string, password: string, confirmPassword?: string): Promise<void> {
    await this.nameInput.fill(name);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    if (this.confirmPasswordInput && confirmPassword) {
      await this.confirmPasswordInput.fill(confirmPassword);
    }
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async register(name: string, email: string, password: string, confirmPassword?: string): Promise<void> {
    await this.fillForm(name, email, password, confirmPassword || password);
    await this.submit();
  }

  async getErrorText(): Promise<string | null> {
    if (await this.errorMessage.isVisible()) {
      return this.errorMessage.textContent();
    }
    return null;
  }

  async goToLogin(): Promise<void> {
    await this.loginLink.click();
  }

  async isDisplayed(): Promise<boolean> {
    return this.pageHeading.isVisible();
  }
}

