# Content bank schema (data/sat/*, data/act/*)

All items are ORIGINAL. Never reproduce or closely paraphrase College Board, ACT, Khan Academy, or any prep-book item. Passages are written fresh (prefer Hawaiʻi Island settings where natural: Waimea, Kohala, Hilo, Mauna Kea, paniolo, fishponds, hula, ranching, astronomy, coffee, volcanology). Answers must be unambiguous. Explanations teach the move, not just the answer.

## skills.json
```json
{"test":"sat","sections":[{"id":"rw","name":"Reading and Writing","skills":[{"id":"rw-ii-central","name":"Central Ideas and Details","domain":"Information and Ideas","tip":"one-line strategy"}]}]}
```
Skill ids: lowercase, hyphenated, prefixed by section id. ACT sections: english, math, reading, science.

## drills.json (array)
```json
{"id":"sat-rw-ii-central-001","section":"rw","skill":"rw-ii-central","difficulty":2,
 "passage":"optional passage or table text (plain text; use \\n for line breaks)",
 "stem":"the question",
 "choices":["A text","B text","C text","D text"],
 "answer":1,
 "explain":"why the keyed answer is right, 2 to 4 sentences, teaches the move",
 "distractors":["why A is tempting and wrong","(keyed) ","why C is wrong","why D is wrong"],
 "hint":"one nudge that does not give it away",
 "worked":"a fully worked solution, 3 to 8 short steps, each on its own line",
 "timed_ok":true}
```
Rules: exactly 4 choices on every choice item, ACT Math included (the enhanced ACT, 2025, moved Math from five choices to four: "The math section now includes four answer choices instead of five", counselorblog.act.org, The Enhanced ACT Explained). The one exception is SAT student-produced response items, which use `"choices":[]` and `"answer":"23"` as a string, with `"answer_alt":["23.0"]` optional. `distractors` and `traps` are arrays aligned with `choices` (`traps` entries are trap ids from engine.js TRAP_NAMES, or null for the key). Keys must be balanced: in each section no key position above 35% or below 15% (keys.py fails otherwise); run `python3 build_scripts/banks/rebalance.py` to reshuffle choice order with everything mapped along. `answer` is a 0-based index for choice items. `difficulty` 1 easy, 2 medium, 3 hard, roughly 30/45/25 split. `timed_ok` false for items too long for a timed module. Math may use plain-text notation (x^2, sqrt(x), 3/4, pi) and simple tables; no LaTeX, no images.

Minimum per skill: 16 items. Target 20.

## cards.json (array)
```json
{"id":"sat-card-punct-001","section":"rw","topic":"Punctuation","front":"When do you use a semicolon between clauses?","back":"Between two independent clauses with no conjunction.","tags":["grammar"]}
```
Verbatim-answer facts only: rules, definitions, formulas not on the SAT reference sheet, all needed ACT geometry/trig formulas, unit conversions, transition-word meanings, science graph-reading moves. 40 to 60 cards per section. Backs under 25 words.

## timed.json
```json
{"modules":[{"id":"sat-rw-m1","section":"rw","name":"Reading and Writing Module 1","minutes":32,"count":27}]}
```
Module items are drawn at runtime from drills where `timed_ok` is true, in difficulty order easy to hard, so you only declare modules. SAT: rw m1/m2 27 items 32 min, math m1/m2 22 items 35 min. ACT (2025 enhanced, verify against act.org): english 50 items 35 min, math 45 items 50 min, reading 36 items 40 min, science 40 items 40 min.

## QA before you finish
1. Run `python3 build_scripts/verify/keys.py` from the repo root: it checks ids unique, answer index in range, 4 choices, required fields, no duplicate stems, per-skill minimum, 40+ cards per section, and key-letter balance (drills per section and podcast checks per show).
2. Blind-solve pass: re-read every item as a student with the explanation hidden; if you would not confidently pick the key, rewrite the item.
3. No item may depend on outside knowledge beyond the test's scope.
