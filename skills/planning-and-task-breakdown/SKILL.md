---
name: planning-and-task-breakdown
description: "Zerlegt eine Spec in geordnete Aufgaben (tasks/plan.md) aus agent-skills. Nur verwenden, wenn der Nutzer /agent-skills-de:plan oder /agent-skills-de:build aufruft oder diesen Skill ausdrücklich nennt. Für Ticket-Zerlegung im Alltag gilt der Skill to-tickets."
---

# Planung und Aufgabenzerlegung

## Überblick

Zerlege Arbeit in kleine, verifizierbare Aufgaben mit expliziten Akzeptanzkriterien. Eine gute Aufgabenzerlegung entscheidet darüber, ob ein Agent Arbeit zuverlässig abschließt oder ein verworrenes Chaos produziert. Jede Aufgabe sollte klein genug sein, um sie in einer einzigen fokussierten Session umzusetzen, zu testen und zu verifizieren.

## Wann verwenden

- Du hast eine Spec und musst sie in umsetzbare Einheiten zerlegen
- Eine Aufgabe wirkt zu groß oder zu vage, um sie anzugehen
- Arbeit muss auf mehrere Agenten oder Sessions parallelisiert werden
- Du musst den Umfang an einen Menschen kommunizieren
- Die Reihenfolge der Umsetzung ist nicht offensichtlich

**Wann NICHT verwenden:** Änderungen an einer einzelnen Datei mit offensichtlichem Umfang oder wenn die Spec bereits klar definierte Aufgaben enthält.

## Der Planungsprozess

### Schritt 1: Plan Mode betreten

Arbeite vor dem Schreiben von Code im schreibgeschützten Modus:

- Lies die Spec und die relevanten Teile der Codebasis
- Identifiziere bestehende Muster und Konventionen
- Erfasse die Abhängigkeiten zwischen Komponenten
- Halte Risiken und Unbekannte fest

**Schreibe während der Planung KEINEN Code.** Das Ergebnis ist ein Plan-Dokument, gespeichert in `tasks/plan.md`, und eine Aufgabenliste, festgehalten im Ziel der Aufgabenliste (siehe Ausgabedateien; Standard `tasks/todo.md`) – keine Implementierung.

### Schritt 2: Den Abhängigkeitsgraphen ermitteln

Erfasse, was wovon abhängt:

```
Database schema
    │
    ├── API models/types
    │       │
    │       ├── API endpoints
    │       │       │
    │       │       └── Frontend API client
    │       │               │
    │       │               └── UI components
    │       │
    │       └── Validation logic
    │
    └── Seed data / migrations
```

Die Reihenfolge der Umsetzung folgt dem Abhängigkeitsgraphen von unten nach oben: Baue zuerst die Fundamente.

### Schritt 3: Vertikal in Scheiben schneiden

Baue nicht erst die komplette Datenbank, dann die komplette API, dann die komplette UI, sondern jeweils einen vollständigen Feature-Pfad nach dem anderen:

**Schlecht (horizontales Schneiden):**
```
Task 1: Build entire database schema
Task 2: Build all API endpoints
Task 3: Build all UI components
Task 4: Connect everything
```

**Gut (vertikales Schneiden):**
```
Task 1: User can create an account (schema + API + UI for registration)
Task 2: User can log in (auth schema + API + UI for login)
Task 3: User can create a task (task schema + API + UI for creation)
Task 4: User can view task list (query + API + UI for list view)
```

Jede vertikale Scheibe liefert funktionierende, testbare Funktionalität.

### Schritt 4: Aufgaben schreiben

Jede Aufgabe folgt dieser Struktur, egal ob sie in der Markdown-Aufgabenliste landet oder als Eintrag in einem externen Tracker (siehe Ausgabedateien):

```markdown
## Task [N]: [Short descriptive title]

**Description:** One paragraph explaining what this task accomplishes.

**Acceptance criteria:**
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]

**Verification:**
- [ ] Tests pass: [the repository's focused-test command]
- [ ] Build succeeds: [the repository's build command]
- [ ] Manual check: [description of what to verify]

**Dependencies:** [Task numbers this depends on, or "None"]

**Files likely touched:**
- `src/path/to/file.ts`
- `tests/path/to/test.ts`

**Estimated scope:** [Small: 1-2 files | Medium: 3-5 files | Large: 5+ files]
```

### Schritt 5: Ordnen und Checkpoints setzen

Ordne die Aufgaben so, dass:

1. Abhängigkeiten erfüllt sind (zuerst das Fundament bauen)
2. Jede Aufgabe das System in einem lauffähigen Zustand hinterlässt
3. Verifikations-Checkpoints nach jeweils 2–3 Aufgaben stattfinden
4. Risikoreiche Aufgaben früh kommen (fail fast)

