#!/usr/bin/env python3
"""Generate per-school home screen icons and manifests from the white horse mask.
Output: assets/icons/schools/<id>-{180,192,512,512-maskable}.png and assets/manifests/<id>.webmanifest.
Primary colour follows the same adjustment as app.js applyPalette (mirrored in verify/contrast.py)."""
import json, os, sys, pathlib
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "build_scripts" / "verify"))
from contrast import contrast, on_color, darken, PAPER

def primary_for(c):
    p = c["primary"]
    if contrast(p, "#FFFFFF") < 2.5 and contrast(c["secondary"], "#FFFFFF") >= 2.5: p = c["secondary"]
    if contrast(p, PAPER) < 3: p = darken(p, 0.35)
    steps = 0
    while contrast(p, on_color(p)) < 4.5 and steps < 6: p = darken(p, 0.12); steps += 1
    return p

def main():
    data = json.load(open(ROOT / "data" / "schools.json", encoding="utf-8"))
    base = json.load(open(ROOT / "site.webmanifest", encoding="utf-8"))
    mask = Image.open(ROOT / "assets" / "icons" / "source-1024.png").convert("L").point(lambda v: 255 if v > 150 else 0)
    out = ROOT / "assets" / "icons" / "schools"; out.mkdir(exist_ok=True)
    mdir = ROOT / "assets" / "manifests"; mdir.mkdir(exist_ok=True)
    white = Image.new("RGB", mask.size, "#FBF8F1")
    for s in data["schools"]:
        color = primary_for(s["colors"])
        full = Image.new("RGB", mask.size, color); full.paste(white, (0, 0), mask)
        for n in (180, 192, 512): full.resize((n, n), Image.LANCZOS).save(out / f"{s['id']}-{n}.png")
        mk = Image.new("RGB", (512, 512), color); mk.paste(full.resize((420, 420), Image.LANCZOS), (46, 46)); mk.save(out / f"{s['id']}-512-maskable.png")
        m = dict(base); m["theme_color"] = color; m["start_url"] = "../../index.html"; m["id"] = "/"; m["scope"] = "../../"
        m["icons"] = [{"src": f"../icons/schools/{s['id']}-192.png", "sizes": "192x192", "type": "image/png"},
                      {"src": f"../icons/schools/{s['id']}-512.png", "sizes": "512x512", "type": "image/png"},
                      {"src": f"../icons/schools/{s['id']}-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
        json.dump(m, open(mdir / f"{s['id']}.webmanifest", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(data['schools'])} schools: icons in {out.relative_to(ROOT)}, manifests in {mdir.relative_to(ROOT)}")

if __name__ == "__main__": main()
