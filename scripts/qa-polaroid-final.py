"""Single polaroid + love-letter seal screenshots with longer timeouts."""

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
PORT = 9341


def main() -> None:
    OUT.mkdir(exist_ok=True)
    userdata = OUT / "chrome-profile-qa3"
    userdata.mkdir(exist_ok=True)
    proc = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={userdata}",
            "--window-size=1280,1600",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(20):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                break
            except Exception:
                time.sleep(0.25)
        else:
            raise RuntimeError("chrome debug port not ready")

        ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=120)
        mid = 0

        def call(method: str, params: dict | None = None) -> dict:
            nonlocal mid
            mid += 1
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg.get("result", {})

        def wait_ready() -> None:
            for _ in range(40):
                res = call(
                    "Runtime.evaluate",
                    {"expression": "document.readyState", "returnByValue": True},
                )
                if res.get("result", {}).get("value") == "complete":
                    return
                time.sleep(0.25)

        def shot(name: str, clip: dict | None = None) -> None:
            params: dict = {"format": "png", "fromSurface": True}
            if clip:
                params["clip"] = {**clip, "scale": 1}
            data = base64.b64decode(call("Page.captureScreenshot", params)["data"])
            (OUT / name).write_bytes(data)
            (ASSETS / f"preview-{name}").write_bytes(data)
            print("wrote", name, len(data))

        call("Page.enable")
        call("Runtime.enable")
        call("Network.enable")

        call("Page.navigate", {"url": "http://localhost:3000/portfolio?v=2"})
        wait_ready()
        time.sleep(2.5)
        call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('.polaroid-card');
  if (el) el.scrollIntoView({block:'center', inline:'center'});
})()
"""
            },
        )
        time.sleep(0.8)

        metrics = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const card = document.querySelector('.polaroid-card');
  const mat = document.querySelector('.polaroid-mat');
  const photo = document.querySelector('.polaroid-photo');
  const seal = document.querySelector('.polaroid-seal');
  if (!card) return {missing:true};
  const cr = card.getBoundingClientRect();
  const mr = mat.getBoundingClientRect();
  const pr = photo.getBoundingClientRect();
  return {
    topFrac: +((pr.top - mr.top) / cr.height).toFixed(3),
    botFrac: +((mr.bottom - pr.bottom) / cr.height).toFixed(3),
    sideFrac: +((pr.left - mr.left) / cr.width).toFixed(3),
    sealSrc: seal && seal.getAttribute('src'),
    couple: document.querySelector('.polaroid-caption')?.textContent,
    box: (() => {
      const r = card.getBoundingClientRect();
      return {x: Math.max(0,r.x-56), y: Math.max(0,r.y-56), width: r.width+112, height: r.height+120};
    })(),
  };
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("metrics", json.dumps(metrics, indent=2))
        shot("polaroid-final.png", metrics.get("box"))

        call("Page.navigate", {"url": "http://localhost:3000/?v=2"})
        wait_ready()
        time.sleep(2)
        call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const section = document.querySelector('#love-letters');
  if (section) {
    section.scrollIntoView({block:'center'});
    section.classList.add('is-in-view');
  }
})()
"""
            },
        )
        time.sleep(1.5)
        seal_info = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('.love-letter-seal');
  const unit = document.querySelector('.love-letter-unit') || el?.parentElement;
  if (!el || !unit) return null;
  const r = unit.getBoundingClientRect();
  return {
    text: el.textContent.trim(),
    hasSvg: !!el.querySelector('svg'),
    hasHa: /\\bha\\b/i.test(el.textContent) || !!el.querySelector('span.font-script'),
    box: {x: Math.max(0,r.x-12), y: Math.max(0,r.y-12), width: Math.min(r.width+24,480), height: Math.min(r.height+24,580)},
  };
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("seal", json.dumps(seal_info, indent=2))
        if seal_info:
            shot("love-letter-final.png", seal_info["box"])

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
