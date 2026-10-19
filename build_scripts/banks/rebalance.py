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

Ordered choices (on by default for ORDERED_FILES; --no-order turns it off):
  - numeric items, where every choice parses as a number with the same unit (fractions, negatives,
    "$", "%", "x 10^n", pi and sqrt forms, trailing units such as "mph", "mg/L" or "m^2", clock times such as
    "8:06 a.m.", ranges such as "10 to 20", "10–20" or "Weeks 2 to 4" (by the first number, then the second) and
    coordinate pairs such as "(3, -4)" (by x, then y)), keep their
    choices in ascending numeric order, as the real ACT does, because the app teaches backsolving
    from the middle choice;
  - "Student N" style items (Student, Scientist, Hypothesis, Geologist, Biologist N, singles before
    pairs) keep 1, 2, 3 order, with None / Neither / Both / All three last.
  The key letter of an ordered item is then fixed by its values. For ACT Math, which was authored with
  five choices (source/act_drills_math_5choice.json), the script balances letters by choosing, per
  numeric item, which wrong choice to leave out: leaving out one below the key moves the key up a
  letter, one above leaves it where it is. A wrong choice with no distractor note is always the one
  left out when there is one. Items that cannot move are left in order, and the remaining (non-ordered)
  items are shuffled to even out the rest; keys.py accepts 15% to 35% per letter.

