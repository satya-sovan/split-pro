import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class GroupsPage extends BasePage {
  // Locators based on actual GroupsView.vue
  readonly createGroupButton: Locator;
  readonly joinGroupButton: Locator;
  readonly groupsList: Locator;
  readonly groupCards: Locator;
  readonly loadingSpinner: Locator;
  readonly emptyState: Locator;

  // Create Group Dialog (CreateGroupDialog.vue)
  readonly createGroupDialog: Locator;
  readonly groupNameInput: Locator;
  readonly currencySelect: Locator;
  readonly simplifyDebtsCheckbox: Locator;
  readonly dialogCancelButton: Locator;
  readonly dialogSubmitButton: Locator;

  constructor(page: Page) {
    super(page);
    // Main buttons
    this.createGroupButton = page.getByRole('button', { name: /create group/i });
    this.joinGroupButton = page.getByRole('button', { name: /join group/i });

    // List
    this.groupsList = page.locator('.space-y-3');
    this.groupCards = page.locator('[class*="group-card"], .space-y-3 > div');
    this.loadingSpinner = page.locator('.animate-spin');
    this.emptyState = page.getByText(/no groups yet/i);

    // Dialog
    this.createGroupDialog = page.getByRole('dialog');
    this.groupNameInput = page.getByRole('dialog').locator('#name');
    this.currencySelect = page.getByRole('dialog').locator('select').first();
    this.simplifyDebtsCheckbox = page.getByRole('dialog').locator('#simplify');
    this.dialogCancelButton = page.getByRole('dialog').getByRole('button', { name: /cancel/i });
    this.dialogSubmitButton = page.getByRole('dialog').getByRole('button', { name: /create group/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/groups');
    await this.page.waitForLoadState('networkidle');
  }

  async waitForLoad(): Promise<void> {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
  }

  async openCreateGroupDialog(): Promise<void> {
    await this.createGroupButton.click();
    await this.createGroupDialog.waitFor({ state: 'visible' });
  }

  async createGroup(name: string): Promise<void> {
    await this.openCreateGroupDialog();
    await this.groupNameInput.fill(name);
    await this.dialogSubmitButton.click();
    // Wait for dialog to close
    await this.createGroupDialog.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {});
  }

  async closeCreateDialog(): Promise<void> {
    await this.dialogCancelButton.click();
    await this.createGroupDialog.waitFor({ state: 'hidden' });
  }

  async getGroupCount(): Promise<number> {
    await this.waitForLoad();
    return await this.groupCards.count();
  }

  async clickFirstGroup(): Promise<void> {
    await this.groupCards.first().click();
  }

  async hasGroups(): Promise<boolean> {
    await this.waitForLoad();
    const count = await this.getGroupCount();
    return count > 0;
  }

  async hasEmptyState(): Promise<boolean> {
    await this.waitForLoad();
    return await this.emptyState.isVisible();
  }

  async isDisplayed(): Promise<boolean> {
    const url = this.page.url();
    return url.includes('/groups');
  }
}
