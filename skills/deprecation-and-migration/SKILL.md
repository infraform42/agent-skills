---
name: deprecation-and-migration
description: "Steuert Abkündigung (Deprecation) und Migration: Entfernen alter Systeme, APIs oder Features sowie das sichere Umziehen von Nutzern auf eine neue Implementierung. Verwenden, wenn alte Systeme, APIs oder Features entfernt werden, wenn Nutzer von einer Implementierung auf eine andere migriert werden, wenn ein Datenbankschema in Produktion migriert wird (z. B. Spalte umbenennen oder löschen ohne Downtime, expand/contract) oder wenn entschieden werden muss, ob bestehender Code weiter gepflegt oder abgekündigt wird. „kündige die alte API ab“, „plane die Migration auf das neue System“, „benenne die Spalte ohne Downtime um“, „sollen wir das Legacy-System weiter pflegen?“, „entferne den alten Code sauber“"
---

# Abkündigung und Migration

## Überblick

Code ist eine Verbindlichkeit, kein Vermögenswert. Jede Codezeile verursacht laufende Wartungskosten: Bugs müssen behoben, Abhängigkeiten aktualisiert, Sicherheitspatches eingespielt und neue Entwickler eingearbeitet werden. Abkündigung (Deprecation) ist die Disziplin, Code zu entfernen, der seinen Unterhalt nicht mehr verdient; Migration ist der Prozess, Nutzer sicher vom Alten zum Neuen zu bringen.

Die meisten Engineering-Organisationen sind gut darin, Dinge zu bauen. Wenige sind gut darin, sie wieder zu entfernen. Dieser Skill schließt diese Lücke.

## Wann verwenden

- Ein altes System, eine alte API oder Bibliothek durch eine neue ersetzen
- Ein nicht mehr benötigtes Feature einstellen
- Doppelte Implementierungen konsolidieren
- Toten Code entfernen, der niemandem gehört, von dem aber alle abhängen
- Den Lebenszyklus eines neuen Systems planen (die Abkündigungsplanung beginnt beim Design)
- Entscheiden, ob ein Legacy-System weiter gepflegt wird oder ob sich eine Migration lohnt

## Grundprinzipien

### Code ist eine Verbindlichkeit

Jede Codezeile verursacht laufende Kosten: Sie braucht Tests, Dokumentation, Sicherheitspatches, Abhängigkeits-Updates und kognitiven Aufwand für jeden, der in der Nähe arbeitet. Der Wert von Code ist die Funktionalität, die er bietet, nicht der Code selbst. Lässt sich dieselbe Funktionalität mit weniger Code, weniger Komplexität oder besseren Abstraktionen bereitstellen, sollte der alte Code weg.

### Hyrums Gesetz macht das Entfernen schwer

Mit genügend Nutzern wird von jedem beobachtbaren Verhalten irgendjemand abhängig – einschließlich Bugs, Timing-Eigenheiten und undokumentierter Nebeneffekte. Deshalb erfordert eine Abkündigung aktive Migration und nicht nur eine Ankündigung. Nutzer können nicht „einfach wechseln“, wenn sie von Verhalten abhängen, das der Ersatz nicht nachbildet.

### Die Abkündigungsplanung beginnt beim Design

Frage beim Bau von etwas Neuem: „Wie würden wir das in 3 Jahren wieder entfernen?“ Systeme mit sauberen Schnittstellen, Feature-Flags und minimaler Oberfläche lassen sich leichter abkündigen als Systeme, die Implementierungsdetails überall durchsickern lassen.

## Die Abkündigungsentscheidung

Beantworte vor jeder Abkündigung diese Fragen:

```
1. Does this system still provide unique value?
   → If yes, maintain it. If no, proceed.

2. How many users/consumers depend on it?
   → Quantify the migration scope.

3. Does a replacement exist?
   → If no, build the replacement first. Don't deprecate without an alternative.

4. What's the migration cost for each consumer?
   → If trivially automated, do it. If manual and high-effort, weigh against maintenance cost.

5. What's the ongoing maintenance cost of NOT deprecating?
   → Security risk, engineer time, opportunity cost of complexity.
```

## Verpflichtende vs. empfehlende Abkündigung

