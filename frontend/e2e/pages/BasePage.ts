import { Page, Locator } from '@playwright/test';

/**
 * Base Page Object class with common functionality
 */
export abstract class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  abstract goto(): Promise<void>;

  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }

  async takeScreenshot(name: string): Promise<Buffer> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    return this.page.screenshot({
      path: `screenshots/${name}-${timestamp}.png`,
      fullPage: true
    });
  }

  async waitForElement(locator: Locator, timeout = 10000): Promise<void> {
    await locator.waitFor({ state: 'visible', timeout });
  }

  async isVisible(locator: Locator): Promise<boolean> {
    return locator.isVisible();
  }

  async getToastMessage(): Promise<string | null> {
    const toast = this.page.locator('[data-sonner-toast]').first();
    if (await toast.isVisible()) {
      return toast.textContent();
    }
    return null;
  }

  async waitForToast(timeout = 5000): Promise<string | null> {
    const toast = this.page.locator('[data-sonner-toast]').first();
    await toast.waitFor({ state: 'visible', timeout });
    return toast.textContent();
  }

  async dismissToast(): Promise<void> {
    const toast = this.page.locator('[data-sonner-toast]').first();
    if (await toast.isVisible()) {
      await toast.click();
    }
  }

  async waitForApiResponse(urlPattern: string | RegExp, timeout = 10000): Promise<void> {
    await this.page.waitForResponse(urlPattern, { timeout });
  }

  async isOnPage(urlPattern: string | RegExp): Promise<boolean> {
    return new RegExp(urlPattern).test(this.page.url());
  }

  getCurrentPath(): string {
    const url = new URL(this.page.url());
    return url.pathname;
  }

  async pressKey(key: string): Promise<void> {
    await this.page.keyboard.press(key);
  }

  async tabToNextElement(): Promise<void> {
    await this.page.keyboard.press('Tab');
  }
}

