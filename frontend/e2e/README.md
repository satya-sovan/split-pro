# SplitPro E2E Test Suite

End-to-end UI automation tests using Playwright.

## 📁 Project Structure

```
e2e/
├── config/                 # Environment configuration
│   └── index.ts
├── fixtures/               # Test fixtures and data
│   ├── index.ts
│   ├── test-fixtures.ts    # Playwright custom fixtures
│   └── test-data.ts        # Mock data for tests
├── pages/                  # Page Object Models
│   ├── BasePage.ts
│   ├── LoginPage.ts
│   ├── RegisterPage.ts
│   ├── HomePage.ts
│   ├── AddExpensePage.ts
│   ├── ExpensesPage.ts
│   ├── ExpenseDetailsPage.ts
│   ├── GroupsPage.ts
│   ├── GroupDetailsPage.ts
│   ├── BalancesPage.ts
│   ├── AccountPage.ts
│   └── index.ts
├── tests/                  # Test files
│   ├── app-launch.spec.ts
│   ├── auth.spec.ts
│   ├── navigation.spec.ts
│   ├── crud.spec.ts
│   ├── forms.spec.ts
│   ├── tables.spec.ts
│   ├── modals.spec.ts
│   ├── error-handling.spec.ts
│   ├── accessibility.spec.ts
│   └── visual.spec.ts
├── utils/                  # Helper utilities
│   ├── auth.ts
│   ├── api-mocker.ts
│   ├── helpers.ts
│   └── index.ts
├── global-setup.ts         # Global test setup
├── playwright.config.ts    # Playwright configuration
├── package.json
├── tsconfig.json
└── .env.example
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- pnpm

### Installation

```bash
cd frontend/e2e
pnpm install
pnpm exec playwright install
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

## 📋 Running Tests

### ⚠️ IMPORTANT: Start the Frontend First!

Before running tests, start the frontend dev server in a **separate terminal**:

```bash
# Terminal 1: Start frontend
cd frontend
pnpm dev
```

Wait until you see `Local: http://localhost:5173` then run tests in another terminal.

### All Tests (Chromium only)

```bash
# Terminal 2: Run tests
cd frontend/e2e
pnpm test
```

### With UI Mode

```bash
pnpm test:ui
```

### Headed Mode (See Browser)

```bash
pnpm test:headed
```

### Debug Mode

```bash
pnpm test:debug
```

### Specific Browser

```bash
pnpm test:chromium
pnpm test:firefox
pnpm test:webkit
```

### Mobile Tests

```bash
pnpm test:mobile
```

### View Report

```bash
pnpm report
```

## 🧪 Test Coverage

| Category | Tests |
|----------|-------|
| App Launch | Page load, routing, assets |
| Authentication | Login, logout, session persistence |
| Navigation | Menu, deep links, browser history |
| CRUD | Create, read, update, delete |
| Forms | Validation, submission, errors |
| Tables | Pagination, sorting, filtering |
| Modals | Open, close, confirm, cancel |
| Error Handling | API failures, network errors |
| Accessibility | ARIA, keyboard, screen readers |
| Visual | Screenshots, responsive design |

## 🏗️ Page Object Model

Each page has a corresponding Page Object that encapsulates:

- Element locators
- User actions
- Assertions

Example usage:

```typescript
import { test, expect } from '../fixtures';

test('login flow', async ({ loginPage, page }) => {
  await loginPage.goto();
  await loginPage.login('user@test.com', 'password');
  await expect(page).toHaveURL(/\/home/);
});
```

## 🔧 Fixtures

Custom fixtures provide:

- **Page Objects**: Pre-instantiated for each test
- **AuthHelper**: Login/logout utilities
- **ApiMocker**: Mock API responses
- **ScreenshotHelper**: Visual testing utilities

## 🎭 API Mocking

Mock API responses for edge cases:

```typescript
test('handle error', async ({ apiMocker }) => {
  await apiMocker.mockServerError('**/expenses**');
  // Test error handling
});
```

## 📸 Screenshots

Screenshots are captured:

- Automatically on test failure
- Manually via `screenshotHelper`
- For visual regression testing

Output: `test-results/screenshots/`

## 🎥 Videos & Traces

- Videos: Retained on failure
- Traces: Captured on first retry

View traces:

```bash
pnpm exec playwright show-trace test-results/trace.zip
```

## 🔄 CI/CD Integration

GitHub Actions example:

```yaml
- name: Install Playwright
  run: pnpm exec playwright install --with-deps

- name: Run E2E Tests
  run: pnpm test
  env:
    BASE_URL: ${{ vars.BASE_URL }}
    CI: true

- name: Upload Report
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: playwright-report
    path: playwright-report/
```

## 📝 Writing Tests

1. Create test file in `tests/`
2. Import fixtures: `import { test, expect } from '../fixtures'`
3. Use page objects for interactions
4. Use auto-waiting (no manual sleeps)

```typescript
import { test, expect } from '../fixtures';

test.describe('Feature', () => {
  test.beforeEach(async ({ authHelper }) => {
    await authHelper.loginAsTestUser();
  });

  test('should do something', async ({ homePage }) => {
    await homePage.goto();
    // assertions
  });
});
```

## 🐛 Debugging

1. **UI Mode**: `pnpm test:ui`
2. **Debug Mode**: `pnpm test:debug`
3. **Trace Viewer**: Open trace files in Playwright UI
4. **Console Logs**: Check test output
5. **Screenshots**: Review failure screenshots

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/docs)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model](https://playwright.dev/docs/pom)
- [API Testing](https://playwright.dev/docs/api-testing)

