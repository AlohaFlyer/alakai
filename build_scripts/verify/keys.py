#!/usr/bin/env python3
"""verify/keys.py [sat|act|all]: structural checks on the content banks. Exit 1 on failure."""
import json, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIN_PER_SKILL = int(os.environ.get("MIN_PER_SKILL", "16"))
REQ = ["id", "section", "skill", "difficulty", "stem", "choices", "answer", "explain", "hint", "worked"]

def load(path):
    with open(path, encoding="utf-8") as f: return json.load(f)

def check_test(test):
    d = os.path.join(ROOT, "data", test)
    errs, warns = [], []
    skills = load(os.path.join(d, "skills.json"))
    skill_ids = {}
    for sec in skills["sections"]:
        for sk in sec["skills"]:
            if sk["id"] in skill_ids: errs.append(f"dup skill id {sk['id']}")
            skill_ids[sk["id"]] = sec["id"]
    drills = []
    for p in sorted(glob.glob(os.path.join(d, "drills*.json"))): drills += load(p)
    ids, stems, per = set(), set(), {k: 0 for k in skill_ids}
    for it in drills:
        for k in REQ:
            if k not in it: errs.append(f"{it.get('id','?')}: missing {k}")
        if it["id"] in ids: errs.append(f"dup item id {it['id']}")
        ids.add(it["id"])
        if it["skill"] not in skill_ids: errs.append(f"{it['id']}: unknown skill {it['skill']}")
        elif skill_ids[it["skill"]] != it["section"]: errs.append(f"{it['id']}: section {it['section']} does not match skill's section {skill_ids[it['skill']]}")
        else: per[it["skill"]] += 1
        ch = it.get("choices", [])
        if ch:
            want = 5 if (test == "act" and it["section"] == "math") else 4
            if len(ch) != want: errs.append(f"{it['id']}: {len(ch)} choices, want {want}")
            if not isinstance(it["answer"], int) or not (0 <= it["answer"] < len(ch)): errs.append(f"{it['id']}: answer index out of range")
            if len(set(c.strip().lower() for c in ch)) != len(ch): errs.append(f"{it['id']}: duplicate choices")
            if "distractors" in it and len(it["distractors"]) != len(ch): warns.append(f"{it['id']}: distractors length {len(it['distractors'])}")
        else:
            if not isinstance(it["answer"], str): errs.append(f"{it['id']}: free-response answer must be a string")
        if it["difficulty"] not in (1, 2, 3): errs.append(f"{it['id']}: difficulty {it['difficulty']}")
        key = (it.get("passage", "") + it["stem"]).strip().lower()
        if key in stems: errs.append(f"{it['id']}: duplicate stem")
        stems.add(key)
        if len(it["explain"]) < 40: warns.append(f"{it['id']}: explanation short")
    for k, n in per.items():
        if n < MIN_PER_SKILL: errs.append(f"skill {k}: {n} items, need {MIN_PER_SKILL}")
    cards = []
    for p in sorted(glob.glob(os.path.join(d, "cards*.json"))): cards += load(p)
    cids = set()
    for c in cards:
        for k in ["id", "section", "topic", "front", "back"]:
            if k not in c: errs.append(f"card {c.get('id','?')}: missing {k}")
        if c["id"] in cids: errs.append(f"dup card id {c['id']}")
        cids.add(c["id"])
        if len(c["back"].split()) > 30: warns.append(f"card {c['id']}: back is long")
    timed = load(os.path.join(d, "timed.json")) if os.path.exists(os.path.join(d, "timed.json")) else {"modules": []}
    for m in timed["modules"]:
        pool = [it for it in drills if it["section"] == m["section"] and it.get("timed_ok", True)]
        if len(pool) < m["count"]: errs.append(f"module {m['id']}: pool {len(pool)} < count {m['count']}")
    print(f"{test}: {len(drills)} drills, {len(cards)} cards, {len(timed['modules'])} modules, {len(skill_ids)} skills")
    for w in warns[:20]: print("  warn:", w)
    if len(warns) > 20: print(f"  ... {len(warns)-20} more warnings")
    return errs

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    tests = ["sat", "act"] if which == "all" else [which]
    allerrs = []
    for t in tests:
        if not os.path.exists(os.path.join(ROOT, "data", t, "skills.json")): print(f"{t}: no skills.json yet"); continue
        allerrs += [f"[{t}] {e}" for e in check_test(t)]
    if allerrs:
        print("FAILURES:"); [print("  " + e) for e in allerrs[:60]]
        if len(allerrs) > 60: print(f"  ... {len(allerrs)-60} more")
        sys.exit(1)
    print("keys ok")
