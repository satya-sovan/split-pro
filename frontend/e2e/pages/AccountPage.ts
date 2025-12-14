import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Account Page Object
 * Handles user account settings and profile
 */
export class AccountPage extends BasePage {
  // Locators based on actual AccountView.vue
  readonly userAvatar: Locator;
  readonly userName: Locator;
  readonly userEmail: Locator;
  readonly currencySelect: Locator;
  readonly languageSelect: Locator;
  readonly exportDataButton: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);
    // User info
    this.userAvatar = page.locator('.h-16.w-16.rounded-full');
    this.userName = page.locator('.text-xl.font-bold');
    this.userEmail = page.locator('.text-muted-foreground').first();

    // Settings
    this.currencySelect = page.locator('#currency');
    this.languageSelect = page.locator('#language');

    // Actions - based on AccountView.vue - the logout button has destructive styling
    this.exportDataButton = page.locator('button').filter({ hasText: /export data/i });
    this.logoutButton = page.getByText('Logout').locator('..');
  }

  async goto(): Promise<void> {
    await this.page.goto('/account');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get user name
   */
  async getUserName(): Promise<string> {
    return (await this.userName.textContent()) || '';
  }

  /**
   * Get user email
   */
  async getUserEmail(): Promise<string> {
    return (await this.userEmail.textContent()) || '';
  }

  /**
   * Change currency
   */
  async selectCurrency(currency: string): Promise<void> {
    await this.currencySelect.selectOption(currency);
  }

  /**
   * Change language
   */
  async selectLanguage(language: string): Promise<void> {
    await this.languageSelect.selectOption(language);
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    await this.logoutButton.click();
  }

  /**
   * Export user data
   */
  async exportData(): Promise<void> {
    await this.exportDataButton.click();
  }

  /**
   * Check if Account page is displayed
   */
  async isDisplayed(): Promise<boolean> {
    const url = this.page.url();
    return url.includes('/account');
  }
}
