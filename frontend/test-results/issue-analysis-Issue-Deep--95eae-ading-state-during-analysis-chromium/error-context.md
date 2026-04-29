# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: issue-analysis.spec.ts >> Issue Deep Analysis E2E >> should show loading state during analysis
- Location: e2e\issue-analysis.spec.ts:87:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=正在分析').or(locator('.typing-indicator'))
Expected: visible
Error: strict mode violation: locator('text=正在分析').or(locator('.typing-indicator')) resolved to 2 elements:
    1) <div class="typing-indicator">…</div> aka locator('.typing-indicator')
    2) <div>正在分析 TEST-789...</div> aka getByText('正在分析 TEST-')

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('text=正在分析').or(locator('.typing-indicator'))

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]:
    - heading "SSD Knowledge Portal" [level=2] [ref=e6]
    - generic [ref=e7]:
      - generic [ref=e8] [cursor=pointer]: 💬 Chat
      - generic [ref=e9] [cursor=pointer]: 🔍 Issues Analysis
      - generic [ref=e10] [cursor=pointer]: 📊 Daily Reports
      - generic [ref=e11] [cursor=pointer]: 📚 Knowledge Base
  - generic [ref=e13]:
    - button "← 返回列表" [ref=e14] [cursor=pointer]
    - generic [ref=e20]: 正在分析 TEST-789...
