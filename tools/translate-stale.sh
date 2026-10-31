#!/bin/sh
# Übersetzt alle neuen oder veralteten Dateien (4 parallel) und setzt danach die Fork-Anpassungen.
#   tools/translate-stale.sh
set -eu
cd "$(dirname "$0")/.."
PY="${I18N_PYTHON:-$HOME/venvs/skills-i18n/bin/python}"
"$PY" -I tools/i18n.py stale | xargs -P 4 -I{} "$PY" -I tools/i18n.py translate {} || echo "Mindestens eine Datei ist fehlgeschlagen, siehe FEHLER-Zeilen"
/opt/local/bin/python3.14 -I tools/fork_manifest.py
echo "Noch offen:"; "$PY" -I tools/i18n.py stale
