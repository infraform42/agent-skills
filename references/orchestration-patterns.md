# Orchestrierungsmuster

Referenzkatalog der Agent-Orchestrierungsmuster, die dieses Repo empfiehlt, sowie der Anti-Patterns, die du vermeiden solltest. Lies ihn, bevor du einen neuen Slash-Command hinzufügst, der mehrere Personas koordiniert, oder bevor du eine neue Persona einführst, die bestehende Personas „umhüllt“.

Die maßgebliche Regel: **Der Nutzer (oder ein Slash-Command) ist der Orchestrator. Personas rufen keine anderen Personas auf.** Skills sind verpflichtende Zwischenschritte innerhalb des Workflows einer Persona.

---

## Empfohlene Muster

### 1. Direkter Aufruf (keine Orchestrierung)

Eine Persona, eine Perspektive, ein Artefakt. Die Standardwahl und die günstigste Option.

```
user → code-reviewer → report → user
```

**Verwenden, wenn:** die Arbeit eine Perspektive auf ein Artefakt ist und sich in einem Satz beschreiben lässt.

**Beispiele:**
- „Review this PR“ → `code-reviewer`
- „Find security issues in `auth.ts`“ → `security-auditor`
- „What tests are missing for the checkout flow?“ → `test-engineer`

**Kosten:** ein Round Trip. Die Baseline, mit der du orchestrierte Muster immer vergleichen solltest.

---

### 2. Slash-Command für eine einzelne Persona

Ein Slash-Command, der eine Persona mit den Skills des Projekts umhüllt. Das erspart dem Nutzer, den Workflow jedes Mal neu zu erklären.

```
/review → code-reviewer (with code-review-and-quality skill) → report
```

**Verwenden, wenn:** derselbe Aufruf einer einzelnen Persona mit demselben Setup wiederholt vorkommt.

**Beispiele in diesem Repo:** `/review`, `/test`, `/code-simplify`.

**Kosten:** dieselben wie beim direkten Aufruf. Der Slash-Command ist nur ein gespeicherter Prompt.

**Gegensignal:** Wenn der Rumpf des Slash-Commands größtenteils aus „entscheide, welche Persona aufzurufen ist“ besteht, lösche ihn und lass den Nutzer die Persona direkt aufrufen.

---

### 3. Paralleles Fan-out mit Merge

Mehrere Personas bearbeiten gleichzeitig denselben Input und liefern jeweils einen unabhängigen Report. Ein Merge-Schritt (im Kontext des Hauptagenten) führt sie zu einer einzigen Entscheidung zusammen.

```
                    ┌─→ code-reviewer    ─┐
/ship → fan out  ───┼─→ security-auditor ─┤→ merge → go/no-go + rollback
                    └─→ test-engineer    ─┘
```

**Verwenden, wenn:**
- die Teilaufgaben wirklich unabhängig sind (kein gemeinsamer veränderlicher Zustand, keine Reihenfolgeabhängigkeit)
- jeder Subagent von einem eigenen Kontextfenster profitiert
- der Merge-Schritt klein genug ist, um im Hauptkontext zu bleiben
- die Wall-Clock-Latenz eine Rolle spielt

**Beispiele in diesem Repo:** `/ship`.

**Kosten:** N parallele Subagent-Kontexte + ein Merge-Turn. Höher als beim direkten Aufruf, aber schneller in der Wall-Clock-Zeit und mit besseren Reports, weil jeder Subagent auf seine einzelne Perspektive fokussiert bleibt.

**Checkliste zur Validierung, bevor du dieses Muster einsetzt:**
- [ ] Kann ich alle Subagents gleichzeitig laufen lassen, ohne Probleme mit der Reihenfolge?
- [ ] Liefert jede Persona eine andere *Art* von Befund und nicht nur denselben Befund aus anderem Blickwinkel?
- [ ] Passt der Merge-Schritt in den verbleibenden Kontext des Hauptagenten?
- [ ] Ist die Wartezeit des Nutzers lang genug, dass Parallelität tatsächlich spürbar ist?

