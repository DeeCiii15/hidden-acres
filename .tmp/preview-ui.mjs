import { spawn } from "child_process";
import fs from "fs";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
let WebSocket;
try {
  WebSocket = require("ws");
} catch {
  console.error("ws not found");
  process.exit(1);
}

const chrome =
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe";
const outDir = "C:\\Dev\\hidden-acres\\.tmp\\ui-preview";
const port = 9333;

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
await send(
  "Emulation.setDeviceMetricsOverride",
  { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false },
  sessionId,
);

async function shot(file, scrollToLove) {
  await send("Page.navigate", { url: "http://localhost:3000/" }, sessionId);
  await sleep(2800);
  if (scrollToLove) {
    await send(
      "Runtime.evaluate",
      {
        expression:
          "document.getElementById('love-letters')?.scrollIntoView({block:'center'});",
      },
      sessionId,
    );
    await sleep(1500);
  }
  const { data } = await send(
    "Page.captureScreenshot",
    { format: "png" },
    sessionId,
  );
  const path = `${outDir}\\${file}`;
  fs.writeFileSync(path, Buffer.from(data, "base64"));
  console.log("wrote", path, fs.statSync(path).size);
}

await shot("home-contact.png", false);
await shot("love-letters.png", true);

const evalRes = await send(
  "Runtime.evaluate",
  {
    expression: `(() => {
      const counter = document.querySelector('#love-letters p.font-ui')?.textContent?.replace(/\\s+/g,' ').trim();
      const unveiled = document.querySelector('.love-letter-unit.is-unveiled');
      const env = document.querySelector('.love-letter-unit.is-unveiled .love-letter-envelope') || document.querySelector('.love-letter-envelope');
      const bar = document.querySelector('[class*=\"fixed\"][class*=\"bottom-3\"], [class*=\"fixed\"][class*=\"bottom-5\"]');
      const barInner = bar?.firstElementChild;
      const br = barInner?.getBoundingClientRect();
      return {
        counter,
        unveiledLift: unveiled ? getComputedStyle(unveiled).getPropertyValue('--letter-lift').trim() : null,
        envelopeFilter: env ? getComputedStyle(env).filter : null,
        barRightGap: br ? Math.round(window.innerWidth - br.right) : null,
        activeCount: document.querySelectorAll('.love-letter-unit.is-active').length,
      };
    })()`,
    returnByValue: true,
  },
  sessionId,
);
console.log(JSON.stringify(evalRes.result.value, null, 2));

ws.close();
proc.kill();
process.exit(0);
