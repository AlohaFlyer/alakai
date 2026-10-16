# alakai-ping (Cloudflare Worker)

The only server-side piece of alakaitestprep.app. `POST /ping {school, grade}` increments an aggregate monthly counter in KV. Nothing else is stored: no bodies, IPs, user agents or per-event timestamps. `GET /stats` with `Authorization: Bearer <STATS_TOKEN>` returns the counters.

## Deploy (Ryan, on the Mac, wrangler logged in as ryanpettit@gmail.com)

```
cd worker/alakai-ping
npx wrangler@4 kv namespace create PINGS          # paste the id into wrangler.toml
npx wrangler@4 secret put STATS_TOKEN             # any long random string
npx wrangler@4 deploy
```

The custom domain `ping.alakaitestprep.app` is created by wrangler on deploy (zone must be on the same Cloudflare account). Allowed origins are listed at the top of worker.js.

## Read the counters
```
curl -H "Authorization: Bearer <STATS_TOKEN>" https://ping.alakaitestprep.app/stats
```
Keys look like `2026-10|hpa|11`.
