---
description: Führt die Pre-Launch-Checkliste per parallelem Fan-out an spezialisierte Personas aus und fasst die Ergebnisse zu einer Go/No-Go-Entscheidung zusammen
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:shipping-and-launch auf.

`/ship` ist ein **Fan-out-Orchestrator**. Er führt drei spezialisierte Personas parallel gegen die aktuelle Änderung aus und führt ihre Berichte dann zu einer einzigen Go/No-Go-Entscheidung samt Rollback-Plan zusammen. Die Personas arbeiten unabhängig voneinander – ohne gemeinsamen Zustand und ohne feste Reihenfolge –, und genau das macht die parallele Ausführung hier sicher und nützlich.

## Phase A — Paralleler Fan-out

Starte drei Subagents gleichzeitig mit dem Agent-Tool. **Setze alle drei Agent-Tool-Aufrufe in einem einzigen Assistant-Turn ab, damit sie parallel laufen** – sequenzielle Aufrufe verfehlen den Zweck dieses Commands.

In Claude Code übergibt jeder Aufruf `subagent_type` passend zum `name`-Feld der Persona:

1. **`code-reviewer`** — Führe ein Review entlang von fünf Achsen durch (Korrektheit, Lesbarkeit, Architektur, Sicherheit, Performance), bezogen auf die gestageten Änderungen oder die letzten Commits. Gib das Standard-Review-Template aus.
2. **`security-auditor`** — Führe eine Schwachstellen- und Threat-Model-Prüfung durch. Prüfe OWASP Top 10, Umgang mit Secrets, Auth/Authz und CVEs in Abhängigkeiten. Gib den Standard-Audit-Bericht aus.
3. **`test-engineer`** — Analysiere die Testabdeckung der Änderung. Identifiziere Lücken beim Happy Path, bei Edge Cases, Fehlerpfaden und Nebenläufigkeitsszenarien. Gib die Standard-Coverage-Analyse aus.

In anderen Harnesses ohne Agent-Tool rufst du den System-Prompt jeder Persona nacheinander auf und behandelst ihre Ausgaben so, als wären sie parallel zurückgekommen – die Merge-Phase funktioniert trotzdem.

Constraints (aus dem Subagent-Modell von Claude Code):
- Subagents können keine anderen Subagents starten – lass keine Persona an eine andere delegieren.
- Jeder Subagent bekommt ein eigenes Kontextfenster und liefert nur seinen Bericht an diese Hauptsession zurück.
- Wenn du Teammitglieder brauchst, die miteinander kommunizieren, statt nur zurückzumelden, nutze Claude Code Agent Teams und verweise auf diese Personas als Teammate-Typen (siehe `references/orchestration-patterns.md`).

**Persona-Auflösung.** Wenn du eigene Versionen von `code-reviewer`, `security-auditor` oder `test-engineer` in `.claude/agents/` oder `~/.claude/agents/` definiert hast, haben diese Vorrang vor den Versionen dieses Plugins – `/ship` übernimmt deine Anpassungen automatisch. Das ist beabsichtigt: Plugin-Subagents stehen in der Scope-Prioritätstabelle von Claude Code ganz unten, daher gewinnen Definitionen auf Nutzerebene by design.

## Phase B — Zusammenführung im Hauptkontext

Sobald alle drei Berichte vorliegen, fasst der Hauptagent (nicht eine Subpersona) sie zusammen:

1. **Code Quality** — Aggregiere die Critical/Required-Befunde von `code-reviewer` sowie fehlschlagende Tests, Lint- oder Build-Ausgaben. Löse Duplikate zwischen den Reviewern auf.
2. **Security** — Stufe alle Critical/High-Befunde von `security-auditor` zu Launch-Blockern hoch. Gleiche sie mit der Security-Achse von `code-reviewer` ab.
3. **Performance** — Übernimm die Performance-Achse von `code-reviewer`; prüfe gegebenenfalls zusätzlich die Core Web Vitals.
4. **Accessibility** — Verifiziere Tastaturnavigation, Screenreader-Unterstützung und Kontrast (von den drei Personas nicht abgedeckt – prüfe das direkt hier oder nutze die Accessibility-Checkliste).
5. **Infrastructure** — Umgebungsvariablen, Migrationen, Monitoring, Feature-Flags. Verifiziere direkt.
6. **Documentation** — README, ADRs, Changelog. Verifiziere direkt.

## Phase C — Entscheidung und Rollback

Erzeuge eine einzige Ausgabe:

```markdown
## Ship Decision: GO | NO-GO

### Blockers (must fix before ship)
- [Source persona: Critical finding + file:line]

### Recommended fixes (should fix before ship)
- [Source persona: Important finding + file:line]

### Acknowledged risks (shipping anyway)
- [Risk + mitigation]

### Rollback plan
- Trigger conditions: [what signals would prompt rollback]
- Rollback procedure: [exact steps]
- Recovery time objective: [target]

### Specialist reports (full)
- [code-reviewer report]
- [security-auditor report]
- [test-engineer report]
```

## Rules

1. Die drei Personas aus Phase A laufen parallel – niemals sequenziell.
2. Personas rufen sich nicht gegenseitig auf. Der Hauptagent führt die Ergebnisse in Phase B zusammen.
3. Der Rollback-Plan ist vor jeder GO-Entscheidung Pflicht.
4. Wenn eine Persona einen Critical-Befund meldet, lautet das Standardurteil NO-GO, es sei denn, der Nutzer akzeptiert das Risiko ausdrücklich.
5. **Überspringe den Fan-out nur, wenn alle folgenden Bedingungen erfüllt sind:** Die Änderung betrifft höchstens 2 Dateien, der Diff umfasst weniger als 50 Zeilen, und sie berührt weder Auth, Payments, Datenzugriff noch Config/Env. Andernfalls gilt standardmäßig der Fan-out. `/ship` ist für produktionsreife Änderungen gedacht – ist der Blast Radius nicht trivial, führe das parallele Review auch dann durch, wenn der Diff klein aussieht.
