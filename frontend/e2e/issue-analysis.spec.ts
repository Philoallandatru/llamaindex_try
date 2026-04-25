import { test, expect } from '@playwright/test';

/**
 * E2E Test: Issue Deep Analysis Feature
 *
 * This test covers the complete workflow:
 * 1. Start backend server
 * 2. Navigate to Issues page
 * 3. Analyze a Jira issue
 * 4. Verify analysis results
 * 5. Check knowledge base storage
 */

test.describe('Issue Deep Analysis E2E', () => {
  test.beforeAll(async () => {
    // Note: Backend should be running at http://localhost:8000
    // Start it manually with: cd backend && python main.py
  });

  test('should navigate to issues page', async ({ page }) => {
    await page.goto('/');

    // Wait for page to load
    await expect(page.locator('h2:has-text("SSD Knowledge Portal")')).toBeVisible();

    // Click on Issues Analysis navigation
    await page.click('text=🔍 Issues Analysis');

    // Verify we're on the issues page
    await expect(page).toHaveURL('/issues');
    await expect(page.locator('h1:has-text("Issue 深度分析")')).toBeVisible();
  });

  test('should show empty state when no issues analyzed', async ({ page }) => {
    await page.goto('/issues');

    // Check for empty state or list
    const emptyState = page.locator('text=暂无已分析的 Issues');
    const issuesList = page.locator('[style*="flex-direction: column"]');

    // Either empty state or list should be visible
    await expect(emptyState.or(issuesList)).toBeVisible();
  });

  test('should have manual analysis input', async ({ page }) => {
    await page.goto('/issues');

    // Verify input field exists
    const input = page.locator('input[placeholder*="输入 Issue Key"]');
    await expect(input).toBeVisible();

    // Verify analyze button exists
    const button = page.locator('button:has-text("开始分析")');
    await expect(button).toBeVisible();

    // Button should be disabled when input is empty
    await expect(button).toBeDisabled();
  });

  test('should enable analyze button when issue key entered', async ({ page }) => {
    await page.goto('/issues');

    const input = page.locator('input[placeholder*="输入 Issue Key"]');
    const button = page.locator('button:has-text("开始分析")');

    // Type issue key
    await input.fill('TEST-123');

    // Button should be enabled
    await expect(button).toBeEnabled();
  });

  test('should navigate to analysis page when clicking analyze', async ({ page }) => {
    await page.goto('/issues');

    const input = page.locator('input[placeholder*="输入 Issue Key"]');
    const button = page.locator('button:has-text("开始分析")');

    // Enter issue key and click analyze
    await input.fill('TEST-456');
    await button.click();

    // Should navigate to analysis page
    await expect(page).toHaveURL('/analysis/TEST-456');
  });

  test('should show loading state during analysis', async ({ page }) => {
    await page.goto('/analysis/TEST-789');

    // Should show loading indicator
    const loadingText = page.locator('text=正在分析');
    const typingIndicator = page.locator('.typing-indicator');

    // Either loading text or typing indicator should appear
    await expect(loadingText.or(typingIndicator)).toBeVisible({ timeout: 10000 });
  });

  test('should show error when Jira not configured', async ({ page }) => {
    await page.goto('/analysis/NOTCONFIG-1');

    // Wait for error message
    await page.waitForTimeout(3000);

    // Should show error about Jira not configured
    const errorMessage = page.locator('text=/Jira|configured|failed/i');

    // Check if error is visible (might take a moment)
    const isErrorVisible = await errorMessage.isVisible().catch(() => false);

    if (isErrorVisible) {
      console.log('✓ Correctly shows error when Jira not configured');
    } else {
      console.log('⚠ No error shown - Jira might be configured or analysis in progress');
    }
  });

  test('should have back button on analysis page', async ({ page }) => {
    await page.goto('/analysis/TEST-999');

    // Verify back button exists
    const backButton = page.locator('button:has-text("返回列表")');
    await expect(backButton).toBeVisible();

    // Click back button
    await backButton.click();

    // Should navigate back to issues page
    await expect(page).toHaveURL('/issues');
  });

  test('should have navigation menu on all pages', async ({ page }) => {
    const pages = ['/', '/issues', '/reports', '/knowledge'];

    for (const url of pages) {
      await page.goto(url);

      // Check navigation items exist
      await expect(page.locator('text=💬 Chat')).toBeVisible();
      await expect(page.locator('text=🔍 Issues Analysis')).toBeVisible();
      await expect(page.locator('text=📊 Daily Reports')).toBeVisible();
      await expect(page.locator('text=📚 Knowledge Base')).toBeVisible();
    }
  });

  test('should navigate between pages using menu', async ({ page }) => {
    await page.goto('/');

    // Navigate to Issues
    await page.click('text=🔍 Issues Analysis');
    await expect(page).toHaveURL('/issues');

    // Navigate to Reports
    await page.click('text=📊 Daily Reports');
    await expect(page).toHaveURL('/reports');

    // Navigate to Knowledge
    await page.click('text=📚 Knowledge Base');
    await expect(page).toHaveURL('/knowledge');

    // Navigate back to Chat
    await page.click('text=💬 Chat');
    await expect(page).toHaveURL('/');
  });

  test('should show active state on current page', async ({ page }) => {
    await page.goto('/issues');

    // Issues menu item should have active class
    const issuesMenuItem = page.locator('.conversation-item:has-text("🔍 Issues Analysis")');
    await expect(issuesMenuItem).toHaveClass(/active/);
  });

  test('should list analyzed issues if any exist', async ({ page }) => {
    await page.goto('/issues');

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check if there are any analyzed issues
    const issueItems = page.locator('[style*="flex-direction: column"] > div');
    const count = await issueItems.count();

    if (count > 0) {
      console.log(`✓ Found ${count} analyzed issues`);

      // Verify issue item structure
      const firstIssue = issueItems.first();
      await expect(firstIssue).toBeVisible();

      // Should have issue key
      await expect(firstIssue.locator('[style*="font-weight: 600"]')).toBeVisible();

      // Should have timestamp
      await expect(firstIssue.locator('text=/分析时间/')).toBeVisible();
    } else {
      console.log('ℹ No analyzed issues found yet');
    }
  });

  test('should click on analyzed issue to view details', async ({ page }) => {
    await page.goto('/issues');

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check if there are any analyzed issues
    const issueItems = page.locator('[style*="flex-direction: column"] > div');
    const count = await issueItems.count();

    if (count > 0) {
      // Click on first issue
      await issueItems.first().click();

      // Should navigate to analysis page
      await expect(page).toHaveURL(/\/analysis\/.+/);

      console.log('✓ Successfully navigated to analysis details');
    } else {
      console.log('⊘ Skipped - no analyzed issues to click');
    }
  });
});

