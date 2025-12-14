import { FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests
 * Runs once before all tests
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global test setup...');

  // Environment validation
  const requiredEnvVars = ['BASE_URL'];
  const missingVars = requiredEnvVars.filter(
    (varName) => !process.env[varName] && varName !== 'BASE_URL'
  );

  if (missingVars.length > 0) {
    console.warn(`⚠️  Missing optional environment variables: ${missingVars.join(', ')}`);
  }

  // Log configuration
  const baseUrl = config.projects[0]?.use?.baseURL || process.env.BASE_URL || 'http://localhost:8012';
  console.log(`📍 Base URL: ${baseUrl}`);
  console.log(`🖥️  Projects: ${config.projects.map((p) => p.name).join(', ')}`);

  console.log('✅ Global setup complete');
}

export default globalSetup;

