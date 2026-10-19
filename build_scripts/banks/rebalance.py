#!/usr/bin/env python3
"""banks/rebalance.py [--force] [--check] [--seed N]: even out answer-key letters.

For each drills file in data/sat and data/act, and for each show's podcast checks
(build_scripts/podcast/checks/<test>-ep*.json, balanced across the whole show), choice order is
shuffled per item with a seeded RNG so the key letters come out roughly even. Each item's answer,
distractors and traps move with their choices, and "Choice X" / "choices X and Y" references in
explain, worked, hint and distractors are rewritten to the new letters.

Kept in place:
  - "NO CHANGE" as the first choice (ACT English convention);
  - a trailing block of None / Neither / Both / All of / Cannot be determined choices;
  - items whose text names a choice letter in a way this script cannot rewrite safely
    (for example "Both A and B are ..."); in files where letters are math or science variables
    (angle A, cost C, Reef A) only "Choice X" patterns count.
Free-response items (no choices) are skipped.

A file already inside the band (every position between 15% and 35% of keyed items) is left alone
unless --force. --check prints the distribution and exits 1 if any file is outside the band.
Re-running is stable: the same seed and input give the same output.
After changing the podcast checks, run build_scripts/podcast/publish.py to rebuild data/episodes.json.
"""
import argparse, glob, json, os, random, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LETTERS = "ABCDE"
LO, HI = 0.15, 0.35
# Files where capital letters in the text are variables or labels, not choice letters (checked by hand).
LETTERS_ARE_VARIABLES = {"act/drills_math.json", "act/drills_science.json", "sat/drills_math.json"}
ANCHOR_TAIL = re.compile(r"^\s*(none\b|neither\b|both\b|all of\b|cannot be determined|it cannot be determined|not enough information)", re.I)
NO_CHANGE = re.compile(r"^\s*NO CHANGE\b")
CHOICE_REF = re.compile(r"\b([Cc]hoices?|[Oo]ptions?|[Aa]nswer choices?)(\s+)([A-E])\b((?:\s*(?:,|and|or|,\s*and|,\s*or)\s*[A-E]\b)*)")
BARE = re.compile(r"(?<![A-Za-z0-9'ʻ\-])([A-E])(?![A-Za-z0-9'ʻ\-])")
TEXT_FIELDS = ("explain", "worked", "hint")


def distribution(items):
    c = Counter(LETTERS[it["answer"]] for it in items if it.get("choices"))
    n = sum(c.values())
    width = max((len(it["choices"]) for it in items if it.get("choices")), default=4)
    return c, n, width


def in_band(items):
    c, n, width = distribution(items)
    if not n: return True
    return all(LO <= c.get(LETTERS[k], 0) / n <= HI for k in range(width))


def fmt(items):
    c, n, width = distribution(items)
    return " ".join(f"{LETTERS[k]} {c.get(LETTERS[k], 0)} ({100 * c.get(LETTERS[k], 0) / n:.0f}%)" for k in range(width)) + f"  n={n}" if n else "no keyed items"


def pinned_positions(choices):
    pins = set()
    if choices and NO_CHANGE.match(choices[0]): pins.add(0)
    k = len(choices) - 1
    while k >= 0 and ANCHOR_TAIL.match(choices[k]):
        pins.add(k); k -= 1
    if len(pins) >= len(choices) - 1: pins = set(range(len(choices)))  # nothing meaningful left to move
    return pins


def texts(it):
    out = [(k, it.get(k) or "") for k in TEXT_FIELDS]
    out += [("distractors", d or "") for d in (it.get("distractors") or [])]
    return out


def unsafe_letters(it, rel):
    """True when the item's text refers to choice letters in a form we cannot rewrite."""
    if rel in LETTERS_ARE_VARIABLES: return False
    for _, t in texts(it):
        stripped = CHOICE_REF.sub("", t)
        stripped = re.sub(r"\b(Passage|Plant|Reef|Study|Trial|Site|Station|Group|Student|Table|Figure|Experiment|Scientist|Model)\s+[A-E]\b", "", stripped)
        for m in BARE.finditer(stripped):
            ch = m.group(1)
            after = stripped[m.end():m.end() + 2]
            if ch == "A" and re.match(r"\s[a-zʻ]", after): continue  # the article "A"
            return True
    return False


def remap_text(t, perm_old_to_new):
    def sub(m):
        word, sp, first, rest = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        new_first = LETTERS[perm_old_to_new[LETTERS.index(first)]]
        new_rest = re.sub(r"[A-E]\b", lambda r: LETTERS[perm_old_to_new[LETTERS.index(r.group(0))]], rest)
        return f"{word}{sp}{new_first}{new_rest}"
    return CHOICE_REF.sub(sub, t)


