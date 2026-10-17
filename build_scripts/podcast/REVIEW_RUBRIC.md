# Script review rubric

Grade each script in build_scripts/podcast/scripts/*.md. Write build_scripts/podcast/review/<stem>.md containing either `PASS` or a numbered fix list. A script passes only if every item holds:

1. Facts: every number, date, fee, policy and section length matches the source named on the `facts:` line and current official practice (digital SAT: RW 2 x 27 q x 32 min, Math 2 x 22 q x 35 min, 400 to 1600, adaptive by module; enhanced ACT 2025: English 50 q 35 min, Math 45 q 50 min, Reading 36 q 40 min, Science optional 40 q 40 min, Composite = mean of E, M, R; no guessing penalty on either). Flag anything stated as fact that is not on the facts line.
2. One concept per episode (at most three teaching points that serve it).
3. A callback to the previous episode in the first minute (Ep 1 excepted).
4. A pause-and-try worked example: the stem is read, the listener is told to pause, then the walk-through. The stem must be short enough to hold without seeing it.
5. A trap named with the app's wording: too extreme, half right, true but irrelevant, answers the wrong part, opposite, calculation slip, misread the question, stopped a step early, adds an assumption, near miss.
6. Kaden (or the student) recaps at the end; Derek rates it (never a ten).
7. A `homework:` header line with a label and an href that points at a real page or a real skill or section id from data/<test>/skills.json.
8. House rule: no Hawaiian word or place name from lexicon.json in any non-Pono line (render2.py --dry-run must print 0 spliced terms). Pidgin only in banter and only for local characters; every teaching sentence is standard English.
9. Length 1,000 to 1,400 words (panels up to 1,700); 3 to 5 voices.
10. Tone: school-safe, local and Gen Z humor, no stereotypes, no joke at any school's expense, no medical advice (accommodations: "talk to your counselor" only), no branded prep-company names.
11. Teaching matches data/strategies.json and the app's features (eliminator x, flag, placement check, drills, Blitz, timed, error log, weekly plan, Strategies tab, official practice button, Science toggle).