Füge dem Ziel der Aufgabenliste explizite Checkpoints hinzu:

```markdown
## Checkpoint: After Tasks 1-3
- [ ] All tests pass
- [ ] Application builds without errors
- [ ] Core user flow works end-to-end
- [ ] Review with human before proceeding
```

## Richtlinien zur Aufgabengröße

| Größe | Dateien | Umfang | Beispiel |
|------|-------|-------|---------|
| **XS** | 1 | Einzelne Funktion oder Konfigurationsänderung | Eine Validierungsregel hinzufügen |
| **S** | 1-2 | Eine Komponente oder ein Endpoint | Einen neuen API-Endpoint hinzufügen |
| **M** | 3-5 | Eine Feature-Scheibe | Registrierungsablauf für Nutzer |
| **L** | 5-8 | Feature mit mehreren Komponenten | Suche mit Filterung und Paginierung |
| **XL** | 8+ | **Zu groß – weiter zerlegen** | — |

Ist eine Aufgabe L oder größer, zerlege sie in kleinere Aufgaben. Ein Agent arbeitet am besten mit S- und M-Aufgaben.

**Wann du eine Aufgabe weiter zerlegen solltest:**
- Sie würde mehr als eine fokussierte Session dauern (grob 2+ Stunden Agentenarbeit)
- Du kannst die Akzeptanzkriterien nicht in 3 oder weniger Stichpunkten beschreiben
- Sie berührt zwei oder mehr unabhängige Subsysteme (z. B. Auth und Billing)
- Du schreibst „und“ in den Aufgabentitel (ein Zeichen für zwei Aufgaben)

## Ausgabedateien

- **Plan-Dokument:** Speichere den Implementierungsplan in `tasks/plan.md`. Das ist immer eine Markdown-Datei – Designentscheidungen, Risiken und offene Fragen lassen sich nicht sauber auf einzelne Tracker-Issues abbilden.
- **Aufgabenliste:** Halte jede Aufgabe im **Ziel der Aufgabenliste** (unten definiert) fest.

Lege das Verzeichnis `tasks/` an, falls es nicht existiert.

**Überschreibe nie einen unvollständigen Plan.** Prüfe vor dem Schreiben von `tasks/plan.md` oder `tasks/todo.md`, ob sie bereits existieren und noch unabgehakte Aufgaben enthalten:

- Dieselbe Arbeit wird neu geplant (der Nutzer hat darum gebeten, diesen Plan zu überarbeiten oder zu erweitern) → aktualisiere die bestehenden Dateien direkt.
- Andere Arbeit → **halte an und frage nach.** Die unabgehakten Aufgaben könnten gerade in einer anderen Session in Umsetzung sein. Lösche, überschreibe oder benenne die bestehenden Dateien nicht eigenmächtig um; lege den Konflikt dar und lass den Nutzer entscheiden (erst den alten Plan abschließen, ihn ausdrücklich verwerfen oder dir sagen, wo der neue Plan liegen soll).

Dieselbe Regel gilt für ein externes Ziel der Aufgabenliste: Schließe oder lösche nie in großen Mengen offene Tracker-Einträge eines anderen Plans, um Platz für neue zu schaffen.

### Ziel der Aufgabenliste

Das Ziel der Aufgabenliste ist der Ort, an dem Aufgaben und Checkpoints festgehalten werden. Es wird einmalig hier definiert; jeder andere Verweis in diesem Skill bezieht sich darauf.

- **Standard: eine Markdown-Datei im Checklisten-Stil unter `tasks/todo.md`.** Das ist die Konvention, die der `/build`-Command und andere nachgelagerte Tools erwarten. Verwende sie, solange das Projekt nichts anderes vorgibt.
- **Externer Tracker:** Wenn die Agent-Regeln des Projekts (`CLAUDE.md`, `AGENTS.md` usw.) oder der Nutzer einen Issue-Tracker festlegen (z. B. GitHub Issues, Jira, Linear, `bd`/beads), lege stattdessen pro Aufgabe einen Tracker-Eintrag an, statt `tasks/todo.md` zu schreiben. Bilde die Struktur aus Schritt 4 auf die Felder des Trackers ab: Akzeptanzkriterien und Verifikationsschritte im Text des Eintrags, Abhängigkeiten über den Verknüpfungsmechanismus des Trackers (`bd dep add`, „blocked by“ usw.). Halte die Checkpoints aus Schritt 5 ebenfalls als Tracker-Einträge fest, oder als Checkliste im Plan-Dokument, falls der Tracker kein natürliches Äquivalent bietet.

