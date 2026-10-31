---
description: Definiert und erzwingt den Qualitätsmaßstab des Projekts – per Interview, mit sinnvollen Defaults und einer CONSTRAINTS.md
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:constraint-driven-development auf.

$ARGUMENTS

Standardverhalten ohne Argumente: Richte Constraints für dieses Repository ein.

1. **Erst erkennen.** Lies package.json / pyproject.toml / go.mod, den Test-Runner, vorhandene Lint-Konfigurationen, die aktuelle Coverage-Ausgabe, CI-Workflows und das verwendete Agent-Harness. Berichte in zwei Zeilen, was du gefunden hast. Frage nie nach etwas, das du selbst lesen kannst.

2. **Interview mit höchstens vier Fragen.** Stelle sie einzeln, jeweils mit deiner besten Vermutung und einem brauchbaren Default, sodass auch ein „Weiß ich nicht" eine funktionierende Konfiguration ergibt:
   - Welche Dimensionen über das Minimum hinaus (Coverage, Security, Performance, Accessibility, Architektur)
   - Blockieren oder warnen, wenn eine Prüfung mitten in einer Aufgabe fehlschlägt
   - Zielwerte vorgeben oder die heutigen Werte messen und halten
   - Langsamste tolerierte Prüfung, bevor die Arbeit zurückgegeben wird

3. **Schreibe CONSTRAINTS.md** im Repo-Root mit einem Floor-Abschnitt, durchgesetzten Zahlenwerten, nur gemessenen Metriken mit den heutigen Werten und einer Ausnahmentabelle mit Verantwortlichen und Ablaufdatum. Jede Zahl braucht eine genannte Begründung.

4. **Installiere, was jede gewählte Dimension braucht.** Eine Dimension mit Zahl, aber ohne Tool dahinter, ist nur ein Wunsch. Nimm das De-facto-Tool, damit bestehende Konfiguration weiter funktioniert: Semgrep für Code-Scanning, gitleaks (immer mit `--redact`) für Secrets, osv-scanner für Abhängigkeiten, axe-core für Accessibility, Lighthouse für Web Vitals, size-limit für Bundles, dependency-cruiser für Grenzen, Stryker für die Qualität der Assertions. Halte den exakten Befehl neben jeder Regel in CONSTRAINTS.md fest. Accessibility und Performance brauchen eine laufende URL; hat das Projekt keine, sage das und streiche die Dimension, statt eine Prüfung zu erfinden. Ergänze die Befehle in package.json als check:fast / check:task / check:full.

5. **Ordne jede Prüfung nach Kosten ein.** Typen, Lint und Secrets in die Edit-Schleife (Sekunden). Zugehörige Tests und Coverage der geänderten Zeilen am Ende der Aufgabe (unter 90 s). Alles andere im Review oder in der CI. Beschränke Prüfungen auf den Diff, nicht auf das gesamte Repo.

6. **Weise den Agenten darauf hin.** Füge in CLAUDE.md eine Zeile ein, die Agenten anweist, CONSTRAINTS.md zu lesen und sie nie abzuschwächen, nur damit eine Änderung durchgeht.

7. **Verifiziere.** Führe die Constraints gegen den aktuellen Branch aus. Schlägt etwas fehl, mit dem der Nutzer nicht einverstanden ist, korrigiere den Constraint sofort, statt ein Gate zurückzulassen, das die Leute zu ignorieren lernen.

Unterbefehle:
- `/constraints check` — führt die aktuellen Constraints gegen diesen Branch aus und berichtet
- `/constraints guard` — prüft den Diff auf einen aufgeweichten Qualitätsmaßstab: gesenkte Schwellenwerte, übersprungene oder gelöschte Tests, neue Suppression-Kommentare, unfertige Stubs, neue Ausnahmen
- `/constraints ratchet` — hält die heute gemessenen Werte als Untergrenze fest, die nicht unterschritten werden darf
