#!/usr/bin/env python3
"""verify/e2e/run.py [--port N | --base URL] [--only name,name] [--headed]

End-to-end journeys in headless Chromium (Python Playwright), iPhone-sized, Pacific/Honolulu time:
onboarding (and redo, and refresh mid-way), placement, drill miss logging, timed ACT Reading and Science
passage modules with resume, podcast listening and check, Settings dark mode, plus the debug pass 3 repros
(weekly plan in test week, cross-test deep links, corrupt storage, milestone banner, flashcard name, tap
targets, offline 404).

Nothing leaves the machine: the anonymous ping Worker is intercepted (and counted), episode audio is served
from a generated WAV, and Google Fonts are stubbed. With --port (default 8767) the script serves the repo
itself; with --base it uses a server you already started (python3 -m http.server 8765 --bind 127.0.0.1).
Exit 1 on any failure.
"""
import argparse, io, json, math, os, struct, subprocess, sys, time, traceback, wave
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TZ = "Pacific/Honolulu"
PROFILE = {"test": "sat", "minutes": "30", "device": "mix", "missmode": "answer", "firstmode": "either", "timepressure": "sometimes",
           "grade": "11", "name": "Kai", "email": "kai@example.com", "pemail": "mom@example.com", "milestones": True, "onboarded": True,
           "science": True, "setSize": 6}


