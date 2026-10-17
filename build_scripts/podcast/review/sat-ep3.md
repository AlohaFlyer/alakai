# sat-ep3 review, pass 1 (episode was already rendered: re-render needed)

1. House rule: Lehua opened with "Aloha", Derek said "Pau", Lehua closed with "Mahalo". All are Hawaiian words in non-Pono lines. render2 missed them because its term match is case-sensitive against lowercase lexicon keys (see report). Replaced with "Hey, welcome back", removed "Pau.", and changed "Mahalo" to "Thanks for listening".
2. Missing facts: line. Added one covering timings, per-question seconds, adaptive modules, no guessing penalty, Bluebook tools and countdown clock, and checkpoint targets sourced to timing.html and strategies.json.
3. Missing homework line. Added `homework: Do one timed module | timed.html`.
4. No callback (design rule 2). Added a 3-line warm-up near the top: when are you allowed to cross out (Ep 2). The repeated cross-out lecture later was cut to two lines that point back to it.
5. No Kaden recap or Derek rating at the end (rubric 6). Added a recap; moved Derek's one rating ("Seven. / Why not higher? / Nothing's higher.") there from the mid-episode "read the last sentence first" tip.
6. Gag overuse: Pono had five rodeo/horse bits. Kept the central "clock is a horse" setup plus its "fighting the horse" tie-in. Cut "brand before you buy the cow", "ahead on a horse", and "ride the first horse clean" (which also repeated Ep 1's rodeo draw). Kaden's bus appeared three times. Opening changed to "My alarm was early", the mid-episode bus mention was removed, and the closing "It left. / Should've flagged it." payoff was kept.
7. Pidgin in a teaching sentence: Pono's "You got time left, you go back to the flags" is now "If you have time left, go back to the flags."
8. Checkpoint times were given as elapsed time, but Bluebook counts down. Added "Those are minutes used. The Bluebook clock counts down, so do that subtraction once before test day."
9. Strategy mismatch: "Being ahead means you're probably rushing" was stronger than timing.html ("speed is not the problem"). Now "Ahead is not bad. Ahead and careless is bad... use the extra time to read every word."
10. Inaccurate: "Module one is the same difficulty for everybody" is now "a mix of easy, medium, and hard questions for everybody" (matches Ep 1).
11. Overstated math: "a quarter of a point on average" was duplicated with the cross-out odds. Simplified to "A guess at least has a chance."
12. target_minutes 11 changed to 8 (1,275 words is about 8.5 min). Outro now names Ep 4 (Desmos).

Linters: render2 0 spliced; render.py ok, 1,275 words. checks/sat-ep3.json answers are all still taught.

## Pass 2

1. Gag logic (introduced in pass 1): Derek's "Seven. / Why not higher? / Nothing's higher." contradicts Ep 2, where he gave a nine. Now "You left out reading the question first," which is true of Kaden's recap.
2. Wrong arithmetic: "Almost have it for one more minute is three questions you never saw." At 71 s per RW question, one minute is less than one question. Now "Three more minutes on that one question is two or three questions you never reach."
3. Flat teaching line (pass 1 wording): "Ahead is not bad. Ahead and careless is bad. Speed is not the problem, so..." Now "Ahead is fine. Ahead and careless is the problem. So use the extra time to read every word."
4. Concept creep: the read-the-question-first block is Ep 5's concept. Kept it as a time leak and added the cross-reference "That gets a whole episode of its own, episode five."

Verified: checkpoint targets match timing.html (RW 9 at 10:40, 18 at 21:20; Math 7 at 11:40, 15 at 23:20) and are one-third and two-thirds of each module's clock; ten-second rule from timing.html; timed.html runs checkpoints by default; Ep 4 cross-reference; checks answers taught.
Linters: render2 0 spliced; render.py ok, 1,286 words.
