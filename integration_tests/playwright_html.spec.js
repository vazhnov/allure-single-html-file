const fs = require('node:fs');
const { test, expect } = require('@playwright/test');

const ignoredFailurePattern = /googletagmanager\.com\/gtag\/js/i;

test('single-file allure report opens without runtime errors', async ({ page }) => {
  const targetHtml = process.env.TARGET_HTML;
  const screenshotPath = process.env.SCREENSHOT_PATH;

  if (!targetHtml) {
    throw new Error('TARGET_HTML env variable is required.');
  }

  if (!fs.existsSync(targetHtml)) {
    throw new Error(`HTML file not found: ${targetHtml}`);
  }

  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];

  page.on('console', (msg) => {
    const text = msg.text();
    if (msg.type() === 'error' && !ignoredFailurePattern.test(text)) {
      consoleErrors.push(text);
    }
  });

  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  page.on('requestfailed', (request) => {
    const url = request.url();
    if (!ignoredFailurePattern.test(url)) {
      const reason = request.failure()?.errorText ?? 'unknown';
      failedRequests.push(`${url} :: ${reason}`);
    }
  });

  await page.goto(`file://${targetHtml}`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForSelector('.app', { timeout: 60000 });
  await page.waitForTimeout(1000);

  if (screenshotPath) {
    await page.screenshot({ path: screenshotPath, fullPage: true });
  }

  expect(pageErrors, `pageerror events: ${JSON.stringify(pageErrors, null, 2)}`).toEqual([]);
  expect(consoleErrors, `console.error events: ${JSON.stringify(consoleErrors, null, 2)}`).toEqual([]);
  expect(failedRequests, `requestfailed events: ${JSON.stringify(failedRequests, null, 2)}`).toEqual([]);
});
