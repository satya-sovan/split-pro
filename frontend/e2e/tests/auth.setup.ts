import { test as setup, expect } from '@playwright/test';
import { config } from '../config';

const authFile = 'playwright/.auth/user.json';

/**
 * Authentication setup - runs once before all tests
 * Logs in and saves the authentication state
 */
setup('authenticate', async ({ page }) => {
  // Go to login page
  await page.goto('/auth/login');

  // Fill in credentials
  await page.locator('#email').fill(config.testUser.email);
  await page.locator('#password').fill(config.testUser.password);

  // Submit login
  await page.locator('button[type="submit"]').click();

  // Wait for login to complete - should redirect to home
  await page.waitForURL(/\/home/, { timeout: 15000 });

  // Verify we're logged in
  await expect(page).toHaveURL(/\/home/);

  // Save authentication state
  await page.context().storageState({ path: authFile });
});