Lautet eine Antwort „nein“, weiche auf den direkten Aufruf oder einen Command für eine einzelne Persona aus.

---

### 4. Sequenzielle Pipeline als vom Nutzer gesteuerte Slash-Commands

Der Nutzer führt Slash-Commands in einer festgelegten Reihenfolge aus und trägt dabei Kontext (oder die commit-Historie) von einem zum nächsten. Es gibt keinen Orchestrator-Agenten – der Nutzer IST der Orchestrator.

```
user runs:  /spec  →  /plan  →  /build  →  /test  →  /review  →  /ship
```

**Verwenden, wenn:** der Workflow Abhängigkeiten hat (jeder Schritt braucht das Ergebnis des vorherigen) und menschliches Urteilsvermögen zwischen den Schritten Mehrwert bringt.

**Beispiele in diesem Repo:** der gesamte Lebenszyklus DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP.

**Kosten:** ein Subagent-Kontext pro Schritt. Für die Orchestrierungsebene fallen keine Kosten an, weil es keinen Orchestrator-Agenten gibt.

**Warum nicht automatisieren:** Ein LLM-„Lifecycle-Orchestrator“ würde (a) Nuancen zwischen den Schritten verlieren, weil er für die Übergabe zusammenfassen muss, (b) die menschlichen Checkpoints überspringen, die Arbeit in die falsche Richtung früh abfangen, und (c) die Token-Kosten durch Paraphrasier-Turns verdoppeln.

---

### 5. Research-Isolation (Kontexterhalt)

Erfordert eine Aufgabe das Lesen großer Materialmengen, die den Hauptkontext nicht verschmutzen sollen, starte einen Research-Subagent, der nur eine Zusammenfassung zurückgibt.

```
main agent → research sub-agent (reads 50 files) → digest → main agent continues
```

**Verwenden, wenn:**
- die Hauptsession auf eine nachgelagerte Aufgabe fokussiert bleiben muss
- das Ergebnis der Recherche deutlich kleiner ist als der Input, den sie verarbeitet
- die Entscheidungsqualität davon profitiert, dass der Hauptagent anschließend Raum zum Nachdenken hat

**Beispiele:** „Find every call site of this deprecated API across the monorepo“, „Summarize what these 30 ADRs say about caching.“

**Kosten:** ein isolierter Subagent-Kontext. Lohnt sich immer dann, wenn die Alternative wäre, Hunderte Dateien in den Hauptkontext zu laden.

**Nutze in Claude Code den eingebauten `Explore`-Subagent** statt eine eigene Research-Persona zu definieren. `Explore` läuft auf Haiku, hat keinen Zugriff auf Schreib-/Edit-Tools und ist genau für dieses Muster gebaut. Definiere einen eigenen Research-Subagent nur, wenn `Explore` nicht passt (z. B. wenn du einen domänenspezifischen System-Prompt brauchst, den das Modell nicht von selbst ableiten würde).

---

## Kompatibilität mit Claude Code

Dieser Katalog ist Harness-unabhängig, aber die meisten Leser werden ihn auf Claude Code ausführen. So bildet sich jedes Muster auf die Primitive von Claude Code ab – und so erzwingt die Plattform unsere Regeln teilweise von selbst.

### Wo Personas liegen

Plugin-Subagents liegen in `agents/` im Plugin-Root. Dieses Repo ist ein Plugin (`.claude-plugin/plugin.json`), daher werden `agents/code-reviewer.md`, `agents/security-auditor.md` und `agents/test-engineer.md` automatisch erkannt, sobald das Plugin aktiviert ist. Eine Pfadkonfiguration ist nicht nötig.

### Subagents vs. Agent Teams

