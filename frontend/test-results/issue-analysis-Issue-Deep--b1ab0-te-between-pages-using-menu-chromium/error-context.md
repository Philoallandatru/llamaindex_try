# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: issue-analysis.spec.ts >> Issue Deep Analysis E2E >> should navigate between pages using menu
- Location: e2e\issue-analysis.spec.ts:145:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('text=📚 Knowledge Base')
    - locator resolved to <div class="conversation-item">📚 Knowledge Base</div>
  - attempting click action
    - waiting for element to be visible, enabled and stable
    - element is not stable
  - retrying click action
    - waiting for element to be visible, enabled and stable
  - element was detached from the DOM, retrying

```

# Page snapshot

```yaml
- generic [ref=e3]: Reports page coming soon...
```

# Test source

```ts
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
  95  |     await expect(loadingText.or(typingIndicator)).toBeVisible({ timeout: 10000 });
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
> 157 |     await page.click('text=📚 Knowledge Base');
      |                ^ Error: page.click: Test timeout of 30000ms exceeded.
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
  196 |       console.log('ℹ No analyzed issues found yet');
  197 |     }
  198 |   });
  199 | 
  200 |   test('should click on analyzed issue to view details', async ({ page }) => {
  201 |     await page.goto('/issues');
  202 | 
  203 |     // Wait for data to load
  204 |     await page.waitForTimeout(2000);
  205 | 
  206 |     // Check if there are any analyzed issues
  207 |     const issueItems = page.locator('[style*="flex-direction: column"] > div');
  208 |     const count = await issueItems.count();
  209 | 
  210 |     if (count > 0) {
  211 |       // Click on first issue
  212 |       await issueItems.first().click();
  213 | 
  214 |       // Should navigate to analysis page
  215 |       await expect(page).toHaveURL(/\/analysis\/.+/);
  216 | 
  217 |       console.log('✓ Successfully navigated to analysis details');
  218 |     } else {
  219 |       console.log('⊘ Skipped - no analyzed issues to click');
  220 |     }
  221 |   });
  222 | });
  223 | 
  224 | test.describe('Analysis Page Components', () => {
  225 |   test('should have proper page structure', async ({ page }) => {
  226 |     await page.goto('/analysis/STRUCT-1');
  227 | 
  228 |     // Should have sidebar
  229 |     await expect(page.locator('.sidebar')).toBeVisible();
  230 | 
  231 |     // Should have main panel
  232 |     await expect(page.locator('.main-panel')).toBeVisible();
  233 | 
  234 |     // Should have back button
  235 |     await expect(page.locator('button:has-text("返回列表")')).toBeVisible();
  236 |   });
  237 | 
  238 |   test('should display analysis sections when loaded', async ({ page }) => {
  239 |     // This test would need a real analyzed issue
  240 |     // For now, just verify the page structure
  241 |     await page.goto('/analysis/DISPLAY-1');
  242 | 
  243 |     await page.waitForTimeout(2000);
  244 | 
  245 |     // Check if analysis result is shown (might be loading or error)
  246 |     const hasAnalysis = await page.locator('h1').count() > 0;
  247 | 
  248 |     if (hasAnalysis) {
  249 |       console.log('✓ Analysis page has content structure');
  250 |     } else {
  251 |       console.log('ℹ Analysis page is loading or showing error');
  252 |     }
  253 |   });
  254 | });
  255 | 
  256 | test.describe('API Integration', () => {
  257 |   test('should call backend API endpoints', async ({ page }) => {
```