---
name: incremental-implementation
description: "Umsetzung in dünnen, prüfbaren Scheiben aus agent-skills. Nur verwenden, wenn der Nutzer /agent-skills-de:build aufruft oder diesen Skill ausdrücklich nennt. Für Umsetzung im Alltag gilt der Skill implement."
---

# Inkrementelle Umsetzung

## Überblick

Baue in dünnen vertikalen Scheiben: Setze ein Stück um, teste es, verifiziere es und erweitere dann. Implementiere nie ein ganzes Feature in einem Durchgang. Jedes Inkrement soll das System in einem funktionierenden, testbaren Zustand hinterlassen. Das ist die Ausführungsdisziplin, die große Features beherrschbar macht.

## Wann verwenden

- Bei jeder Änderung über mehrere Dateien
- Beim Bau eines neuen Features anhand einer Aufgabenaufteilung
- Beim Refaktorieren von bestehendem Code
- Immer dann, wenn du versucht bist, mehr als ~100 Zeilen zu schreiben, bevor du testest

**Wann NICHT verwenden:** Bei Änderungen in einer einzelnen Datei oder Funktion, deren Umfang ohnehin minimal ist.

## Der Inkrement-Zyklus

```
┌──────────────────────────────────────┐
│                                      │
│   Implement ──→ Test ──→ Verify ──┐  │
│       ▲                           │  │
│       └───── Commit ◄─────────────┘  │
│              │                       │
│              ▼                       │
│          Next slice                  │
│                                      │
└──────────────────────────────────────┘
```

Für jede Scheibe:

1. **Implementieren:** Setze das kleinste vollständige Stück Funktionalität um
2. **Testen:** Führe die Test-Suite aus (oder schreibe einen Test, falls keiner existiert)
3. **Verifizieren:** Stelle sicher, dass die Scheibe wie erwartet funktioniert (Tests bestehen, Build läuft durch, manuelle Prüfung)
4. **Committen:** Sichere deinen Fortschritt mit einer aussagekräftigen Nachricht (siehe `git-workflow-and-versioning` für Hinweise zu atomaren commits)
5. **Zur nächsten Scheibe übergehen:** Mach weiter, fang nicht von vorn an

## Strategien zum Schneiden

### Vertikale Scheiben (bevorzugt)

Baue einen vollständigen Pfad durch den gesamten Stack:

```
Slice 1: Create a task (DB + API + basic UI)
    → Tests pass, user can create a task via the UI

Slice 2: List tasks (query + API + UI)
    → Tests pass, user can see their tasks

Slice 3: Edit a task (update + API + UI)
    → Tests pass, user can modify tasks

Slice 4: Delete a task (delete + API + UI + confirmation)
    → Tests pass, full CRUD complete
```

Jede Scheibe liefert funktionierende Ende-zu-Ende-Funktionalität.

### Contract-First-Schneiden

Wenn Backend und Frontend parallel entwickelt werden müssen:

```
Slice 0: Define the API contract (types, interfaces, OpenAPI spec)
Slice 1a: Implement backend against the contract + API tests
Slice 1b: Implement frontend against mock data matching the contract
Slice 2: Integrate and test end-to-end
```

### Risiko-zuerst-Schneiden

Gehe zuerst das riskanteste oder unsicherste Stück an:

```
Slice 1: Prove the WebSocket connection works (highest risk)
Slice 2: Build real-time task updates on the proven connection
Slice 3: Add offline support and reconnection
```

Scheitert Scheibe 1, merkst du das, bevor du in Scheibe 2 und 3 investiert hast.

## Umsetzungsregeln

### Regel 0: Einfachheit zuerst

Frage dich, bevor du Code schreibst: „Was ist das Einfachste, das funktionieren könnte?“

