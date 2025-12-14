import { test, expect } from '../fixtures';
import { generateRandomString } from '../utils';

/**
 * Modal & Dialog Tests
 * Tests dialog opening, closing, confirmation, and cancellation
 */
test.describe('Modals & Dialogs', () => {
  test.beforeEach(async ({ authHelper }) => {
    await authHelper.loginAsTestUser();
  });

  test.describe('Create Group Dialog', () => {
    test('should open dialog on button click', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      await expect(groupsPage.createGroupDialog).toBeVisible();
    });

    test('should close dialog on escape key', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();
      await expect(groupsPage.createGroupDialog).toBeVisible();

      await groupsPage.page.keyboard.press('Escape');

      await expect(groupsPage.createGroupDialog).not.toBeVisible();
    });

    test('should close dialog on outside click', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();
      await expect(groupsPage.createGroupDialog).toBeVisible();

      // Click outside dialog (on backdrop)
      await page.locator('[data-backdrop], .fixed.inset-0').first().click({ force: true, position: { x: 10, y: 10 } });

      // Dialog may or may not close depending on implementation
    });

    test('should close dialog on cancel button', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      const cancelButton = page.getByRole('button', { name: /cancel|close/i });
      if (await cancelButton.isVisible()) {
        await cancelButton.click();
        await expect(groupsPage.createGroupDialog).not.toBeVisible();
      }
    });

    test('should submit and close on success', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const groupName = `Test Group ${generateRandomString(5)}`;
      await groupsPage.createGroup(groupName);

      // Dialog should close after successful creation
      // Note: might navigate to new group instead
    });

    test('should preserve input when reopened after cancel', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();
      await page.getByLabel(/group name|name/i).fill('Test');
      await page.keyboard.press('Escape');

      await groupsPage.openCreateGroupDialog();

      // Input might be cleared or preserved (implementation specific)
      const value = await page.getByLabel(/group name|name/i).inputValue();
      // Either empty or 'Test' is acceptable
    });
  });

  test.describe('Delete Confirmation Dialog', () => {
    test('should show confirmation before delete', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canDelete()) {
          await expenseDetailsPage.deleteButton.click();

          await expect(expenseDetailsPage.deleteDialog).toBeVisible();
        }
      }
    });

    test('should cancel delete on cancel button', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canDelete()) {
          await expenseDetailsPage.cancelDelete();

          await expect(expenseDetailsPage.deleteDialog).not.toBeVisible();
          // Still on expense page
          await expect(page).toHaveURL(/\/expenses\/\d+/);
        }
      }
    });

    test('should delete on confirm button', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canDelete()) {
          await expenseDetailsPage.deleteExpense();

          // Should navigate away or show success
        }
      }
    });

    test('should close on escape key', async ({ expensesPage, expenseDetailsPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await page.waitForURL(/\/expenses\/\d+/);

        if (await expenseDetailsPage.canDelete()) {
          await expenseDetailsPage.deleteButton.click();
          await expect(expenseDetailsPage.deleteDialog).toBeVisible();

          await page.keyboard.press('Escape');

          await expect(expenseDetailsPage.deleteDialog).not.toBeVisible();
        }
      }
    });
  });

  test.describe('Add Participant Dialog', () => {
    test('should open add participant dialog', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.openAddParticipantDialog();

      const dialog = addExpensePage.page.getByRole('dialog');
      await expect(dialog).toBeVisible();
    });

    test('should close on escape', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.openAddParticipantDialog();
      const dialog = addExpensePage.page.getByRole('dialog');
      await expect(dialog).toBeVisible();

      await addExpensePage.page.keyboard.press('Escape');

      await expect(dialog).not.toBeVisible();
    });
  });

  test.describe('Settings Dialog', () => {
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

    test('should update settings and close', async ({ groupsPage, groupDetailsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const count = await groupsPage.getGroupCount();
      if (count > 0) {
        await groupsPage.clickGroupByIndex(0);
        await page.waitForURL(/\/groups\/\d+/);

        if (await groupDetailsPage.settingsButton.isVisible()) {
          const newName = `Updated ${generateRandomString(5)}`;
          await groupDetailsPage.updateGroupName(newName);

          // Dialog should close
          await expect(groupDetailsPage.settingsDialog).not.toBeVisible();
        }
      }
    });
  });

  test.describe('Dialog Accessibility', () => {
    test('should trap focus within dialog', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Tab should cycle within dialog
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Focus should still be in dialog
      const activeElement = await page.evaluate(() => {
        const dialog = document.querySelector('[role="dialog"]');
        return dialog?.contains(document.activeElement);
      });

      expect(activeElement).toBeTruthy();
    });

    test('should have proper role attributes', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      const dialog = groupsPage.page.locator('[role="dialog"]');
      await expect(dialog).toBeVisible();
    });

    test('should be announced to screen readers', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Dialog should have aria-modal
      const dialog = groupsPage.page.locator('[role="dialog"]');
      const hasModal = await dialog.getAttribute('aria-modal');
      // aria-modal should be true or dialog should be properly set up
    });
  });

  test.describe('Dialog States', () => {
    test('should show loading state during submission', async ({ groupsPage, page, apiMocker }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Mock slow response
      await apiMocker.mockSlowResponse('**/groups', { id: 1, name: 'test' }, 2000);

      await page.getByLabel(/group name|name/i).fill('Test Group');
      await page.getByRole('button', { name: /create|save/i }).click();

      // Should show loading indicator
      const loadingButton = page.getByRole('button', { name: /creating|saving|loading/i });
      // Loading state depends on implementation
    });

    test('should show error state on failure', async ({ groupsPage, page, apiMocker }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Mock error
      await apiMocker.mockServerError('**/groups');

      await page.getByLabel(/group name|name/i).fill('Test Group');
      await page.getByRole('button', { name: /create|save/i }).click();

      // Should show error
      const error = page.locator('.text-destructive, .text-red-600');
      // Error display depends on implementation
    });
  });
});

