---
name: documentation-and-adrs
description: Hält Entscheidungen und Dokumentation fest. Verwenden, wenn eine Architekturentscheidung (ADR) oder die Begründung hinter einer Designentscheidung dokumentiert werden soll, bei Änderungen an öffentlichen APIs, beim Ausliefern von Features oder wenn Kontext festgehalten werden muss, den künftige Entwickler und Agents zum Verständnis der Codebasis brauchen. Typische Anfragen sind „schreib einen ADR dazu“, „dokumentiere diese Architekturentscheidung“, „halte fest, warum wir das so gebaut haben“, „aktualisiere die README und das Changelog“ oder „dokumentiere die öffentliche API“.
---

# Dokumentation und ADRs

## Überblick

Dokumentiere Entscheidungen, nicht nur Code. Die wertvollste Dokumentation hält das *Warum* fest: den Kontext, die Constraints und die Trade-offs, die zu einer Entscheidung geführt haben. Code zeigt, *was* gebaut wurde; Dokumentation erklärt, *warum es so gebaut wurde* und *welche Alternativen erwogen wurden*. Dieser Kontext ist unverzichtbar für künftige Menschen und Agents, die in der Codebasis arbeiten.

## Wann verwenden

- Bei einer wichtigen Architekturentscheidung
- Bei der Wahl zwischen konkurrierenden Ansätzen
- Beim Hinzufügen oder Ändern einer öffentlichen API
- Beim Ausliefern eines Features, das für Nutzer sichtbares Verhalten ändert
- Beim Onboarding neuer Teammitglieder (oder Agents) ins Projekt
- Wenn du merkst, dass du dasselbe immer wieder erklärst

**Wann NICHT verwenden:** Dokumentiere keinen offensichtlichen Code. Schreibe keine Kommentare, die nur wiederholen, was der Code ohnehin sagt. Schreibe keine Doku für Wegwerf-Prototypen.

## Architecture Decision Records (ADRs)

ADRs halten die Überlegungen hinter wichtigen technischen Entscheidungen fest. Sie sind die wertvollste Dokumentation, die du schreiben kannst.

### Wann ein ADR zu schreiben ist

- Wahl eines Frameworks, einer Bibliothek oder einer größeren Abhängigkeit
- Entwurf eines Datenmodells oder Datenbankschemas
- Auswahl einer Authentifizierungsstrategie
- Entscheidung über eine API-Architektur (REST vs. GraphQL vs. tRPC)
- Wahl zwischen Build-Tools, Hosting-Plattformen oder Infrastruktur
- Jede Entscheidung, die sich nur teuer rückgängig machen ließe

### Zuerst die bestehende Konvention übernehmen

Prüfe vor dem Anlegen eines ADR den verfügbaren Repository-Kontext auf eine etablierte Konvention: vorhandene ADRs, Projektanweisungen sowie ADR-bezogene Konfiguration oder Tooling (z. B. eine `.adr-dir`-Datei). Eine etablierte Konvention hat Vorrang vor den Standardvorgaben unten. Übernimm:

- **Ablageort und Format**, z. B. `docs/adr/*.md`, `Documentation/Decisions/*.rst`, ein MADR-Layout oder ein `adr-tools`-Setup. Übernimm das vorhandene Verzeichnis, die Dateiendung und die Auszeichnungssprache (Markdown vs. reStructuredText).
- **Nummerierung und Benennung**: Setze die bestehende Reihenfolge und das Dateinamensmuster fort (`ADR-004-Title.rst`, `0004-title.md`, …); fange nicht wieder bei 001 an und führe kein zweites Schema ein.
- **Abschnittsüberschriften**: Verwende die Überschriften des Projekts, statt ihm die Vorlage hier aufzuzwingen.

Widersprechen sich die verfügbaren Hinweise, mache den Widerspruch sichtbar, statt stillschweigend ein weiteres Schema einzuführen. Nur wenn sich keine Konvention feststellen lässt, wendest du die Standardvorlage unten an.

### ADR-Vorlage

Lege ADRs in `docs/decisions/` mit fortlaufender Nummerierung ab (sofern das Projekt nicht bereits einen anderen Ablageort nutzt, siehe oben):

