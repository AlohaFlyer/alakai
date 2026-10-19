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
Rules: exactly 4 choices on every choice item, ACT Math included (the enhanced ACT, 2025, moved Math from five choices to four: "The math section now includes four answer choices instead of five", counselorblog.act.org, The Enhanced ACT Explained). The one exception is SAT student-produced response items, which use `"choices":[]` and `"answer":"23"` as a string, with `"answer_alt":["23.0"]` optional. `distractors` and `traps` are arrays aligned with `choices` (`traps` entries are trap ids from engine.js TRAP_NAMES, or null for the key). Keys must be balanced: in each section no key position above 35% or below 15% (keys.py fails otherwise); run `python3 build_scripts/banks/rebalance.py` to reshuffle choice order with everything mapped along. ACT Math and ACT Science keep numeric choices (plain numbers and units such as m^2, clock times by time of day, ranges such as "10 to 20" or "Weeks 2 to 4" by the first number, coordinate pairs by x then y) in ascending order and "Student 1 / 2 / 3" style choices in number order (None, Neither, Both, All three last), as the real ACT does; rebalance.py balances those files by choosing which wrong choice an ACT Math item leaves out (from `build_scripts/banks/source/act_drills_math_5choice.json`) and by shuffling only the non-ordered items, and keys.py fails an ACT Math or Science item that is out of order. `answer` is a 0-based index for choice items. `difficulty` 1 easy, 2 medium, 3 hard, roughly 30/45/25 split. `timed_ok` false for items too long for a timed module. Math may use plain-text notation (x^2, sqrt(x), 3/4, pi) and simple tables; no LaTeX, no images.

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

Passage modules (ACT Reading and Science). A module with a `passages` block is built from whole passages, never loose items (engine.js `buildPassageModule`): each entry of `sets` (optionally `repeat`ed) is one passage block of a `type` (Reading: the label before the colon at the start of the passage, such as `LITERARY NARRATIVE`; Science: the skill), filled with whole passages of that type (least-seen first), trimmed to `items`, items in bank order inside each passage. `order: "sets"` keeps the sets in the order written, `order: "bank"` sorts them by the bank position of their first passage. `checkpoint` is the Time squeeze page's halfway mark (`minute`, `sets` done). The timed page shows each passage once in a panel (sticky beside the questions on wide screens) with its questions under it. Items that share a passage in a loose module (the few ACT Math tables) are kept next to each other. SAT items carry one short passage each, so SAT modules are unchanged.
```json
{"id":"act-reading","section":"reading","minutes":40,"count":36,"passages":{"type_from":"label","order":"sets","checkpoint":{"minute":20,"sets":2},
 "sets":[{"type":"LITERARY NARRATIVE","name":"Literary narrative","items":9},{"type":"SOCIAL SCIENCE","items":9},{"type":"HUMANITIES","items":9},{"type":"NATURAL SCIENCE","items":9}]}}
```
Bank shortfall, noted here as the build rule asks: the real ACT Reading section is 4 passages of about 9 questions, but this bank's passages carry 4 or 5 questions each (17 passages: 3 each of Literary narrative, Social science, Humanities and Natural science with 5 questions, 5 paired sets with 4). So each of the 4 Reading blocks is padded from the same passage type: one 5-question passage plus 4 questions of a second passage of that type (shown as "part 1 of 2", "part 2 of 2"), 9 questions and 10 minutes a block. Paired passages (`reading-integration`) do not fit a 9-question block yet and stay in drills and placement until the bank has paired sets of 9. Science passages carry 4 questions (15 passages; `science-research` 005 has a fifth that is not `timed_ok`, `science-conflict` 009 and 017 have 3 timed items), so the 40-question Science module is 10 whole passages, 4 minutes each, in bank order: 4 data representation, 4 research summaries, 2 conflicting viewpoints (the real test has 6 or 7 longer passages). A type with too few timed items is padded from another passage of the section and `keys.py` warns. To move toward the real shape, write longer passages (9 Reading or 6 to 7 Science questions) and raise `items` in timed.json.

## QA before you finish
1. Run `python3 build_scripts/verify/keys.py` from the repo root: it checks ids unique, answer index in range, 4 choices, required fields, no duplicate stems, per-skill minimum, 40+ cards per section, and key-letter balance (drills per section and podcast checks per show).
2. Blind-solve pass: re-read every item as a student with the explanation hidden; if you would not confidently pick the key, rewrite the item.
3. No item may depend on outside knowledge beyond the test's scope.
