import { spawn } from "child_process";
import fs from "fs";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const WebSocket = require("ws");

const chrome =
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe";
const outDir = "C:\\Dev\\hidden-acres\\.tmp\\ui-preview";
const port = 9346;

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

fs.mkdirSync(outDir, { recursive: true });

const proc = spawn(
  chrome,
  [
    "--headless=new",
    "--disable-gpu",
    `--remote-debugging-port=${port}`,
    "--window-size=1280,900",
    "about:blank",
  ],
  { stdio: "ignore" },
);

let version;
for (let i = 0; i < 40; i++) {
  try {
    version = await fetch(`http://127.0.0.1:${port}/json/version`).then((r) =>
      r.json(),
    );
    break;
  } catch {
    await sleep(250);
  }
}
if (!version) {
  console.error("no cdp");
  proc.kill();
  process.exit(1);
}

const ws = new WebSocket(version.webSocketDebuggerUrl);
await new Promise((res, rej) => {
  ws.once("open", res);
  ws.once("error", rej);
});

let id = 0;
const pending = new Map();
ws.on("message", (data) => {
  const msg = JSON.parse(data.toString());
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result);
  }
});

function send(method, params = {}, sessionId) {
  const msg = { id: ++id, method, params };
  if (sessionId) msg.sessionId = sessionId;
  ws.send(JSON.stringify(msg));
  return new Promise((resolve, reject) =>
    pending.set(msg.id, { resolve, reject }),
  );
}

const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", {
  targetId,
  flatten: true,
});
await send("Page.enable", {}, sessionId);
await send("Runtime.enable", {}, sessionId);

async function shot(file, width, height, mobile) {
  await send(
    "Emulation.setDeviceMetricsOverride",
    { width, height, deviceScaleFactor: mobile ? 2 : 1, mobile },
    sessionId,
  );
  await send(
    "Page.navigate",
    { url: "http://localhost:3000/" },
    sessionId,
  );
  await sleep(4000);
  await send(
    "Runtime.evaluate",
    {
      expression: `(() => {
        const section = document.getElementById('love-letters');
        if (!section) return false;
        section.scrollIntoView({ block: 'center' });
        section.classList.add('is-in-view');
        const units = [...section.querySelectorAll('.love-letter-unit')];
        const active =
          units.find((u) => u.classList.contains('is-active')) ||
          units[Math.floor(units.length / 2)];
        units.forEach((u) => u.classList.remove('is-unveiled'));
        if (active) active.classList.add('is-unveiled', 'is-active');
        return true;
      })()`,
    },
    sessionId,
  );
  await sleep(2200);

  const metrics = await send(
    "Runtime.evaluate",
    {
      expression: `(() => {
        const section = document.getElementById('love-letters');
        const subtitle = [...(section?.querySelectorAll('p') || [])].find((p) =>
          p.textContent?.includes('Words pressed'),
        );
        const ul = section?.querySelector('ul');
        const unit =
          section?.querySelector('.love-letter-unit.is-unveiled') ||
          section?.querySelector('.love-letter-unit.is-active');
        const sheet = unit?.querySelector('.love-letter-sheet');
        const env = unit?.querySelector('.love-letter-envelope');
        const ur = ul?.getBoundingClientRect();
        const er = env?.getBoundingClientRect();
        const sr = sheet?.getBoundingClientRect();
        const subr = subtitle?.getBoundingClientRect();
        return {
          lift: unit
            ? getComputedStyle(unit).getPropertyValue('--letter-lift').trim()
            : null,
          envW: er ? Math.round(er.width) : null,
          envH: er ? Math.round(er.height) : null,
          unitMinH: unit ? getComputedStyle(unit).minHeight : null,
          subtitleToSheet: sr && subr ? Math.round(sr.top - subr.bottom) : null,
          subtitleToUl: ur && subr ? Math.round(ur.top - subr.bottom) : null,
          sheetAboveUl: sr && ur ? Math.round(ur.top - sr.top) : null,
          sheetClipped: sr && ur ? sr.top < ur.top - 1 : null,
          unveiled: !!unit?.classList.contains('is-unveiled'),
          subtitle: subtitle?.textContent?.trim() || null,
        };
      })()`,
      returnByValue: true,
    },
    sessionId,
  );
  console.log(file, JSON.stringify(metrics.result.value, null, 2));

  await send(
    "Runtime.evaluate",
    {
      expression:
        "document.getElementById('love-letters')?.scrollIntoView({block:'center'})",
    },
    sessionId,
  );
  await sleep(500);

  const { data } = await send(
    "Page.captureScreenshot",
    { format: "png", captureBeyondViewport: false },
    sessionId,
  );
  const path = `${outDir}\\${file}`;
  fs.writeFileSync(path, Buffer.from(data, "base64"));
  console.log("wrote", path, fs.statSync(path).size);
}

await shot("love-letters-tight.png", 1280, 900, false);
await shot("love-letters-tight-mobile.png", 390, 844, true);

ws.close();
proc.kill();
process.exit(0);
