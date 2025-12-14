import { test as base, expect } from '@playwright/test';
import {
  LoginPage,
  RegisterPage,
  HomePage,
  AddExpensePage,
  GroupsPage,
  GroupDetailsPage,
  ExpensesPage,
  ExpenseDetailsPage,
  BalancesPage,
  AccountPage,
} from '../pages';
import { AuthHelper, ApiMocker, ScreenshotHelper } from '../utils';

type SAHASplitFixtures = {
  loginPage: LoginPage;
  registerPage: RegisterPage;
  homePage: HomePage;
  addExpensePage: AddExpensePage;
  groupsPage: GroupsPage;
  groupDetailsPage: GroupDetailsPage;
  expensesPage: ExpensesPage;
  expenseDetailsPage: ExpenseDetailsPage;
  balancesPage: BalancesPage;
  accountPage: AccountPage;
  authHelper: AuthHelper;
  apiMocker: ApiMocker;
  screenshotHelper: ScreenshotHelper;
  authenticatedPage: void;
};

export const test = base.extend<SAHASplitFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  registerPage: async ({ page }, use) => {
    await use(new RegisterPage(page));
  },

  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },

  addExpensePage: async ({ page }, use) => {
    await use(new AddExpensePage(page));
  },

  groupsPage: async ({ page }, use) => {
    await use(new GroupsPage(page));
  },

  groupDetailsPage: async ({ page }, use) => {
    await use(new GroupDetailsPage(page));
  },

  expensesPage: async ({ page }, use) => {
    await use(new ExpensesPage(page));
  },

  expenseDetailsPage: async ({ page }, use) => {
    await use(new ExpenseDetailsPage(page));
  },

  balancesPage: async ({ page }, use) => {
    await use(new BalancesPage(page));
  },

  accountPage: async ({ page }, use) => {
    await use(new AccountPage(page));
  },

  authHelper: async ({ page, context }, use) => {
    await use(new AuthHelper(page, context));
  },

  apiMocker: async ({ page }, use) => {
    const mocker = new ApiMocker(page);
    await use(mocker);
    await mocker.clearMocks();
  },

  screenshotHelper: async ({ page }, use) => {
    await use(new ScreenshotHelper(page, 'test-results/screenshots'));
  },

  authenticatedPage: async ({ page, context }, use) => {
    const authHelper = new AuthHelper(page, context);
    await authHelper.loginAsTestUser();
    await use();
  },
});

export { expect };

