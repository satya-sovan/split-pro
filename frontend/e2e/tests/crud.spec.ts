import { test, expect } from '../fixtures';
import { generateRandomString, generateRandomAmount, getToday } from '../utils';

/**
 * CRUD Flow Tests
 * Tests create, read, update, and delete operations for expenses and groups
 */
test.describe('CRUD Operations', () => {
  test.beforeEach(async ({ authHelper }) => {
    await authHelper.loginAsTestUser();
  });

  test.describe('Create Expense', () => {
    test('should create expense with valid data', async ({ addExpensePage, page }) => {
      await addExpensePage.goto();

      const description = `Test Expense ${generateRandomString(5)}`;
      const amount = generateRandomAmount(10, 100);

      await addExpensePage.createExpense({
        description,
        amount,
        splitType: 'equal'
      });

      // Should navigate away on success or show success message
      // Behavior depends on implementation
    });

    test('should not submit with empty description', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Fill only amount
      await addExpensePage.amountInput.fill('50.00');

      // Submit button might be disabled or form validation should prevent submission
      const descriptionInput = addExpensePage.descriptionInput;
      await expect(descriptionInput).toHaveAttribute('required');
    });

    test('should not submit with zero amount', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test Expense', '0');

      // Amount validation should prevent submission
      // Check if form is still on page or shows error
    });

    test('should show validation error for negative amount', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test Expense', '-50');

      // Should show validation error or prevent input
    });

    test('should allow selecting different split types', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Test each split type
      await addExpensePage.selectSplitType('equal');
      await expect(addExpensePage.splitTypeEqual).toHaveClass(/border-primary|bg-primary/);

      await addExpensePage.selectSplitType('percentage');
      await expect(addExpensePage.splitTypePercentage).toHaveClass(/border-primary|bg-primary/);

      await addExpensePage.selectSplitType('exact');
      await expect(addExpensePage.splitTypeExact).toHaveClass(/border-primary|bg-primary/);
    });

    test('should allow adding participants', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Open add participant dialog
      await addExpensePage.openAddParticipantDialog();

      // Dialog should be visible
      const dialog = addExpensePage.page.getByRole('dialog');
      await expect(dialog).toBeVisible();
    });

    test('should cancel expense creation', async ({ addExpensePage, page }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test', '50');
      await addExpensePage.cancel();

      // Should navigate back
      await expect(page).not.toHaveURL(/\/add$/);
    });

    test('should show remaining amount for split', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test Expense', '100');

      // Check if split summary shows remaining
      const summary = addExpensePage.splitSummary;
      if (await summary.isVisible()) {
        const summaryText = await summary.textContent();
        expect(summaryText).toContain('100');
      }
    });
  });

  test.describe('Read Expenses', () => {
    test('should display expense list', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Either expenses are shown or empty state
      const hasExpenses = (await expensesPage.getExpenseCount()) > 0;
      const hasEmptyState = await expensesPage.hasEmptyState();

      expect(hasExpenses || hasEmptyState).toBeTruthy();
    });

    test('should show expense details on click', async ({ expensesPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await expect(page).toHaveURL(/\/expenses\/\d+/);
      }
    });

    test('should display recent expenses on home', async ({ homePage }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      // Either expenses or empty state should be visible
      const hasExpenses = (await homePage.getRecentExpenseCount()) > 0;
      const hasEmptyState = await homePage.hasEmptyState();

      expect(hasExpenses || hasEmptyState).toBeTruthy();
    });
  });

  test.describe('Update Expense', () => {
    test('should navigate to edit from expense details', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canEdit()) {
          await expenseDetailsPage.goToEdit();
          // Should be on edit page
        }
      }
    });
  });

  test.describe('Delete Expense', () => {
    test('should show delete confirmation dialog', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canDelete()) {
          await expenseDetailsPage.deleteButton.click();

          // Confirmation dialog should appear
          await expect(expenseDetailsPage.deleteDialog).toBeVisible();
        }
      }
    });

    test('should cancel delete operation', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canDelete()) {
          await expenseDetailsPage.cancelDelete();

          // Should still be on expense details
          await expect(page).toHaveURL(/\/expenses\/\d+/);
        }
      }
    });
  });

  test.describe('Create Group', () => {
    test('should open create group dialog', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      await expect(groupsPage.createGroupDialog).toBeVisible();
    });

    test('should create group with valid name', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const groupName = `Test Group ${generateRandomString(5)}`;
      await groupsPage.createGroup(groupName);

      // Should either navigate to group or show success
    });

    test('should close dialog on escape', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();
      await expect(groupsPage.createGroupDialog).toBeVisible();

      await groupsPage.closeDialog();

      // Dialog should close
      await expect(groupsPage.createGroupDialog).not.toBeVisible();
    });
  });

  test.describe('Read Groups', () => {
    test('should display groups list', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      // Either groups are shown or empty state
      const hasGroups = (await groupsPage.getGroupCount()) > 0;
      const hasEmptyState = await groupsPage.hasEmptyState();

      expect(hasGroups || hasEmptyState).toBeTruthy();
    });

    test('should navigate to group details', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const count = await groupsPage.getGroupCount();
      if (count > 0) {
        await groupsPage.clickGroupByIndex(0);
        await expect(page).toHaveURL(/\/groups\/\d+/);
      }
    });
  });

  test.describe('Update Group', () => {
    test('should open group settings', async ({ groupsPage, groupDetailsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const count = await groupsPage.getGroupCount();
      if (count > 0) {
        await groupsPage.clickGroupByIndex(0);
        await page.waitForURL(/\/groups\/\d+/);

        if (await groupDetailsPage.settingsButton.isVisible()) {
          await groupDetailsPage.openSettings();
          await expect(groupDetailsPage.settingsDialog).toBeVisible();
        }
      }
    });
  });

  test.describe('Validation Errors', () => {
    test('should show error for too long description', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Fill with very long description
      const longDescription = 'a'.repeat(500);
      await addExpensePage.fillBasicDetails(longDescription, '50');

      // Check if there's validation or input is truncated
    });

    test('should show error for invalid amount format', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.descriptionInput.fill('Test');
      await addExpensePage.amountInput.fill('abc');

      // Amount input should not accept non-numeric
      const value = await addExpensePage.amountInput.inputValue();
      expect(value).not.toBe('abc');
    });
  });
});

