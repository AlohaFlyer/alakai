# sat-ep1 review, pass 1 (LIVE episode: changed lines need re-render)

1. LIVE. Opening said "welcome back" on the first published episode (Ep 0 never publishes). Now "Hey, welcome to SAT Notes, episode one."
2. LIVE. Overstated: "Every college publishes a middle fifty percent range for admitted students." Changed to "Most colleges publish a middle fifty percent range for their admitted or enrolled students. That means a quarter of those students..."
3. LIVE. Cross-reference: "We have a whole episode on how to guess well. That's episode two." Ep 2 is Crossing Out. Changed to "We have a whole episode on making those guesses smarter by crossing out wrong answers. That's episode two."
4. LIVE. Cross-reference: reference sheet "in episode seven". The plan puts it in Ep 11. Changed to "episode eleven".
5. LIVE. Cross-reference: "Episode two is guessing and the two-pass method." Two-pass is Ep 3. Changed to "Episode two is crossing out, how to find the wrong answers."
6. Facts line: added the claims the episode makes that were not listed (selective private colleges going back to required testing, approved calculator and reference sheet, one passage per question, Bluebook Mark for Review / eliminator / navigation grid) and corrected "published by each school" to "most colleges". Header only, no audio.

Verified unchanged: UH flagship "Do No Harm" line matches manoa.hawaii.edu/admissions/freshman (the policy covers admission and scholarships; some scholarships and direct-entry programs may require scores). Timings, 400 to 1600, 75/25 split are correct.

Linters: render2 0 spliced; render.py ok, 1,255 words.

## Pass 2 (LIVE: lines 2 to 5 need re-render)

1. Header: Do No Harm wording now matches manoa.hawaii.edu/admissions/freshman exactly ("scholarships or department direct entry programs may require test scores"), which supports Derek's direct-entry line; added the public-university/merit-scholarship claim the episode makes.
2. LIVE. Wrong fact: "That's shorter than one movie... / Way shorter." 2 hr 14 min plus a 10-minute break is about the length of a long movie with trailers, not way shorter. Now "That's like one long movie with all the trailers. / About that, yeah. Way shorter than the old paper test."
3. LIVE. Wrong statistic word: "a thousand thirty is the middle of the whole country." 1029 is the mean, not the median (and Ep 10 teaches the difference). Now "the national average." 1029 verified in the College Board 2025 Total Group report.
4. LIVE. Grammar in a teaching line: "Reading and Writing is short passages" now "uses short passages."
5. LIVE. Loose tool description: Bluebook has Mark for Review and an answer eliminator, not "a flag button and a little x". Now "a flag to mark it for review, and a tool to cross out choices."

Verified: timings, 400 to 1600, 75/25 split, unscored pretest items, Ep 2 and Ep 11 cross-references, one rodeo bit, one rating, one Kaden bus line, checks/sat-ep1.json.
Linters: render2 0 spliced; render.py ok, 1,260 words.

## Pass 3 (LIVE: line 28 needs re-render)

1. LIVE. Line 28, redundancy introduced by pass 2: "the national average total ... was one thousand twenty-nine. That's from College Board's own report. So roughly a thousand thirty is the national average." said the same fact twice in a row. Cut the last sentence; the line now ends "That's from College Board's own report." Kaden's "So anything over that is good?" still follows naturally.
2. Header only (no audio): line 16 says the test is "way shorter than the old paper test", which was not on the facts line. Added "the paper SAT it replaced in 2024 was 3 hours without the essay (College Board)".

Read in context, pass 2's other changes (lines 15 and 16 movie exchange, 51 "uses short passages", 53 Mark for Review wording) sound natural at speaking pace.
Verified: section timings and 2 hr 14 min; 400 to 1600; 1029 class of 2025 mean; Do No Harm wording against the facts line; middle-50 explanation is correct (a quarter below, a quarter above); Ep 2 and Ep 11 cross-references; placement check is "two questions from every skill" (placement.html); "Free official practice" button exists (assets/app.js); one Pono rodeo bit, one Derek rating, Kaden's bus pass line (the "cheat code" remark reads as slang, not the gag); checks/sat-ep1.json answers taught.
Linters: render2 0 spliced; render.py ok, 1,251 words, 4 voices.
