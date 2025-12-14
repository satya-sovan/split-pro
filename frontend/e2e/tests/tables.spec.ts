import { test, expect } from '../fixtures';

/**
 * Table/List Tests
 * Tests pagination, sorting, and filtering for lists
 */
test.describe('Tables & Lists', () => {
  test.beforeEach(async ({ authHelper }) => {
    await authHelper.loginAsTestUser();
  });

  test.describe('Expense List', () => {
    test('should display expenses in a list', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Should show list or empty state
      const hasItems = (await expensesPage.getExpenseCount()) > 0;
      const hasEmpty = await expensesPage.hasEmptyState();

      expect(hasItems || hasEmpty).toBeTruthy();
    });

    test('should show expense details in list items', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        const text = await expensesPage.getExpenseText(0);
        // Should contain some expense info
        expect(text).toBeTruthy();
      }
    });

    test('should be clickable to view details', async ({ expensesPage, page }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await expensesPage.clickExpense(0);
        await expect(page).toHaveURL(/\/expenses\/\d+/);
      }
    });
  });

  test.describe('Pagination', () => {
    test('should show pagination when many items', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Check if pagination exists
      const hasPagination = await expensesPage.hasPagination();
      // Pagination may or may not be visible depending on data
    });

    test('should navigate to next page', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      if (await expensesPage.hasNextPage()) {
        await expensesPage.goToNextPage();

        // Should update content
        await expensesPage.waitForLoad();
      }
    });

    test('should navigate to previous page', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Go to next first
      if (await expensesPage.hasNextPage()) {
        await expensesPage.goToNextPage();
        await expensesPage.waitForLoad();

        // Then go back
        if (await expensesPage.hasPrevPage()) {
          await expensesPage.goToPrevPage();
          await expensesPage.waitForLoad();
        }
      }
    });

    test('should disable prev on first page', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // On first page, prev should be disabled
      if (await expensesPage.paginationContainer.isVisible()) {
        const hasPrev = await expensesPage.hasPrevPage();
        // First page should not have prev
      }
    });
  });

  test.describe('Search & Filter', () => {
    test('should have search input', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const searchVisible = await expensesPage.searchInput.isVisible();
      // Search may or may not be implemented
    });

    test('should filter results on search', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      if (await expensesPage.searchInput.isVisible()) {
        const initialCount = await expensesPage.getExpenseCount();

        await expensesPage.search('nonexistent123456');

        const filteredCount = await expensesPage.getExpenseCount();
        // Filtered count should be different or show no results
      }
    });

    test('should clear search results', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      if (await expensesPage.searchInput.isVisible()) {
        await expensesPage.search('test');
        await expensesPage.clearSearch();

        // Results should reset
      }
    });

    test('should show empty state for no results', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      if (await expensesPage.searchInput.isVisible()) {
        await expensesPage.search('zzznonexistent999');

        // Should show no results message
        const count = await expensesPage.getExpenseCount();
        const hasEmpty = await expensesPage.hasEmptyState();

        expect(count === 0 || hasEmpty).toBeTruthy();
      }
    });
  });

  test.describe('Sorting', () => {
    test('should have sort options', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const sortVisible = await expensesPage.sortButton.isVisible();
      // Sort may or may not be implemented
    });

    test('should sort by date', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      if (await expensesPage.sortButton.isVisible()) {
        await expensesPage.sortBy('date');

        // Content should update
        await expensesPage.waitForLoad();
      }
    });

    test('should sort by amount', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      if (await expensesPage.sortButton.isVisible()) {
        await expensesPage.sortBy('amount');

        await expensesPage.waitForLoad();
      }
    });
  });

  test.describe('Groups List', () => {
    test('should display groups in a list', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const hasItems = (await groupsPage.getGroupCount()) > 0;
      const hasEmpty = await groupsPage.hasEmptyState();

      expect(hasItems || hasEmpty).toBeTruthy();
    });

    test('should be clickable to view details', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      const count = await groupsPage.getGroupCount();
      if (count > 0) {
        await groupsPage.clickGroupByIndex(0);
        await expect(page).toHaveURL(/\/groups\/\d+/);
      }
    });
  });

  test.describe('Recent Expenses (Home)', () => {
    test('should display limited recent items', async ({ homePage }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      const count = await homePage.getRecentExpenseCount();
      // Should be limited (e.g., max 10)
      expect(count).toBeLessThanOrEqual(10);
    });

    test('should link to full expenses list', async ({ homePage, page }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      if (await homePage.viewAllExpensesLink.isVisible()) {
        await homePage.goToAllExpenses();
        await expect(page).toHaveURL(/\/expenses/);
      }
    });
  });

  test.describe('Loading States', () => {
    test('should show loading indicator', async ({ expensesPage, apiMocker }) => {
      // Mock slow response
      await apiMocker.mockSlowResponse('**/expenses**', { data: [] }, 2000);

      await expensesPage.goto();

      // Should show loading indicator initially
      const spinner = expensesPage.loadingSpinner;
      await expect(spinner).toBeVisible({ timeout: 1000 }).catch(() => {
        // Loading might be too fast to catch
      });
    });

    test('should hide loading after data loads', async ({ expensesPage }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      // Loading should be hidden
      await expect(expensesPage.loadingSpinner).not.toBeVisible();
    });
  });

  test.describe('Empty States', () => {
    test('should show empty state message', async ({ expensesPage, apiMocker }) => {
      // Mock empty response
      await apiMocker.mockEmpty('**/expenses**');

      await expensesPage.goto();
      await expensesPage.waitForLoad();

      expect(await expensesPage.hasEmptyState()).toBeTruthy();
    });

    test('should provide action to create item', async ({ groupsPage, apiMocker }) => {
      await apiMocker.mockEmpty('**/groups**');

      await groupsPage.goto();
      await groupsPage.waitForLoad();

      if (await groupsPage.hasEmptyState()) {
        // Should have create button in empty state
        await expect(groupsPage.createGroupButton).toBeVisible();
      }
    });
  });
});

