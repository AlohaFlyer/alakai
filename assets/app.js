/* Alakaʻi Test Prep: shared runtime. No network except: data/*.json fetches (same origin), one anonymous ping (see Ping). */
(function () {
  'use strict';
  const NS = 'alakai.';
  const VERSION = '0.3.0';

  // ---------- Local store ----------
  const Store = {
    get(key, fallback) {
      try { const v = localStorage.getItem(NS + key); return v === null ? fallback : JSON.parse(v); }
      catch (e) { return fallback; }
    },
    set(key, value) { try { localStorage.setItem(NS + key, JSON.stringify(value)); } catch (e) {} },
    del(key) { try { localStorage.removeItem(NS + key); } catch (e) {} },
    keys() { const out = []; try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && k.startsWith(NS)) out.push(k.slice(NS.length)); } } catch (e) {} return out; },
    exportAll() { const o = {}; this.keys().forEach(k => o[k] = this.get(k)); return { version: VERSION, exported: new Date().toISOString(), data: o }; },
    eraseAll() { this.keys().forEach(k => this.del(k)); return DB.clear(); }
  };

  // ---------- IndexedDB for attempt history ----------
  const DB = {
    _db: null,
    open() {
      if (this._db) return Promise.resolve(this._db);
      return new Promise((res, rej) => {
        if (!('indexedDB' in window)) return res(null);
        const r = indexedDB.open('alakai', 1);
        r.onupgradeneeded = () => {
          const db = r.result;
          const s = db.createObjectStore('attempts', { keyPath: 'id', autoIncrement: true });
          s.createIndex('test', 'test'); s.createIndex('skill', 'skill'); s.createIndex('ts', 'ts');
        };
        r.onsuccess = () => { this._db = r.result; res(this._db); };
        r.onerror = () => res(null);
      });
    },
    async add(rec) { const db = await this.open(); if (!db) return; rec.ts = rec.ts || Date.now(); return new Promise(res => { const t = db.transaction('attempts', 'readwrite'); t.objectStore('attempts').add(rec); t.oncomplete = () => res(true); t.onerror = () => res(false); }); },
    async all(test) { const db = await this.open(); if (!db) return []; return new Promise(res => { const t = db.transaction('attempts'); const out = []; const req = test ? t.objectStore('attempts').index('test').openCursor(IDBKeyRange.only(test)) : t.objectStore('attempts').openCursor(); req.onsuccess = e => { const c = e.target.result; if (c) { out.push(c.value); c.continue(); } else res(out); }; req.onerror = () => res(out); }); },
    async clear() { const db = await this.open(); if (!db) return; return new Promise(res => { const t = db.transaction('attempts', 'readwrite'); t.objectStore('attempts').clear(); t.oncomplete = () => res(true); t.onerror = () => res(false); }); }
  };

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
  function darken(hex, amt) { const [r, g, b] = hexToRgb(hex).map(c => Math.max(0, Math.round(c * (1 - amt)))); return '#' + [r, g, b].map(c => c.toString(16).padStart(2, '0')).join(''); }

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
      const steps = ios
        ? 'Hold the old Alakaʻi icon, tap Remove App, then open this site in Safari, tap Share, then Add to Home Screen.'
        : 'Hold the old Alakaʻi icon and uninstall it, then open this site in Chrome, tap the menu, then Add to Home screen.';
      el.innerHTML = `<h3>Want the icon on your phone to match ${esc(schoolName || 'your school')}?</h3>
        <p class="muted">Phones copy the icon once when you add it, so the old one stays until you swap it. ${steps}</p>
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
  function getTest() { return Store.get('test', 'sat'); }
  function setTest(t) { Store.set('test', t); document.documentElement.dataset.test = t; document.querySelectorAll('[data-test-label]').forEach(el => el.textContent = t.toUpperCase()); document.querySelectorAll('.toggle [data-test]').forEach(b => b.setAttribute('aria-pressed', b.dataset.test === t ? 'true' : 'false')); document.dispatchEvent(new CustomEvent('alakai:test', { detail: t })); }
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
  function profile() { return Store.get('profile', null); }
  function requireOnboarding() {
    const p = profile();
    const page = location.pathname.split('/').pop() || 'index.html';
    if (!p && !['index.html', 'onboard.html', 'settings.html', ''].includes(page)) location.replace('onboard.html?next=' + encodeURIComponent(page));
    return p;
  }

  // ---------- Ping (one time, anonymous) ----------
  const PING_URL = 'https://ping.alakaitestprep.app/ping';
  async function pingOnce(schoolId, grade) {
    if (Store.get('pinged', false)) return;
    try {
      await fetch(PING_URL, { method: 'POST', mode: 'cors', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ school: schoolId, grade: grade }), keepalive: true });
    } catch (e) { /* offline or worker not deployed yet; never retried beyond next onboarding completion */ }
    Store.set('pinged', true);
    Store.set('ping_sent', { school: schoolId, grade: grade, at: new Date().toISOString() });
  }


  // ---------- Progress + report ----------
  const Progress = {
    async summary(test) {
      const attempts = await DB.all(test);
      const bySkill = {}, bySection = {};
      let right = 0;
      attempts.forEach(a => {
        if (a.kind === 'drill' || a.kind === 'timed' || a.kind === 'blitz') {
          const sk = bySkill[a.skill] = bySkill[a.skill] || { n: 0, r: 0, time: 0, careless: 0, concept: 0 };
          sk.n++; if (a.correct) { sk.r++; right++; } sk.time += a.ms || 0; if (a.cause === 'careless') sk.careless++; if (a.cause === 'concept') sk.concept++;
          const se = bySection[a.section] = bySection[a.section] || { n: 0, r: 0 }; se.n++; if (a.correct) se.r++;
        }
      });
      const timed = Store.get(test + '.timed', []);
      const episodes = Store.get(test + '.episodes', {});
      const blitz = Store.get(test + '.blitz', []);
      const days = new Set(attempts.map(a => new Date(a.ts).toDateString()));
      return { attempts: attempts.length, right, bySkill, bySection, timed, episodes, blitz, activeDays: days.size, streak: streakDays(days) };
    }
  };
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
    const dte = p.testdate ? Math.ceil((new Date(p.testdate) - Date.now()) / 86400000) : null;
    const L = [];
    L.push(`Alakaʻi Test Prep progress report`);
    L.push(`Student: ${p.name || ''}   School: ${sc ? sc.name : ''}   Grade: ${p.grade || ''}`);
    L.push(`Test: ${test.toUpperCase()}${dte !== null ? `   Days to test: ${dte}` : ''}   Report date: ${new Date().toLocaleDateString()}`);
    L.push('');
    L.push(`Practice: ${s.attempts} questions answered, ${s.attempts ? Math.round(100 * s.right / s.attempts) : 0}% correct, ${s.activeDays} active days, current streak ${s.streak} day${s.streak === 1 ? '' : 's'}.`);
    L.push('');
    L.push('By section:');
    Object.entries(s.bySection).forEach(([k, v]) => L.push(`  ${name(k)}: ${v.r}/${v.n} (${Math.round(100 * v.r / v.n)}%)`));
    const weak = Object.entries(s.bySkill).filter(([, v]) => v.n >= 4).sort((a, b) => a[1].r / a[1].n - b[1].r / b[1].n).slice(0, 5);
    if (weak.length) { L.push(''); L.push('Weakest skills (needs 4+ attempts):'); weak.forEach(([k, v]) => L.push(`  ${name(k)}: ${v.r}/${v.n}, avg ${Math.round(v.time / v.n / 1000)}s per item`)); }
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
    const log = Store.get('sentlog', []); log.push({ at: new Date().toISOString(), to: [r.to, r.cc].filter(Boolean).join(', '), subject: r.subject }); Store.set('sentlog', log.slice(-50));
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
    btn.addEventListener('click', e => { e.stopPropagation(); fill(); const open = menu.hidden; menu.hidden = !open; btn.setAttribute('aria-expanded', String(open)); });
    document.addEventListener('click', () => { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); });
    document.addEventListener('alakai:test', () => { if (!menu.hidden) fill(); });
  }
  function mountNav(current) {
    const nav = document.querySelector('nav.tabs'); if (!nav) return;
    const items = [['dashboard.html', 'Dashboard'], ['drill.html', 'Drills'], ['quiz.html', 'Quizzers'], ['timed.html', 'Timed'], ['notes.html', '<span data-test-label>SAT</span> Notes Podcast'], ['timing.html', 'Time squeeze'], ['strategies.html', 'Strategies'], ['settings.html', 'Settings']];
    nav.innerHTML = items.map(([h, l]) => `<a href="${h}" ${h === current ? 'aria-current="page"' : ''}>${l}</a>`).join('');
  }
  function fmtTime(s) { s = Math.max(0, Math.round(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
  function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
  function esc(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

  async function boot(opts) {
    opts = opts || {};
    mountFrame();
    const theme = Store.get('theme', 'auto'); if (theme !== 'auto') document.documentElement.dataset.theme = theme;
    const school = await initPalette();
    document.documentElement.dataset.test = getTest();
    document.querySelectorAll('[data-test-label]').forEach(el => el.textContent = getTest().toUpperCase());
    document.querySelectorAll('.toggle[data-mount]').forEach(mountToggle);
    mountNav(opts.page);
    mountPractice();
    document.querySelectorAll('[data-test-label]').forEach(el => el.textContent = getTest().toUpperCase());
    if (opts.gate) requireOnboarding();
    return { school, profile: profile(), test: getTest() };
  }

  window.Alakai = { VERSION, setPattern, Progress, buildReport, sendReport, milestone, Store, DB, data, boot, getTest, setTest, profile, feedbackLine, showFeedback, pingOnce, contrast, onColor, fmtTime, shuffle, esc, applyPalette, homeIconPrompt };
})();
