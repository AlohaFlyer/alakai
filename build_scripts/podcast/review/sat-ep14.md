# sat-ep14 review, pass 1 (panel)

1. Facts line cited a dead URL (satsuite.collegeboard.org/sat/scores/sending-scores returns "Page not found"). Replaced with verified sources: superscore definition from blog.collegeboard.org/what-is-an-sat-superscore ("Colleges that superscore the SAT use your best section-level scores, even if they're from different tests"; only some colleges do); Score Choice page satsuite.collegeboard.org/scores/sending-sat-scores/additional/score-choice ("some colleges and scholarship programs require you to send all your scores").
2. Score sending was missing from the superscore answer (plan lists it). Derek now adds: to get superscored the college needs both test dates, so you send both, and some colleges want every score, so check that too.
3. Attempts: "no limit" verified at satsuite.collegeboard.org/help-center/how-many-times-can-student-take-sat-and-when-should-they-take-it ("Students can take the SAT as many times as they want"). Pono now also gives College Board's own recommendation: at least twice, spring of junior year and fall of senior year.
4. Fee waivers: the facts line and Pono said counselor only; satsuite.collegeboard.org/sat/registration/fee-waivers also allows a request directly to College Board. Pono now says both. The dead fees URL was dropped.
5. Homework rewritten as two clean steps matching the UI: open Settings, type the email in the parent or teacher email box, tap Save (settings.html has a Save button and the field is optional); then on the dashboard tap Send progress report (dashboard.html button label). It opens in your own email app with them copied, and the student presses send (settings.html privacy note: addressed to you, parent or teacher in CC).
6. PSAT/NMSQT: "built the same way" softened to "it tests the same skills, in Bluebook"; facts line now cites the October 1 to 30, 2026 window and BigFuture's junior-year rule.

Verified: superscore arithmetic 600 + 550 = 1150, 570 + 620 = 1190, 600 + 620 = 1220; 15 x 7 = 105 minutes; onboarding offers 15/30/45/60 and Settings has Redo onboarding; Do No Harm wording matches the approved Ep 1 line; accommodations line is counselor only; nerves answer has no medical advice; Ep 5 reading cross-reference correct; Kaden's season recap matches Eps 1 to 14; ratings never ten (season high 9 holds: Eps 7, 10, 12, 14); one bus gag, one rodeo bit, one comma bit; sunset (Pono says Kaunaʻoa) does not repeat within three; five voices. checks/sat-ep14.json one answer each.
Linters: render2 0 spliced; render.py ok, 1,426 words, 5 voices (panel limit 1,700).

## Pass 2

1. Open item from pass 1 resolved: the PSAT "same skills, in Bluebook" line is supportable. College Board's parents guide: "Structured similarly to the SAT, the PSAT/NMSQT measures the same knowledge and skills" (satsuite.collegeboard.org/media/pdf/parents-guide-digital-psat-nmsqt.pdf); student guide: "Bluebook is our custom-built application you'll use to take the PSAT/NMSQT" and SAT Suite tests "measure the same content domains" (satsuite.collegeboard.org/psat-nmsqt-student-guide/test-taking-information/introducing-digital), same 2 h 14 min, 2 x 27 x 32 and 2 x 22 x 35. Facts line now cites both instead of a bare "(College Board)". Script line unchanged.
2. Trap label made defensible: Kaden picked the best single date, which is a different method, not obviously "one more step." Derek now says "You stopped a step early. You compared the totals, but a superscore goes one step further, to each section. It takes the best of each section."

Re-checked: 1150, 1190, 1220; 105 minutes; Settings has Redo onboarding, the parent or teacher email field and Save; dashboard has Send progress report; counselor-only accommodations; no medical advice on nerves; one rating (9, never ten); five voices. Left alone: render.py estimates 9.6 min against target_minutes 8; words (1,439) are inside the 1,700 panel limit. Linters: render2 0 spliced; render.py ok, 1,439 words, 5 voices.

## Pass 3

1. Pass 2 open item decided: trimmed banter only, 1,439 to 1,384 words (est 9.6 to 9.2 min). Cuts: "We got a lot"; Sarah and Derek's pause-and-try setup shortened ("Make it a pause-and-try. Last one of the season." / "I'll read it twice."); Kaden "There it is" / Pono "Last episode. Had to." after the horse line; Lehua "and it's the right one".
2. Gag count: Sarah had two comma bits ("I stop at every comma" and the niece's "Happy, birthday" card). Cut the card, kept the on-topic line; Lehua's "Of course you do" now leads straight into the accommodations question.

All nine listener questions kept, superscore pause-and-try intact (1150, 1190, 1220), season recap intact. Stopped at 1,384 rather than 1,350: the next cuts would be Kaden's test-day proof lines or retrieval beats. Checks unaffected. Linters: render2 0 spliced; render.py ok, 1,384 words, 5 voices (panel limit 1,700).
