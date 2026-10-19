/* Alakaʻi Test Prep: question engine shared by drills, timed sections, and redo. Depends on app.js. */
(function () {
  'use strict';
  const A = window.Alakai, S = A.Store;
  const TRAP_NAMES = { extreme: 'Trap: too extreme', 'half-right': 'Trap: half right', irrelevant: 'Trap: true but irrelevant', 'wrong-part': 'Trap: answers the wrong part', opposite: 'Trap: opposite', 'calc-slip': 'Trap: calculation slip', misread: 'Trap: misread the question', partial: 'Trap: stopped a step early', overreach: 'Trap: adds an assumption', 'grammar-near-miss': 'Trap: near miss', other: 'Trap: other trap' };
  const FILES = { sat: ['drills_rw.json', 'drills_math.json'], act: ['drills_english.json', 'drills_math.json', 'drills_reading.json', 'drills_science.json'] };

  const Bank = {
    _cache: {},
    async load(test) {
      if (this._cache[test]) return this._cache[test];
      const skills = await A.data(`data/${test}/skills.json`);
      let items = [];
      for (const f of FILES[test]) { try { items = items.concat(await A.data(`data/${test}/${f}`)); } catch (e) { /* bank not built yet */ } }
      const byId = {}; items.forEach(i => byId[i.id] = i);
      const skillName = {}, sectionOf = {}, sectionName = {};
      skills.sections.forEach(sec => { sectionName[sec.id] = sec.name; sec.skills.forEach(sk => { skillName[sk.id] = sk.name; sectionOf[sk.id] = sec.id; }); });
      this._cache[test] = { skills, items, byId, skillName, sectionOf, sectionName };
      return this._cache[test];
    },
    visibleSections(bank, test, profile) { return bank.skills.sections.filter(sec => !(test === 'act' && sec.id === 'science' && !(profile && profile.science))); }
  };

  // Interleaved set: pull from several skills, shuffle within difficulty bands, never two of the same skill in a row when avoidable
  function buildSet(bank, { skill, section, n, exclude }) {
    exclude = exclude || new Set();
    let pool = bank.items.filter(i => !exclude.has(i.id));
    if (skill) pool = pool.filter(i => i.skill === skill);
    else if (section) pool = pool.filter(i => i.section === section);
    pool = A.shuffle(pool);
    // weight unseen items first
    const seen = S.get('seen', {});
    pool.sort((a, b) => (seen[a.id] || 0) - (seen[b.id] || 0));
    const out = []; let last = null;
    while (out.length < n && pool.length) {
      let idx = pool.findIndex(i => i.skill !== last); if (idx < 0) idx = 0;
      const it = pool.splice(idx, 1)[0]; out.push(it); last = it.skill;
    }
    return out;
  }

  // ---------- Passage modules (timed ACT Reading and Science) ----------
  // A module with a "passages" block in timed.json is built from whole passages, never from loose items: each set
  // is one passage block of a given type (Reading: the passage label before the colon, Science: the skill), filled
  // with whole passages of that type and trimmed to the set size. A type the bank is short of is padded with another
  // passage of the same section (docs/BANK_SCHEMA.md). Items keep bank order inside their passage.
  function passageType(item, from) { if (from === 'skill') return item.skill; const m = /^([A-Z][A-Z ]+):/.exec(item.passage || ''); return m ? m[1].trim() : ''; }
  function passagesOf(bank, section, from) {
    const map = new Map();
    bank.items.forEach((it, idx) => {
      if (it.section !== section || it.timed_ok === false || !it.passage) return;
      let p = map.get(it.passage); if (!p) { p = { text: it.passage, idx, type: passageType(it, from), items: [] }; map.set(it.passage, p); }
      p.items.push(it);
    });
    return [...map.values()];
  }
  function buildPassageModule(bank, mod) {
    const cfg = mod.passages, from = cfg.type_from || 'label';
    const seen = S.get('seen', {}); const all = passagesOf(bank, mod.section, from); const used = new Set();
    const avgSeen = p => p.items.reduce((a, i) => a + (+seen[i.id] || 0), 0) / p.items.length;
    const specs = []; (cfg.sets || []).forEach(s => { for (let r = 0; r < (s.repeat || 1); r++) specs.push(s); });
    const sets = specs.map(spec => {
      const parts = []; let n = 0;
      const fill = cands => {
        while (n < spec.items) {
          const left = cands.filter(p => !used.has(p)); if (!left.length) return;
          const need = spec.items - n;
          // A passage that covers what is still needed beats one that would leave a stub; least seen first, ties random.
          const fits = left.filter(p => p.items.length >= need);
          const pool = A.shuffle(fits.length ? fits : left).sort((a, b) => (fits.length ? 0 : b.items.length - a.items.length) || avgSeen(a) - avgSeen(b));
          const p = pool[0]; used.add(p);
          const k = Math.min(p.items.length, need); const keep = new Set(A.shuffle(p.items.map((_, j) => j)).slice(0, k));
          parts.push({ passage: p, items: p.items.filter((_, j) => keep.has(j)) }); n += k;
        }
      };
      fill(all.filter(p => p.type === spec.type));
      if (n < spec.items) fill(all); // short of this type: closest is another passage of the same section
      parts.sort((a, b) => a.passage.idx - b.passage.idx);
      return { name: spec.name || spec.type, parts, first: parts.length ? parts[0].passage.idx : 1e9 };
    }).filter(s => s.parts.length);
    if (cfg.order === 'bank') sets.sort((a, b) => a.first - b.first);
    const items = [], groups = [];
    sets.forEach((s, si) => s.parts.forEach((pt, pi) => pt.items.forEach(it => { items.push(it); groups.push([si, pi]); })));
    return { items, groups, setNames: sets.map(s => s.name) };
  }
  // Loose modules (and placement): items that share a passage or table sit next to each other, in first-seen order.
  function clusterByPassage(items) {
    const out = [], done = new Set();
    items.forEach(it => { if (done.has(it)) return; (it.passage ? items.filter(x => x.passage === it.passage) : [it]).forEach(x => { if (!done.has(x)) { done.add(x); out.push(x); } }); });
    return out;
  }

  // Render one item into container; returns a promise resolving {correct, ms, picked}
  function renderItem(container, item, opts) {
    opts = opts || {};
    const profile = A.profile() || {};
    const mode = opts.mode || profile.missmode || 'answer';
    const start = Date.now();
    const free = !item.choices || item.choices.length === 0;
    const letters = 'ABCDE';
    const strat = opts.strategy; // {name, steps[]} or undefined
    container.innerHTML = `
      ${strat ? `<details class="approach"><summary>Approach: ${A.esc(strat.name)}</summary><ol>${strat.steps.map(x => `<li>${A.esc(x)}</li>`).join('')}</ol></details>` : ''}
      ${item.passage ? `<div class="passage card" style="box-shadow:none;background:var(--paper-2)">${A.esc(item.passage).replace(/\n/g, '<br>')}</div>` : ''}
      <div class="q-stem">${A.esc(item.stem).replace(/\n/g, '<br>')}</div>
      ${free ? `<div class="row">${gridIn('')}<button id="submit">Check</button></div>`
             : `<div class="choices">${item.choices.map((c, i) => `<div class="choice-row"><button class="choice" data-i="${i}"><strong>${letters[i]}.</strong> ${A.esc(c)}</button><button class="strike" data-i="${i}" title="Cross out" aria-label="Cross out ${letters[i]}" aria-pressed="false">×</button></div>`).join('')}</div>`}
      <div class="row" style="margin-top:8px">${opts.allowFlag ? '<button class="ghost" id="flag">Flag for later</button>' : ''}${mode === 'hint' ? '<button class="ghost" id="hintbtn">Hint</button>' : ''}<span class="muted" id="skillname">${A.esc(opts.skillName || '')}</span></div>
      <div id="fb" aria-live="polite"></div>`;
    wireGridIn(container);
    return new Promise(resolve => {
      let hintUsed = false, tries = 0, settled = false, firstPick = null;
      const hb = container.querySelector('#hintbtn'); if (hb) hb.addEventListener('click', () => { hintUsed = true; showHint(); });
      function showHint() { let h = container.querySelector('.hintbox'); if (!h) { h = document.createElement('div'); h.className = 'explain hintbox'; container.querySelector('#fb').appendChild(h); } h.textContent = 'Hint: ' + item.hint; }
      const struck = new Set();
      container.querySelectorAll('.strike').forEach(b => b.addEventListener('click', () => { const i = +b.dataset.i; const row = b.parentElement; if (struck.has(i)) { struck.delete(i); row.classList.remove('struck'); } else { struck.add(i); row.classList.add('struck'); } b.setAttribute('aria-pressed', struck.has(i) ? 'true' : 'false'); }));
      const fl = container.querySelector('#flag'); if (fl) fl.addEventListener('click', () => { fl.textContent = 'Flagged'; opts.onFlag && opts.onFlag(item); });
      // Hint mode: a wrong first try shows the hint (hintUsed). A right second try is shown as right but recorded
      // as a miss (correct false, retry true, cause "needed hint"), so accuracy and the error log stay honest.
      function finish(correct, picked) {
        if (settled) return; settled = true;
        const ms = Date.now() - start;
        const retry = correct && firstPick !== null;
        // Answered: strike keys, the answer box and its keys stop responding too.
        container.querySelectorAll('.strike, #free, #submit, .minus-row .key').forEach(x => { x.disabled = true; });
        container.querySelectorAll('.choice').forEach(b => { b.disabled = true; const i = +b.dataset.i; if (i === item.answer) b.dataset.state = 'right'; else if (i === picked || i === firstPick) b.dataset.state = 'wrong'; });
        if (!opts.silent) explain(correct, picked, retry);
        const trapPick = retry ? firstPick : picked;
        const trap = (!free && (!correct || retry) && item.traps && item.traps[trapPick]) || null;
        resolve({ correct: correct && !retry, shownRight: correct, retry, ms, picked, firstPick, hintUsed, tries, struck: [...struck], trap, cause: retry ? 'needed hint' : null });
      }
      function explain(correct, picked, retry) {
        const fb = container.querySelector('#fb');
        if (retry) { const old = fb.querySelector('.feedback'); if (old) old.remove(); const el = document.createElement('div'); el.className = 'feedback right'; el.textContent = 'Got it on the second try. It goes in your error log so it comes back.'; fb.prepend(el); el.tabIndex = -1; try { el.focus({ preventScroll: true }); } catch (e) {} }
        else A.showFeedback(fb, correct ? 'right' : 'wrong', opts.streak, { focus: !opts.silent });
        const parts = [];
        if (!correct && !free && item.distractors && item.distractors[picked]) parts.push(`<p>${item.traps && item.traps[picked] ? `<span class="chip warn">${A.esc(TRAP_NAMES[item.traps[picked]] || item.traps[picked])}</span> ` : ''}<strong>Why ${letters[picked]} tempts you:</strong> ${A.esc(item.distractors[picked])}</p>`);
        if (!correct && !free && struck.has(item.answer)) parts.push(`<p class="muted">You crossed out the right answer. Cross out only when you can say why it is wrong.</p>`);
        parts.push(`<p><strong>${free ? 'Answer: ' + A.esc(item.answer) + '. Why' : 'Why ' + letters[item.answer] + ' is right'}:</strong> ${A.esc(item.explain)}</p>`);
        if (mode === 'worked' || (!correct && item.worked)) parts.push(`<details ${mode === 'worked' ? 'open' : ''}><summary>Worked solution</summary><pre style="white-space:pre-wrap;font-family:inherit">${A.esc(item.worked)}</pre></details>`);
        const d = document.createElement('div'); d.className = 'explain'; d.innerHTML = parts.join(''); fb.appendChild(d);
        const b = document.createElement('button'); b.textContent = opts.nextLabel || 'Next'; b.style.marginTop = '10px'; b.addEventListener('click', () => opts.onNext && opts.onNext()); fb.appendChild(b);
      }
      container.querySelectorAll('.choice').forEach(b => b.addEventListener('click', () => {
        const i = +b.dataset.i; tries++;
        if (i === item.answer) return finish(true, i);
        if (mode === 'hint' && tries === 1 && !opts.timed) { b.dataset.state = 'wrong'; b.disabled = true; firstPick = i; hintUsed = true; showHint(); return; }
        finish(false, i);
      }));
      const sub = container.querySelector('#submit'); if (sub) {
        const check = () => { const v = container.querySelector('#free').value.trim(); if (!v) return; tries++; const ok = normalize(v) === normalize(item.answer) || (item.answer_alt || []).some(a => normalize(a) === normalize(v)); if (ok) return finish(true, v); if (mode === 'hint' && tries === 1 && !opts.timed) { firstPick = v; hintUsed = true; notQuite(v); showHint(); return; } finish(false, v); };
        function notQuite(v) { const inp = container.querySelector('#free'); inp.classList.add('free-wrong'); inp.setAttribute('aria-invalid', 'true'); inp.addEventListener('input', () => { inp.classList.remove('free-wrong'); inp.removeAttribute('aria-invalid'); }, { once: true }); const fb = container.querySelector('#fb'); let el = fb.querySelector('.feedback'); if (!el) { el = document.createElement('div'); fb.prepend(el); } el.className = 'feedback wrong'; el.setAttribute('role', 'status'); el.textContent = `Not quite: ${v} is not it. Read the hint and try once more.`; }
        sub.addEventListener('click', check); container.querySelector('#free').addEventListener('keydown', e => { if (e.key === 'Enter') check(); });
      }
    });
  }
  // Student-produced response box. iOS shows a digits-and-point keypad for inputmode="decimal" (no minus, no slash),
  // so the box carries its own "−" (sign toggle) and "/" keys; a hardware or full keyboard can type them as usual.
  function gridIn(value) {
    return `<span class="minus-row"><input type="text" id="free" inputmode="decimal" pattern="-?[0-9./]*" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" placeholder="Your answer" aria-label="Your answer" aria-describedby="free-help" style="max-width:180px" value="${A.esc(value || '')}"><button type="button" class="key" data-key="neg" aria-label="Negative: switch the sign">−</button><button type="button" class="key" data-key="slash" aria-label="Fraction bar">/</button></span><small class="muted" id="free-help" style="flex-basis:100%">Negative: tap −. Fraction: tap / (7/2).</small>`;
  }
  function wireGridIn(container) {
    const inp = container.querySelector('#free'); if (!inp) return;
    let caret = null; const keep = () => { try { caret = inp.selectionStart; } catch (e) { caret = null; } };
    ['keyup', 'click', 'input', 'select', 'blur'].forEach(ev => inp.addEventListener(ev, keep));
    container.querySelectorAll('.minus-row .key').forEach(k => {
      // Keep the caret (and the keypad) in the box: the key must not take focus.
      k.addEventListener('mousedown', e => e.preventDefault()); k.addEventListener('pointerdown', e => e.preventDefault());
      k.addEventListener('click', () => {
        if (inp.disabled || inp.readOnly) return;
        let v = inp.value, at = caret === null || caret > v.length ? v.length : caret;
        if (k.dataset.key === 'neg') { const neg = /^\s*[-−]/.test(v); v = neg ? v.replace(/^\s*[-−]/, '') : '-' + v.trimStart(); at = Math.max(0, at + (neg ? -1 : 1)); }
        else { v = v.slice(0, at) + '/' + v.slice(at); at += 1; }
        inp.value = v; caret = at;
        try { inp.focus(); inp.setSelectionRange(at, at); } catch (e) {}
        inp.dispatchEvent(new Event('input', { bubbles: true }));
      });
    });
  }
  function normalize(v) { v = String(v).trim().replace(/[−–]/g, '-').replace(/\s+/g, '').replace(/^\+/, ''); const n = Number(v); if (!isNaN(n) && v !== '') return String(Math.round(n * 10000) / 10000); if (/^-?\d+\/\d+$/.test(v)) { const [a, b] = v.split('/').map(Number); if (b) return String(Math.round(a / b * 10000) / 10000); } return v.toLowerCase(); }

  // Records one graded attempt the moment it is graded. Misses go to the error log right away with cause
  // "unsorted" (or the cause already known); setCause() fills it in later if the student answers "Why did you miss it?".
  // Resolves with the DB key of the attempt.
  async function record(test, item, res, kind, extra) {
    const seen = S.get('seen', {}); seen[item.id] = (seen[item.id] || 0) + 1; S.set('seen', seen);
    const miss = !res.correct;
    const cause = res.cause || (miss && kind !== 'blitz' ? 'unsorted' : null);
    if (miss && kind !== 'blitz') {
      const log = S.get(test + '.errlog', []);
      const open = log.find(e => e && e.id === item.id && !e.done);
      if (!open) log.push({ id: item.id, skill: item.skill, at: Date.now(), due: Date.now() + 3 * 86400000, done: false, cause, trap: res.trap || null });
      else if (kind === 'redo') { open.due = Date.now() + 3 * 86400000; if (res.trap) open.trap = res.trap; }
      S.set(test + '.errlog', log.slice(-300));
    } else if (res.correct && kind === 'redo') {
      const log = S.get(test + '.errlog', []); log.forEach(e => { if (e && e.id === item.id) e.done = true; }); S.set(test + '.errlog', log);
    }
    return A.DB.add(Object.assign({ test, kind, item: item.id, skill: item.skill, section: item.section, correct: !!res.correct, ms: res.ms, hint: !!res.hintUsed, retry: !!res.retry, cause, trap: res.trap || null, struck: (res.struck || []).length }, extra || {}));
  }
  async function setCause(test, item, key, cause) {
    const log = S.get(test + '.errlog', []);
    const e = log.slice().reverse().find(x => x && x.id === item.id && !x.done); if (e) { e.cause = cause; S.set(test + '.errlog', log); }
    return A.DB.patch(key, { cause });
  }

  function askCause(container) {
    return new Promise(resolve => {
      const d = document.createElement('div'); d.className = 'row'; d.style.marginTop = '8px';
      d.innerHTML = '<span class="muted">Why did you miss it?</span>' + [['careless', 'Careless'], ['concept', 'Didn\'t know it'], ['time', 'Rushed']].map(([v, l]) => `<button class="secondary" data-c="${v}">${l}</button>`).join('');
      d.querySelectorAll('button').forEach(b => b.addEventListener('click', () => { d.innerHTML = `<span class="chip">${b.textContent}</span>`; resolve(b.dataset.c); }));
      // After the verdict, so keyboard and screen reader users meet it right after the "right / wrong" line.
      const fb = container.querySelector('#fb'); const v = fb.querySelector('.feedback'); if (v) v.after(d); else fb.prepend(d);
    });
  }

  let _strat = null;
  async function strategyFor(test, skill) { if (!_strat) { try { _strat = await A.data('data/strategies.json'); } catch (e) { _strat = {}; } } return (_strat[test] || {})[skill] || null; }
  // Skill levels: Attempted, Familiar (>=60% over 5), Proficient (>=75% over 10 with a hard item right), Mastered (Proficient + a correct redo)
  function level(stats) { if (!stats || !stats.n) return 'New'; const acc = stats.r / stats.n; if (stats.n >= 10 && acc >= 0.75 && stats.hardRight && stats.redoRight) return 'Mastered'; if (stats.n >= 10 && acc >= 0.75 && stats.hardRight) return 'Proficient'; if (stats.n >= 5 && acc >= 0.6) return 'Familiar'; return 'Attempted'; }
  const CAUSE_NAMES = { careless: 'careless', concept: 'didn\'t know it', time: 'rushed or ran out of time', unsorted: 'missed', 'needed hint': 'needed the hint' };
  window.AlakaiEngine = { buildPassageModule, clusterByPassage, passagesOf, gridIn, wireGridIn, strategyFor, level, TRAP_NAMES, CAUSE_NAMES, Bank, buildSet, renderItem, record, setCause, askCause, normalize };
})();
