#!/usr/bin/env python3
"""render.py <script.md> [--engine elevenlabs|cartesia] [--dry-run] [--out DIR]

Renders a podcast script into per-scene audio with ElevenLabs Text-to-Dialogue (default)
or, for A/B testing, Cartesia per-line TTS. Then master.sh concatenates and normalizes.

Script format:
  # Title line
  cast: key, key, key        (keys from cast.json; 3 to 5)
  target_minutes: N
  NAME: line                  (NAME matches a cast key case-insensitively, or the character's display name)

Guards:
  - every cast member needs a voice_id in cast.json (unless --dry-run)
  - every flagged token (acronym or word with ʻokina/kahakō) must be in lexicon.json
  - 3 to 5 distinct speakers per episode

Env: ELEVENLABS_API_KEY, CARTESIA_API_KEY (read from build_scripts/podcast/.env if present).
"""
import argparse, json, os, re, sys, time, pathlib, unicodedata

HERE = pathlib.Path(__file__).resolve().parent
CAST = json.loads((HERE / "cast.json").read_text())
LEX = json.loads((HERE / "lexicon.json").read_text())

def load_env():
    p = HERE / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

def parse(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    title, cast, minutes, lines = "", [], 0, []
    for raw in text.splitlines():
        s = raw.strip()
        if not s: continue
        if s.startswith("# "): title = s[2:].strip(); continue
        if s.lower().startswith("cast:"): cast = [c.strip().lower() for c in s[5:].split(",") if c.strip()]; continue
        if s.lower().startswith("target_minutes:"): minutes = float(s.split(":", 1)[1]); continue
        m = re.match(r"^([A-Za-zʻ' .]+?):\s+(.*)$", s)
        if not m: sys.exit(f"unparsable line: {s[:60]}")
        lines.append((m.group(1).strip().lower(), m.group(2).strip()))
    return title, cast, minutes, lines

def chars():
    by = {}
    for c in CAST["characters"]:
        by[c["key"]] = c; by[c["name"].lower()] = c
        first = c["name"].split()[0].lower(); by.setdefault(first, c)
        if first in ("coach", "aunty", "uncle", "mr.", "mrs."): by[c["name"].split()[1].lower()] = c
    return by

def lexicon_check(lines):
    terms = LEX["terms"]; known = {k.lower() for k in terms}
    known_words = set(); [known_words.update(k.lower().split()) for k in terms]
    syll = set(LEX.get("_respelling_syllables", []))
    missing = set()
    for _, text in lines:
        for pat in LEX["flag_patterns"]:
            for tok in re.findall(pat, text):
                t = tok.strip(".,!?;:\"'()").lower()
                if not t: continue
                if t in known or t in known_words or t in syll: continue
                if len(t) <= 2: continue
                if t in {"i", "a", "ok", "tv", "ya", "no", "am", "pm"}: continue
                missing.add(tok)
    return sorted(missing)

def build_pdict_rules():
    return [{"string_to_replace": k, "type": "alias", "alias": v["say"]} for k, v in LEX["terms"].items() if v.get("say") and v["say"].lower() != k.lower()]

def scenes(lines, limit=1900):
    out, cur, n = [], [], 0
    for sp, t in lines:
        if n + len(t) > limit and cur: out.append(cur); cur, n = [], 0
        cur.append((sp, t)); n += len(t)
    if cur: out.append(cur)
    return out

def render_elevenlabs(ep_scenes, by, outdir, pdict_id):
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY") or sys.exit("ELEVENLABS_API_KEY missing")
    prev = []
    for i, sc in enumerate(ep_scenes):
        body = {"model_id": "eleven_v3", "inputs": [{"text": t, "voice_id": by[sp]["voice_id"]} for sp, t in sc]}
        if pdict_id: body["pronunciation_dictionary_locators"] = [pdict_id]
        if prev: body["previous_request_ids"] = prev[-3:]
        r = requests.post("https://api.elevenlabs.io/v1/text-to-dialogue?output_format=mp3_44100_128", headers={"xi-api-key": key, "Content-Type": "application/json"}, json=body, timeout=600)
        if r.status_code != 200: sys.exit(f"scene {i}: {r.status_code} {r.text[:300]}")
        (outdir / f"scene{i:02d}.mp3").write_bytes(r.content)
        rid = r.headers.get("request-id");
        if rid: prev.append(rid)
        print(f"  scene {i}: {len(sc)} lines, {len(r.content):,} bytes")
        time.sleep(0.5)

def ensure_pdict_elevenlabs():
    """Create (once) a pronunciation dictionary from the lexicon; cache its locator in .pdict.json"""
    import requests
    cache = HERE / ".pdict.json"
    if cache.exists(): return json.loads(cache.read_text())
    key = os.environ["ELEVENLABS_API_KEY"]
    rules = build_pdict_rules()
    r = requests.post("https://api.elevenlabs.io/v1/pronunciation-dictionaries/add-from-rules", headers={"xi-api-key": key}, json={"name": "alakai-lexicon", "rules": rules}, timeout=60)
    if r.status_code != 200: print("pdict create failed:", r.status_code, r.text[:200]); return None
    d = r.json(); loc = {"pronunciation_dictionary_id": d["id"], "version_id": d["version_id"]}
    cache.write_text(json.dumps(loc)); return loc

def render_cartesia(lines, by, outdir):
    import requests
    key = os.environ.get("CARTESIA_API_KEY") or sys.exit("CARTESIA_API_KEY missing")
    for i, (sp, t) in enumerate(lines):
        vid = by[sp].get("cartesia_voice_id") or sys.exit(f"{sp}: cartesia_voice_id missing in cast.json")
        r = requests.post("https://api.cartesia.ai/tts/bytes", headers={"Authorization": f"Bearer {key}", "Cartesia-Version": "2026-08-14"}, json={"model_id": "sonic-3.6", "transcript": t, "voice": vid, "language": "en", "output_format": {"container": "mp3", "sample_rate": 44100, "bit_rate": 128000}}, timeout=120)
        if r.status_code != 200: sys.exit(f"line {i}: {r.status_code} {r.text[:200]}")
        (outdir / f"line{i:03d}.mp3").write_bytes(r.content)
    print(f"  {len(lines)} lines rendered")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("script"); ap.add_argument("--engine", default="elevenlabs"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--out")
    a = ap.parse_args(); load_env()
    title, cast, minutes, lines = parse(a.script)
    by = chars()
    speakers = sorted({sp for sp, _ in lines})
    unknown = [s for s in speakers if s not in by]
    if unknown: sys.exit(f"unknown speakers: {unknown}")
    distinct = {by[s]["key"] for s in speakers}
    if not (CAST["min_voices_per_episode"] <= len(distinct) <= CAST["max_voices_per_episode"]): sys.exit(f"{len(distinct)} voices; need 3 to 5")
    missing = lexicon_check(lines)
    if missing: sys.exit("lexicon missing: " + ", ".join(missing))
    words = sum(len(t.split()) for _, t in lines); chars_n = sum(len(t) for _, t in lines)
    est = words / 150
    print(f"{title}\n  {len(lines)} lines, {words} words, {chars_n:,} chars, {len(distinct)} voices, est {est:.1f} min (target {minutes})")
    if a.dry_run: print("  dry run ok"); return
    for k in distinct:
        if not [c for c in CAST["characters"] if c["key"] == k][0].get("voice_id") and a.engine == "elevenlabs": sys.exit(f"{k}: voice_id missing in cast.json")
    slug = pathlib.Path(a.script).stem
    outdir = pathlib.Path(a.out) if a.out else HERE / "out" / f"{slug}-{a.engine}"
    outdir.mkdir(parents=True, exist_ok=True)
    if a.engine == "elevenlabs":
        pd = ensure_pdict_elevenlabs(); render_elevenlabs(scenes(lines), by, outdir, pd)
    else:
        render_cartesia(lines, by, outdir)
    (outdir / "meta.json").write_text(json.dumps({"title": title, "slug": slug, "engine": a.engine, "lines": len(lines), "words": words}, indent=1))
    print(f"  wrote {outdir}")

if __name__ == "__main__":
    main()
