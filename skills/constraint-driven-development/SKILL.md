---
name: constraint-driven-development
description: "Legt den Qualitätsmaßstab eines Projekts als schriftlichen Vertrag in CONSTRAINTS.md fest und verhindert, dass Agents ihn stillschweigend senken. Befragt den Nutzer zu den relevanten Dimensionen (z. B. Accessibility, Web-Performance, Coverage), schlägt Standard-Schwellen vor und prüft den Diff auf aufgeweichte Maßstäbe: neue @ts-ignore- oder eslint-disable-Unterdrückungen, übersprungene oder gelöschte Tests, entfernte Assertions, Stubs, gesenkte Schwellen. Verwenden, wenn kein Qualitätsmaßstab festgehalten ist, wenn ein Agent Checks abschaltet oder Tests überspringt, um grün zu werden, oder wenn eine Coverage- oder Performance-Schwelle gebraucht wird. Englische Trigger: \"set up constraints\", \"define our standards\". Typische Anfragen: „leg unsere Qualitätsstandards fest“, „richte Constraints für das Projekt ein“, „welche Coverage-Schwelle sollen wir nehmen“, „der Agent hat die Tests einfach übersprungen“."
---

# Constraint-getriebene Entwicklung

## Überblick

Andere Skills in diesem Pack beschreiben, wie Gutes aussieht. `code-review-and-quality` liefert dir fünf Achsen. `test-driven-development` liefert dir einen Zyklus. `security-and-hardening` liefert dir eine Bedrohungsliste. All das steht in Prosa, die der Agent liest und der er folgen kann oder auch nicht, und nichts davon überlebt das Ende der Session.

Dieser Skill erzeugt etwas anderes: eine schriftliche Festlegung des Maßstabs **dieses Projekts**, mit Zahlen, die die Konversation überdauert und sich maschinell prüfen lässt.

Der Grund ist wichtig. Als du den Code selbst geschrieben hast, hat dir das Lesen gezeigt, ob er etwas taugt. Ein Agent schreibt an einem Nachmittag mehr, als du in der ganzen Woche lesen wirst. Also wandert das Urteil aus deinem Kopf in Checks, die rund um die Schleife laufen. Diese Checks müssen existieren, sie brauchen Zahlen, die du tatsächlich gewählt hast, und sie müssen nah genug an der Arbeit auslösen, dass der Agent seine eigene Ausgabe korrigiert.

Spec-driven Development sagt, was gebaut wird. Test-driven Development belegt, dass es funktioniert. Constraint-driven Development definiert, was „gut genug zum Ausliefern“ bedeutet, bevor jemand im PR darüber streitet.

## Wann verwenden

Wende diesen Skill an, wenn:

- ein Projekt oder ein größeres Feature startet und kein Qualitätsmaßstab schriftlich vorliegt
- der Nutzer bittet, „Constraints einzurichten“, „Quality Gates hinzuzufügen“, „unsere Standards zu definieren“ oder „den Agent daran zu hindern, Murks auszuliefern“
- ein Agent Mengen an Code erzeugt, die niemand Zeile für Zeile liest
- CI Checks hat, aber niemand sagen kann, welche einen merge blockieren und welche nur Dekoration sind
- Coverage-, Performance- oder Accessibility-Zahlen pro PR ausdiskutiert statt einmal entschieden werden
- du kurz davor bist, `/build auto` oder eine andere autonome Schleife zu starten, und das Einzige zwischen ihr und main eine Test-Suite ist, die der Agent ebenfalls geschrieben hat

**Wann NICHT verwenden:**

- Das Projekt hat bereits eine `CONSTRAINTS.md` und der Nutzer ändert sie nicht – lies sie und befolge sie stattdessen
- Einmalige Skripte, Spikes, Wegwerf-Prototypen
- Der Nutzer will jetzt ein Code-Review (`code-review-and-quality`) oder eine gebaute CI-Pipeline (`ci-cd-and-automation`)
- Code vor dem Product-Market-Fit mit zwei Wochen erwarteter Lebensdauer – der Floor unten lohnt sich trotzdem, der Rest nicht

## Constraints laden

