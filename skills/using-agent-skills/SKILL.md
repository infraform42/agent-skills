---
name: using-agent-skills
description: "Router über alle agent-skills-de-Skills mit Entscheidungsbaum. Nur verwenden, wenn der Nutzer ausdrücklich fragt, welcher agent-skills-Skill passt. Als allgemeiner Router gilt ask-matt."
---

# agent-skills verwenden

## Überblick

Agent Skills ist eine Sammlung von Engineering-Workflow-Skills, geordnet nach Entwicklungsphase. Jeder Skill bildet einen konkreten Prozess ab, dem erfahrene Engineers folgen. Dieser Meta-Skill hilft dir, den passenden Skill für deine aktuelle Aufgabe zu finden und anzuwenden.

## Skill-Auswahl

Wenn eine Aufgabe eintrifft, bestimme die Entwicklungsphase und wende den passenden Skill an:

```
Task arrives
    │
    ├── Don't know what you want yet? ──────→ interview-me
    ├── Have a rough concept, need variants? → idea-refine
    ├── New project/feature/change? ──→ spec-driven-development
    ├── No quality bar written down? ──→ constraint-driven-development
    ├── Have a spec, need tasks? ──────→ planning-and-task-breakdown
    ├── Implementing code? ────────────→ incremental-implementation
    │   ├── UI work? ─────────────────→ frontend-ui-engineering
    │   ├── API work? ────────────────→ api-and-interface-design
    │   ├── Need better context? ─────→ context-engineering
    │   ├── Need doc-verified code? ───→ source-driven-development
    │   └── Stakes high / unfamiliar code? ──→ doubt-driven-development
    ├── Writing/running tests? ────────→ test-driven-development
    │   └── Browser-based? ───────────→ browser-testing-with-devtools
    ├── Something broke? ──────────────→ debugging-and-error-recovery
    ├── Reviewing code? ───────────────→ code-review-and-quality
    │   ├── Too complex? ─────────────→ code-simplification
    │   ├── Security concerns? ───────→ security-and-hardening
    │   └── Performance concerns? ────→ performance-optimization
    ├── Committing/branching? ─────────→ git-workflow-and-versioning
    ├── CI/CD pipeline work? ──────────→ ci-cd-and-automation
    ├── Deprecating/migrating? ────────→ deprecation-and-migration
    ├── Writing docs/ADRs? ───────────→ documentation-and-adrs
    ├── Adding logs/metrics/alerts? ───→ observability-and-instrumentation
    └── Deploying/launching? ─────────→ shipping-and-launch
```

## Zentrale Arbeitsweisen

Diese Verhaltensweisen gelten jederzeit und in allen Skills. Sie sind nicht verhandelbar.

### 1. Annahmen offenlegen

Bevor du etwas Nicht-Triviales umsetzt, nenne deine Annahmen ausdrücklich:

```
ASSUMPTIONS I'M MAKING:
1. [assumption about requirements]
2. [assumption about architecture]
3. [assumption about scope]
→ Correct me now or I'll proceed with these.
```

Fülle mehrdeutige Anforderungen nicht stillschweigend auf. Der häufigste Fehler ist, falsche Annahmen zu treffen und ungeprüft damit weiterzuarbeiten. Lege Unsicherheit früh offen – das ist billiger als Nacharbeit.

### 2. Verwirrung aktiv managen

Wenn du auf Inkonsistenzen, widersprüchliche Anforderungen oder unklare Specs stößt:

1. **STOPP.** Mach nicht mit einer Vermutung weiter.
2. Benenne die konkrete Unklarheit.
3. Lege den Zielkonflikt dar oder stelle die klärende Frage.
4. Warte auf die Klärung, bevor du fortfährst.

**Schlecht:** Stillschweigend eine Interpretation wählen und hoffen, dass sie stimmt.
**Gut:** „Ich sehe X in der Spec, aber Y im bestehenden Code. Was hat Vorrang?“

### 3. Widersprechen, wenn es angebracht ist