Claude Code kennt zwei Parallelitäts-Primitive. Muster 3 (paralleles Fan-out mit Merge) entspricht **Subagents**. Brauchst du Teammates, die miteinander kommunizieren, nutze stattdessen **Agent Teams**.

| | Subagents | Agent Teams |
|--|-----------|-------------|
| Koordination | Der Hauptagent verteilt die Arbeit, Subagents berichten nur zurück | Teammates schreiben sich gegenseitig und teilen eine Aufgabenliste |
| Kontext | Eigenes Kontextfenster pro Subagent | Eigenes Kontextfenster pro Teammate |
| Wann verwenden | Unabhängige Aufgaben, die Reports liefern | Kollaborative Arbeit, die Diskussion erfordert |
| Status | Stabil | Experimentell – erfordert `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| Kosten | Niedriger | Höher – jeder Teammate ist eine eigene Claude-Instanz |

**Die Personas in diesem Repo funktionieren in beiden Modi.** Werden sie als Subagents gestartet (z. B. durch `/ship`), berichten sie ihre Befunde an die Hauptsession. Werden sie als Teammates gestartet (`Spawn a teammate using the security-auditor agent type…`), können sie die Befunde der anderen direkt hinterfragen. Die Persona-Definition ist dieselbe; nur der Kontext des Starts ändert sich.

Eine Feinheit: Die Frontmatter-Felder `skills` und `mcpServers` einer Persona werden berücksichtigt, wenn sie als Subagent läuft, aber **ignoriert, wenn sie als Teammate läuft** – Teammates laden Skills und MCP-Server aus deinen Projekt- und Nutzereinstellungen, genau wie eine normale Session. Hängt eine Persona davon ab, dass ein bestimmter Skill oder MCP-Server geladen ist, konfiguriere ihn auf Session-Ebene, damit er in beiden Modi verfügbar ist.

### Von der Plattform erzwungene Regeln

Zwei Regeln in diesem Katalog sind nicht bloß Konvention – Claude Code erzwingt sie:

- **„Subagents cannot spawn other subagents“** (wörtlich aus der Dokumentation). Anti-Pattern B (Persona ruft Persona auf) und Anti-Pattern D (tiefe Persona-Bäume) können in Claude Code konstruktionsbedingt nicht existieren.
- **„No nested teams“** – Teammates können keine eigenen Teams starten. Dieselben Anti-Patterns sind damit auch auf Team-Ebene blockiert.

Du kannst die Muster dieses Katalogs also übernehmen, ohne dir Sorgen zu machen, dass Contributors versehentlich die Anti-Patterns bauen. Sie werden schlicht nicht geladen.

### Eingebaute Subagents, die du kennen solltest

Prüfe vor dem Definieren eines eigenen Subagents, ob einer der folgenden die Rolle abdeckt:

| Eingebaut | Zweck |
|----------|---------|
| `Explore` | Schreibgeschützte Suche und Analyse der Codebasis. Nutze ihn für Muster 5 (Research-Isolation). |
| `Plan` | Schreibgeschützte Recherche im Plan-Modus. |
| `general-purpose` | Mehrstufige Aufgaben, die sowohl Erkundung als auch Änderungen erfordern. |

Definiere diese nicht neu. Setze deine spezialisierten Personas (code-reviewer, security-auditor, test-engineer) darauf auf.

### Frontmatter-Einschränkungen für Plugin-Agents

Plugin-Subagents unterstützen die Frontmatter-Felder `hooks`, `mcpServers` und `permissionMode` **nicht** – sie werden stillschweigend ignoriert. Braucht eine künftige Persona eines davon, muss der Nutzer die Datei stattdessen nach `.claude/agents/` oder `~/.claude/agents/` kopieren.

In Plugin-Agents funktionieren folgende Felder: `name`, `description`, `tools`, `disallowedTools`, `model`, `maxTurns`, `skills`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`. Setze `model` pro Persona, wenn du die Kosten optimieren willst (z. B. Haiku für die Coverage-Scans von `test-engineer`, Sonnet für `code-reviewer`, Opus für `security-auditor`).