| Typ | Wann verwenden | Mechanismus |
|------|-------------|-----------|
| **Empfehlend (Advisory)** | Die Migration ist optional, das alte System ist stabil | Warnungen, Dokumentation, sanfte Hinweise. Nutzer migrieren in ihrem eigenen Tempo. |
| **Verpflichtend (Compulsory)** | Das alte System hat Sicherheitsprobleme, blockiert den Fortschritt oder die Wartungskosten sind nicht tragbar | Harte Frist. Das alte System wird zum Datum X entfernt. Migrationswerkzeuge bereitstellen. |

**Standardmäßig empfehlend vorgehen.** Verpflichtend nur, wenn Wartungskosten oder Risiko die erzwungene Migration rechtfertigen. Eine verpflichtende Abkündigung erfordert Migrationswerkzeuge, Dokumentation und Support – eine bloße Fristankündigung reicht nicht.

## Der Migrationsprozess

### Schritt 1: Den Ersatz bauen

Kündige nichts ab, ohne eine funktionierende Alternative zu haben. Der Ersatz muss:

- Alle kritischen Anwendungsfälle des alten Systems abdecken
- Dokumentation und Migrationsleitfäden haben
- Sich in Produktion bewährt haben (nicht nur „theoretisch besser“ sein)

### Schritt 2: Ankündigen und dokumentieren

```markdown
## Deprecation Notice: OldService

**Status:** Deprecated as of 2025-03-01
**Replacement:** NewService (see migration guide below)
**Removal date:** Advisory — no hard deadline yet
**Reason:** OldService requires manual scaling and lacks observability.
            NewService handles both automatically.

### Migration Guide
1. Replace `import { client } from 'old-service'` with `import { client } from 'new-service'`
2. Update configuration (see examples below)
3. Run the migration verification script: `npx migrate-check`
```

### Schritt 3: Schrittweise migrieren

Migriere Konsumenten einzeln, nicht alle auf einmal. Für jeden Konsumenten:

```
1. Identify all touchpoints with the deprecated system
2. Update to use the replacement
3. Verify behavior matches (tests, integration checks)
4. Remove references to the old system
5. Confirm no regressions
```

**Die Churn-Regel:** Wenn dir die Infrastruktur gehört, die abgekündigt wird, bist du dafür verantwortlich, deine Nutzer zu migrieren – oder abwärtskompatible Updates bereitzustellen, die keine Migration erfordern. Kündige nicht an und überlasse die Nutzer dann sich selbst.

### Schritt 4: Das alte System entfernen

Erst nachdem alle Konsumenten migriert sind:

```
1. Verify zero active usage (metrics, logs, dependency analysis)
2. Remove the code
3. Remove associated tests, documentation, and configuration
4. Remove the deprecation notices
5. Celebrate — removing code is an achievement
```

## Migrationsmuster

### Strangler-Muster

Betreibe altes und neues System parallel. Leite den Traffic schrittweise vom alten zum neuen System um. Sobald das alte System 0 % des Traffics verarbeitet, entferne es.

```
Phase 1: New system handles 0%, old handles 100%
Phase 2: New system handles 10% (canary)
Phase 3: New system handles 50%
Phase 4: New system handles 100%, old system idle
Phase 5: Remove old system
```

### Adapter-Muster

Erstelle einen Adapter, der Aufrufe der alten Schnittstelle in die neue Implementierung übersetzt. Konsumenten nutzen weiter die alte Schnittstelle, während du das Backend migrierst.

```typescript
// Adapter: old interface, new implementation
class LegacyTaskService implements OldTaskAPI {
  constructor(private newService: NewTaskService) {}

  // Old method signature, delegates to new implementation
  getTask(id: number): OldTask {
    const task = this.newService.findById(String(id));
    return this.toOldFormat(task);
  }

  // Translate the new shape back into what old consumers expect
  private toOldFormat(task: Task): OldTask {
    return { id: Number(task.id), title: task.title, done: task.status === 'done' };
  }
}
```

### Feature-Flag-Migration

Nutze Feature-Flags, um Konsumenten einzeln vom alten auf das neue System umzuschalten:

```typescript
function getTaskService(userId: string): TaskService {
  if (featureFlags.isEnabled('new-task-service', { userId })) {
    return new NewTaskService();
  }
  return new OldTaskService();
}
```

