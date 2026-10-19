# Alakaʻi Test Prep: debug pass 3 (final gate)

Date: 2026-10-18 (HST). Build tested: master `1e68393` (site 1.0.2, sw `alakai-v15`). Live site checked identical to local (sha1 of index.html, app.js, engine.js, sw.js, dashboard.html, act/drills_math.json; versions.json 1.0.2).
Method: full read of README.md, docs/BANK_SCHEMA.md, assets/app.js, engine.js, app.css, sw.js and every page, then an independent pass before reading pass1/pass2 and their fix notes. Python Playwright (Chromium 1.56) at 390x844 iPhone UA, 820x1180 iPad UA, 1280x800 desktop and 320x640, light and dark, time zone Pacific/Honolulu, against a local copy (127.0.0.1:8765), a scratch copy served with `Cache-Control: max-age=600` (SW update and a true offline run with the server stopped), and the live site (SW precache, offline deep links, 404, manifests, audio). The ping Worker was intercepted in every run: no real pings were sent. Nothing was posted, sent or bought. No repo file was edited except this report and docs/DEBUG_REPORT.md.
Tutor read: 15 seeded-random drill items per section (SAT RW, SAT Math, ACT English, Math, Reading, Science: 90 items) and 5 random cards per card file (30 cards), key and explanation checked by hand.

