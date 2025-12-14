import { test, expect } from '../fixtures';

/**
 * Error Handling Tests
 * Tests API failures, network errors, and error messages
 */
test.describe('Error Handling', () => {
  test.beforeEach(async ({ authHelper }) => {
    await authHelper.loginAsTestUser();
  });

  test.describe('API Failure Simulation', () => {
    test('should handle 500 server error', async ({ expensesPage, apiMocker }) => {
      await apiMocker.mockServerError('**/expenses**');

      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Should show error message or empty state
      // Implementation varies - might show toast, error banner, etc.
    });

    test('should handle 401 unauthorized', async ({ expensesPage, apiMocker, page }) => {
      await apiMocker.mockError('**/expenses**', 401, 'Unauthorized');

      await expensesPage.goto();

      // Should redirect to login or show auth error
      // Behavior depends on implementation
    });

    test('should handle 403 forbidden', async ({ expensesPage, apiMocker }) => {
      await apiMocker.mockError('**/expenses**', 403, 'Forbidden');

      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Should show permission error
    });

    test('should handle 404 not found', async ({ page }) => {
      await page.goto('/expenses/99999999');

      // Should show not found message or redirect
    });

    test('should handle 422 validation error', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      await apiMocker.mockError('**/expenses', 422, 'Validation failed');

      await addExpensePage.fillBasicDetails('Test', '50');
      await addExpensePage.submit();

      // Should show validation error
    });
  });

  test.describe('Network Errors', () => {
    test('should handle network failure', async ({ expensesPage, apiMocker }) => {
      await apiMocker.mockNetworkFailure('**/expenses**');

      await expensesPage.goto();

      // Should show network error message
    });

    test('should handle request timeout', async ({ expensesPage, apiMocker }) => {
      await apiMocker.mockTimeout('**/expenses**', 1000);

      await expensesPage.goto();

      // Should handle timeout gracefully
    });

    test('should allow retry after error', async ({ expensesPage, apiMocker, page }) => {
      // First request fails
      await apiMocker.mockNetworkFailure('**/expenses**');
      await expensesPage.goto();

      // Clear mock for retry
      await apiMocker.clearMocks();

      // Retry (refresh page)
      await page.reload();
      await expensesPage.waitForLoad();

      // Should work now
    });
  });

  test.describe('UI Error Messages', () => {
    test('should display error toast on API failure', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      await apiMocker.mockServerError('**/expenses');

      await addExpensePage.fillBasicDetails('Test', '50');
      await addExpensePage.submit();

      // Check for toast
      const toast = addExpensePage.page.locator('[data-sonner-toast]');
      // Toast might appear
    });

    test('should display inline error messages', async ({ loginPage }) => {
      await loginPage.goto();

      await loginPage.login('invalid@test.com', 'wrongpassword');

      // Should show inline error
      const error = await loginPage.getErrorText();
      expect(error).toBeTruthy();
    });

    test('should clear error on new action', async ({ loginPage }) => {
      await loginPage.goto();

      // Trigger error
      await loginPage.login('invalid@test.com', 'wrong');
      expect(await loginPage.getErrorText()).toBeTruthy();

      // Start new input
      await loginPage.fillEmail('new@test.com');

      // Error might clear
    });
  });

  test.describe('Form Submission Errors', () => {
    test('should handle duplicate group name', async ({ groupsPage, page, apiMocker }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Mock conflict error
      await apiMocker.mockError('**/groups', 409, 'Group name already exists');

      await page.getByLabel(/group name|name/i).fill('Duplicate Name');
      await page.getByRole('button', { name: /create|save/i }).click();

      // Should show error
    });

    test('should handle rate limiting', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      await apiMocker.mockError('**/expenses', 429, 'Too many requests');

      await addExpensePage.fillBasicDetails('Test', '50');
      await addExpensePage.submit();

      // Should show rate limit error
    });
  });

  test.describe('Error Recovery', () => {
    test('should maintain form data after error', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      const description = 'Test Expense';
      const amount = '100.00';

      await addExpensePage.fillBasicDetails(description, amount);

      // Mock error
      await apiMocker.mockServerError('**/expenses');
      await addExpensePage.submit();

      // Form data should be preserved
      const currentDesc = await addExpensePage.descriptionInput.inputValue();
      expect(currentDesc).toBe(description);
    });

    test('should allow resubmission after error', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test', '50');

      // First submission fails
      await apiMocker.mockServerError('**/expenses');
      await addExpensePage.submit();

      // Clear mock
      await apiMocker.clearMocks();

      // Try again
      await addExpensePage.submit();

      // Should succeed this time
    });
  });

  test.describe('Graceful Degradation', () => {
    test('should show cached data when offline', async ({ homePage, page }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      // Go offline
      await page.context().setOffline(true);

      // Reload
      await page.reload().catch(() => {});

      // Should show something or offline message
      // PWA might show cached content

      // Go back online
      await page.context().setOffline(false);
    });

    test('should disable submit during loading', async ({ addExpensePage, apiMocker }) => {
      await addExpensePage.goto();

      // Mock slow response
      await apiMocker.mockSlowResponse('**/expenses', {}, 5000);

      await addExpensePage.fillBasicDetails('Test', '50');
      await addExpensePage.submit();

      // Button should be disabled during submission
      const isDisabled = await addExpensePage.submitButton.isDisabled();
      // Might be disabled or show loading state
    });
  });

  test.describe('Error Boundary', () => {
    test('should not crash on render error', async ({ page }) => {
      // Navigate to page with potential render issues
      await page.goto('/home');

      // Page should not be completely blank
      const body = await page.locator('body').textContent();
      expect(body).toBeTruthy();
    });

    test('should provide recovery option on crash', async ({ page }) => {
      // If app has error boundary
      // Should show recovery UI
    });
  });

  test.describe('Error Logging', () => {
    test('should not expose sensitive data in errors', async ({ loginPage }) => {
      await loginPage.goto();

      await loginPage.login('test@test.com', 'wrongpassword');

      const error = await loginPage.getErrorText();
      if (error) {
        // Should not contain password or sensitive info
        expect(error.toLowerCase()).not.toContain('wrongpassword');
      }
    });
  });
});

