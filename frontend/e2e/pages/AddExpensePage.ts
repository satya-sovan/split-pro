import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';
import type { SplitType } from '../fixtures/test-data';

export class AddExpensePage extends BasePage {
  // Locators based on actual AddExpenseView.vue
  readonly descriptionInput: Locator;
  readonly amountInput: Locator;
  readonly currencySelect: Locator;
  readonly categoryPicker: Locator;
  readonly dateInput: Locator;
  readonly paidBySelect: Locator;
  readonly groupSelect: Locator;

  // Split type buttons
  readonly splitTypeEqual: Locator;
  readonly splitTypeExact: Locator;
  readonly splitTypePercentage: Locator;
  readonly splitTypeShare: Locator;

  // Participants section
  readonly addParticipantButton: Locator;
  readonly participantRows: Locator;
  readonly remainingAmount: Locator;

  // Actions
  readonly cancelButton: Locator;
  readonly submitButton: Locator;

  // Dialog
  readonly addParticipantDialog: Locator;

  constructor(page: Page) {
    super(page);
    // Form fields - based on AddExpenseView.vue
    this.descriptionInput = page.locator('#name');
    this.amountInput = page.locator('input[inputmode="decimal"]').first();
    this.currencySelect = page.locator('select').first();
    this.categoryPicker = page.getByText(/category/i).locator('..').locator('button, select').first();
    this.dateInput = page.locator('#date');
    this.paidBySelect = page.locator('select').nth(1);
    this.groupSelect = page.locator('select').nth(2);

    // Split type buttons
    this.splitTypeEqual = page.getByRole('button', { name: /equally/i });
    this.splitTypeExact = page.getByRole('button', { name: /exact amounts/i });
    this.splitTypePercentage = page.getByRole('button', { name: /by percentage/i });
    this.splitTypeShare = page.getByRole('button', { name: /by shares/i });

    // Participants
    this.addParticipantButton = page.getByRole('button', { name: /add person/i });
    this.participantRows = page.locator('[class*="participant"]');
    this.remainingAmount = page.getByText(/remaining to split/i).locator('..').locator('span').last();

    // Actions
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.submitButton = page.getByRole('button', { name: /save expense/i });

    // Dialog
    this.addParticipantDialog = page.getByRole('dialog');
  }

  async goto(): Promise<void> {
    await this.page.goto('/add');
    await this.page.waitForLoadState('networkidle');
  }

  async fillBasicDetails(description: string, amount: string, date?: string): Promise<void> {
    await this.descriptionInput.fill(description);
    await this.amountInput.fill(amount);
    if (date) {
      await this.dateInput.fill(date);
    }
  }

  async selectSplitType(type: SplitType): Promise<void> {
    const buttonMap: Record<SplitType, Locator> = {
      equal: this.splitTypeEqual,
      percentage: this.splitTypePercentage,
      shares: this.splitTypeShare,
      exact: this.splitTypeExact
    };
    await buttonMap[type].click();
  }

  async openAddParticipantDialog(): Promise<void> {
    await this.addParticipantButton.click();
  }

  async getParticipantCount(): Promise<number> {
    return await this.participantRows.count();
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async cancel(): Promise<void> {
    await this.cancelButton.click();
  }

  async getRemainingAmount(): Promise<string> {
    return await this.remainingAmount.textContent() || '0';
  }

  async hasRequiredFieldIndicators(): Promise<boolean> {
    const indicators = this.page.locator('.text-destructive');
    const count = await indicators.count();
    return count > 0;
  }

  async isValid(): Promise<boolean> {
    const isDisabled = await this.submitButton.isDisabled();
    return !isDisabled;
  }

  async createExpense(details: {
    description: string;
    amount: string;
    date?: string;
    splitType?: SplitType;
  }): Promise<void> {
    await this.fillBasicDetails(details.description, details.amount, details.date);
    if (details.splitType) {
      await this.selectSplitType(details.splitType);
    }
    await this.submit();
  }
}
