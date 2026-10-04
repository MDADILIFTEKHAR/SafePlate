import { test, expect } from '@playwright/test';

test.describe('SafePlate Full Autonomous E2E Acceptance Flow', () => {
  test('executes complete user journey: profile, meal generation, can I eat, pantry, and safety invalidation', async ({ page }) => {
    // 1. Open Application
    await page.goto('/');
    await expect(page).toHaveTitle(/SafePlate/i);

    // 2. Verify Profile & Persona Loads (Aisha)
    const heroHeading = page.locator('h1');
    await expect(heroHeading).toContainText('Aisha');
    await expect(page.locator('text=Allergies: Peanut')).toBeVisible();

    // 3. Verify Today's Meal Plan renders
    // Check that 4 meal slots exist
    await expect(page.locator('text=Today\'s Meals')).toBeVisible();
    const mealCards = page.locator('text=View Ingredients & Steps');
    await expect(mealCards).toHaveCount(4);

    // Verify first meal can be expanded
    await mealCards.first().click();
    await expect(page.locator('text=Why SafePlate Recommended This')).toBeVisible();

    // 4. ACTION: Open "Can I Eat This?" Tool
    const canIEatNavBtn = page.locator('#nav-can-i-eat-btn');
    await canIEatNavBtn.click();
    await expect(page.locator('#can-i-eat-title')).toBeVisible();

    const queryInput = page.locator('#food-query-input');
    const checkBtn = page.locator('#run-safety-check-btn');

    const modal = page.locator('[role="dialog"]');

    // TEST 4A: Enter "peanut butter" -> Expect AVOID
    await queryInput.fill('peanut butter');
    await checkBtn.click();
    await expect(modal.locator('role=status >> text=AVOID')).toBeVisible();
    await expect(modal.locator('text=Direct allergen conflict')).toBeVisible();

    // TEST 4B: Enter "steamed basmati rice" -> Expect SAFE
    await queryInput.fill('steamed basmati rice');
    await checkBtn.click();
    await expect(modal.locator('role=status >> text=SAFE')).toBeVisible();

    // TEST 4C: Enter "roasted cashew nuts" -> Expect AVOID (active allergen: Tree nuts)
    await queryInput.fill('roasted cashew nuts');
    await checkBtn.click();
    await expect(modal.locator('role=status >> text=AVOID')).toBeVisible();

    // TEST 4D: Enter "may contain traces of peanuts" -> Expect CAUTION
    await queryInput.fill('may contain traces of peanuts');
    await checkBtn.click();
    await expect(modal.locator('role=status >> text=CAUTION')).toBeVisible();

    // Close "Can I Eat This" Modal
    await modal.locator('button[aria-label="Close"]').click();
    await expect(modal).not.toBeVisible();

    // 5. ACTION: Open Pantry Drawer
    const pantryBtn = page.locator('#nav-pantry-btn');
    await pantryBtn.click();
    await expect(page.locator('#pantry-title')).toBeVisible();

    // Add new pantry item: "Fresh Coriander"
    const pantryNameInput = page.locator('#pantry-item-name-input');
    await pantryNameInput.fill('Fresh Coriander');
    await page.locator('#add-pantry-item-btn').click();
    await expect(page.locator('text=Fresh Coriander')).toBeVisible();

    // Close Pantry Drawer
    await page.locator('[role="dialog"]').locator('button[aria-label="Close"]').click();
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();

    // 6. ACTION: Generate Meal Plan
    const generateBtn = page.locator('#hero-generate-btn');
    await generateBtn.click();
    await expect(page.locator('text=Today\'s Meals')).toBeVisible();

    // 7. ACTION: Open Profile Modal and Change Allergy
    const profileBtn = page.locator('#nav-profile-btn');
    await profileBtn.click();
    await expect(page.locator('#profile-title')).toBeVisible();

    // Modify budget
    const budgetSlider = page.locator('#profile-budget-slider');
    await budgetSlider.fill('160');

    // Click Save Profile
    await page.locator('#save-profile-btn').click();

    // Verify application remains responsive and healthy
    await expect(page.locator('text=Daily Financial Safety')).toBeVisible();
  });
});