```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | /**
  4   |  * E2E Test: Issue Deep Analysis Feature
  5   |  *
  6   |  * This test covers the complete workflow:
  7   |  * 1. Start backend server
  8   |  * 2. Navigate to Issues page
  9   |  * 3. Analyze a Jira issue
  10  |  * 4. Verify analysis results
  11  |  * 5. Check knowledge base storage
  12  |  */
  13  | 
  14  | test.describe('Issue Deep Analysis E2E', () => {
  15  |   test.beforeAll(async () => {
  16  |     // Note: Backend should be running at http://localhost:8000
  17  |     // Start it manually with: cd backend && python main.py
  18  |   });
  19  | 
  20  |   test('should navigate to issues page', async ({ page }) => {
  21  |     await page.goto('/');
  22  | 
  23  |     // Wait for page to load
  24  |     await expect(page.locator('h2:has-text("SSD Knowledge Portal")')).toBeVisible();
  25  | 
  26  |     // Click on Issues Analysis navigation
  27  |     await page.click('text=🔍 Issues Analysis');
  28  | 
  29  |     // Verify we're on the issues page
  30  |     await expect(page).toHaveURL('/issues');
  31  |     await expect(page.locator('h1:has-text("Issue 深度分析")')).toBeVisible();
  32  |   });
  33  | 
  34  |   test('should show empty state when no issues analyzed', async ({ page }) => {
  35  |     await page.goto('/issues');
  36  | 
  37  |     // Check for empty state or list
  38  |     const emptyState = page.locator('text=暂无已分析的 Issues');
  39  |     const issuesList = page.locator('[style*="flex-direction: column"]');
  40  | 
  41  |     // Either empty state or list should be visible
  42  |     await expect(emptyState.or(issuesList)).toBeVisible();
  43  |   });
  44  | 
  45  |   test('should have manual analysis input', async ({ page }) => {
  46  |     await page.goto('/issues');
  47  | 
  48  |     // Verify input field exists
  49  |     const input = page.locator('input[placeholder*="输入 Issue Key"]');
  50  |     await expect(input).toBeVisible();
  51  | 
  52  |     // Verify analyze button exists
  53  |     const button = page.locator('button:has-text("开始分析")');
  54  |     await expect(button).toBeVisible();
  55  | 
  56  |     // Button should be disabled when input is empty
  57  |     await expect(button).toBeDisabled();
  58  |   });
  59  | 
  60  |   test('should enable analyze button when issue key entered', async ({ page }) => {
  61  |     await page.goto('/issues');
  62  | 
  63  |     const input = page.locator('input[placeholder*="输入 Issue Key"]');
  64  |     const button = page.locator('button:has-text("开始分析")');
  65  | 
  66  |     // Type issue key
  67  |     await input.fill('TEST-123');
  68  | 
  69  |     // Button should be enabled
  70  |     await expect(button).toBeEnabled();
  71  |   });
  72  | 
  73  |   test('should navigate to analysis page when clicking analyze', async ({ page }) => {
  74  |     await page.goto('/issues');
  75  | 
  76  |     const input = page.locator('input[placeholder*="输入 Issue Key"]');
  77  |     const button = page.locator('button:has-text("开始分析")');
  78  | 
  79  |     // Enter issue key and click analyze
  80  |     await input.fill('TEST-456');
  81  |     await button.click();
  82  | 
  83  |     // Should navigate to analysis page
  84  |     await expect(page).toHaveURL('/analysis/TEST-456');
  85  |   });
  86  | 
  87  |   test('should show loading state during analysis', async ({ page }) => {
  88  |     await page.goto('/analysis/TEST-789');
  89  | 
  90  |     // Should show loading indicator
  91  |     const loadingText = page.locator('text=正在分析');
  92  |     const typingIndicator = page.locator('.typing-indicator');
  93  | 
  94  |     // Either loading text or typing indicator should appear
> 95  |     await expect(loadingText.or(typingIndicator)).toBeVisible({ timeout: 10000 });
      |                                                   ^ Error: expect(locator).toBeVisible() failed
  96  |   });
  97  | 
  98  |   test('should show error when Jira not configured', async ({ page }) => {
  99  |     await page.goto('/analysis/NOTCONFIG-1');
  100 | 
  101 |     // Wait for error message
  102 |     await page.waitForTimeout(3000);
  103 | 
  104 |     // Should show error about Jira not configured
  105 |     const errorMessage = page.locator('text=/Jira|configured|failed/i');
  106 | 
  107 |     // Check if error is visible (might take a moment)
  108 |     const isErrorVisible = await errorMessage.isVisible().catch(() => false);
  109 | 
  110 |     if (isErrorVisible) {
  111 |       console.log('✓ Correctly shows error when Jira not configured');
  112 |     } else {
  113 |       console.log('⚠ No error shown - Jira might be configured or analysis in progress');
  114 |     }
  115 |   });
  116 | 
  117 |   test('should have back button on analysis page', async ({ page }) => {
  118 |     await page.goto('/analysis/TEST-999');
  119 | 
  120 |     // Verify back button exists
  121 |     const backButton = page.locator('button:has-text("返回列表")');
  122 |     await expect(backButton).toBeVisible();
  123 | 
  124 |     // Click back button
  125 |     await backButton.click();
  126 | 
  127 |     // Should navigate back to issues page
  128 |     await expect(page).toHaveURL('/issues');
  129 |   });
  130 | 
  131 |   test('should have navigation menu on all pages', async ({ page }) => {
  132 |     const pages = ['/', '/issues', '/reports', '/knowledge'];
  133 | 
  134 |     for (const url of pages) {
  135 |       await page.goto(url);
  136 | 
  137 |       // Check navigation items exist
  138 |       await expect(page.locator('text=💬 Chat')).toBeVisible();
  139 |       await expect(page.locator('text=🔍 Issues Analysis')).toBeVisible();
  140 |       await expect(page.locator('text=📊 Daily Reports')).toBeVisible();
  141 |       await expect(page.locator('text=📚 Knowledge Base')).toBeVisible();
  142 |     }
  143 |   });
  144 | 
  145 |   test('should navigate between pages using menu', async ({ page }) => {
  146 |     await page.goto('/');
  147 | 
  148 |     // Navigate to Issues
  149 |     await page.click('text=🔍 Issues Analysis');
  150 |     await expect(page).toHaveURL('/issues');
  151 | 
  152 |     // Navigate to Reports
  153 |     await page.click('text=📊 Daily Reports');
  154 |     await expect(page).toHaveURL('/reports');
  155 | 
  156 |     // Navigate to Knowledge
  157 |     await page.click('text=📚 Knowledge Base');
  158 |     await expect(page).toHaveURL('/knowledge');
  159 | 
  160 |     // Navigate back to Chat
  161 |     await page.click('text=💬 Chat');
  162 |     await expect(page).toHaveURL('/');
  163 |   });
  164 | 
  165 |   test('should show active state on current page', async ({ page }) => {
  166 |     await page.goto('/issues');
  167 | 
  168 |     // Issues menu item should have active class
  169 |     const issuesMenuItem = page.locator('.conversation-item:has-text("🔍 Issues Analysis")');
  170 |     await expect(issuesMenuItem).toHaveClass(/active/);
  171 |   });
  172 | 
  173 |   test('should list analyzed issues if any exist', async ({ page }) => {
  174 |     await page.goto('/issues');
  175 | 
  176 |     // Wait for data to load
  177 |     await page.waitForTimeout(2000);
  178 | 
  179 |     // Check if there are any analyzed issues
  180 |     const issueItems = page.locator('[style*="flex-direction: column"] > div');
  181 |     const count = await issueItems.count();
  182 | 
  183 |     if (count > 0) {
  184 |       console.log(`✓ Found ${count} analyzed issues`);
  185 | 
  186 |       // Verify issue item structure
  187 |       const firstIssue = issueItems.first();
  188 |       await expect(firstIssue).toBeVisible();
  189 | 
  190 |       // Should have issue key
  191 |       await expect(firstIssue.locator('[style*="font-weight: 600"]')).toBeVisible();
  192 | 
  193 |       // Should have timestamp
  194 |       await expect(firstIssue.locator('text=/分析时间/')).toBeVisible();
  195 |     } else {
```