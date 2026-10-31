#!/bin/sh
# Prüft nur lesend, ob addyosmani/agent-skills neue Commits hat, und meldet sie als macOS-Mitteilung.
# Ändert keine Branches und kein Arbeitsverzeichnis; aktualisiert nur refs/remotes/upstream/main.
#   tools/upstream-check.sh
set -eu
cd "$(dirname "$0")/.."
git fetch -q upstream main
n=$(git rev-list --count main..upstream/main)
echo "$(date '+%Y-%m-%d %H:%M') upstream/main: $n neue Commits gegenüber main"
if [ "$n" -gt 0 ]; then
  git log --oneline main..upstream/main | head -10
  /usr/bin/osascript -e "display notification \"$n neue Upstream-Commits, Ablauf in FORK.md\" with title \"agent-skills-de\""
fi
