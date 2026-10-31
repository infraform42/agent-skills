---
name: spec-driven-development
description: "Spec vor dem Code (SPEC.md) aus agent-skills. Nur verwenden, wenn der Nutzer /agent-skills-de:spec aufruft oder diesen Skill ausdrücklich nennt. Für Specs im Alltag gilt der Skill to-spec."
---

# Spec-getriebene Entwicklung

## Überblick

Schreibe eine strukturierte Spezifikation, bevor du Code schreibst. Die Spec ist die gemeinsame Single Source of Truth zwischen dir und dem menschlichen Entwickler — sie legt fest, was wir bauen, warum wir es bauen und woran wir erkennen, dass es fertig ist. Code ohne Spec ist Raten.

## Wann verwenden

- Ein neues Projekt oder Feature beginnt
- Anforderungen sind mehrdeutig oder unvollständig
- Die Änderung betrifft mehrere Dateien oder Module
- Du stehst vor einer Architekturentscheidung
- Die Umsetzung würde länger als 30 Minuten dauern

**Wann NICHT verwenden:** Einzeilige Fixes, Tippfehlerkorrekturen oder Änderungen, deren Anforderungen eindeutig und in sich abgeschlossen sind.

## Der Workflow mit Gates

Spec-Driven Development besteht aus vier Phasen, denen ein Scope-Check (Phase 0) vorangeht, der nur greift, wenn eine einzelne Anfrage mehrere unabhängig testbare Fähigkeiten bündelt. Gehe erst zur nächsten Phase über, wenn die aktuelle validiert ist.

```
SPECIFY ──→ PLAN ──→ TASKS ──→ IMPLEMENT
   │          │        │          │
   ▼          ▼        ▼          ▼
 Human      Human    Human      Human
 reviews    reviews  reviews    reviews
```

### Phase 0: Scope-Check

Die meisten Anfragen beschreiben eine einzige Fähigkeit. Trifft das hier zu, überspringe diese Phase und gehe direkt zu Specify — Phase 0 existiert für die Ausnahme, nicht für die Regel, und sie führt keine Hierarchie für Features mit nur einer Fähigkeit ein.

**Erkennung.** Zerlege vor dem Spezifizieren, wenn eine einzelne Anforderung mehrere unabhängig testbare Fähigkeiten bündelt:

- Die Anforderung nennt unterschiedliche Fähigkeiten mit jeweils eigenen Konsumenten oder Daten (z. B. Identität, Abrechnung, Benachrichtigungen, Reporting)
- Akzeptanzkriterien bilden Gruppen, die getrennt ausgeliefert und verifiziert werden könnten
- Eine Fähigkeit könnte gestrichen oder ersetzt werden, ohne die Anforderungen der anderen umzuschreiben

**Schlage eine Capability Map vor, bevor du eine Spec schreibst.** Klein und reviewbar — eine Modultabelle plus Build-Reihenfolge, kein Projektplan:

```markdown
# Capability Map: [Initiative Name]

| Module id | Responsibility | Depends on |
|---|---|---|
| identity | Accounts, sessions, SSO | — |
| billing | Plans, invoices, payments | identity |
| notifications | Email and webhook fan-out | identity |
| reporting | Usage dashboards | billing, notifications |

Build order: identity → billing, notifications → reporting
```

- **Stabile Modul-IDs.** Kebab-Case, einmal gewählt, mitten in der Initiative nie umbenannt. Specs, Pläne und nachgelagerte Commands wählen Arbeit anhand dieser IDs aus, statt zu raten, welche Spec gerade aktiv ist.
- **Abhängigkeitsrichtung ohne Zyklen.** Pfeile zeigen nur in eine Richtung. Braucht jedes von zwei Modulen das andere, sind es ein Modul.
- **Schnittstellen liegen an der Grenze.** Die Map hält fest, dass `billing` von `identity` abhängt; der Vertrag zwischen beiden gehört in die Spec des bereitstellenden Moduls (siehe `api-and-interface-design` für den Entwurf).

**Die Map hat ein Gate wie jede Phase.** Der Mensch prüft Modulgrenzen, Abhängigkeitsrichtung und Build-Reihenfolge, bevor eine Modul-Spec geschrieben wird. Eine falsche Map ist teuer; zehn Zeilen zu prüfen ist es nicht.

