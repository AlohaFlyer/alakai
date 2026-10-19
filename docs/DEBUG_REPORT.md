# Alakaʻi Test Prep: debug summary (passes 1 to 3)

Date: 2026-10-18. Final build tested: `1e68393`, site 1.0.2, service worker `alakai-v15`, live at alakaitestprep.app and identical to the repo.

## Bottom line

No blockers left and all 81 earlier findings still fixed. Pass 3 found 21 new issues: 1 major, 11 minor, 9 cosmetic, none fixed yet. The major one: timed ACT Reading and Science jump to a new passage almost every question. Fine for students now if ACT timed Reading and Science get fixed (or labeled "practice set, not test format") before you push the ACT side hard.

## The three passes

| Pass | Build | Found | Blocker / major / minor / cosmetic | Fixed |
|---|---|---|---|---|
| 1 | `de9f743` (1.0.0) | 48 | 1 / 12 / 25 / 10 | 48 of 48 (`8b8d1d9`, 1.0.1) |
| 2 | `8b8d1d9` (1.0.1) | 33 | 1 / 5 / 18 / 9 | 32 of 33, 1 not reproducible (`1e68393`, 1.0.2) |
| 3 | `1e68393` (1.0.2) | 21 | 0 / 1 / 11 / 9 | 21 of 21 (1.0.3, sw `alakai-v16`; see Round 3 fixes) |

Regression: pass 2 rechecked all 48 pass-1 fixes (48 pass). Pass 3 rechecked all 81 (81 pass).

## The worst bugs and what changed

- **Drill misses were lost** (pass 1 blocker) if a student tapped Next without answering "Why did you miss it?". Every answer is now saved the moment it is graded.
- **Dark mode hid flashcard answers and links** (pass 2 blocker): school colours used as text on dark paper fell as low as 1.01:1. A per-theme text colour now clears 4.5:1 for all 26 schools, and contrast.py tests both themes.
- **Accuracy and the parent report were wrong**, placement did not seed weak spots, and a double tap could finish a timed module twice and skip a module (pass 1). Fixed.
- **A refresh threw away a timed module**, and podcasts had no resume (pass 1). Both now resume.
- **The service worker could not work offline for `/` or deep links, and a version bump could precache stale files** (passes 1 and 2). Banks are precached, pages match without the query string, and installs skip the HTTP cache.
- **Days to test was one short every afternoon in Hawaiʻi** (pass 2): the date was read as UTC. Now local.
- **The "sent once" ping could go twice**, and onboarding could hang on a dead ping (passes 1 and 2). It now goes once, fire and forget.
- **Answer keys were biased** (ACT Math B or C 74% of the time) and ACT Math had 5 choices; then the fix scrambled numeric order (passes 1 and 2). Now 4 choices, balanced keys, ascending numeric choices.
- **iPhone students could not type negative grid-in answers** (pass 2). The box now has − and / keys.

## Still open (pass 3, details in docs/debug/pass3.md)

Worth fixing before a wide launch:
1. **ACT timed Reading and Science scatter passages** (major): 36 Reading questions came from 17 passages with 35 switches. The Time squeeze pacing advice can't be practiced. Fix: draw whole passages and keep their items together (timed.html:132-143).
2. **The weekly plan suggests a full-length test 1 to 3 days before the test**, against the app's own "night before: pau" advice (dashboard.html:220).
3. **Screen readers don't hear right/wrong feedback, and flashcards read only "Flashcard. Press Enter…"**, not the question (app.js showFeedback, quiz.html:50).
4. **The podcast check may not unlock if the student listens with the phone locked** (not verified on a device; check on an iPhone).
5. **Some ACT choices with units, times and ranges are still out of order**, and keys.py misses them (4 items, plus 5 coordinate-pair items).

The rest are smaller: offline nested URLs show a broken page, links to the other test's drills say "No items", corrupt storage can still halt the dashboard part way, the milestone banner outlives a test toggle, some tap targets are 40 px, Redo onboarding starts blank, plus 9 cosmetic items.

Content: a hand read of 90 random drills and 30 cards found no wrong keys and no explanation that contradicts its key.

## How to rerun the checks

- Static suite (every push): `bash build_scripts/verify/all.sh` from the repo root (contrast for 26 schools x 2 themes, keys and balance, links, JSON, node syntax, podcast dry runs, smoke test). It does not catch #6 above until `numeric_value` in rebalance.py is extended.
- Browser runs: serve a copy with `python3 -m http.server 8765 --bind 127.0.0.1` and drive it with Python Playwright (Chromium) at 390x844 (iPhone UA), 820x1180 (iPad UA), 1280x800 and 320x640, light and dark, `timezone_id="Pacific/Honolulu"`. Always route `https://ping.alakaitestprep.app/**` to a stub so no real pings are sent. Use a browser user agent for audio.alakaitestprep.app (it returns 403 otherwise).
- Service worker: index.html registers the SW only on https, so for local tests register it by hand on a scratch copy served with `Cache-Control: max-age=600` (GitHub Pages' header), then stop the server for a true offline run. Playwright's `set_offline` does not cut service-worker traffic.
- The pass-3 Playwright scripts lived in the session scratchpad and are not in the repo. If you want them kept, they should go in `build_scripts/verify/e2e/`.

## Round 3 fixes

Site **1.0.3**, service worker **`alakai-v16`**. All 21 pass-3 findings addressed: major 1/1, minor 11/11, cosmetic 9/9 (one part of #1 fixed differently). Details per bug: `docs/debug/pass3-fixes.md`.

- **ACT timed Reading and Science are built from whole passages.** Reading: 4 blocks in ACT order (Literary narrative, Social science, Humanities, Natural science), 9 questions and 10 minutes each; the bank's passages hold 5 questions, so each block is one passage plus 4 questions of a second passage of the same type. Science: 10 whole 4-question passages in bank order (4 data, 4 research, 2 conflicting viewpoints), 4 minutes each, 40 questions; the brief's 6 to 7 passages would be only 24 to 28 questions with this bank. Each passage shows once in a panel that stays put while the student works its questions; checkpoints match the Time squeeze page (Reading passage 2 at 20:00, Science passage 5 at 20:00, timing.html updated). SAT modules are unchanged (one short passage per item).
- **Test week follows Ep 13**: full-length test about 14 days out and no later than 3 days out, light review 2 days out, rest the day before, nothing on test day.
- **Accessibility**: polite live region on all feedback, focus moves to the verdict, flashcards are named by their question, 44 px targets for everyone.
- **Podcast listening counts from the audio clock**, so a locked phone or background tab still counts toward the 90% check (seeks still do not). Verified in Chromium by detaching the page's handler mid-play; still worth one check on an iPhone.
- **ACT natural order now covers units (m^2), clock times, ranges and coordinate pairs**, and keys.py enforces it. Keys and explanations unchanged.
- Offline unknown URLs get the styled 404 page; links to the other test's drills switch the toggle; corrupt storage no longer stops the dashboard; the milestone banner follows the toggle; Redo onboarding and a mid-onboarding refresh keep answers; plus the cosmetic fixes (local export date, unsaved hint, ʻokina, 2.77, score bands, offline player line, volume card).
- **The Playwright journeys are now in the repo**: `build_scripts/verify/e2e/run.py`, run by `all.sh` (11 journeys; all fail on the pass-3 build, all pass now). This replaces the last bullet under "How to rerun the checks": the scripts are no longer scratchpad-only.

Still worth doing: write longer ACT Reading and Science passages (9 and 6 to 7 questions) so the timed modules can use the real passage counts, and add 9-question paired Reading sets; check #5 on an iPhone with the screen locked.
