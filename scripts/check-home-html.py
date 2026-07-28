import urllib.request
from pathlib import Path

html = urllib.request.urlopen("http://localhost:3000/").read().decode("utf-8", "ignore")
Path("tmp-imgs/home.html").write_text(html, encoding="utf-8")
print("len", len(html))
print("love-letters", "love-letters" in html)
print("id portfolio", 'id="portfolio"' in html)
print("wax-seal-ha", "wax-seal-ha" in html)
print("polaroid-card", "polaroid-card" in html)
print("twine-wrap.png", "twine-wrap.png" in html)
