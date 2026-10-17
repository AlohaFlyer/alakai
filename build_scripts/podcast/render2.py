#!/usr/bin/env python3
"""render2.py <script.md> [--dry-run]

Second-generation renderer. Finding from 2026-10-16 sound checks: ElevenLabs pronunciation dictionaries
(alias or IPA) do not fix Hawaiian on any model, but the locally-trained voice (Mikey / Coach Pono) says
Hawaiian correctly from plain spelling on eleven_v3. So:

  - Every line is rendered per line with /v1/text-to-speech on eleven_v3, no dictionary.
  - Lines spoken by a character flagged "hawaiian_native" in cast.json are rendered whole.
  - For every other character, each Hawaiian term (from lexicon.json, matched longest-first) is cut out of
    the line: the English fragments are rendered in that character's voice, and the term itself is taken
    from the approved per-term clip bank (out/termbank/<slug>.mp3, rendered once in the native voice via
    termbank.py) and spliced in with a 60 ms crossfade and level match. The seam is audible but small, and
    the word is right.
  - Acronyms (SAT, ACT, HPA, ...) keep their alias expansion by plain text substitution before TTS,
    which every model honors ("ess ay tee").

Output: out/<slug>-v2/line###.mp3 plus concat list; master.sh then mixes music and normalizes.
"""
import argparse, json, os, re, sys, pathlib, subprocess, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R

TERMS = R.LEX["terms"]
def is_hawaiian(t): return bool(re.search(r"[ʻāēīōūĀĒĪŌŪ]", t)) or (t[0].islower() and t not in ("shoots",)) or t in ("Waimea","Kohala","Hilo","Puna","Kona","Kamuela","Kealakehe","Konawaena","Kealakekua","Lehua","Pono","Hele-On","Makua Lani","Kamehameha","Ke Kula","Mauna Kea","Hawaii")
CAST_NAMES = {c["name"] for c in R.CAST["characters"]} | {c["name"].split()[-1] for c in R.CAST["characters"]} | {c["name"].split()[0] for c in R.CAST["characters"]}
CAST_LOWER = {n.lower() for n in CAST_NAMES}
HAW = sorted([t for t in TERMS if is_hawaiian(t) and not t.startswith("_") and t.lower() not in CAST_LOWER], key=len, reverse=True)
ACR = {t: v["say"] for t, v in TERMS.items() if not is_hawaiian(t) and not t.startswith("_") and v.get("say")}
def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower().replace("ʻ", "")).strip("-")

def expand_acronyms(text):
    for t in sorted(ACR, key=len, reverse=True):
        text = re.sub(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])", ACR[t], text)
    return text

def split_hawaiian(text):
    """Return list of (kind, text): kind 'en' or 'haw'."""
    pat = "|".join(re.escape(t) for t in HAW)
    parts, pos = [], 0
    for m in re.finditer(pat, text, flags=re.IGNORECASE):
        # word boundary check for plain-ascii terms
        s, e = m.span()
        if s and text[s-1].isalpha(): continue
        if e < len(text) and text[e].isalpha(): continue
        if s > pos: parts.append(("en", text[pos:s]))
        parts.append(("haw", m.group(0))); pos = e
    if pos < len(text): parts.append(("en", text[pos:]))
    return parts

def tts(key, vid, text, out, model="eleven_v3"):
    import requests
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128", headers={"xi-api-key": key, "Content-Type": "application/json"}, json={"text": text, "model_id": model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": float(os.environ.get("TTS_SPEED", "1.1"))}}, timeout=180)
    if r.status_code != 200: sys.exit(f"tts {r.status_code}: {r.text[:200]}")
    out.write_bytes(r.content); time.sleep(0.25)

def concat_with_crossfade(parts, out):
    """parts: list of mp3 paths. Crossfade 60 ms between neighbours, loudness-match each part to -18 LUFS first."""
    if len(parts) == 1: subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(parts[0]), "-c", "copy", str(out)], check=True); return
    inputs = []; filt = []
    for i, p in enumerate(parts):
        inputs += ["-i", str(p)]; filt.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=mono,loudnorm=I=-18:TP=-2:LRA=7,apad=pad_dur=0.02[a{i}]")
    chain = "[a0]"
    for i in range(1, len(parts)):
        filt.append(f"{chain}[a{i}]acrossfade=d={os.environ.get('XFADE','0.06')}:c1=tri:c2=tri[x{i}]"); chain = f"[x{i}]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", chain, "-b:a", "128k", str(out)], check=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("script"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--out")
    a = ap.parse_args(); R.load_env()
    title, cast, minutes, lines = R.parse(a.script); by = R.chars()
    natives = {c["key"] for c in R.CAST["characters"] if c.get("hawaiian_native")}
    bank = HERE / "out" / "termbank"
    missing_bank = set()
    plan = []
    for n, (sp, text) in enumerate(lines):
        c = by[sp]; text2 = expand_acronyms(text)
        if c["key"] in natives: plan.append((n, c, [("en", text2)])); continue
        parts = split_hawaiian(text2)
        for k, t in parts:
            if k == "haw" and not (bank / f"{slug(t)}.mp3").exists(): missing_bank.add(t)
        plan.append((n, c, parts))
    nh = sum(1 for _, c, parts in plan for k, _ in parts if k == "haw")
    offenders = [(n, c["name"], t) for n, c, parts in plan for k, t in parts if k == "haw"]
    if offenders and not os.environ.get("ALLOW_SPLICE"):
        print("HOUSE RULE: only hawaiian_native characters may say Hawaiian words. Rewrite these lines or route them to Coach Pono:")
        for n, name, t in offenders: print(f"  line {n+1} ({name}): {t}")
        sys.exit(1)
    print(f"{title}: {len(lines)} lines, {nh} spliced Hawaiian terms, natives: {sorted(natives) or 'none'}")
    if missing_bank: print("  termbank missing:", ", ".join(sorted(missing_bank)), "(run termbank.py)")
    if a.dry_run: return
    if missing_bank: sys.exit(1)
    key = os.environ["ELEVENLABS_API_KEY"]
    s = pathlib.Path(a.script).stem; outdir = pathlib.Path(a.out) if a.out else HERE / "out" / f"{s}-v2"; outdir.mkdir(parents=True, exist_ok=True)
    for n, c, parts in plan:
        final = outdir / f"line{n:03d}.mp3"
        if final.exists(): continue
        pieces = []
        for j, (k, t) in enumerate(parts):
            if k == "haw": pieces.append(bank / f"{slug(t)}.mp3"); continue
            t = t.strip()
            if not re.search(r"[A-Za-z0-9]", t): continue
            p = outdir / f"line{n:03d}_{j}.mp3"
            if not p.exists(): tts(key, c["voice_id"], t, p)
            pieces.append(p)
        concat_with_crossfade(pieces, final); print(f"  line {n} ({c['name']}): {len(pieces)} piece(s)")
    (outdir / "list.txt").write_text("".join(f"file '{(outdir / f'line{n:03d}.mp3').resolve()}'\n" for n, _, _ in plan))
    print("  wrote", outdir)

if __name__ == "__main__":
    main()
