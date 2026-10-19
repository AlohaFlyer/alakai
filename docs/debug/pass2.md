# Alakaʻi Test Prep: debug pass 2

Date: 2026-10-18. Build tested: master `8b8d1d9` (site 1.0.1, sw `alakai-v14`). Live site checked identical to local (md5 of sw.js, app.js, engine.js, app.css, drill/timed/notes/dashboard/404.html, episodes.json, act/drills_math.json, versions.json).
Method: full code read of every page, app.js, engine.js, sw.js, the data files and both build scripts, formed before reading pass1.md and pass1-fixes.md. Then Python Playwright (Chromium) at 390x844 iPhone UA, 820x1180 iPad UA, 1280x800 desktop and 320x640, light and dark, against a local copy (127.0.0.1:8765) and, for end-to-end and the service worker, the live site plus a scratch copy served with GitHub Pages' `Cache-Control: max-age=600` (the only way to take the network down for the SW). The ping Worker was intercepted in every run; no real pings were sent. Audio was routed to the local `audio/` copies for the podcast runs; R2 was checked with HEAD only. No repo file was edited except this report.

Counts: **1 blocker, 5 major, 18 minor, 9 cosmetic (33 new).** Regression: **48 of 48 pass1 fixes pass** (three of them with new follow-on bugs, cross-referenced below).

Line numbers are for `8b8d1d9`.

## Bugs

### Blocker

1. **[blocker] Dark mode: the school primary colour is used as a text colour on a dark background, so flashcard answers vanish and links, focus rings and the SAT/ACT toggle are near invisible.**
   Page: quiz.html (Study), and every page with links (drill picker, strategies, dashboard weak spots, error log), the focus ring everywhere, notes episode numbers, toggle and nav highlight.
   Repro: Settings, school Kohala, Appearance Dark (or a phone in dark mode), Save. Quizzers, Study, flip a card.
   Happened: the answer ("s = r * theta") renders `#222222` on `#1C2520`, contrast 1.01:1; it is invisible (screenshot taken). Waiākea, CLA, Keaʻau links are `#022C66` on `#141A16`, 1.31:1. Computed for all 26 schools: primary-as-text on dark paper ranges 1.11:1 (Kohala) to 3.61:1 (green schools); **none reaches 4.5:1**. The focus outline (3 px primary) and the pressed toggle / current nav tab (primary fill on dark paper) are equally faint, so keyboard users lose their place. `--ok`, `--bad` are not redefined for dark: `.feedback.wrong` and `.clock.low` are 2.97:1.
   Expected: in dark mode, text and outlines that use the school colour switch to a lightened tint (or `--ink`) that meets 4.5:1; status colours get dark-mode values. contrast.py should also test primary against dark paper.
   Cause: app.css:51 `a { color: var(--primary) }`, quiz.html:25 `.flash .back { color: var(--primary) }`, app.css:182, app.css:198 (focus outline), notes.html `.ep .n`, timing.html `.num`; app.css:26-29 dark block redefines only ink/paper/line. app.js:117-133 `applyPalette` only checks primary against light paper `#FBF8F1`.

### Major

2. **[major] Service worker: a version bump can precache the old files, leaving students on stale (or mixed) code until the next bump.**
   Page: sw.js (all pages). Repro (scratch copy served with `Cache-Control: max-age=600`, as GitHub Pages does): load the site so `alakai-v14` installs, then within 10 minutes change sw.js to `alakai-v15` and app.js `VERSION` to `9.9.9`, reload twice.
   Happened: the cache list is `["alakai-v15"]` (v14 deleted) but `Alakai.VERSION` is still `1.0.1`: the v15 install fetched app.js from the browser's HTTP cache. Because pages and assets are cache-first, the student keeps the old file under the new cache name until the version after next. If only some files are still fresh in the HTTP cache, new HTML can be paired with old JS.
   Expected: install always fetches from the network.
   Cause: sw.js:11 `c.addAll(SHELL)` uses default cache mode. Use `c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))`.