Das Interview braucht einen Nutzer, der live dabei ist. **Führe es nicht in nicht-interaktiven Kontexten aus** (CI, `/loop`, autonome Läufe). Fehlen dort Constraints, wende den Floor unten an, vermerke, dass du das getan hast, und markiere den Rest für einen Menschen.

## Der Ablauf

### Schritt 1: Erst erkunden, dann fragen

Frage nie nach etwas, das du lesen kannst. Sammle vor der ersten Frage:

| Was | Wo nachsehen |
|------|---------------|
| Sprache und Stack | `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` |
| Test-Runner | Dev-Dependencies, `test`-Skript, vorhandene Testdateien |
| Vorhandene Linter | `eslint.config.*`, `biome.json`, `.ruff.toml` |
| Coverage heute | Ausgabe in `coverage/` oder die Suite einmal laufen lassen |
| CI | `.github/workflows/`, `.gitlab-ci.yml` |
| Agent-Harness | `.claude/`, `.codex/`, `AGENTS.md` |

Berichte in zwei Zeilen, was du gefunden hast, und frage dann nur nach dem, was übrig bleibt.

### Schritt 2: Vier Fragen, jede mit Default

Folge der Ein-Frage-pro-Runde-Disziplin aus `interview-me`, mit einer Änderung: Jede Frage hier hat einen Default, sodass „Weiß ich nicht“ eine vollständige Antwort ist, die trotzdem eine funktionierende Konfiguration ergibt.

```
Q1: Beyond the floor, which of these do you want enforced?
    (a) Test coverage on new code
    (b) Security scanning
    (c) Performance budgets
    (d) Accessibility
    (e) Architecture boundaries
GUESS: (a) and (b) — you have a test runner already and you're handling user input.
DEFAULT if unsure: (a) and (b).
Say what each pick costs: (c) and (d) need a running URL, (e) needs a rules file written.
```

```
Q2: When a check fails while the agent is mid-task, should it block or warn?
GUESS: Block. You're running agents unattended and a warning nobody reads is a warning.
DEFAULT if unsure: Block on the floor, warn on everything else for the first two weeks.
```

```
Q3: Do you have target numbers in mind, or should I measure where you are today and hold that line?
GUESS: Measure. Most teams don't have a number, and an invented one gets ignored.
DEFAULT if unsure: Measure and hold. See "Ratchets" below.
```

```
Q4: What's the slowest check you'll tolerate before the agent hands work back?
GUESS: About 90 seconds. Longer and you'll stop running it.
DEFAULT if unsure: 90 seconds at task end, unlimited in CI.
```

Höre bei vier auf. Ein Intake mit zwölf Fragen erzeugt eine Konfiguration, die niemand versteht, und einen Nutzer, der den Start bereut.

### Schritt 3: CONSTRAINTS.md schreiben

Eine Datei im Repo-Root. Jeder Agent in jedem Harness kann sie lesen, und eine Änderung daran erscheint im Review, wo sie hingehört.

