#!/bin/bash
# Render a deep-dive animation (step-back, coach's board) to a 1080x1920 MP4 for YouTube Shorts.
# Usage: bash kit/short_mp4.sh src/anim/X.html out.mp4 [speeds, default "1" = the looping house standard]
# Music: MUSIC=path/to/track (default kit/soundtrack.mp3), MUSIC_START=seconds into the track (default 0).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PAGE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUTMP4="$2"; SPEEDS="${3:-1}"
WORK="$(mktemp -d)"; mkdir "$WORK/f"
N=$(node "$HERE/short_frames.js" "$PAGE" "$WORK/f" 0 0 "$SPEEDS" | sed -n 's/^frames //p')
Q=$(( (N + 3) / 4 ))
for i in 0 1 2 3; do node "$HERE/short_frames.js" "$PAGE" "$WORK/f" $((i*Q)) $(((i+1)*Q)) "$SPEEDS" >/dev/null & done; wait
DUR=$(python3 -c "print(round($N/30,2))")
ffmpeg -y -loglevel error -framerate 30 -i "$WORK/f/f%04d.png" -i "${MUSIC:-$HERE/soundtrack.mp3}" \
  -filter_complex "[0:v]scale=1080:1920,format=yuv420p[v];[1:a]atrim=${MUSIC_START:-0}:$(python3 -c "print(${MUSIC_START:-0}+$DUR)"),asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.6,afade=t=out:st=$(python3 -c "print(max(0,$DUR-1.5))"):d=1.5[a]" \
  -map "[v]" -map "[a]" -t "$DUR" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 160k -movflags +faststart "$OUTMP4"
rm -rf "$WORK"
echo "$OUTMP4 ($N frames, ${DUR}s)"