Prüfe den Code nach dem Schreiben anhand dieser Fragen:
- Geht das auch mit weniger Zeilen?
- Rechtfertigen diese Abstraktionen ihre Komplexität?
- Würde ein Staff Engineer das ansehen und sagen: „Warum hast du nicht einfach …“?
- Baue ich für hypothetische künftige Anforderungen oder für die aktuelle Aufgabe?

```
SIMPLICITY CHECK:
✗ Generic EventBus with middleware pipeline for one notification
✓ Simple function call

✗ Abstract factory pattern for two similar components
✓ Two straightforward components with shared utilities

✗ Config-driven form builder for three forms
✓ Three form components
```

Drei ähnliche Codezeilen sind besser als eine voreilige Abstraktion. Implementiere zuerst die naive, offensichtlich korrekte Version. Optimiere erst, nachdem die Korrektheit durch Tests belegt ist.

### Regel 0.5: Scope-Disziplin

Fasse nur an, was die Aufgabe erfordert.

Tu das NICHT:
- Code neben deiner Änderung „aufräumen“
- Imports in Dateien refaktorieren, die du nicht änderst
- Kommentare entfernen, die du nicht vollständig verstehst
- Features einbauen, die nicht im Spec stehen, weil sie „nützlich erscheinen“
- Syntax in Dateien modernisieren, die du nur liest

Wenn dir außerhalb des Aufgabenumfangs etwas Verbesserungswürdiges auffällt, notiere es, aber behebe es nicht:

```
NOTICED BUT NOT TOUCHING:
- src/utils/format.ts has an unused import (unrelated to this task)
- The auth middleware could use better error messages (separate task)
→ Want me to create tasks for these?
```

### Regel 1: Eine Sache nach der anderen

Jedes Inkrement ändert genau eine logische Sache. Vermische keine Belange:

**Schlecht:** Ein commit, der eine neue Komponente hinzufügt, eine bestehende refaktoriert und die Build-Konfiguration aktualisiert.

**Gut:** Drei getrennte commits, einer pro Änderung.

### Regel 2: Kompilierbar bleiben

Nach jedem Inkrement muss das Projekt bauen und müssen die bestehenden Tests bestehen. Hinterlasse die Codebasis zwischen den Scheiben nie in einem kaputten Zustand.

### Regel 3: Feature-Flags für unfertige Features

Wenn ein Feature für Nutzer noch nicht bereit ist, du aber Inkremente mergen musst:

```typescript
// Feature flag for work-in-progress
const ENABLE_TASK_SHARING = process.env.FEATURE_TASK_SHARING === 'true';

if (ENABLE_TASK_SHARING) {
  // New sharing UI
}
```

So kannst du kleine Inkremente in den Main-Branch mergen, ohne unfertige Arbeit offenzulegen.

### Regel 4: Sichere Defaults

Neuer Code sollte standardmäßig sicheres, konservatives Verhalten zeigen:

```typescript
// Safe: disabled by default, opt-in
export function createTask(data: TaskInput, options?: { notify?: boolean }) {
  const shouldNotify = options?.notify ?? false;
  // ...
}
```

### Regel 5: Rollback-freundlich

Jedes Inkrement sollte unabhängig revertierbar sein:

- Additive Änderungen (neue Dateien, neue Funktionen) lassen sich leicht zurücknehmen
- Änderungen an bestehendem Code sollten minimal und fokussiert sein
- Datenbank-Migrationen sollten passende Rollback-Migrationen haben
- Lösche nichts in einem commit und ersetze es im selben commit; trenne beides

## Arbeiten mit Agents

Wenn du einen Agent anweist, inkrementell zu implementieren:

```
"Let's implement Task 3 from the plan.

Start with just the database schema change and the API endpoint.
Don't touch the UI yet — we'll do that in the next increment.

After implementing, run the repository's test and build commands to
verify nothing is broken."
```

Sei explizit darüber, was bei jedem Inkrement im Scope liegt und was NICHT.

## Inkrement-Checkliste

Verifiziere nach jedem Inkrement mit den eigenen Befehlen des Repositorys (siehe Abschnitt „Discover the Stack First“ im Skill test-driven-development):