**Danach rekursiv pro Modul.** Durchlaufe Specify → Plan → Tasks → Implement für jedes Modul in Abhängigkeitsreihenfolge. Jedes Modul bekommt eine eigene Spec, zugeschnitten auf Ziel, Grenzen und Erfolgskriterien dieses Moduls. Speichere die freigegebene Map im Projekt-Root und die Spec jedes Moduls daneben, benannt nach der Modul-ID (`SPEC-identity.md`, `SPEC-billing.md`) — die Map, nicht das Erraten von Dateinamen, ist der Index dessen, was existiert.

### Phase 1: Specify

Beginne mit einer übergeordneten Vision. Stelle dem Menschen Rückfragen, bis die Anforderungen konkret sind.

**Lege Annahmen sofort offen.** Liste vor jedem Spec-Inhalt auf, was du annimmst:

```
ASSUMPTIONS I'M MAKING:
1. This is a web application (not native mobile)
2. Authentication uses session-based cookies (not JWT)
3. The database is PostgreSQL (based on existing Prisma schema)
4. We're targeting modern browsers only (no IE11)
→ Correct me now or I'll proceed with these.
```

Fülle mehrdeutige Anforderungen nicht stillschweigend auf. Der ganze Zweck der Spec ist, Missverständnisse aufzudecken, *bevor* Code entsteht — Annahmen sind die gefährlichste Form des Missverständnisses.

**Schreibe ein Spec-Dokument, das diese sechs Kernbereiche abdeckt:**

1. **Objective** — Was bauen wir und warum? Wer ist der Nutzer? Wie sieht Erfolg aus?

2. **Commands** — Vollständige ausführbare Befehle mit Flags, nicht nur Tool-Namen.
   ```
   Build: npm run build
   Test: npm test -- --coverage
   Lint: npm run lint -- --fix
   Dev: npm run dev
   ```

3. **Project Structure** — Wo der Quellcode liegt, wohin Tests gehören, wo Dokumentation hingehört.
   ```
   src/           → Application source code
   src/components → React components
   src/lib        → Shared utilities
   tests/         → Unit and integration tests
   e2e/           → End-to-end tests
   docs/          → Documentation
   ```

4. **Code Style** — Ein echtes Code-Snippet, das deinen Stil zeigt, schlägt drei Absätze Beschreibung. Nimm Namenskonventionen, Formatierungsregeln und Beispiele für gute Ausgabe auf.

5. **Testing Strategy** — Welches Framework, wo Tests liegen, Erwartungen an die Abdeckung, welche Teststufen für welche Belange.

6. **Boundaries** — Dreistufiges System:
   - **Always do:** Tests vor Commits ausführen, Namenskonventionen einhalten, Eingaben validieren
   - **Ask first:** Datenbankschema-Änderungen, neue Abhängigkeiten, Änderungen an der CI-Konfiguration
   - **Never do:** Secrets committen, Vendor-Verzeichnisse bearbeiten, fehlschlagende Tests ohne Freigabe entfernen

**Spec-Template:**

```markdown
# Spec: [Project/Feature Name]

## Objective
[What we're building and why. User stories or acceptance criteria.]

## Tech Stack
[Framework, language, key dependencies with versions]

## Commands
[Build, test, lint, dev — full commands]

## Project Structure
[Directory layout with descriptions]

## Code Style
[Example snippet + key conventions]

## Testing Strategy
[Framework, test locations, coverage requirements, test levels]

## Boundaries
- Always: [...]
- Ask first: [...]
- Never: [...]

## Success Criteria
[How we'll know this is done — specific, testable conditions]

## Open Questions
[Anything unresolved that needs human input]
```

**Externe Spec-Tools:** Dieser Workflow ist formatagnostisch. Nutzt das Projekt bereits OpenSpec oder ein anderes Spezifikationssystem, behalte dessen Artefaktformat und Ablagekonventionen bei, statt eine doppelte `SPEC.md` anzulegen. Dieser Skill verantwortet die Gates für Klärung, Inhalt und Freigabe; das externe Tool verantwortet, wie die freigegebene Spec dargestellt wird.

