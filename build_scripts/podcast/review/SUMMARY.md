# Review summary, 2026-10-16 (three passes, fresh Opus reviewer each pass)

| Script | Words | Voices | Fixes pass 1 / 2 / 3 | Verdict |
|---|---|---|---|---|
| sat-ep0 (dev only) | 778 | 5 | 7 / 3 / 0 | PASS |
| sat-ep1 (live) | 1,251 | 4 | 6 / 5 / 2 | PASS, re-rendered |
| sat-ep2 | 1,283 | 4 | 4 / 1 / 0 | PASS, awaiting Ryan's approval to render |
| sat-ep3 | 1,286 | 4 | 12 / 4 / 0 | PASS, needs full re-render |
| sat-ep4 | 1,164 | 4 | 5 / 1 / 0 | PASS, awaiting approval |
| sat-ep5 | 1,082 | 4 | 5 / 3 / 0 | PASS, awaiting approval |
| act-ep1 (live) | 1,118 | 5 | 9 / 6 / 2 | PASS, re-rendered |

Headline fixes: ACT fee $65 -> $70 (act.org); "21 is the middle" -> class of 2025 average 19.4; SAT 1029 is the mean, not the median; "shorter than a movie" was false (2 h 14 min plus a break); "one more minute is three questions" arithmetic (script and app); mechanical pencils are banned on the paper ACT; Hawaiian words in non-Pono lines in Ep 3 (linter made case-insensitive); cross-references realigned to SEASON_PLAN.md; gag collisions (five rodeo bits in one episode); missing callbacks, recaps, ratings, homework lines and checks.

Verified sources: act.org/gradclass2025; reports.collegeboard.org 2025 total group report; manoa.hawaii.edu/admissions/freshman (Do No Harm); hilo.hawaii.edu/admissions/freshman.php (accepts ACT/SAT); act.org fees and fee waivers; act.org understanding-your-scores (Science and STEM reporting); act.org test day ID page (pencils).

Open, non-blocking: act-ep1 "some schools and scholarships still look for Science" is soft advice without a source. Per-pass detail is in review/<stem>.md.

## SAT Ep 6 to 14

Three passes, 2026-10-16. Words and voices from render.py --dry-run; both linters clean on all nine (render2 0 spliced).

| Script | Words | Voices | Fixes pass 1 / 2 / 3 | Verdict |
|---|---|---|---|---|
| sat-ep6 | 1,208 | 4 | 1 / 0 / 0 | PASS, awaiting Ryan's approval to render |
| sat-ep7 | 1,156 | 4 | 5 / 1 / 0 | PASS, awaiting approval |
| sat-ep8 | 1,132 | 4 | 5 / 0 / 0 | PASS, awaiting approval |
| sat-ep9 | 1,200 | 4 | 3 / 0 / 1 | PASS, awaiting approval |
| sat-ep10 | 1,159 | 4 | 2 / 1 / 0 | PASS, awaiting approval |
| sat-ep11 | 1,209 | 4 | 4 / 0 / 0 | PASS, awaiting approval |
| sat-ep12 | 1,066 | 4 | 1 / 0 / 0 | PASS, awaiting approval |
| sat-ep13 | 1,144 | 4 | 4 / 2 / 0 | PASS, awaiting approval |
| sat-ep14 (panel) | 1,384 | 5 | 6 / 2 / 2 | PASS, awaiting approval (est 9.2 min vs 8 target) |

Pass 3 changes: Ep 9 got a worked plug-in number (t = 2, target 34, 40 - 3t hits, 40 + 3t misses). Ep 14 trimmed 55 words of banter and dropped a second comma bit. Lehua's places Ep 4 to 14 never repeat (Costco, record store, paddling, Pac-Man, food trucks, pond, cake, volleyball, airport, sunset). Ratings run 8 to 9, never ten. Every callback and next-episode line matches SEASON_PLAN.md.


## ACT Ep 0, 2 to 14

Three passes, 2026-10-16. Words and voices from render.py --dry-run after pass 3; both linters clean on all fourteen (render2 0 spliced).

| Script | Words | Voices | Fixes pass 1 / 2 / 3 | Verdict |
|---|---|---|---|---|
| act-ep0 (dev only) | 725 | 5 | 3 / 1 / 0 | PASS, awaiting Ryan's approval to render |
| act-ep2 | 1,164 | 4 | 5 / 1 / 0 | PASS, awaiting approval |
| act-ep3 | 1,102 | 4 | 4 / 0 / 0 | PASS, awaiting approval |
| act-ep4 | 1,074 | 4 | 5 / 0 / 1 | PASS, awaiting approval |
| act-ep5 | 1,126 | 4 | 7 / 0 / 0 | PASS, awaiting approval |
| act-ep6 | 1,073 | 4 | 6 / 0 / 0 | PASS, awaiting approval |
| act-ep7 | 1,052 | 4 | 4 / 0 / 0 | PASS, awaiting approval |
| act-ep8 | 1,079 | 3 | 4 / 0 / 0 | PASS, awaiting approval |
| act-ep9 | 1,051 | 4 | 4 / 0 / 1 | PASS, awaiting approval |
| act-ep10 | 1,094 | 4 | 3 / 1 / 0 | PASS, awaiting approval |
| act-ep11 | 1,118 | 4 | 5 / 0 / 0 | PASS, awaiting approval |
| act-ep12 | 1,075 | 4 | 3 / 0 / 2 | PASS, awaiting approval |
| act-ep13 | 1,190 | 4 | 6 / 1 / 0 | PASS, awaiting approval |
| act-ep14 (panel) | 1,430 | 5 | 4 / 0 / 1 | PASS, awaiting approval (est 9.5 min vs 9 target) |

Pass 3 changes (5 script edits in 4 scripts, plus checks/act-ep12.json): Ep 4 "hood up again" replaced with a callback to Ep 3's "eyes still loading"; Ep 12 stem no longer says "by accident", so Kaden has to reason from setup, time and size to Careless and calculation slip (checks reworded to match); Ep 9 triples rule now requires the biggest number of the set to be the long side; Ep 14 recap now states the superscore as best English, Math and Reading from any dates. Lehua's places Ep 0 to 14 never repeat (paddling, Costco, record store, Ironman cycling, cake, pond, volleyball, wedges, Pac-Man, golf, airport, Beach 69, food trucks, volcano, sunset); Costco once. Ratings run 7 to 9, never ten. One rodeo bit per Pono episode. Every callback and next-episode line matches SEASON_PLAN.md and live Ep 1 (pace is episode three, SAT vs ACT is episode two, Science is episode eleven). Every homework href resolves to a real page, skill id or section id.
