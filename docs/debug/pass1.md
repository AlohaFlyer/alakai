# Alakaʻi Test Prep: debug pass 1

Date: 2026-10-18. Build tested: master `de9f743` (site 1.0.0, sw `alakai-v13`). Live site files checked identical to local (md5 of app.js, sw.js, drill.html, episodes.json).
Method: code read of every page plus Python Playwright (Chromium) at 390x844 iPhone UA, 820x1180 iPad UA, 1280x800 desktop, light and dark, against the live site and a local copy on 127.0.0.1:8765. The ping endpoint was intercepted in every run (no real pings sent). The service-worker version bump was simulated on a scratch copy, not the repo.

Counts: **1 blocker, 12 major, 25 minor, 10 cosmetic (48 total).**

Line numbers are for the files as they stand at `de9f743`.

## Bugs

### Blocker

1. **[blocker] Drills: a miss is lost if the student taps Next without answering "Why did you miss it?"**
   Page: drill.html. Repro: open `drill.html?skill=rw-ii-central`, pick a wrong choice, ignore the Careless / Didn't know it / Rushed row, tap Next. Repeat to the end of the set.
   Happened: the miss is never written to IndexedDB or to `sat.errlog` (`errlog` stayed null and the DB had 0 attempts after 9 skipped misses). The set summary still says "Misses are in your error log", and the average time uses only the recorded items (it showed "about 1s per item"; it would show NaN if every item were missed). Because the Next button sits below the explanation and the cause row sits above it, this is the path most students will take.
   Expected: every answer is recorded the moment it is graded, and the cause gets attached later if the student gives one.
   Cause: drill.html:115 `res.cause = await E.askCause(host)` blocks `results.push` and `E.record` (drill.html:116). The Next button that engine.js:82 creates is live right away and calls `onNext`, which re-renders the item, so the `askCause` promise never resolves.

### Major

2. **[major] Dashboard accuracy and the parent report are wrong. Placement does not seed weak spots.**
   Page: dashboard.html, the report email, placement.html. Repro: finish the placement check with some answers right (I had 15 of 44), then open the dashboard and tap Send progress report.
   Happened: the dashboard shows "44 questions answered, 0%" accuracy. The report body says "44 questions answered, 0% correct", and its By section list is empty. Weak spots says "Do a few drills first", the section rings say "0 done", and the weekly plan lists skills in file order. Flashcard grades (`kind:'card'`) and redo attempts dilute accuracy the same way.
   Expected: accuracy uses the same records in the numerator and the denominator. Placement shows up in weak spots, as placement.html:87 promises ("Weak spots are seeded on your dashboard").
   Cause: app.js:191 counts `right`, `bySkill` and `bySection` only for kinds drill, timed and blitz, but app.js:201 returns `attempts.length` across all kinds. Placement records `kind 'placement'` (placement.html:81).

3. **[major] Timed: a double tap on "To the end" finishes the module twice.**
   Page: timed.html. Repro: in the full-length test, answer every item in RW Module 2, then double-tap Next / To the end on the last item.
   Happened: two `sat-rw-m2` entries were saved to `sat.timed`, and 81 timed records went to the DB instead of 54. The chain also advanced twice, which put two buttons in the review card: "Take a 10-minute break, then start Math Module 2" and "…Math Module 1". Taking the first one skips Math Module 1.
   Expected: finish runs once, with a guard flag or a disabled button.
   Cause: timed.html:137 calls `finish(false)` on every click. `finish` (timed.html:139) awaits per-item records before it hides `#run`, so the button stays clickable.

4. **[major] Timed full-length chain: old "Continue to …" buttons pile up.**
   Page: timed.html review card. Repro: start the full-length test and finish RW M1, then RW M2.
   Happened: the review card shows "Continue to Reading and Writing Module 2" (stale) next to the new break button. Tapping the stale one re-runs a module that is already done. Old buttons also stay after the chain ends.
   Expected: one current Continue button, and old ones removed.
   Cause: timed.html:158-160 `document.getElementById('rsummary').after(btn)` never removes the previous button.

