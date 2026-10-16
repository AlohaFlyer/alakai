# Launch checklist (P8 to P10)

Ryan-at-keyboard items, in order. Each is one-time.

1. **GitHub repo**: create `AlohaFlyer/alakai` (public, empty, no README) at github.com/new. Then Claude pushes `main`.
2. **ElevenLabs key**: `build_scripts/podcast/.env` on the Mac clone (done via pbpaste). Render pilots: `python3 build_scripts/podcast/render.py build_scripts/podcast/scripts/sat-ep0.md`, same for ep3, then `./build_scripts/podcast/master.sh out/sat-ep0-elevenlabs sat-ep0`, and `python3 build_scripts/podcast/publish.py`.
3. **Cartesia A/B** (optional): free key at cartesia.ai, add `CARTESIA_API_KEY` to `.env`, add `cartesia_voice_id` per character in cast.json, render ep0 with `--engine cartesia`.
4. **Domain**: buy alakaitestprep.app at Cloudflare Registrar (same account as ha330pilot.app).
5. **GitHub Pages**: repo Settings, Pages, deploy from `main` root. Custom domain alakaitestprep.app (CNAME file is already in the repo). Enforce HTTPS once the cert issues.
6. **DNS at Cloudflare**: CNAME `alakaitestprep.app` to `alohaflyer.github.io` (proxied off until Pages cert issues, then on), CNAME `www` same.
7. **Worker**: `cd worker/alakai-ping && npx wrangler@4 kv namespace create PINGS` (paste id into wrangler.toml), `npx wrangler@4 secret put STATS_TOKEN`, `npx wrangler@4 deploy`. Creates ping.alakaitestprep.app.
8. **Audio hosting**: either commit `audio/*.mp3` (simple, repo grows ~5 MB per episode) or create R2 bucket `alakai-audio`, connect custom domain `audio.alakaitestprep.app`, set `AUDIO_BASE=https://audio.alakaitestprep.app/` when running publish.py.
9. **Cultural review**: send `docs/DESIGN_NOTES.md` (border patterns) and the Disclosures text to a Hawaiian cultural practitioner. Ryan sends. Bars stay solid until sign-off anyway.
10. **Verify live**: `bash build_scripts/verify/all.sh` green locally, then open the live site on a phone, run onboarding, one drill, one Blitz round, Send report, confirm the mailto opens.

Register: t1062 on homeofficemanager.app.
