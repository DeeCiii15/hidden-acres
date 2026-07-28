"""Capture #love-letters and #portfolio from the homepage."""
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
PORT = 9460


def main() -> None:
    OUT.mkdir(exist_ok=True)
    user = OUT / f"chrome-profile-{int(time.time())}"
    user.mkdir()
    proc = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={user}",
            "--window-size=1400,1100",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        tabs = None
        for _ in range(40):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                break
            except Exception:
                time.sleep(0.15)
        assert tabs
        page_tab = next(
            (
                t
                for t in tabs
                if t.get("type") == "page"
                and not str(t.get("url", "")).startswith("chrome-extension:")
            ),
            None,
        )
        if page_tab is None:
            # create a fresh page target
            created = json.load(
                urllib.request.urlopen(
                    f"http://127.0.0.1:{PORT}/json/new?http://localhost:3000/"
                )
            )
            page_tab = created if isinstance(created, dict) else tabs[0]
            time.sleep(0.5)
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
            page_tab = next(
                (
                    t
                    for t in tabs
                    if "localhost:3000" in t.get("url", "")
                    or t.get("id") == page_tab.get("id")
                ),
                tabs[0],
            )
        print("using tab", page_tab.get("url"), page_tab.get("title"))
        ws = websocket.create_connection(page_tab["webSocketDebuggerUrl"], timeout=90)
        mid = 0

        def call(method: str, params: dict | None = None) -> dict:
            nonlocal mid
            mid += 1
            i = mid
            ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == i:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg.get("result", {})

        def navigate(url: str) -> None:
            call("Page.navigate", {"url": url})
            time.sleep(3.5)
            for _ in range(20):
                res = call(
                    "Runtime.evaluate",
                    {
                        "expression": "document.readyState + ':' + !!document.querySelector('#love-letters')",
                        "returnByValue": True,
                    },
                )
                val = res.get("result", {}).get("value", "")
                print("ready", val)
                if val.startswith("complete") and val.endswith("true"):
                    return
                time.sleep(0.4)

        def shot(name: str) -> None:
            res = call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
            data = base64.b64decode(res["data"])
            (OUT / name).write_bytes(data)
            (ASSETS / f"preview-{name}").write_bytes(data)
            print("wrote", name, len(data))

        call("Page.enable")
        call("Runtime.enable")
        navigate("http://localhost:3000/")
        time.sleep(1.2)
        info = call(
            "Runtime.evaluate",
            {
                "expression": """
({
  href: location.href,
  title: document.title,
  bodyLen: document.body ? document.body.innerText.length : 0,
  ids: [...document.querySelectorAll('[id]')].map(e => e.id).slice(0, 30),
  htmlSnippet: document.documentElement.outerHTML.slice(0, 500)
})
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("page info", info)

        for section, name in (
            ("#love-letters", "love-letters.png"),
            ("#portfolio", "home-portfolio.png"),
        ):
            top = call(
                "Runtime.evaluate",
                {
                    "expression": f"""
(() => {{
  const el = document.querySelector('{section}');
  if (!el) return null;
  el.classList.add('is-in-view');
  return el.getBoundingClientRect().top + window.scrollY;
}})()
""",
                    "returnByValue": True,
                },
            )["result"]["value"]
            print(section, "top", top)
            if top is None:
                continue
            call(
                "Runtime.evaluate",
                {"expression": f"window.scrollTo(0, Math.max(0, {top} - 70))"},
            )
            time.sleep(1.3)
            shot(name)

        seal = call(
            "Runtime.evaluate",
            {
                "expression": """
(() => {
  const el = document.querySelector('.love-letter-unit.is-active .love-letter-seal')
    || document.querySelector('.love-letter-seal');
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x:r.x, y:r.y, w:r.width, h:r.height, html: el.innerHTML.slice(0,160)};
})()
""",
                "returnByValue": True,
            },
        )["result"]["value"]
        print("seal", seal)
        if seal and seal["w"] > 0 and seal["y"] > 0:
            res = call(
                "Page.captureScreenshot",
                {
                    "format": "png",
                    "fromSurface": True,
                    "clip": {
                        "x": max(0, seal["x"] - 24),
                        "y": max(0, seal["y"] - 24),
                        "width": seal["w"] + 48,
                        "height": seal["h"] + 48,
                        "scale": 1,
                    },
                },
            )
            data = base64.b64decode(res["data"])
            (ASSETS / "preview-love-letter-seal.png").write_bytes(data)
            print("seal shot", len(data))

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
