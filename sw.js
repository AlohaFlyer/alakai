/* Alakaʻi Test Prep service worker: cache-first for app shell and data, network-first for episodes.json, never caches audio. */
const VERSION = 'alakai-v1';
const SHELL = ['index.html', 'onboard.html', 'dashboard.html', 'drill.html', 'quiz.html', 'timed.html', 'timing.html', 'notes.html', 'settings.html',
  'assets/app.css', 'assets/app.js', 'assets/engine.js', 'assets/patterns/solid.svg', 'assets/patterns/a.svg', 'assets/patterns/b.svg', 'assets/patterns/c.svg', 'assets/patterns/d.svg', 'assets/patterns/e.svg', 'assets/patterns/f.svg', 'assets/patterns/g.svg', 'assets/hero-900.jpg',
  'data/schools.json', 'data/feedback.json', 'data/onboarding.json', 'data/sat/skills.json', 'data/act/skills.json', 'data/sat/timed.json', 'data/act/timed.json'];

self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  if (u.pathname.endsWith('.mp3')) return;
  if (u.pathname.endsWith('episodes.json') || u.pathname.endsWith('versions.json')) {
    e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(VERSION).then(x => x.put(e.request, c)); return r; }).catch(() => caches.match(e.request)));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok && (u.pathname.endsWith('.json') || u.pathname.endsWith('.html') || u.pathname.startsWith('/assets/'))) { const c = r.clone(); caches.open(VERSION).then(x => x.put(e.request, c)); } return r; })));
});