3. **[major] Days to test is off by one every afternoon in Hawaiʻi; the day before the test says "test is today".**
   Page: dashboard.html, report email, weekly plan. Repro: test date 2026-11-07, browser time zone Pacific/Honolulu, clock 2026-11-06 15:00.
   Happened: "0 / test is today". At 09:00 the same day it says "1". From 2 pm HST every day the count is one short; the full-length plan items (14 and 3 days out) shift with it. America/Los_Angeles shows the same flip from 4 pm.
   Expected: count calendar days in local time.
   Cause: dashboard.html:131 and app.js:299 `new Date(profile.testdate)` parses `YYYY-MM-DD` as UTC midnight (2 pm the day before in HST). Use `new Date(y, m - 1, d)` and compare local midnights.

4. **[major] The "sent once" ping is sent twice if the student leaves the placement page before the Worker answers.**
   Page: placement.html then any page. Repro: Worker answering in 1.5 s (rural connection); finish onboarding, tap "Skip for now" on placement within 0.3 s.
   Happened: the Worker received two POSTs `{"school":"kohala","grade":"11"}`. The first is a `keepalive` request that completes after unload, but its `.then` never runs, so `pinged` is not stored; the dashboard then retries. Counts are inflated and the disclosure "It is sent once" is false.
   Expected: one POST per device.
   Cause: app.js:244-256: success is recorded only in the page's `.then`; `tries === 1` on dashboard re-sends. Options: mark `pinged` optimistically when the request is dispatched (accept a rare miss), or have the Worker dedupe on a random one-time token stored before sending.

5. **[major] ACT Math and Science numeric choices are now in random order, which breaks the backsolve strategy the app teaches.**
   Page: drill/timed/placement, data/act/drills_math.json, drills_science.json. Repro: open `drill.html?item=act-math-functions-007` (choices 48, 133, 64, 69) or `act-math-geometry-019` (3, 11, 6, 7).
   Happened: 86 of 96 all-numeric ACT Math items and 7 of 8 ACT Science items are not in ascending or descending order (SAT Math: 73 of 83 still ordered). Strategies "Work backward from choices" and ACT Ep 7 (check question "where do you start? A middle choice, so you know which way to move") rely on ordered choices; the real ACT orders them. pass1-fixes.md notes the trade-off, but keeping order and balancing keys are compatible: rebalance by choosing which ordered slot holds the key per item (regenerate one distractor above or below the key where needed), or exempt numeric items and accept a looser band for them.
   Cause: build_scripts/banks/rebalance.py shuffles numeric choice lists like any other.

6. **[major] On iPhone, negative grid-in answers cannot be typed.**
   Page: drill, timed, placement (SAT Math free response). Repro: iPhone, `drill.html?item=sat-math-adv-nonlinear-016` (key `-3`) or `sat-math-psda-inference-012` (key `-7`).
   Happened: the field uses `inputmode="decimal"`; the iOS decimal keypad has digits and a decimal point only, no minus and no slash. Those two items are unanswerable on iPhone, and fraction keys (7/2, 36/13, 75/16, 1/3) can only be entered as decimals. The real SAT accepts negatives and fractions.
   Expected: `inputmode="text"` (or `type="text"` with `pattern`), or a small "−" and "/" button row.
   Cause: engine.js:55, timed.html:177, placement.html:74.

### Minor

