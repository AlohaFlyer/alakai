#!/usr/bin/env python3
"""render_cartesia.py <script.md> [--dry-run] [--pick]
Per-line render with Cartesia Sonic (sonic-3.6), raw Hawaiian spelling, no dictionary.
--pick: list candidate library voices for each character brief (no credits used) and write cast_cartesia.json template.
Voices: cast.json 'cartesia_voice_id' per character (fill after --pick). Output out/<slug>-cartesia/line###.mp3 + list.txt.
Env: CARTESIA_API_KEY in build_scripts/podcast/.env
"""
import argparse, json, os, re, sys, pathlib, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R
from render2 import expand_acronyms

API = "https://api.cartesia.ai"; VER = "2026-08-14"

def hdr(key): return {"Authorization": f"Bearer {key}", "Cartesia-Version": VER, "Content-Type": "application/json"}

def pick(key):
    import requests
    r = requests.get(f"{API}/voices/", headers=hdr(key), params={"limit": 100}, timeout=60)
    if r.status_code != 200: sys.exit(f"voices: {r.status_code} {r.text[:200]}")
    voices = r.json().get("data", r.json() if isinstance(r.json(), list) else [])
    print(f"{len(voices)} voices visible")
    want = {"lehua": ("female", ["warm", "friendly", "conversational", "young"]), "derek": ("male", ["calm", "neutral", "professional"]), "sarah": ("female", ["expressive", "storyteller", "clear"]), "pono": ("male", ["deep", "relaxed", "mature"]), "kaden": ("male", ["young", "casual", "teen"])}
    tmpl = {}
    for k, (g, kws) in want.items():
        scored = []
        for v in voices:
            desc = (v.get("description", "") + " " + v.get("name", "")).lower(); gender = (v.get("gender") or "").lower()
            s = sum(1 for w in kws if w in desc) + (2 if gender == g else 0)
            if (v.get("language") or "en") == "en": scored.append((s, v.get("name"), v.get("id"), v.get("description", "")[:80]))
        scored.sort(reverse=True); tmpl[k] = [{"name": n, "id": i, "desc": d} for s, n, i, d in scored[:5]]
        print(f"\n{k}:"); [print(f"   {n}  {i}  {d}") for s, n, i, d in scored[:5]]
    (HERE / "cast_cartesia_candidates.json").write_text(json.dumps(tmpl, indent=1)); print("\nwrote cast_cartesia_candidates.json; put chosen ids into cast.json as cartesia_voice_id")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("script", nargs="?"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--pick", action="store_true"); ap.add_argument("--speed", default="1.05")
    a = ap.parse_args(); R.load_env()
    key = os.environ.get("CARTESIA_API_KEY") or sys.exit("CARTESIA_API_KEY missing in .env")
    if a.pick: return pick(key)
    import requests
    title, cast, minutes, lines = R.parse(a.script); by = R.chars()
    missing = sorted({by[sp]["name"] for sp, _ in lines if not by[sp].get("cartesia_voice_id")})
    print(f"{title}: {len(lines)} lines; cartesia voices missing for: {missing or 'none'}")
    if a.dry_run or missing: return
    s = pathlib.Path(a.script).stem; outdir = HERE / "out" / f"{s}-cartesia"; outdir.mkdir(parents=True, exist_ok=True)
    for n, (sp, text) in enumerate(lines):
        f = outdir / f"line{n:03d}.mp3"
        if f.exists(): continue
        c = by[sp]
        body = {"model_id": "sonic-3.6", "transcript": expand_acronyms(text), "voice": c["cartesia_voice_id"], "language": "en", "output_format": {"container": "mp3", "sample_rate": 44100, "bit_rate": 128000}, "generation_config": {"speed": float(a.speed)}}
        r = requests.post(f"{API}/tts/bytes", headers=hdr(key), json=body, timeout=120)
        if r.status_code != 200:
            body.pop("generation_config", None); body["transcript"] = f'<speed ratio="{a.speed}"/>' + body["transcript"]
            r = requests.post(f"{API}/tts/bytes", headers=hdr(key), json=body, timeout=120)
            if r.status_code != 200: sys.exit(f"line {n}: {r.status_code} {r.text[:200]}")
        f.write_bytes(r.content); print(f"  line {n} ({c['name']})"); time.sleep(0.2)
    (outdir / "list.txt").write_text("".join(f"file '{(outdir / f'line{n:03d}.mp3').resolve()}'\n" for n in range(len(lines))))
    print("  wrote", outdir)

if __name__ == "__main__":
    main()
