#!/usr/bin/env python3
"""soundcheck.py [--voice KEY] [--only term,term]
Renders one short clip per Hawaiian / local term in lexicon.json, through the same pronunciation dictionary
the episodes use, so every word can be approved by ear before an episode is rendered.
Output: out/soundcheck/<nn>-<slug>.mp3 plus out/soundcheck/index.html with a play button per term.
"""
import argparse, json, os, re, sys, pathlib, time, html
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--voice", default="lehua"); ap.add_argument("--only", default=""); ap.add_argument("--all", action="store_true", help="include acronyms too")
    a = ap.parse_args(); R.load_env()
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY") or sys.exit("ELEVENLABS_API_KEY missing")
    by = R.chars(); vid = by[a.voice]["voice_id"]
    pd = R.ensure_pdict_elevenlabs()
    terms = R.LEX["terms"]
    def hawaiian(t): return bool(re.search(r"[ʻāēīōūĀĒĪŌŪ]", t)) or t[0].islower() or t in ("Waimea","Kohala","Hilo","Puna","Kona","Kamuela","Kealakehe","Konawaena","Kealakekua","Lehua","Pono","Kaden","Medeiros","Nakamura","Hele-On","Merrie Monarch","Makua Lani","Kamehameha","Ke Kula","Mauna Kea","Hawaii")
    sel = [t for t in terms if (a.all or hawaiian(t)) and not t.startswith("_")]
    if a.only: sel = [t for t in sel if t in a.only.split(",")]
    outdir = HERE / "out" / "soundcheck"; outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, t in enumerate(sel):
        slug = re.sub(r"[^a-z0-9]+", "-", t.lower().replace("ʻ", "")).strip("-")
        f = outdir / f"{i:02d}-{slug}.mp3"
        if not f.exists():
            body = {"model_id": "eleven_v3", "inputs": [{"text": f"{t}.", "voice_id": vid}]}
            if pd: body["pronunciation_dictionary_locators"] = [pd]
            r = requests.post("https://api.elevenlabs.io/v1/text-to-dialogue?output_format=mp3_44100_64", headers={"xi-api-key": key, "Content-Type": "application/json"}, json=body, timeout=120)
            if r.status_code != 200: print(t, r.status_code, r.text[:120]); continue
            f.write_bytes(r.content); time.sleep(0.3)
        rows.append((t, terms[t].get("say", ""), f.name)); print(f"  {i:02d} {t}")
    page = ["<!doctype html><meta charset=utf-8><title>Sound check</title><style>body{font-family:system-ui;max-width:760px;margin:20px auto;padding:0 16px;background:#FBF8F1;color:#16211B}.r{display:grid;grid-template-columns:1fr 1fr 200px;gap:10px;align-items:center;padding:8px 0;border-bottom:1px solid #ddd}.say{color:#4A5A50;font-family:ui-monospace,monospace;font-size:.9rem}audio{width:200px;height:30px}</style><h1>Alakaʻi sound check</h1><p>Voice: " + html.escape(by[a.voice]["name"]) + ". Each clip is the word alone through the episode pronunciation dictionary.</p>"]
    for t, say, fn in rows: page.append(f'<div class="r"><strong>{html.escape(t)}</strong><span class="say">{html.escape(say)}</span><audio controls preload="none" src="{fn}"></audio></div>')
    (outdir / "index.html").write_text("\n".join(page), encoding="utf-8")
    print(f"{len(rows)} clips, {outdir}/index.html")

if __name__ == "__main__":
    main()