def wav_bytes(seconds=12, rate=8000):
    """A quiet 440 Hz tone: Chromium (no MP3 codec in headless builds) can play WAV."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", int(800 * math.sin(2 * math.pi * 440 * i / rate))) for i in range(seconds * rate)))
    return buf.getvalue()


class Run:
    def __init__(self, base, headed=False):
        self.base = base.rstrip("/"); self.headed = headed; self.pings = []; self.wav = wav_bytes()

    def context(self, browser, width=390, height=844, **kw):
        ctx = browser.new_context(viewport={"width": width, "height": height}, timezone_id=TZ, locale="en-US",
                                  user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1", **kw)
        def ping(route):
            req = route.request
            if req.method == "POST": self.pings.append(req.post_data)
            route.fulfill(status=200, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type"}, body="ok")
        ctx.route("https://ping.alakaitestprep.app/**", ping)
        ctx.route("https://audio.alakaitestprep.app/**", lambda r: r.fulfill(status=200, headers={"Content-Type": "audio/wav", "Accept-Ranges": "none"}, body=self.wav))
        ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, headers={"Content-Type": "text/css"}, body=""))
        ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        return ctx

    def page(self, ctx):
        pg = ctx.new_page(); pg.errors = []
        pg.on("pageerror", lambda e: pg.errors.append(str(e)))
        pg.on("dialog", lambda d: d.accept())
        return pg

    def seed(self, pg, extra=None, profile=None):
        pg.goto(self.base + "/index.html")
        data = {"profile": profile if profile is not None else PROFILE, "school": "hpa", "test": "sat", "pinged": True}
        data.update(extra or {})
        pg.evaluate("d => { localStorage.clear(); for (const [k, v] of Object.entries(d)) localStorage.setItem('alakai.' + k, JSON.stringify(v)); }", data)

    def bank(self, pg, test, file):
        return pg.evaluate("p => fetch(p).then(r => r.json())", f"data/{test}/{file}")


def check(cond, msg):
    if not cond: raise AssertionError(msg)


def local_date(days):
    return (datetime.now(ZoneInfo(TZ)) + timedelta(days=days)).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- journeys
def onboarding(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.pings.clear()
    pg.goto(r.base + "/index.html"); pg.evaluate("localStorage.clear(); sessionStorage.clear()")
    pg.goto(r.base + "/onboard.html")
    plan = {"Which test": "ACT", "worries": "Math", "Where will you": "Phone", "ACT only": "Yes", "When you miss": "A hint, then let me retry"}
    reloaded = False
    for step in range(20):
        pg.wait_for_selector("#q:not(:empty)")
        q = pg.text_content("#q"); n = pg.text_content("#step")
        if step == 3 and not reloaded:
            # Refresh mid-onboarding: same question, earlier answers kept (pass 3 #20).
            pg.reload(); pg.wait_for_selector("#q:not(:empty)"); reloaded = True
            check(pg.text_content("#step") == n, f"refresh restarted onboarding: {n} -> {pg.text_content('#step')}")
            continue
        if pg.query_selector(".opts button"):
            want = next((v for k, v in plan.items() if k in q), None)
            btn = pg.locator(".opts button", has_text=want).first if want else pg.locator(".opts button").first
            btn.click(); btn.click()  # double tap must not skip a question
            pg.wait_for_function("s => document.getElementById('step').textContent !== s", arg=n)
        elif pg.query_selector("#in[type=date]"):
            pg.fill("#in", local_date(30)); pg.click("#next")
        elif pg.query_selector("#in[type=text]"):
            pg.click("#skip")
        elif pg.query_selector("#c-school"):
            pg.select_option("#c-school", "kohala"); pg.select_option("#c-grade", "10")
            pg.fill("#c-name", "Kai"); pg.fill("#c-email", "kai@example.com"); pg.fill("#c-pemail", "mom@example.com")
            check(pg.text_content("#c-shape") == '{"school":"kohala","grade":"10"}', "disclosure line does not follow the selects")
            pg.click("#next"); break
    pg.wait_for_url("**/placement.html*"); pg.wait_for_timeout(800)
    prof = pg.evaluate("JSON.parse(localStorage.getItem('alakai.profile'))")
    check(prof and prof["test"] == "act" and prof["science"] is True and prof["device"] == "phone" and prof["testdate"] == local_date(30), f"profile wrong: {prof}")
    check(len(r.pings) == 1 and json.loads(r.pings[0]) == {"school": "kohala", "grade": "10"}, f"ping not exactly once with two fields: {r.pings}")
    # Redo prefills everything, keeps parent email and test date (pass 3 #12).
    pg.goto(r.base + "/onboard.html?redo=1"); pg.wait_for_selector(".opts button")
    check(pg.get_attribute(".opts button:has-text('ACT')", "aria-pressed") == "true", "redo did not prefill the test answer")
    for _ in range(20):
        n = pg.text_content("#step")
        if pg.query_selector("#c-school"): pg.click("#next"); break
        pg.click("#next"); pg.wait_for_function("s => document.getElementById('step').textContent !== s", arg=n)
    pg.wait_for_url("**/dashboard.html*"); pg.wait_for_timeout(500)
    prof = pg.evaluate("JSON.parse(localStorage.getItem('alakai.profile'))")
    check(prof["pemail"] == "mom@example.com" and prof["testdate"] == local_date(30), f"redo dropped fields: {prof}")
    check(len(r.pings) == 1, f"redo sent another ping: {r.pings}")
    check(not pg.errors, pg.errors); ctx.close()


def placement(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.seed(pg)
    pg.goto(r.base + "/placement.html"); pg.click("#start")
    for _ in range(3):
        pg.wait_for_selector("#item .choice, #item #free")
        if pg.query_selector("#item .choice"): pg.click("#item .choice >> nth=1")
        else: pg.fill("#free", "1")
        pg.click("#next")
    pg.click("#stop"); pg.wait_for_timeout(500)
    recs = pg.evaluate("Alakai.DB.all('sat')")
    check(len([x for x in recs if x["kind"] == "placement"]) == 3, f"placement records: {len(recs)}")
    check(pg.evaluate("document.activeElement.id") == "done-h", "focus not moved to the placement result")
    check(pg.evaluate("JSON.parse(localStorage.getItem('alakai.sat.placement')).n") == 3, "placement summary not stored")
    check(not pg.errors, pg.errors); ctx.close()


def drill_miss(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.seed(pg)
    pg.goto(r.base + "/drill.html?skill=rw-ii-central"); pg.wait_for_selector("#item .choice")
    # Answer A until one is wrong (a right answer moves on with Next).
    for _ in range(6):
        pg.click("#item .choice[data-i='0']"); pg.wait_for_selector("#fb .feedback")
        if pg.get_attribute("#item .choice[data-i='0']", "data-state") == "wrong": break
        pg.click("#fb > button"); pg.wait_for_selector("#item .choice:not([disabled])")
    else: raise AssertionError("no miss in 6 tries")
    item = {"id": None}
    check(pg.get_attribute("#fb", "aria-live") == "polite", "feedback region is not a live region")
    check(pg.evaluate("document.activeElement.classList.contains('feedback')"), "focus not on the verdict after answering")
    log = pg.evaluate("JSON.parse(localStorage.getItem('alakai.sat.errlog'))")
    check(log and log[-1]["skill"] == "rw-ii-central" and log[-1]["cause"] == "unsorted" and not log[-1]["done"], f"miss not logged at once: {log}")
    pg.click("#fb button[data-c='careless']"); pg.wait_for_timeout(300)
    log = pg.evaluate("JSON.parse(localStorage.getItem('alakai.sat.errlog'))")
    check(log[-1]["cause"] == "careless", "cause not saved")
    recs = pg.evaluate("Alakai.DB.all('sat')")
    check(recs and recs[-1]["cause"] == "careless" and recs[-1]["correct"] is False, "attempt record not patched")
    check(not pg.errors, pg.errors); ctx.close()


def timed_passages(r, b):
    ctx = r.context(b, width=1280, height=800); pg = r.page(ctx); r.seed(pg, {"test": "act"}, dict(PROFILE, test="act"))
    for mod, file, sets, per in (("act-reading", "drills_reading.json", 4, 9), ("act-science", "drills_science.json", 10, 4)):
        pg.goto(r.base + "/timed.html"); pg.click(f"button[data-m='{mod}']"); pg.wait_for_selector("#ppanel h3")
        st = pg.evaluate("JSON.parse(localStorage.getItem('alakai.act.timed_inprogress'))")
        bank = r.bank(pg, "act", file); by = {i["id"]: i for i in bank}; order = {i["id"]: k for k, i in enumerate(bank)}
        ids = st["itemIds"]; g = st["groups"]
        check(len(ids) == sets * per, f"{mod}: {len(ids)} items")
        check(len({x[0] for x in g}) == sets and all(sum(1 for x in g if x[0] == s) == per for s in range(sets)), f"{mod}: sets {g}")
        seq = [by[i]["passage"] for i in ids]
        switches = sum(1 for a, c in zip(seq, seq[1:]) if a != c)
        check(len(set(seq)) == switches + 1, f"{mod}: a passage comes back after another one")
        for k in range(1, len(ids)):
            if seq[k] == seq[k - 1]: check(order[ids[k]] > order[ids[k - 1]], f"{mod}: items not in passage order")
        if mod == "act-science":
            firsts = [order[ids[k]] for k in range(len(ids)) if k == 0 or seq[k] != seq[k - 1]]
            check(firsts == sorted(firsts), f"science passages not in bank order: {firsts}")
        if mod == "act-reading":
            types = [by[ids[k]]["passage"].split(":")[0] for k in range(0, 36, 9)]
            check(types == ["LITERARY NARRATIVE", "SOCIAL SCIENCE", "HUMANITIES", "NATURAL SCIENCE"], f"reading set types {types}")
        # The panel is drawn once per passage: moving within it keeps the same node.
        pg.evaluate("document.getElementById('ppanel').firstChild.dataset.mark = '1'")
        pg.click("#next")
        check(pg.evaluate("document.getElementById('ppanel').firstChild.dataset.mark") == "1", "passage panel redrawn inside a passage")
        pg.evaluate("localStorage.removeItem('alakai.act.timed_inprogress')"); pg.goto(r.base + "/index.html")
        pg.evaluate("localStorage.removeItem('alakai.act.timed_inprogress')")
    # Resume mid-module.
    pg.goto(r.base + "/timed.html"); pg.click("button[data-m='act-reading']"); pg.wait_for_selector("#item .choice")
    pg.click("#item .choice >> nth=2"); pg.click("#next"); pg.click("#item .choice >> nth=0")
    for _ in range(9): pg.click("#next")
    label = pg.text_content("#ppanel h3")
    pg.reload(); pg.wait_for_selector("#res-go"); pg.click("#res-go"); pg.wait_for_selector("#ppanel h3")
    st = pg.evaluate("JSON.parse(localStorage.getItem('alakai.act.timed_inprogress'))")
    check(st["answers"][0] == 2 and st["answers"][1] == 0 and st["idx"] == 10, f"resume lost answers {st['answers'][:3]} idx {st['idx']}")
    check(pg.text_content("#ppanel h3") == label and label.startswith("Passage 2 of 4"), f"resume label {label}")
    # SAT modules stay one short passage per item (no grouping).
    r.seed(pg); pg.goto(r.base + "/timed.html"); pg.click("button[data-m='sat-rw-m1']"); pg.wait_for_selector("#item .choice")
    st = pg.evaluate("JSON.parse(localStorage.getItem('alakai.sat.timed_inprogress'))")
    rw = {i["id"]: i for i in r.bank(pg, "sat", "drills_rw.json")}
    check(len({rw[i]["passage"] for i in st["itemIds"]}) == 27 and not st.get("groups") and pg.is_hidden("#ppanel"), "SAT RW module changed shape")
    check(not pg.errors, pg.errors); ctx.close()


def podcast(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.seed(pg)
    pg.goto(r.base + "/notes.html?ep=1"); pg.wait_for_function("document.getElementById('audio').readyState >= 1", timeout=15000)
    rec = lambda: pg.evaluate("(JSON.parse(localStorage.getItem('alakai.sat.episodes')) || {})['1'] || {}")
    # Scrubbing to the end never unlocks the check.
    pg.evaluate("a => { const x = document.getElementById('audio'); x.currentTime = x.duration * 0.97; }", None); pg.wait_for_timeout(400)
    check(not rec().get("listened"), "scrub to the end unlocked the check")
    pg.evaluate("document.getElementById('audio').currentTime = 0"); pg.wait_for_timeout(300)
    # Play with the page's handler detached for 3 s (what a locked phone looks like to the page: no events while the
    # audio keeps playing), then the next event is one big step, which must count.
    pg.evaluate("() => { const a = document.getElementById('audio'); window._tu = a.ontimeupdate; a.ontimeupdate = null; a.playbackRate = 1; return a.play(); }")
    pg.wait_for_timeout(3200)
    pg.evaluate("() => { document.getElementById('audio').ontimeupdate = window._tu; }"); pg.wait_for_timeout(600)
    heard = pg.evaluate("() => { document.getElementById('audio').pause(); return 0; }"); pg.wait_for_timeout(300)
    h = rec().get("heard", 0)
    check(h >= 2.5, f"locked-screen playback not counted: heard {h}")
    # Finish listening (2x) and take the check.
    pg.evaluate("() => { const a = document.getElementById('audio'); a.playbackRate = 2; return a.play(); }")
    pg.wait_for_function("(JSON.parse(localStorage.getItem('alakai.sat.episodes')) || {})['1']?.listened === true", timeout=20000)
    ep = next(e for e in pg.evaluate("fetch('data/episodes.json').then(r => r.json())")["sat"] if e["n"] == 1)
    for k, q in enumerate(ep["check"]):
        pg.wait_for_selector("#check .choice:not([disabled])"); pg.wait_for_timeout(450)
        pg.click(f"#check .choice[data-k='{q['answer']}']"); pg.wait_for_selector("#cfb button")
        check(pg.get_attribute("#cfb", "aria-live") == "polite", "check feedback not live")
        pg.click("#cfb button")
    pg.wait_for_selector("#check .chip.ok")
    check(rec().get("done") and rec().get("check") == len(ep["check"]), f"check not recorded: {rec()}")
    check(not pg.errors, pg.errors); ctx.close()


def settings_dark(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.seed(pg)
    pg.goto(r.base + "/settings.html"); pg.wait_for_selector("#theme")
    pg.select_option("#theme", "dark")
    check(pg.is_visible("#unsaved"), "no unsaved-changes hint")
    pg.click("#save"); pg.wait_for_timeout(200)
    check(pg.is_hidden("#unsaved"), "unsaved hint stays after Save")
    pg.goto(r.base + "/dashboard.html"); pg.wait_for_timeout(600)
    check(pg.evaluate("document.documentElement.dataset.theme") == "dark", "theme not applied on the next page")
    check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(20, 26, 22)", "dark paper not used")
    ratio = pg.evaluate("Alakai.contrast(getComputedStyle(document.documentElement).getPropertyValue('--primary-text').trim(), '#141A16')")
    check(ratio >= 4.5, f"primary text contrast {ratio:.2f} in dark mode")
    check(not pg.errors, pg.errors); ctx.close()


# ---------------------------------------------------------------- pass 3 repros
def week_plan(r, b):
    ctx = r.context(b); pg = r.page(ctx)
    for days, full in ((14, True), (3, True), (2, False), (1, False)):
        r.seed(pg, profile=dict(PROFILE, testdate=local_date(days)))
        pg.goto(r.base + "/dashboard.html"); pg.wait_for_selector("#plan a")
        plan = pg.inner_text("#plan")
        check(("Full-length" in plan) == full, f"{days} days out, plan: {plan!r}")
        check("1 days" not in plan, "unpluralized days")
        if days == 1: check("Rest day" in plan, f"day before is not rest: {plan!r}")
    check(not pg.errors, pg.errors); ctx.close()


def deep_links(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.seed(pg)
    pg.goto(r.base + "/drill.html?skill=english-punct"); pg.wait_for_selector("#item .choice")
    check(pg.evaluate("Alakai.getTest()") == "act" and pg.get_attribute(".toggle [data-test=act]", "aria-pressed") == "true", "ACT link did not switch the test")
    pg.goto(r.base + "/drill.html?item=sat-rw-ii-central-001"); pg.wait_for_selector("#item .choice")
    check(pg.evaluate("Alakai.getTest()") == "sat", "SAT item link did not switch back")
    check(not pg.errors, pg.errors); ctx.close()


def corrupt_storage(r, b):
    ctx = r.context(b); pg = r.page(ctx)
    r.seed(pg, {"sat.timed": [{"n": 3, "right": 1, "name": "x", "id": None, "seconds": 60, "at": 1}, {"id": "sat-rw-m1", "name": "RW", "n": 27, "right": 20, "seconds": 900, "at": 2}],
                "pattern": "../../x", "sentlog": [{"junk": 1}, None], "milestone_pending": {"test": "sat", "text": "RW done"}},
           profile=dict(PROFILE, lastscore=1200, name={"a": 1}))
    bad = []
    pg.on("request", lambda q: bad.append(q.url) if "/x.svg" in q.url else None)
    pg.goto(r.base + "/dashboard.html"); pg.wait_for_selector("#plan a")
    check("Reading and Writing" in pg.text_content("#band"), f"band not rendered: {pg.text_content('#band')}")
    check("1200" in pg.text_content("#baseline") and "object" not in pg.text_content("#who"), "profile text fields not coerced")
    check(not bad, f"junk pattern id requested {bad}")
    # Milestone banner belongs to SAT: a toggle to ACT hides it (pass 3 #10).
    check(pg.is_visible("#milestone"), "milestone banner not shown")
    pg.click(".toggle [data-test=act]"); pg.wait_for_timeout(400)
    check(pg.is_hidden("#milestone"), "milestone banner survived the toggle")
    pg.goto(r.base + "/settings.html"); pg.wait_for_selector("#sentlog")
    check("Invalid Date" not in pg.text_content("#sentlog"), "junk sent-log row shown")
    check(not pg.errors, pg.errors); ctx.close()


def a11y_targets(r, b):
    ctx = r.context(b); pg = r.page(ctx); r.seed(pg)
    pg.goto(r.base + "/quiz.html"); pg.click("#study"); pg.wait_for_selector("#front:not(:empty)")
    front = pg.text_content("#front")
    check(pg.get_by_role("button", name=front).count() == 1, "flashcard name is not its question")
    pg.goto(r.base + "/drill.html"); pg.wait_for_selector("a.skill-link")
    small = pg.evaluate("""() => [...document.querySelectorAll('.toggle button, a.skill-link, label.check')].map(e => [e.textContent.trim().slice(0, 20), e.getBoundingClientRect().height]).filter(x => x[1] < 44)""")
    check(not small, f"targets under 44 px: {small}")
    pg.click("a.skill-link >> nth=0"); pg.wait_for_selector("#item .choice")
    h = pg.evaluate("(() => { const s = document.querySelector('details.approach summary'); return s ? s.getBoundingClientRect().height : 44; })()")
    check(h >= 44, f"Approach row {h}px")
    check(not pg.errors, pg.errors); ctx.close()


def offline_404(r, b):
    # A true offline run: its own server on another port, stopped once the service worker has precached
    # (a context's offline switch does not reach service worker fetches in Chromium).
    port = 8799
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        time.sleep(0.8)
        ctx = r.context(b, service_workers="allow"); pg = r.page(ctx)
        pg.goto(base + "/index.html")
        pg.evaluate("d => { localStorage.clear(); for (const [k, v] of Object.entries(d)) localStorage.setItem('alakai.' + k, JSON.stringify(v)); }", {"profile": PROFILE, "school": "hpa", "test": "sat", "pinged": True})
        pg.evaluate("navigator.serviceWorker.register('sw.js').then(() => navigator.serviceWorker.ready)")
        pg.reload(); pg.wait_for_function("navigator.serviceWorker.controller !== null", timeout=20000)
        n = pg.evaluate("caches.keys().then(async k => (await (await caches.open(k[0])).keys()).length)")
        check(n >= 50, f"precache has {n} entries")
    finally:
        srv.terminate(); srv.wait()
    for path in ("/a/b/c", "/drill.html/extra"):
        pg.goto(base + path); pg.wait_for_timeout(700)
        check("That page is not here" in pg.content(), f"{path}: offline fallback is not the 404 page")
        check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(251, 248, 241)", f"{path}: unstyled")
    pg.goto(base + "/dashboard.html"); pg.wait_for_selector("#plan a")
    check(not pg.errors, pg.errors); ctx.close()


JOURNEYS = [onboarding, placement, drill_miss, timed_passages, podcast, settings_dark, week_plan, deep_links, corrupt_storage, a11y_targets, offline_404]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8767); ap.add_argument("--base"); ap.add_argument("--only"); ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    srv = None; base = a.base
    if not base:
        srv = subprocess.Popen([sys.executable, "-m", "http.server", str(a.port), "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        base = f"http://127.0.0.1:{a.port}"; time.sleep(1)
    r = Run(base, a.headed); fails = []
    only = set(a.only.split(",")) if a.only else None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=not a.headed, args=["--autoplay-policy=no-user-gesture-required"])
            for j in JOURNEYS:
                if only and j.__name__ not in only: continue
                t0 = time.time()
                try: j(r, b); print(f"  pass  {j.__name__} ({time.time() - t0:.1f}s)")
                except Exception as e:
                    fails.append(j.__name__); print(f"  FAIL  {j.__name__}: {e}")
                    if not isinstance(e, AssertionError): traceback.print_exc()
            b.close()
    finally:
        if srv: srv.terminate()
    if fails: print("E2E FAILURES: " + ", ".join(fails)); sys.exit(1)
    print("e2e ok")


if __name__ == "__main__":
    main()