Wenn du einen externen Tracker verwendest, vermerke das in `tasks/plan.md` (z. B. „Tasks tracked in Linear project FOO“), damit nachgelagerte Schritte und künftige Sessions wissen, wo sie nachsehen müssen, und führe den Abschnitt „Task List“ des Plan-Dokuments als geordneten Index der Tracker-IDs oder -Links statt als doppelte Checkliste.

## Vorlage für das Plan-Dokument

```markdown
# Implementation Plan: [Feature/Project Name]

## Overview
[One paragraph summary of what we're building]

## Architecture Decisions
- [Key decision 1 and rationale]
- [Key decision 2 and rationale]

## Task List

### Phase 1: Foundation
- [ ] Task 1: ...
- [ ] Task 2: ...

### Checkpoint: Foundation
- [ ] Tests pass, builds clean

### Phase 2: Core Features
- [ ] Task 3: ...
- [ ] Task 4: ...

### Checkpoint: Core Features
- [ ] End-to-end flow works

### Phase 3: Polish
- [ ] Task 5: ...
- [ ] Task 6: ...

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Ready for review

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [High/Med/Low] | [Strategy] |

## Open Questions
- [Question needing human input]
```

Wenn die Aufgaben in einem externen Tracker liegen, führe den obigen Abschnitt „Task List“ als geordneten Index der Tracker-IDs oder -Links statt als doppelte Checkliste.

## Möglichkeiten zur Parallelisierung

Wenn mehrere Agenten oder Sessions zur Verfügung stehen:

- **Sicher parallelisierbar:** Unabhängige Feature-Scheiben, Tests für bereits implementierte Features, Dokumentation
- **Muss sequenziell erfolgen:** Datenbank-Migrationen, Änderungen an geteiltem State, Abhängigkeitsketten
- **Erfordert Abstimmung:** Features, die sich einen API-Vertrag teilen (zuerst den Vertrag definieren, dann parallelisieren)

## Typische Ausreden

| Ausrede | Realität |
|---|---|
| „Ich finde das beim Umsetzen schon heraus“ | So landest du bei einem verworrenen Chaos und Nacharbeit. 10 Minuten Planung sparen Stunden. |
| „Die Aufgaben sind offensichtlich“ | Schreib sie trotzdem auf. Explizite Aufgaben bringen versteckte Abhängigkeiten und vergessene Randfälle ans Licht. |
| „Planung ist Overhead“ | Die Planung ist die Aufgabe. Implementierung ohne Plan ist nur Tippen. |
| „Ich kann alles im Kopf behalten“ | Kontextfenster sind endlich. Schriftliche Pläne überstehen Session-Grenzen und Compaction. |
| „Der alte `tasks/plan.md` ist veraltet, ich ersetze ihn einfach“ | Unabgehakte Aufgaben könnten gerade in einer anderen Session in Umsetzung sein. Das Überschreiben zerstört Arbeitsstand, der sonst nirgends existiert. Halte an und frage nach. |

## Warnsignale

- Die Umsetzung beginnt ohne schriftliche Aufgabenliste
- Ein `tasks/plan.md` oder `tasks/todo.md` mit noch unabgehakten Aufgaben für andere Arbeit wird überschrieben, ohne nachzufragen
- `tasks/todo.md` wird geschrieben, obwohl das Projekt einen externen Tracker festgelegt hat (oder Aufgaben werden auf beide verteilt)
- Aufgaben lauten „implement the feature“, ohne Akzeptanzkriterien
- Keine Verifikationsschritte im Plan
- Alle Aufgaben haben XL-Größe
- Keine Checkpoints zwischen den Aufgaben
- Die Reihenfolge der Abhängigkeiten wurde nicht berücksichtigt

## Verifikation

Bestätige vor Beginn der Umsetzung:

- [ ] Jede Aufgabe hat Akzeptanzkriterien
- [ ] Jede Aufgabe hat einen Verifikationsschritt
- [ ] Aufgabenabhängigkeiten sind identifiziert und korrekt geordnet
- [ ] Aufgaben sind im Ziel der Aufgabenliste festgehalten (Standard `tasks/todo.md`)
- [ ] Kein bestehender unvollständiger Plan wurde ohne ausdrückliche Bestätigung des Nutzers überschrieben
- [ ] Keine Aufgabe berührt mehr als ca. 5 Dateien
- [ ] Zwischen den großen Phasen gibt es Checkpoints
- [ ] Der Mensch hat den Plan geprüft und freigegeben

## Siehe auch

Akzeptanzkriterien gelten pro Aufgabe und beantworten die Frage „Haben wir das Richtige gebaut?“. Sie setzen auf der projektweiten Definition of Done auf, dem festen Maßstab, den jede Aufgabe erfüllen muss, bevor sie als erledigt gilt. Siehe `../../references/definition-of-done.md`.
