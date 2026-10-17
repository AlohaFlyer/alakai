# Launch checklist (P8 to P10)

Ryan-at-keyboard items, in order. Each is one-time.

1. **GitHub repo**: AlohaFlyer/alakai, branch master, Pages live (done 2026-10-16).
2. **Episodes**: Ep 0 and Ep 3 are rendered (ElevenLabs, house rule). Remaining episodes render on the Mac clone per `build_scripts/podcast/README.md`, a few per month as ElevenLabs credits allow; publish.py lists unrendered ones as Coming soon.
3. **Icons**: done (horse mark; per-school home screen icons regenerate with `python3 build_scripts/icons/build_school_icons.py` if schools.json changes).
4. **Domain**: alakaitestprep.app registered at Cloudflare 2026-10-16, auto-renew on.
5. **GitHub Pages**: master root, custom domain, HTTPS enforced (done).
6. **DNS at Cloudflare**: `@` and `www` CNAME to alohaflyer.github.io, DNS only (done). audio and ping subdomains are managed by R2 and the Worker.
7. **Worker**: deployed 2026-10-17 at ping.alakaitestprep.app (KV namespace in wrangler.toml). Read counts: `curl -H "Authorization: Bearer $STATS_TOKEN" https://ping.alakaitestprep.app/stats` with STATS_TOKEN from the Mac clone's build_scripts/podcast/.env. Redeploy: `cd worker/alakai-ping && CLOUDFLARE_API_TOKEN=... npx wrangler@4 deploy`.
8. **Audio hosting**: R2 bucket `alakai-audio` serving at audio.alakaitestprep.app (done 2026-10-17). Upload per episode with wrangler (see build_scripts/podcast/README.md); mp3s are not committed.
9. **Cultural review**: send `docs/DESIGN_NOTES.md` (border patterns) and the Disclosures text to a Hawaiian cultural practitioner. Ryan sends. Bars stay solid until sign-off anyway.
10. **Verify live**: `bash build_scripts/verify/all.sh` green locally, then open the live site on a phone, run onboarding, one drill, one Blitz round, Send report, confirm the mailto opens.

Register: t1062 on homeofficemanager.app.
