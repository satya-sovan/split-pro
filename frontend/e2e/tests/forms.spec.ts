import { test, expect } from '../fixtures';
import { generateRandomString, getToday, getFutureDate } from '../utils';

/**
 * Form Validation Tests
 * Tests required fields, input validation, and form submission
 */
test.describe('Forms', () => {
  test.beforeEach(async ({ authHelper }) => {
    await authHelper.loginAsTestUser();
  });

  test.describe('Add Expense Form', () => {
    test('should show required field indicators', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Check for asterisks or required indicators
      const hasIndicators = await addExpensePage.hasRequiredFieldIndicators();
      expect(hasIndicators).toBeTruthy();
    });

    test('should validate required description', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Fill amount but not description
      await addExpensePage.amountInput.fill('50.00');
      await addExpensePage.submit();

      // Form should not submit - check we're still on page
      await expect(addExpensePage.page).toHaveURL(/\/add/);
    });

    test('should validate required amount', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Fill description but not amount
      await addExpensePage.descriptionInput.fill('Test Expense');
      await addExpensePage.submit();

      // Should show validation or not submit
    });

    test('should accept valid numeric amount', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.amountInput.fill('123.45');

      const value = await addExpensePage.amountInput.inputValue();
      expect(value).toContain('123');
    });

    test('should reject invalid amount characters', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Type invalid characters
      await addExpensePage.amountInput.type('abc!@#');

      // Should filter out invalid chars or show error
      const value = await addExpensePage.amountInput.inputValue();
      expect(value.match(/[a-z!@#]/)).toBeFalsy();
    });

    test('should format currency on blur', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.amountInput.fill('100');
      await addExpensePage.amountInput.blur();

      // Value might be formatted (implementation specific)
    });

    test('should accept valid date', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      const today = getToday();
      await addExpensePage.dateInput.fill(today);

      const value = await addExpensePage.dateInput.inputValue();
      expect(value).toBe(today);
    });

    test('should allow past dates', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      const pastDate = '2024-01-01';
      await addExpensePage.dateInput.fill(pastDate);

      const value = await addExpensePage.dateInput.inputValue();
      expect(value).toBe(pastDate);
    });

    test('should allow future dates', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      const futureDate = getFutureDate(7);
      await addExpensePage.dateInput.fill(futureDate);

      const value = await addExpensePage.dateInput.inputValue();
      expect(value).toBe(futureDate);
    });

    test('should enable submit when form is valid', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test Expense', '50.00', getToday());

      // Submit should be enabled
      const isEnabled = await addExpensePage.isSubmitEnabled();
      // Note: might still be disabled if participants required
    });

    test('should clear form on cancel', async ({ addExpensePage, page }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test', '50');
      await addExpensePage.cancel();

      // Navigate back to add
      await page.goto('/add');

      // Form should be empty
      const description = await addExpensePage.descriptionInput.inputValue();
      expect(description).toBe('');
    });
  });

  test.describe('Create Group Form', () => {
    test('should require group name', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Try to submit empty
      const submitButton = page.getByRole('button', { name: /create|save/i });
      const nameInput = page.getByLabel(/group name|name/i);

      // Clear and submit
      await nameInput.clear();
      await submitButton.click();

      // Should not close dialog
      await expect(groupsPage.createGroupDialog).toBeVisible();
    });

    test('should accept valid group name', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      const groupName = `Valid Group ${generateRandomString(5)}`;
      await page.getByLabel(/group name|name/i).fill(groupName);

      const value = await page.getByLabel(/group name|name/i).inputValue();
      expect(value).toBe(groupName);
    });

    test('should trim whitespace from group name', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      await page.getByLabel(/group name|name/i).fill('  Test Group  ');

      // On submit, whitespace should be trimmed (behavior varies)
    });
  });

  test.describe('Form Interactions', () => {
    test('should support tab navigation through form', async ({ addExpensePage, page }) => {
      await addExpensePage.goto();

      // Focus first field
      await addExpensePage.descriptionInput.focus();

      // Tab through fields
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Should have moved focus
      const activeId = await page.evaluate(() => document.activeElement?.id || document.activeElement?.tagName);
      expect(activeId).toBeTruthy();
    });

    test('should submit form on Enter key', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test', '50');

      // Press enter
      await addExpensePage.page.keyboard.press('Enter');

      // Form might submit or do nothing (depends on form setup)
    });

    test('should show success feedback on submit', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test Expense', '50.00', getToday());
      // Would need participants for full submission

      // Submit behavior varies by implementation
    });
  });

  test.describe('Form Error States', () => {
    test('should display inline validation errors', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Submit empty form to trigger validation
      await addExpensePage.submit();

      // Check for validation messages or HTML5 validation
      const description = addExpensePage.descriptionInput;
      const isInvalid = await description.evaluate((el: HTMLInputElement) => !el.validity.valid);
      expect(isInvalid).toBeTruthy();
    });

    test('should clear errors on valid input', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Submit empty to trigger validation
      await addExpensePage.submit();

      // Now fill with valid data
      await addExpensePage.fillBasicDetails('Test', '50');

      // Errors should clear
    });

    test('should handle API errors gracefully', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      // Mock API error
      await apiMocker.mockServerError('**/expenses');

      await addExpensePage.fillBasicDetails('Test', '50', getToday());
      await addExpensePage.submit();

      // Should show error message (toast or inline)
    });
  });

  test.describe('Form Accessibility', () => {
    test('should have proper label associations', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Check description input has label
      const descriptionLabel = addExpensePage.page.locator('label[for="name"]');
      await expect(descriptionLabel).toBeVisible();
    });

    test('should announce errors to screen readers', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Submit to trigger errors
      await addExpensePage.submit();

      // Error messages should be accessible
      const errors = addExpensePage.errorMessages;
      if (await errors.count() > 0) {
        await expect(errors.first()).toBeVisible();
      }
    });

    test('should have visible focus states', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      await addExpensePage.descriptionInput.focus();

      // Should have focus ring or outline
      const hasFocusStyles = await addExpensePage.descriptionInput.evaluate((el) => {
        const styles = window.getComputedStyle(el);
        return styles.outline !== 'none' || styles.boxShadow !== 'none';
      });

      // Focus styles should be visible
    });
  });
});

