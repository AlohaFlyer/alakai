# sat-ep5 review, pass 1

1. Strategy gap: data/strategies.json rw-cs-words step 4 is "Plug your pick back in and reread," and the homework points listeners to that Strategies tab, but the walk-through skipped the step. Added: "Plug it back in. 'The plants proved surprisingly resilient, surviving three frosts with little damage.' Reads right."
2. Comma gag logic: "talking about my mom like she was finished" made no sense (the brother's mom is her mom too, and the comma does not change that reading). Now "or if he was calling himself a done mom."
3. Gag overuse: Kaden's bus appeared at the open and again at the close. Kept the opening; replaced the closer with "Kaden, prediction for your rating next episode? / Eight. / Don't predict my ratings." (a callback, not a second rating).
4. Missing checks file. Wrote checks/sat-ep5.json (predict before choices, why "indestructible" is too extreme, too narrow on Central Ideas).
5. Facts line: sourced the plug-back-in and read-question-first steps to strategies.json.

Verified: callback matches Ep 4; outro cross-reference to Ep 6 matches the plan; trap wording matches engine.js; skill id rw-cs-words exists; central-idea advice matches rw-ii-central.

Linters: render2 0 spliced; render.py ok, 1,101 words.

## Pass 2

1. Comma gag (pass 1 wording): "calling himself a done mom" did not land, and the comma it hinged on was a direct-address comma, the same joke as Ep 2's "let's eat grandma". Replaced with a list-comma joke from her mom, matching the cast.json gag: "Pick up milk eggs and rice." / "I asked her what a milk egg is." / "She sent the list again. Same list. Still no commas."
2. Imprecise definition in a teaching line: too broad "means it's about the whole topic in the world" now "means it covers more than this passage actually says."
3. Wrong analogy: "It's like checking your work in math" (predicting comes before, not after). Now "Same in math. You want your own number before you look at theirs."

Verified: worked example has one defensible answer (B, resilient); too extreme matches engine.js; steps match strategies.json rw-cs-words and rw-ii-central; Ep 4 callback and Ep 6 cross-reference; one Kaden bus line, one rating; checks answers taught.
Linters: render2 0 spliced; render.py ok, 1,082 words.

## Pass 3

PASS. No changes.

Verified by ear: the stem is read twice with no choices, the listener predicts, then the choices are read twice; resilient is the only defensible answer and indestructible is a clean too-extreme trap tied to "with little damage." Plug-back-in step matches strategies.json rw-cs-words. Too narrow and too broad are taught, so checks/sat-ep5.json question 3 has one answer. Callback to Ep 4 trap; Ep 6 cross-reference matches SEASON_PLAN.md. One bus line, one comma bit (list comma, distinct from Ep 2's direct-address joke), one rating; no Lehua place. rw-cs-words exists.
Linters: render2 0 spliced; render.py ok, 1,082 words, 4 voices.