### Mehrere Subagents parallel starten

In Claude Code erfordert das parallele Fan-out (Muster 3), **mehrere Agent-Tool-Aufrufe in einem einzigen Assistant-Turn** abzusetzen. Aufeinanderfolgende Turns serialisieren die Ausführung. `/ship` weist ausdrücklich darauf hin. Jeder neue Orchestrator-Command sollte das ebenfalls tun.

---

## Praxisbeispiel: Agent Teams für Debugging mit konkurrierenden Hypothesen

Dieses Beispiel zeigt, wann du statt des Subagent-Fan-outs von `/ship` zu **Agent Teams** greifen solltest. Die beiden Muster sehen aus der Ferne ähnlich aus – beide starten dieselben drei Personas –, aber der Nutzen entsteht an anderer Stelle.

### Das Szenario

> *Der Checkout hängt gelegentlich ca. 30 Sekunden, bevor er abschließt. Es passiert etwa einmal pro 50 Sessions. Keine Fehler in den Logs. Begann nach dem Release der letzten Woche.*

Plausible Ursachen (sich gegenseitig ausschließend, alle passen zu den Symptomen):

1. Eine Race Condition im neuen Payment-Confirmation-Flow
2. Eine Auth-Prüfung, die gelegentlich auf einen langsamen synchronen Netzwerkaufruf durchfällt
3. Ein fehlender Index auf einer Query, die mit der Warenkorbgröße skaliert
4. Eine instabile Drittanbieter-API, bei der das SDK stillschweigend wiederholt, bevor es in den Timeout läuft

Ein einzelner Agent wählt die erste plausible Theorie und hört auf zu suchen. Ein Subagent-Fan-out im Stil von `/ship` würde jede Persona unabhängig berichten lassen – aber ihre Reports treffen nie aufeinander, also schließt nichts die falschen Theorien aus.

Genau das ist der Fall, den die Agent-Teams-Dokumentation beschreibt: *„With multiple independent investigators actively trying to disprove each other, the theory that survives is much more likely to be the actual root cause.“*

### Warum das *kein* Job für `/ship` ist

| | `/ship` (Subagents) | Agent Teams |
|--|--------------------|-------------|
| Subagents sehen | Denselben Diff, unterschiedliche Blickwinkel | Eine gemeinsame Aufgabenliste, die Nachrichten der anderen |
| Output | Drei unabhängige Reports → ein Merge | Adversariale Debatte → Konsens über die Ursache |
| Passt, wenn | Du ein Urteil zu einem bekannten Artefakt willst | Du das Artefakt unter den Hypothesen erst *finden* willst |

`/ship` ist ein Urteil; Agent Teams sind eine Untersuchung.

### Setup (einmalig, pro Umgebung)

Agent Teams ist experimentell. In `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Erfordert Claude Code v2.1.32 oder neuer. Die Personas in diesem Repo werden automatisch übernommen – du musst keine Team-Konfigurationsdateien von Hand schreiben.

### Der Trigger-Prompt

Tippe in natürlicher Sprache in die Lead-Session:

```
Users report checkout hangs for ~30 seconds intermittently after last
week's release. No errors in logs.

Create an agent team to debug this with competing hypotheses. Spawn
three teammates using the existing agent types:

  - code-reviewer  — investigate race conditions and blocking calls
                     in the checkout code path
  - security-auditor — investigate auth checks, session handling,
                       and any synchronous network calls added recently
  - test-engineer  — propose tests that would distinguish between the
                     hypotheses and check coverage gaps in checkout

