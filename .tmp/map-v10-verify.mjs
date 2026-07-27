const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: true, channel: "chrome" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto("http://localhost:3000/", { waitUntil: "networkidle", timeout: 60000 });
  const el = page.locator('img[alt*="Illustrated map"]').first();
  await el.scrollIntoViewIfNeeded();
  await page.waitForTimeout(900);
  const box = await el.boundingBox();
  console.log("map box", box);
  const clip = box
    ? {
        x: Math.max(0, box.x - 240),
        y: Math.max(0, box.y - 50),
        width: Math.min(1440 - Math.max(0, box.x - 240), box.width + 480),
        height: Math.min(850, box.height + 100),
      }
    : undefined;
  await page.screenshot({ path: ".tmp/map-v10-clip.png", clip });
  const pond = page.getByRole("button", { name: /Ceremony Pond/i });
  if (await pond.count()) {
    await pond.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: ".tmp/map-v10-clip-pond.png", clip });
  }
  const inn = page.getByRole("button", { name: /The Inn/i });
  if (await inn.count()) {
    await inn.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: ".tmp/map-v10-clip-inn.png", clip });
  }
  await browser.close();
  console.log("done");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
