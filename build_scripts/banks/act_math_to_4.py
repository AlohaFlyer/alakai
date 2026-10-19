#!/usr/bin/env python3
"""banks/act_math_to_4.py: one-time conversion of data/act/drills_math.json from 5 to 4 answer choices.

The enhanced ACT (2025) gives Math four answer choices instead of five (counselorblog.act.org,
"The Enhanced ACT Explained": "The math section now includes four answer choices instead of five.").
For each 5-choice item, one wrong choice is removed, the least plausible one:
  1. a wrong choice with no distractor explanation, else
  2. one with no named trap (trap null, then "other"), else
  3. for numeric choices, the one furthest from the key (log ratio), else the last wrong choice.
answer, distractors and traps are remapped to the remaining choices. Idempotent: 4-choice items are left alone.
Run banks/rebalance.py afterwards to even out the key letters.
"""
import json, math, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "data" / "act" / "drills_math.json"
NUM = re.compile(r"^\s*\$?\s*(-?\d[\d,]*\.?\d*)")

def num(s):
    m = NUM.match(s.replace("−", "-"))
    if not m: return None
    try: return float(m.group(1).replace(",", ""))
    except ValueError: return None

def pick_removal(it):
    ans = it["answer"]; ch = it["choices"]; dis = it.get("distractors") or [""] * len(ch); traps = it.get("traps") or [None] * len(ch)
    key_val = num(ch[ans])
    def score(i):
        s = 0.0
        if not (dis[i] or "").strip(): s += 1000
        t = traps[i]
        if t is None: s += 100
        elif t == "other": s += 50
        v = num(ch[i])
        if v is not None and key_val is not None:
            a, b = abs(v) + 1e-9, abs(key_val) + 1e-9
            s += min(40, abs(math.log(a / b)) * 10) + (5 if (v < 0) != (key_val < 0) else 0)
        return s + i * 1e-3  # stable tie-break toward later choices
    wrong = [i for i in range(len(ch)) if i != ans]
    return max(wrong, key=score)

def main():
    items = json.loads(PATH.read_text())
    changed = 0
    for it in items:
        ch = it.get("choices") or []
        if len(ch) != 5: continue
        drop = pick_removal(it)
        keep = [i for i in range(5) if i != drop]
        it["choices"] = [ch[i] for i in keep]
        if "distractors" in it: it["distractors"] = [it["distractors"][i] for i in keep]
        if "traps" in it and isinstance(it["traps"], list): it["traps"] = [it["traps"][i] for i in keep]
        it["answer"] = keep.index(it["answer"])
        changed += 1
    PATH.write_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"act math: {changed} items converted to 4 choices")

if __name__ == "__main__":
    sys.exit(main())
