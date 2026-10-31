---
name: doubt-driven-development
description: Unterzieht jede nicht triviale Entscheidung einem adversarialen Review mit frischem Kontext, bevor sie Bestand hat. Verwenden, wenn jede Annahme vor dem Weitermachen ins Kreuzverhör soll, wenn ein Plan auf versteckte Fehlermodi hin belastet wird, wenn Korrektheit wichtiger ist als Tempo, bei Arbeit in unbekanntem Code, bei hohem Risiko (Production-Auth, sicherheitskritische Logik, riskante Migration, irreversible Operationen) oder immer dann, wenn sich ein selbstsicheres Ergebnis jetzt günstiger verifizieren lässt, als es später zu debuggen. Auslöser wie „hinterfrag diese Entscheidung kritisch“, „versuch meinen Plan zu widerlegen“, „stell diese Annahme auf den Prüfstand“, „such die Schwachstellen in meinem Ansatz“, „mach ein Doubt-Review, bevor wir committen“.
---

# Doubt-Driven Development

## Überblick

Eine selbstsichere Antwort ist nicht automatisch eine korrekte. In langen Sessions sammelt sich Kontext an, der Annahmen unbemerkt zu „Fakten“ macht. Doubt-driven development ist die Disziplin, vor jedem nicht trivialen Ergebnis einen Reviewer mit frischem Kontext zu materialisieren, der darauf ausgerichtet ist, zu **widerlegen**, nicht zu bestätigen.

Das ist nicht `/review`. `/review` ist ein Urteil über ein fertiges Artefakt. Hier geht es um eine Haltung während der Arbeit: Nicht triviale Entscheidungen werden ins Kreuzverhör genommen, solange Kurskorrekturen noch günstig sind.

## Wann verwenden

Eine Entscheidung ist **nicht trivial**, wenn mindestens eine dieser Bedingungen zutrifft:

- Sie führt Verzweigungslogik ein oder ändert sie
- Sie überschreitet eine Modul- oder Servicegrenze
- Sie behauptet eine Eigenschaft, die das Typsystem oder der Compiler nicht prüfen kann (Thread-Sicherheit, Idempotenz, Reihenfolge, Invarianten)
- Ihre Korrektheit hängt von Kontext ab, den der spätere Leser nicht sehen kann
- Ihr Wirkungsradius ist irreversibel (Production-Deploy, Datenmigration, Änderung der öffentlichen API)

Wende den Skill an, wenn du:

- kurz davor bist, unter Unsicherheit eine Architekturentscheidung zu treffen
- kurz davor bist, nicht trivialen Code zu committen
- kurz davor bist, eine nicht offensichtliche Tatsache zu behaupten („das ist sicher“, „das skaliert“, „das entspricht der Spec“)
- in Code arbeitest, den du nicht vollständig verstehst

**Wann NICHT verwenden:**

- Mechanische Operationen (Umbenennen, Formatieren, Dateien verschieben)
- Eine klare, eindeutige Nutzeranweisung befolgen
- Bestehenden Code lesen oder zusammenfassen
- Einzeilige Änderungen mit offensichtlicher Korrektheit
- Reine Tooling-Operationen (Tests ausführen, Dateien auflisten)
- Der Nutzer hat ausdrücklich Tempo vor Verifikation verlangt

Wer jeden Tastenanschlag anzweifelt, liefert nichts aus. Der Skill gilt nur für nicht triviale Entscheidungen im obigen Sinne.

## Lade-Constraints

Dieser Skill ist für den **Orchestrator der Hauptsession** gedacht, in dem Schritt 3 (DOUBT, unten im Detail) einen Reviewer mit frischem Kontext starten kann.

