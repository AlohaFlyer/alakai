#!/usr/bin/env python3
"""Build every icon size from the per-school 1024 masters in assets/icons/schools/src/<id>-1024.png
(Grok set, 2026-10-16; layout: Alakaʻi on top, horse with glasses, Test Prep at the bottom).
Per school: <id>-{180,192,512}.png, <id>-512-maskable.png, <id>-64.png (tab favicon, rounded),
<id>-mark-72.png (horse only, rounded, header mark) and assets/manifests/<id>.webmanifest.
The default school (hpa) also writes the root set: favicon.ico, assets/icons/{favicon-16/32/48/64,
apple-touch-icon, icon-192, icon-512, icon-512-maskable, mark-72}.png and assets/og.png."""
import json, pathlib
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "assets" / "icons" / "schools" / "src"
OUT = ROOT / "assets" / "icons" / "schools"; MAN = ROOT / "assets" / "manifests"

def rounded(im, frac=0.22):
    im = im.convert("RGBA"); s = im.size[0]
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * frac), fill=255)
    im.putalpha(m); return im

def build(sid, color, root=False):
    src = Image.open(SRC / f"{sid}-1024.png").convert("RGB"); S = src.size[0]
    for n in (180, 192, 512): src.resize((n, n), Image.LANCZOS).save(OUT / f"{sid}-{n}.png")
    mk = Image.new("RGB", (512, 512), color); mk.paste(src.resize((420, 420), Image.LANCZOS), (46, 46)); mk.save(OUT / f"{sid}-512-maskable.png")
    rounded(src).resize((64, 64), Image.LANCZOS).save(OUT / f"{sid}-64.png")
    band = src.crop((int(S * .12), int(S * .15), int(S * .88), int(S * .85)))
    sq = Image.new("RGB", (S, S), color); h = band.resize((900, int(900 * band.size[1] / band.size[0])), Image.LANCZOS); sq.paste(h, ((S - h.size[0]) // 2, (S - h.size[1]) // 2))
    rounded(sq, .26).resize((72, 72), Image.LANCZOS).save(OUT / f"{sid}-mark-72.png")
    if root:
        ic = ROOT / "assets" / "icons"
        for n in (16, 32, 48, 64): rounded(src).resize((n, n), Image.LANCZOS).save(ic / f"favicon-{n}.png")
        rounded(src).resize((48, 48), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
        src.resize((180, 180), Image.LANCZOS).save(ic / "apple-touch-icon.png")
        src.resize((192, 192), Image.LANCZOS).save(ic / "icon-192.png"); src.resize((512, 512), Image.LANCZOS).save(ic / "icon-512.png")
        mk.save(ic / "icon-512-maskable.png"); rounded(sq, .26).resize((72, 72), Image.LANCZOS).save(ic / "mark-72.png")
        src.save(ic / "source-1024.png")
        og = Image.new("RGB", (1200, 630), "#FBF8F1"); r = rounded(src).resize((460, 460), Image.LANCZOS); og.paste(r, (370, 85), r); og.save(ROOT / "assets" / "og.png")

def main():
    data = json.load(open(ROOT / "data" / "schools.json", encoding="utf-8"))
    base = json.load(open(ROOT / "site.webmanifest", encoding="utf-8"))
    OUT.mkdir(exist_ok=True); MAN.mkdir(exist_ok=True)
    for s in data["schools"]:
        src = Image.open(SRC / f"{s['id']}-1024.png").convert("RGB"); color = "#%02X%02X%02X" % src.getpixel((20, 20))
        build(s["id"], color, root=(s["id"] == data["default"]))
        m = dict(base); m["theme_color"] = color; m["start_url"] = "../../index.html"; m["id"] = "/"; m["scope"] = "../../"
        m["icons"] = [{"src": f"../icons/schools/{s['id']}-192.png", "sizes": "192x192", "type": "image/png"},
                      {"src": f"../icons/schools/{s['id']}-512.png", "sizes": "512x512", "type": "image/png"},
                      {"src": f"../icons/schools/{s['id']}-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
        json.dump(m, open(MAN / f"{s['id']}.webmanifest", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(data['schools'])} schools built from {SRC.relative_to(ROOT)}")

if __name__ == "__main__": main()
