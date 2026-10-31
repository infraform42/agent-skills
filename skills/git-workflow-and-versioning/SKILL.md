---
name: git-workflow-and-versioning
description: "Strukturiert Git-Workflow-Praktiken. Verwenden beim Committen, Branchen und Auflösen von Konflikten, beim Aufteilen unaufgeräumter Arbeit im Working Tree in saubere atomare Commits, beim Öffnen oder Reviewen eines Pull Requests (PR), beim Pushen auf ein Remote oder bei der Organisation paralleler Arbeitsstränge. Verwenden bei Releases, bei der Wahl des Semantic-Version-Bumps, beim Taggen oder Schreiben eines Changelogs. Verwenden, wenn eine Commit-Message oder ein Changelog-Eintrag geschrieben oder eine Änderung in Commits aufgeteilt werden soll, auch wenn der Diff inline eingefügt ist und die Message einfach wirkt. Auch bei Anfragen wie „schreib die Commit-Message dazu“, „teile das in saubere Commits auf“, „löse den Merge-Konflikt“, „tagge den Release“, „schreib den Changelog-Eintrag“."
---

# Git-Workflow und Versionierung

## Überblick

Git ist dein Sicherheitsnetz. Behandle Commits als Speicherpunkte, Branches als Sandboxes und die Historie als Dokumentation. Wenn KI-Agenten Code in hohem Tempo erzeugen, ist disziplinierte Versionskontrolle der Mechanismus, der Änderungen überschaubar, reviewbar und umkehrbar hält.

## Wann verwenden

Immer. Jede Codeänderung läuft über Git.

## Grundprinzipien

### Trunk-Based Development (empfohlen)

Halte `main` jederzeit deploybar. Arbeite in kurzlebigen Feature-Branches, die innerhalb von 1–3 Tagen zurückgemergt werden. Langlebige Entwicklungs-Branches sind versteckte Kosten: Sie laufen auseinander, erzeugen Merge-Konflikte und verzögern die Integration. Die DORA-Forschung zeigt durchgängig, dass Trunk-Based Development mit leistungsstarken Engineering-Teams korreliert.

```
main ──●──●──●──●──●──●──●──●──●──  (always deployable)
        ╲      ╱  ╲    ╱
         ●──●─╱    ●──╱    ← short-lived feature branches (1-3 days)
```

Das ist der empfohlene Standard. Teams, die Gitflow oder langlebige Branches nutzen, können die Prinzipien (atomare Commits, kleine Änderungen, aussagekräftige Messages) auf ihr Branching-Modell übertragen – die Commit-Disziplin ist wichtiger als die konkrete Branching-Strategie.

- **Dev-Branches kosten.** Mit jedem Tag, den ein Branch lebt, wächst das Merge-Risiko.
- **Release-Branches sind in Ordnung.** Etwa, wenn du einen Release stabilisieren musst, während main weiterläuft.
- **Feature-Flags > lange Branches.** Deploye unfertige Arbeit lieber hinter Flags, statt sie wochenlang auf einem Branch zu halten.

### 1. Früh und oft committen

Jedes gelungene Inkrement bekommt einen eigenen Commit. Sammle keine großen uncommitteten Änderungen an.

```
Work pattern:
  Implement slice → Test → Verify → Commit → Next slice

Not this:
  Implement everything → Hope it works → Giant commit
```

Commits sind Speicherpunkte. Wenn die nächste Änderung etwas kaputt macht, kannst du sofort zum letzten funktionierenden Stand zurückkehren.

### 2. Atomare Commits

Jeder Commit tut genau eine logische Sache:

```
# Good: Each commit is self-contained
git log --oneline
a1b2c3d Add task creation endpoint with validation
d4e5f6g Add task creation form component
h7i8j9k Connect form to API and add loading state
m1n2o3p Add task creation tests (unit + integration)

# Bad: Everything mixed together
git log --oneline
x1y2z3a Add task feature, fix sidebar, update deps, refactor utils
```

### 3. Aussagekräftige Messages

Commit-Messages erklären das *Warum*, nicht nur das *Was*:

```
# Good: Explains intent
feat: add email validation to registration endpoint

Prevents invalid email formats from reaching the database.
Uses Zod schema validation at the route handler level,
consistent with existing validation patterns in auth.ts.

# Bad: Describes what's obvious from the diff
update auth.ts
```

**Format:**
```
<type>: <short description>

<optional body explaining why, not what>
```

