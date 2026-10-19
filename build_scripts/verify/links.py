#!/usr/bin/env python3
"""verify/links.py: every local href/src in the html pages must resolve to a file in the repo."""
import os, re, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bad = []
for page in glob.glob(os.path.join(ROOT, "*.html")):
    s = open(page, encoding="utf-8").read()
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', s):
        u = m.group(1)
        if u.startswith(("http", "mailto:", "data:", "//", "javascript:")) or "${" in u: continue
        if not os.path.exists(os.path.join(ROOT, u.lstrip("/"))): bad.append(f"{os.path.basename(page)}: {u}")
    for m in re.finditer(r"""['"]((?:data|assets|audio)/[^'"]+\.(?:json|svg|jpg|png|js|css))['"]""", s):
        u = m.group(1)
        if "${" in u or "+" in u: continue
        if not os.path.exists(os.path.join(ROOT, u)): bad.append(f"{os.path.basename(page)}: {u}")
if bad: print("BROKEN:\n  " + "\n  ".join(sorted(set(bad)))); sys.exit(1)
print("links ok")
