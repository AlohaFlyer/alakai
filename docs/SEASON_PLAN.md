# Season 1 plan: SAT Notes Podcast and ACT Notes Podcast

Revised 2026-10-16 after Ryan's review of Ep 1 of both shows. Fourteen episodes per show. Ep 0 is a development-only pronunciation episode and never publishes. Ep 1 of each show is live.

## Episode design rules (every episode)

1. One concept. If the outline has more than three teaching points, split the episode.
2. Open with a callback: Kaden gets asked one thing from the previous episode (retrieval). Thirty seconds, max.
3. One worked example the listener can hold in their head without seeing it: short stem, read twice, "pause it and try", then the walk-through.
4. One named trap from the app's trap list, said the way the app says it, so the listener recognizes it in the error log. The app's names: too extreme, half right, true but irrelevant, answers the wrong part, opposite, calculation slip, misread the question, stopped a step early, adds an assumption, near miss.
5. Kaden recaps in his own words at the end (retrieval again). Derek rates it.
6. Homework is a deep link, not a sentence: episodes.json carries `homework: {"label": "...", "href": "drill.html?skill=..."}` and the Notes page shows it as a button under the player.
7. Standard English for every teaching sentence; pidgin only in banter for local characters; only Coach Pono says Hawaiian words (render2.py enforces).
8. Facts go on the `facts:` header line and get checked by the reviewer against the official source named there. Fees and dates say "this year" and "check the official site".
9. 1,000 to 1,400 words (panels up to 1,700). Three to four voices; panels and Ep 0 use all five.
10. Every gag at most once per episode: Lehua's after-show plans (they rotate; see cast.json `places`: Costco, paddling at the harbor, the record store, Pac-Man at the pizza place, chocolate cake at the barbecue place, potato wedges at the gas station, the Saturday hike to the pond, the Christmas parade, hula practice, polo, the horses at the stable, dropping her dad at the airport, tennis or golf down the hill, Beach 69, boogie boarding at Kua Bay, a bike ride or Ironman cycling practice, soccer by the rodeo arena, the Saturday farmers markets, the Wednesday food trucks and the red barn grilled cheese, volleyball at the district park, sunset at the beach by the old hotel, an early swim at the big white-sand beach, a hike at the volcano; Lehua says the English, Pono says the Hawaiian place name if anyone does; Costco at most once per four episodes), Derek's rating out of ten (never a ten), Pono's rodeo metaphors, Sarah's commas, Kaden's bus, game, or car.

## Review rubric (a fresh agent grades every script before it renders)

Pass requires all of: facts match the named source; one concept; a pause-and-try example; a named trap; callback and recap present; homework link points at a real skill or section id; house rule and pidgin rule hold; length in range; no joke at a school's expense; no stereotypes; no medical advice (accommodations are described as "talk to your counselor about accommodations" only). Reviewer writes PASS or a numbered fix list to `build_scripts/podcast/review/<ep>.md`.

## SAT Notes Podcast

| # | Title | Concept | Example | Trap | Homework |
|---|---|---|---|---|---|
| 0 | How We Say Things | dev only | | | |
| 1 | How This Test Actually Works (live) | structure, adaptive modules, scores, no blanks | | | placement.html |
| 2 | Crossing Out: how to find the wrong answers | elimination beats guessing; the 6 trap types the app names | a Words in Context item with a "right idea, wrong word" distractor | Opposite | drill.html?section=rw |
| 3 | The Time Squeeze (rendered) | two-pass, checkpoints, module 1 accuracy | | | timed.html |
| 4 | Desmos Is Your Co-pilot | graph to solve systems and quadratics; when typing is slower than algebra | system of two linear equations, "where do they cross" | Answers the wrong part | drill.html?skill=math-alg-systems |
| 5 | Read the Question First | Words in Context and Central Ideas: predict, then match | one-paragraph stem, predict the word before looking at choices | Too extreme | drill.html?skill=rw-cs-words |
| 6 | The Smallest Step | Inference and Command of Evidence, including the chart questions | "which choice most logically completes" with a one-step inference | Adds an assumption | drill.html?skill=rw-ii-inference |
| 7 | Where the Sentence Breaks | Boundaries: independent vs dependent clause, comma, semicolon, colon, dash | a two-clause sentence, pick the punctuation | Near miss | drill.html?skill=rw-sec-boundaries |
| 8 | However, Therefore, For Example | Transitions by relationship, plus the "notes" rhetorical synthesis questions | two sentences, name the relationship, then pick | Opposite | drill.html?skill=rw-ei-transitions |
| 9 | Lines Are Rates | linear equations, slope as rate, systems, plug in and backsolve | word problem with a rate and a starting value | Calculation slip | drill.html?skill=math-alg-linear-fn |
| 10 | Percent, Ratio, and the Mean vs the Median | percent change, units in ratios, mean vs median, exponential vs linear growth | "price goes up 20% then down 20%" | Misread the question | drill.html?skill=math-psda-percent |
| 11 | Quadratics and the Reference Sheet | vertex and factored forms, what is on the reference sheet, SOH CAH TOA, grid-in rules | a quadratic in vertex form, read the max | Answers the wrong part | drill.html?skill=math-adv-quadratics |
| 12 | The Error Log Habit | careless vs concept vs time, redo in 3 days, the weekly plan, Blitz | a real-sounding wrong answer, sort it into the three buckets | Calculation slip | dashboard.html |
| 13 | The Last Seven Days | Bluebook full length, sleep, what to bring, the drive to the test center, PSAT in October for juniors | | | timed.html |
| 14 | Listener Questions | National Merit, superscore, how many times, test optional, fee waivers, nerves, reading speed, accommodations (counselor only), studying with a job | | | settings.html (send a report) |