**Typen:**
- `feat` — Neues Feature
- `fix` — Bugfix
- `refactor` — Codeänderung, die weder einen Bug behebt noch ein Feature hinzufügt
- `test` — Tests hinzufügen oder aktualisieren
- `docs` — Nur Dokumentation
- `chore` — Tooling, Abhängigkeiten, Konfiguration

### 4. Belange getrennt halten

Vermische keine Formatierungsänderungen mit Verhaltensänderungen. Vermische keine Refactorings mit Features. Jede Art von Änderung gehört in einen eigenen Commit – idealerweise in einen eigenen PR:

```
# Good: Separate concerns
git commit -m "refactor: extract validation logic to shared utility"
git commit -m "feat: add phone number validation to registration"

# Bad: Mixed concerns
git commit -m "refactor validation and add phone number field"
```

**Trenne Refactoring von Feature-Arbeit.** Eine Refactoring-Änderung und eine Feature-Änderung sind zwei verschiedene Änderungen – reiche sie getrennt ein. So lässt sich jede Änderung leichter reviewen, zurückrollen und in der Historie nachvollziehen. Kleine Aufräumarbeiten (etwa eine Variable umbenennen) können nach Ermessen des Reviewers in einem Feature-Commit mitlaufen.

### 5. Änderungen angemessen dimensionieren

Ziel sind ~100 Zeilen pro Commit/PR. Änderungen über ~1000 Zeilen solltest du aufteilen. Wie du große Änderungen zerlegst, steht in den Aufteilungsstrategien von `code-review-and-quality`.

```
~100 lines  → Easy to review, easy to revert
~300 lines  → Acceptable for a single logical change
~1000 lines → Split into smaller changes
```

## Branching-Strategie

### Feature-Branches

```
main (always deployable)
  │
  ├── feature/task-creation    ← One feature per branch
  ├── feature/user-settings    ← Parallel work
  └── fix/duplicate-tasks      ← Bug fixes
```

- Zweige von `main` ab (oder vom Default-Branch des Teams)
- Halte Branches kurzlebig (Merge innerhalb von 1–3 Tagen) – langlebige Branches sind versteckte Kosten
- Lösche Branches nach dem Merge
- Bevorzuge Feature-Flags gegenüber langlebigen Branches bei unfertigen Features

### Branch-Namen

```
feature/<short-description>   → feature/task-creation
fix/<short-description>       → fix/duplicate-tasks
chore/<short-description>     → chore/update-deps
refactor/<short-description>  → refactor/auth-module
```

## Arbeiten mit Worktrees

Für parallele KI-Agenten-Arbeit nutzt du Git-Worktrees, um mehrere Branches gleichzeitig laufen zu lassen:

```bash
# Create a worktree for a feature branch
git worktree add ../project-feature-a feature/task-creation
git worktree add ../project-feature-b feature/user-settings

# Each worktree is a separate directory with its own branch
# Agents can work in parallel without interfering
ls ../
  project/              ← main branch
  project-feature-a/    ← task-creation branch
  project-feature-b/    ← user-settings branch

# When done, merge and clean up
git worktree remove ../project-feature-a
```

Vorteile:
- Mehrere Agenten können gleichzeitig an verschiedenen Features arbeiten
- Kein Branch-Wechsel nötig (jedes Verzeichnis hat seinen eigenen Branch)
- Scheitert ein Experiment, löschst du den Worktree – nichts geht verloren
- Änderungen bleiben isoliert, bis sie ausdrücklich gemergt werden

## Das Speicherpunkt-Muster

```
Agent starts work
    │
    ├── Makes a change
    │   ├── Test passes? → Commit → Continue
    │   └── Test fails? → Revert to last commit → Investigate
    │
    ├── Makes another change
    │   ├── Test passes? → Commit → Continue
    │   └── Test fails? → Revert to last commit → Investigate
    │
    └── Feature complete → All commits form a clean history
```

Dieses Muster sorgt dafür, dass du nie mehr als ein Inkrement an Arbeit verlierst. Gerät ein Agent aus der Spur, bringt dich `git reset --hard HEAD` zurück zum letzten erfolgreichen Stand.

## Zusammenfassungen von Änderungen

Liefere nach jeder Änderung eine strukturierte Zusammenfassung. Das erleichtert das Review, dokumentiert die Scope-Disziplin und macht unbeabsichtigte Änderungen sichtbar:

