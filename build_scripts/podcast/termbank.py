#!/usr/bin/env python3
"""termbank.py [--voice pono] [--only a,b,c]
Renders every Hawaiian term in lexicon.json once, in the hawaiian_native voice, raw spelling, eleven_v3,
into out/termbank/<slug>.mp3, trimmed of leading/trailing silence. These clips are spliced into other
characters' lines by render2.py. Re-run with --only after a lexicon fix; existing clips are kept otherwise.
"""
import argparse, os, re, sys, pathlib, subprocess, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R
from render2 import HAW, slug, tts

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--voice", default="pono"); ap.add_argument("--only", default=""); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(); R.load_env(); key = os.environ["ELEVENLABS_API_KEY"]
    vid = R.chars()[a.voice]["voice_id"]
    out = HERE / "out" / "termbank"; out.mkdir(parents=True, exist_ok=True)
    sel = [t for t in HAW if not a.only or t in a.only.split(",")]
    for t in sel:
        f = out / f"{slug(t)}.mp3"; raw = out / f"{slug(t)}.raw.mp3"
        if f.exists() and not a.force: continue
        tts(key, vid, f"{t}.", raw)
        # trim silence and the trailing period pause
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse", "-b:a", "128k", str(f)], check=True)
        raw.unlink(); print(" ", t)
    print(f"termbank: {len(list(out.glob('*.mp3')))} clips")

if __name__ == "__main__":
    main()