- **Füge diesen Skill NICHT zum `skills:`-Frontmatter einer Persona hinzu.** Eine Persona, die Schritt 3 befolgt, würde eine weitere Persona starten – das Orchestrierungs-Anti-Pattern, das `../../references/orchestration-patterns.md` ausdrücklich verbietet („personas do not invoke other personas“).
- **Wenn du diesen Skill innerhalb eines Subagent-Kontexts anwendest** (in dem Claude Code verschachteltes Starten von Subagents verhindert): Bevorzugt meldest du dem Nutzer, dass doubt-driven nicht verschachtelt laufen kann, und überlässt es der Hauptsession. Nur als letzter Ausweg gibt es einen abgeschwächten Fallback mit Selbstbefragung: Formuliere ARTIFACT + CONTRACT als frischen Selbst-Prompt mit einer harten gedanklichen Trennung von deinen bisherigen Überlegungen und durchlaufe die Schritte 1–5. Das ist **kein Review mit frischem Kontext** (du trägst deinen eigenen Kontext mit dir), also kennzeichne das Ergebnis als abgeschwächt und eskaliere bevorzugt, sobald der Nutzer erreichbar ist.

## Der Ablauf

Kopiere diese Checkliste, wenn du den Skill anwendest:

```
Doubt cycle:
- [ ] Step 1: CLAIM — wrote the claim + why-it-matters
- [ ] Step 2: EXTRACT — isolated artifact + contract, stripped reasoning
- [ ] Step 3: DOUBT — invoked fresh-context reviewer with adversarial prompt
- [ ] Step 4: RECONCILE — classified every finding against the artifact text
- [ ] Step 5: STOP — met stop condition (trivial findings, 3 cycles, or user override)
```

### Schritt 1: CLAIM — Mach sichtbar, was gelten soll

Benenne die Entscheidung in zwei bis drei Zeilen:

```
CLAIM: "The new caching layer is thread-safe under the
        read-heavy workload described in the spec."
WHY THIS MATTERS: a race here corrupts user data and is
                  hard to detect in QA.
```

Wenn du den Claim nicht so kompakt formulieren kannst, hast du ein Bauchgefühl, keine Entscheidung. Mach ihn sichtbar, bevor du ihn prüfst.

### Schritt 2: EXTRACT — Kleinste prüfbare Einheit

Ein Reviewer mit frischem Kontext braucht das **Artefakt** und den **Contract**, nicht den Weg dorthin.

- Code: der Diff oder die Funktion – nicht die ganze Datei
- Entscheidung: der Vorschlag in 3–5 Sätzen plus die Constraints, die er erfüllen muss
- Behauptung: der Claim plus die Belege, die ihn angeblich stützen (getrennt vom CLAIM-Block aus Schritt 1, der die zu prüfende Hypothese des Orchestrators ist)

Entferne deine Argumentation. Wenn du Schlussfolgerungen übergibst, bekommst du eine Bestätigung deiner Schlussfolgerungen zurück. Die Einheit muss so klein sein, dass ein Reviewer sie in einem Durchgang erfassen kann – bei einem PR mit 500 Zeilen zerlege zuerst.

Entferne Argumentation, nicht Belege: Widerspricht ein Aufrufer, eine Absicherung oder ein Test dem Claim, gehört er in die Einheit.

### Schritt 3: DOUBT — Reviewer mit frischem Kontext aufrufen

Der Prompt des Reviewers **muss adversarial sein**. Die Rahmung entscheidet über die Antwort.

```
Adversarial review. Find what is wrong with this artifact.
Assume the author is overconfident. Look for:
- Unstated assumptions
- Edge cases not handled
- Hidden coupling or shared state
- Ways the contract could be violated
- Existing conventions this might break
- Failure modes under unexpected input

Do NOT validate. Do NOT summarize. Find issues, or state
explicitly that you cannot find any after thorough examination.

ARTIFACT: <paste artifact>
CONTRACT: <paste contract>
```

**Übergib nur ARTIFACT + CONTRACT. Übergib NICHT den CLAIM.** Gibst du dem Reviewer deine Schlussfolgerung, verzerrt das ihn in Richtung Zustimmung. Der Reviewer muss unabhängig feststellen, ob das Artefakt den Contract erfüllt.

