# Podcast pipeline (SAT Notes / ACT Notes)

1. Write the script in `scripts/<test>-ep<N>.md` (format in render.py docstring). Add a `checks/<test>-ep<N>.json` with 3 questions.
2. `python3 render.py scripts/sat-ep0.md --dry-run` must pass (cast, voice count, lexicon).
3. Put keys in `.env` (gitignored): `ELEVENLABS_API_KEY=...` and optionally `CARTESIA_API_KEY=...`.
4. Pick voices once: ElevenLabs voice library, one per character, paste each `voice_id` into cast.json. Never change them later.
5. `python3 render.py scripts/sat-ep0.md` then `./master.sh out/sat-ep0-elevenlabs sat-ep0`.
6. `python3 publish.py` rebuilds data/episodes.json. With R2: upload `audio/*.mp3` to the bucket and run with `AUDIO_BASE=https://audio.alakaitestprep.app/`.

Cartesia A/B: add `cartesia_voice_id` per character, `python3 render.py scripts/sat-ep0.md --engine cartesia`, `./master.sh out/sat-ep0-cartesia sat-ep0-cartesia`.
