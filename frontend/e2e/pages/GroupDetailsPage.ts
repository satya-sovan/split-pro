import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class GroupDetailsPage extends BasePage {
  readonly groupName: Locator;
  readonly settingsButton: Locator;
  readonly addExpenseButton: Locator;
  readonly settleUpButton: Locator;
  readonly membersList: Locator;
  readonly addMemberButton: Locator;
  readonly expensesList: Locator;
  readonly expenseCards: Locator;
  readonly emptyExpensesState: Locator;
  readonly balancesSummary: Locator;
  readonly settingsDialog: Locator;
  readonly addMemberDialog: Locator;
  readonly settleUpDialog: Locator;

  constructor(page: Page) {
    super(page);
    this.groupName = page.getByRole('heading').first();
    this.settingsButton = page.getByRole('button', { name: /settings|edit/i });
    this.addExpenseButton = page.getByRole('button', { name: /add expense/i });
    this.settleUpButton = page.getByRole('button', { name: /settle up/i });
    this.membersList = page.locator('[data-testid="members-list"]');
    this.addMemberButton = page.getByRole('button', { name: /add member/i });
    this.expensesList = page.locator('[data-testid="expenses-list"]');
    this.expenseCards = page.locator('[data-testid="expense-card"]');
    this.emptyExpensesState = page.getByText(/no expenses/i);
    this.balancesSummary = page.locator('[data-testid="balances-summary"]');
    this.settingsDialog = page.getByRole('dialog').filter({ hasText: /settings/i });
    this.addMemberDialog = page.getByRole('dialog').filter({ hasText: /add member/i });
    this.settleUpDialog = page.getByRole('dialog').filter({ hasText: /settle/i });
  }

  async goto(groupId?: string | number): Promise<void> {
    await this.page.goto(`/groups/${groupId || ''}`);
    await this.waitForPageLoad();
  }

  async gotoGroup(groupId: string | number): Promise<void> {
    await this.page.goto(`/groups/${groupId}`);
    await this.waitForPageLoad();
  }

  async getGroupName(): Promise<string | null> {
    return this.groupName.textContent();
  }

  async openSettings(): Promise<void> {
    await this.settingsButton.click();
    await this.settingsDialog.waitFor({ state: 'visible' });
  }

  async openAddMember(): Promise<void> {
    await this.addMemberButton.click();
    await this.addMemberDialog.waitFor({ state: 'visible' });
  }

  async openSettleUp(): Promise<void> {
    await this.settleUpButton.click();
    await this.settleUpDialog.waitFor({ state: 'visible' });
  }

  async goToAddExpense(): Promise<void> {
    await this.addExpenseButton.click();
  }

  async getExpenseCount(): Promise<number> {
    return this.expenseCards.count();
  }

  async clickExpense(index: number): Promise<void> {
    await this.expenseCards.nth(index).click();
  }

  async updateGroupName(newName: string): Promise<void> {
    await this.openSettings();
    const nameInput = this.page.getByLabel(/group name|name/i);
    await nameInput.clear();
    await nameInput.fill(newName);
    await this.page.getByRole('button', { name: /save|update/i }).click();
  }

  async addMember(email: string): Promise<void> {
    await this.openAddMember();
    await this.page.getByLabel(/email/i).fill(email);
    await this.page.getByRole('button', { name: /add|invite/i }).click();
  }

  async closeDialog(): Promise<void> {
    await this.page.keyboard.press('Escape');
  }

  async hasEmptyState(): Promise<boolean> {
    return this.emptyExpensesState.isVisible();
  }
}

