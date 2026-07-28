"""QA screenshots + DOM checks for polaroids and love-letter seals."""

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
PORT = 9334


def main() -> None:
    OUT.mkdir(exist_ok=True)
    userdata = OUT / "chrome-profile2"
    userdata.mkdir(exist_ok=True)
    proc = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={userdata}",
            "--window-size=1400,1100",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.6)
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
        ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=60)
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

        def shot(name: str, clip: dict | None = None) -> None:
            params: dict = {"format": "png", "fromSurface": True}
            if clip:
                params["clip"] = {**clip, "scale": 1}
            res = call("Page.captureScreenshot", params)
            data = base64.b64decode(res["data"])
            (OUT / name).write_bytes(data)
            (ASSETS / f"preview-{name}").write_bytes(data)
            print("wrote", name, len(data))

        call("Page.enable")
        call("Runtime.enable")

        call("Page.navigate", {"url": "http://localhost:3000/"})
        time.sleep(2.5)
        call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('#love-letters');
  if (el) { el.scrollIntoView({block:'center'}); el.classList.add('is-in-view'); }
})()
"""
            },
        )
        time.sleep(1.2)

        seals = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const seals = [...document.querySelectorAll('.love-letter-seal')];
  return seals.slice(0, 3).map((el) => ({
    text: el.textContent.trim(),
    hasSvg: !!el.querySelector('svg'),
    hasHaSpan: !!el.querySelector('span.font-script'),
    html: el.innerHTML.trim().slice(0, 180),
  }));
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("SEALS", json.dumps(seals, indent=2))

        call("Page.navigate", {"url": "http://localhost:3000/portfolio"})
        time.sleep(2.2)
        call("Runtime.evaluate", {"expression": "window.scrollTo(0, 480)"})
        time.sleep(0.5)

        metrics = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const card = document.querySelector('.polaroid-card');
  const mat = document.querySelector('.polaroid-mat');
  const photo = document.querySelector('.polaroid-photo');
  const seal = document.querySelector('.polaroid-seal');
  const twine = document.querySelector('.polaroid-twine');
  const caption = document.querySelector('.polaroid-caption');
  if (!card || !mat || !photo) return null;
  const cr = card.getBoundingClientRect();
  const mr = mat.getBoundingClientRect();
  const pr = photo.getBoundingClientRect();
  return {
    card: [Math.round(cr.width), Math.round(cr.height)],
    topPx: Math.round(pr.top - mr.top),
    sideL: Math.round(pr.left - mr.left),
    sideR: Math.round(mr.right - pr.right),
    botPx: Math.round(mr.bottom - pr.bottom),
    topFrac: +((pr.top - mr.top) / cr.height).toFixed(3),
    botFrac: +((mr.bottom - pr.bottom) / cr.height).toFixed(3),
    sideFrac: +((pr.left - mr.left) / cr.width).toFixed(3),
    sealW: seal ? Math.round(seal.getBoundingClientRect().width) : null,
    sealSrc: seal ? seal.getAttribute('src') : null,
    twineSrc: twine ? twine.getAttribute('src') : null,
    couple: caption ? caption.textContent : null,
  };
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("POLAROID", json.dumps(metrics, indent=2))

        box = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('.polaroid-card');
  const r = el.getBoundingClientRect();
  return {
    x: Math.max(0, r.x - 48),
    y: Math.max(0, r.y - 48),
    width: r.width + 96,
    height: r.height + 110,
  };
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        shot("polaroid-card-v2.png", box)

        call("Page.navigate", {"url": "http://localhost:3000/"})
        time.sleep(2.2)
        call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('#love-letters');
  if (el) { el.scrollIntoView({block:'center'}); el.classList.add('is-in-view'); }
})()
"""
            },
        )
        time.sleep(1.2)
        sbox = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el =
    document.querySelector('.love-letter-unit.is-active .love-letter-seal') ||
    document.querySelector('.love-letter-seal');
  const unit = el.closest('.love-letter-unit') || el.parentElement;
  const r = unit.getBoundingClientRect();
  return {
    x: Math.max(0, r.x - 8),
    y: Math.max(0, r.y - 8),
    width: Math.min(r.width + 16, 460),
    height: Math.min(r.height + 16, 560),
    text: el.textContent.trim(),
    hasSvg: !!el.querySelector('svg'),
    hasHaSpan: !!el.querySelector('span.font-script'),
  };
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("sealbox", sbox)
        shot(
            "love-letter-envelope.png",
            {k: sbox[k] for k in ("x", "y", "width", "height")},
        )

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