**Formuliere Anweisungen als Erfolgskriterien um.** Übersetze vage Anforderungen in konkrete Bedingungen:

```
REQUIREMENT: "Make the dashboard faster"

REFRAMED SUCCESS CRITERIA:
- Dashboard LCP < 2.5s on 4G connection
- Initial data load completes in < 500ms
- No layout shift during load (CLS < 0.1)
→ Are these the right targets?
```

So kannst du iterieren, es erneut versuchen und gezielt auf ein klares Ziel hin Probleme lösen, statt zu raten, was „schneller“ bedeutet.

**Halte nach dem Schreiben der Spec an (KRITISCH).** Sobald die Spec gespeichert ist:

1. Fasse sie zusammen und liste alle Open Questions auf.
2. Bitte den Menschen, sie freizugeben oder Änderungen anzufordern.
3. **BEENDE DEINEN ZUG SOFORT.** Starte in diesem Zug NICHT Phase 2, rufe NICHT `planning-and-task-breakdown` auf und schreibe KEINEN Code. Die Planung beginnt erst, nachdem der Mensch die Spec in einem späteren Zug freigegeben hat.

### Phase 2: Plan

Erstelle mit der validierten Spec einen technischen Umsetzungsplan:

1. Identifiziere die wichtigsten Komponenten und ihre Abhängigkeiten
2. Lege die Umsetzungsreihenfolge fest (was zuerst gebaut werden muss)
3. Halte Risiken und Gegenmaßnahmen fest
4. Bestimme, was parallel gebaut werden kann und was sequenziell sein muss
5. Definiere Verifikations-Checkpoints zwischen den Phasen

> Folge `planning-and-task-breakdown` für das Abbilden des Abhängigkeitsgraphen und die Mechanik des vertikalen Schneidens hinter diesen Schritten; dort liegt die maßgebliche Quelle. Die obigen Punkte sind eine knappe Zusammenfassung; weichen sie jemals ab, hat `planning-and-task-breakdown` Vorrang.
>
> **Ausgabekonvention:** Speichere den Plan in `tasks/plan.md` und trage die Aufgabenliste in das Ziel für Aufgabenlisten ein, das `planning-and-task-breakdown` definiert (Standard `tasks/todo.md`; Projekte können stattdessen einen externen Tracker festlegen). Lege `tasks/` an, falls es nicht existiert. Nachgelagerte Commands (`/build` usw.) erwarten diese Standardwerte.

Der Plan sollte reviewbar sein: Der Mensch sollte ihn lesen und sagen können „Ja, das ist der richtige Ansatz“ oder „Nein, ändere X.“

### Phase 3: Tasks

Zerlege den Plan in einzelne, umsetzbare Aufgaben:

- Jede Aufgabe sollte in einer einzigen fokussierten Sitzung abschließbar sein
- Jede Aufgabe hat explizite Akzeptanzkriterien
- Jede Aufgabe enthält einen Verifikationsschritt (Test, Build, manuelle Prüfung)
- Aufgaben sind nach Abhängigkeit geordnet, nicht nach gefühlter Wichtigkeit
- Keine Aufgabe sollte Änderungen an mehr als ~5 Dateien erfordern

> Folge `planning-and-task-breakdown` für die vollständige Mechanik zu Aufgabengröße und Abhängigkeitsreihenfolge; dort liegt die maßgebliche Quelle. Das Template unten ist eine knappe Inline-Form; weichen sie jemals ab, hat `planning-and-task-breakdown` Vorrang.

**Aufgaben-Template:**
```markdown
- [ ] Task: [Description]
  - Acceptance: [What must be true when done]
  - Verify: [How to confirm — test command, build, manual check]
  - Files: [Which files will be touched]
```

### Phase 4: Implement

Arbeite die Aufgaben nacheinander ab und folge dabei `skills/incremental-implementation/SKILL.md` (`incremental-implementation`) und `skills/test-driven-development/SKILL.md` (`test-driven-development`). Nutze `skills/context-engineering/SKILL.md` (`context-engineering`), um in jedem Schritt die passenden Spec-Abschnitte und Quelldateien zu laden, statt den Agenten mit der gesamten Spec zu überfluten.

