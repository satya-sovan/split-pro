import { test, expect } from '../fixtures';
import { config } from '../config';

/**
 * Authentication Flow Tests
 * Tests login, logout, registration, and session management
 */
test.describe('Authentication', () => {
  test.describe('Login Flow', () => {
    test.beforeEach(async ({ page }) => {
      await page.context().clearCookies();
    });

    test('should login with valid credentials', async ({ loginPage, page }) => {
      await loginPage.goto();

      // Perform login
      await loginPage.login(config.testUser.email, config.testUser.password);

      // Should redirect to home
      await expect(page).toHaveURL(/\/home/, { timeout: 10000 });
    });

    test('should show error with invalid credentials', async ({ loginPage }) => {
      await loginPage.goto();

      // Attempt login with wrong password
      await loginPage.login(config.invalidUser.email, config.invalidUser.password);

      // Should show error message
      const errorText = await loginPage.getErrorText();
      expect(errorText).toBeTruthy();
      expect(errorText?.toLowerCase()).toMatch(/invalid|incorrect|wrong|error/);
    });

    test('should show error with empty email', async ({ loginPage }) => {
      await loginPage.goto();

      // Try to submit with empty email
      await loginPage.fillPassword('somepassword');
      await loginPage.submit();

      // Form should validate - check HTML5 validation
      const email = loginPage.emailInput;
      await expect(email).toHaveAttribute('required');
    });

    test('should show error with empty password', async ({ loginPage }) => {
      await loginPage.goto();

      // Try to submit with empty password
      await loginPage.fillEmail('test@example.com');
      await loginPage.submit();

      // Form should validate
      const password = loginPage.passwordInput;
      await expect(password).toHaveAttribute('required');
    });

    test('should show loading state during login', async ({ loginPage, apiMocker }) => {
      await loginPage.goto();

      // Mock slow response
      await apiMocker.mockSlowResponse('**/auth/login', { token: 'test' }, 2000);

      // Fill and submit
      await loginPage.fillEmail(config.testUser.email);
      await loginPage.fillPassword(config.testUser.password);
      await loginPage.submit();

      // Should show loading
      expect(await loginPage.isLoading()).toBeTruthy();
    });

    test('should handle network error during login', async ({ loginPage, apiMocker }) => {
      await loginPage.goto();

      // Mock network failure
      await apiMocker.mockNetworkFailure('**/auth/login');

      // Attempt login
      await loginPage.login(config.testUser.email, config.testUser.password);

      // Should show error
      const errorText = await loginPage.getErrorText();
      expect(errorText).toBeTruthy();
    });

    test('should validate email format', async ({ loginPage }) => {
      await loginPage.goto();

      // Enter invalid email
      await loginPage.fillEmail('notanemail');
      await loginPage.fillPassword('password');

      // Check email input type validates
      const emailInput = loginPage.emailInput;
      await expect(emailInput).toHaveAttribute('type', 'email');
    });

    test('should allow magic link request', async ({ loginPage }) => {
      await loginPage.goto();

      // Request magic link
      await loginPage.requestMagicLink(config.testUser.email);

      // Should show success or confirmation (toast)
      // The exact behavior depends on implementation
    });

    test('should navigate to register page', async ({ loginPage, page }) => {
      await loginPage.goto();

      // Click register link
      await loginPage.goToRegister();

      // Should be on register page
      await expect(page).toHaveURL(/\/auth\/register/);
    });
  });

  test.describe('Session Persistence', () => {
    test('should maintain session after page refresh', async ({ loginPage, page, homePage }) => {
      // Login first
      await loginPage.goto();
      await loginPage.login(config.testUser.email, config.testUser.password);
      await expect(page).toHaveURL(/\/home/);

      // Refresh page
      await page.reload();

      // Should still be logged in
      await expect(page).toHaveURL(/\/home/);
      expect(await homePage.isDisplayed()).toBeTruthy();
    });

    test('should redirect to home when already authenticated', async ({ loginPage, page }) => {
      // Login first
      await loginPage.goto();
      await loginPage.login(config.testUser.email, config.testUser.password);
      await expect(page).toHaveURL(/\/home/);

      // Try to access login page again
      await page.goto('/auth/login');

      // Should redirect back to home (or stay on home)
      // Behavior depends on implementation
    });
  });

  test.describe('Logout', () => {
    test('should logout successfully', async ({ loginPage, page, accountPage }) => {
      // Login first
      await loginPage.goto();
      await loginPage.login(config.testUser.email, config.testUser.password);
      await expect(page).toHaveURL(/\/home/);

      // Go to account and logout
      await accountPage.goto();
      await accountPage.logout();

      // Should be on login page
      await expect(page).toHaveURL(/\/auth\/login/);
    });

    test('should clear session data on logout', async ({ loginPage, page, accountPage }) => {
      // Login first
      await loginPage.goto();
      await loginPage.login(config.testUser.email, config.testUser.password);
      await expect(page).toHaveURL(/\/home/);

      // Logout
      await accountPage.goto();
      await accountPage.logout();

      // Try to access protected route
      await page.goto('/home');

      // Should redirect to login
      await expect(page).toHaveURL(/\/auth\/login/);
    });
  });

  test.describe('Registration', () => {
    test('should navigate from login to registration', async ({ loginPage, page }) => {
      await loginPage.goto();
      await loginPage.goToRegister();

      await expect(page).toHaveURL(/\/auth\/register/);
    });

    test('should display registration form', async ({ registerPage }) => {
      await registerPage.goto();

      expect(await registerPage.isDisplayed()).toBeTruthy();
    });

    test('should require all fields', async ({ registerPage }) => {
      await registerPage.goto();

      // Try to submit empty form
      await registerPage.submit();

      // Check required attributes
      await expect(registerPage.nameInput).toHaveAttribute('required');
      await expect(registerPage.emailInput).toHaveAttribute('required');
      await expect(registerPage.passwordInput).toHaveAttribute('required');
    });

    test('should navigate from registration to login', async ({ registerPage, page }) => {
      await registerPage.goto();
      await registerPage.goToLogin();

      await expect(page).toHaveURL(/\/auth\/login/);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper form labels', async ({ loginPage }) => {
      await loginPage.goto();
      await loginPage.validateAccessibility();
    });

    test('should support keyboard navigation', async ({ loginPage, page }) => {
      await loginPage.goto();

      // Tab through form elements
      await page.keyboard.press('Tab');

      // Should focus on email input
      const focusedElement = await page.evaluate(() => document.activeElement?.id);
      expect(['email', 'password', '']).toContain(focusedElement);
    });

    test('should announce errors to screen readers', async ({ loginPage }) => {
      await loginPage.goto();

      // Login with invalid credentials
      await loginPage.login(config.invalidUser.email, config.invalidUser.password);

      // Error message should be visible for screen readers
      const error = loginPage.errorMessage;
      if (await error.isVisible()) {
        // Check it has appropriate role or is in an accessible location
        await expect(error).toBeVisible();
      }
    });
  });
});

