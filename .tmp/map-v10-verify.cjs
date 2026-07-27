const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: true, channel: "chrome" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1400 } });
  await page.goto("http://localhost:3000/", { waitUntil: "networkidle", timeout: 60000 });
  const el = page.locator('img[alt*="Illustrated map"]').first();
  await el.evaluate((node) => node.scrollIntoView({ block: "center" }));
  await page.waitForTimeout(1500);
  // Wait for popout images
  await page.waitForSelector('a[aria-label*="Chapel"] img', { timeout: 15000 }).catch(() => {});
  const box = await el.boundingBox();
  const clip = box && {
    x: Math.max(0, box.x - 260),
    y: Math.max(0, box.y - 30),
    width: Math.min(1440, box.width + 520),
    height: Math.min(1400 - Math.max(0, box.y - 30), box.height + 60),
  };
  await page.screenshot({ path: ".tmp/map-v10-final.png", clip });
  // Verify MAP_IMAGE path in DOM
  const src = await el.getAttribute("src");
  console.log("map src", src);
  // Click inn, wait for image
  await page.getByRole("button", { name: /Preview The Inn/i }).click();
  await page.waitForTimeout(1200);
  const innCard = page.locator('a[aria-label*="The Inn"]');
  const innImg = innCard.locator("img");
  console.log("inn img count", await innImg.count());
  if (await innImg.count()) {
    console.log("inn img src", await innImg.first().getAttribute("src"));
    console.log("inn img complete", await innImg.first().evaluate((i) => ({ complete: i.complete, w: i.naturalWidth, h: i.naturalHeight })));
  }
  await page.screenshot({ path: ".tmp/map-v10-final-inn.png", clip });
  await browser.close();
  console.log("done");
})().catch((e) => { console.error(e); process.exit(1); });