7. **[minor] Blitz: after a card times out, its choices stay live; tapping one scores and doubles the card loop.** Repro: Blitz, let a card's 8 s bar run out, then tap the right answer within 0.9 s. Happened: score 0 to 10, streak 1, the right answer was never revealed, and two `blitzCard` calls ran (the front changed twice in 1 s). Cause: quiz.html:156 calls `miss(true)` without disabling buttons or marking the key; :164 schedules `blitzCard` while the click handler (:157-163) schedules another.
8. **[minor] Podcast check: a double tap on Next skips a question or starts another episode.** Repro: unlock a check, answer Check 2, double-tap Next. Happened: the second tap landed on the episode list below (the check shrank), which called `play()` for Ep 2; Ep 3's check restarts from 1 next time. With a taller layout it skips Check 3 instead. Cause: notes.html:130 `nb.onclick = () => { i++; next(); }` has no guard.
9. **[minor] Dashboard: toggling SAT, ACT, SAT quickly leaves ACT data under the SAT toggle.** Repro: dashboard on SAT, ACT banks slow (first load on a slow link; simulated 0.8 s), tap ACT then SAT. Happened: toggle and subtitle say SAT, plan is SAT, but the section rings read English, Math, Reading, Science and the skill-level table is ACT's. Cause: dashboard.html:128-218 `render()` awaits several loads and writes the DOM in pieces; an older render finishing last wins. Fix: a render token, and ignore stale renders.
10. **[minor] ACT full-length test without Science puts the break before Math instead of after it.** Repro: ACT profile, Science off, Timed, Full-length test, finish English. Happened: "Take a 10-minute break, then start Math"; after Math, "Continue to Reading". The ACT break is between Math and Reading. Cause: timed.html:213 `chain.length === 1` assumes four modules; use `nextMod.section === 'reading'`.
11. **[minor] Placement ignores the SAT/ACT toggle.** Repro: start the SAT placement, tap ACT. Happened: the header and nav say ACT while SAT items continue and are filed under SAT; the time estimate stays SAT's. Cause: placement.html:59 fixes `test` and there is no `alakai:test` listener (every other page has one).
12. **[minor] Offline podcast page says the show is "being recorded" when episodes.json was never cached.** Repro: first visit loads the dashboard only, go offline, open `notes.html` or `notes.html?ep=3`. Happened: "SAT Notes Podcast, episode 1 is being recorded… Check back soon." and the deep link does nothing. Expected: precache episodes.json (it is small) or say "You're offline; episodes need a connection." Cause: sw.js:4-8 (not in SHELL), notes.html:68 swallows the error and :75 shows the empty-show text.
13. **[minor] Junk entries inside stored arrays still crash pages.** Repro: `alakai.sat.errlog = [null]` then `drill.html?mode=redo` or tick "Only ones I've missed" (`null.done`, drill.html:94, :102); `sat.timed = [null]` (dashboard "reading 'name'", :166); `sat.blitz = [null]` (dashboard :169, quiz :92); `sentlog = [null]` (settings :218); `sat.timed_inprogress.answers = "x"` (timed :106, picker stops rendering resume). Pass 1 #26 fixed the top-level shape only.
14. **[minor] Touch targets under 40 px remain.** Nav tabs are 36 px tall on every page (app.css:98, `padding: 6px 10px`); error-log "redo" links 33x19 (dashboard.html:175); strategies "Drill it" 37x27 (strategies.html:66); inline footer/"Details"/"About this pattern" links 16-20 px.
15. **[minor] Time squeeze scrolls sideways at 320 px.** The budget table is 342 px wide (timing.html:50 and :56), so the page scrolls horizontally. Wrap the table in an `overflow-x:auto` box or shorten headers.
16. **[minor] Onboarding: Next on an unanswered single-choice question does nothing, with no message.** Repro: Q3, tap Next without choosing. Cause: onboard.html `collect()` returns false silently. Show "Pick one to continue".
17. **[minor] Onboarding asks the scariest section before the Science question, so ACT students can flag Science and then switch it off.** The section list is built before `science` is answered (onboard.html:79-80; data/onboarding.json:13 orders science last). Move the Science question before `fear`.
18. **[minor] ACT Ep 11 homework "Drill Science" alerts "No items for that yet." when Science is off.** Same for any `drill.html?section=science` link. Hide the homework button or offer to turn Science on (notes.html homework render; drill.html:101 excludes science).
19. **[minor] Saving Settings before onboarding creates a profile that skips onboarding and placement.** Repro (confirmed in code): new visitor opens Settings, types a name, Save. `profile` is stored without `onboarded`, so `requireOnboarding` (app.js:226-231) lets every gated page through, while index still shows the first-visit card. Cause: settings.html:202 `if (np.name || p.onboarded)`.
20. **[minor] Content: a worked solution contradicts itself.** `act-english-grammar-006`: "Choice C shifts person; D shifts number and tense. Answer: choice D." D ("they arrive") is the key; B ("one arrived") is the one that shifts number and tense. Authoring error present since v0.1.0. The other 450 "Choice X" references in explain/worked/hint were checked against the keys and are consistent.
21. **[minor] Light mode: trap chips and status text fall below AA.** `.chip.warn` (`#B07A12` on its 15% tint) is about 3.3:1; `.chip.ok` about 4.3:1 (app.css:129-131). These carry the trap names in drills and the skill levels.
22. **[minor] "Free official practice" menu: Escape does not close it and focus is not moved into it.** app.js:347-353 (only an outside click closes).
23. **[minor] Error log shows at most 12 rows with no "and N more".** With 27 open misses only 12 appear (dashboard.html:171); the rest are reachable only through "Redo … due".
24. **[minor] All 28 episodes have an empty `topic`.** The list shows a blank second line under every title and the player's topic line is empty ("  Resumes at 0:07."). data/episodes.json; notes.html:75 and :115.