```markdown
# ADR-001: Use PostgreSQL for primary database

## Status
Proposed | Accepted | Superseded by ADR-XXX | Deprecated

## Date
2025-01-15

## Context
We need a primary database for the task management application. Key requirements:
- Relational data model (users, tasks, teams with relationships)
- ACID transactions for task state changes
- Support for full-text search on task content
- Managed hosting available (for small team, limited ops capacity)

## Decision
Use PostgreSQL with Prisma ORM.

## Alternatives Considered

### MongoDB
- Pros: Flexible schema, easy to start with
- Cons: Our data is inherently relational; would need to manage relationships manually
- Rejected: Relational data in a document store leads to complex joins or data duplication

### SQLite
- Pros: Zero configuration, embedded, fast for reads
- Cons: Limited concurrent write support, no managed hosting for production
- Rejected: Not suitable for multi-user web application in production

### MySQL
- Pros: Mature, widely supported
- Cons: PostgreSQL has better JSON support, full-text search, and ecosystem tooling
- Rejected: PostgreSQL is the better fit for our feature requirements

## Consequences
- Prisma provides type-safe database access and migration management
- We can use PostgreSQL's full-text search instead of adding Elasticsearch
- Team needs PostgreSQL knowledge (standard skill, low risk)
- Hosting on managed service (Supabase, Neon, or RDS)
```

### ADR-Lebenszyklus

```
PROPOSED → ACCEPTED → (SUPERSEDED or DEPRECATED)
```

- **Lösche alte ADRs nicht.** Sie halten den historischen Kontext fest.
- Ändert sich eine Entscheidung, schreibe ein neues ADR, das auf das alte verweist und es ablöst.

## Inline-Dokumentation

### Wann kommentieren

Kommentiere das *Warum*, nicht das *Was*:

```typescript
// BAD: Restates the code
// Increment counter by 1
counter += 1;

// GOOD: Explains non-obvious intent
// Rate limit uses a fixed window that opens on the first request after the
// previous one expires, not on a clock schedule. Known gap: a client can spend
// the full limit just before a reset and again just after (2x in a moment)
if (now - windowStart > WINDOW_SIZE_MS) {
  counter = 0;
  windowStart = now;
}
```

### Wann NICHT kommentieren

```typescript
// Don't comment self-explanatory code
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// Don't leave TODO comments for things you should just do now
// TODO: add error handling  ← Just add it

// Don't leave commented-out code
// const oldImplementation = () => { ... }  ← Delete it, git has history
```

### Bekannte Stolperfallen dokumentieren

```typescript
/**
 * IMPORTANT: This function must be called before the first render.
 * If called after hydration, it causes a flash of unstyled content
 * because the theme context isn't available during SSR.
 *
 * See ADR-003 for the full design rationale.
 */
export function initializeTheme(theme: Theme): void {
  // ...
}
```

## API-Dokumentation

Für öffentliche APIs (REST, GraphQL, Bibliotheksschnittstellen):

### Inline mit Typen (bevorzugt für TypeScript)

```typescript
/**
 * Creates a new task.
 *
 * @param input - Task creation data (title required, description optional)
 * @returns The created task with server-generated ID and timestamps
 * @throws {ValidationError} If title is empty or exceeds 200 characters
 * @throws {AuthenticationError} If the user is not authenticated
 *
 * @example
 * const task = await createTask({ title: 'Buy groceries' });
 * console.log(task.id); // "task_abc123"
 */
export async function createTask(input: CreateTaskInput): Promise<Task> {
  // ...
}
```

### OpenAPI / Swagger für REST-APIs

```yaml
paths:
  /api/tasks:
    post:
      summary: Create a task
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTaskInput'
      responses:
        '201':
          description: Task created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '422':
          description: Validation error
```

## README-Struktur

Jedes Projekt sollte eine README haben, die Folgendes abdeckt:

```markdown
# Project Name

One-paragraph description of what this project does.

## Quick Start
1. Clone the repo
2. Install dependencies: `npm install`
3. Set up environment: `cp .env.example .env`
4. Run the dev server: `npm run dev`

## Commands
| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm test` | Run tests |
| `npm run build` | Production build |
| `npm run lint` | Run linter |

## Architecture
Brief overview of the project structure and key design decisions.
Link to ADRs for details.

## Contributing
How to contribute, coding standards, PR process.
```

## Changelog pflegen

Für ausgelieferte Features:

```markdown
# Changelog

