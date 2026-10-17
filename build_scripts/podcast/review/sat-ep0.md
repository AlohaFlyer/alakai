# sat-ep0 review, pass 1

1. Cross-reference: "We are doing math, Kaden. Episode four." Ep 4 is Desmos in SEASON_PLAN.md. Changed to "Math starts soon, Kaden. Episode four is the built-in graphing calculator."
2. Pronunciation claim: "Four little syllables and that ʻokina in the middle" contradicted Kaden's three-beat respelling (hah-VAI-ee), and the ʻokina sits before the final vowel, not in the middle. Changed to "And that ʻokina before the last ee, that little catch".
3. Overstated fact: "the PSAT you take junior year can get you scholarship money" changed to "is the one that can qualify you for National Merit scholarships".
4. Unsourced claim: "The kid who built the app we're sitting inside of goes there." Not supported by any facts entry. Replaced with "The app starts out in their red and white" (default palette per docs/SCHOOL_PALETTES.md).
5. Missing homework line. Added `homework: Take the placement check | placement.html`, and the outro now says "Go take the placement check" instead of "Go do three drills".
6. Gag rotation: Ep 0 and Ep 4 both used the Costco run. Ep 0 now uses the early swim at the big white-sand beach (Lehua says the English; Pono says Hāpuna). Kaden's bus is the only Kaden gag in the episode.
7. Facts line rewritten to cover what the episode actually states (SAT name, PSAT/NMSQT, Bluebook, Khan Academy, Hāpuna, app palette); the old Costco entry was removed with the Costco gag.

Linters: render2 0 spliced terms; render.py dry run ok, 769 words (Ep 0 allowance ~770).

## Pass 2

1. Gag overuse: Derek gave two ratings ("Four out of ten" and "Eight out of ten for honesty"). Kept the first; the second is now "Agreed. But at least it's honest about it." Line 49 ("when I rate your shortcut a six") stays as the gag's introduction, alongside Pono's and Sarah's.
2. Wrong fact: "Blue book, two words, one app." Bluebook is one word. Now "You say it like two words, blue book, but it's one word and one app."
3. Punctuation: "What is an S-A-T even." now ends with a question mark.

Verified: Ep 4 cross-reference, HPA red default and Konawaena kelly green (docs/SCHOOL_PALETTES.md), Hāpuna said only by Pono, one Kaden bus gag, checks/sat-ep0.json answers all taught.
Linters: render2 0 spliced; render.py ok, 778 words.

## Pass 3

PASS. No changes.

Verified: Ep 4 and Ep 1 cross-references match SEASON_PLAN.md; ʻokina placement and respellings (Kaden's Hah-VAI-ee and Koh-nah-WY-nah are sounding-out respellings, allowed); every Hawaiian place and word is in a Pono line (case-insensitive scan, only character names in other lines); HPA red-and-white default and Konawaena green per docs/SCHOOL_PALETTES.md; one Derek rating ("Four out of ten"; line 49 is the gag intro, not a rating); one Kaden bus bit; Lehua's place (early swim at the big white-sand beach, Pono says Hāpuna) is used nowhere else in SAT Eps 0 to 5; checks/sat-ep0.json answers all taught; school-safe.
Linters: render2 0 spliced; render.py ok, 778 words, 5 voices.