### Cosmetic

25. **[cosmetic]** Error log and trap summary show the bare word "Trap" for trap id `other` (engine.js:5 `other: 'Trap'`, stripped of "Trap: " in dashboard.html:174-175).
26. **[cosmetic]** "More episodes are being recorded. New ones show up here as they are approved." still shows although both 14-episode seasons are complete (notes.html:80).
27. **[cosmetic]** On iPad the icon prompt says "Want the icon on your phone…" (app.js:172).
28. **[cosmetic]** Onboarding contact step: changing the School select does not update the `{"school":"…"}` disclosure line or preview the colours (onboard.html contact render).
29. **[cosmetic]** Strike (×) buttons stay active after an item is answered (engine.js:72 disables only `.choice`).
30. **[cosmetic]** 404.html has no frame bar or palette: a blank 42 px band at the top and always HPA red.
31. **[cosmetic]** Timed milestone key uses `list.length`, which sticks at 51 once 50 modules are stored, so timed-section prompts stop after the 50th (timed.html:207).
32. **[cosmetic]** `.gitignore` lists tracked core files (`assets/app.js`, `engine.js`, `app.css`, `data/*.json`); harmless while tracked, but a fresh clone that deletes and re-adds them would silently drop them.
33. **[cosmetic]** Blitz draws cards with replacement, so the same card can come up twice in a row (quiz.html:150).

## Regression: pass 1 findings

Each was rerun by its pass 1 repro (P = Playwright run, C = code/data check).