## [1.2.0] - 2025-01-20
### Added
- Task sharing: users can share tasks with team members (#123)
- Email notifications for task assignments (#124)

### Fixed
- Duplicate tasks appearing when rapidly clicking create button (#125)

### Changed
- Task list now loads 50 items per page (was 20) for better UX (#126)
```

## Dokumentation für Agents

Besonderheiten für den Kontext von KI-Agents:

- **CLAUDE.md / Rules-Dateien**: Dokumentiere Projektkonventionen, damit Agents ihnen folgen
- **Spec-Dateien**: Halte Specs aktuell, damit Agents das Richtige bauen
- **ADRs**: Helfen Agents zu verstehen, warum frühere Entscheidungen getroffen wurden (verhindert, dass sie neu entschieden werden)
- **Inline-Stolperfallen**: Bewahren Agents davor, in bekannte Fallen zu tappen

## Prosa-Review

Prüfe nach der technischen Kontrolle den Text im Hinblick auf die Menschen, die ihn nutzen werden. Klarere Formulierungen dürfen die Entscheidung und ihre Grenzen nicht verändern.

1. Markiere die Details, die die Überarbeitung überstehen müssen: Namen, Zahlen und Einheiten, Befehle, Pfade, Links, Bedingungen, Trade-offs und Unsicherheiten. Prüfe sie gegen den verfügbaren Code und Entscheidungskontext; markiere alles, was du nicht belegen kannst.
2. Ersetze Standardfloskeln zur Einleitung, werbende Adjektive und wiederholte Zusammenfassungen durch die konkreten Informationen, die der Leser braucht. Ersetze eine unbelegte Behauptung nicht durch ein erfundenes Beispiel oder eine stärkere Garantie. Behalte notwendige technische Wiederholungen und die etablierte Terminologie des Projekts bei.
3. Vergleiche das überarbeitete Dokument mit dem Original und seinen Quellen. Stelle jede verlorene Einschränkung oder jeden verlorenen Vorbehalt wieder her, prüfe, dass Befehls- und Codebeispiele weiterhin wie dokumentiert funktionieren, und benenne offene Sachfragen, statt sie glattzuschleifen.

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Der Code ist selbsterklärend“ | Code zeigt, was passiert. Er zeigt nicht, warum, welche Alternativen verworfen wurden oder welche Constraints gelten. |
| „Wir schreiben die Doku, wenn die API stabil ist“ | APIs stabilisieren sich schneller, wenn du sie dokumentierst. Die Doku ist der erste Test des Designs. |
| „Niemand liest Doku“ | Agents tun es. Künftige Entwickler tun es. Du selbst in drei Monaten tust es. |
| „ADRs sind Overhead“ | Ein ADR in 10 Minuten erspart eine zweistündige Debatte über dieselbe Entscheidung sechs Monate später. |
| „Kommentare veralten“ | Kommentare zum *Warum* bleiben stabil. Kommentare zum *Was* veralten – deshalb schreibst du nur die ersteren. |

## Warnsignale

- Architekturentscheidungen ohne schriftliche Begründung
- Öffentliche APIs ohne Dokumentation oder Typen
- Eine README, die nicht erklärt, wie das Projekt gestartet wird
- Auskommentierter Code statt Löschung
- TODO-Kommentare, die seit Wochen dort stehen
- Keine ADRs in einem Projekt mit wesentlichen Architekturentscheidungen
- Dokumentation, die den Code wiederholt, statt die Absicht zu erklären

## Verifikation

Nach dem Dokumentieren:

- [ ] Für alle wichtigen Architekturentscheidungen existieren ADRs
- [ ] Die README deckt Quick Start, Befehle und Architekturüberblick ab
- [ ] API-Funktionen haben eine Dokumentation von Parametern und Rückgabetypen
- [ ] Bekannte Stolperfallen sind inline dort dokumentiert, wo sie relevant sind
- [ ] Es bleibt kein auskommentierter Code zurück
- [ ] Rules-Dateien (CLAUDE.md usw.) sind aktuell und korrekt
- [ ] Prosa-Änderungen bewahren Details der Quelle, Trade-offs der Entscheidung und Einschränkungen, ohne unbelegte Garantien hinzuzufügen
