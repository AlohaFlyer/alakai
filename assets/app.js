/* Alakaʻi Test Prep: shared runtime. No network except: data/*.json fetches (same origin), one anonymous ping (see Ping). */
(function () {
  'use strict';
  const NS = 'alakai.';
  const VERSION = '1.0.2';

  // ---------- Local store ----------
  // Browsers with site data blocked throw on localStorage and IndexedDB. Fall back to memory for this page
  // and show one notice (see storageNotice) instead of crashing or looping through onboarding.
  const mem = {};
  let lsOk = true;
  try { const t = NS + '__probe'; localStorage.setItem(t, '1'); localStorage.removeItem(t); } catch (e) { lsOk = false; }
  function isPlain(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }
  // Stored values are checked against the fallback's shape: an array fallback needs an array back, an object
  // fallback a plain object, a string/number/boolean fallback the same type. Anything else returns the fallback.
  function shapeOk(v, fallback) {
    if (fallback === undefined || fallback === null) return true;
    if (Array.isArray(fallback)) return Array.isArray(v);
    if (isPlain(fallback)) return isPlain(v);
    return typeof v === typeof fallback;
  }
  const Store = {
    ok: lsOk,
    get(key, fallback) {
      let v;
      try {
        if (lsOk) { const raw = localStorage.getItem(NS + key); if (raw === null) return fallback; v = JSON.parse(raw); }
        else { if (!(key in mem)) return fallback; v = JSON.parse(mem[key]); }
      } catch (e) { return fallback; }
      return shapeOk(v, fallback) ? v : fallback;
    },
    set(key, value) { const raw = JSON.stringify(value); if (lsOk) { try { localStorage.setItem(NS + key, raw); return; } catch (e) { /* quota or blocked: keep it in memory */ } } mem[key] = raw; },
    // An array of plain objects: stored lists can hold junk (null, numbers, strings) after a bad import or an old build.
    list(key) { return this.get(key, []).filter(isPlain); },
    del(key) { delete mem[key]; if (lsOk) { try { localStorage.removeItem(NS + key); } catch (e) {} } },
    keys() { const out = new Set(Object.keys(mem)); if (lsOk) { try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && k.startsWith(NS)) out.add(k.slice(NS.length)); } } catch (e) {} } return [...out]; },
    exportAll() { const o = {}; this.keys().forEach(k => o[k] = this.get(k)); return { version: VERSION, exported: new Date().toISOString(), data: o }; },
    // Erase means "remove my data", not "new device": the record that the one anonymous ping went out is kept
    // so the next onboarding does not send it again (the disclosure says it is sent once).
    eraseAll() { const keep = ['pinged', 'ping_sent']; this.keys().filter(k => !keep.includes(k)).forEach(k => this.del(k)); return DB.clear(); }
  };

  // ---------- IndexedDB for attempt history ----------
  // Falls back to an in-memory list when IndexedDB is missing, throws, or fails to open.
  const DB = {
    _db: null, _failed: false, _mem: [], _memId: 0,
    open() {
      if (this._db) return Promise.resolve(this._db);
      if (this._failed) return Promise.resolve(null);
      return new Promise(res => {
        const fail = () => { this._failed = true; storageNotice(); res(null); };
        let r;
        try { if (!window.indexedDB) return fail(); r = window.indexedDB.open('alakai', 1); } catch (e) { return fail(); }
        r.onupgradeneeded = () => {
          const db = r.result;
          const s = db.createObjectStore('attempts', { keyPath: 'id', autoIncrement: true });
          s.createIndex('test', 'test'); s.createIndex('skill', 'skill'); s.createIndex('ts', 'ts');
        };
        r.onsuccess = () => { this._db = r.result; res(this._db); };
        r.onerror = () => fail();
        r.onblocked = () => fail();
      });
    },
    // Resolves with the new record's key (or null), so callers can patch it later.
    async add(rec) {
      rec.ts = rec.ts || Date.now();
      const db = await this.open();
      if (!db) { rec.id = ++this._memId; this._mem.push(rec); return rec.id; }
      return new Promise(res => { try { const t = db.transaction('attempts', 'readwrite'); const q = t.objectStore('attempts').add(rec); let key = null; q.onsuccess = () => { key = q.result; }; t.oncomplete = () => res(key); t.onerror = () => res(null); } catch (e) { res(null); } });
    },
    // Merge fields into an existing record.
    async patch(key, fields) {
      if (key === null || key === undefined) return false;
      const db = await this.open();
      if (!db) { const r = this._mem.find(x => x.id === key); if (r) Object.assign(r, fields); return !!r; }
      return new Promise(res => { try { const t = db.transaction('attempts', 'readwrite'); const st = t.objectStore('attempts'); const g = st.get(key); g.onsuccess = () => { if (g.result) st.put(Object.assign(g.result, fields)); }; t.oncomplete = () => res(true); t.onerror = () => res(false); } catch (e) { res(false); } });
    },
    async all(test) {
      const db = await this.open();
      if (!db) return this._mem.filter(r => !test || r.test === test).map(r => Object.assign({}, r));
      return new Promise(res => { const out = []; try { const t = db.transaction('attempts'); const req = test ? t.objectStore('attempts').index('test').openCursor(IDBKeyRange.only(test)) : t.objectStore('attempts').openCursor(); req.onsuccess = e => { const c = e.target.result; if (c) { out.push(c.value); c.continue(); } else res(out); }; req.onerror = () => res(out); } catch (e) { res(out); } });
    },
    async clear() {
      this._mem = [];
      const db = await this.open(); if (!db) return;
      return new Promise(res => { try { const t = db.transaction('attempts', 'readwrite'); t.objectStore('attempts').clear(); t.oncomplete = () => res(true); t.onerror = () => res(false); } catch (e) { res(false); } });
    }
  };

  // One notice per page when storage is unavailable.
  function storageNotice() {
    const put = () => {
      if (document.getElementById('storage-notice')) return;
      const el = document.createElement('div'); el.id = 'storage-notice'; el.className = 'card banner'; el.setAttribute('role', 'status');
      el.innerHTML = '<strong>This browser is blocking storage, so progress cannot be saved.</strong> You can still practice, but answers and settings are lost when you leave this page. To keep progress, allow site data for alakaitestprep.app or use a normal (not private) window.';
      const host = document.querySelector('.wrap'); if (host) { const nav = host.querySelector('nav.tabs') || host.querySelector('.topbar'); if (nav) nav.after(el); else host.prepend(el); }
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', put); else put();
  }
  if (!lsOk) storageNotice();

  // ---------- Data ----------
  const cache = {};
  async function data(path) {
    if (cache[path]) return cache[path];
    const r = await fetch(path, { cache: 'no-cache' });
    if (!r.ok) throw new Error('Could not load ' + path);
    cache[path] = await r.json();
    return cache[path];
  }

  // ---------- Palette ----------
  function hexToRgb(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  function lum([r, g, b]) { const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); }
  function contrast(a, b) { const la = lum(hexToRgb(a)), lb = lum(hexToRgb(b)); const [hi, lo] = la > lb ? [la, lb] : [lb, la]; return (hi + 0.05) / (lo + 0.05); }
  function onColor(bg) { return contrast(bg, '#FFFFFF') >= contrast(bg, '#1F1F1F') ? '#FFFFFF' : '#1F1F1F'; }
  function toHex([r, g, b]) { return '#' + [r, g, b].map(c => c.toString(16).padStart(2, '0')).join(''); }
  function darken(hex, amt) { return toHex(hexToRgb(hex).map(c => Math.max(0, Math.round(c * (1 - amt))))); }
  function lighten(hex, amt) { return toHex(hexToRgb(hex).map(c => Math.min(255, Math.round(c + (255 - c) * amt)))); }

  // The school primary is a fill colour (buttons, bars). Used as text or an outline on the page it must reach 4.5:1
  // against both paper colours of the active theme: darker on light paper, lighter on dark paper. Mirrors verify/contrast.py.
  const PAPERS = { light: ['#FBF8F1', '#F2EDE0'], dark: ['#141A16', '#1C2520'] };
  function isDark() {
    const t = document.documentElement.dataset.theme;
    if (t === 'dark') return true; if (t === 'light') return false;
    try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
  }
  function primaryText(primary, dark) {
    const papers = PAPERS[dark ? 'dark' : 'light']; let c = primary;
    for (let i = 0; i < 60 && !papers.every(p => contrast(c, p) >= 4.5); i++) c = dark ? lighten(c, 0.06) : darken(c, 0.06);
    return c;
  }
  let _palette = null;
  function applyTextColor() {
    if (!_palette) return;
    document.documentElement.style.setProperty('--primary-text', primaryText(_palette, isDark()));
  }
  function setTheme(v) {
    if (v === 'light' || v === 'dark') document.documentElement.dataset.theme = v; else delete document.documentElement.dataset.theme;
    applyTextColor();
  }
  try {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) mq.addEventListener('change', applyTextColor); else if (mq.addListener) mq.addListener(applyTextColor);
  } catch (e) { /* old browser: theme follows the first load */ }

  function applyPalette(school) {
    const root = document.documentElement.style;
    let primary = school.colors.primary;
    // A near-white primary (e.g. "White" first) cannot carry buttons or bars; swap with secondary.
    if (contrast(primary, '#FFFFFF') < 2.5 && contrast(school.colors.secondary, '#FFFFFF') >= 2.5) primary = school.colors.secondary;
    // Keep bars readable on paper: if primary is too light vs paper, darken a notch.
    if (contrast(primary, '#FBF8F1') < 3) primary = darken(primary, 0.35);
    // Text on primary must hit WCAG AA 4.5:1; nudge darker until it does (mirrors verify/contrast.py).
    for (let i = 0; i < 6 && contrast(primary, onColor(primary)) < 4.5; i++) primary = darken(primary, 0.12);
    root.setProperty('--primary', primary);
    _palette = primary; applyTextColor();
    root.setProperty('--secondary', school.colors.secondary);
    root.setProperty('--accent', school.colors.accent);
    root.setProperty('--on-primary', onColor(primary));
    root.setProperty('--on-secondary', onColor(school.colors.secondary));
    document.documentElement.dataset.school = school.id;
    setFavicon(primary, school.id);
  }

  // Favicon, header mark, home screen icon and manifest all follow the chosen school.
  // Files are pre-built per school by build_scripts/icons/build_school_icons.py (Grok icon set).
  // The static favicon.ico / apple-touch-icon stay HPA red because browsers fetch those once at install.
  function setFavicon(color, schoolId) {
    try {
      if (!schoolId) return;
      const u = p => new URL(p, document.baseURI).href;
      let link = document.querySelector('link[rel="icon"][data-dynamic]');
      if (!link) {
        document.querySelectorAll('link[rel="icon"]').forEach(l => l.remove());
        link = document.createElement('link'); link.rel = 'icon'; link.type = 'image/png'; link.dataset.dynamic = '1';
        document.head.appendChild(link);
      }
      link.href = u('assets/icons/schools/' + schoolId + '-64.png');
      document.querySelectorAll('img.mark').forEach(m => { m.src = u('assets/icons/schools/' + schoolId + '-mark-72.png'); });
      const at = document.querySelector('link[rel="apple-touch-icon"]');
      if (at) at.href = u('assets/icons/schools/' + schoolId + '-180.png');
      const mf = document.querySelector('link[rel="manifest"]');
      if (mf) mf.href = u('assets/manifests/' + schoolId + '.webmanifest');
      const tc = document.querySelector('meta[name="theme-color"]');
      if (tc) tc.content = color;
    } catch (e) { /* cosmetic */ }
  }

  // Home screen icon prompt. Phones copy the icon once at Add to Home Screen and never refresh it,
  // so after a school change we offer the manual swap. Shown only where it applies (installed app or iOS Safari).
  function homeIconPrompt(host, schoolName) {
    try {
      const ua = navigator.userAgent;
      const ios = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
      const standalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
      const school = Store.get('school', 'hpa');
      if (!(ios || standalone) || Store.get('iconSchool', null) === school) return;
      const el = document.createElement('div'); el.className = 'card icon-prompt';
      const ipad = /iPad/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) || (!/Mobile/.test(ua) && /Android/.test(ua));
      const steps = ios
        ? 'Hold the old Alakaʻi icon, tap Remove App, then open this site in Safari, tap Share, then Add to Home Screen.'
        : 'Hold the old Alakaʻi icon and uninstall it, then open this site in Chrome, tap the menu, then Add to Home screen.';
      el.innerHTML = `<h3>Want the icon on your ${ipad ? 'tablet' : 'phone'} to match ${esc(schoolName || 'your school')}?</h3>
        <p class="muted">${ipad ? 'Tablets' : 'Phones'} copy the icon once when you add it, so the old one stays until you swap it. ${steps}</p>
        <div class="row"><button type="button" data-act="done">Done, I swapped it</button><button type="button" class="secondary" data-act="later">Not now</button></div>`;
      el.addEventListener('click', e => { const a = e.target.dataset.act; if (!a) return; if (a === 'done') Store.set('iconSchool', school); el.remove(); });
      host.appendChild(el);
    } catch (e) { /* cosmetic */ }
  }

  async function initPalette() {
    const s = await data(rel('data/schools.json'));
    const id = Store.get('school', s.default);
    const school = s.schools.find(x => x.id === id) || s.schools.find(x => x.id === s.default);
    applyPalette(school);
    const pat = Store.get('pattern', 'solid');
    setPattern(pat);
    return school;
  }

  function setPattern(id) { const u = new URL('assets/patterns/' + id + '.svg', document.baseURI).href; document.documentElement.style.setProperty('--pattern', `url("${u}")`); }

  // Resolve relative paths from any page depth (all pages live at root, so this is identity, kept for safety)
  function rel(p) { return p; }

  // ---------- Test toggle ----------
  function getTest() { const t = Store.get('test', 'sat'); return t === 'act' ? 'act' : 'sat'; }
  function setTest(t) { t = t === 'act' ? 'act' : 'sat'; Store.set('test', t); document.documentElement.dataset.test = t; document.querySelectorAll('[data-test-label]').forEach(el => el.textContent = t.toUpperCase()); document.querySelectorAll('.toggle [data-test]').forEach(b => b.setAttribute('aria-pressed', b.dataset.test === t ? 'true' : 'false')); document.dispatchEvent(new CustomEvent('alakai:test', { detail: t })); }
  function mountToggle(el) {
    el.innerHTML = '<button type="button" data-test="sat" aria-pressed="false">SAT</button><button type="button" data-test="act" aria-pressed="false">ACT</button>';
    el.querySelectorAll('button').forEach(b => b.addEventListener('click', () => setTest(b.dataset.test)));
    setTest(getTest());
  }

  // ---------- Feedback ----------
  let lastLine = { right: '', wrong: '' };
  async function feedbackLine(kind, streak) {
    const f = await data(rel('data/feedback.json'));
    if (kind === 'right' && streak && f.streak[String(streak)]) return f.streak[String(streak)];
    const pool = f[kind] || [];
    let line = pool[Math.floor(Math.random() * pool.length)];
    if (pool.length > 1) while (line === lastLine[kind]) line = pool[Math.floor(Math.random() * pool.length)];
    lastLine[kind] = line; return line;
  }
  async function showFeedback(container, kind, streak) {
    const line = await feedbackLine(kind, streak);
    let el = container.querySelector('.feedback');
    if (!el) { el = document.createElement('div'); container.prepend(el); }
    el.className = 'feedback ' + kind; el.textContent = line; return line;
  }

  // ---------- Profile / onboarding gate ----------
  function profile() { const p = Store.get('profile', null); return isPlain(p) ? p : null; }
  // With storage blocked a profile can never be saved, so the gate would loop. Run on a temporary profile instead
  // (the storage notice explains why nothing sticks).
  const TEMP_PROFILE = { test: 'sat', minutes: '30', missmode: 'answer', timepressure: 'sometimes', setSize: 10, science: true, milestones: false, temporary: true };
  function requireOnboarding() {
    let p = profile();
    const page = location.pathname.split('/').pop() || 'index.html';
    if (!p && !Store.ok) { p = Object.assign({}, TEMP_PROFILE); Store.set('profile', p); return p; }
    if (!p && !['index.html', 'onboard.html', 'settings.html', ''].includes(page)) location.replace('onboard.html?next=' + encodeURIComponent(page + location.search));
    return p;
  }
  // Only same-origin page names are allowed as an onboarding "next" target.
  function safeNext(n) { return typeof n === 'string' && /^[a-z0-9_-]+\.html(\?[^#]*)?$/i.test(n) ? n : null; }

  // ---------- Ping (one time, anonymous) ----------
  // Onboarding only queues the ping (ping_pending) and moves on. The next page sends it, fire-and-forget with a
  // 3-second timeout. Before the request goes out, ping_pending.sending holds the dispatch time, so a page opened
  // while it is in flight does not send it again. Success marks it sent. A retry (dashboard only, one at most) needs
  // no "sent", a "sending" mark older than 60 s, and fewer than 2 tries. If the sending page unloads before the
  // answer, the keepalive request carries on without us, so it is treated as sent (a rare miss beats a double count).
  // The body is exactly {school, grade}: the disclosure promises no other field, so no request id is added.
  const PING_URL = 'https://ping.alakaitestprep.app/ping';
  const PING_WAIT = 60000;
  function pingOnce(schoolId, grade) {
    if (Store.get('pinged', false) || !Store.ok) return;
    Store.set('ping_pending', { school: schoolId, grade: grade, tries: 0 });
  }
  function markPinged(p, extra) { Store.set('pinged', true); Store.set('ping_sent', Object.assign({ school: p.school, grade: p.grade, at: new Date().toISOString() }, extra || {})); Store.del('ping_pending'); }
  function sendPendingPing(page) {
    const p = Store.get('ping_pending', null);
    if (!p || Store.get('pinged', false)) { if (p) Store.del('ping_pending'); return Promise.resolve(false); }
    const tries = +p.tries || 0, sending = +p.sending || 0;
    if (sending && Date.now() - sending < PING_WAIT) return Promise.resolve(false); // in flight from another page
    if (tries >= 2 || (tries === 1 && page !== 'dashboard.html')) return Promise.resolve(false);
    p.tries = tries + 1; p.sending = Date.now(); Store.set('ping_pending', p);
    let settled = false;
    const onHide = () => { if (!settled) { settled = true; markPinged(p, { assumed: true }); } };
    window.addEventListener('pagehide', onHide);
    const ctl = typeof AbortController === 'function' ? new AbortController() : null;
    const timer = setTimeout(() => { if (ctl) ctl.abort(); }, 3000);
    return fetch(PING_URL, { method: 'POST', mode: 'cors', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ school: p.school, grade: p.grade }), keepalive: true, signal: ctl ? ctl.signal : undefined })
      .then(r => { if (!r.ok) throw new Error('ping ' + r.status); if (!settled) { settled = true; markPinged(p); } return true; })
      // A failure or a timeout keeps the "sending" mark: a slow Worker may still have counted it, so the one retry
      // waits out PING_WAIT.
      .catch(() => { settled = true; return false; })
      .finally(() => { clearTimeout(timer); window.removeEventListener('pagehide', onHide); });
  }

  // ---------- Progress + report ----------
  // Accuracy uses the same records on both sides: drill, timed and blitz attempts ("practice").
  // Placement also feeds bySkill and bySection so it seeds weak spots, the rings and the weekly plan;
  // it is reported on its own line, as are redo attempts. Flashcard grades are never counted.
  const PRACTICE = ['drill', 'timed', 'blitz'];
  const Progress = {
    async summary(test) {
      const all = await DB.all(test);
      const bySkill = {}, bySection = {};
      let n = 0, right = 0; const placement = { n: 0, r: 0 }, redo = { n: 0, r: 0 };
      all.forEach(a => {
        const practice = PRACTICE.includes(a.kind);
        if (a.kind === 'placement') { placement.n++; if (a.correct) placement.r++; }
        if (a.kind === 'redo') { redo.n++; if (a.correct) redo.r++; }
        if (practice) { n++; if (a.correct) right++; }
        if (practice || a.kind === 'placement') {
          const sk = bySkill[a.skill] = bySkill[a.skill] || { n: 0, r: 0, time: 0, timed: 0, careless: 0, concept: 0 };
          sk.n++; if (a.correct) sk.r++; if (a.ms) { sk.time += a.ms; sk.timed++; } if (a.cause === 'careless') sk.careless++; if (a.cause === 'concept') sk.concept++;
          const se = bySection[a.section] = bySection[a.section] || { n: 0, r: 0 }; se.n++; if (a.correct) se.r++;
        }
      });
      const timed = Store.list(test + '.timed').filter(t => typeof t.n === 'number');
      const epRaw = Store.get(test + '.episodes', {}); const episodes = {};
      Object.keys(epRaw).forEach(k => { if (isPlain(epRaw[k])) episodes[k] = epRaw[k]; });
      const blitz = Store.list(test + '.blitz').filter(b => typeof b.score === 'number');
      const days = new Set(all.filter(a => a.ts).map(a => new Date(a.ts).toDateString()));
      return { attempts: n, right, placement, redo, bySkill, bySection, timed, episodes, blitz, activeDays: days.size, streak: streakDays(days) };
    }
  };
  // Days to test: the YYYY-MM-DD date is a local calendar date (new Date('2026-11-07') would be UTC midnight, which is
  // the afternoon before in Hawaiʻi). Whole local days from today's local midnight; null when unset or unreadable.
  function parseLocalDate(s) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || '').trim()); if (!m) return null;
    const d = new Date(+m[1], +m[2] - 1, +m[3]); return isNaN(d) ? null : d;
  }
  function daysTo(s, now) {
    const t = parseLocalDate(s); if (!t) return null;
    const n = now ? new Date(now) : new Date(); const today = new Date(n.getFullYear(), n.getMonth(), n.getDate());
    return Math.round((t - today) / 86400000); // round, not floor: a DST day is 23 or 25 hours
  }
  // Average seconds per item over the attempts that carry a time (placement and timed records have none).
  function avgSec(v) { return v.timed ? Math.round(v.time / v.timed / 1000) : null; }
  function streakDays(set) {
    let n = 0; const d = new Date();
    for (;;) { if (set.has(d.toDateString())) { n++; d.setDate(d.getDate() - 1); } else if (n === 0) { d.setDate(d.getDate() - 1); if (set.has(d.toDateString())) { n++; d.setDate(d.getDate() - 1); } else break; } else break; if (n > 400) break; }
    return n;
  }
  async function buildReport(test) {
    const p = profile() || {}; const s = await Progress.summary(test);
    const skills = await data(`data/${test}/skills.json`).catch(() => null);
    const name = k => { if (!skills) return k; for (const sec of skills.sections) { if (sec.id === k) return sec.name; const f = sec.skills.find(x => x.id === k); if (f) return f.name; } return k; };
    const schools = await data('data/schools.json'); const sc = schools.schools.find(x => x.id === Store.get('school', schools.default));
    const dte = daysTo(p.testdate);
    const L = []; const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
    L.push(`Alakaʻi Test Prep progress report`);
    L.push(`Student: ${p.name || ''}   School: ${sc ? sc.name : ''}   Grade: ${p.grade || ''}`);
    L.push(`Test: ${test.toUpperCase()}${dte !== null && dte >= 0 ? `   Days to test: ${dte}` : ''}   Report date: ${new Date().toLocaleDateString()}`);
    L.push('');
    L.push(`Practice (drills and timed): ${plural(s.attempts, 'question')} answered${s.attempts ? `, ${Math.round(100 * s.right / s.attempts)}% correct` : ''}, ${plural(s.activeDays, 'active day')}, current streak ${plural(s.streak, 'day')}.`);
    if (s.placement.n) L.push(`Placement check: ${s.placement.r}/${s.placement.n} right.`);
    if (s.redo.n) L.push(`Redo of missed items: ${s.redo.r}/${s.redo.n} right.`);
    L.push('');
    if (Object.keys(s.bySection).length) L.push('By section (practice plus placement):');
    Object.entries(s.bySection).forEach(([k, v]) => L.push(`  ${name(k)}: ${v.r}/${v.n} (${Math.round(100 * v.r / v.n)}%)`));
    const weak = Object.entries(s.bySkill).filter(([, v]) => v.n >= 2).sort((a, b) => a[1].r / a[1].n - b[1].r / b[1].n).slice(0, 5);
    if (weak.length) { L.push(''); L.push('Weakest skills (2+ attempts, placement included):'); weak.forEach(([k, v]) => { const t = avgSec(v); L.push(`  ${name(k)}: ${v.r}/${v.n}${t !== null ? `, avg ${t}s per item` : ''}`); }); }
    if (s.timed.length) { L.push(''); L.push('Timed sections:'); s.timed.slice(-6).forEach(t => L.push(`  ${t.name}: ${t.right}/${t.n} in ${fmtTime(t.seconds)} (${t.unanswered || 0} left blank, ${t.flagged || 0} flagged)`)); }
    const eps = Object.values(s.episodes); if (eps.length) { L.push(''); L.push(`${test.toUpperCase()} Notes episodes completed: ${eps.filter(e => e.done).length}`); eps.filter(e => e.done).forEach(e => L.push(`  Ep ${e.n} ${e.title}${e.check !== undefined ? ` (check ${e.check}/3)` : ''}`)); }
    if (s.blitz.length) { const best = Math.max(...s.blitz.map(b => b.score)); L.push(''); L.push(`Blitz high score: ${best}`); }
    L.push(''); L.push('Next three actions:');
    const next = []; weak.slice(0, 2).forEach(([k]) => next.push(`Drill ${name(k)} (10 items)`)); if (!s.timed.length) next.push('Do one full timed module'); next.push('Review the error log and redo the items due'); next.slice(0, 3).forEach((n, i) => L.push(`  ${i + 1}. ${n}`));
    L.push(''); L.push('Sent from the student\'s own email via Alakaʻi Test Prep (alakaitestprep.app). Nothing is stored on our side.');
    const subject = `Alakaʻi Test Prep progress: ${p.name || 'student'}, ${new Date().toLocaleDateString()}`;
    return { subject, body: L.join('\n'), to: p.email || '', cc: p.pemail || '' };
  }
  async function sendReport(test) {
    const r = await buildReport(test);
    const url = `mailto:${encodeURIComponent(r.to)}?${r.cc ? 'cc=' + encodeURIComponent(r.cc) + '&' : ''}subject=${encodeURIComponent(r.subject)}&body=${encodeURIComponent(r.body)}`;
    const log = Store.list('sentlog'); log.push({ at: new Date().toISOString(), to: [r.to, r.cc].filter(Boolean).join(', '), subject: r.subject }); Store.set('sentlog', log.slice(-50));
    location.href = url; return r;
  }
  function milestone(test, key) {
    const p = profile(); if (!p || p.milestones === false) return false;
    const seen = Store.get('milestones', {}); if (seen[test + ':' + key]) return false;
    seen[test + ':' + key] = Date.now(); Store.set('milestones', seen); return true;
  }

  // ---------- Chrome ----------
  function mountFrame() {
    if (document.querySelector('.frame-bar')) return;
    ['top', 'left', 'right'].forEach(pos => {
      const solid = document.createElement('div'); solid.className = 'frame-solid ' + pos; document.body.prepend(solid);
      const bar = document.createElement('div'); bar.className = 'frame-bar ' + pos; bar.setAttribute('aria-hidden', 'true'); document.body.prepend(bar);
    });
  }
  async function mountPractice() {
    if (document.querySelector('.practice-btn')) return;
    const bar = document.querySelector('.topbar'); if (!bar) return;
    let links = { sat: [], act: [] }; try { links = await data('data/links.json'); } catch (e) { return; }
    const wrap = document.createElement('div'); wrap.className = 'practice';
    wrap.innerHTML = `<button type="button" class="practice-btn secondary" aria-haspopup="true" aria-expanded="false">Free official practice</button><div class="practice-menu" hidden></div>`;
    const toggle = bar.querySelector('.toggle'); if (toggle) toggle.before(wrap); else bar.appendChild(wrap);
    const btn = wrap.querySelector('.practice-btn'), menu = wrap.querySelector('.practice-menu');
    const fill = () => { const t = getTest(); menu.innerHTML = `<div class="muted" style="padding:4px 10px;font-size:.8rem">${t.toUpperCase()} official, free</div>` + (links[t] || []).map(l => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.name)}</a>`).join('') + `<div class="muted" style="padding:4px 10px;font-size:.8rem">${t === 'sat' ? 'ACT' : 'SAT'}</div>` + (links[t === 'sat' ? 'act' : 'sat'] || []).slice(0, 1).map(l => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.name)}</a>`).join(''); };
    const close = (refocus) => { if (menu.hidden) return; menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (refocus) btn.focus(); };
    btn.addEventListener('click', e => { e.stopPropagation(); fill(); const open = menu.hidden; menu.hidden = !open; btn.setAttribute('aria-expanded', String(open)); if (open) { const first = menu.querySelector('a'); if (first) first.focus(); } });
    document.addEventListener('click', e => { if (!wrap.contains(e.target)) close(false); });
    // Escape closes it and returns focus to the button; Tab out of the menu closes it too.
    wrap.addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) { e.preventDefault(); close(true); } });
    menu.addEventListener('click', e => { if (e.target.closest('a')) close(false); });
    wrap.addEventListener('focusout', e => { if (!menu.hidden && e.relatedTarget && !wrap.contains(e.relatedTarget)) close(false); });
    document.addEventListener('alakai:test', () => { if (!menu.hidden) fill(); });
  }
  const NAV_PARENT = { 'placement.html': 'dashboard.html' };
  function mountNav(current) {
    const nav = document.querySelector('nav.tabs'); if (!nav) return;
    const parent = NAV_PARENT[current];
    const items = [['dashboard.html', 'Dashboard'], ['drill.html', 'Drills'], ['quiz.html', 'Quizzers'], ['timed.html', 'Timed'], ['notes.html', '<span data-test-label>SAT</span> Notes Podcast'], ['timing.html', 'Time squeeze'], ['strategies.html', 'Strategies'], ['settings.html', 'Settings']];
    nav.innerHTML = items.map(([h, l]) => `<a href="${h}" ${h === current ? 'aria-current="page"' : h === parent ? 'aria-current="true"' : ''}>${l}</a>`).join('');
  }
  function fmtTime(s) { s = Math.max(0, Math.round(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
  function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
  function esc(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

  async function boot(opts) {
    opts = opts || {};
    mountFrame();
    const theme = Store.get('theme', 'auto'); if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
    const school = await initPalette();
    document.documentElement.dataset.test = getTest();
    document.querySelectorAll('[data-test-label]').forEach(el => el.textContent = getTest().toUpperCase());
    document.querySelectorAll('.toggle[data-mount]').forEach(mountToggle);
    mountNav(opts.page);
    mountPractice();
    document.querySelectorAll('[data-test-label]').forEach(el => el.textContent = getTest().toUpperCase());
    const p = opts.gate ? requireOnboarding() : profile();
    if (p && p.device === 'phone') document.documentElement.dataset.device = 'phone';
    if (opts.page !== 'onboard.html') sendPendingPing(opts.page);
    return { school, profile: p, test: getTest() };
  }

  window.Alakai = { VERSION, avgSec, daysTo, parseLocalDate, safeNext, sendPendingPing, storageNotice, setPattern, Progress, buildReport, sendReport, milestone, Store, DB, data, boot, getTest, setTest, profile, feedbackLine, showFeedback, pingOnce, contrast, onColor, primaryText, setTheme, isDark, fmtTime, shuffle, esc, applyPalette, homeIconPrompt };
})();