Have them message each other directly to challenge each other's
theories. Update findings as consensus emerges. Only converge when
two teammates agree they can disprove the others'.
```

Der Lead startet drei Teammates mit den Namen der vorhandenen Personas. Der Persona-Text wird dem System-Prompt jedes Teammates als zusätzliche Anweisung **angehängt** (zusätzlich zu den Team-Koordinationsanweisungen, die der Lead installiert); der obige Trigger-Prompt wird zu ihrer Aufgabe.

### Was passiert

1. Jeder Teammate läuft in seinem eigenen Kontextfenster und erkundet die Codebasis aus seinem eigenen Blickwinkel.
2. Teammates senden sich Befunde per `message` direkt zu. Der Lead muss nichts weiterreichen.
3. Die gemeinsame Aufgabenliste zeigt, wer was untersucht – jederzeit sichtbar mit `Ctrl+T` (In-Process-Modus) oder in einem tmux-Pane (Split-Modus).
4. Findet `code-reviewer` ein `Promise.all`, das sequenziell sein sollte, schreibt er `security-auditor`, um zu bestätigen, dass der Auth-Aufruf nicht Teil der Race Condition ist. `security-auditor` prüft und antwortet – entweder bestätigt er, dass die Race Condition das eigentliche Problem ist, oder er liefert Gegenbeweise.
5. `test-engineer` schlägt für die Theorie, die gerade führt, einen fokussierten Integrationstest vor, mit dem das Team verifiziert, bevor es den Konsens erklärt.
6. Der Lead führt den konvergierten Befund zusammen und präsentiert ihn dir.

Du kannst bei jedem Teammate eingreifen, indem du mit `Shift+Down` durchschaltest und tippst – nützlich, um einen Ermittler umzulenken, der in die falsche Richtung läuft.

### Wann aufräumen

Sobald die Untersuchung bei einer Ursache angekommen ist, sag dem Lead:

```
Clean up the team
```

Räume immer über den Lead auf, nie über einen Teammate (laut Dokumentation fehlt Teammates der vollständige Team-Kontext fürs Aufräumen).

### Kostenerwartung

Drei Sonnet-Teammates, die ca. 10–15 Minuten untersuchen, kosten spürbar mehr als dieselben drei Personas, die `/ship` als Subagents startet. Die Rechtfertigung ist die *Qualität der Schlussfolgerung* – beim Produktions-Debugging, wo ein falscher Fix teuer ist, sind die zusätzlichen Tokens ein Schnäppchen. Bei einem Routine-PR-Review bleib bei `/ship`.

### Anti-Pattern in diesem Szenario

Baue das **nicht** als `/debug`-Slash-Command nach, der Subagents verteilt. Subagents können einander keine Nachrichten schicken – du würdest die adversariale Debatte verlieren, die dieses Muster erst wirksam macht. Wenn ein Workflow immer wieder vorkommt, dokumentiere den obigen Trigger-Prompt als Snippet, statt ihn in einen Slash-Command zu packen, der Subagents zweckentfremdet.

### Wann Agent Teams *nicht* verwenden

- Produktionsreifes Urteil zu einem bekannten Diff → nutze `/ship` (Subagents).
- Eine Spezialistenperspektive auf ein Artefakt → direkter Persona-Aufruf.
- Sequenzieller Lebenszyklus (Spec → Plan → Build) → vom Nutzer gesteuerte Slash-Commands (Muster 4).
- Leselastige Recherche mit kleiner Zusammenfassung → eingebauter `Explore`-Subagent.

Greife nur dann zu Agent Teams, wenn Teammates sich gegenseitig hinterfragen **müssen**, um die richtige Antwort zu liefern.

---

## Anti-Patterns

### A. Router-Persona („Meta-Orchestrator“)

Eine Persona, deren Aufgabe es ist zu entscheiden, welche andere Persona aufgerufen wird.

```
/work → router-persona → "this needs a review" → code-reviewer → router (paraphrases) → user
```

**Warum das scheitert:**
- Reine Routing-Schicht ohne fachlichen Mehrwert
- Fügt zwei Paraphrasier-Hops hinzu → Informationsverlust + etwa doppelte Token-Kosten
- Der Nutzer wusste bereits, dass er ein Review wollte; er hätte direkt `/review` aufrufen können
- Wiederholt die Arbeit, die Slash-Commands und das Intent-Mapping in `AGENTS.md` bereits leisten

**Stattdessen:** Slash-Commands ergänzen oder verfeinern. Das Mapping von Intent auf Command in `AGENTS.md` dokumentieren.

---

### B. Persona, die eine andere Persona aufruft

Ein `code-reviewer`, der intern `security-auditor` aufruft, sobald er Auth-Code sieht.

**Warum das scheitert:**
- Personas sind dafür ausgelegt, eine einzelne Perspektive zu liefern; sie zu verketten untergräbt das
- Die Zusammenfassung, die die aufrufende Persona weitergibt, verliert Kontext, den die aufgerufene Persona braucht
- Fehlerbilder vervielfachen sich (welches Ausgabeformat gilt? wessen Regeln gelten?)
- Verbirgt die Kosten vor dem Nutzer

**Stattdessen:** Die aufrufende Persona *empfiehlt* in ihrem Report ein Folge-Audit. Der Nutzer oder ein Slash-Command führt den zweiten Durchlauf aus.

---

### C. Sequenzieller Orchestrator, der paraphrasiert

Ein Agent, der im Auftrag des Nutzers nacheinander `/spec`, `/plan`, `/build` usw. aufruft.

**Warum das scheitert:**
- Verliert die menschlichen Checkpoints, die Arbeit in die falsche Richtung abfangen
- Jede Übergabe fasst Kontext zusammen – über eine lange Pipeline summiert sich der Drift
- Verdoppelt die Token-Kosten: Orchestrator-Turn + Subagent-Turn für jeden Schritt
- Nimmt dem Nutzer genau dort die Handlungsfreiheit, wo Urteilsvermögen am wichtigsten ist

**Stattdessen:** Den Nutzer als Orchestrator belassen. Die empfohlene Reihenfolge in `README.md` dokumentieren und Nutzer sie selbst aufrufen lassen.

---

### D. Tiefe Persona-Bäume

`/ship` ruft einen `pre-ship-coordinator` auf, der einen `quality-coordinator` aufruft, der `code-reviewer` aufruft.

**Warum das scheitert:**
- Jede Ebene fügt Latenz und Tokens ohne Entscheidungswert hinzu
- Debugging wird zur mehrstufigen Untersuchung
- Die Persona-Blätter verlieren durch mehrere Zusammenfassungsschritte Kontext

**Stattdessen:** Die Orchestrierungstiefe auf höchstens 1 halten (Slash-Command → Personas). Der Merge passiert im Hauptagenten.

---

## Entscheidungsfluss

Gehe bei einem neuen orchestrierten Workflow diesen Ablauf durch:

```
Is the work one perspective on one artifact?
├── Yes → Direct invocation. Stop.
└── No  → Will the same composition repeat?
         ├── No  → Direct invocation, ad hoc. Stop.
         └── Yes → Are sub-tasks independent?
                  ├── No  → Sequential slash commands run by user (Pattern 4).
                  └── Yes → Parallel fan-out with merge (Pattern 3).
                           Validate against the checklist above.
                           If any check fails → fall back to single-persona command (Pattern 2).
```

---

## Wann ein neues Muster in diesen Katalog gehört

Nimm einen neuen Eintrag erst auf, wenn:

1. du das Muster mindestens zweimal in echter Arbeit eingesetzt hast
2. du ein konkretes Artefakt in diesem Repo nennen kannst, das es demonstriert
3. du erklären kannst, warum ein bestehendes Muster nicht funktioniert hätte
4. du seinen Anti-Pattern-Schatten beschreiben kannst (was Leute stattdessen fälschlich bauen werden)

Voreilige Katalogeinträge werden zu Wunschdokumentation, der niemand folgt.