In Claude Code starten die rollenbasierten Reviewer in `agents/` per Design mit isoliertem Kontext und sind hier verwendbar – Besetzung und Zuordnung je Fachgebiet findest du in `agents/`.

**Der obige adversariale Prompt hat Vorrang vor dem Standard-Antwortformat der Persona.** Personas wie `code-reviewer` sind darauf ausgelegt, ausgewogene Urteile mit Stärken und Schwächen zu liefern; doubt-driven braucht eine Ausgabe, die nur Probleme enthält. Füge den adversarialen Prompt wortgetreu in den Aufruf ein, damit er das Standardverhalten der Persona überschreibt. Lässt sich das Antwortformat einer Persona nicht sauber überschreiben, weiche auf einen generischen Subagent mit dem adversarialen Prompt aus.

#### Cross-Model-Eskalation

Ein Reviewer aus demselben Modell teilt blinde Flecken mit dem ursprünglichen Autor – ein unvoreingenommeneres Modell mit anderer Architektur findet sie. Doubt-driven ist für nicht triviale Entscheidungen ohnehin Opt-in, daher gehört das Angebot eines Cross-Model-Reviews in diesem Rahmen zum Wert des Skills und ist keine optionale Reibung.

**Interaktive Sessions: immer anbieten. Nie stillschweigend überspringen.**

**Schritt 1: Den Nutzer fragen**

Halte nach dem Single-Model-Review aus Schritt 3 oben, aber vor RECONCILE, an und frage:

> *„Single-Model-Review abgeschlossen. Möchtest du eine Zweitmeinung von einem anderen Modell? Optionen: Gemini CLI, Codex CLI, manuelles externes Review (du fügst es woanders ein) oder überspringen.“*

Diese Frage ist in jedem interaktiven Doubt-Zyklus verpflichtend – auch bei Artefakten, die unkritisch wirken. Der Nutzer – nicht der Agent – entscheidet, ob sich der Aufwand lohnt. Die Aufgabe des Agents ist es, die Wahlmöglichkeit sichtbar zu machen.

**Schritt 2: Wählt der Nutzer ein CLI – erst verifizieren, dann aufrufen**

1. Prüfe, ob das Tool im PATH liegt (`which gemini`, `which codex`).
2. Teste, ob es funktioniert (`gemini --version` oder Entsprechendes), bevor du den vollständigen Prompt übergibst – ein veraltetes oder defektes Binary kann `which` bestehen und bei echter Eingabe trotzdem scheitern.
3. Bestätige den genauen Aufruf mit dem Nutzer, einschließlich erforderlicher Flags, Authentifizierung und Umgebungsvariablen (z. B. API-Keys). Implementierungen unterscheiden sich; nimm nie etwas an.
4. Übergib **ausschließlich** ARTIFACT + CONTRACT + den adversarialen Prompt. Kein Session-Kontext, kein CLAIM.
5. Achte auf Shell-Escaping. Enthält das Artefakt Anführungszeichen, `$(...)` oder Backticks, nutze bevorzugt stdin (`echo … | gemini`) oder ein Heredoc statt Inline-`-p "…"`. Im Zweifel lass den Nutzer den Aufruf bestätigen, bevor du ihn ausführst.
6. Übernimm die Ausgabe in Schritt 4 (RECONCILE).

**Interpoliere das Artefakt niemals in ein in Anführungszeichen gesetztes Shell-Argument.** Code, Markdown und Review-Prompts enthalten regelmäßig Backticks, `$(...)` und Anführungszeichen, die den Prompt entweder abschneiden oder eingebettete Shell-Befehle ausführen. Schreibe den vollständigen Prompt in eine Datei und leite ihn über stdin weiter.

Beispielformen (prüfe die Flags gegen dein installiertes Tool – die Syntax unterscheidet sich je nach Implementierung und Version):