5. **[major] Timed: a refresh, Back or accidental swipe mid-module throws the whole module away without a warning.**
   Page: timed.html. Repro: start Math Module 1 (35 min), answer 15 items, pull to refresh or press Back.
   Happened (confirmed in code, not run on the live site): no state is persisted, there is no `beforeunload` prompt, and no resume is offered. The answers and clock are gone and nothing is recorded. Drills lose only the item in progress.
   Expected: state saved to `alakai.<test>.timed_inprogress` (items, answers, flags, end time) with a resume offer, or at least a `beforeunload` confirm while `#run` is visible.
   Cause: timed.html:92-116 keep `items`, `answers` and `end` only in closure variables.

6. **[major] Podcast: playback position is not saved, so there is no resume.**
   Page: notes.html. Repro: play SAT Ep 2 for a few minutes, leave, come back and tap Ep 2.
   Happened: `alakai.sat.episodes` was still null after playback. The episode restarts at 0:00.
   Expected: the position is saved periodically (every 5 s or on pause) and restored after `loadedmetadata`.
   Cause: notes.html:87 updates `rec.pos` only in memory and calls `S.set` only on the first crossing of 90%. Also, notes.html:88 sets `currentTime` before the metadata has loaded (`preload="none"`), which would be ignored even if a position were saved.

7. **[major] Podcast: the 3-question check resets when the audio ends.**
   Page: notes.html. Repro: play an episode, scrub past 90% so the check unlocks, answer Check 1 while the audio keeps playing, and let the audio finish.
   Happened: the check jumped from "Check 2/3" back to "Check 1/3" and the score reset to 0.
   Expected: the check is rendered once per unlock, and `onended` does nothing if it is already shown or done.
   Cause: notes.html:89 `a.onended` calls `renderCheck(e, rec)` unconditionally, and `renderCheck` starts again at `i = 0`.

8. **[major] Hint mode counts wrong-then-right as fully correct, with no error-log entry.**
   Page: drill.html with the profile set to `missmode: 'hint'` (the onboarding choice "A hint, then let me retry"). Repro: pick a wrong answer, read the auto hint, then pick the right one.
   Happened: the item was recorded `correct: true, hint: false` with no error-log entry. These students' accuracy, skill levels and error log overstate them.
   Expected: record correct-after-retry separately (for example `retry: true`), count it as a miss for the error log, and set `hintUsed = true` when the hint is shown automatically.
   Cause: engine.js:87 shows the hint without setting `hintUsed`. engine.js:86 then calls `finish(true, …)`.

9. **[major] Onboarding Finish hangs with no feedback if the ping endpoint does not answer.**
   Page: onboard.html, last step. Repro: block or blackhole `ping.alakaitestprep.app` (a captive portal, school filter or flaky rural connection) and tap Finish.
   Happened: the page was still on onboard.html 15 s later, with nothing on screen. The profile is saved, but the student never reaches placement.
   Expected: the ping is fire-and-forget, or races a timeout of about 2 s, and navigation does not wait on it.
   Cause: onboard.html:118 `await A.pingOnce(...)`, and app.js:177 `await fetch(...)` with no `AbortController` timeout.

10. **[major] Offline: the service worker cannot serve `/`, any URL with a query string, or banks not yet visited.**
    Page: all of them, through sw.js. Repro: load the live site once, wait more than 10 min (the GitHub Pages `max-age=600`), go offline, then open `alakaitestprep.app/`, `drill.html?skill=…`, `onboard.html?redo=1`, `notes.html?ep=3`, or toggle to ACT.
    Happened: `caches.match` returned false for `/`, `drill.html?skill=rw-ii-central`, `onboard.html?redo=1`, `onboard.html?next=drill.html`, `notes.html?ep=3`, `data/act/drills_english.json`, `data/act/cards_math.json`, `site.webmanifest` and `favicon.ico`. During the test these still loaded only because Chromium's HTTP cache was fresh. After a version bump, `data/sat/drills_*.json` are also evicted until the page is revisited online.
    Expected: precache the drill and card banks, map `/` to `index.html`, and use `caches.match(req, {ignoreSearch: true})` for navigations.
    Cause: sw.js:3 (the SHELL list has no banks, `/`, `favicon.ico` or manifest) and sw.js:17 (`caches.match(e.request)` takes the search string into account).

