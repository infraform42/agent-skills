---
description: Implementiert Aufgaben inkrementell – bauen, testen, verifizieren, committen. Mit dem Zusatz "auto" läuft der gesamte Plan in einem einzigen freigegebenen Durchgang.
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:incremental-implementation zusammen mit agent-skills-de:test-driven-development auf.

## Modi

- **`/build`** — Implementiere die *nächste* offene Aufgabe und halte dann an (vorsichtig, jeweils eine Scheibe).
- **`/build auto`** — Erzeuge bei Bedarf den Plan, hole eine einmalige Freigabe ein und implementiere dann *jede* Aufgabe, ohne zwischendurch anzuhalten.

`$ARGUMENTS` wählt den Modus. Behandle `auto` (kanonisch) oder `all` als autonomen Modus; alles andere (oder leer) ist der Standardmodus mit einer einzelnen Aufgabe. Hinweis: Der autonome Modus ist nicht schneller *pro Aufgabe* – er durchläuft dieselbe testgetriebene Schleife –, er entfällt lediglich das manuelle Weiterschalten *zwischen* den Aufgaben.

## Standard: eine Aufgabe

Wähle die nächste offene Aufgabe aus dem Plan. Danach:

1. Lies die Akzeptanzkriterien der Aufgabe
2. Lade den relevanten Kontext (bestehender Code, Muster, Typen)
3. Schreibe einen fehlschlagenden Test für das erwartete Verhalten (RED)
4. Implementiere den minimalen Code, damit der Test besteht (GREEN)
5. Führe die komplette Test-Suite aus, um Regressionen zu erkennen
6. Führe den Build aus, um die Kompilierung zu verifizieren
7. Committe mit einer aussagekräftigen Nachricht
8. Markiere die Aufgabe als erledigt und halte an

## Autonom: der gesamte Plan (`/build auto`)

Nutze das, sobald eine Spec existiert und du Planung und Umsetzung in einem Durchlauf zusammenfassen willst. Es entfällt das manuelle Weiterschalten zwischen den Aufgaben – **nicht** die Verifikation. Jede Aufgabe braucht weiterhin einen bestandenen Test und einen eigenen commit.

1. **Spec voraussetzen.** Suche ausschließlich an bekannten Pfaden nach einer Spec: `SPEC.md` im Repo-Root, `docs/SPEC.md` oder eine Datei unter `spec/`. Eine README oder ein beliebiges Dokument zählt **nicht**. Existiert keine, brich ab und weise den Nutzer an, zuerst `/spec` auszuführen – erfinde keine Anforderungen.
2. **Sauberen Ausgangszustand herstellen.** Führe `git status --porcelain` aus. Gibt es uncommittete Änderungen außerhalb der erwarteten Planungsartefakte (`SPEC.md`, `docs/SPEC.md`, `spec/*`, `tasks/plan.md`, `tasks/todo.md`), brich ab und bitte den Nutzer, zu committen, zu stashen oder zu bestätigen, wie damit umzugehen ist. Die autonomen commits pro Aufgabe dürfen keine unbeteiligte lokale Arbeit mitnehmen, sonst gilt die Garantie eines sauberen Rollbacks nicht mehr.
3. **Bei Bedarf planen.** Existiert keine `tasks/plan.md`, rufe agent-skills-de:planning-and-task-breakdown auf, um eine zu erzeugen.
4. **Einziger Checkpoint.** Lege den vollständigen Plan vor und warte auf eine eindeutige Zustimmung (z. B. „approve“, „go“, „yes“). Behandle zögerliche Antworten („sieht vernünftig aus“, „na gut“) als **nicht** freigegeben. Das ist die einzige menschliche Hürde – nach der Freigabe läuft alles autonom. Hast du `tasks/plan.md` erzeugt, committe sie jetzt als einen einzelnen vorbereitenden commit, damit sie nicht in den commit der ersten Aufgabe einfließt.
5. **Jede Aufgabe in Abhängigkeitsreihenfolge ausführen.** Nutze die deklarierten Abhängigkeiten jeder Aufgabe; sind sie nicht explizit angegeben, arbeite in der Reihenfolge, in der der Plan die Aufgaben aufführt. Durchlaufe für jede Aufgabe die vollständige Standardschleife von oben (RED → GREEN → Regression → Build → commit → als erledigt markieren). Stage nur die Dateien, die diese Aufgabe berührt hat, plus ihr Statusupdate – niemals blind `git add -A` – und erstelle pro Aufgabe einen commit, damit jeder Punkt ein sauberer Rollback-Punkt ist.
6. **Halte an und frage den Nutzer** (nicht einfach durchdrücken), wenn:
   - ein Test nicht zum Bestehen gebracht werden kann oder der Build ohne naheliegende Lösung bricht → folge agent-skills-de:debugging-and-error-recovery
   - die Spec mehrdeutig ist oder eine Aufgabe eine Entscheidung erfordert, die die Spec nicht abdeckt
   - eine Aufgabe hochriskant oder irreversibel ist – Änderungen an Auth/Berechtigungen, destruktive Daten-Migrationen, Zahlungen, Löschungen, Deployments, alles, was Secrets berührt, **oder alles, was du nicht mit `git revert` rückgängig machen kannst** → folge agent-skills-de:doubt-driven-development und hole eine ausdrückliche Freigabe ein, bevor du fortfährst

   Nachdem der Nutzer ein Hindernis gelöst hat, ruft er `/build auto` erneut auf – der Lauf setzt bei der nächsten offenen Aufgabe fort.
7. **Am Ende zusammenfassen:** erledigte Aufgaben, hinzugefügte Tests, erstellte commits und alles, was übersprungen, markiert oder dem Nutzer überlassen wurde.

Schlägt ein Schritt fehl, folge dem Skill agent-skills-de:debugging-and-error-recovery.