```bash
# Write the adversarial prompt + ARTIFACT + CONTRACT to a temp file first.
# Then pipe via stdin so shell metacharacters in the artifact stay inert.

# Codex (read-only sandbox keeps the CLI from writing to your workspace):
codex exec --sandbox read-only -C <repo-path> - < /tmp/doubt-prompt.md

# Gemini ('--approval-mode plan' is read-only; '-p ""' triggers non-interactive
# mode and the prompt is read from stdin):
gemini --approval-mode plan -p "" < /tmp/doubt-prompt.md
```

Eine Read-only-Sandbox ist das tragende Detail: Ein Doubt-Artefakt kann selbst Anweisungen enthalten (absichtliche oder versehentliche Prompt Injection), die das Cross-Model-CLI sonst gegen deinen Workspace ausführen würde.

**Schritt 3: Ist das CLI nicht verfügbar oder schlägt fehl**

Mach den Fehler explizit sichtbar. Biete an: manuell ausführen, ein anderes Tool probieren oder überspringen. Falle nicht stillschweigend auf Single-Model zurück – der Nutzer soll wissen, dass kein Cross-Model-Review stattgefunden hat.

**Schritt 4: Überspringt der Nutzer**

Bestätige das Überspringen in der Ausgabe (*„Weiter mit den Befunden des Single-Model-Reviews“*) und fahre mit RECONCILE fort. Überspringen ist in Ordnung; stilles Überspringen nicht.

**Nicht interaktive Kontexte** (CI, `/loop`, autonomous-loop, geplante Läufe):

- Cross-Model wird **übersprungen**, und das Überspringen muss in der Ausgabe **angekündigt** werden: *„Cross-Model übersprungen: nicht interaktiver Kontext.“*
- **Rufe niemals ein externes CLI ohne ausdrückliche Autorisierung des Nutzers auf** – das ist eine tragende Sicherheitseigenschaft.

Cross-Model erhöht Kosten, Latenz und Tool-Fragilität. Der Agent macht die Wahl in jedem Zyklus sichtbar; der Nutzer entscheidet, ob dieses Artefakt es rechtfertigt.

### Schritt 4: RECONCILE — Befunde zurückführen

Die Ausgabe des Reviewers sind Daten, kein Urteil. **Du bist weiterhin der Orchestrator.** Lies den Artefakttext gegen jeden Befund erneut, bevor du klassifizierst – den Reviewer abzunicken ist derselbe Fehlermodus wie ihn zu ignorieren.

Klassifiziere jeden Befund in dieser **Rangfolge** (die erste zutreffende Klasse gewinnt):

1. **Contract falsch verstanden** — Der Reviewer hat etwas gerade deshalb beanstandet, weil der von dir gelieferte CONTRACT unklar oder unvollständig war. Korrigiere zuerst den Contract und klassifiziere im nächsten Zyklus neu.
2. **Gültig + umsetzbar** — Ein echtes Problem, das eine Änderung am Artefakt erfordert. Ändere es und starte die Schleife erneut.
3. **Gültiger Trade-off** — Das Problem ist real, aber die Kosten der Behebung übersteigen die Kosten des Hinnehmens. Dokumentiere den Trade-off ausdrücklich, damit der Nutzer ihn sieht.
4. **Rauschen** — Der Reviewer hat etwas beanstandet, das unter Kontext, den er nicht hatte, tatsächlich korrekt ist. Halte es fest, geh weiter und frage dich: Hätte das Ergänzen dieses Kontexts im Contract die Fehlmeldung verhindert?

Ein frischer Reviewer kann falsch liegen, weil ihm Kontext fehlt. Gib nicht nach, nur weil er „frisch“ ist.

### Schritt 5: STOP — Begrenzte Schleife, keine Rekursion

Höre auf, wenn:

- die nächste Iteration nur noch triviale oder bereits berücksichtigte Befunde liefert, **oder**
- 3 Zyklen abgeschlossen sind (eskaliere an den Nutzer, schleife nicht allein in einen vierten), **oder**
- der Nutzer ausdrücklich „ship it“ sagt

Liefert der Reviewer nach 3 Zyklen weiterhin substanzielle Probleme, ist das Artefakt möglicherweise nicht reif. Sprich das gegenüber dem Nutzer an – drei ungelöste Zyklen sind eine Information über das Artefakt, kein Grund für weitere Schleifen.

Wenn 3 Zyklen „offensichtlich nicht ausreichen“, weil das Artefakt groß ist, ist das Artefakt zu groß: Geh zurück zu Schritt 2 und zerlege es. Hebe die Grenze nicht auf.

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Ich bin sicher, den Zweifelsschritt kann ich überspringen“ | Sicherheit korreliert bei neuartigen Problemen schlecht mit Korrektheit. Gerade in Momenten der Gewissheit verstecken sich blinde Flecken. |
| „Einen Reviewer zu starten ist teuer“ | Einen falschen commit in Production zu debuggen ist teurer. Die Prüfung ist begrenzt, der Bug nicht. |
| „Der Reviewer wird nur Nits liefern“ | Nur wenn der Prompt nicht eingegrenzt ist. Beschränke ihn auf „Probleme, die dazu führen würden, dass dies den Contract verletzt“. |
| „Ich mache Zweifel am Ende mit `/review`“ | `/review` ist ein finales Gate. Doubt-driven fängt falsche Richtungen früh ab, wenn Kurskorrekturen günstig sind. Zum PR-Zeitpunkt ist es zu spät. |
| „Wenn ich jeden Schritt anzweifle, liefere ich nie aus“ | Der Skill gilt für nicht triviale Entscheidungen, nicht für jeden Tastenanschlag. Lies „Wann NICHT verwenden“ noch einmal. |
| „Zwei Meinungen sind immer besser als eine“ | Nicht, wenn die zweite weniger Kontext hat und Rauschen erzeugt. Gleiche ab, statt dich zu fügen. |
| „Der Reviewer war anderer Meinung, also lag ich falsch“ | Dem Reviewer fehlt dein Kontext – Widerspruch ist eine Information, kein Urteil. Lies das Artefakt erneut, klassifiziere, entscheide dann. |
| „Cross-Model ist immer besser“ | Cross-Model findet blinde Flecken, die ein einzelnes Modell mit sich selbst teilt, bringt aber Kosten und Tool-Fragilität mit. Biete es in jedem interaktiven Doubt-Zyklus an – der Nutzer entscheidet, ob das Artefakt es rechtfertigt. Die Aufgabe des Agents ist, die Wahl sichtbar zu machen, nicht sie zu versperren. |
| „Der Nutzer hat einmal ja gesagt, also darf ich das CLI weiter aufrufen“ | Jeder Aufruf ist eine eigene Autorisierung. Artefakt, Prompt und Flags ändern sich zwischen den Aufrufen – bestätige den genauen Befehl vor jedem Lauf erneut mit dem Nutzer. |

## Warnsignale

