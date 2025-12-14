import { test, expect } from '../fixtures';
import { ScreenshotHelper } from '../utils';

/**
 * Visual Validation Tests
 * Screenshots for major flows and failure scenarios
 */
test.describe('Visual Validation', () => {
  test.describe('Login Flow Screenshots', () => {
    test('should capture login page', async ({ loginPage, screenshotHelper }) => {
      await loginPage.goto();

      await screenshotHelper.takeFullPage('login-page');
    });

    test('should capture login error state', async ({ loginPage, screenshotHelper }) => {
      await loginPage.goto();
      await loginPage.login('invalid@test.com', 'wrongpassword');

      // Wait for error to appear
      await loginPage.page.waitForTimeout(500);

      await screenshotHelper.takeFullPage('login-error');
    });

    test('should capture login loading state', async ({ loginPage, apiMocker, screenshotHelper }) => {
      await loginPage.goto();

      await apiMocker.mockSlowResponse('**/auth/login', { token: 'test' }, 5000);

      await loginPage.fillEmail('test@test.com');
      await loginPage.fillPassword('password');
      await loginPage.submit();

      await screenshotHelper.takeFullPage('login-loading');
    });
  });

  test.describe('Home Page Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture home page', async ({ homePage, screenshotHelper }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeFullPage('home-page');
    });

    test('should capture home page on mobile', async ({ homePage, screenshotHelper, page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeFullPage('home-page-mobile');
    });

    test('should capture empty home state', async ({ homePage, apiMocker, screenshotHelper }) => {
      await apiMocker.mockEmpty('**/expenses**');

      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeFullPage('home-empty');
    });
  });

  test.describe('Add Expense Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture add expense form', async ({ addExpensePage, screenshotHelper }) => {
      await addExpensePage.goto();

      await screenshotHelper.takeFullPage('add-expense-form');
    });

    test('should capture form with data', async ({ addExpensePage, screenshotHelper }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Dinner', '75.50');
      await addExpensePage.selectSplitType('equal');

      await screenshotHelper.takeFullPage('add-expense-filled');
    });

    test('should capture split type options', async ({ addExpensePage, screenshotHelper }) => {
      await addExpensePage.goto();

      await addExpensePage.fillBasicDetails('Test', '100');

      // Capture each split type
      await addExpensePage.selectSplitType('equal');
      await screenshotHelper.takeViewport('split-type-equal');

      await addExpensePage.selectSplitType('percentage');
      await screenshotHelper.takeViewport('split-type-percentage');

      await addExpensePage.selectSplitType('exact');
      await screenshotHelper.takeViewport('split-type-exact');
    });
  });

  test.describe('Groups Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture groups list', async ({ groupsPage, screenshotHelper }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await screenshotHelper.takeFullPage('groups-list');
    });

    test('should capture create group dialog', async ({ groupsPage, screenshotHelper }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      await screenshotHelper.takeViewport('create-group-dialog');
    });

    test('should capture empty groups state', async ({ groupsPage, apiMocker, screenshotHelper }) => {
      await apiMocker.mockEmpty('**/groups**');

      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await screenshotHelper.takeFullPage('groups-empty');
    });
  });

  test.describe('Expenses List Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture expenses list', async ({ expensesPage, screenshotHelper }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      await screenshotHelper.takeFullPage('expenses-list');
    });

    test('should capture expenses loading', async ({ expensesPage, apiMocker, screenshotHelper }) => {
      await apiMocker.mockSlowResponse('**/expenses**', { data: [] }, 5000);

      await expensesPage.goto();

      await screenshotHelper.takeViewport('expenses-loading');
    });
  });

  test.describe('Balances Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture balances page', async ({ balancesPage, screenshotHelper }) => {
      await balancesPage.goto();
      await balancesPage.waitForLoad();

      await screenshotHelper.takeFullPage('balances-page');
    });
  });

  test.describe('Account Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture account page', async ({ accountPage, screenshotHelper }) => {
      await accountPage.goto();

      await screenshotHelper.takeFullPage('account-page');
    });
  });

  test.describe('Error State Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture server error state', async ({ expensesPage, apiMocker, screenshotHelper }) => {
      await apiMocker.mockServerError('**/expenses**');

      await expensesPage.goto();
      await expensesPage.page.waitForTimeout(1000);

      await screenshotHelper.takeFullPage('server-error');
    });

    test('should capture network error state', async ({ expensesPage, apiMocker, screenshotHelper }) => {
      await apiMocker.mockNetworkFailure('**/expenses**');

      await expensesPage.goto();
      await expensesPage.page.waitForTimeout(1000);

      await screenshotHelper.takeFullPage('network-error');
    });
  });

  test.describe('Responsive Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture desktop view', async ({ homePage, screenshotHelper, page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeFullPage('home-desktop');
    });

    test('should capture tablet view', async ({ homePage, screenshotHelper, page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeFullPage('home-tablet');
    });

    test('should capture mobile view', async ({ homePage, screenshotHelper, page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeFullPage('home-mobile');
    });
  });

  test.describe('Visual Regression Setup', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should match login page snapshot', async ({ loginPage, page }) => {
      await page.context().clearCookies();
      await loginPage.goto();

      // Use Playwright's built-in visual comparison
      await expect(page).toHaveScreenshot('login-baseline.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match home page snapshot', async ({ homePage, page }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      await expect(page).toHaveScreenshot('home-baseline.png', {
        fullPage: true,
        animations: 'disabled',
        mask: [page.locator('[data-testid="timestamp"]')] // Mask dynamic content
      });
    });
  });

  test.describe('Component Screenshots', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should capture bottom navigation', async ({ homePage, screenshotHelper }) => {
      await homePage.goto();
      await homePage.waitForLoad();

      await screenshotHelper.takeElement('nav', 'bottom-navigation');
    });

    test('should capture expense card', async ({ expensesPage, screenshotHelper }) => {
      await expensesPage.goto();
      await expensesPage.waitForLoad();

      const count = await expensesPage.getExpenseCount();
      if (count > 0) {
        await screenshotHelper.takeElement('[data-testid="expense-card"]', 'expense-card');
      }
    });
  });
});

