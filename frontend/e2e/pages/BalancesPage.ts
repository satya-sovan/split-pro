import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Balances Page Object
 * Handles balance viewing and settlements
 */
export class BalancesPage extends BasePage {
  // Summary
  readonly totalOwed: Locator;
  readonly totalOwe: Locator;
  readonly netBalance: Locator;

  // Balance cards
  readonly balanceCards: Locator;
  readonly friendBalances: Locator;
  readonly groupBalances: Locator;

  // Actions
  readonly settleUpButton: Locator;
  readonly convertCurrencyButton: Locator;

  // Empty state
  readonly emptyState: Locator;
  readonly loadingSpinner: Locator;

  constructor(page: Page) {
    super(page);

    // Summary
    this.totalOwed = page.locator('[data-testid="total-owed"]');
    this.totalOwe = page.locator('[data-testid="total-owe"]');
    this.netBalance = page.locator('[data-testid="net-balance"]');

    // Balance cards
    this.balanceCards = page.locator('[data-testid="balance-card"]');
    this.friendBalances = page.locator('[data-testid="friend-balance"]');
    this.groupBalances = page.locator('[data-testid="group-balance"]');

    // Actions
    this.settleUpButton = page.getByRole('button', { name: /settle up/i });
    this.convertCurrencyButton = page.getByRole('button', { name: /convert/i });

    // Empty state
    this.emptyState = page.getByText(/no balances|all settled/i);
    this.loadingSpinner = page.locator('.animate-spin');
  }

  async goto(): Promise<void> {
    await this.page.goto('/balances');
    await this.waitForPageLoad();
  }

  /**
   * Wait for balances to load
   */
  async waitForLoad(): Promise<void> {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
  }

  /**
   * Get balance card count
   */
  async getBalanceCount(): Promise<number> {
    return this.balanceCards.count();
  }

  /**
   * Click on friend balance
   */
  async clickFriendBalance(friendName: string): Promise<void> {
    await this.page.getByText(friendName).click();
  }

  /**
   * Click settle up for a friend
   */
  async settleUpWithFriend(friendName: string): Promise<void> {
    const friendCard = this.page.locator(`[data-testid="friend-balance"]:has-text("${friendName}")`);
    await friendCard.getByRole('button', { name: /settle up/i }).click();
  }

  /**
   * Check if all settled
   */
  async isAllSettled(): Promise<boolean> {
    return this.emptyState.isVisible();
  }

  /**
   * Get friend balance amount
   */
  async getFriendBalanceAmount(friendName: string): Promise<string | null> {
    const friendCard = this.page.locator(`[data-testid="friend-balance"]:has-text("${friendName}")`);
    return friendCard.locator('[data-testid="balance-amount"]').textContent();
  }
}
