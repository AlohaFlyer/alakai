# Alakaʻi Test Prep: debug pass 1 fixes

Date: 2026-10-18. Fixes for the 48 findings in `docs/debug/pass1.md` (build `618fefd`). Site 1.0.0 to **1.0.1**, service worker `alakai-v13` to **`alakai-v14`**.

Result: **48 of 48 addressed.** 43 fixed as asked, 5 fixed differently (noted below), 0 not fixed. Blocker 1/1, major 12/12, minor 25/25, cosmetic 10/10.

Verification: every repro below was rerun with Python Playwright (Chromium, 390x844) against a local server, with the ping endpoint intercepted (no real pings) and R2 audio served from the local `audio/` copies. `bash build_scripts/verify/all.sh` passes, including `smoke.py`.

## Bugs

| # | Sev | Status | What changed |
|---|---|---|---|
| 1 | blocker | fixed | drill.html records every attempt the moment it is graded (`E.record` no longer waits on the cause question). Misses go to the DB and `errlog` with cause `unsorted`; "Why did you miss it?" patches both if answered (`DB.patch`, `E.setCause`). Repro: 6 misses with Next and no cause gave 6 DB records and 6 errlog entries; summary shows no NaN. |
| 2 | major | fixed | `Progress.summary`: accuracy is right/n over drill, timed and blitz only, same records on both sides. Placement feeds `bySkill` and `bySection` (weak spots, rings, weekly plan) and gets its own report line; redo has its own line; cards never count. Weak spots now need 2 attempts (placement gives 2 per skill). Dashboard labels say "drill and timed". Repro: after placement only, 0 practice / "–" accuracy, weak spots and rings filled, report lists placement and sections; 3/4 drills plus 5 cards plus 1 redo gives 4 answered, 75%. |
| 3 | major | fixed | timed.html `finish` is guarded (`running`/`finishing` flags) and disables Next, Back and Finish on the first call. Repro: double tap "To the end" gave 1 `sat.timed` entry and 27 records. |
| 4 | major | fixed | Chain buttons carry `.chain-next` and are removed at every finish and start; the button disables itself on tap. Repro: one current button after RW M1 and after RW M2. |
| 5 | major | fixed differently | Module state (item ids, answers, flags, current item, time left, chain) saved to `alakai.<test>.timed_inprogress` on every answer, flag, move, every 5 s, `pagehide` and `visibilitychange`. The picker offers Resume or Abandon. The clock pauses while away (resumes with the time that was left). The chain between modules is saved to `alakai.<test>.timed_chain`. Starting a new section while one is saved asks first. Repro: reload and Back both offered Resume; answers, flag and clock (34:59 to 34:58) came back; chain continued; Abandon cleared it. |
| 6 | major | fixed | notes.html saves `pos` every 5 s and on pause, restores it on `loadedmetadata`, shows "Resumes at m:ss". Fixed a race where the load-time `timeupdate` zeroed the saved position. Repro: saved 25.7 s, resumed at 27 s after reload. |
| 7 | major | fixed | `renderCheck` renders once per unlock (keyed by test and episode); `ended` no longer calls it. Repro: on Check 2/3, an `ended` event left it on Check 2/3. |
| 8 | major | fixed | engine.js hint mode: the automatic hint sets `hintUsed`; a right second try is shown as "Got it on the second try" but recorded `correct: false, retry: true, hint: true, cause: 'needed hint'` with the first pick's trap, and goes in the error log. Drill summary counts it as a miss ("+N after the hint"). |
| 9 | major | fixed differently | Finish no longer awaits anything: `pingOnce` only queues `ping_pending`. The next page sends it fire-and-forget with a 3 s `AbortController` timeout, marks `pinged` only on a 2xx, and the dashboard retries once if it failed (2 tries total). Repro: blackholed ping, Finish navigated in 0.13 s; one retry from the dashboard, no third; a 204 marks it sent with exactly one POST. |
| 10 | major | fixed | sw.js precaches `./` and `index.html` both, `404.html`, `favicon.ico`, `site.webmanifest` and every drill and card bank for both tests (53 entries). Pages match with `ignoreSearch` and `/` maps to `index.html`; offline navigation falls back to `index.html`. Audio still never cached; network-first for episodes.json and versions.json kept. Repro offline: `/`, `drill.html?skill=…`, `onboard.html?redo=1`, `onboard.html?next=…`, `notes.html?ep=3`, ACT banks, manifest and favicon all 200 from the service worker; the ACT toggle loads offline. |
| 11 | major | fixed | `#card` is `role="button" tabindex="0"` with Enter and Space to flip and `aria-expanded`; `.ep` rows are `role="button" tabindex="0"` with Enter and Space to play. Focus ring added. |
| 12 | major | fixed | app.js probes localStorage once; if it throws, Store runs from memory. `DB.open` checks `window.indexedDB`, catches a synchronous throw and `onerror`/`onblocked`, and falls back to an in-memory list. One notice ("This browser is blocking storage, so progress cannot be saved") per page. With no storage the gate uses a temporary profile instead of redirecting, so onboarding no longer loops, and no ping is queued. Repro (both "IDB throws" and "IDB undefined", localStorage throwing): dashboard renders fully with one notice and no errors; onboarding lands on placement; drills work. |
| 13 | major | fixed differently | New `build_scripts/banks/rebalance.py` (seeded per file, stable on rerun) shuffles choice order with answer, distractors, traps and "Choice X" text references moved together; keeps NO CHANGE first and trailing None/Neither/Both blocks last. keys.py now fails any section or show with a key position above 35% or below 15%. Distributions below. episodes.json regenerated with publish.py. |
| 14 | minor | fixed | Drills capture the test per run and the toggle ends the set; Study and Blitz capture the test and the toggle ends them (an interrupted Blitz round is not scored); the podcast player saves and closes on toggle; a timed module saves itself (resumable from its own test) and the picker switches. Repro: nothing SAT filed under ACT. |
| 15 | minor | fixed | onboard.html: an option tap schedules one advance; repeat taps do not add another, and Next during that window takes it over instead of adding a step. Repro: double tap stays on Q2; option plus quick Next advances 1. |
| 16 | minor | fixed | `collect(false)` on Back saves what is typed without the alert. |
| 17 | minor | fixed | `Alakai.safeNext` allows only same-origin page names (`name.html` plus an optional query). Repro: `?next=https://example.org/` lands on placement.html. |
| 18 | minor | fixed | Contact labels have `for`; the date and text inputs use `aria-labelledby="q"`. |
| 19 | minor | fixed | A boolean `science` from a saved profile is mapped to `yes`/`no` for the question and kept on Finish. Repro: Next-through keeps `science: true`, and Yes shows pressed. |
| 20 | minor | fixed | Dashboard shows the flagged section only when the current test has it (Both plus English shows on ACT, not SAT). The Both option list is unchanged. |
| 21 | minor | fixed | The gate passes `page + location.search` to `next`, and onboarding returns there. Repro: `onboard.html?next=drill.html%3Fskill%3Drw-ii-central`. |
| 22 | minor | fixed | Grade buttons disable on the first tap (guard flag), and the delayed `nextCard` only runs for the card that was graded. Repro: double tap Yes gives step 1 and the queue drops by 1. |
| 23 | minor | fixed differently | Topics list their card counts, and Blitz is disabled with a note for any topic under 6 cards (not 4), because a 4- or 5-card topic shows nearly the same answer set every card. The topics stay in the list for Study. |
| 24 | minor | fixed | Settings gains Feedback after a miss, Pacing coach and Minutes a day (which sets drill length); the drill and timed copy now names those controls. |
| 25 | minor | fixed | Erase keeps `pinged` and `ping_sent` (erase means "remove my data", not "new device"); the confirm text says so. Repro: erase then onboard again sent no second ping. |
| 26 | minor | fixed | `Store.get` checks the stored value against the fallback's shape (array, plain object, or same primitive type) and returns the fallback otherwise; `getTest` only returns sat or act; `profile()` must be an object; errlog and episode loops skip junk entries. Repro: errlog `{"a":1}`, timed `"x"`, blitz `{}`, episodes `[1]`, test `"xyz"` gave no errors on any page. |
| 27 | minor | fixed | Timed grid buttons 40x40, strike buttons 44 px wide, drill skill links 40 px tall, brand and practice button min-height 44 px, choices min-height 44 px. |
| 28 | minor | fixed | New `404.html` with root-absolute links back to Dashboard, Drills and Home (precached). links.py now resolves root-absolute paths. |
| 29 | minor | fixed | Strike buttons carry `aria-pressed` (drills and placement). |
| 30 | minor | fixed | A past test date shows "Done" with "test date passed: set the next one in Settings", the plan note says so, and the report omits negative days. Day 0 reads "test is today". |
| 31 | minor | fixed | The dashboard nudge computes the same estimate as placement (2 per visible skill x 1.1 min): 48 min for SAT. |
| 32 | minor | fixed | All three are used now: `firstmode` hear puts the podcast first in Next up and read puts the flagged section's strategies first; `device` phone turns on bigger tap targets; `lastscore` shows as the starting score in the Estimated band card. onboarding.json effects notes updated. |
| 33 | minor | fixed | The index picker starts on "Choose your school"; Start without a choice shows a message and stays. The onboarding contact step also has the placeholder and requires a school. |
| 34 | minor | fixed | The 90% rule now counts seconds actually played (`heard`, small forward steps only, persisted), not position. Repro: scrubbing to 95% and playing to the end stays locked; 90% heard unlocks. |
| 35 | minor | fixed | Confirmed on act.org ("The math section now includes four answer choices instead of five", counselorblog.act.org, The Enhanced ACT Explained). `build_scripts/banks/act_math_to_4.py` removed one wrong choice per item (no distractor text first, then no named trap, then the numeric outlier), remapping answer, distractors and traps; all 168 keys verified unchanged. BANK_SCHEMA.md and keys.py now say 4 for every test. data/act/timed.json states no choice count, so it is unchanged. |
| 36 | minor | fixed | 6 original ACT Science cards added (41 total). keys.py now fails any card section under 40. |
| 37 | minor | fixed | A wrong first free-response submit in hint mode shows "Not quite: X is not it…", marks the input (`aria-invalid`, red border) until it changes, then shows the hint. |
| 38 | minor | fixed | "Take a 10-minute break" now runs a 10:00 countdown with "Start … now"; the next module starts at 0:00. |
| 39 | cosmetic | fixed differently | The counter stays honest (10 for SAT, 11 for ACT or Both, since the Science question appears) and the footer count now follows it instead of saying 10. |
| 40 | cosmetic | fixed | Report pluralizes days, active days and questions. |
| 41 | cosmetic | fixed | "Answer: 23. Why:" |
| 42 | cosmetic | fixed | Parentheses only when there is a status note ("Colors: Alakaʻi default"). |
| 43 | cosmetic | fixed | "The frame is solid by default. Seven optional patterns…". The "Reviewed for cultural appropriateness: pending" line is now an HTML comment, not public text. |
| 44 | cosmetic | fixed | Disabled choices keep full opacity when they carry the right or wrong state; only the other choices dim to .6. |
| 45 | cosmetic | fixed | `tick()` runs once at start, so the clock shows the full time immediately. |
| 46 | cosmetic | fixed | Pages without a tab highlight their parent: placement marks Dashboard (`aria-current="true"`). |
| 47 | cosmetic | fixed | The picked choice gets a 2 px inset ring, a tinted background, a "✓ Selected" line and `aria-pressed`. |
| 48 | cosmetic | fixed | The weekly plan reads the module lengths from timed.json: "32 to 35 min" for SAT, "35 to 50 min" for ACT (Science only when on). |

