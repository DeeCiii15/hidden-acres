const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: true, channel: "chrome" });
  const page = await browser.newPage({
    viewport: { width: 1400, height: 900 },
    deviceScaleFactor: 2,
  });
  await page.goto("http://localhost:3000/", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.getByRole("heading", { name: "The venue" }).scrollIntoViewIfNeeded();
  await page.waitForTimeout(1200);

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

  // Click painted pin bodies via tip coords shifted up ~3% (label center of pin)
  const tips = [
    { name: "The Inn", x: 56.2, y: 7.9 - 3.2 },
    { name: "The Chapel", x: 40.9, y: 37.6 - 3.2 },
    { name: "The Ceremony Pond", x: 28.8, y: 54.8 - 3.2 },
    { name: "The Rusted Silo", x: 61.0, y: 58.9 - 3.2 },
    { name: "Groom", x: 47.2, y: 59.8 - 3.2 },
    { name: "Courtyard", x: 54.3, y: 68.5 - 3.2 },
    { name: "Bridal", x: 70.8, y: 71.4 - 3.2 },
    { name: "The Ballroom", x: 46.0, y: 86.1 - 3.2 },
  ];

  const imgBox = await page.locator('img[alt*="Illustrated map"]').boundingBox();
  console.log("IMG_BOX", imgBox);

  for (const tip of tips) {
    const cx = imgBox.x + (tip.x / 100) * imgBox.width;
    const cy = imgBox.y + (tip.y / 100) * imgBox.height;
    const hit = await page.evaluate(
      ({ x, y }) => {
        const el = document.elementFromPoint(x, y);
        return el
          ? {
              tag: el.tagName,
              aria: el.getAttribute("aria-label"),
              cls: el.className?.toString?.().slice(0, 80),
            }
          : null;
      },
      { x: cx, y: cy },
    );
    await page.mouse.click(cx, cy);
    await page.waitForTimeout(200);
    const pressed = await page
      .locator(`button[aria-label*="${tip.name}"]`)
      .first()
      .getAttribute("aria-pressed")
      .catch(() => null);
    console.log(
      `PAINTED_CLICK ${tip.name}: hit=${JSON.stringify(hit)} pressed=${pressed}`,
    );
  }

  await page.screenshot({
    path: "C:/Dev/hidden-acres/.tmp/map-pin-verify-dpr2.png",
  });
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