def apply_perm(it, new_order):
    """new_order[new_pos] = old_pos."""
    old_to_new = {old: new for new, old in enumerate(new_order)}
    it["choices"] = [it["choices"][o] for o in new_order]
    for k in ("distractors", "traps"):
        if isinstance(it.get(k), list) and len(it[k]) == len(new_order): it[k] = [it[k][o] for o in new_order]
    it["answer"] = old_to_new[it["answer"]]
    for k in TEXT_FIELDS:
        if it.get(k): it[k] = remap_text(it[k], old_to_new)
    if isinstance(it.get("distractors"), list): it["distractors"] = [remap_text(d, old_to_new) if d else d for d in it["distractors"]]


def rebalance(items, rel, seed):
    rng = random.Random(f"{seed}:{rel}")
    keyed = [it for it in items if it.get("choices") and isinstance(it.get("answer"), int)]
    if not keyed: return 0, 0
    width = max(len(it["choices"]) for it in keyed)
    counts = Counter()
    movable, fixed = [], 0
    for it in keyed:
        pins = pinned_positions(it["choices"])
        if it["answer"] in pins or len(pins) >= len(it["choices"]) or unsafe_letters(it, rel):
            counts[it["answer"]] += 1; fixed += 1
        else:
            movable.append((it, pins))
    order = list(range(len(movable))); rng.shuffle(order)
    for idx in order:
        it, pins = movable[idx]
        n = len(it["choices"])
        free = [p for p in range(n) if p not in pins]
        low = min(counts[p] for p in free)
        target = rng.choice([p for p in free if counts[p] == low])
        others = [o for o in range(n) if o not in pins and o != it["answer"]]
        rng.shuffle(others)
        new_order = [None] * n
        for p in pins: new_order[p] = p
        new_order[target] = it["answer"]
        slots = [p for p in range(n) if new_order[p] is None]
        for p, o in zip(slots, others): new_order[p] = o
        apply_perm(it, new_order)
        counts[target] += 1
    return len(movable), fixed


def write_drills(path, items):
    with open(path, "w", encoding="utf-8") as f: f.write(json.dumps(items, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_checks(path, items):
    with open(path, "w", encoding="utf-8") as f: f.write("[\n" + ",\n".join(" " + json.dumps(q, ensure_ascii=False) for q in items) + "\n]\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="reshuffle files that are already inside the band")
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if a file is outside the band")
    ap.add_argument("--seed", default="alakai-2026-10")
    a = ap.parse_args()
    bad = False
    # Drill banks, one file at a time.
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*", "drills_*.json"))):
        rel = os.path.relpath(path, os.path.join(ROOT, "data"))
        items = json.load(open(path, encoding="utf-8"))
        before = fmt(items)
        if a.check:
            ok = in_band(items); bad |= not ok
            print(f"{rel}: {before}{'' if ok else '  OUTSIDE BAND'}"); continue
        if in_band(items) and not a.force:
            print(f"{rel}: in band, left alone: {before}"); continue
        moved, fixed = rebalance(items, rel, a.seed)
        write_drills(path, items)
        print(f"{rel}: before {before}\n{' ' * len(rel)}  after  {fmt(items)}  ({moved} shuffled, {fixed} kept in place)")
    # Podcast checks, balanced across each show.
    for test in ("sat", "act"):
        files = sorted(glob.glob(os.path.join(ROOT, "build_scripts", "podcast", "checks", f"{test}-ep*.json")), key=lambda p: int(re.search(r"ep(\d+)", p).group(1)))
        per = [(p, json.load(open(p, encoding="utf-8"))) for p in files]
        allq = [q for _, qs in per for q in qs]
        rel = f"podcast checks {test} ({len(files)} files)"
        before = fmt(allq)
        if a.check:
            ok = in_band(allq); bad |= not ok
            print(f"{rel}: {before}{'' if ok else '  OUTSIDE BAND'}"); continue
        if in_band(allq) and not a.force:
            print(f"{rel}: in band, left alone: {before}"); continue
        moved, fixed = rebalance(allq, f"checks/{test}", a.seed)
        for p, qs in per: write_checks(p, qs)
        print(f"{rel}: before {before}\n{' ' * len(rel)}  after  {fmt(allq)}  ({moved} shuffled, {fixed} kept in place)")
    if a.check and bad: sys.exit(1)


if __name__ == "__main__":
    main()
