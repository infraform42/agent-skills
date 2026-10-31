#!/bin/sh
# Richtet tools/upstream-check.sh als wöchentlichen launchd-Job ein (montags 09:00) oder entfernt ihn.
#   tools/install-upstream-check.sh            # einrichten
#   tools/install-upstream-check.sh --remove   # entfernen
set -eu
LABEL=de.infraform42.agent-skills-upstream
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SCRIPT="$(cd "$(dirname "$0")" && pwd)/upstream-check.sh"
LOG="$HOME/Library/Logs/agent-skills-upstream.log"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
if [ "${1:-}" = "--remove" ]; then
  /bin/rm -f "$PLIST"
  echo "entfernt: $LABEL"
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/sh</string><string>$SCRIPT</string></array>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/local/bin:/usr/bin:/bin</string></dict>
  <key>StartCalendarInterval</key><dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF
plutil -lint "$PLIST"
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "eingerichtet: $LABEL (montags 09:00), Log: $LOG"
