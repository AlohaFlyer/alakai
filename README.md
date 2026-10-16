# Alakaʻi Test Prep (alakaitestprep.app)

Free, no-login SAT and ACT prep for Hawaiʻi Island high schoolers. Static site on GitHub Pages behind Cloudflare DNS, same pattern as ha330pilot.app. Everything a student does stays in their browser; the only server-side piece is `worker/alakai-ping` (an anonymous school-and-grade counter).

Plan: HPA Project doc `claude/ALAKAI_TEST_PREP_PLAN_v1.0.md`. Content schema: `docs/BANK_SCHEMA.md`. Palette derivations: `docs/PALETTE_NOTES.md`. Credits: `docs/CREDITS.md`.

## Layout
- `*.html` pages, `assets/` css/js/patterns/hero, `data/` banks and config, `sw.js` offline shell.
- `build_scripts/verify/` checks: `contrast.py`, `keys.py`, `links.py`, `smoke.py`. Run `bash build_scripts/verify/all.sh` before every push.
- `build_scripts/podcast/` ElevenLabs Text-to-Dialogue pipeline, cast and lexicon.
- `worker/alakai-ping/` Cloudflare Worker.

## Local
`python3 -m http.server 8765` from the repo root, open http://localhost:8765/.