A file already inside the band (every position between 15% and 35% of keyed items) is left alone
unless --force (ordered files are always re-derived, which is stable). --check prints the distribution and exits 1 if any file is outside the band.
Re-running is stable: the same seed and input give the same output.
After changing the podcast checks, run build_scripts/podcast/publish.py to rebuild data/episodes.json.
"""
import argparse, glob, json, math, os, random, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LETTERS = "ABCDE"
LO, HI = 0.15, 0.35
# Files where capital letters in the text are variables or labels, not choice letters (checked by hand).
LETTERS_ARE_VARIABLES = {"act/drills_math.json", "act/drills_science.json", "sat/drills_math.json"}
ANCHOR_TAIL = re.compile(r"^\s*(none\b|neither\b|both\b|all of\b|all three\b|all the\b|cannot be determined|it cannot be determined|not enough information)", re.I)
# Files whose numeric and "Student N" choices keep their natural order.
ORDERED_FILES = {"act/drills_math.json", "act/drills_science.json"}
FIVE_CHOICE_SOURCE = {"act/drills_math.json": os.path.join(os.path.dirname(os.path.abspath(__file__)), "source", "act_drills_math_5choice.json")}
LABEL = re.compile(r"^\s*(Students?|Scientists?|Hypothes[ie]s|Geologists?|Biologists?)\s+(\d+)((?:\s*(?:,|and|,\s*and)\s*\d+)*)\b(.*)$", re.I)
NO_CHANGE = re.compile(r"^\s*NO CHANGE\b")
CHOICE_REF = re.compile(r"\b([Cc]hoices?|[Oo]ptions?|[Aa]nswer choices?)(\s+)([A-E])\b((?:\s*(?:,|and|or|,\s*and|,\s*or)\s*[A-E]\b)*)")
BARE = re.compile(r"(?<![A-Za-z0-9'ʻ\-])([A-E])(?![A-Za-z0-9'ʻ\-])")
TEXT_FIELDS = ("explain", "worked", "hint")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from act_math_to_4 import pick_removal  # the 5-to-4 rule: which wrong choice is least plausible


NUM = r"[-−]?\s*\d[\d,]*(?:\.\d+)?(?:/\d+)?"
CLOCK = re.compile(r"^(\d{1,2}):(\d{2})\s*(?:([ap])\.?\s*m\.?)?$", re.I)
RANGE = re.compile(r"^(?:([A-Za-z]+)\s+)?(" + NUM + r")(?:\s*(?:to|–|—)\s*|-)(" + NUM + r")\s*([%°A-Za-z/ .²³^0-9]*)$", re.I)
PAIR = re.compile(r"^\(\s*(" + NUM + r")\s*,\s*(" + NUM + r")\s*\)$")


def _num(s):
    s = s.replace("−", "-").replace(",", "").replace(" ", "")
    if "/" in s:
        a, b = s.split("/"); return float(a) / float(b)
    return float(s)


def _unit(u):
    u = re.sub(r"\^\s*2\b", "²", u.strip()); u = re.sub(r"\^\s*3\b", "³", u)
    return u.lower().rstrip(".").strip()


def numeric_value(text):
    """(value, unit) when the choice is a number with an optional unit, else None. value is a tuple, so clock times
    (minutes after midnight), ranges ("10 to 20", "10–20", "Weeks 2 to 4": first number, then second) and
    coordinate pairs ("(3, -4)": x, then y) sort with plain numbers."""
    raw = text.strip()
    m = CLOCK.match(raw)
    if m:
        h, mi, ap = int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()
        if ap == "a" and h == 12: h = 0
        if ap == "p" and h != 12: h += 12
        return (float(h * 60 + mi),), "clock"
    m = PAIR.match(raw)
    if m: return (_num(m.group(1)), _num(m.group(2))), "pair"
    m = RANGE.match(raw)
    if m:
        unit = _unit(m.group(4) or "")
        if unit and (re.search(r"\d", unit) or not re.fullmatch(r"[%°a-z/ .²³]+", unit)): return None
        try: lo, hi = _num(m.group(2)), _num(m.group(3))
        except (ValueError, ZeroDivisionError): return None
        return (lo, hi), "range:" + (m.group(1) or "").lower() + ":" + unit
    v = _scalar(raw)
    return ((v[0],), v[1]) if v else None


def _scalar(text):
    t = text.strip().replace("−", "-").replace("–", "-")
    t = re.sub(r"\s*\^\s*([23])\s*$", lambda m: "²" if m.group(1) == "2" else "³", t) if re.search(r"[A-Za-z]\s*\^\s*[23]\s*$", t) else t
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    t = re.sub(r"^\$\s*", "", t); t = re.sub(r"^-\s*\$\s*", "-", t)
    t = re.sub(r"\s*[x×]\s*10\s*\^\s*", "*10**", t)
    m = re.match(r"^([-+0-9.\s/*()^]|sqrt\(|pi\b|π|\*\*)+", t)
    if not m: return None
    expr, unit = m.group(0), t[m.end():].strip()
    if not re.search(r"\d|pi|π", expr): return None
    if unit and (re.search(r"\d", unit) or not re.fullmatch(r"[%°A-Za-z/ .²³]+", unit)): return None
    e = expr.strip().replace("^", "**").replace("π", "pi")
    e = re.sub(r"sqrt\(", "math.sqrt(", e); e = re.sub(r"(?<![A-Za-z.])pi\b", "math.pi", e)
    e = re.sub(r"(\d|\))\s*(math\.|\()", r"\1*\2", e)
    e = re.sub(r"(\d)\s+(\d)", r"\1 \2", e)
    try: v = float(eval(e, {"__builtins__": {}, "math": math}))
    except Exception: return None
    return v, unit.lower().rstrip(".")


def numeric_order(choices):
    """Ascending order (list of old positions) when every choice is a number with the same unit, else None."""
    vals = [numeric_value(c) for c in choices]
    if any(v is None for v in vals): return None
    if len({u for _, u in vals}) != 1 or len({tuple(round(x, 9) for x in v) for v, _ in vals}) != len(vals): return None
    return sorted(range(len(choices)), key=lambda i: vals[i][0])


def label_order(choices):
    """1, 2, 3 order for "Student N" style choices (singles before pairs, anchors last), else None."""
    keys, tail = {}, []
    for i, c in enumerate(choices):
        m = LABEL.match(c)
        if m: keys[i] = (len(re.findall(r"\d+", m.group(2) + m.group(3))), [int(x) for x in re.findall(r"\d+", m.group(2) + m.group(3))])
        elif ANCHOR_TAIL.match(c): tail.append(i)
        else: return None
    if len(keys) < 2: return None
    return sorted(keys, key=lambda i: keys[i]) + tail


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


def canonical(it):
    """NO CHANGE first, None / Neither / Both / All of choices last, the rest in text order, so the shuffle that
    follows depends only on the item and not on its current order (re-running the script is then stable)."""
    ch = it["choices"]; n = len(ch)
    head = [p for p in range(n) if NO_CHANGE.match(ch[p])][:1]
    tail = sorted((p for p in range(n) if p not in head and ANCHOR_TAIL.match(ch[p])), key=lambda p: ch[p])
    mid = sorted((p for p in range(n) if p not in head and p not in tail), key=lambda p: ch[p])
    apply_perm(it, head + mid + tail)


def assign_free(free, counts, rng, stable=False):
    """Shuffle each movable item so its key lands on the least-used free position."""
    if stable: free = sorted(free, key=lambda x: x[0]["id"])
    order = list(range(len(free))); rng.shuffle(order)
    for idx in order:
        it, pins = free[idx]
        n = len(it["choices"])
        slots_free = [p for p in range(n) if p not in pins]
        low = min(counts[p] for p in slots_free)
        target = rng.choice([p for p in slots_free if counts[p] == low])
        others = [o for o in range(n) if o not in pins and o != it["answer"]]
        rng.shuffle(others)
        new_order = [None] * n
        for p in pins: new_order[p] = p
        new_order[target] = it["answer"]
        slots = [p for p in range(n) if new_order[p] is None]
        for p, o in zip(slots, others): new_order[p] = o
        apply_perm(it, new_order)
        counts[target] += 1


def five_choice_options(src):
    """For a 5-choice numeric source item: [(key position, kept old indices, is_default)] per allowed left-out choice."""
    ch, ans = src["choices"], src["answer"]
    if len(ch) != 5 or numeric_order(ch) is None: return None
    dis = src.get("distractors") or [""] * 5
    wrong = [i for i in range(5) if i != ans]
    bare = [i for i in wrong if not (dis[i] or "").strip()]
    cands = bare or wrong  # a choice with no distractor note is never kept over one that has one
    vals = {i: numeric_value(ch[i])[0] for i in range(5)}
    out = []
    for d in cands:
        keep = sorted((i for i in range(5) if i != d), key=lambda i: vals[i])
        out.append((keep.index(ans), keep, d))
    return out


def build_from_source(it, src, keep):
    """Rewrite it's choices, distractors, traps and answer from the 5-choice source, keeping `keep` in that order."""
    it["choices"] = [src["choices"][i] for i in keep]
    if src.get("distractors"): it["distractors"] = [src["distractors"][i] for i in keep]
    if src.get("traps"): it["traps"] = [src["traps"][i] for i in keep]
    it["answer"] = keep.index(src["answer"])


