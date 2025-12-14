import { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export class ScreenshotHelper {
  private page: Page;
  private outputDir: string;

  constructor(page: Page, outputDir: string = 'screenshots') {
    this.page = page;
    this.outputDir = outputDir;
    this.ensureDir();
  }

  private ensureDir(): void {
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  private getTimestamp(): string {
    return new Date().toISOString().replace(/[:.]/g, '-');
  }

  async takeFullPage(name: string): Promise<string> {
    const filename = `${name}-${this.getTimestamp()}.png`;
    const filepath = path.join(this.outputDir, filename);
    await this.page.screenshot({ path: filepath, fullPage: true });
    return filepath;
  }

  async takeViewport(name: string): Promise<string> {
    const filename = `${name}-${this.getTimestamp()}.png`;
    const filepath = path.join(this.outputDir, filename);
    await this.page.screenshot({ path: filepath, fullPage: false });
    return filepath;
  }

  async takeElement(selector: string, name: string): Promise<string> {
    const element = this.page.locator(selector);
    const filename = `${name}-${this.getTimestamp()}.png`;
    const filepath = path.join(this.outputDir, filename);
    await element.screenshot({ path: filepath });
    return filepath;
  }

  async takeForComparison(name: string): Promise<Buffer> {
    return this.page.screenshot({ fullPage: true });
  }
}

export function getToday(): string {
  return new Date().toISOString().split('T')[0];
}

export function getYesterday(): string {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  return date.toISOString().split('T')[0];
}

export function getFutureDate(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().split('T')[0];
}

export function getPastDate(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date.toISOString().split('T')[0];
}

export function generateRandomEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(7);
  return `test-${timestamp}-${random}@example.com`;
}

export function generateRandomString(length: number = 10): string {
  return Math.random().toString(36).substring(2, 2 + length);
}

export function generateRandomAmount(min: number = 1, max: number = 1000): string {
  const amount = (Math.random() * (max - min) + min).toFixed(2);
  return amount;
}

export async function waitForCondition(
  condition: () => Promise<boolean>,
  timeout: number = 10000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }
  throw new Error(`Condition not met within ${timeout}ms`);
}

export async function pressShortcut(page: Page, shortcut: string): Promise<void> {
  const keys = shortcut.split('+');
  const modifiers: string[] = [];
  let mainKey = '';

  for (const key of keys) {
    const normalizedKey = key.trim().toLowerCase();
    if (['ctrl', 'control', 'shift', 'alt', 'meta', 'cmd'].includes(normalizedKey)) {
      modifiers.push(normalizedKey === 'ctrl' ? 'Control' : normalizedKey.charAt(0).toUpperCase() + normalizedKey.slice(1));
    } else {
      mainKey = key.trim();
    }
  }

  for (const mod of modifiers) {
    await page.keyboard.down(mod);
  }

  await page.keyboard.press(mainKey);

  for (const mod of modifiers.reverse()) {
    await page.keyboard.up(mod);
  }
}