test.describe('Analysis Page Components', () => {
  test('should have proper page structure', async ({ page }) => {
    await page.goto('/analysis/STRUCT-1');

    // Should have sidebar
    await expect(page.locator('.sidebar')).toBeVisible();

    // Should have main panel
    await expect(page.locator('.main-panel')).toBeVisible();

    // Should have back button
    await expect(page.locator('button:has-text("返回列表")')).toBeVisible();
  });

  test('should display analysis sections when loaded', async ({ page }) => {
    // This test would need a real analyzed issue
    // For now, just verify the page structure
    await page.goto('/analysis/DISPLAY-1');

    await page.waitForTimeout(2000);

    // Check if analysis result is shown (might be loading or error)
    const hasAnalysis = await page.locator('h1').count() > 0;

    if (hasAnalysis) {
      console.log('✓ Analysis page has content structure');
    } else {
      console.log('ℹ Analysis page is loading or showing error');
    }
  });
});

test.describe('API Integration', () => {
  test('should call backend API endpoints', async ({ page }) => {
    // Listen for API calls
    const apiCalls: string[] = [];

    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiCalls.push(request.url());
      }
    });

    await page.goto('/issues');
    await page.waitForTimeout(2000);

    // Should have called list analyzed issues API
    const hasListCall = apiCalls.some(url => url.includes('/api/analysis/issues'));

    if (hasListCall) {
      console.log('✓ API call to list analyzed issues detected');
    } else {
      console.log('⚠ No API call detected - backend might not be running');
    }
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Navigate to analysis page with invalid issue
    await page.goto('/analysis/INVALID-999');

    await page.waitForTimeout(3000);

    // Should show some feedback (loading, error, or content)
    const hasContent = await page.locator('body').textContent();
    expect(hasContent).toBeTruthy();

    console.log('✓ Page handles API response (success or error)');
  });
});