### Datenbankschema-Migrationen (Expand/Contract)

Eine Schemaänderung ist die riskanteste Migration, weil sich Daten als Einziges nicht durch das Zurücksetzen eines Deployments per Rollback wiederherstellen lassen. Der typische Fehler ist, die Schemaänderung an die Codeänderung zu koppeln: Wer eine Spalte im selben Release umbenennt, in dem der neue Name verwendet wird, hat im Rollout-Fenster – wenn alter und neuer Code gleichzeitig laufen – immer eine Seite, die eine nicht existierende Spalte abfragt. Die Lösung: **Ändere eine Spalte nie an Ort und Stelle.** Migriere in additiven Phasen, sodass alter und neuer Code in jedem Schritt gültig sind.

```
EXPAND ──────────────→ MIGRATE ──────────────→ CONTRACT
add the new column,    backfill existing rows,  once no code reads the
nullable, alongside    dual-write old+new from  old column, drop it in
the old one            the app                  a later, separate deploy
```

**Durchgespieltes Beispiel – `name` in `full_name` umbenennen:**

1. **Expand.** Füge `full_name` als nullable hinzu. Deploye. (Alter Code ignoriert sie; nichts geht kaputt.)
2. **Dual-write.** Die App schreibt bei jedem Insert/Update sowohl `name` als auch `full_name`. Deploye.
3. **Backfill.** Kopiere `name → full_name` für bestehende Zeilen in Batches, damit die Tabelle nicht gesperrt wird.
4. **Lesezugriffe umstellen.** Richte die App auf `full_name` aus, schreibe weiterhin beides. Deploye und lass es sich bewähren.
5. **Contract.** Höre auf, `name` zu schreiben, und lösche die Spalte dann – in einem *separaten, späteren* Deployment.

Jeder Schritt ist einzeln deploybar und umkehrbar: Verhält sich Schritt 4 falsch, setzt du den Code zurück, und `full_name` wird weiterhin befüllt. Behandle jede Phase als dünne vertikale Scheibe – siehe den Skill `incremental-implementation`.

**Regeln:**
- **Additiv zuerst, destruktiv zuletzt und allein.** Hinzufügungen (neue nullable Spalte, neue Tabelle, neuer Index) sind in jedem Deployment sicher; Drops und Umbenennungen bekommen ein eigenes Deployment, *nachdem* kein Code mehr auf die alte Struktur verweist.
- **Jede Migration hat einen getesteten Down-Pfad.** Eine Migration, die du nicht umkehren kannst, ist ein Deployment, das du nicht per Rollback zurücknehmen kannst. Schreibe und führe das `down` aus, bevor du mergst.
- **Backfill in Batches, abseits des Hot Path.** Ein einzelnes `UPDATE` über Millionen Zeilen sperrt die Tabelle; zerlege es in Chunks und drossele es.
- **Große Indizes bauen, ohne Schreibzugriffe zu blockieren** (z. B. Postgres `CREATE INDEX CONCURRENTLY`).
- **Entkopple per Feature-Flag vom Code**, wenn der Cutover riskant ist – genau wie im obigen Muster Feature-Flag-Migration.

## Zombie-Code

Zombie-Code ist Code, der niemandem gehört, von dem aber alle abhängen. Er wird nicht aktiv gepflegt, hat keinen klaren Verantwortlichen und sammelt Sicherheitslücken und Kompatibilitätsprobleme an. Anzeichen:

- Seit über 6 Monaten keine Commits, aber es gibt aktive Konsumenten
- Kein zugewiesener Maintainer oder Team
- Fehlschlagende Tests, die niemand repariert
- Abhängigkeiten mit bekannten Schwachstellen, die niemand aktualisiert
- Dokumentation, die auf nicht mehr existierende Systeme verweist

**Reaktion:** Weise entweder einen Verantwortlichen zu und pflege den Code ordentlich, oder kündige ihn mit einem konkreten Migrationsplan ab. Zombie-Code darf nicht im Schwebezustand bleiben – er bekommt entweder Investitionen oder wird entfernt.

## Typische Ausreden