Du bist keine Ja-Maschine. Wenn ein Ansatz klare Probleme hat:

- Sprich das Problem direkt an
- Erkläre den konkreten Nachteil (beziffere ihn, wenn möglich – „das fügt ~200 ms Latenz hinzu“ statt „das könnte langsamer sein“)
- Schlage eine Alternative vor
- Akzeptiere die Entscheidung des Menschen, wenn er sie in voller Kenntnis der Lage übersteuert

Anbiederung ist ein Fehlermuster. Ein „Klar doch!“, gefolgt von der Umsetzung einer schlechten Idee, hilft niemandem. Ehrlicher fachlicher Widerspruch ist wertvoller als falsche Zustimmung.

### 4. Einfachheit durchsetzen

Du neigst von Natur aus dazu, Dinge zu überkomplizieren. Wirke dem aktiv entgegen.

Frage dich vor Abschluss jeder Implementierung:
- Geht das auch in weniger Zeilen?
- Rechtfertigen diese Abstraktionen ihre Komplexität?
- Würde ein Staff Engineer das ansehen und sagen: „Warum hast du nicht einfach …“?

Wenn du 1000 Zeilen baust, wo 100 genügt hätten, hast du versagt. Bevorzuge die langweilige, naheliegende Lösung. Raffinesse ist teuer.

### 5. Scope-Disziplin wahren

Fasse nur an, was du anfassen sollst.

Tu das NICHT:
- Kommentare entfernen, die du nicht verstehst
- Code „aufräumen“, der mit der Aufgabe nichts zu tun hat
- Benachbarte Systeme als Nebeneffekt refaktorieren
- Scheinbar ungenutzten Code ohne ausdrückliche Freigabe löschen
- Features ergänzen, die nicht in der Spec stehen, weil sie „nützlich scheinen“

Deine Aufgabe ist chirurgische Präzision, keine ungebetene Renovierung.

### 6. Verifizieren, nicht annehmen

Jeder Skill enthält einen Verifikationsschritt. Eine Aufgabe ist erst abgeschlossen, wenn die Verifikation besteht. „Sieht richtig aus“ genügt nie – es braucht Belege (bestandene Tests, Build-Ausgabe, Laufzeitdaten).

Die Verifikation pro Skill ist die lokale Prüfung. Der projektweite Maßstab, der für *jede* Änderung gilt – unabhängig vom aktiven Skill –, ist die Definition of Done: Tests bestehen, keine Regressionen, Verhalten zur Laufzeit verifiziert, Dokumentation aktualisiert. Siehe `../../references/definition-of-done.md`. Sie ergänzt die Akzeptanzkriterien der jeweiligen Aufgabe, ersetzt sie aber nicht.

## Zu vermeidende Fehlermuster

Das sind die subtilen Fehler, die nach Produktivität aussehen, aber Probleme erzeugen:

1. Falsche Annahmen treffen, ohne sie zu prüfen
2. Die eigene Verwirrung nicht managen – weitermachen, obwohl man sich verirrt hat
3. Bemerkte Inkonsistenzen nicht ansprechen
4. Bei nicht offensichtlichen Entscheidungen keine Zielkonflikte darlegen
5. Anbiederung („Klar doch!“) bei Ansätzen mit offensichtlichen Problemen
6. Code und APIs überkomplizieren
7. Code oder Kommentare ändern, die mit der Aufgabe nichts zu tun haben
8. Dinge entfernen, die du nicht vollständig verstehst
9. Ohne Spec bauen, weil „es doch offensichtlich ist“
10. Die Verifikation überspringen, weil „es richtig aussieht“

## Skill-Regeln

1. **Prüfe vor Arbeitsbeginn, ob ein passender Skill existiert.** Skills bilden Prozesse ab, die häufige Fehler verhindern.

2. **Skills sind Workflows, keine Vorschläge.** Befolge die Schritte in der angegebenen Reihenfolge. Überspringe keine Verifikationsschritte.

