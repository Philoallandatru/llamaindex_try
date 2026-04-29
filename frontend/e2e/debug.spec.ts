import { test, expect } from '@playwright/test';

test('debug page load', async ({ page }) => {
  // Capture console messages
  page.on('console', msg => {
    console.log(`[BROWSER ${msg.type()}]:`, msg.text());
  });

  // Capture page errors
  page.on('pageerror', err => {
    console.error('[PAGE ERROR]:', err.message);
  });

  // Navigate to the app
  await page.goto('/');

  // Wait a bit for the app to load
  await page.waitForTimeout(3000);

  // Take a screenshot
  await page.screenshot({ path: 'test-results/debug-screenshot.png', fullPage: true });

  // Get the page HTML
  const html = await page.content();
  console.log('[PAGE HTML LENGTH]:', html.length);
  console.log('[PAGE HTML PREVIEW]:', html.substring(0, 500));

  // Check if root element exists
  const root = await page.locator('#root').count();
  console.log('[ROOT ELEMENT COUNT]:', root);

  // Check if there's any text content
  const bodyText = await page.locator('body').textContent();
  console.log('[BODY TEXT]:', bodyText?.substring(0, 200));
});