| Ausrede | Realität |
|---|---|
| „Es funktioniert noch, warum entfernen?“ | Funktionierender Code, den niemand pflegt, sammelt Sicherheitsschulden und Komplexität an. Die Wartungskosten wachsen unbemerkt. |
| „Jemand könnte es später noch brauchen“ | Wird es später gebraucht, lässt es sich neu bauen. Ungenutzten Code „für alle Fälle“ zu behalten kostet mehr als ein Neubau. |
| „Die Migration ist zu teuer“ | Vergleiche die Migrationskosten mit den laufenden Wartungskosten über 2–3 Jahre. Langfristig ist die Migration meist günstiger. |
| „Wir kündigen es ab, wenn das neue System fertig ist“ | Die Abkündigungsplanung beginnt beim Design. Bis das neue System fertig ist, gibt es neue Prioritäten. Plane jetzt. |
| „Die Nutzer migrieren von selbst“ | Tun sie nicht. Stelle Werkzeuge, Dokumentation und Anreize bereit – oder erledige die Migration selbst (die Churn-Regel). |
| „Wir können beide Systeme unbegrenzt weiterbetreiben“ | Zwei Systeme für dieselbe Aufgabe bedeuten doppelte Kosten für Wartung, Tests, Dokumentation und Einarbeitung. |
| „Benenn die Spalte einfach um, das ist eine Zeile“ | Während des Rollouts laufen alter und neuer Code gleichzeitig – einer fragt eine nicht mehr existierende Spalte ab. Expand/Contract, niemals an Ort und Stelle umbenennen. |
| „Ich füge die Spalte hinzu und lösche die alte in derselben Migration“ | Das koppelt ein sicheres Hinzufügen an ein destruktives Löschen. Drops bekommen ein eigenes Deployment, nachdem kein Code mehr auf die alte Struktur verweist. |
| „Den Rollback schreiben wir, falls wir ihn brauchen“ | Eine Migration ohne Down-Pfad ist ein Deployment, das du nicht zurücknehmen kannst. Schreibe und führe das `down` aus, bevor du mergst. |

## Warnsignale

- Abgekündigte Systeme ohne verfügbaren Ersatz
- Abkündigungsankündigungen ohne Migrationswerkzeuge oder Dokumentation
- „Weiche“ Abkündigung, die seit Jahren nur empfehlend ist und keine Fortschritte macht
- Zombie-Code ohne Verantwortlichen und mit aktiven Konsumenten
- Neue Features, die zu einem abgekündigten System hinzugefügt werden (investiere stattdessen in den Ersatz)
- Abkündigung ohne Messung der aktuellen Nutzung
- Code entfernen, ohne zu verifizieren, dass es keine aktiven Konsumenten mehr gibt
- Eine Schemaänderung und der davon abhängige Code werden im selben Deployment ausgeliefert
- Eine Spalte wird an Ort und Stelle umbenannt oder gelöscht statt per Expand/Contract
- Eine Migration wird ohne getesteten Down-Pfad gemergt, oder ein Backfill sperrt die Tabelle

## Verifikation

Nach Abschluss einer Abkündigung:

- [ ] Der Ersatz hat sich in Produktion bewährt und deckt alle kritischen Anwendungsfälle ab
- [ ] Ein Migrationsleitfaden mit konkreten Schritten und Beispielen existiert
- [ ] Alle aktiven Konsumenten wurden migriert (verifiziert über Metriken/Logs)
- [ ] Alter Code, Tests, Dokumentation und Konfiguration sind vollständig entfernt
- [ ] Im Codebestand verweist nichts mehr auf das abgekündigte System
- [ ] Die Abkündigungshinweise sind entfernt (sie haben ihren Zweck erfüllt)

Nach einer Datenbankschema-Migration:

- [ ] Die Änderung wird in additiven Phasen ausgeliefert (expand → backfill → contract), nicht als einzelne Änderung an Ort und Stelle
- [ ] Alter und neuer Code sind in jedem Deployment-Schritt gegen das Schema gültig
- [ ] Jede Migration hat einen getesteten Down-Pfad; Backfills laufen in gedrosselten Batches
- [ ] Destruktive Schritte (Drop/Rename) werden in einem eigenen Deployment ausgeliefert, nachdem kein Code mehr auf die alte Struktur verweist