```
CHANGES MADE:
- src/routes/tasks.ts: Added validation middleware to POST endpoint
- src/lib/validation.ts: Added TaskCreateSchema using Zod

THINGS I DIDN'T TOUCH (intentionally):
- src/routes/auth.ts: Has similar validation gap but out of scope
- src/middleware/error.ts: Error format could be improved (separate task)

POTENTIAL CONCERNS:
- The Zod schema is strict — rejects extra fields. Confirm this is desired.
- Added zod as a dependency (72KB gzipped) — already in package.json
```

Dieses Muster deckt falsche Annahmen früh auf und gibt Reviewern eine klare Übersicht über die Änderung. Der Abschnitt „DIDN'T TOUCH“ ist besonders wichtig – er zeigt, dass du Scope-Disziplin gewahrt und keine ungefragte Renovierung gestartet hast.

## Hygiene vor dem Commit

Vor jedem Commit:

```bash
# 1. Check what you're about to commit
git diff --staged

# 2. Ensure no secrets (lists matching file names only — any output means review them)
git diff --staged -i -G'password|secret|api_key|token' --name-only

# 3. Run tests
npm test

# 4. Run linting
npm run lint

# 5. Run type checking
npx tsc --noEmit
```

Automatisiere das mit Git-Hooks:

```json
// package.json (using lint-staged + husky)
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

## Umgang mit generierten Dateien

- **Committe generierte Dateien** nur, wenn das Projekt sie erwartet (z. B. `package-lock.json`, Prisma-Migrationen)
- **Committe nicht**: Build-Ausgaben (`dist/`, `.next/`), Umgebungsdateien (`.env`) oder IDE-Konfiguration (`.vscode/settings.json`, sofern nicht geteilt)
- **Pflege eine `.gitignore`**, die mindestens abdeckt: `node_modules/`, `dist/`, `.env`, `.env.local`, `*.pem`

## Git zum Debuggen nutzen

```bash
# Find which commit introduced a bug
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>
# Git checkouts midpoints; run your test at each to narrow down

# View what changed recently
git log --oneline -20
git diff HEAD~5..HEAD -- src/

# Find who last changed a specific line
git blame src/services/task.ts

# Search commit messages for a keyword
git log --grep="validation" --oneline
```

## Release & Versionierung

Mit Commits verfolgst *du* Änderungen; eine **Version** ist, wie deine *Konsumenten* sie verfolgen. Sobald irgendetwas anderes von deinem Code abhängt – ein anderes Team, ein veröffentlichtes Paket, ein ausgerollter Client –, reicht „latest auf main“ nicht mehr als Antwort auf „Was läuft bei mir, und ist ein Upgrade sicher?“. Eine Versionsnummer und ein Changelog sind der Vertrag, der diese Frage beantwortet.

### Semantic Versioning

Für alles mit Konsumenten versionierst du als `MAJOR.MINOR.PATCH` und lässt die Nummer Bedeutung tragen:

```
  MAJOR  breaking change — consumers must change their code to upgrade
  MINOR  new functionality, backward-compatible — safe to upgrade
  PATCH  bug fix, backward-compatible — safe to upgrade