def order_and_balance(items, rel, seed):
    """Ordered mode: see the module docstring. Returns (ordered, flexible, shuffled, fixed) counts."""
    rng = random.Random(f"{seed}:{rel}:ordered")
    src_items = {}
    if rel in FIVE_CHOICE_SOURCE and os.path.exists(FIVE_CHOICE_SOURCE[rel]):
        src_items = json.load(open(FIVE_CHOICE_SOURCE[rel], encoding="utf-8"))["items"]
    keyed = [it for it in items if it.get("choices") and isinstance(it.get("answer"), int)]
    counts = Counter(); flex, free = [], []; n_ordered = n_fixed = 0
    for it in keyed:
        src = src_items.get(it["id"])
        opts = five_choice_options(src) if src else None
        if opts and src["choices"][src["answer"]] == it["choices"][it["answer"]]:
            # The default is the choice banks/act_math_to_4.py leaves out (recomputed from the source, so reruns agree).
            default = pick_removal(dict(src, id=it["id"]))
            if len({p for p, _, _ in opts}) == 1:
                pos, keep, _ = next(o for o in opts if o[2] == default) if default is not None and any(o[2] == default for o in opts) else opts[0]
                build_from_source(it, src, keep); counts[pos] += 1; n_ordered += 1
            else:
                flex.append((it, src, opts, default))
            continue
        order = numeric_order(it["choices"]) or label_order(it["choices"])
        if order is not None:
            apply_perm(it, order); counts[it["answer"]] += 1; n_ordered += 1; continue
        if unsafe_letters(it, rel):
            counts[it["answer"]] += 1; n_fixed += 1; continue
        canonical(it)
        pins = pinned_positions(it["choices"])
        if it["answer"] in pins or len(pins) >= len(it["choices"]):
            counts[it["answer"]] += 1; n_fixed += 1
        else:
            free.append((it, pins))
    # Flexible numeric items: put the key on the least-used letter; ties keep the conversion's original choice.
    flex.sort(key=lambda x: x[0]["id"]); free.sort(key=lambda x: x[0]["id"])
    order = list(range(len(flex))); rng.shuffle(order)
    for idx in order:
        it, src, opts, default = flex[idx]
        low = min(counts[p] for p, _, _ in opts)
        best = [o for o in opts if counts[o[0]] == low]
        pick = next((o for o in best if o[2] == default), None) or best[0]
        build_from_source(it, src, pick[1]); counts[pick[0]] += 1
    assign_free(free, counts, rng, stable=True)
    return n_ordered, len(flex), len(free), n_fixed


def write_drills(path, items):
    with open(path, "w", encoding="utf-8") as f: f.write(json.dumps(items, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_checks(path, items):
    with open(path, "w", encoding="utf-8") as f: f.write("[\n" + ",\n".join(" " + json.dumps(q, ensure_ascii=False) for q in items) + "\n]\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="reshuffle files that are already inside the band")
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if a file is outside the band")
    ap.add_argument("--seed", default="alakai-2026-10")
    ap.add_argument("--no-order", action="store_true", help="treat ORDERED_FILES like any other file (numeric choices get shuffled)")
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
        if rel in ORDERED_FILES and not a.no_order:
            o, fl, sh, fx = order_and_balance(items, rel, a.seed)
            write_drills(path, items)
            print(f"{rel}: before {before}\n{' ' * len(rel)}  after  {fmt(items)}  ({o} in fixed order, {fl} ordered with a chosen left-out choice, {sh} shuffled, {fx} kept in place)")
            continue
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
