/* Alakaʻi Test Prep service worker: cache-first for app shell and data, network-first for episodes.json, never caches audio. */
const VERSION = 'alakai-v15';
const BANKS = ['sat/drills_rw.json', 'sat/drills_math.json', 'sat/cards_rw.json', 'sat/cards_math.json',
  'act/drills_english.json', 'act/drills_math.json', 'act/drills_reading.json', 'act/drills_science.json',
  'act/cards_english.json', 'act/cards_math.json', 'act/cards_reading.json', 'act/cards_science.json'].map(p => 'data/' + p);
const SHELL = ['./', 'index.html', 'onboard.html', 'dashboard.html', 'drill.html', 'quiz.html', 'timed.html', 'timing.html', 'notes.html', 'settings.html', 'placement.html', 'strategies.html', '404.html',
  'favicon.ico', 'site.webmanifest',
  'assets/app.css', 'assets/app.js', 'assets/engine.js', 'assets/patterns/solid.svg', 'assets/patterns/a.svg', 'assets/patterns/b.svg', 'assets/patterns/c.svg', 'assets/patterns/d.svg', 'assets/patterns/e.svg', 'assets/patterns/f.svg', 'assets/patterns/g.svg', 'assets/hero-900.jpg', 'assets/icons/favicon-32.png', 'assets/icons/mark-72.png', 'assets/icons/icon-192.png',
  'data/schools.json', 'data/episodes.json', 'data/feedback.json', 'data/onboarding.json', 'data/strategies.json', 'data/links.json', 'data/sat/scale.json', 'data/act/scale.json', 'data/sat/skills.json', 'data/act/skills.json', 'data/sat/timed.json', 'data/act/timed.json'].concat(BANKS);

// cache: 'reload' skips the browser HTTP cache (GitHub Pages sends max-age=600), so a version bump always
// precaches the files that are on the server now, never a stale copy from the last ten minutes.
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });

function putCopy(req, r) { if (r && r.ok) { const c = r.clone(); caches.open(VERSION).then(x => x.put(req, c)); } return r; }

self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  if (u.pathname.endsWith('.mp3')) return; // audio is never cached (R2, range requests)
  if (u.pathname.endsWith('episodes.json') || u.pathname.endsWith('versions.json')) {
    e.respondWith(fetch(e.request).then(r => putCopy(e.request, r)).catch(() => caches.match(e.request, { ignoreSearch: true })));
    return;
  }
  // Pages: "/" is index.html, and the query string (drill.html?skill=..., notes.html?ep=3) never changes the file.
  const isPage = e.request.mode === 'navigate' || u.pathname.endsWith('.html') || u.pathname.endsWith('/');
  if (isPage) {
    const path = u.pathname.endsWith('/') ? u.pathname + 'index.html' : u.pathname;
    const key = new URL(path, location.origin).href;
    e.respondWith(caches.match(key, { ignoreSearch: true })
      .then(hit => hit || fetch(key, { cache: 'reload' }).then(r => putCopy(key, r)))
      .catch(() => caches.match('index.html')));
    return;
  }
  // Everything else same-origin: cache first, then network (and keep a copy of data and assets), then nothing.
  // html, js and css missing from the cache are fetched past the HTTP cache too, so a stale copy is never stored.
  const fresh = /\.(html|js|css)$/.test(u.pathname);
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(fresh ? new Request(e.request.url, { cache: 'reload' }) : e.request).then(r => {
    if (u.pathname.endsWith('.json') || u.pathname.startsWith('/assets/') || u.pathname.endsWith('.ico') || u.pathname.endsWith('.webmanifest')) putCopy(e.request, r);
    return r;
  })));
});
