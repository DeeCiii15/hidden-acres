"""Headless Chrome screenshots via DevTools Protocol (no Playwright)."""
from __future__ import annotations

import base64
import json
import subprocess
import time
import urllib.request
from pathlib import Path

import websocket

OUT = Path(__file__).resolve().parents[1] / "tmp-imgs"
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
PORT = 9333


def main() -> None:
    OUT.mkdir(exist_ok=True)
    user_data = OUT / "chrome-profile"
    user_data.mkdir(exist_ok=True)
    proc = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={user_data}",
            "--window-size=1400,1100",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.5)
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
        ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=60)
        msg_id = 0

        def call(method: str, params: dict | None = None) -> dict:
            nonlocal msg_id
            msg_id += 1
            mid = msg_id
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg.get("result", {})

        def wait_load(timeout: float = 20) -> None:
            end = time.time() + timeout
            while time.time() < end:
                res = call(
                    "Runtime.evaluate",
                    {"expression": "document.readyState", "returnByValue": True},
                )
                if res.get("result", {}).get("value") == "complete":
                    return
                time.sleep(0.25)

        def screenshot(name: str) -> None:
            res = call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
            data = base64.b64decode(res["data"])
            (OUT / name).write_bytes(data)
            (ASSETS / f"preview-{name}").write_bytes(data)
            print("wrote", name, len(data))

        call("Page.enable")
        call("Runtime.enable")

        call("Page.navigate", {"url": "http://localhost:3000/portfolio"})
        wait_load()
        time.sleep(1.5)
        call("Runtime.evaluate", {"expression": "window.scrollTo(0, 360)"})
        time.sleep(0.5)
        screenshot("polaroid-portfolio.png")

        # Card close-up via clip around first polaroid
        box = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('.polaroid-card');
  if (!el) return null;
  const r = el.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  return {x: Math.max(0,r.x-24), y: Math.max(0,r.y-28), width: r.width+48, height: r.height+56, dpr};
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        if box:
            res = call(
                "Page.captureScreenshot",
                {
                    "format": "png",
                    "fromSurface": True,
                    "clip": {
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"],
                        "scale": 1,
                    },
                },
            )
            data = base64.b64decode(res["data"])
            (OUT / "polaroid-card-closeup.png").write_bytes(data)
            (ASSETS / "preview-polaroid-card-closeup.png").write_bytes(data)
            print("wrote polaroid-card-closeup.png", len(data))

        call("Page.navigate", {"url": "http://localhost:3000/"})
        wait_load()
        time.sleep(1.5)
        call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('#love-letters');
  if (el) { el.scrollIntoView({block:'center'}); el.classList.add('is-in-view'); }
})()
""",
            },
        )
        time.sleep(1.4)
        screenshot("love-letters.png")

        seal = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('.love-letter-seal');
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x: Math.max(0,r.x-40), y: Math.max(0,r.y-40), width: r.width+80, height: r.height+80, text: el.textContent.trim()};
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("seal", seal)
        if seal:
            res = call(
                "Page.captureScreenshot",
                {
                    "format": "png",
                    "fromSurface": True,
                    "clip": {
                        "x": seal["x"],
                        "y": seal["y"],
                        "width": seal["width"],
                        "height": seal["height"],
                        "scale": 1,
                    },
                },
            )
            data = base64.b64decode(res["data"])
            (OUT / "love-letter-seal.png").write_bytes(data)
            (ASSETS / "preview-love-letter-seal.png").write_bytes(data)
            print("wrote love-letter-seal.png", len(data))

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
