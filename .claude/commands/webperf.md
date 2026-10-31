---
description: Führt ein Web-Performance-Audit über die Persona web-performance-auditor durch
disable-model-invocation: true
---

`/webperf` zielt speziell auf Webanwendungen. Verwende den Command nicht für Utility-Bibliotheken, CLIs oder reinen Server-Code ohne Ausgabe im Browser.

## Modus bestimmen

**Deep-Modus** — aktiviere ihn, sobald eines der folgenden Elemente vorliegt:
- Eine Lighthouse-JSON-Report-Datei (z. B. `npx lighthouse <url> --output json --output-path ./report.json` oder `npx -p chrome-devtools-mcp chrome-devtools lighthouse_audit --output-format=json` aus der Chrome-DevTools-MCP-CLI)
- Eine PageSpeed-Insights-JSON-Antwort (enthält Lighthouse + CrUX)
- Eine CrUX-API-Antwort (erfordert `CRUX_API_KEY` oder `GOOGLE_API_KEY`)
- Ein DevTools-Performance-Trace
- Eine Live-URL plus der im Harness konfigurierte MCP-Server `chrome-devtools` (der Agent kann Metriken direkt über `lighthouse_audit` und die `performance_*`-Tools erfassen)
- Die lokal aufgerufene Chrome-DevTools-MCP-CLI (über `npx -p chrome-devtools-mcp chrome-devtools <tool>` oder nach `npm i -g chrome-devtools-mcp`) — der Nutzer führt Befehle wie `chrome-devtools lighthouse_audit --output-format=json` aus und übergibt die JSON-Ausgabe an den Agent

**Quick-Modus** — Standard, wenn nichts davon vorliegt. Der Agent durchsucht den Quellcode nach strukturellen Anti-Patterns und kennzeichnet jeden Befund als `potential impact`.

## Audit durchführen

Starte den Subagent `web-performance-auditor`. Übergib ihm explizit:

- Die Dateien, Komponenten oder den Diff, die geprüft werden sollen
- Alle Artefaktpfade (Lighthouse-JSON, PSI-JSON, CrUX-Antwort, Trace) oder eingefügte JSON-Inhalte
- Die Ziel-URL oder den Seitennamen, sofern bekannt
- Einen Hinweis, welchen Modus du erwartest (Quick oder Deep), damit der Agent fehlende Eingaben meldet, falls Deep gemeint war

Der Subagent liefert eine Scorecard (nur mit belegten Werten befüllt), eine nach Priorität sortierte Liste der Befunde, positive Beobachtungen und proaktive Empfehlungen.

## Ausgabe

Gib den vollständigen Audit-Report an den Nutzer zurück. Ein Zusammenführungs- oder Synthese-Schritt ist nicht nötig — dies ist ein Command mit einer einzigen Persona.
