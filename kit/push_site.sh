#!/bin/bash
# Commit new reels, rebuild the site on top of the latest main, and push. Safe when several recap runs push at once.
# Usage (from the repo root): bash kit/push_site.sh "Recap reels: 2026-11-07 (SAS-POR, DEN-IND)"
set -e
MSG="$1"
git add -A reels data/writeups kit/shorts kit/boards/candidates src/anim
git commit -qm "$MSG" || { echo "no new reels to commit"; exit 0; }
for try in 1 2 3 4 5 6; do
  git pull -q --rebase origin main
  python3 build.py >/dev/null
  git add -A dist
  REBUILT=0; git commit -qm "Rebuild site" && REBUILT=1
  if git push -q origin main; then echo "pushed on try $try"; exit 0; fi
  if [ "$REBUILT" = 1 ]; then git reset -q --hard HEAD~1; fi   # drop only the rebuild commit; rebuild again after the next pull
  sleep $((try * 15))
done
echo "PUSH FAILED after 6 tries"; exit 1