```

Die Nummer ist ein Versprechen, also sorge dafür, dass der Code dazu passt. Ein „Patch“, der Verhalten ändert, auf das sich Konsumenten verlassen haben, ist eine als Patch getarnte Major-Änderung (Hyrums Gesetz – siehe Skill `api-and-interface-design`). Wenn unklar ist, ob eine Änderung breaking ist, geh davon aus, dass sie es ist; ein überraschender Major ist weit billiger als ein kaputter Konsument.

### Den Release taggen – der Tag ist die Source of Truth

Ein Release ist ein unveränderlicher Punkt in der Historie, kein beweglicher Branch. Tagge ihn, damit er sich jederzeit reproduzieren lässt:

```bash
git tag -a v1.4.0 -m "Release 1.4.0"
git push origin v1.4.0
```

Leite die Version aus dem Tag ab, statt sie in verstreuten Dateien von Hand zu pflegen, damit Artefakt, Tag und Changelog nie voneinander abweichen können.

### Einen Changelog für Menschen führen

Ein Changelog ist nicht `git log`. Er ist die kuratierte, konsumentenorientierte Antwort auf „Was hat sich geändert, und betrifft es mich?“ – gruppiert nach `Added / Changed / Fixed / Deprecated / Removed / Security`, Neuestes oben, jeder Eintrag formuliert um die Auswirkung für Nutzer, nicht um interne Mechanik.

```markdown
## [1.4.0] - 2025-06-12
### Added
- Bulk task import via CSV
### Fixed
- Timezone drift in recurring task due dates
### Deprecated
- `GET /v1/tasks/all` — use the paginated `GET /v1/tasks` (removal in 2.0)
```

Schreibe den Eintrag in derselben Änderung, die den Effekt auslöst, solange die Auswirkung frisch ist – nicht erst zum Release-Zeitpunkt per Commit-Archäologie rekonstruiert. Breaking Changes bekommen einen Migrationshinweis und ein Abkündigungsfenster (folge dem Skill `deprecation-and-migration`); den eigentlichen Release auszuliefern ist Aufgabe des Skills `shipping-and-launch` – dieser Abschnitt ist der Versionierungsvertrag, der ihn speist.

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Ich committe, wenn das Feature fertig ist“ | Ein riesiger Commit lässt sich nicht reviewen, debuggen oder zurückrollen. Committe jede Scheibe. |
| „Die Message ist egal“ | Messages sind Dokumentation. Dein zukünftiges Ich (und zukünftige Agenten) müssen verstehen, was sich warum geändert hat. |
| „Ich squashe später alles“ | Squashen zerstört die Entwicklungsgeschichte. Bevorzuge von Anfang an saubere inkrementelle Commits. |
| „Branches bedeuten Mehraufwand“ | Kurzlebige Branches kosten nichts und verhindern, dass konkurrierende Arbeit kollidiert. Das Problem sind langlebige Branches – merge innerhalb von 1–3 Tagen. |
| „Ich teile diese Änderung später auf“ | Große Änderungen sind schwerer zu reviewen, riskanter zu deployen und schwerer zurückzurollen. Teile auf, bevor du einreichst, nicht danach. |
| „Ich brauche keine .gitignore“ | Bis eine `.env` mit Produktions-Secrets committet wird. Richte sie sofort ein. |
| „Ist nur ein kleiner Fix, ich erhöhe den Patch“ | Prüfe, was Konsumenten beobachten können. Eine Verhaltensänderung, auf die sie sich verlassen haben, ist ein Major – egal wie klein der Diff ist. |
| „Der Changelog ist einfach das Commit-Log“ | Commits sind für dich; der Changelog ist für Konsumenten und nach Auswirkung kuratiert. Wer ihn aus rohen Commits generiert, begräbt das Wesentliche. |
| „Den Changelog schreiben wir zum Release“ | Dann wird die Auswirkung aus dem Gedächtnis rekonstruiert, und die Hälfte fehlt. Schreibe den Eintrag mit der Änderung. |

## Warnsignale

- Große uncommittete Änderungen sammeln sich an
- Commit-Messages wie „fix“, „update“, „misc“
- Formatierungsänderungen vermischt mit Verhaltensänderungen
- Keine `.gitignore` im Projekt
- `node_modules/`, `.env` oder Build-Artefakte werden committet
- Langlebige Branches, die stark von main abweichen
- Force-Push auf geteilte Branches
- Ein Breaking Change wird unter einem Minor- oder Patch-Bump ausgeliefert
- Ein Release ohne Tag oder eine von Hand gepflegte Versionsnummer, die nicht zum Tag passt
- Ein nutzersichtbarer Release ohne Changelog-Eintrag oder ein Changelog, der nur hineinkopierte Commit-Messages enthält

## Verifikation

Für jeden Commit:

- [ ] Der Commit tut genau eine logische Sache
- [ ] Die Message erklärt das Warum und folgt den Typ-Konventionen
- [ ] Tests laufen vor dem Commit durch
- [ ] Keine Secrets im Diff
- [ ] Keine reinen Formatierungsänderungen vermischt mit Verhaltensänderungen
- [ ] `.gitignore` deckt die Standard-Ausschlüsse ab

Für jeden Release (alles mit Konsumenten):

- [ ] Der Versions-Bump passt zur Änderung: breaking → major, additiv → minor, Fix → patch
- [ ] Der Release ist getaggt, und die Version ist aus dem Tag abgeleitet, nicht von Hand und abweichend gepflegt
- [ ] Der Changelog enthält für diese Version einen kuratierten, menschenlesbaren Eintrag, nach Auswirkung gruppiert
