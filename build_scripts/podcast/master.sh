#!/bin/bash
# master.sh <out-dir> <episode-slug>   e.g. master.sh out/sat-ep0-elevenlabs sat-ep0
# Concatenates scene*.mp3 (or line*.mp3 with 350 ms gaps), normalizes to -16 LUFS, writes ../../audio/<slug>.mp3
set -e
IN="$1"; SLUG="$2"; HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$HERE/../../audio"; mkdir -p "$OUT"
cd "$IN"
if ls scene*.mp3 >/dev/null 2>&1; then
  for f in scene*.mp3; do echo "file '$PWD/$f'"; done > list.txt
  ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy joined.mp3
else
  # per-line (Cartesia): insert 350 ms silence between lines
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=44100:cl=mono -t 0.35 gap.mp3
  : > list.txt; for f in line*.mp3; do echo "file '$PWD/$f'" >> list.txt; echo "file '$PWD/gap.mp3'" >> list.txt; done
  ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt joined.mp3
fi
ffmpeg -y -loglevel error -i joined.mp3 -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 -b:a 96k "$OUT/$SLUG.mp3"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$SLUG.mp3" | awk -v s="$SLUG" '{printf "%s: %d:%02d\n", s, int($1/60), int($1%60)}'
