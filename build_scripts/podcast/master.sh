#!/bin/bash
# master.sh <out-dir> <episode-slug>   e.g. master.sh out/sat-ep0-elevenlabs sat-ep0
# 1. concat scene*.mp3 (or line*.mp3 with 350 ms gaps) -> voice.mp3
# 2. music bed: intro.mp3 plays, voice starts 3 s before intro ends (intro ducks to -12 dB under voice);
#    outro.mp3 starts 2 s before voice ends at -14 dB under the last words, then rises and plays out.
# 3. loudnorm to -16 LUFS, 96 kbps mp3 -> ../../audio/<slug>.mp3
set -e
IN="$1"; SLUG="$2"; HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$HERE/../../audio"; MUSIC="$HERE/music"; mkdir -p "$OUT"
cd "$IN"
if [ -f list.txt ] && ! ls scene*.mp3 >/dev/null 2>&1; then
  TEMPO="${VOICE_TEMPO:-1.08}"; GAP="${LINE_GAP:-0.12}"
  ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -af "silenceremove=stop_periods=-1:stop_threshold=-45dB:stop_duration=0.35:stop_silence=${GAP},atempo=${TEMPO}" voice.mp3
elif ls scene*.mp3 >/dev/null 2>&1; then
  for f in scene*.mp3; do echo "file '$PWD/$f'"; done > list.txt
  ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy voice.mp3
else
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=44100:cl=mono -t 0.35 gap.mp3
  : > list.txt; for f in line*.mp3; do echo "file '$PWD/$f'" >> list.txt; echo "file '$PWD/gap.mp3'" >> list.txt; done
  ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt voice.mp3
fi
VDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 voice.mp3)
IDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MUSIC/intro.mp3")
VOICE_START=$(python3 -c "print(max(0, $IDUR - 3.0))")
OUTRO_START=$(python3 -c "print($VOICE_START + $VDUR - 2.0)")
# intro: full level until voice starts, then duck to -12 dB and fade out over 4 s
# outro: starts at -14 dB, rises to full over 3 s after voice ends, plays out
ffmpeg -y -loglevel error \
  -i "$MUSIC/intro.mp3" -i voice.mp3 -i "$MUSIC/outro.mp3" \
  -filter_complex "\
   [0:a]aformat=sample_rates=44100:channel_layouts=stereo,volume='if(lt(t,$VOICE_START),1,0.25)':eval=frame,afade=t=out:st=$(python3 -c "print($VOICE_START+1)"):d=4[intro];\
   [1:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay=$(python3 -c "print(int($VOICE_START*1000))")|$(python3 -c "print(int($VOICE_START*1000))")[voice];\
   [2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume='if(lt(t,2.5),0.2,min(1,0.2+(t-2.5)/3))':eval=frame,adelay=$(python3 -c "print(int($OUTRO_START*1000))")|$(python3 -c "print(int($OUTRO_START*1000))")[outro];\
   [intro][voice][outro]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[mix]" \
  -map "[mix]" -ar 44100 -b:a 96k "$OUT/$SLUG.mp3"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$SLUG.mp3" | awk -v s="$SLUG" '{printf "%s: %d:%02d (voice %.0fs)\n", s, int($1/60), int($1%60), '"$VDUR"'}'