Counts: **0 blocker, 1 major, 11 minor, 9 cosmetic (21 new).** Regression: **81 of 81 earlier findings pass** (three have follow-on findings below: P1-26 to #9, P1-27/P2-14 to #11, P2-5 to #6).

Line numbers are for `1e68393`.

## Bugs

### Major

1. **[major] Timed ACT Reading and Science scatter passages: almost every question is a new passage.**
   Page: timed.html (ACT Reading, ACT Science, and the full-length ACT chain).
   Repro: ACT profile with Science on, Timed, start Reading. Read `alakai.act.timed_inprogress.itemIds` and group by `passage`.
   Happened: Reading drew 36 items from **17 different passages** with **35 passage switches** in 36 questions (sequence ABCDEFGHIEDJKCIJCLHL...); Science drew 40 items from 15 passages with 38 switches. Each item reprints its full passage, so a student rereads a new 400-word passage nearly every question, and the same passage comes back several times out of order. The Time squeeze page tells them "4 passages in 40 minutes: 10 minutes a passage" and "Reading: passage 2 done at 20:00. Science: passage 3 done at 20:00", which this module makes impossible to practice. The bank has 4 to 5 items per passage (Reading 17 passages, Science 15).
   Expected: ACT Reading and Science modules pick whole passages (Reading about 4 passages, Science about 6 to 7) and keep each passage's items together, ordered by passage, not by item difficulty.
   Cause: timed.html:132-143 `start()` shuffles items, picks by difficulty band and then sorts all items by difficulty, with no notion of a passage set. Same draw for placement (placement.html setup), which matters less because it is untimed.

### Minor

2. **[minor] The weekly plan schedules a full-length test the day before the real test.**
   Page: dashboard.html, This week. Repro: test date 2026-11-07, clock 2026-11-06 23:30 HST.
   Happened: "Full-length test (test is in 1 days)" (also at 2 and 3 days out, and every day from 14 to 11 days out). The Time squeeze handout says "The night before: pau. No new material. Sleep." and the plan note says "full test at 14 and 3 days out".
   Expected: one full test at about 14 days and one at about 3 days, never 1 or 2 days out.
   Cause: dashboard.html:220 `dte <= 14 && dte > 10 || dte <= 3 && dte > 0`.

3. **[minor] Screen readers are not told whether an answer was right.**
   Page: drill.html, placement (end), notes.html check, quiz Blitz. Repro: VoiceOver or the accessibility tree; answer a drill item.
   Happened: the verdict line ("Shoots. Da test does that on purpose."), the trap chip and the explanation are inserted with no `role="status"` or `aria-live` (0 live regions in `#fb`), and the tapped choice becomes disabled, so focus drops to `<body>`. Only the hint-mode "Not quite" line has `role="status"`.
   Expected: the feedback container is a polite live region, and focus moves to the verdict or the Next button.
   Cause: app.js:247-252 `showFeedback`, engine.js:84-91 `explain`.

4. **[minor] Flashcards: the question is hidden from screen readers.**
   Page: quiz.html Study. Repro: accessibility tree of `#card`.
   Happened: the button's accessible name is "Flashcard. Press Enter or Space to flip."; the front text ("What is a dangling modifier?") is not part of the name, and button content is not read separately by VoiceOver or TalkBack.
   Expected: name from content (drop `aria-label`, keep the hint as `aria-describedby`), or `aria-label` built from the front text.
   Cause: quiz.html:50.

5. **[minor] Risk, not verified on a device: the podcast check may never unlock when the episode is played with the phone locked or the app in the background.**
   Page: notes.html. The 90% rule counts only `timeupdate` steps under 2 s while the page script is running (notes.html:111). When iOS suspends a locked or backgrounded page, playback continues but the next `timeupdate` after waking is one large jump, which is thrown away. A student who listens on the bus with the screen off would hear the whole episode and still see "unlocks when you have listened to 90%". In Chromium at 2x the count works (20 s of play added 30 s heard); at 16x it never counts (4 s steps), which shows the mechanism.
   Expected: check on an iPhone; if confirmed, credit a jump when the audio was not paused and not seeking between the two events (keep the seek guard).

6. **[minor] ACT natural-order rule: choices with units, clock times and ranges are still out of order, and keys.py does not catch them.**
   Page: data/act/drills_math.json, drills_science.json. Repro: `drill.html?item=act-math-modeling-013` (ACT profile).
   Happened: `act-math-modeling-013` 225, 900, 432, 450 m^2; `act-math-prealgebra-008` 11:36, 8:36, 8:06, 9:00 a.m.; `act-science-data-011` Weeks 6 to 8, 2 to 4, 4 to 6, 0 to 2; `act-science-research-020` 20 to 25 C, 25 to 30 C, 10 to 15 C, 15 to 20 C. Coordinate pairs are also unordered by x (`act-math-coordinate-002`, `-009`, `-011`, `-012`, `-019`, e.g. (-4/3, 0), (32/3, 0), (16/3, 0), (6, 0)). BANK_SCHEMA.md says ACT Math and Science numeric choices are ascending.
   Expected: these parse as ordered values (unit `m^2`, times, "a to b" ranges by the first number, pairs by x then y) and keys.py fails them when out of order.
   Cause: build_scripts/banks/rebalance.py:58 `numeric_value` rejects `^` units, times and ranges, so keys.py:63 skips the item.

7. **[minor] Offline, an unknown or nested URL shows a broken, unstyled page with a script error.**
   Page: sw.js. Repro (scratch copy, SW installed, server stopped): open `/a/b/c` or `/drill.html/extra`.
   Happened: the SW falls back to `index.html`, served at the nested URL, so its relative `assets/app.css` and `assets/app.js` resolve to `/a/b/assets/...`, miss the cache and fail: no styles, and "Cannot read properties of undefined (reading 'boot')". Online the same URLs get the good 404 page.
   Expected: fall back to `404.html` (it has `<base href="/">` and is precached), or match the fallback's assets from the root.
   Cause: sw.js:33 `.catch(() => caches.match('index.html'))`.

8. **[minor] A drill link for the other test says "No items for that yet."**
   Page: drill.html. Repro: SAT selected, open `drill.html?skill=english-punct` (or `?section=reading`, `?item=act-math-algebra-004`), for example a link a teacher shares.
   Happened: alert "No items for that yet." and the SAT picker.
   Expected: switch to the test that owns the skill or item (skill ids are unique across tests), or say "That is an ACT drill: switch to ACT?".
   Cause: drill.html:147 deep links run `start()` against the current test's bank only.

9. **[minor] Corrupt storage can still stop the dashboard part way.** (Follow-on to P1-26 and P2-13.)
   Repro A: `alakai.sat.timed = [{"n":3,"right":1,"name":"x","id":null,"seconds":60,"at":1}]`, open the dashboard. Happened: `Cannot read properties of null (reading 'includes')` at dashboard.html:203; Estimated band, Official practice, the weekly plan and the milestone banner never render.
   Repro B: `profile.lastscore` stored as a number (1200). Happened: `(profile.lastscore || "").trim is not a function` at dashboard.html:197, same stop. A non-string `profile.name` shows "Aloha, [object Object]" and goes into the report subject.
   Also: `alakai.pattern = "../../x"` requests `/assets/patterns/../../x.svg` (404) because app.js:218-219 does not check the id; a junk sent-log entry shows "Invalid Date / undefined" in Settings.
   Expected: `Progress.summary` keeps timed records only with a string `id` and numeric `right`/`n`; profile text fields are coerced with `String()`; pattern ids are checked against the list.

10. **[minor] The milestone banner survives a test toggle and then sends the other test's report.**
    Page: dashboard.html. Repro: finish an SAT timed module, open the dashboard (banner shows), tap ACT, tap "Send progress report" in the banner.
    Happened: the banner stays (it is only ever shown, never hidden, by `render`) and the report is built for ACT.
    Cause: dashboard.html:226-227 has no `else` that hides `#milestone`.

11. **[minor] Touch targets still under 44 px.** (Follow-on to P1-27 and P2-14; all meet the WCAG 2.2 minimum of 24 px.)
    Measured at every size: SAT/ACT toggle 63x40 and 66x40 on every page (app.css:134); drill skill links 40 to 41 px tall; drill Easy / Medium / Hard / "Only ones I've missed" checkbox rows 24 px tall; the "Approach" and "Transcript" `<summary>` rows 24 px tall; timed question grid 40x40. Only the onboarding answer "phone" enlarges buttons (and not summaries or checkbox labels), so iPad and "mix" students get the small sizes.

12. **[minor] Redo onboarding starts blank and silently drops the parent email and test date.**
    Page: settings.html "Redo onboarding" to onboard.html?redo=1. Repro: profile with email, parent email, test date; Redo, pick answers, skip the date, fill the required name and grade, Finish.
    Happened: no question or contact field is prefilled, so the parent CC and test date are gone unless retyped, and the dashboard loses its countdown.
    Expected: prefill from the current profile (redo means "change my answers"), or say on the first step that everything starts over.
    Cause: onboard.html:60 `params.get('redo') ? null : A.profile()`.

### Cosmetic

13. **[cosmetic]** "Full-length test (test is in 1 days)" (dashboard.html:220). Pluralize.
14. **[cosmetic]** Export file name uses the UTC date: at 22:00 HST on 10-18 it is `alakai-export-2026-10-19.json` (settings.html:215).
15. **[cosmetic]** Settings previews theme, school colours and pattern the moment a select changes, but they revert on the next page unless Save is tapped, with no hint that there are unsaved changes (settings.html:184-185).
16. **[cosmetic]** Content: "Hawaii Island" and "Kauai" without the ʻokina in the shared passage of `act-science-conflict-013` to `-016`; the rest of the bank uses Hawaiʻi.
17. **[cosmetic]** Content: `sat-math-alg-linear-fn-016` (key 36/13) accepts "2.77". The SAT requires a decimal to fill the answer space (5 characters for a positive answer: 2.769, truncated or rounded), so the real test would mark 2.77 wrong. Drop "2.77" from `answer_alt`.
18. **[cosmetic]** Score bands: SAT 80% gives 620 to 700 and 90% gives 720 to 800, so nothing maps to 710; ACT English tops out at 35 (data/sat/scale.json, data/act/scale.json).
19. **[cosmetic]** Offline, a podcast episode opens a player that never plays, with no "audio needs a connection" line (notes.html:94; the list itself handles offline).
20. **[cosmetic]** A refresh in the middle of onboarding restarts at Question 1 and loses the answers so far (onboard.html:67 keeps them in memory only).
21. **[cosmetic]** Card `sat-card-math-059` "Volume formulas given on the SAT reference sheet" has the back "Box, cylinder, sphere, cone, and pyramid volumes": a list of names, not a recallable fact, and it shows up as a Blitz answer.

## Tutor read (content)

90 drills, 15 per section, seeded random (seed 3303), keys and explanations checked by hand: **no wrong keys, no explanation that contradicts its key.** Math checked by recomputation (slopes, rational equations, percent change, permutations, probability, space diagonal, circle form, trig max, x-intercept 16/3). RW and Reading keys are the best-supported choice in every sampled item; Science table and graph reads match the data. Notes: `act-reading-craft-001` ("add gentle humor") is the best of the four but softer than the others; `act-english-strategy-004` is correct but repeats "machines" in the keyed sentence. 30 cards (5 per file): all accurate and verbatim-style, except #21. No duplicate fronts or backs in any card file.

## Regression: all 81 earlier findings

P = Playwright rerun of the original repro, C = code or data check, L = live site.

| # | Finding | Result | How checked |
|---|---|---|---|
| P1-1 | Miss lost without cause | pass | P: 3 misses, Next without cause; DB and errlog have all 3, cause `unsorted`, one patched to `concept` |
| P1-2 | Accuracy, report, placement seeding | pass | P: placement only: 0 answered, "–", weak spots filled, report "Placement check: 10/44"; then 4 drills + 1 card: 4 answered, 25% on both dashboard and report |
| P1-3 | Double tap To the end | pass | P: 1 `sat.timed` entry, 22 timed records |
| P1-4 | Chain buttons pile up | pass | P: 1 button after RW M1, 1 after RW M2 |
| P1-5 | Refresh mid-module | pass | P: reload and Back/Forward offer Resume; 3 answers, flag, item 4, clock 31:59 restored |
| P1-6 | Podcast position | pass | P: saved 120.5 s, "Resumes at 2:01", playing at 124 s |
| P1-7 | Check resets on ended | pass | P: on Check 2/3, `ended` fired, still 2/3 |
| P1-8 | Hint retry counted right | pass | P: `correct:false, retry:true, hint:true, cause:'needed hint'`, errlog entry |
| P1-9 | Finish hangs on dead ping | pass | P: Worker hanging 4 s, Finish navigated in 0.09 s |
| P1-10 | Offline gaps | pass | P (server stopped): `/`, dashboard, `drill.html?skill=`, `onboard.html?redo=1`, `?next=`, `notes.html?ep=3` (14 episodes), quiz, timed, ACT toggle; L: 54 entries in `alakai-v15`. See #7 |
| P1-11 | Keyboard cards, episodes | pass | P: Enter flips (`aria-expanded` true), Enter on `.ep` plays. See #4 |
| P1-12 | Blocked storage | pass | P: localStorage, sessionStorage and indexedDB getters throwing: 9 pages render with one notice, drill answers, Start reaches onboarding, no ping |
| P1-13 | Key bias | pass | C: keys.py; own tally SAT RW 25/25/25/25, SAT Math 25 each, ACT English 28/27/23/22, Math 25 each, Reading 26/25/20/29, Science 25/26/25/25; podcast checks in band |
| P1-14 | Toggle mid-drill | pass | P: toggle hides the run |
| P1-15 | Onboarding double tap | pass | P: double tap on every option over 3 full onboardings, no question skipped |
| P1-16 | Back from contact alerts | pass | P: no dialog |
| P1-17 | Open redirect | pass | P: `?next=https://example.org/` lands on placement.html |
| P1-18 | Contact labels | pass | P: all six `label[for]` |
| P1-19 | Science off on re-run | pass | P: "yes" pressed, `science:true` kept |
| P1-20 | Both + English on SAT | pass | P: not on SAT Next up, on ACT |
| P1-21 | Deep link query at gate | pass | P: `onboard.html?next=drill.html%3Fskill%3Drw-ii-central` |
| P1-22 | Study double tap | pass | P: step 1, queue 117 to 116 |
| P1-23 | Blitz small topics | pass | P: Apostrophes (5) disables Blitz with the note |
| P1-24 | Settings lacks options | pass | C/P: missmode, timepressure, minutes present and saved |
| P1-25 | Erase re-pings | pass | P: after erase only `pinged`, `ping_sent`, `test`; re-onboarding sent 0 pings |
| P1-26 | Bad stored values | pass | P: errlog `{"a":1}`, timed `"x"`, blitz `{}`, episodes `[1]`, test `"xyz"`: no page errors on 6 pages. See #9 |
| P1-27 | Touch targets | pass | P: values as fixed (grid 40, strike 44, choices 44+, brand 44). See #11 |
| P1-28 | No 404 | pass | L: `/nope.html`, `/a/b/c`, `/drill.html/extra`, `/Dashboard.html` give the custom page, styled, mark loads |
| P1-29 | Strike state | pass | P: `aria-pressed="true"` |
| P1-30 | Negative days | pass | P: 2026-11-08 shows "Done", "test date passed…", report omits days |
| P1-31 | Placement estimate | pass | P: 48 on placement and nudge |
| P1-32 | Unused onboarding answers | pass | P: firstmode hear puts the podcast first; device phone sets `data-device` |
| P1-33 | HPA preselected | pass | P: placeholder; Start shows "Choose your school first" |
| P1-34 | 90% by scrubbing | pass | P: scrub to end stays locked; real play unlocks. See #5 |
| P1-35 | ACT Math 5 choices | pass | C: 168 items, 4 choices each |
| P1-36 | Science cards | pass | C: 41 |
| P1-37 | Free response hint signal | pass | P: "Not quite", `aria-invalid`, hint |
| P1-38 | Break | pass | P: 10:00 countdown, Start now; reload during break offers Continue |
| P1-39 | Question counter | pass | P: footer count equals "of N" |
| P1-40 | "1 active days" | pass | P: "1 active day, current streak 1 day" |
| P1-41 | "Why :" | pass | P: "Answer: 1/3. Why:" |
| P1-42 | Empty parentheses | pass | P: "Colors: Alakaʻi default" |
| P1-43 | Pattern disclosure | pass | C: "solid by default. Seven optional patterns"; review note is a comment |
| P1-44 | Dimmed reveal | pass | C: app.css:176-177 |
| P1-45 | Clock 0:00 | pass | P: "35:00" at start |
| P1-46 | Placement nav | pass | P: Dashboard `aria-current="true"` |
| P1-47 | Picked choice | pass | C/P: ring, tint, "✓ Selected", `aria-pressed` |
| P1-48 | Plan module length | pass | P: "32 to 35 min" |
| P2-1 | Dark mode contrast | pass | P: own text-contrast audit of 11 pages x 26 schools x 2 themes (data, drill answered, timed): 0 failures |
| P2-2 | SW precache stale | pass | P (max-age=600 copy): v16 install sent 54 `no-cache` requests; `Alakai.VERSION` 9.9.9 |
| P2-3 | Days to test in HST | pass | P: 11-06 23:30 HST 1, 11-07 00:30 0, 10-18 13:00 20 |
| P2-4 | Ping twice | pass | P: Worker 1.5 s, Skip after 0.3 s, dashboard, drills: 1 POST |
| P2-5 | ACT numeric order | pass | C: `act-math-functions-007` 5, 48, 64, 69; `geometry-019` 3, 6, 7, 11; keys.py passes. See #6 |
| P2-6 | iPhone negative grid-in | pass | P (iPhone UA, tap keys): "3" then − gives -3 (right), toggles back; 36 / 13 via the "/" key right; focus stays in the box |
| P2-7 | Blitz timeout tap | pass | P: after 8 s, 0 choices enabled, key shown, score 0 |
| P2-8 | Check double tap | pass | P: double taps on every choice and Next: 3/3, stayed on the episode |
| P2-9 | Dashboard fast toggle | pass | P: ACT banks delayed 0.8 s, ACT then SAT: SAT rings |
| P2-10 | ACT break position | pass | P: Science off and on: break before Reading |
| P2-11 | Placement toggle | pass | P: 2 SAT placement records, note shown, ACT intro |
| P2-12 | Offline podcast list | pass | P: offline `notes.html?ep=3` lists 14 |
| P2-13 | Junk inside arrays | pass | P: `[null,3,"x"]`, `[null]` lists and bad `timed_inprogress`: no page errors on 6 pages |
| P2-14 | Touch targets | pass | P: nav, redo, Drill it, footer links 44+. See #11 |
| P2-15 | Timing at 320 | pass | P: no horizontal scroll on any page at 320 |
| P2-16 | Next with no pick | pass | P: "Pick one to continue." |
| P2-17 | Science before fear | pass | P: order and list (ACT, No: English, Math, Reading) |
| P2-18 | Science homework off | pass | P: confirm shown; yes saves `science:true` and starts the drill |
| P2-19 | Settings before onboarding | pass | P: draft saved, no profile, dashboard redirects |
| P2-20 | grammar-006 worked | pass | C: "Choice B shifts number and tense; C shifts person. Answer: choice D." |
| P2-21 | Light chip contrast | pass | P: contrast audit, 0 failures |
| P2-22 | Practice menu keys | pass | P: focus to first link, Escape closes and refocuses |
| P2-23 | Error log "and N more" | pass | P: "and 8 more (8 due: redo the due ones)." |
| P2-24 | Empty episode topics | pass | P: every row has a topic |
| P2-25 | Bare "Trap" | pass | P: "other trap" |
| P2-26 | "Being recorded" line | pass | P: absent |
| P2-27 | iPad wording | pass | P: "Want the icon on your tablet to match Kaʻū?" |
| P2-28 | Contact disclosure line | pass | P: `{"school":"kohala","grade":"10"}` follows the selects |
| P2-29 | Strike after answer | pass | P: all strike buttons disabled |
| P2-30 | 404 frame and palette | pass | L: 3 frame bars, school mark |
| P2-31 | Timed milestone count | pass | C: timed.html:211 running `timedcount` |
| P2-32 | .gitignore | pass (still not reproducible) | C: `git check-ignore --no-index` matches none of app.js, engine.js, app.css, data |
| P2-33 | Blitz repeats | pass | P: 57 cards in a round, 0 back-to-back repeats |

## Checked and passed

- Verify suite: `bash build_scripts/verify/all.sh` passes (contrast, keys, links, JSON, node, podcast dry runs, smoke); the tree stayed clean.
- Journeys at iPhone, iPad and desktop, light and dark: landing (Start without school blocked), onboarding SAT, ACT (Science No) and Both (Science Yes) with double taps on every option, 200-character name, ping exactly once with body `{"school":"kohala","grade":"10"}`, placement (44 items, Stop and score, by-section table), dashboard, report mailto (1.5 kB, `mailto:kai%40example.com?cc=mom%40example.com&subject=…`).
- Days to test in Pacific/Honolulu across midnight, test day, past date and 20 days out; report line matches.
- Drills: skill, section, mixed, item and redo deep links; misses logged with trap and cause; reload mid-set; double tap Next (no skips, 8 of 8 recorded); Science-off gate both ways; grid-in minus and fraction keys on iPhone UA.
- Quizzers: due count, small-topic Blitz gate, Study keyboard flip, double-tap grade, No requeues, 60 s Blitz round with a fake clock (score saved, high-score table), no duplicate answer texts, toggle mid-round not scored.
- Timed: resume after reload and Back/Forward; SAT full-length chain with adaptive M2 ("easier") and the break, reload during the break and Continue; time-up auto finish; ACT chain with and without Science (break before Reading); toggle mid-module saves.
- Podcasts: all 28 mp3s 206 `audio/mpeg` under a browser UA; resume, scrub lock, unlock by real play at 2x, check with double taps, done mark, keyboard play, toggle closes the player, report line.
- Settings: theme, school, pattern, science, date saved and applied on the next page; iOS icon prompt; export (keys plus attempts); erase keeps only the ping record; re-onboarding sends no ping.
- Contrast: own audit of every visible text node on 11 pages for all 26 schools in both themes with seeded data and answered states: 0 failures (detector validated on an injected 1.4:1 line).
- Layout: no horizontal scroll at 320, 390, 820, 1280 on 13 pages, including the timed run and review, with a long Hawaiian name.
- Service worker (live): `alakai-v15`, 54 entries, controls the page; offline deep links work; per-school manifest and theme-color swap (Hilo #034CB2); 26 manifests valid with all icons present.
- Robustness: invalid JSON in 11 keys, wrong-typed values in 21 keys, blocked storage: every page renders (exceptions in #9).
- Official practice links: all 5 return 200.