| # | Pass 1 finding | Result | How checked / note |
|---|---|---|---|
| 1 | Miss lost on Next without cause | pass | P: 5 misses, Next, no cause: 5 DB records and errlog entries, cause `unsorted` |
| 2 | Accuracy and report wrong, placement not seeding | pass | P: placement only gives 0 answered, "–", weak spots and rings filled, report "Placement check: 5/10"; after drills 10 answered 50% on both dashboard and report |
| 3 | Double tap "To the end" finishes twice | pass | P: 1 `sat.timed` entry, 27 records |
| 4 | Chain buttons pile up | pass | P: one button after RW M1 and after RW M2 |
| 5 | Refresh mid-module loses it | pass | P: reload offered Resume; answers, flag, item and clock (31:57 to 31:56, paused) restored |
| 6 | Podcast position not saved | pass | P: paused at 6.9 s, reload, "Resumes at 0:07", resumed at 8.4 s |
| 7 | Check resets on ended | pass | P: on Check 2/3 when `ended` fired, stayed on 2/3 (see new #8 for double tap) |
| 8 | Hint retry counted as correct | pass | P: recorded `correct:false, retry:true, hint:true, cause:'needed hint'`, errlog entry, summary "(10 more after the hint)" |
| 9 | Finish hangs on dead ping | pass | P: blackholed ping, Finish navigated at once; 2 tries total. See new #4 (double send) |
| 10 | Offline gaps | pass | P (scratch copy, server killed): `/`, `drill.html?skill=`, `onboard.html?redo=1`, `?next=`, all pages, ACT toggle (drills, cards, dashboard) work offline; 53 entries in `alakai-v14`. See new #2, #12 |
| 11 | Keyboard: cards, episodes | pass | P: Space flips (`aria-expanded` true), Enter on focused `.ep` plays; role=button, tabindex 0 |
| 12 | Blocked storage crash/loop | pass | P: localStorage throwing + no indexedDB: every page renders, one notice each, onboarding reaches placement, drills work, no ping; IDB `open` throwing: dashboard renders with notice |
| 13 | Key-position bias | pass | C: keys.py passes; distributions in band. See new #5 (numeric order) |
| 14 | Toggle mid-drill files under wrong test | pass | P: toggle ends the set, DB has only `sat:` record |
| 15 | Onboarding double tap skips | pass | P: double tap stays on Q2; option plus Next advances 1 |
| 16 | Back from contact alerts | pass | P: no dialog |
| 17 | Open redirect | pass | P: `?next=https://example.org/` lands on placement.html |
| 18 | Contact labels | pass | P: all six `label[for]`; `#in` has `aria-labelledby="q"` |
| 19 | Science turned off on re-run | pass | P: "Yes" shown pressed, `science:true` kept |
| 20 | Both + English on SAT | pass | P: SAT Next up omits it, ACT shows it |
| 21 | Deep link query lost at gate | pass | P: `onboard.html?next=drill.html%3Fskill%3Drw-ii-central` |
| 22 | Study double tap | pass | P: step 1, queue 117 to 116 |
| 23 | Blitz topics under minimum | pass | P: Polygons (1) disables Blitz with note; counts listed |
| 24 | Settings lacks options | pass | P: missmode, timepressure, minutes saved; setSize 14 used by drills |
| 25 | Erase re-pings | pass | P: after erase only `pinged`, `ping_sent` (and re-set `test`) remain |
| 26 | Bad stored values crash | pass | P: pass 1 values (errlog object, timed string, blitz object, episodes array, test "xyz") no errors. See new #13 (null inside arrays) |
| 27 | Touch targets | pass | P: timed grid 40x40, strike 44 (52 on phone profile), choices 44+, brand 44, practice 48, skill links 41. See new #14 (nav tabs, redo links) |
| 28 | No 404 | pass | live: unknown URL returns custom 404 page |
| 29 | Strike has no state | pass | P: `aria-pressed="true"` after tap |
| 30 | Negative days | pass | P: "Done" / "test date passed…", report omits days. See new #3 (time zone) |
| 31 | Placement estimate mismatch | pass | P: 48 min on both (SAT); 40 ACT without Science |
| 32 | Unused onboarding answers | pass | P: firstmode hear puts podcast first; device phone sets `data-device`; lastscore shown |
| 33 | HPA preselected | pass | P: placeholder selected; Start shows "Choose your school first" |
| 34 | 90% by scrubbing | pass | P: scrub to 95% and play to end stays locked; real play unlocks at 90% |
| 35 | ACT Math 5 choices | pass | C: 168 items, all 4 choices, keys in range |
| 36 | ACT Science 35 cards | pass | C: 41 cards |
| 37 | Free response hint no signal | pass | P: "Not quite: 99999 is not it…", `aria-invalid`, hint shown |
| 38 | Break has no break | pass | P: 9:59 countdown with "Start … now" |
| 39 | Counter vs "10 quick questions" | pass | P: footer follows 10/11 |
| 40 | "1 active days" | pass | P: "1 active day" |
| 41 | "Why :" | pass | P: "Answer: -3. Why: …" |
| 42 | Empty parentheses for Other | pass | P: "Colors: Alakaʻi default" |
| 43 | Pattern disclosure text | pass | C: "solid by default. Seven optional patterns"; review note is an HTML comment |
| 44 | Dimmed reveal | pass | C: app.css keeps full opacity on stated choices |
| 45 | Clock 0:00 at start | pass | P: "32:00" immediately |
| 46 | Placement nav highlight | pass | P: Dashboard `aria-current="true"` |
| 47 | Picked choice hard to see | pass | P: `aria-pressed`, ring, tint, "✓ Selected" |
| 48 | Plan always 35 min | pass | P: "32 to 35 min" SAT, "35 to 50 min" ACT |

## Checked and passed

- Console: no errors or warnings on any of the 13 pages (incl. `/` and 404) at phone, iPad, desktop and 320 px, light and dark, first visit and returning. Only aborted requests from the onboarding redirect.
- Layout: no horizontal scroll at 320, 390, 820, 1280 on any page except timing.html (#15); a 50-character Hawaiian name wraps cleanly on the returning card and dashboard at 320 px.
- Links and assets (live, iPhone UA): all 53 precache entries, 26 manifests and their 78 icons, 78 per-school favicon/mark/apple-touch icons: 200. All 28 mp3s on audio.alakaitestprep.app: 200 `audio/mpeg`. 404.html served for unknown paths. Manifests valid JSON, `scope`/`start_url`/icons resolve. `verify/all.sh` passes and left the tree clean.
- Data integrity (own script): 441 SAT + 429 ACT drills, no duplicate ids, every skill exists and matches its section, 4 choices on every choice item, answer in range, no duplicate choices, explain/hint/worked present, distractors and traps aligned with choices, trap on the key always null, all trap ids known, 16+ per skill (min 20). 61 SAT grid-ins with string answers. Cards: no topic duplicates of backs, backs under 25 words, Blitz-ineligible topics are disabled. Timed pools cover every module and difficulty band. Episodes: 3 checks each, 4 choices, answers in range, every homework skill/section exists. strategies.json covers every skill id with no extras.
- ACT Math sanity read, 20 random reshuffled items (seeded): every kept set has the key plus three plausible wrongs with matching distractor notes; worked solutions do not cite letters (numeric), so the reshuffle did not break them. Letter references across all banks (451 found): all consistent with the key except #20.
- Onboarding SAT, ACT, Both (incl. Science unsure → on), name/email/parent, the ping queued on Finish and sent exactly once on the next page when the Worker answers promptly (`{"school":"kohala","grade":"11"}`), "What gets stored" anchor, ping status line.
- Placement: 2 per skill, by-section table, "Start here" links, errlog seeded with traps, nudge hidden afterwards.
- Dashboard: streak, rings, weak spots, skill levels (Attempted/New ordering), Next up, weekly plan budget, official links, error log with unsorted ("missed <date>") and "needed the hint"/trap causes, due chips, trap summary, milestone banner (100 drills) and Later, Send progress report (sentlog entry; mailto `mailto:kai%40example.com?cc=mom%40example.com&subject=…&body=…`, 1.3 kB), report numbers match the dashboard.
- Drills: skill, section, mixed, redo due (marks done), `?item=`, Approach box, trap chip, crossed-out note, feedback modes (answer, hint, worked), double tap on Next does not skip (6 of 6, drillcount 6).
- Timed: SAT adaptive M2 ("harder" after 67% M1), standalone M2 unrouted, pace text, flags, resume, abandon, toggle saves module and full-length chain (resume banner after toggling during the break), results and band ("Math: 720 to 800" with disclaimer).
- Quizzers: due count, topic counts, Study flip/grade/schedule, Blitz clock, streak lines, round summary and score saved.
- Podcasts: both lists under each toggle, R2 URLs, transcript, homework link, position resume, 90% rule, check not reset on ended, dashboard count.
- Settings: school change re-themes primary, favicon, mark, apple-touch-icon, manifest and theme-color and persists; icon prompt on iPhone and iPad UA, not desktop; patterns; theme; export (file name, keys, version); erase; redo onboarding; disclosures.
- Toggle and nav highlight correct on all 8 nav pages plus placement (parent highlight); strategies and timing swap content with the toggle; practice menu lists the current test first and closes on outside click.
- Service worker: offline after first load for every page, deep links and the bare domain (scratch copy with the server stopped); old cache deleted on bump (but see #2).