- Einen Reviewer mit frischem Kontext für eine einzeilige Umbenennung oder Formatierungsänderung starten
- Die Ausgabe des Reviewers als maßgeblich behandeln, ohne den Artefakttext erneut zu lesen
- Mehr als 3 Zyklen schleifen, ohne an den Nutzer zu eskalieren
- Den Reviewer mit „ist das gut?“ statt „finde Probleme“ ansprechen
- Zweifel unter Zeitdruck bei einer folgenreichen Entscheidung überspringen
- Frischen Kontext für ein unverändertes Artefakt erneut starten (du bekommst dieselben Befunde; du zögerst nur)
- **Doubt-Theater (prüfbares Signal)**: Über 2 oder mehr Zyklen, in denen der Reviewer substanzielle Befunde geliefert hat, wurde kein einziger Befund als umsetzbar klassifiziert. Du validierst, statt zu zweifeln. Stopp und eskaliere.
- Erst nach dem commit zweifeln – das ist `/review`, nicht doubt-driven development
- Einen Aufruf eines externen CLI fest verdrahten, ohne mit dem Nutzer zu bestätigen, dass das Tool existiert, konfiguriert ist und genau diese Syntax akzeptiert
- **Cross-Model in einem interaktiven Doubt-Zyklus stillschweigend überspringen.** Auch wenn du es nicht empfiehlst, muss das Angebot sichtbar sein. Überspringen ist in Ordnung; stilles Überspringen nicht.
- Stillschweigend zurückfallen, wenn ein externes CLI Fehler meldet oder fehlt – mach den Fehler sichtbar und lass den Nutzer umlenken
- Den Contract aus der Eingabe des Reviewers entfernen
- Den CLAIM an den Reviewer übergeben (verzerrt in Richtung Zustimmung)

## Zusammenspiel mit anderen Skills

- **`code-review-and-quality` / `/review`**: ergänzend. `/review` ist das nachträgliche PR-Urteil; doubt-driven läuft während der Arbeit pro Entscheidung. Nutze beides.
- **`source-driven-development`**: SDD verifiziert *Fakten über Frameworks* gegen die offizielle Dokumentation. Doubt-driven verifiziert *deine Argumentation über das Artefakt*. SDD prüft, dass die API existiert; doubt-driven prüft, ob du sie unter dem Contract korrekt verwendet hast.
- **`test-driven-development`**: Der RED-Schritt von TDD ist konkret gewordener Zweifel – ein fehlschlagender Test ist ein Widerlegungsversuch. Wo TDD greift, *ist* dieser fehlschlagende Test der Zweifelsschritt für Verhaltensbehauptungen.
- **`debugging-and-error-recovery`**: Wenn der Reviewer einen echten Fehlermodus aufdeckt, wechsle in den Debugging-Skill, um ihn einzugrenzen und zu beheben.
- **Orchestrierungsregeln des Repos** (`../../references/orchestration-patterns.md`): Dieser Skill orchestriert aus der Hauptsession. Eine Persona, die eine andere Persona aufruft, ist Anti-Pattern B – siehe Lade-Constraints oben.

## Verifikation

Nach der Anwendung von doubt-driven development:

- [ ] Jede nicht triviale Entscheidung (laut obiger Definition) wurde vor ihrem Bestand ausdrücklich als CLAIM benannt
- [ ] Mindestens ein Review mit frischem Kontext pro nicht trivialem Artefakt (ein fehlschlagender Test aus dem RED-Schritt von TDD erfüllt das für Verhaltensbehauptungen, siehe Zusammenspiel mit anderen Skills)
- [ ] Der Reviewer erhielt ARTIFACT + CONTRACT – NICHT den CLAIM, NICHT deine Argumentation
- [ ] Der Prompt des Reviewers war adversarial („finde Probleme“), nicht bestätigend („ist das gut“)
- [ ] Befunde wurden gegen den Artefakttext klassifiziert (nicht abgenickt), nach der Rangfolge: Contract falsch verstanden / umsetzbar / Trade-off / Rauschen
- [ ] Eine Stoppbedingung wurde erreicht (triviale Befunde, 3 Zyklen oder Override durch den Nutzer)
- [ ] Im interaktiven Modus wurde Cross-Model dem Nutzer **ausdrücklich angeboten** (unabhängig vom Risiko des Artefakts) und die Antwort in der Ausgabe bestätigt
- [ ] Im nicht interaktiven Modus wurde Cross-Model übersprungen und das Überspringen angekündigt
- [ ] Jedem Aufruf eines externen CLI gingen eine PATH-Prüfung, ein Test des funktionierenden Binarys, eine Syntaxbestätigung mit dem Nutzer und eine ausdrückliche Autorisierung zur Ausführung voraus
