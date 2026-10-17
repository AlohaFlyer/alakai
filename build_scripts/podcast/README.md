# Podcast pipeline (SAT Notes / ACT Notes)

Engine: ElevenLabs only (decision 2026-10-16). Voices in cast.json are final; never change a voice_id once an episode is published.

House rule: only Coach Pono (hawaiian_native) says Hawaiian words and place names. Everyone else says the English (Big Island, the prep school up the road) or sounds out a respelling. render2.py refuses a script that breaks this.

1. Write `scripts/<test>-ep<N>.md` (format in render.py docstring: title line, `cast:`, `facts:`, `target_minutes:`, then `NAME: line`). Add `checks/<test>-ep<N>.json` with 3 questions. Pidgin only in banter; every teaching sentence in standard English. Any real place, hour, price or date goes on the `facts:` line, verified.
2. Lint: `python3 render.py scripts/sat-ep1.md --dry-run` (cast, voice count, lexicon) and `python3 render2.py scripts/sat-ep1.md --dry-run` (house rule, must say 0 spliced terms).
3. `.env` (gitignored) holds `ELEVENLABS_API_KEY=...` on the Mac clone only.
4. Render per line on eleven_v3: `python3 render2.py scripts/sat-ep1.md` (writes out/sat-ep1-v2/, resumable; TTS_SPEED defaults to 1.1).
5. Master with music and loudness: `./master.sh out/sat-ep1-v2 sat-ep1` (silence trim, atempo 1.08, slack key intro and outro from music/, loudnorm -16 LUFS) writes audio/sat-ep1.mp3.
6. Upload the master to R2: `CLOUDFLARE_API_TOKEN=... npx wrangler@4 r2 object put alakai-audio/<ep>.mp3 --file ../../audio/<ep>.mp3 --content-type audio/mpeg --remote` (token in .env on the Mac). Then `python3 publish.py` rebuilds data/episodes.json with https://audio.alakaitestprep.app/ URLs; mp3s are not committed.

Budget: roughly 1,300 words per episode is about 7,500 characters of TTS; an ElevenLabs Creator plan (100k characters per month) covers about 12 episodes a month.
