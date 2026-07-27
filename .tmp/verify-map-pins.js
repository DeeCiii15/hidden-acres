const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const outDir = path.join(__dirname, ".tmp");
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
    channel: "chrome",
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto("http://localhost:3000/", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.getByRole("heading", { name: "The venue" }).scrollIntoViewIfNeeded();
  await page.waitForTimeout(1000);

  const mapInfo = await page.evaluate(() => {
    const img = document.querySelector('img[alt*="Illustrated map"]');
    if (!img) return null;
    return {
      src: img.currentSrc || img.src,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      displayW: img.clientWidth,
      displayH: img.clientHeight,
    };
  });
  console.log("MAP", JSON.stringify(mapInfo, null, 2));

  const pins = page.locator('button[aria-label^="Preview "]');
  const count = await pins.count();
  console.log("PIN_COUNT", count);

  const results = [];
  for (let i = 0; i < count; i++) {
    const pin = pins.nth(i);
    const label = await pin.getAttribute("aria-label");
    const box = await pin.boundingBox();
    await pin.scrollIntoViewIfNeeded();
    await pin.click({ timeout: 5000 });
    await page.waitForTimeout(300);
    const pressed = await pin.getAttribute("aria-pressed");
    const name = (label || "").replace("Preview ", "");
    const card = page.locator(`a[aria-label^="${name}"]`).first();
    const cardVisible = await card.isVisible().catch(() => false);
    results.push({ label, pressed, box, cardVisible });
    console.log(
      `CLICK ${label}: pressed=${pressed} cardVisible=${cardVisible} box=${JSON.stringify(box)}`,
    );
  }

  await page.screenshot({
    path: path.join(outDir, "map-pin-verify.png"),
    fullPage: false,
  });
  console.log("RESULTS_JSON", JSON.stringify(results, null, 2));
  await browser.close();
})().catch((e) => {
  console.error("ERR", e);
  process.exit(1);
});
