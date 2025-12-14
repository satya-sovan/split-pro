import { Page, Route } from '@playwright/test';

/**
 * API mocking utilities for testing error states and edge cases
 */
export class ApiMocker {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Mock API endpoint with custom response
   */
  async mockEndpoint(
    urlPattern: string | RegExp,
    response: {
      status?: number;
      body?: unknown;
      headers?: Record<string, string>;
    }
  ): Promise<void> {
    await this.page.route(urlPattern, async (route: Route) => {
      await route.fulfill({
        status: response.status || 200,
        contentType: 'application/json',
        headers: response.headers,
        body: JSON.stringify(response.body || {}),
      });
    });
  }

  /**
   * Mock API to return error
   */
  async mockError(urlPattern: string | RegExp, statusCode: number, message: string): Promise<void> {
    await this.mockEndpoint(urlPattern, {
      status: statusCode,
      body: { error: message, message },
    });
  }

  /**
   * Mock network failure
   */
  async mockNetworkFailure(urlPattern: string | RegExp): Promise<void> {
    await this.page.route(urlPattern, async (route: Route) => {
      await route.abort('failed');
    });
  }

  /**
   * Mock timeout
   */
  async mockTimeout(urlPattern: string | RegExp, delayMs: number = 30000): Promise<void> {
    await this.page.route(urlPattern, async (route: Route) => {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      await route.abort('timedout');
    });
  }

  /**
   * Mock slow response
   */
  async mockSlowResponse(
    urlPattern: string | RegExp,
    response: unknown,
    delayMs: number = 3000
  ): Promise<void> {
    await this.page.route(urlPattern, async (route: Route) => {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  }

  /**
   * Mock login failure
   */
  async mockLoginFailure(): Promise<void> {
    await this.mockError('**/api/**/auth/login', 401, 'Invalid credentials');
  }

  /**
   * Mock server error
   */
  async mockServerError(urlPattern: string | RegExp): Promise<void> {
    await this.mockError(urlPattern, 500, 'Internal server error');
  }

  /**
   * Mock expenses endpoint
   */
  async mockExpenses(expenses: unknown[]): Promise<void> {
    await this.mockEndpoint('**/api/**/expenses**', {
      body: { data: expenses, total: expenses.length },
    });
  }

  /**
   * Mock groups endpoint
   */
  async mockGroups(groups: unknown[]): Promise<void> {
    await this.mockEndpoint('**/api/**/groups**', {
      body: { data: groups, total: groups.length },
    });
  }

  /**
   * Mock empty response
   */
  async mockEmpty(urlPattern: string | RegExp): Promise<void> {
    await this.mockEndpoint(urlPattern, {
      body: { data: [], total: 0 },
    });
  }

  /**
   * Clear all mocks
   */
  async clearMocks(): Promise<void> {
    await this.page.unrouteAll();
  }

  /**
   * Intercept and log API calls
   */
  async interceptAndLog(urlPattern: string | RegExp): Promise<void> {
    await this.page.route(urlPattern, async (route: Route) => {
      const request = route.request();
      console.log(`API Call: ${request.method()} ${request.url()}`);
      console.log(`Body: ${request.postData()}`);
      await route.continue();
    });
  }
}

/**
 * Factory function to create API mocker
 */
export function createApiMocker(page: Page): ApiMocker {
  return new ApiMocker(page);
}
