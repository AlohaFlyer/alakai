#!/bin/bash
# Run every check. Exit non-zero on the first failure.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/../.."
cd "$ROOT"
python3 build_scripts/verify/contrast.py
python3 build_scripts/verify/keys.py
python3 build_scripts/verify/links.py
for f in data/*.json data/*/*.json; do python3 -c "import json,sys;json.load(open('$f'))" || { echo "bad json: $f"; exit 1; }; done
node --check assets/app.js && node --check assets/engine.js && node --check sw.js && node --check worker/alakai-ping/worker.js
for s in build_scripts/podcast/scripts/*.md; do python3 build_scripts/podcast/render.py "$s" --dry-run >/dev/null; done

python3 -I build_scripts/verify/smoke.py 8766
python3 -I build_scripts/verify/e2e/run.py --port 8767
echo "ALL CHECKS PASSED"
