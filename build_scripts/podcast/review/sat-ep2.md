# sat-ep2 review, pass 1

1. By-ear example: the stem says "unusually blank", and a listener can hear "blank" as a real word meaning expressionless. Sarah now sets the rule first: "When I say 'blank,' that's the missing word."
2. Flat or confusing line: Kaden's "that's actually kind of hard" (slang for cool) reads as "difficult" in a lesson about odds. Changed to "kind of fire".
3. Comma gag logic: Sarah "was in the group chat" of Lehua's auntie, which only makes sense if they are family. Now Lehua screenshotted it for Sarah, and Sarah "texted her back with the comma."
4. Missing checks file. Wrote checks/sat-ep2.json (when to cross out, naming the Opposite trap from the worked example, the odds after two cross-outs). Each answer is taught in the episode.

Verified: the six trap names match assets/engine.js TRAP_NAMES wording; "You crossed out the right answer" message exists (engine.js line 78); the odds arithmetic is correct; callback, pause-and-try, named trap (Opposite), recap and rating are all present; each gag appears once; homework section id `rw` exists.

Linters: render2 0 spliced; render.py ok, 1,286 words.

## Pass 2

1. Comma gag logic (introduced in pass 1): Sarah "texted back" Lehua's auntie and was "left on read," which implies a private chat she is not in. Now the auntie posted it on her page, Sarah commented with the comma, and the auntie deleted the comment.

Verified: ten trap names and the six listed match engine.js TRAP_NAMES; "You crossed out the right answer" message (engine.js line 78); the app's cross-out button is a × beside each choice; odds arithmetic; worked example has one defensible answer (B); recap lists the six in the order taught; one rating, one comma bit, one Kaden game line; section id rw exists; checks answers taught.
Linters: render2 0 spliced; render.py ok, 1,283 words.

## Pass 3

PASS. No changes.

Verified by ear: Sarah sets up "blank" before the stem, the stem is one sentence read twice with choices, and the walk-through crosses out A (opposite, named trap), then D, then separates timid (right idea, wrong word, matching SEASON_PLAN's example spec) from diplomatic. One defensible answer (B). Odds arithmetic (1 in 4, 1 in 3, 1 in 2; one in two is twice a blind guess) correct. Ten trap names in engine.js, six listed in app wording and recapped in the same order. One comma bit (pass 2 version is logical), one rating, one Kaden game line, no Lehua place. Ep 3 outro cross-reference; drill.html reads ?section= and rw exists; checks answers taught.
Linters: render2 0 spliced; render.py ok, 1,283 words, 4 voices.