11. **[major] Keyboard and switch access: flashcards and podcast episodes cannot be operated.**
    Page: quiz.html (Study) and notes.html (episode list). Repro: Tab through the page.
    Happened: `#card` (the flip card) and `.ep` rows are `<div>`s with click handlers, `tabIndex -1` and no role. A keyboard user cannot flip a card, so Study is unusable, and cannot start an episode.
    Expected: `<button>` elements, or `role="button" tabindex="0"` plus Enter and Space handlers.
    Cause: quiz.html:49 and :109, notes.html:75-76.

12. **[major] Browsers with site data blocked: the dashboard crashes and onboarding loops forever.**
    Page: dashboard.html, onboard.html. Repro: Chrome with "Block all site data" (localStorage throws and `indexedDB.open` throws SecurityError). This was simulated with init scripts.
    Happened: if IndexedDB throws on access, dashboard.html dies with `Uncaught (in promise) Error` and shows nothing below the stats. If `window.indexedDB` is undefined, it throws "Cannot read properties of undefined (reading 'open')". If localStorage throws, Finish goes to `onboard.html?next=placement.html` forever, and the ping fires on every pass because `pinged` cannot be stored.
    Expected: wrap `indexedDB.open` in try/catch and check `window.indexedDB` itself. When storage is unavailable, show one banner ("this browser is blocking storage; progress cannot be saved") instead of looping.
    Cause: app.js:26 (`'indexedDB' in window` is not enough; `open` can throw synchronously inside the Promise executor) and app.js:168 (the gate does not know when storage is unavailable).

13. **[major] Content: answer-key position bias in the ACT bank and the podcast checks.**
    Page: data/act/drills_math.json, drills_science.json, data/episodes.json. Repro: tally answer indexes.
    Happened: in ACT math the key is A 14, B 63, C 62, D 25, E 4 (always picking B or C wins 74% of the time). In ACT science it is A 10, B 31, C 19, D 1 (61 items). In the podcast checks the key is B for 24 of 42 SAT and 27 of 42 ACT questions, and D only once in each show. The SAT banks are balanced (about 25% each).
    Expected: keys roughly uniform per section, with a check added to build_scripts/verify/keys.py (for example, fail if any position is above 35% or below 15%).
    Cause: content generation. Re-shuffle choices together with `distractors` and `traps`.

### Minor

