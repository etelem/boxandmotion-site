#!/bin/bash
# Render a reel to a 1080x1920 MP4 for YouTube Shorts.
# Usage: bash mp4.sh out/X-reel.html out/X-recap.mp4
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
REEL="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUTMP4="$2"
WORK="$(mktemp -d)"
python3 "$HERE/hooks.py" "$REEL" "$WORK/copy.html"
cp "$HERE/soundtrack.mp3" "$WORK/"
mkdir "$WORK/f"
for r in "0 495" "495 990" "990 1485" "1485 1980"; do node "$HERE/export.js" "$WORK/copy.html" "$WORK/f" $r & done; wait
PAD=$(python3 -c "import re,sys;t=open('$REEL').read();print(re.search(r'--navy-mid:(#[0-9a-fA-F]{6})',t).group(1).lstrip('#'))")
ffmpeg -y -loglevel error -framerate 30 -i "$WORK/f/f%04d.png" -i "$HERE/soundtrack.mp3" \
  -filter_complex "[0:v]scale=1080:1560,pad=1080:1920:0:180:color=0x$PAD,format=yuv420p[v]" \
  -map "[v]" -map 1:a -t 66 -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 160k -shortest -movflags +faststart "$OUTMP4"
rm -rf "$WORK"
echo "$OUTMP4"
