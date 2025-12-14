import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  // Locators based on actual HomeView.vue
  readonly welcomeHeading: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;

  // Quick action cards
  readonly addExpenseCard: Locator;
  readonly balancesCard: Locator;
  readonly groupsCard: Locator;

  // Recent expenses section
  readonly recentExpensesHeading: Locator;
  readonly viewAllLink: Locator;
  readonly viewAllExpensesLink: Locator; // Alias
  readonly expenseCards: Locator;

  // Bottom navigation (from MainLayout.vue)
  readonly bottomNav: Locator;
  readonly homeNavLink: Locator;
  readonly balancesNavLink: Locator;
  readonly addNavLink: Locator;
  readonly groupsNavLink: Locator;
  readonly accountNavLink: Locator;

  constructor(page: Page) {
    super(page);
    // Main content
    this.welcomeHeading = page.getByRole('heading', { name: /welcome/i, level: 1 });
    this.loadingSpinner = page.locator('.animate-spin');
    this.emptyState = page.getByText(/no expenses yet/i);

    // Action cards - based on actual router-links in HomeView.vue
    this.addExpenseCard = page.locator('a[href="/add"]').filter({ hasText: /add expense/i });
    this.balancesCard = page.locator('a[href="/balances"]').filter({ hasText: /balances/i });
    this.groupsCard = page.locator('a[href="/groups"]').filter({ hasText: /groups/i });

    // Recent expenses
    this.recentExpensesHeading = page.getByRole('heading', { name: /recent expenses/i });
    this.viewAllLink = page.getByRole('link', { name: /view all/i });
    this.viewAllExpensesLink = this.viewAllLink; // Alias
    this.expenseCards = page.locator('[class*="expense-card"], .space-y-3 > div');

    // Bottom navigation - try multiple selectors for flexibility
    this.bottomNav = page.locator('nav.fixed, nav[class*="fixed"], [class*="bottom"][class*="nav"]');
    this.homeNavLink = page.locator('a[href="/home"]').last();
    this.balancesNavLink = page.locator('a[href="/balances"]').last();
    this.addNavLink = page.locator('a[href="/add"]').last();
    this.groupsNavLink = page.locator('a[href="/groups"]').last();
    this.accountNavLink = page.locator('a[href="/account"]').last();
  }

  async goto(): Promise<void> {
    await this.page.goto('/home');
  }

  async waitForLoad(): Promise<void> {
    // Wait for either welcome heading or loading spinner to disappear
    await this.page.waitForLoadState('networkidle');
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
  }

  async goToAddExpense(): Promise<void> {
    await this.addExpenseCard.click();
  }

  async goToBalances(): Promise<void> {
    await this.balancesCard.click();
  }

  async goToGroups(): Promise<void> {
    await this.groupsCard.click();
  }

  async goToAllExpenses(): Promise<void> {
    await this.viewAllLink.click();
  }

  async getRecentExpensesCount(): Promise<number> {
    await this.page.waitForTimeout(500);
    return await this.expenseCards.count();
  }

  // Alias for compatibility
  async getRecentExpenseCount(): Promise<number> {
    return await this.getRecentExpensesCount();
  }

  async hasEmptyState(): Promise<boolean> {
    const emptyIndicators = this.page.locator('.text-muted, [class*="empty"], .text-gray-500');
    try {
      return await emptyIndicators.first().isVisible({ timeout: 2000 });
    } catch {
      return false;
    }
  }

  async navigateViaBottomNav(destination: 'home' | 'balances' | 'add' | 'groups' | 'account'): Promise<void> {
    const navMap = {
      home: this.homeNavLink,
      balances: this.balancesNavLink,
      add: this.addNavLink,
      groups: this.groupsNavLink,
      account: this.accountNavLink
    };
    await navMap[destination].click();
  }

  async getActiveNavItem(): Promise<string> {
    const navItems = ['home', 'balances', 'groups', 'account'];
    for (const item of navItems) {
      const link = this.page.locator(`a[href="/${item}"]`).last();
      try {
        const classes = await link.getAttribute('class', { timeout: 2000 });
        if (classes?.includes('text-primary')) {
          return item;
        }
      } catch {
        continue;
      }
    }
    return '';
  }

  async isDisplayed(): Promise<boolean> {
    try {
      // Check if we're on home page by URL or welcome heading
      const url = this.page.url();
      if (url.includes('/home')) {
        return true;
      }
      return await this.welcomeHeading.isVisible({ timeout: 3000 });
    } catch {
      return false;
    }
  }

  async hasRecentExpenses(): Promise<boolean> {
    const count = await this.getRecentExpensesCount();
    return count > 0;
  }

  async isEmptyState(): Promise<boolean> {
    return await this.emptyState.isVisible();
  }
}
