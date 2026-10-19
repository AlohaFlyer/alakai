# Alakaʻi Test Prep: debug pass 2 fixes

Date: 2026-10-18. Fixes for the 33 findings in `docs/debug/pass2.md` (build `8b8d1d9`, report commit `746cd00`), including the three follow-ons to pass 1 fixes #9 (now #4), #26 (now #13) and #27 (now #14). Site 1.0.1 to **1.0.2** (`versions.json`, `assets/app.js`), service worker `alakai-v14` to **`alakai-v15`**.

Result: **32 of 33 addressed** (30 fixed as asked, 2 fixed differently), **1 not fixed** (not reproducible). Blocker 1/1, major 5/5, minor 18/18, cosmetic 8/9.

Verification: each group's repro was rerun with Python Playwright (Chromium; 390x844 iPhone UA, 820x1180 iPad UA, 1280x800, 320x640; light and dark) against `127.0.0.1:8765`, with the ping endpoint intercepted (no real pings) and R2 audio blocked. The service worker runs used a scratch copy served with `Cache-Control: max-age=600`; the same run on the old `sw.js` reproduced the bug. `bash build_scripts/verify/all.sh` passes (contrast, keys, links, JSON, node syntax, podcast dry runs, smoke).

## Bugs

| # | Sev | Status | What changed / how checked |
|---|---|---|---|
| 1 | blocker | fixed | New `--primary-text` token, set by `applyPalette` per theme: the effective primary darkened until it reaches 4.5:1 on both light papers (#FBF8F1, #F2EDE0), or lightened until 4.5:1 on both dark papers (#141A16, #1C2520). Recomputed on the `prefers-color-scheme` change listener and by the Settings theme select (`Alakai.setTheme`). Used for links, every focus ring (now also select, input, summary), flashcard answers, notes episode numbers, timing `.num`, the picked-choice ring, the explain bar, link-card arrows, and an edge on the pressed toggle, the current nav tab, onboarding options and answered timed-grid buttons. Bars and rings use it in dark mode. `--ok`, `--bad`, `--warn` get dark values (#5FD39A, #FF8F85, #E8B84A). `contrast.py` now checks all 26 schools in both themes (4.5:1 on both papers) plus the status colours on their tints, and fails if the CSS tokens drift. Repro: Kohala dark, card back 4.86:1, links 5.46:1, focus ring 5.46:1 (was 1.01:1); Waiākea 4.69 / 5.26; theme select light #222222 to dark #8f8f8f and back with OS scheme. Results per school below. |
| 2 | major | fixed | Install precaches with `new Request(u, { cache: 'reload' })`; a page missing from the cache is fetched with `cache: 'reload'`, and so is any other html, js or css miss before it is stored. Repro (max-age=600 copy): after the bump the cache is `alakai-vB` and `Alakai.VERSION` is the new value (old sw.js: new cache name, old 1.0.2 code). |
| 3 | major | fixed | `Alakai.parseLocalDate` / `Alakai.daysTo`: `YYYY-MM-DD` as `new Date(y, m-1, d)`, whole local days from today's local midnight (rounded for DST). Used by the dashboard, the weekly plan and the report. Repro, test 2026-11-07, Pacific/Honolulu: 09:00, 15:00 and 23:59 on 11-06 all show 1 ("day to test", singular now), 00:01 on 11-07 shows 0, 11-08 "Done"; Los Angeles 16:30 shows 1; across the DST change 7. |
| 4 | major | fixed differently | `ping_pending.sending` (timestamp) is stored before the fetch. Another page does not send while that mark is under 60 s old; the dashboard's one retry needs no "sent", a mark older than 60 s and fewer than 2 tries. Different from the brief: no client id is sent, because the Worker cannot key on one (worker/ is off limits) and the disclosure promises exactly two fields and no device ID. Instead, if the page unloads while its keepalive request is in flight, the ping is treated as sent (`ping_sent.assumed: true`): a rare miss rather than a double count. Repro, Worker answering in 1.5 s, Skip after 0.3 s: 1 POST, also after coming back more than 60 s later; failing Worker: 1 POST, a retry only after 60 s, then none. |
| 5 | major | fixed | `build_scripts/banks/rebalance.py` has an ordered mode for `act/drills_math.json` and `act/drills_science.json` (on by default, `--no-order` turns it off). Numeric items (every choice parses as a number with the same unit: fractions, negatives, `$`, `%`, `x 10^n`, pi and sqrt forms, units) are ascending; "Student/Scientist/Hypothesis/Geologist N" items are in 1, 2, 3 order with None/Neither/Both/All three last. ACT Math is balanced by choosing, per numeric item, which wrong choice to leave out of the five it was authored with (new `build_scripts/banks/source/act_drills_math_5choice.json`, from `618fefd`): a choice with no distractor note is always the one left out; otherwise the key goes to the least-used letter, ties keep the original conversion's pick. Non-ordered items are shuffled to even out the rest. Re-running is stable (verified from both the old and new files). 135 ACT Math items and 24 Science items are now in natural order; 48 ACT Math items keep a different wrong choice than before; every key, stem, explanation and worked solution is unchanged and no ACT Math text cites a letter. keys.py now fails an ACT Math or Science item out of order (and still enforces 15% to 35%). Repro: `act-math-functions-007` A 5, B 48, C 64, D 69; `act-math-geometry-019` 3, 6, 7, 11; `act-science-conflict-003` Student 1 only, 2 only, 3 only, Students 1 and 3. Distributions below. |
| 6 | major | fixed | Grid-in boxes (drills, timed, placement, one helper `AlakaiEngine.gridIn`) keep `inputmode="decimal"` with `pattern="-?[0-9./]*"` and add two on-screen keys: "−" toggles the sign and "/" inserts a fraction bar at the caret (keys do not steal focus). Unicode minus is accepted by `normalize`. Repro (iPhone UA, typing digits only, as the iOS decimal pad allows): `sat-math-adv-nonlinear-016` "3" + − gives -3, right; `sat-math-psda-inference-012` -7, right; `sat-math-alg-linear-fn-016` 36 / 13 typed with the "/" key, right. |
| 7 | minor | fixed | Each Blitz card settles once (tap or 8 s timeout); the timeout disables the choices and reveals the key; only one next card is scheduled, keyed to a card sequence number. Repro: after the timeout, choices disabled, key shown; a forced tap scored nothing (0) and the card changed once. |
| 8 | minor | fixed | Check Next disables itself on the first tap; a check choice ignores taps in the first 0.4 s after it renders; an episode row ignores taps within 0.7 s of a check tap. The last button reads "Finish the check". Repro: double tap on Next stayed on Ep 2 and moved to Check 3/3; double tap on Finish stayed on Ep 2 with "Check done". |
| 9 | minor | fixed | Dashboard `render()` takes a sequence number and stops at every await if a newer render started. Repro (ACT banks delayed 0.8 s, ACT then SAT): toggle SAT, subtitle SAT, rings Reading and Writing, Math. |
| 10 | minor | fixed | ACT break goes before Reading (`nextMod.section === 'reading' && mod.section === 'math'`). Repro (Science off): after English "Continue to Math", after Math "Take a 10-minute break, then start Reading". |
| 11 | minor | fixed | Placement is built per test and rebuilds on `alakai:test`. A toggle mid-check scores what was answered under the test it was taken in and says so, then shows the other test's intro (heading, estimate). Repro: 2 SAT answers then ACT: 2 `sat:placement` records, note "Your SAT placement answers so far (2) were scored…", "ACT placement check", 46 min, 42 ACT items. |
| 12 | minor | fixed | `data/episodes.json` is precached (still network-first). If it cannot load, the page says "You are offline… Episodes need a connection" (or "did not load" when online) instead of "being recorded". Repro: offline first visit (dashboard only) to `notes.html?ep=3` lists 14 episodes and opens the player; with the file blocked and no SW, the connection message shows. |
| 13 | minor | fixed | `Store.list(key)` returns only plain objects; used for errlog (drill redo, "Only ones I've missed", dashboard), timed (dashboard, report, SAT M2 routing), blitz (dashboard, report, quiz scores and end of round), sentlog, fulltests. `Progress.summary` drops junk timed, blitz and episode entries. A saved timed module needs array `answers`, `flags`, `chain` or it is dropped; a junk episode record is ignored. Repro with `[null, 3, "x"]` lists, `episodes {"1":null,"2":"x"}`, `timed_inprogress.answers = "x"`: drill redo, missed-only, dashboard, quiz, settings, timed, notes and the report run with no page errors. Pass 1 #26 follow-on. |
| 14 | minor | fixed | Nav tabs 44 px (min-height, inline-flex); error-log "redo", weak-spot and placement "Start here" links, strategies "Drill it", onboarding "Details" and Settings links get a 44 px tap box (`a.tap`); footer and `small > a` links get a padded hit area with no layout change. Repro (iPhone UA): nav 44, redo 44, footer 48, Drill it 44, "About this pattern" 48. Pass 1 #27 follow-on. |
| 15 | minor | fixed | Both budget tables sit in an `overflow-x:auto` box and the headers are shorter (Items, Min, Per item). Repro: at 320 px no page is wider than 320 (every page, SAT and ACT, including timing.html and 404). |
| 16 | minor | fixed | Next on an unanswered single-choice question shows "Pick one to continue." (role alert) and stays. |
| 17 | minor | fixed | `data/onboarding.json` asks Science before "Which section worries you most?"; a "No" removes Science from that list (also for "Both"), and a Science fear is dropped if Science ends up off. Repro (ACT, Science No): sections offered English, Math, Reading. |
| 18 | minor | fixed | A Science drill link while Science is off (`drill.html?section=science` or a science skill) asks "ACT Science is off… Turn Science on now?" and, on yes, saves it and starts the drill. The podcast homework button for Science says Science is off and that the drill page will ask. Repro: dialog shown, profile `science: true`, item rendered. |
| 19 | minor | fixed differently | Settings no longer creates a profile before onboarding. What was typed is saved as `profile_draft` (with a note and a link to onboarding), onboarding prefills from it and deletes it on Finish. Repro: new visitor, Settings, name, Save: no `profile`, dashboard redirects to onboarding, draft name "Kai" kept. |
| 20 | minor | fixed | `act-english-grammar-006` worked solution: "Choice B shifts number and tense; C shifts person. Answer: choice D." |
| 21 | minor | fixed | Light status colours darkened: `--ok` #176B41, `--bad` #A12A24, `--warn` #7F5600; chip text on its own 12% to 15% tint is now 4.53, 4.94 and 4.50:1 or better on both light papers (dark values 5.4:1 or better). Checked by contrast.py. |
| 22 | minor | fixed | The practice menu moves focus to its first link on open, Escape closes it and returns focus to the button, tabbing out or tapping a link closes it. Repro: focus in menu on open; after Escape hidden and focus on the button. |
| 23 | minor | fixed | Under the 12 rows: "and N more (M due: redo the due ones)" or "…, not due yet". Repro: 27 open misses: 12 rows plus "and 15 more (15 due: redo the due ones)." |
| 24 | minor | fixed | Each published script (Ep 1 to 14, both shows) has a `topic:` header line taken from the Concept column of `docs/SEASON_PLAN.md` (first letter capitalised; Sat Ep 14 "accommodations (counselor only)" reads "accommodations (ask your counselor)" for students). `publish.py` now also refreshes the topic for episodes whose mp3 is only on R2; rerun, and the only field that changed in `data/episodes.json` is `topic` (28 of 28 filled). No dialogue line was touched. |
| 25 | cosmetic | fixed | Trap id `other` is "Trap: other trap", shown as "other trap" in the error log and trap summary. |
| 26 | cosmetic | fixed | The "More episodes are being recorded" line shows only while an episode is listed as coming. |
| 27 | cosmetic | fixed | The icon prompt says "tablet" on iPad (and Android tablets): "Want the icon on your tablet to match Kohala?" |
| 28 | cosmetic | fixed | The contact step's School and Grade selects update the `{"school":"…","grade":"…"}` line and preview the school colours as they change. |
| 29 | cosmetic | fixed | After an item is answered the strike buttons, and for grid-ins the box, Check and the −// keys, are disabled. |
| 30 | cosmetic | fixed | 404.html has `<base href="/">` and runs `Alakai.boot`, so it gets the frame bar, the school palette, mark and favicon at any depth. |
| 31 | cosmetic | fixed | The timed milestone key uses a running count (`<test>.timedcount`), not the stored list capped at 50. Repro with 50 stored: a milestone after every module. |
| 32 | cosmetic | not fixed: not reproducible | `.gitignore` at `746cd00` (and every earlier commit) lists only build outputs (`docs/preview_*.png`, `build_scripts/podcast/out/`, `.env`, `__pycache__/`, `.DS_Store`, `audio/tests/`, `audio/test-*.mp3`, `audio/*.mp3`); `git check-ignore --no-index` matches nothing for `assets/app.js`, `engine.js`, `app.css` or `data/*.json`, and there is no global excludes file. Nothing to change. |
| 33 | cosmetic | fixed | Blitz draws from a shuffled deck: no repeat until every card has been shown, never the same card twice in a row across reshuffles. Repro: 26 cards in a round, 0 back-to-back repeats. |

Why #4 and #19 are "fixed differently" is in their rows. Not changed on purpose: SAT Math choice order. The ordered mode covers the two ACT files named in the report; SAT Math (in band, left alone since pass 1, with letter references in its worked solutions) still has 27 numeric items by this parser that are neither ascending nor descending. They are authoring order, not a shuffle; reordering them is a separate content pass.

## Key-letter distributions (after)

| Bank | A | B | C | D | n |
|---|---|---|---|---|---|
| ACT Math | 42 (25%) | 42 (25%) | 42 (25%) | 42 (25%) | 168 |
| ACT Science | 15 (25%) | 16 (26%) | 15 (25%) | 15 (25%) | 61 |
| ACT English, Reading, SAT Math, SAT RW, podcast checks | unchanged from pass 1 | | | | |

ACT Math: 135 numeric items in ascending order (18 with only one possible key letter, 117 placed by choosing the left-out choice), 32 shuffled, 1 pinned. ACT Science: 15 numeric and 9 "Student N" style items in natural order, 37 shuffled.

## Dark mode contrast per school

Primary as text (`--primary-text`), lower ratio of the two papers in each theme (light #FBF8F1 / #F2EDE0, dark #141A16 / #1C2520). "Raw" is the school primary on dark paper before this fix.

| School | Primary | Raw on dark | Light text | Ratio | Dark text | Ratio |
|---|---|---|---|---|---|---|
| hpa | #C8102E | 2.67 | #C8102E | 5.03 | #db6478 | 4.57 |
| parker | #8F0018 | 1.63 | #8F0018 | 8.24 | #c37683 | 4.67 |
| stjoseph | #CC0022 | 2.69 | #CC0022 | 5.00 | #e06478 | 4.69 |
| waiakea | #022C66 | 1.16 | #022C66 | 11.56 | #768dad | 4.63 |
| cla | #022C66 | 1.16 | #022C66 | 11.56 | #768dad | 4.63 |
| makualani | #5B2C8F | 1.65 | #5B2C8F | 8.16 | #9b7ebb | 4.57 |
| ksh | #0B3D91 | 1.57 | #0B3D91 | 8.59 | #7391c0 | 4.90 |
| whea | #00824B | 3.22 | #007a46 | 4.64 | #389e73 | 4.72 |
| haas | #034CB2 | 2.01 | #034CB2 | 6.70 | #6591d0 | 4.88 |
| volcano | #2F4F3A | 1.72 | #2F4F3A | 7.81 | #809487 | 4.87 |
| kealakehe | #0075b2 | 3.14 | #006ea7 | 4.74 | #3893c3 | 4.59 |
| honokaa | #00824B | 3.22 | #007a46 | 4.64 | #389e73 | 4.72 |
| hilo | #034CB2 | 2.01 | #034CB2 | 6.70 | #6591d0 | 4.88 |
| konawaena | #00824B | 3.22 | #007a46 | 4.64 | #389e73 | 4.72 |
| kohala | #222222 | 1.01 | #222222 | 13.61 | #8f8f8f | 4.86 |
| keaau | #022C66 | 1.16 | #022C66 | 11.56 | #768dad | 4.63 |
| kanu | #C8102E | 2.67 | #C8102E | 5.03 | #db6478 | 4.57 |
| laupahoehoe | #034CB2 | 2.01 | #034CB2 | 6.70 | #6591d0 | 4.88 |
| connections | #2F4F3A | 1.72 | #2F4F3A | 7.81 | #809487 | 4.87 |
| kaumeke | #2F4F3A | 1.72 | #2F4F3A | 7.81 | #809487 | 4.87 |
| kau | #8F0018 | 1.63 | #8F0018 | 8.24 | #c37683 | 4.67 |
| ehunui | #CC0022 | 2.69 | #CC0022 | 5.00 | #e06478 | 4.69 |
| pahoa | #00824B | 3.22 | #007a46 | 4.64 | #389e73 | 4.72 |
| keanalaahana | #2F4F3A | 1.72 | #2F4F3A | 7.81 | #809487 | 4.87 |
| nawahi | #2F4F3A | 1.72 | #2F4F3A | 7.81 | #809487 | 4.87 |
| other | #2F4F3A | 1.72 | #2F4F3A | 7.81 | #809487 | 4.87 |

All 26 schools pass 4.5:1 in both themes. "Primary" is the effective primary after the existing swap/darken rules (Kealakehe's declared #0085CA is darkened to #0075b2 for button text). Status colours on their tints: light ok 4.53, bad 4.94, warn 4.50; dark 6.13, 5.42, 6.19 (lower of both papers, 12% to 15% tint). Full table in `docs/PALETTE_NOTES.md`.

## Files

Changed: `assets/app.js`, `assets/engine.js`, `assets/app.css`, `sw.js`, `versions.json`, `404.html`, `dashboard.html`, `drill.html`, `notes.html`, `onboard.html`, `placement.html`, `quiz.html`, `settings.html`, `strategies.html`, `timed.html`, `timing.html`, `data/act/drills_math.json`, `data/act/drills_science.json`, `data/act/drills_english.json` (one worked solution), `data/onboarding.json`, `data/episodes.json` (topics only), `build_scripts/banks/rebalance.py`, `build_scripts/verify/contrast.py`, `build_scripts/verify/keys.py`, `build_scripts/podcast/publish.py`, `build_scripts/podcast/scripts/{sat,act}-ep1..14.md` (one `topic:` header line each), `docs/BANK_SCHEMA.md`, `docs/PALETTE_NOTES.md` (regenerated).
New: `build_scripts/banks/source/act_drills_math_5choice.json`, this file.
Not touched: dialogue lines in `build_scripts/podcast/scripts/`, `audio/`, `worker/`. Nothing was sent anywhere and nothing was pushed.