```markdown
# Constraints

Last reviewed: 2026-08-08 by @addy

## Floor (always enforced, no setup required)

- No new suppression comments: `@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`
- No unimplemented stubs: `throw new Error("Not implemented")`, empty `catch {}`
- No skipped or deleted tests without a reason in the commit message
- No secrets in source
- This file does not get weakened to make a change pass

## Enforced with numbers

| Dimension | Rule | Checked by | Runs at |
|-----------|------|-----------|---------|
| Types | Zero type errors | `tsc --noEmit` | every edit |
| Lint | Zero errors from our config | `biome check` | every edit |
| Secrets | No secrets in source | `gitleaks dir . --redact` | every edit |
| Coverage | Changed lines ≥ 80% covered | `vitest run --coverage` + git diff | task end, CI |
| Security: code | Nothing at high or above | `npm run check:security` | CI |
| Security: deps | Nothing at high or above | `osv-scanner scan source -r .` | CI |
| Accessibility | Zero critical or serious | `npm run check:a11y` | preview deploy |
| Performance | LCP ≤ 2500ms, CLS ≤ 0.1 | `lighthouse $PREVIEW_URL --output=json` | preview deploy |

Every row names the command that produces the verdict. A dimension with a
number and no command in this column is an aspiration, not a constraint.

## Measured, not yet enforced

| Metric | Today | Direction |
|--------|-------|-----------|
| Project coverage | 62.4% | must not fall |
| Bundle size (main) | 184 kB | must not grow |

## Exceptions

| ID | Rule | Path | Reason | Owner | Expires |
|----|------|------|--------|-------|---------|
| W1 | `no-explicit-any` | `src/legacy/**` | Rewrite tracked in ENG-441 | @addy | 2026-11-01 |
```

Füge dann je eine Zeile zu `AGENTS.md` und `CLAUDE.md` hinzu: `Read CONSTRAINTS.md before writing code. Do not weaken it to make a change pass.`

### Schritt 4: Installieren, was jede Dimension braucht

Eine Dimension zu wählen heißt, etwas zu installieren. Lass den Nutzer nicht mit einer Zahl und ohne Mechanismus zurück, und erfinde keinen eigenen Checker, wenn es einen De-facto-Standard gibt – diese Tools sind aufgeführt, weil ihre Regelformate und Schwellenwerte das sind, woran sich alles andere im Ökosystem ausrichtet, sodass die vorhandene Konfiguration des Teams weiter funktioniert.

| Dimension | Tool | Installation | Ausführen | Gate bei |
|-----------|------|---------|-----|---------|
| Types (TS) | tsc | bereits vorhanden | `tsc --noEmit` | jedem Fehler |
| Types (Python) | mypy | `pip install mypy` | `mypy .` | jedem Fehler |
| Lint | deine bestehende Konfiguration | bereits vorhanden | `eslint .` / `biome check` / `ruff check` | jedem Fehler |
| Coverage (JS) | dein Test-Runner | Vitest: `npm i -D @vitest/coverage-v8`; Jest: bereits vorhanden | `vitest run --coverage` (oder `jest --coverage`) | Coverage der geänderten Zeilen |
| Coverage (Python) | pytest-cov | `pip install pytest-cov` | `pytest --cov --cov-report=lcov` | wie oben |
| Security: Code | Semgrep | `pipx install semgrep` | `npm run check:security` (unten) | high oder critical, einschließlich Legacy-`ERROR` |
| Security: Secrets | gitleaks | `sudo port install gitleaks` | `gitleaks dir . --redact --no-banner` | jedem Fund |
| Security: Dependencies | osv-scanner | `sudo port install osv-scanner` | `osv-scanner scan source -r .` | high oder höher |
| Performance: Seite | Lighthouse | `npm i -D lighthouse` | `lighthouse $URL --output=json --quiet` | LCP, CLS, Performance-Score |
| Performance: Bundle | size-limit | `npm i -D size-limit` | `size-limit --json` | Byte-Budget pro Eintrag |
| Accessibility | axe-core | `npm i -D @axe-core/cli` | `npm run check:a11y` (unten) | null critical oder serious |
| Architektur | dependency-cruiser | `npm i -D dependency-cruiser` | `depcruise --validate src` | jeder Verletzung |
| Assertion-Qualität | Stryker | `npm i -D @stryker-mutator/core` | `stryker run --mutate <changed files>` | Mutation-Score |

Fünf Dinge, die dich erwischen, wenn du sie überspringst:

1. **`--redact` bei gitleaks ist nicht optional.** Ohne es landet das gefundene Secret im Transkript des Agents, und so landet ein geleakter Schlüssel in einem Log, einer Zusammenfassung oder einer commit-Nachricht. Melde die Regel und die Fundstelle, nie den Wert.
2. **Lighthouse und axe brauchen eine URL.** Sie funktionieren nur gegen eine laufende App und gehören deshalb in die Runtime-Stufe, gegen ein Preview-Deployment oder einen lokalen Server, den du vorher startest. Hat das Projekt keine URL, die sich ansprechen lässt – eine CLI, eine Bibliothek, eine Desktop-App –, sag das und streiche die Dimension, statt einen Check zu erfinden, der nicht laufen kann.
3. **Beschränke die teuren Checks auf den Diff.** `stryker run --mutate` auf dem ganzen Repo dauert Stunden und wird abgeschaltet; auf den Dateien, die eine Änderung berührt hat, dauert es unter einer Minute. Dasselbe gilt für Semgrep, das eine Pfadliste akzeptiert.
4. **Coverage braucht keinen zweiten Testlauf.** Lies das lcov, das deine Suite ohnehin schreibt, und schneide es mit `git diff`. Die Suite zweimal laufen zu lassen, um eine Zahl zu bekommen, ist der schnellste Weg, dass alle das hier hassen.
5. **Die Registry-Regeln von Semgrep sind kostenlos nutzbar; prüfe die Lizenz, bevor du sie weiterverteilst.** `opengrep` ist ein Drop-in-Fork mit demselben Regelformat und derselben JSON-Ausgabe, falls das für eure Rechtsabteilung relevant ist.

`semgrep scan` und `axe` können bei Funden mit 0 enden; kopiere [scripts/quality-gate.mjs](scripts/quality-gate.mjs) in das Verzeichnis `scripts/` des Projekts, um diese Schwellenwerte durchzusetzen.
Setze den Scanner vor `&&`, damit ein fehlgeschlagener Scan den Befehl stoppt.

Füge jeden davon dem projekteigenen Skript hinzu, damit er ohne Agent reproduzierbar ist:

```json
{
  "scripts": {
    "check:fast": "tsc --noEmit && eslint . && gitleaks dir . --redact --no-banner",
    "check:task": "npm run check:fast && vitest run --coverage",
    "check:security": "semgrep scan --config p/default --strict --json > semgrep-results.json && node scripts/quality-gate.mjs semgrep semgrep-results.json",
    "check:a11y": "axe \"$PREVIEW_URL\" --tags wcag2a,wcag2aa,wcag21aa --stdout > axe-results.json && node scripts/quality-gate.mjs axe axe-results.json",
    "check:full": "npm run check:task && npm run check:security && osv-scanner scan source -r ."
  }
}
```

Diese Zuordnung ist wichtiger als die Tools. `check:fast` läuft nach einer Änderung, `check:task`, wenn der Agent glaubt, fertig zu sein, `check:full` in CI. Führe `check:a11y` aus, sobald die Preview erreichbar ist und `PREVIEW_URL` gesetzt ist (das Beispiel nutzt POSIX-Shell-Syntax).

Bevor du eine Zeile als durchgesetzt bezeichnest, führe ihren tatsächlichen CI-Befehl gegen eine bekannte Verletzung und eine saubere Kontrolle aus. Bestätige, dass die Verletzung fehlschlägt, die Kontrolle durchläuft und auch Scanner-Fehler fehlschlagen. Bestätige bei einem Schweregrad-Schwellenwert außerdem, dass ein Befund unterhalb des Schwellenwerts durchläuft. Wende das auf jede Dimension an, auch auf Coverage und Lighthouse: Ein erzeugter Report allein setzt die Zahl in `CONSTRAINTS.md` nicht durch.

Die Befehle stehen jetzt an zwei Stellen – in der Spalte `Checked by` der `CONSTRAINTS.md` und in diesen Skripten. `CONSTRAINTS.md` ist die maßgebliche Quelle: Sie trägt die Begründung neben jedem Befehl und erscheint im Review. Die Skripte sind Komfort-Wrapper, die sie spiegeln müssen, keine zweite Quelle der Wahrheit; driften sie auseinander, gewinnt die Datei.

### Schritt 5: An den Lebenszyklus anbinden

Der größte Einzelfehler ist, alles überall laufen zu lassen. Ein Check, der den Agent ausbremst, wird abgeschaltet, und ein abgeschaltetes Gate ist schlimmer als gar keins, weil der Maßstab weiterhin zu existieren scheint.

| Phase | Befehl | Was läuft | Budget |
|-------|---------|-----------|--------|
| BUILD | `/build` | Types, Lint, Secrets, der Floor | unter 5 s, nur geänderte Datei |
| VERIFY | `/test` | Zugehörige Tests, Coverage der geänderten Zeilen | unter 90 s |
| REVIEW | `/review` | Alles, plus die Guards unten | Minuten |
| SHIP | `/ship` | Richtungs-Checks, keine Regressionen | CI |

Zwei Regeln, die das erträglich halten:

1. **Beschränke auf den Diff.** Prüfe die Zeilen, die diese Änderung berührt hat, nicht das ganze Repo. Die Coverage der geänderten Zeilen ist eine Zahl, die der Agent bewegen kann; die Projekt-Coverage hat er geerbt.
2. **Die Kosten bestimmen die Platzierung.** Alles, was länger als ein paar Sekunden dauert, gehört aus der Edit-Schleife heraus. Mutation Testing auf dem ganzen Repo dauert Stunden; auf den Dateien, die eine Änderung berührt hat, unter einer Minute – das ist der Unterschied zwischen einem Check, den Leute ausführen, und einem, den sie nicht ausführen.

### Schritt 6: Den Maßstab selbst bewachen

Jemand wird einwenden: Wenn der Agent den Code und die Checks schreibt, beweisen die Checks nichts. Halb richtig, und es lohnt sich, darum herumzubauen.

Agents basteln keine raffinierten Schlupflöcher. Sie treffen auf einen roten Check und nehmen den billigsten Weg zu Grün. Achte beim Review im Diff auf diese fünf Züge:

1. **Der Schwellenwert wurde verschoben.** Ein Budget gesenkt, ein Schweregrad herabgestuft, ein Check aus der schnellen Stufe entfernt. Vergleiche `CONSTRAINTS.md` mit dem Stand am Abzweigpunkt des Branches.
2. **Ein Test wurde leichter gemacht.** `.skip` hinzugefügt, eine Testdatei gelöscht, Assertions aus Tests entfernt, die geblieben sind.
3. **Ein Checker wurde stummgeschaltet.** Neues `@ts-ignore` oder `eslint-disable`. Vier Unterdrückungen verdienen besondere Aufmerksamkeit, weil sie einen Check abschalten, auf den du dich verlässt: `istanbul ignore` nimmt Code aus der Coverage, statt ihn zu testen, `Stryker disable` versteckt einen überlebenden Mutanten, `nosemgrep` und `gitleaks:allow` tun dasselbe für Security-Befunde.
4. **Arbeit ist unfertig.** Ein Stub, der wirft, ein leeres `catch`, das einen Fehler zum Schweigen bringt, ein `TODO` an der Stelle, wo die Implementierung stehen sollte.
5. **Eine Ausnahme ist aufgetaucht.** Eine neue Zeile in der Exceptions-Tabelle, über die niemand gesprochen hat.

Nichts davon braucht mehr Tooling als `git diff`. Den Maßstab zu verschärfen sollte lautlos geschehen; ihn zu lockern sollte laut sein.

Anders als die nummerierten Dimensionen hat der Floor kein eigenes De-facto-Tool. Ein Agent, der ihn durchsetzen soll, schreibt daher dazu tendenziell einen Checker von Grund auf, und zwei Agents schreiben zwei verschiedene. Eine Referenzimplementierung dieser fünf Checks liegt diesem Skill in [references/floor-guard.md](references/floor-guard.md) bei (diff-beschränkt, Exit `0`/`1`/`2`, Muster pro Ökosystem anpassbar). Passe sie an, statt sie neu zu erfinden, aus demselben Grund, aus dem jede Dimension ein De-facto-Tool nennt: damit der Mechanismus über Läufe und Stacks hinweg derselbe ist.

**Nicht alle Checks sind gleich zirkulär.** Ordne sie nach einer Frage: Kann der Agent dies zum Bestehen bringen, indem er Code schreibt, der nicht funktioniert?

- **Extern** – axe-core kodiert WCAG, `osv-scanner` liest eine Schwachstellendatenbank, Lighthouse misst einen echten Browser. Mit diesen kann der Agent nicht verhandeln.
- **Projekt** – deine Lint-Regeln, deine Schichtgrenzen. Ein Mensch besitzt die Datei.
- **Suite** – deine eigenen Tests. Am nützlichsten und die einzige wirklich zirkuläre Art.

Ein Maßstab, der ganz aus der dritten Art besteht, ist weniger wert als einer mit einer Meinung von außen. Prüfe, dass mindestens ein externer Constraint vorhanden ist.

### Schritt 7: Ratchets, wenn du keine Zahl hast

Setze 80 % Coverage auf eine Codebasis mit 62 %, und du bekommst einen dauerhaft roten Build und dann ein Team, das lernt, rote Builds zu ignorieren.

Die Alternative verlangt keine Entscheidung: Halte fest, wo du stehst, und weigere dich dann, schlechter zu werden. Trage es in die Tabelle „Measured, not yet enforced“ ein, mit der heutigen Zahl und einer Richtung. Jeder Check vergleicht gegen den festgehaltenen Wert, nicht gegen ein Wunschziel. Verbessert sich eine Zahl, aktualisiere sie; sinkt sie, ist das der Befund.

Das beantwortet auch einen berechtigten Einwand zum Training. Modelle werden dafür belohnt, Tests zu bestehen, was sich in Sekunden auswerten lässt. Architekturverfall zeigt sich über Monate und erreicht die Gewichte nie. Ein Ratchet ist die fehlende Strafe, aufgeschrieben dort, wo der Build sie sehen kann.

## Sinnvolle Defaults

Wenn der Nutzer keine Meinung hat, nimm diese. Sie sind so gewählt, dass die meisten Codebasen sie am ersten Tag erfüllen.

| Constraint | Default | Warum diese Zahl |
|------------|---------|-----------------|
| Coverage der geänderten Zeilen | ≥ 80 % | Hoch genug, um einen Test zu erzwingen, niedrig genug für eine Konfigurationszeile |
| Projekt-Coverage | heutiger Wert, darf nicht fallen | Braucht keine Diskussion zur Einführung |
| Mutation-Score (falls genutzt) | ≥ 60 % zum Start | Typisch für eine Suite, die nie mutiert wurde; 80 % ist ausgereift |
| Dependency-Schwachstellen | nichts bei high oder höher | Darunter ist es meist Rauschen |
| LCP | ≤ 2500 ms | Core-Web-Vitals-Schwelle für „gut“ |
| CLS | ≤ 0.1 | Dito |
| Accessibility | null critical oder serious axe-Verstöße | Moderate und minor sind oft strittig |
| Lebensdauer einer Ausnahme | 90 Tage | Lang genug, um den Fix zu planen, kurz genug, um sich zu erinnern |
| Ratchet-Toleranz | 0,5 % | Fängt Drift ab, wenn eine unbeteiligte Datei die Zahl bewegt |

Nenne Zahl und Begründung zusammen. Ein Schwellenwert ohne Begründung wird von der nächsten Person gelöscht, die an ihn stößt.

## Eskalationspfad

Constraints wirken auf drei Stufen von Biss. Beginne bei der ersten.

1. **Nur schriftlich.** `CONSTRAINTS.md` existiert und Agents lesen sie. Kostet nichts, fängt die ehrlichen Fehler, verlässt sich darauf, dass der Agent sich daran hält.
2. **Skriptgesteuert.** Ein `npm run check` (oder `make check`), das die schnellen Checks ausführt, eingebunden in den Post-Edit-Hook deines Agents und in deine CI. Deterministisch, keine neue Dependency.
3. **Tool-gestützt.** Ein eigener Runner, der Diff-Beschränkung, Budgets, Ratchets und die Guard-Checks übernimmt. Verwende ihn, wenn die Konfiguration einem Shell-Skript entwächst. Der Floor-Guard in [references/floor-guard.md](references/floor-guard.md) ist der Ausgangspunkt für die Guard-Check-Hälfte davon.

Die meisten Projekte sollten bei 2 stehen bleiben. Wechsle zu 3, wenn du mehr als etwa dreißig Zeilen Shell zum Ausführen von Checks pflegst.

**Ein erster Lauf kann nur den Floor umfassen.** Der Floor-Guard arbeitet nur auf dem Diff und braucht keine Installationen, also kannst du den Floor am ersten Tag durchsetzen und die nummerierten Dimensionen hinzufügen, sobald du das jeweilige Tool installierst, statt vor dem ersten geschützten commit jeden Checker aufzubauen. Security-Tools, die systemweit installiert werden (gitleaks, osv-scanner), können auch nur in CI laufen, wenn du die Laptops sauber halten willst; lege in der Spalte `Runs at` fest, wo jede Dimension läuft.

## Häufige Ausreden

| Ausrede | Realität |
|--------|---------|
| „Wir fügen Constraints hinzu, sobald sich der Code gesetzt hat“ | Code setzt sich um das herum, was erlaubt war, solange er in Bewegung war |
| „Die Tests sind die Constraints“ | Tests, die du selbst geschrieben hast, belegen nur, dass du dir selbst zustimmst; sie sagen nichts über Coverage neuen Codes, Dependency-Risiko oder Bundle-Wachstum |
| „Wir schaffen keine 80 % Coverage“ | Dann setze nicht 80 % an. Nimm die heutige Zahl und halte sie |
| „Das bremst den Agent aus“ | Nur wenn du langsame Checks in die schnelle Schleife legst. Das ist ein Platzierungsfehler, kein Argument gegen Constraints |
| „Ich merke mir schon, was unsere Standards sind“ | Der Agent tut das nicht, und er schreibt den Großteil des Codes |
| „Constraints blockieren uns beim Ausliefern“ | Eine Ausnahme mit Owner und Datum entblockt dich. Den Constraint zu löschen entblockt alle für immer |

## Warnsignale

Halte an und überdenke die Lage, wenn dir Folgendes auffällt:

- Das Interview ging über vier Fragen hinaus oder erzeugte eine Konfiguration, die der Nutzer nicht erklären kann
- Ein Budget wurde gesetzt, das die Codebasis heute reißt, ohne Plan, es zu erreichen
- Eine Dimension steht mit einer Zahl in CONSTRAINTS.md, aber ohne Tool dahinter
- Ein Checker wurde selbst gebaut, obwohl es einen De-facto-Standard gibt, sodass die vorhandene Konfiguration des Teams ignoriert wird
- Jeder Constraint wird von der projekteigenen Test-Suite geprüft, ohne Meinung von außen
- `CONSTRAINTS.md` wurde im selben commit geändert wie das Feature, das durchgefallen ist
- Eine Ausnahme hat keinen Owner oder ein Ablaufdatum mehr als ein Jahr in der Zukunft
- Der Agent schlug vor, einen Schwellenwert zu lockern, statt den Code zu reparieren
- Langsame Checks landeten in der Edit-Schleife und jemand hat angefangen, `--no-verify` zu übergeben
- Niemand hat `CONSTRAINTS.md` geöffnet, seit sie geschrieben wurde

## Verifikation

Der Skill wurde korrekt angewendet, wenn:

- [ ] `CONSTRAINTS.md` existiert und jede Zahl darin eine genannte Begründung hat
- [ ] Der Floor wird durchgesetzt und besteht auf der aktuellen Codebasis ohne Änderungen
- [ ] Jede vom Nutzer gewählte Dimension hat ein installiertes Tool und einen Befehl, der heute läuft
- [ ] Jeder Constraint nennt, wo er läuft, und die schnelle Stufe bleibt unter wenigen Sekunden
- [ ] Mindestens ein Constraint ist extern (nicht von den eigenen Tests des Projekts beurteilt)
- [ ] Nur gemessene Metriken halten den heutigen Wert und eine Richtung fest
- [ ] Ausnahmen haben einen Owner und ein Ablaufdatum
- [ ] `AGENTS.md` oder `CLAUDE.md` verweist auf die Datei
- [ ] Ein Probelauf auf dem aktuellen Branch erzeugt keine Fehlschläge, denen der Nutzer widerspricht
- [ ] Jeder durchgesetzte Befehl schlägt bei einer absichtlichen Verletzung und einem Scanner-Fehler fehl, besteht eine saubere Kontrolle und behält den vereinbarten Schweregrad-Schwellenwert bei

## Siehe auch

- `interview-me` – die Ein-Frage-pro-Runde-Disziplin, die der Intake dieses Skills übernimmt
- `code-review-and-quality` – wie man reviewt; dieser Skill legt fest, was das Review durchsetzt
- `ci-cd-and-automation` – die Pipeline bauen, in der diese Constraints laufen
- `test-driven-development` – die Suite, die Coverage- und Mutation-Constraints messen
- `security-and-hardening` – was die Security-Dimension enthalten sollte
- `performance-optimization` – woher die Performance-Zahlen kommen