14. **[minor] Toggling SAT/ACT in the middle of a drill, Study session or episode files the record under the wrong test.** Repro: start an SAT drill, tap ACT, answer. The DB got `act:sat-rw-ii-central-002`, and the run card stays on screen. The same happens for card schedules in quiz.html and episode progress in notes.html (`test` is a reassigned global). Cause: drill.html:86 reassigns `test`, and the record uses the outer `test`. Fix: capture `test` per run, or end the run on the toggle.
15. **[minor] Onboarding: a double tap on an option, or a tap followed quickly by Next, skips the next question.** Repro: on Q1, double-tap ACT. The page landed on "Question 3 of 11" and the test-date question was skipped. Cause: onboard.html:95 schedules `setTimeout(() => { i++; render(); }, 180)` on every click, and Next also does `i++`.
16. **[minor] Onboarding: Back from the contact step pops the validation alert** ("Grade and first name help…") when grade or name is empty. Cause: onboard.html:111 runs `collect()`, which alerts at :105.
17. **[minor] Onboarding: open redirect.** `onboard.html?next=https://example.org/` sent the browser to example.org after Finish. Cause: onboard.html:121. Fix: only allow same-origin page names such as `/^[a-z]+\.html(\?.*)?$/`.
18. **[minor] Onboarding contact step: none of the six fields has a programmatic label** (`<label>` has no `for`, and the inputs have no aria-label). Screen readers announce "edit text". Cause: onboard.html:85-90. The date and text questions (`#in`) also have no label.
19. **[minor] Opening onboard.html without `?redo` on an existing ACT profile turns Science off.** Repro: an ACT profile with `science: true`, then open `onboard.html`, tap Next through to Finish. Result: `science: false`. Cause: onboard.html:114 tests `=== 'yes'` against a value that is already boolean, and the science option never shows as pressed.
20. **[minor] "Both" offers ACT sections as the scariest section, then the app runs as SAT.** Repro: onboard with Both and pick English as the scariest. The dashboard's Next up shows "Start with english, the section you flagged" and links `drill.html?section=english`, which alerts "No items for that yet." Cause: onboard.html:76 and dashboard.html:151.
21. **[minor] Deep links lose their query string at the onboarding gate.** `drill.html?skill=X` for a new visitor redirects to `onboard.html?next=drill.html`, so `?skill=` is dropped. This affects every podcast homework link opened from a share. Cause: app.js:168 uses only `pathname`.
22. **[minor] Quizzer Study: a double tap on a grade promotes twice and skips a card.** Repro: flip a card and double-tap Yes. The step went to 2 instead of 1, and the queue dropped from 117 to 115. Cause: quiz.html:110-116 has no guard, and each click schedules `setTimeout(nextCard, 650)`.
23. **[minor] Blitz offers topics it refuses to run.** SAT Polygons (1 card), Triangles (2), Coordinate geometry (2) and Polynomials (2), plus ACT Style (1), give "Need at least 4 cards for Blitz." Topics with exactly 4 cards always show the same 4 answers. Cause: quiz.html:85 builds the topic list without a minimum, and :123 rejects the topic.
24. **[minor] Copy sends students to Settings for options Settings does not have.** drill.html:34 says feedback mode can be changed "in Settings", and timed.html:43 says pacing checkpoints can be changed "in Settings". Settings has no missmode, timepressure or minutes-a-day control, so the only path is Redo onboarding.
25. **[minor] Erase everything clears `pinged`, so the next onboarding pings again**, against the disclosure "It is sent once." Cause: app.js Store.eraseAll, triggered from settings.html:194. Decide whether erase means a new device; if it does not, keep `pinged` and `ping_sent`.
26. **[minor] No type checks on stored values: one bad key crashes a page.** `alakai.sat.errlog = {"a":1}` breaks dashboard (`filter is not a function`). `sat.timed = "x"` breaks dashboard. `sat.blitz = {}` breaks quiz. `test = "xyz"` breaks every page (quiz: `FILES[test] is not iterable`). Garbage that is not JSON in `alakai.profile` is handled (redirect to onboarding). Cause: app.js Store.get. Fix: add an `Array.isArray` / enum guard to Store.get callers, or a typed `getArray`.
27. **[minor] Touch targets under 40 px.** Timed question grid 34x30 (timed.html:26), strike × buttons 34 px wide (app.css:152), drill skill links 36 px tall, brand link 36 px, "Free official practice" 38 px on phone.
28. **[minor] No custom 404.** A broken link gives GitHub's generic "Page not found" with no way back into the app. Add a `404.html`.
29. **[minor] The strike (×) button exposes no state.** There is no `aria-pressed`, so a screen reader cannot tell whether a choice is crossed out. Cause: engine.js:56 and :64.
30. **[minor] Days to test goes negative after the test date** ("-5 days to test"), and the plan text stays the same. Cause: dashboard.html:130-131.
31. **[minor] The placement time estimate disagrees with itself.** The dashboard nudge says "about 20 minutes" (dashboard.html:58). The placement intro computes 48 min for SAT (44 items). Use the computed number in both places.
32. **[minor] Three onboarding answers are collected and never used:** `firstmode` ("Hearing it (play the episode first)" promises a behavior), `device` and `lastscore`. Either use them or drop the questions. That would also make the "10 quick questions" claim true.
33. **[minor] No school chosen means HPA.** The index picker preselects `hpa` (index.html:85), so a student who taps Start without choosing is themed HPA and pinged as `hpa`. This skews the school counter toward HPA. Fix: add a "Choose your school" placeholder.
34. **[minor] The 90% listened rule can be bypassed by scrubbing to the end.** Scrubbing past 90% unlocked the check immediately. Cause: notes.html:87 tests position, not time listened. Accept this or track accumulated play time.
35. **[minor] Content: ACT Math uses 5 answer choices.** The enhanced ACT (2025) moved Math to 4 choices. BANK_SCHEMA.md and drills_math.json use 5 (I am confident but not certain; check act.org). The time-squeeze guessing math is also stated only for four-choice items.
36. **[minor] Content: ACT Science has 35 cards**, below the schema minimum of 40 per section (BANK_SCHEMA.md).
37. **[minor] Free-response items in hint mode:** the first wrong submit shows the hint but gives no "not quite" signal and does not mark the input. Cause: engine.js:91.
38. **[minor] The "Take a 10-minute break" button has no break.** It starts the next module immediately with no countdown. Cause: timed.html:158.

