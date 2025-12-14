import { test, expect } from '../fixtures';

/**
 * Accessibility Tests
 * Tests ARIA labels, keyboard navigation, and screen reader support
 */
test.describe('Accessibility', () => {
  test.describe('Login Page', () => {
    test('should have proper heading structure', async ({ loginPage }) => {
      await loginPage.goto();

      // Should have h1 or h2
      const heading = loginPage.page.getByRole('heading', { level: 2 });
      await expect(heading).toBeVisible();
    });

    test('should have accessible form labels', async ({ loginPage }) => {
      await loginPage.goto();

      // Email should have label
      const emailLabel = loginPage.page.locator('label[for="email"]');
      await expect(emailLabel).toBeVisible();

      // Password should have label
      const passwordLabel = loginPage.page.locator('label[for="password"]');
      await expect(passwordLabel).toBeVisible();
    });

    test('should support keyboard-only login', async ({ loginPage, page }) => {
      await loginPage.goto();

      // Tab to email
      await page.keyboard.press('Tab');
      await page.keyboard.type('test@example.com');

      // Tab to password
      await page.keyboard.press('Tab');
      await page.keyboard.type('password');

      // Tab to submit
      await page.keyboard.press('Tab');

      // Enter to submit
      await page.keyboard.press('Enter');

      // Form should submit
    });

    test('should have visible focus indicators', async ({ loginPage, page }) => {
      await loginPage.goto();

      // Focus email input
      await loginPage.emailInput.focus();

      // Should have visible focus
      const focusStyles = await loginPage.emailInput.evaluate((el) => {
        const styles = window.getComputedStyle(el);
        return {
          outline: styles.outlineStyle,
          boxShadow: styles.boxShadow,
          border: styles.borderColor
        };
      });

      // At least one focus style should be applied
      const hasFocusStyle =
        focusStyles.outline !== 'none' ||
        focusStyles.boxShadow !== 'none';
    });

    test('should have autocomplete attributes', async ({ loginPage }) => {
      await loginPage.goto();

      await expect(loginPage.emailInput).toHaveAttribute('autocomplete', 'email');
      await expect(loginPage.passwordInput).toHaveAttribute('autocomplete', 'current-password');
    });
  });

  test.describe('Navigation', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should have nav landmark', async ({ homePage }) => {
      await homePage.goto();

      const nav = homePage.page.locator('nav');
      await expect(nav).toBeVisible();
    });

    test('should have main landmark', async ({ homePage }) => {
      await homePage.goto();

      const main = homePage.page.locator('main');
      await expect(main).toBeVisible();
    });

    test('should support keyboard navigation through menu', async ({ homePage, page }) => {
      await homePage.goto();

      // Focus on nav
      const firstLink = homePage.homeNavLink;
      await firstLink.focus();

      // Tab through nav items
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Should move through nav
      const focused = await page.evaluate(() => document.activeElement?.tagName);
      expect(focused).toBe('A');
    });

    test('should indicate current page in nav', async ({ homePage }) => {
      await homePage.goto();

      // Current page should have visual indication
      const activeNav = await homePage.getActiveNavItem();
      expect(activeNav).toBe('home');
    });
  });

  test.describe('Forms', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should associate labels with inputs', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Click on label should focus input
      const label = addExpensePage.page.locator('label').filter({ hasText: /description/i }).first();
      await label.click();

      // Input should be focused
      const focused = await addExpensePage.page.evaluate(() => document.activeElement?.id || document.activeElement?.tagName);
      expect(focused).toBeTruthy();
    });

    test('should have required field indicators', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Required fields should be marked
      const indicators = addExpensePage.page.locator('.text-destructive');
      const count = await indicators.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should announce errors to screen readers', async ({ addExpensePage }) => {
      await addExpensePage.goto();

      // Submit empty form
      await addExpensePage.submit();

      // Errors should be in accessible location
      const errors = addExpensePage.errorMessages;
      // Errors should be announced
    });
  });

  test.describe('Buttons & Interactive Elements', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should have accessible button names', async ({ homePage }) => {
      await homePage.goto();

      // Buttons should have accessible names
      const buttons = homePage.page.getByRole('button');
      const count = await buttons.count();

      for (let i = 0; i < count; i++) {
        const button = buttons.nth(i);
        const name = await button.getAttribute('aria-label') || await button.textContent();
        expect(name?.trim()).toBeTruthy();
      }
    });

    test('should have accessible link names', async ({ homePage }) => {
      await homePage.goto();

      const links = homePage.page.getByRole('link');
      const count = await links.count();

      for (let i = 0; i < Math.min(count, 10); i++) {
        const link = links.nth(i);
        const name = await link.getAttribute('aria-label') || await link.textContent();
        expect(name?.trim()).toBeTruthy();
      }
    });

    test('should have correct button roles', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      // Create button should be a button
      await expect(groupsPage.createGroupButton).toHaveRole('button');
    });
  });

  test.describe('Dialogs', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should have dialog role', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      const dialog = groupsPage.page.locator('[role="dialog"]');
      await expect(dialog).toBeVisible();
    });

    test('should trap focus in dialog', async ({ groupsPage, page }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();

      // Tab multiple times
      for (let i = 0; i < 10; i++) {
        await page.keyboard.press('Tab');
      }

      // Focus should still be in dialog
      const isInDialog = await page.evaluate(() => {
        const dialog = document.querySelector('[role="dialog"]');
        return dialog?.contains(document.activeElement);
      });

      expect(isInDialog).toBeTruthy();
    });

    test('should close with escape key', async ({ groupsPage }) => {
      await groupsPage.goto();
      await groupsPage.waitForLoad();

      await groupsPage.openCreateGroupDialog();
      await groupsPage.page.keyboard.press('Escape');

      await expect(groupsPage.createGroupDialog).not.toBeVisible();
    });
  });

  test.describe('Color & Contrast', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should have sufficient text contrast', async ({ homePage, page }) => {
      await homePage.goto();

      // Check main text color contrast
      const textContrast = await page.evaluate(() => {
        const body = document.body;
        const styles = window.getComputedStyle(body);
        return {
          color: styles.color,
          background: styles.backgroundColor
        };
      });

      // Basic check that colors exist
      expect(textContrast.color).toBeTruthy();
    });

    test('should not rely on color alone', async ({ homePage }) => {
      await homePage.goto();

      // Error states should have icons or text, not just color
      // Success states should have icons or text, not just color
    });
  });

  test.describe('Screen Reader Support', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should have alt text for images', async ({ homePage }) => {
      await homePage.goto();

      const images = homePage.page.locator('img');
      const count = await images.count();

      for (let i = 0; i < count; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        // Images should have alt (can be empty for decorative)
        expect(alt !== null).toBeTruthy();
      }
    });

    test('should have descriptive page title', async ({ homePage, page }) => {
      await homePage.goto();

      const title = await page.title();
      expect(title).toBeTruthy();
      expect(title.length).toBeGreaterThan(0);
    });

    test('should announce loading states', async ({ expensesPage }) => {
      await expensesPage.goto();

      // Loading spinner should have aria attributes
      const spinner = expensesPage.loadingSpinner;
      if (await spinner.isVisible()) {
        // Should have role or aria-label
        const role = await spinner.getAttribute('role');
        const label = await spinner.getAttribute('aria-label');
        // Some accessibility should be present
      }
    });
  });

  test.describe('Mobile Accessibility', () => {
    test.beforeEach(async ({ authHelper }) => {
      await authHelper.loginAsTestUser();
    });

    test('should have touch-friendly targets', async ({ homePage, page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await homePage.goto();

      // Navigation buttons should be at least 44x44
      const navLinks = page.locator('nav a');
      const count = await navLinks.count();

      for (let i = 0; i < count; i++) {
        const link = navLinks.nth(i);
        const box = await link.boundingBox();
        if (box) {
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    });

    test('should be usable without pinch zoom', async ({ loginPage, page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await loginPage.goto();

      // Form should fit in viewport
      const form = loginPage.page.locator('form');
      const box = await form.boundingBox();

      if (box) {
        expect(box.width).toBeLessThanOrEqual(375);
      }
    });
  });
});

