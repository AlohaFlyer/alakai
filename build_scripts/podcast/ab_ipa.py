#!/usr/bin/env python3
"""ab_ipa.py: A/B test. For each word, render with an IPA phoneme dictionary on eleven_multilingual_v2
(per-line /v1/text-to-speech) and compare with the existing v3 alias clip in out/soundcheck/.
Writes out/ab/<word>-ipa.mp3 and out/ab/index.html."""
import json, os, re, sys, pathlib, time, html, base64
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R
from hawaiian_ipa import phrase_ipa

WORDS = ["Waimea", "Hawaiʻi", "Kīpuʻupuʻu", "Honokaʻa", "Kealakehe", "Konawaena", "Laupāhoehoe", "ʻōhiʻa", "Alakaʻi", "Kaʻū"]
OVERRIDE = {"Laupāhoehoe": "ˌlaupaːˌhoeˈhoe".replace("hoe", "hoe"), "Kāʻeo": "ˈkaːʔeo"}

def main():
    R.load_env(); import requests
    key = os.environ["ELEVENLABS_API_KEY"]; vid = R.chars()["lehua"]["voice_id"]
    rules = []
    for w in WORDS:
        ipa = OVERRIDE.get(w) or phrase_ipa(w)
        rules.append({"string_to_replace": w, "type": "phoneme", "phoneme": ipa, "alphabet": "ipa"})
    r = requests.post("https://api.elevenlabs.io/v1/pronunciation-dictionaries/add-from-rules", headers={"xi-api-key": key}, json={"name": "alakai-ipa-ab", "rules": rules}, timeout=60)
    if r.status_code != 200: sys.exit(f"pdict: {r.status_code} {r.text[:200]}")
    d = r.json(); loc = {"pronunciation_dictionary_id": d["id"], "version_id": d["version_id"]}
    print("ipa dict", d["id"])
    out = HERE / "out" / "ab"; out.mkdir(parents=True, exist_ok=True)
    rows = []
    for w in WORDS:
        f = out / (re.sub(r"[^a-z]+", "-", w.lower().replace("ʻ", "")) + "-ipa.mp3")
        if not f.exists():
            r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_64", headers={"xi-api-key": key, "Content-Type": "application/json"}, json={"text": f"{w}.", "model_id": "eleven_multilingual_v2", "pronunciation_dictionary_locators": [loc], "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}}, timeout=120)
            if r.status_code != 200: print(w, r.status_code, r.text[:150]); continue
            f.write_bytes(r.content); time.sleep(0.3)
        # find the v3 clip
        slug = re.sub(r"[^a-z0-9]+", "-", w.lower().replace("ʻ", "")).strip("-")
        v3 = sorted((HERE / "out" / "soundcheck").glob(f"*-{slug}.mp3"))
        rows.append((w, OVERRIDE.get(w) or phrase_ipa(w), f, v3[0] if v3 else None)); print(" ", w)
    def b64(p): return base64.b64encode(p.read_bytes()).decode() if p else ""
    page = ['<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>IPA A/B</title><style>body{font-family:system-ui;max-width:820px;margin:20px auto;padding:0 16px;background:#FBF8F1;color:#16211B}.r{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;align-items:center;padding:8px 0;border-bottom:1px solid #ddd}.ipa{font-family:ui-monospace,monospace;font-size:.85rem;color:#4A5A50}audio{width:100%;height:30px}th{text-align:left;font-size:.85rem;color:#4A5A50}</style><h1>Pronunciation A/B</h1><p>A = current (alias respelling, v3 dialogue). B = IPA phonemes on multilingual_v2. Same voice (Hoku).</p><div class="r"><th>Word</th><th>A: current</th><th>B: IPA</th></div>']
    for w, ipa, fb, fa in rows: page.append(f'<div class="r"><div><strong>{html.escape(w)}</strong><br><span class="ipa">/{html.escape(ipa)}/</span></div><audio controls preload="none" src="data:audio/mpeg;base64,{b64(fa)}"></audio><audio controls preload="none" src="data:audio/mpeg;base64,{b64(fb)}"></audio></div>')
    (out / "index.html").write_text("\n".join(page), encoding="utf-8"); print("wrote", out / "index.html")

if __name__ == "__main__":
    main()
