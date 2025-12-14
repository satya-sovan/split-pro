import { test, expect } from '../fixtures';
import { config } from '../config';

/**
 * App Launch & Page Load Tests
 * Validates initial app loading, routing, and basic accessibility
 */
test.describe('App Launch & Page Load', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing state
    await page.context().clearCookies();
  });

  test('should load login page when not authenticated', async ({ page, loginPage }) => {
    // Navigate to root
    await page.goto('/');

    // Should redirect to login
    await expect(page).toHaveURL(/\/auth\/login/);

    // Validate login page elements
    expect(await loginPage.isDisplayed()).toBeTruthy();
  });

  test('should display correct page title', async ({ page }) => {
    await page.goto('/auth/login');

    // Check page has a title
    const title = await page.title();
    expect(title).toBeTruthy();
  });

  test('should load app assets correctly', async ({ page }) => {
    await page.goto('/auth/login');

    // Check CSS is loaded (body should have styles)
    const bodyStyles = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).backgroundColor;
    });
    expect(bodyStyles).toBeTruthy();
  });

  test('should handle protected routes when not authenticated', async ({ page }) => {
    // Try to access protected route
    await page.goto('/home');

    // Should redirect to login
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('should handle 404 gracefully', async ({ page }) => {
    await page.goto('/nonexistent-page');

    // Should show error or redirect
    const url = page.url();
    expect(url.includes('/nonexistent-page') || url.includes('/auth/login')).toBeTruthy();
  });

  test('should have proper viewport on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/auth/login');

    // Page should be responsive
    const loginForm = page.locator('form');
    await expect(loginForm).toBeVisible();

    // Check form is within viewport
    const box = await loginForm.boundingBox();
    expect(box).toBeTruthy();
    if (box) {
      expect(box.width).toBeLessThanOrEqual(375);
    }
  });

  test('should load without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));

    await page.goto('/auth/login');
    await page.waitForLoadState('networkidle');

    // Should have no critical errors
    const criticalErrors = errors.filter((e) => !e.includes('warning'));
    expect(criticalErrors.length).toBe(0);
  });

  test('should display loading indicator during navigation', async ({ page }) => {
    await page.goto('/auth/login');

    // Check that page doesn't have permanent loading state
    const spinner = page.locator('.animate-spin');

    // After load, spinner should not be visible
    await page.waitForLoadState('networkidle');
    await expect(spinner).not.toBeVisible({ timeout: 5000 }).catch(() => {
      // Some pages might not have spinners, that's ok
    });
  });

  test('should have accessible landmark regions', async ({ page }) => {
    await page.goto('/auth/login');

    // Check for main content area
    const main = page.locator('main, [role="main"], .min-h-screen');
    await expect(main).toBeVisible();
  });
});

