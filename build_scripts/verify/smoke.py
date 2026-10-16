#!/usr/bin/env python3
"""verify/smoke.py [port]: headless walk through every page for SAT and ACT; fails on any page error. Screenshots to docs/preview_smoke_*.png (gitignored)."""
import asyncio, json, sys, os, subprocess, time
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
PROFILE = {"test":"sat","minutes":"30","device":"laptop","missmode":"answer","firstmode":"read","fear":"math","timepressure":"sometimes","grade":"11","name":"Smoke","email":"s@example.com","milestones":True,"onboarded":True,"science":True,"setSize":6}
PAGES = ["index.html","settings.html","dashboard.html","drill.html","quiz.html","timed.html","timing.html","notes.html","placement.html","strategies.html"]
async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    errs = []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(); ctx = await b.new_context(viewport={"width":1280,"height":900}); pg = await ctx.new_page()
            pg.on("pageerror", lambda e: errs.append(f"{pg.url}: {e}"))
            pg.on("console", lambda m: errs.append(f"{pg.url}: {m.text}") if m.type == "error" and "ping.alakaitestprep" not in m.text and "404" not in m.text else None)
            await pg.goto(f"http://localhost:{PORT}/index.html")
            await pg.evaluate(f"localStorage.setItem('alakai.profile', JSON.stringify({json.dumps(PROFILE)})); localStorage.setItem('alakai.school', JSON.stringify('hpa'))")
            for test in ("sat", "act"):
                await pg.evaluate(f"localStorage.setItem('alakai.test', JSON.stringify('{test}'))")
                for page in PAGES:
                    await pg.goto(f"http://localhost:{PORT}/{page}"); await pg.wait_for_timeout(900)
                    await pg.screenshot(path=os.path.join(ROOT, "docs", f"preview_smoke_{test}_{page.replace('.html','')}.png"))
                # one drill item per section
                skills = json.load(open(os.path.join(ROOT, "data", test, "skills.json")))
                for sec in skills["sections"]:
                    await pg.goto(f"http://localhost:{PORT}/drill.html?section={sec['id']}"); await pg.wait_for_timeout(1200)
                    ok = await pg.query_selector(".choice, #free")
                    if not ok: errs.append(f"{test} drill section {sec['id']}: no item rendered")
            await b.close()
    finally:
        srv.terminate()
    if errs: print("SMOKE FAILURES:\n  " + "\n  ".join(errs[:30])); sys.exit(1)
    print("smoke ok")
asyncio.run(main())
