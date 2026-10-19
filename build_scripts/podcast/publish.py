#!/usr/bin/env python3
"""publish.py: rebuild data/episodes.json from audio/*.mp3 plus scripts/*.md metadata and checks/*.json.
Audio URL base comes from AUDIO_BASE env (default 'audio/' for repo-hosted, or https://audio.alakaitestprep.app/ for R2)."""
import json, os, re, subprocess, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
BASE = os.environ.get("AUDIO_BASE", "https://audio.alakaitestprep.app/")
CAST = json.loads((HERE / "cast.json").read_text())
APPROVED = json.loads((HERE / "approved.json").read_text())
eps = {"shows": {"sat": "SAT Notes Podcast", "act": "ACT Notes Podcast"}, "sat": [], "act": [], "cast": [{"name": c["name"], "role": c["role"]} for c in CAST["characters"]]}
# Episodes already published keep their entry when the mp3 is not on this machine (audio lives on R2).
try: PREV = json.loads((ROOT / "data" / "episodes.json").read_text())
except Exception: PREV = {"sat": [], "act": []}
for test in ("sat", "act"):
    for n in APPROVED.get(test, []):
        if not (ROOT / "audio" / f"{test}-ep{n}.mp3").exists():
            old = next((e for e in PREV.get(test, []) if e.get("n") == n and not e.get("coming")), None)
            if old:
                # Checks can change without re-rendering audio (for example banks/rebalance.py): always take the current file.
                check = HERE / "checks" / f"{test}-ep{n}.json"
                if check.exists(): old = dict(old, check=json.loads(check.read_text()))
                eps[test].append(old)
for mp3 in sorted((ROOT / "audio").glob("*.mp3")):
    m = re.match(r"(sat|act)-ep(\d+)\.mp3", mp3.name)
    if not m: continue
    test, n = m.group(1), int(m.group(2))
    if n not in APPROVED.get(test, []): continue
    script = HERE / "scripts" / f"{test}-ep{n}.md"
    title = topic = ""; transcript = []; homework = None
    if script.exists():
        for line in script.read_text().splitlines():
            if line.startswith("# "): title = re.sub(r"^.*?Ep \d+: ", "", line[2:]).strip()
            elif line.lower().startswith("topic:"): topic = line.split(":", 1)[1].strip()
            elif line.lower().startswith("homework:"):
                hw = line.split(":", 1)[1].strip()
                if "|" in hw: homework = {"label": hw.split("|", 1)[0].strip(), "href": hw.split("|", 1)[1].strip()}
            elif line.lower().startswith(("cast:", "facts:", "target_minutes:", "note:")): continue
            elif re.match(r"^[A-Za-zʻ' .]+?:\s", line): transcript.append(line)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)]).decode().strip())
    check = HERE / "checks" / f"{test}-ep{n}.json"
    eps[test].append({"n": n, "title": title, "topic": topic, "len": f"{int(dur//60)}:{int(dur%60):02d}", "audio": BASE + mp3.name, "bytes": mp3.stat().st_size, "transcript": "\n".join(transcript), "check": json.loads(check.read_text()) if check.exists() else [], "homework": homework})
# Scripted but not yet rendered: listed as "coming" so the season shows its shape.
for script in sorted((HERE / "scripts").glob("*.md")):
    m = re.match(r"(sat|act)-ep(\d+)\.md", script.name)
    if not m: continue
    test, n = m.group(1), int(m.group(2))
    if any(e["n"] == n for e in eps[test]): continue
    if n not in APPROVED.get(test + "_coming", []): continue
    title = topic = ""
    for line in script.read_text().splitlines():
        if line.startswith("# "): title = re.sub(r"^.*?Ep \d+: ", "", line[2:]).strip()
        elif line.lower().startswith("topic:"): topic = line.split(":", 1)[1].strip()
    eps[test].append({"n": n, "title": title, "topic": topic, "coming": True})
for k in ("sat", "act"): eps[k].sort(key=lambda e: e["n"])
(ROOT / "data" / "episodes.json").write_text(json.dumps(eps, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"episodes.json: sat {len(eps['sat'])}, act {len(eps['act'])}")