## Die Spec lebendig halten

Die Spec ist ein lebendiges Dokument, kein einmaliges Artefakt:

- **Aktualisiere sie, wenn sich Entscheidungen ändern** — Stellst du fest, dass sich das Datenmodell ändern muss, aktualisiere zuerst die Spec und setze dann um.
- **Aktualisiere sie, wenn sich der Scope ändert** — Hinzugefügte oder gestrichene Features gehören in die Spec.
- **Committe die Spec** — Die Spec gehört zusammen mit dem Code in die Versionskontrolle.
- **Verweise in PRs auf die Spec** — Verlinke auf den Spec-Abschnitt, den der jeweilige PR umsetzt.

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Das ist simpel, ich brauche keine Spec“ | Simple Aufgaben brauchen keine *langen* Specs, aber trotzdem Akzeptanzkriterien. Eine Spec mit zwei Zeilen ist in Ordnung. |
| „Die Spec schreibe ich, nachdem ich es programmiert habe“ | Das ist Dokumentation, keine Spezifikation. Der Wert der Spec liegt darin, Klarheit *vor* dem Code zu erzwingen. |
| „Die Spec bremst uns aus“ | Eine Spec in 15 Minuten erspart Stunden an Nacharbeit. Wasserfall in 15 Minuten schlägt Debugging in 15 Stunden. |
| „Die Anforderungen ändern sich sowieso“ | Genau deshalb ist die Spec ein lebendiges Dokument. Eine veraltete Spec ist trotzdem besser als keine. |
| „Der Nutzer weiß, was er will“ | Auch klare Anfragen enthalten implizite Annahmen. Die Spec macht diese Annahmen sichtbar. |
| „Es ist ein großes Feature; Aufteilen ist Overhead“ | Bilden die Akzeptanzkriterien unabhängig testbare Gruppen, zwingt eine monolithische Spec jede nachgelagerte Aufgabe, über den gesamten Vertrag nachzudenken. Eine zehnzeilige Capability Map ist die günstige Alternative. |
| „Ich zerlege das später in der Planung“ | Die Planung schneidet Aufgaben innerhalb einer Spec. Dann existiert das überdimensionierte Artefakt bereits — Modulgrenzen und Abhängigkeitsrichtung müssen entschieden werden, bevor die Spec geschrieben wird, nicht danach. |

## Warnsignale

- Du fängst an, Code zu schreiben, ohne schriftliche Anforderungen
- Du fragst „Soll ich einfach anfangen zu bauen?“, bevor geklärt ist, was „fertig“ heißt
- Du setzt Features um, die in keiner Spec oder Aufgabenliste stehen
- Du triffst Architekturentscheidungen, ohne sie zu dokumentieren
- Du überspringst die Spec, weil „offensichtlich ist, was zu bauen ist“
- Du schreibst die Spec und startest im selben Zug Plan oder Code
- Eine einzelne Spec, deren Anforderungen mehrere unabhängig testbare Fähigkeiten umfassen
- Modulgrenzen oder Build-Reihenfolge werden implizit während der Umsetzung entschieden, weil vorab keine Capability Map freigegeben wurde

## Verifikation

Bestätige vor dem Übergang zur Umsetzung:

- [ ] Die Spec deckt alle sechs Kernbereiche ab
- [ ] Der Mensch hat die Spec geprüft und freigegeben
- [ ] Der Zug endete nach dem Speichern der Spec; die Freigabe kam in einem späteren Zug
- [ ] Erfolgskriterien sind spezifisch und testbar
- [ ] Boundaries (Always/Ask First/Never) sind definiert
- [ ] Die Spec ist in einer Datei im Repository gespeichert
- [ ] Bündelt die Anfrage mehrere unabhängig testbare Fähigkeiten, wurde eine Capability Map (Modul-IDs, Abhängigkeitsrichtung, Build-Reihenfolge) freigegeben, bevor eine Modul-Spec geschrieben wurde
- [ ] Jede Modul-Spec lässt sich auf eine Modul-ID in der freigegebenen Map zurückführen
