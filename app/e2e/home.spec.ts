import { test, expect } from "@playwright/test";

test("homepage has title and CTA", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/{Project Name}/);
  await expect(page.getByRole("link", { name: /get started/i })).toBeVisible();
});