## ACT Notes Podcast

| # | Title | Concept | Example | Trap | Homework |
|---|---|---|---|---|---|
| 0 | How We Say Things, ACT edition | dev only | | | |
| 1 | How the ACT Works (live) | sections, Composite, optional Science, superscore, MyACT | | | placement.html |
| 2 | SAT or ACT? | decide with one practice test of each: pacing, calculator on all math, Science, reading style | | | timed.html |
| 3 | Forty-Two Seconds | per-section pacing, checkpoints, two-pass, no blanks | | | timed.html |
| 4 | Where the Sentence Breaks, ACT edition | punctuation and boundaries, the biggest point pool in English | two-clause sentence, pick the punctuation | Near miss | drill.html?skill=english-punct |
| 5 | Shorter Is Usually Right | agreement, pronouns, tense, modifiers, redundancy | a sentence with a dangling modifier | Near miss | drill.html?skill=english-grammar |
| 6 | What Is This Sentence For? | transitions, purpose questions, add or delete, order | "which choice best accomplishes" with a stated goal | True but irrelevant | drill.html?skill=english-strategy |
| 7 | Backsolve, Plug In, Move On | pre-algebra and algebra: percents, ratios, linear, systems | a word problem solved by backsolving from the middle choice | Misread the question | drill.html?skill=math-algebra |
| 8 | Functions and the Grid | functions, quadratics, coordinate geometry, calculator discipline | read a function value off a described graph | Answers the wrong part | drill.html?skill=math-coordinate |
| 9 | The Last Ten | geometry, trig, the time sinks to skip, the short formula list to memorize (no sheet on the ACT) | SOH CAH TOA with a 3-4-5 triangle | Half right | drill.html?skill=math-trig |
| 10 | Four Passages, One Plan | passage types, order, stems first vs skim first, line references, paired passages | one short stem with a line reference | Too extreme | drill.html?section=reading |
| 11 | It Is a Graph, Not Biology | find the variable, read the trend, mind the units, conflicting viewpoints | a described two-line graph, which goes up faster | Misread the question | drill.html?section=science |
| 12 | The Error Log Habit, ACT edition | careless vs concept vs time, redo in 3 days, weekly plan, Blitz | | Calculation slip | dashboard.html |
| 13 | The Last Seven Days, ACT edition | full practice test, sleep, what to bring, online vs paper, MyACT score sending | | | timed.html |
| 14 | Listener Questions | retakes, superscore, fee waivers, test optional, the Science decision, taking both, nerves, studying with a job | | | settings.html |

## Pipeline

write (2 agents) -> review (1 fresh agent, rubric above) -> fix -> lint (render.py and render2.py dry runs) -> Ryan approves -> render on the Mac -> master -> approved.json -> publish.py -> push.

## Backlog: Season 2 (college path), added 2026-10-16

Ryan's list, to plan later. Same cast, same format, probably a third show or a "College Notes" tag inside both:

- Scoir (how HPA and other Big Island schools use it, what to keep updated)
- Common App (timeline, essay, activities list, recommenders)
- Scholarships (local: Hawaiʻi Community Foundation, Kamehameha Schools, Pauahi; national; how to search without paying)
- Financial aid (FAFSA, CSS Profile, net price calculators, what "meets full need" means)
- How to choose a university (fit, cost, distance from home, mainland vs UH, transfer paths)
- Sports scholarships (NCAA eligibility center, divisions, how recruiting really works for island athletes)
- How to pick a program or major (undeclared is fine, prerequisites, what changes later)