### Cosmetic

39. **[cosmetic]** The onboarding counter reads "Question 1 of 10" and changes to "of 11" once ACT or Both is picked. The footer still says "10 quick questions" (onboard.html:47).
40. **[cosmetic]** The report says "1 active days" (app.js:220).
41. **[cosmetic]** Explanations for free-response items read "Answer: 23. Why :" (engine.js:79).
42. **[cosmetic]** The Settings school note shows empty parentheses for "Other": "Colors: Alakaʻi default ()" (settings.html:164).
43. **[cosmetic]** The pattern disclosure contradicts the app ("The frame is solid in the current release. Three optional patterns…" while seven are offered), and "Reviewed for cultural appropriateness: pending." is public (settings.html:124 and :131).
44. **[cosmetic]** After answering, every choice is disabled at `opacity: .5` (app.css:118), so the green right-answer reveal and the explanation context are dimmed, noticeably so in dark mode.
45. **[cosmetic]** The timed clock shows "0:00" for the first 500 ms of a module before the first tick (timed.html:96).
46. **[cosmetic]** Placement has no nav highlight, because it is not in the tab list.
47. **[cosmetic]** The selected answer in a timed module is shown only by a 1 px primary border (app.css:165), which is hard to see on a phone in light mode.
48. **[cosmetic]** The weekly plan always says "One timed module (35 min)", even for ACT, where Math is 50 min (dashboard.html:197).

## Checked and passed