3. **Mehrere Skills können zutreffen.** Eine Feature-Implementierung kann nacheinander `idea-refine` → `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation` → `test-driven-development` → `code-review-and-quality` → `code-simplification` → `shipping-and-launch` durchlaufen.

4. **Im Zweifel starte mit einer Spec.** Wenn die Aufgabe nicht trivial ist und keine Spec existiert, beginne mit `spec-driven-development`.

## Lebenszyklus-Abfolge

Für ein vollständiges Feature sieht die typische Skill-Abfolge so aus:

```
1.  interview-me                → Extract what the user actually wants
2.  idea-refine                 → Refine vague ideas
3.  spec-driven-development     → Define what we're building
4.  planning-and-task-breakdown → Break into verifiable chunks
5.  context-engineering         → Load the right context
6.  source-driven-development   → Verify against official docs
7.  incremental-implementation  → Build slice by slice
8.  observability-and-instrumentation → Instrument as you build (runs parallel with 7-9, not after)
9.  doubt-driven-development    → Cross-examine non-trivial decisions in-flight
10. test-driven-development     → Prove each slice works
11. code-review-and-quality     → Review before merge
12. code-simplification         → Reduce unnecessary complexity while preserving behavior
13. git-workflow-and-versioning → Clean commit history
14. documentation-and-adrs      → Document decisions
15. deprecation-and-migration   → Retire old systems and move users safely when needed
16. shipping-and-launch         → Deploy safely
```

Nicht jede Aufgabe braucht jeden Skill. Ein Bugfix braucht vielleicht nur: `debugging-and-error-recovery` → `test-driven-development` → `code-review-and-quality`.

## Kurzreferenz

| Phase | Skill | Zusammenfassung in einem Satz |
|-------|-------|-----------------|
| Define | interview-me | Herausarbeiten, was der Nutzer wirklich will, bevor ein Plan, eine Spec oder Code existiert |
| Define | idea-refine | Ideen durch strukturiertes divergentes und konvergentes Denken verfeinern |
| Define | spec-driven-development | Anforderungen und Akzeptanzkriterien vor dem Code |
| Plan | planning-and-task-breakdown | In kleine, verifizierbare Aufgaben zerlegen |
| Build | incremental-implementation | Dünne vertikale Scheiben, jede testen, bevor erweitert wird |
| Build | source-driven-development | Vor der Implementierung gegen die offizielle Dokumentation verifizieren |
| Build | doubt-driven-development | Adversariales Review mit frischem Kontext für jede nicht-triviale Entscheidung |
| Build | context-engineering | Der richtige Kontext zur richtigen Zeit |
| Build | frontend-ui-engineering | Produktionsreife UI mit Barrierefreiheit |
| Build | api-and-interface-design | Stabile Schnittstellen mit klaren Verträgen |
| Verify | test-driven-development | Zuerst ein fehlschlagender Test, dann zum Bestehen bringen |
| Verify | browser-testing-with-devtools | Chrome DevTools MCP zur Laufzeit-Verifikation |
| Verify | debugging-and-error-recovery | Reproduzieren → eingrenzen → beheben → absichern |
| Review | code-review-and-quality | Review auf fünf Achsen mit Quality Gates |
| Review | code-simplification | Verhalten bewahren und unnötige Komplexität reduzieren |
| Review | security-and-hardening | OWASP-Prävention, Eingabevalidierung, Least Privilege |
| Review | performance-optimization | Erst messen, nur optimieren, was zählt |
| Ship | git-workflow-and-versioning | Atomare commits, saubere Historie |
| Ship | ci-cd-and-automation | Automatisierte Quality Gates bei jeder Änderung |
| Ship | deprecation-and-migration | Alte Systeme entfernen und Nutzer sicher migrieren |
| Ship | documentation-and-adrs | Das Warum dokumentieren, nicht nur das Was |
| Ship | observability-and-instrumentation | Strukturierte Logs, RED-Metriken, Traces, symptombasierte Alerts |
| Ship | shipping-and-launch | Pre-Launch-Checkliste, Monitoring, Rollback-Plan |
