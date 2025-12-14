import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class ExpensesPage extends BasePage {
  // Locators based on actual ExpensesView.vue
  readonly pageTitle: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;
  readonly addExpenseLink: Locator;
  readonly expenseList: Locator;
  readonly expenseCards: Locator;

  // Pagination (if exists)
  readonly paginationContainer: Locator;
  readonly prevPageButton: Locator;
  readonly nextPageButton: Locator;

  // Search/Filter
  readonly searchInput: Locator;
  readonly sortSelect: Locator;
  readonly sortButton: Locator;

  constructor(page: Page) {
    super(page);
    // Based on ExpensesView.vue
    this.pageTitle = page.getByRole('heading', { name: /all expenses/i });
    this.loadingSpinner = page.locator('.animate-spin');
    this.emptyState = page.getByText(/no expenses yet/i);
    this.addExpenseLink = page.getByRole('link', { name: /add your first expense/i });
    this.expenseList = page.locator('.space-y-3');
    this.expenseCards = page.locator('.space-y-3 > div');

    // Pagination
    this.paginationContainer = page.locator('[class*="pagination"], nav[aria-label*="pagination"]');
    this.prevPageButton = page.getByRole('button', { name: /prev|previous/i });
    this.nextPageButton = page.getByRole('button', { name: /next/i });

    // Search/Filter
    this.searchInput = page.getByPlaceholder(/search/i);
    this.sortSelect = page.locator('select').filter({ hasText: /sort/i });
    this.sortButton = page.getByRole('button', { name: /sort/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/expenses');
    await this.page.waitForLoadState('networkidle');
  }

  async waitForLoad(): Promise<void> {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
  }

  async getExpenseCount(): Promise<number> {
    await this.waitForLoad();
    return await this.expenseCards.count();
  }

  async clickFirstExpense(): Promise<void> {
    await this.expenseCards.first().click();
  }

  async hasExpenses(): Promise<boolean> {
    await this.waitForLoad();
    const count = await this.getExpenseCount();
    return count > 0;
  }

  async hasEmptyState(): Promise<boolean> {
    await this.waitForLoad();
    return await this.emptyState.isVisible();
  }

  async search(query: string): Promise<void> {
    if (await this.searchInput.isVisible()) {
      await this.searchInput.fill(query);
    }
  }

  async clearSearch(): Promise<void> {
    if (await this.searchInput.isVisible()) {
      await this.searchInput.clear();
    }
  }

  async hasNextPage(): Promise<boolean> {
    try {
      return !(await this.nextPageButton.isDisabled());
    } catch {
      return false;
    }
  }

  async hasPrevPage(): Promise<boolean> {
    try {
      return !(await this.prevPageButton.isDisabled());
    } catch {
      return false;
    }
  }

  async goToNextPage(): Promise<void> {
    await this.nextPageButton.click();
  }

  async goToPrevPage(): Promise<void> {
    await this.prevPageButton.click();
  }

  async hasPagination(): Promise<boolean> {
    try {
      return await this.paginationContainer.isVisible({ timeout: 2000 });
    } catch {
      return false;
    }
  }

  async sortBy(field: string): Promise<void> {
    if (await this.sortButton.isVisible()) {
      await this.sortButton.click();
      const option = this.page.getByRole('option', { name: new RegExp(field, 'i') });
      if (await option.isVisible()) {
        await option.click();
      }
    } else if (await this.sortSelect.isVisible()) {
      await this.sortSelect.selectOption({ label: new RegExp(field, 'i').toString() });
    }
  }

  async isDisplayed(): Promise<boolean> {
    const url = this.page.url();
    return url.includes('/expenses');
  }
}