- Verify suite: `bash build_scripts/verify/all.sh` passes (contrast for 26 schools, keys, links, JSON parse, `node --check`, podcast dry-run, smoke). Working tree was clean afterward.
- Data integrity (own script): 441 SAT and 429 ACT drills. Every drill has id, skill (present in skills.json), section matching its skill's section, stem, choices, answer index in range (string for grid-ins), explain, hint, worked and difficulty 1 to 3. No duplicate ids or duplicate choices; distractor arrays match the choice count; every skill has at least 16 items. Cards: all have id, front, back, topic and section, with no duplicate ids and backs under 25 words. strategies.json covers every skill id in both tests with no extras, and each entry has name, steps, trap and time. Each timed.json module has a big enough `timed_ok` pool in every difficulty band.
- Episodes: 28 episodes (14 SAT, 14 ACT). Every mp3 returns HEAD 200 `audio/mpeg` with `accept-ranges: bytes` under a browser UA. Measured durations match the listed `len` within 1 s. Each episode has 3 checks with the answer in range, and every homework href resolves to a real page, skill or section. Transcripts are present.
- Schools: the 26 ids match exactly the icon sets (64, mark-72, 180, 192, 512, 512-maskable) and `assets/manifests/*.webmanifest`. Manifests are valid JSON and their icons resolve. `site.webmanifest` is valid.
- The ping fires exactly once per onboarding: SAT, ACT and Both each produced one POST `{"school":"kohala","grade":"11"}`, and Redo onboarding did not re-ping. The CORS preflight on the live Worker returns 204 with the right headers. The "What gets stored" link goes to `#disclosures`, and the ping status line renders.
- Onboarding: the dynamic section list, the Science question shown only for ACT and Both, `setSize` derived from minutes, the iconSchool stamp, the redirect to placement, and the returning-visitor card (long Hawaiian names wrap cleanly).
- Placement: two per skill, Science included only when on, untimed, by-section table with "Start here" deep links, errlog seeded with traps.
- Dashboard: streak, days to test, timed table, error log with trap summary and redo links, skill-level table, official links, placement nudge hide rule, milestone pending banner (set after a timed module). The mailto builds `mailto:<student>?cc=<parent>&subject=…&body=…` correctly; with no student email it becomes `mailto:?cc=parent`.
- Drills: section, skill and mixed sets; the Approach box; the trap chip; "You crossed out the right answer" note; worked-solution details; difficulty and missed-only filters; deep links `?skill=`, `?section=`, `?mode=redo`, `?item=`. Bad or out-of-test deep links alert instead of crashing. Keyboard Enter answers a choice. A double click on Next did not skip an item (`strategyFor` resolves before the second click lands).
- Quizzers: due count, topic filter, Study flip and grade scheduling, Blitz 60 s clock, 8 s per-card bar, streak multiplier, local feedback lines (23 distinct lines seen in one round), no duplicate answer texts, round summary, and scores saved.
- Timed: module list, pace text, the adaptive M2 route (an easier M2 after a weak M1, "Module 2 was the easier version" shown), time-up auto finish ("time ran out" with blanks counted), flag and grid states, second-pass jump to the first blank, review list, Send report. The full-length chain moved through RW M1 to RW M2 to the break, apart from bugs 3 and 4.
- Time squeeze: SAT and ACT tables swap with the toggle, and the checkpoint math is correct (RW q9 at 10:40, Math q7 at 11:40, and so on). ACT 2025 lengths match act.org (English 50/35, Math 45/50, Reading 36/40, Science 40/40). Print button and Ep 3 link work.
- Podcasts: list, R2 playback in Chromium, transcript, check locked until 90%, check scoring, done mark, dashboard "1 episode completed", `?ep=` deep link.
- Settings: a school change re-themes `--primary`, the favicon, header mark, apple-touch-icon, manifest link and theme-color (HPA to Kohala) and persists across pages after Save. The iOS-UA icon prompt appears with iOS steps. Theme light and dark applied, patterns applied, the Science toggle hides and shows the ACT Science section, milestones off saved, Export JSON downloads (keys plus attempts), Erase clears and returns to index, the sent log renders.
- SAT/ACT toggle and the nav `aria-current` highlight are correct on all 8 nav pages. The practice menu opens, lists the current test first, and closes on an outside click.
- Layout: no horizontal scroll at 320 px or 390 px on any page (light and dark), nor on drill and timed run states at 390, 820 and 1280. No clipped headings, buttons or chips. All form inputs on non-onboarding pages are labelled, and no button lacks a name.
- Console: no errors or warnings on any page in normal use, local or live, apart from Playwright's own SW-blocked notices.
- Service worker: installs `alakai-v13` with 40 entries. A bump to v14 on a copy deleted v13, activated immediately, and served the new app.js on the next load. Pages load offline while cached (with the limits in bug 10).
- Corrupt storage: `alakai.profile` set to text that is not JSON, or to null, sends the visitor to onboarding with no crash. A missing `school` or `pattern` key falls back cleanly.