Why 5, 9 and 13 are marked "fixed differently" (23 and 39 explain themselves in the table):

- **5**: the clock pauses while the student is away rather than running on, so an accidental refresh costs no time. A `beforeunload` prompt was not added because the module is saved.
- **9**: the ping goes out from the page after onboarding, not from onboarding itself, so navigation never waits and success can be recorded before the page that sent it unloads.
- **13 (SAT and ACT English/Reading)**: rebalance.py leaves a file alone when it is already inside the 15% to 35% band (`--force` reshuffles anyway). SAT RW, SAT Math, ACT English and ACT Reading were already in band and have many "Choice X" and bare-letter references in their worked solutions, so they were not reshuffled.

## Key-letter distributions

| Bank | Before | After |
|---|---|---|
| ACT Math (5 choices, before conversion) | A 14, B 63, C 62, D 25, E 4 (168) | 4 choices: A 42, B 42, C 42, D 42 |
| ACT Math right after 5 to 4 | A 20, B 80, C 60, D 8 | (rebalanced above) |
| ACT Science | A 10, B 31, C 19, D 1 (61) | A 16, B 15, C 15, D 15 |
| ACT English | A 34, B 32, C 28, D 26 (120) | unchanged, in band |
| ACT Reading | A 21, B 20, C 16, D 23 (80) | unchanged, in band |
| SAT Math (choice items) | A 45, B 45, C 45, D 44 (179) | unchanged, in band |
| SAT RW | A 50, B 51, C 50, D 50 (201) | unchanged, in band |
| SAT podcast checks, Ep 1 to 14 | A 5, B 24, C 12, D 1 (42) | A 11, B 9, C 11, D 11 |
| ACT podcast checks, Ep 1 to 14 | A 7, B 27, C 7, D 1 (42) | A 11, B 11, C 11, D 9 |

Ep 0 checks (development only) were balanced with their show and are not published. publish.py now refreshes `check` from `checks/*.json` for published entries whose mp3 is only on R2; every other episodes.json field is byte-identical.

Trade-off to know: ACT Math choices were in ascending numeric order and are now shuffled, as are numbered choices like "Student 1/2/3" in ACT Science. The real ACT orders numeric choices; keeping that order would have kept the key bias.

## Files

Changed: `assets/app.js`, `assets/engine.js`, `assets/app.css`, `drill.html`, `timed.html`, `notes.html`, `quiz.html`, `onboard.html`, `dashboard.html`, `placement.html`, `settings.html`, `index.html`, `sw.js`, `versions.json`, `data/act/drills_math.json`, `data/act/drills_science.json`, `data/act/cards_science.json`, `data/onboarding.json`, `data/episodes.json`, `build_scripts/podcast/checks/*.json`, `build_scripts/podcast/publish.py`, `build_scripts/verify/keys.py`, `build_scripts/verify/links.py`, `docs/BANK_SCHEMA.md`.
New: `404.html`, `build_scripts/banks/rebalance.py`, `build_scripts/banks/act_math_to_4.py`, this file.
Not touched: `build_scripts/podcast/scripts/`, `audio/`, `worker/`.
