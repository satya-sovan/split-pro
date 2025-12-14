import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class ExpenseDetailsPage extends BasePage {
  readonly expenseName: Locator;
  readonly expenseAmount: Locator;
  readonly expenseDate: Locator;
  readonly expenseCategory: Locator;
  readonly paidBySection: Locator;
  readonly splitSection: Locator;
  readonly participantItems: Locator;
  readonly editButton: Locator;
  readonly deleteButton: Locator;
  readonly backButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly cancelDeleteButton: Locator;
  readonly deleteDialog: Locator;

  constructor(page: Page) {
    super(page);
    this.expenseName = page.getByRole('heading').first();
    this.expenseAmount = page.locator('[data-testid="expense-amount"]');
    this.expenseDate = page.locator('[data-testid="expense-date"]');
    this.expenseCategory = page.locator('[data-testid="expense-category"]');
    this.paidBySection = page.locator('[data-testid="paid-by"]');
    this.splitSection = page.locator('[data-testid="split-section"]');
    this.participantItems = page.locator('[data-testid="participant-item"]');
    this.editButton = page.getByRole('button', { name: /edit/i });
    this.deleteButton = page.getByRole('button', { name: /delete/i });
    this.backButton = page.getByRole('button', { name: /back/i });
    this.deleteDialog = page.getByRole('dialog').filter({ hasText: /delete/i });
    this.confirmDeleteButton = page.getByRole('button', { name: /confirm|yes|delete/i }).last();
    this.cancelDeleteButton = page.getByRole('button', { name: /cancel|no/i });
  }

  async goto(expenseId?: string | number): Promise<void> {
    await this.page.goto(`/expenses/${expenseId || ''}`);
    await this.waitForPageLoad();
  }

  async gotoExpense(expenseId: string | number): Promise<void> {
    await this.page.goto(`/expenses/${expenseId}`);
    await this.waitForPageLoad();
  }

  async getExpenseName(): Promise<string | null> {
    return this.expenseName.textContent();
  }

  async getExpenseAmount(): Promise<string | null> {
    return this.expenseAmount.textContent();
  }

  async getParticipantCount(): Promise<number> {
    return this.participantItems.count();
  }

  async goToEdit(): Promise<void> {
    await this.editButton.click();
  }

  async deleteExpense(): Promise<void> {
    await this.deleteButton.click();
    await this.deleteDialog.waitFor({ state: 'visible' });
    await this.confirmDeleteButton.click();
  }

  async cancelDelete(): Promise<void> {
    await this.deleteButton.click();
    await this.deleteDialog.waitFor({ state: 'visible' });
    await this.cancelDeleteButton.click();
  }

  async goBack(): Promise<void> {
    await this.backButton.click();
  }

  async canEdit(): Promise<boolean> {
    return this.editButton.isVisible();
  }

  async canDelete(): Promise<boolean> {
    return this.deleteButton.isVisible();
  }
}

