/* alakai-ping: the one server-side piece of Alakaʻi Test Prep.
   POST /ping {school, grade} -> increments an aggregate counter in KV. Stores counts only.
   GET  /stats (Authorization: Bearer STATS_TOKEN) -> JSON of counters.
   No request bodies, IPs, user agents, or timestamps per event are stored. */

const ALLOWED_ORIGINS = ['https://alakaitestprep.app', 'https://www.alakaitestprep.app', 'http://localhost:8765'];
const GRADES = new Set(['9', '10', '11', '12', 'other', '']);

function cors(origin) {
  const ok = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return { 'Access-Control-Allow-Origin': ok, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400' };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });

    if (url.pathname === '/ping' && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch (e) { return new Response('bad json', { status: 400, headers: cors(origin) }); }
      const school = String(body.school || '').toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 32);
      const grade = String(body.grade || '').slice(0, 5);
      if (!school || !GRADES.has(grade)) return new Response('bad fields', { status: 400, headers: cors(origin) });
      const month = new Date().toISOString().slice(0, 7);
      const key = `${month}|${school}|${grade || 'na'}`;
      // KV has no atomic increment; this is a best-effort counter, which is fine for "which schools use this".
      const cur = parseInt((await env.PINGS.get(key)) || '0', 10);
      await env.PINGS.put(key, String(cur + 1));
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json', ...cors(origin) } });
    }

    if (url.pathname === '/stats' && request.method === 'GET') {
      const auth = request.headers.get('Authorization') || '';
      if (!env.STATS_TOKEN || auth !== `Bearer ${env.STATS_TOKEN}`) return new Response('unauthorized', { status: 401 });
      const out = {}; let cursor;
      do {
        const page = await env.PINGS.list({ cursor });
        for (const k of page.keys) out[k.name] = parseInt((await env.PINGS.get(k.name)) || '0', 10);
        cursor = page.list_complete ? null : page.cursor;
      } while (cursor);
      return new Response(JSON.stringify(out, null, 2), { headers: { 'Content-Type': 'application/json' } });
    }

    return new Response('alakai-ping', { status: 404 });
  }
};