- [ ] Die Änderung tut eine Sache und tut sie vollständig
- [ ] Alle bestehenden Tests bestehen weiterhin (der Test-Befehl des Repositorys: `npm test`, `./gradlew test`, `pytest`, ...)
- [ ] Der Build läuft durch (der Build-Befehl des Repositorys)
- [ ] Die Typprüfung besteht, sofern der Stack eine hat (`npx tsc --noEmit`, `mypy`, ...)
- [ ] Das Linting besteht (der Lint-Befehl des Repositorys)
- [ ] Die neue Funktionalität funktioniert wie erwartet
- [ ] Die Änderung ist mit einer aussagekräftigen Nachricht committet

**Hinweis:** Führe jeden Verifikationsbefehl nach einer Änderung aus, die ihn beeinflussen könnte. Wiederhole denselben Befehl nach einem erfolgreichen Lauf nicht, solange sich der Code seitdem nicht geändert hat; ein erneuter Lauf auf unverändertem Code liefert keine zusätzliche Information.

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Ich teste am Ende alles auf einmal“ | Fehler summieren sich. Ein Fehler in Scheibe 1 macht die Scheiben 2–5 falsch. Teste jede Scheibe. |
| „Alles auf einmal zu machen geht schneller“ | Es *fühlt* sich schneller an, bis etwas kaputtgeht und du nicht findest, welche von 500 geänderten Zeilen schuld ist. |
| „Die Änderungen sind zu klein für einen eigenen commit“ | Kleine commits kosten nichts. Große commits verstecken Fehler und machen Rollbacks schmerzhaft. |
| „Das Feature-Flag ergänze ich später“ | Wenn das Feature nicht fertig ist, darf es für Nutzer nicht sichtbar sein. Füge das Flag jetzt hinzu. |
| „Dieses Refactoring ist klein genug, um es mitzunehmen“ | Refactorings, die mit Features vermischt sind, erschweren Review und Debugging beider. Trenne sie. |
| „Ich führe den Build-Befehl zur Sicherheit noch einmal aus“ | Nach einem erfolgreichen Lauf bringt die Wiederholung desselben Befehls nichts, solange sich der Code nicht geändert hat. Führe ihn nach weiteren Änderungen erneut aus, nicht zur Beruhigung. |

## Warnsignale

- Mehr als 100 Zeilen Code geschrieben, ohne Tests auszuführen
- Mehrere unzusammenhängende Änderungen in einem einzigen Inkrement
- Scope-Ausweitung nach dem Motto „Ich ergänze das kurz noch“
- Test- und Verifikationsschritt überspringen, um schneller zu sein
- Build oder Tests zwischen Inkrementen kaputt
- Große uncommittete Änderungen sammeln sich an
- Abstraktionen bauen, bevor der dritte Anwendungsfall sie erfordert
- Dateien außerhalb des Aufgabenumfangs anfassen, „wenn ich schon mal dabei bin“
- Neue Utility-Dateien für einmalige Operationen anlegen
- Denselben Build-/Test-Befehl zweimal hintereinander ausführen, ohne dass sich dazwischen der Code geändert hat

## Verifikation

Nach Abschluss aller Inkremente einer Aufgabe:

- [ ] Jedes Inkrement wurde einzeln getestet und committet
- [ ] Die komplette Test-Suite besteht
- [ ] Der Build ist sauber
- [ ] Das Feature funktioniert Ende-zu-Ende wie spezifiziert
- [ ] Es bleiben keine uncommitteten Änderungen übrig

## Siehe auch

Die Verifikation pro Inkrement ist die lokale Prüfung. Bevor du eine Aufgabe als erledigt erklärst, wende die projektweite Definition of Done als letztes Quality Gate an, den festen Qualitätsmaßstab, den jedes Inkrement unabhängig von der Aufgabe erfüllen muss. Siehe `../../references/definition-of-done.md`.
