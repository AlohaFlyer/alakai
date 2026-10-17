#!/usr/bin/env python3
"""hawaiian_ipa.py: rule-based IPA for Hawaiian words (orthography is phonemic).
Vowels: a /a/ e /e/ i /i/ o /o/ u /u/; kahakō = long (ː). ʻokina = glottal stop /ʔ/.
Consonants: h k l m n p w. 'w' is [v] after i or e, [w] after u or o, either word-initially or after a (we use [w]).
Diphthongs (falling, first vowel stressed): ai au ae ao ei eu oi ou iu. Stress: penultimate mora-ish; we mark
primary stress on the last long vowel/diphthong if any, else the penultimate syllable; secondary stress every other syllable back.
Output is ElevenLabs-friendly IPA in slashes. Usage: python3 hawaiian_ipa.py Waimea Kīpuʻupuʻu
"""
import re, sys, unicodedata

LONG = {"ā":"a","ē":"e","ī":"i","ō":"o","ū":"u"}
VOW = "aeiou"
DIPH = {"ai","au","ae","ao","ei","eu","oi","ou","iu"}

def normalize(w):
    w = w.replace("'", "ʻ").replace("‘", "ʻ").replace("`", "ʻ")
    return w

def syllabify(word):
    """Return list of syllables as (onset, nucleus, long) for one Hawaiian word (no spaces)."""
    w = normalize(word).lower()
    out = []; i = 0; onset = ""
    while i < len(w):
        c = w[i]
        if c == "ʻ": onset = "ʔ"; i += 1; continue
        if c in "hklmnpw": onset = c; i += 1; continue
        if c in VOW or c in LONG:
            base = LONG.get(c, c); longv = c in LONG
            # diphthong?
            if not longv and i + 1 < len(w) and w[i+1] in VOW and (base + w[i+1]) in DIPH:
                out.append((onset, base + w[i+1], False)); i += 2
            elif longv and i + 1 < len(w) and w[i+1] in VOW and (base + w[i+1]) in DIPH:
                out.append((onset, base + w[i+1], True)); i += 2
            else:
                out.append((onset, base, longv)); i += 1
            onset = ""; continue
        i += 1  # skip anything else
    return out

def to_ipa(word):
    syls = syllabify(word)
    if not syls: return ""
    # stress: last heavy (long or diphthong) syllable gets primary; else penultimate
    last = len(syls) - 1
    if syls[last][2]: primary = last                      # final long vowel: Kaʻū
    elif len(syls) >= 2: primary = last - 1               # default penultimate: Wai-ME-a, Ho-no-KA-ʻa
    else: primary = 0
    # diphthong/long penult already carries stress naturally; nothing else to do
    parts = []
    for k, (o, n, l) in enumerate(syls):
        ons = o
        if ons == "w":
            prev = syls[k-1][1][-1] if k else ""
            ons = "v" if prev in ("i", "e") else "w"
        nuc = n if len(n) == 1 else n  # diphthong kept as two vowel letters
        if l: nuc = nuc[0] + "ː" + nuc[1:]
        mark = "ˈ" if k == primary else ("ˌ" if (primary - k) % 2 == 0 and k != primary and len(syls) > 3 else "")
        parts.append(mark + ons + nuc)
    return "".join(parts)

def phrase_ipa(phrase):
    return " ".join(to_ipa(w) for w in normalize(phrase).split())

if __name__ == "__main__":
    for w in sys.argv[1:]: print(w, "/" + phrase_ipa(w) + "/")
