# Alakaʻi Test Prep: debug summary (passes 1 to 3)

Date: 2026-10-18. Final build tested: `1e68393`, site 1.0.2, service worker `alakai-v15`, live at alakaitestprep.app and identical to the repo.

## Bottom line

No blockers left and all 81 earlier findings still fixed. Pass 3 found 21 new issues: 1 major, 11 minor, 9 cosmetic, none fixed yet. The major one: timed ACT Reading and Science jump to a new passage almost every question. Fine for students now if ACT timed Reading and Science get fixed (or labeled "practice set, not test format") before you push the ACT side hard.

## The three passes

| Pass | Build | Found | Blocker / major / minor / cosmetic | Fixed |
|---|---|---|---|---|
| 1 | `de9f743` (1.0.0) | 48 | 1 / 12 / 25 / 10 | 48 of 48 (`8b8d1d9`, 1.0.1) |
| 2 | `8b8d1d9` (1.0.1) | 33 | 1 / 5 / 18 / 9 | 32 of 33, 1 not reproducible (`1e68393`, 1.0.2) |
| 3 | `1e68393` (1.0.2) | 21 | 0 / 1 / 11 / 9 | 0 so far (report only) |

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
