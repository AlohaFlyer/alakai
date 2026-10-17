# act-ep12 review, pass 1

1. Weak size check: "Twenty percent of sixty should be a small part of sixty," but 18 is also a small part, so it would not catch the slip. Now "Twenty percent is one fifth, so the answer should be a fifth of sixty. Eighteen is almost a third."
2. App behavior overstated: "It always puts in a timed module every week." dashboard.html adds one only when no timed module was done in the past 6 days. Now "If you haven't done a timed module in the past week, it adds one." Facts line corrected.
3. Facts line: added the fifth and third arithmetic.

Verified: 0.2 x 60 = 12; 0.3 x 60 = 18 (0.3, just under 1/3); the buttons Careless, Didn't know it and Rushed (engine.js askCause); redo due 3 days later and Mastered needs a correct redo (engine.js); "ran out of time" label; This week box; full-length test at 11 to 14 and 1 to 3 days out; Blitz 60 s, 8 s a card (quiz.html); calculation slip (plan trap); food trucks place on Wednesday; rating 8; Kaden's game line once.
Linters: render2 0 spliced; render.py ok, 1,074 words.


## Pass 2

PASS

Re-verified against the app: askCause buttons Careless / Didn't know it / Rushed (engine.js line 113); redo due 3 days later (engine.js line 103); Mastered needs a correct redo; This week plan, timed module after 6 days, full test at 11 to 14 and 1 to 3 days out, Blitz two rounds (dashboard.html); 60 s, 8 s a card (quiz.html); 0.2 x 60 = 12, 0.3 x 60 = 18; checks/act-ep12.json matches.
