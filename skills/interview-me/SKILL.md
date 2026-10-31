---
name: interview-me
description: "Interview Frage für Frage, bis die eigentliche Absicht klar ist (agent-skills). Nur verwenden, wenn der Nutzer diesen Skill ausdrücklich nennt. Für Befragungen im Alltag gelten grill-me und grilling."
---

# Interview Me

## Overview

Was Menschen verlangen und was sie tatsächlich wollen, sind zwei verschiedene Dinge. Sie bitten um „ein Dashboard“, weil man eben darum bittet, nicht weil ein Dashboard ihr Problem löst. Sie sagen „mach es schneller“, ohne eine Zielzahl zu nennen.

Der günstigste Zeitpunkt, diese Lücke zu finden, ist vor der Existenz von Plan, Spec oder Code. Sobald du angefangen hast zu bauen, sind die Wechselkosten real, und der Nutzer redet sich das Falsche zu einem „gut genug“ schön. Die Fehlpassung verfestigt sich.

Dieser Skill schließt die Lücke, bevor sie etwas kostet. Die anderen Skills der Define-Phase setzen voraus, dass du ungefähr weißt, was gewollt ist: `idea-refine` erzeugt Varianten aus einer Idee, `spec-driven-development` schreibt die Anforderungen auf, `doubt-driven-development` unterzieht einen Plan einem Stresstest, nachdem du einen entworfen hast. Interview-me ist der Teil vor all diesen: Du stellst jeweils eine Frage, versehen mit deiner besten Vermutung, bis du vorhersagen kannst, was der Nutzer sagen wird, bevor er es sagt.

## When to Use

Wende diesen Skill an, wenn:

- Der Anfrage mindestens eines davon fehlt: **wer** der Nutzer ist, **warum** er es will, wie **Erfolg** aussieht, was der bindende **Constraint** ist
- Die Anfrage konventionell statt konkret ist („Bau mir X“, „mach es schneller“) und du die Konvention nicht ohne Raten auflösen kannst
- Du versucht bist, mit Annahmen zu starten, die du nicht offengelegt hast
- Der Nutzer nicht gesagt hat, auf welchen Wert er optimiert, wenn zwei vernünftige Werte im Konflikt stehen (Einfachheit vs. Flexibilität, Kosten vs. Geschwindigkeit)
- Der Nutzer den Skill ausdrücklich aufruft: „interview me“, „grill me“, „before we start, are we sure?“, „stress-test my thinking“

**Wann NICHT verwenden:**

- Die Anfrage ist eindeutig und in sich geschlossen („benenne diese Variable um“, „behebe diesen Tippfehler“)
- Der Nutzer hat ausdrücklich Geschwindigkeit vor Verifikation verlangt
- Reine Informationsanfragen („Wie funktioniert X?“, „Was macht dieser Code?“)
- Mechanische Operationen (Umbenennungen, Formatierungen, Dateiverschiebungen)
- Du hast bereits ≥95 % Sicherheit; lies die Stopp-Bedingung unten noch einmal, bevor du annimmst, dass du sie nicht hast

## Loading Constraints

Dieser Skill braucht einen anwesenden, antwortenden Nutzer. **Rufe ihn nicht in nicht-interaktiven Kontexten auf**, etwa in CI-Pipelines, geplanten Läufen, `/loop` oder autonomous-loop. Bist du in einem davon und die Anfrage ist unterspezifiziert, melde das dem Nutzer als Blocker, statt zu raten.

## The Process

### Step 1: Hypothese aufstellen, mit einer Sicherheitszahl

Bevor du irgendetwas fragst, schreibe deine aktuell beste Lesart dessen, was der Nutzer will, in **einem Satz** auf, dazu eine ehrliche Sicherheitszahl (0–100 %):

```
HYPOTHESIS: You want a way to answer "how are we doing?" in standup, and "dashboard" was the convention that came to mind.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" means in context, and what success looks like
```

Die Zahl erzwingt Ehrlichkeit. Wenn du eine hohe Zahl notiert hast, aber die Reaktionen des Nutzers auf die nächsten drei Fragen nicht vorhersagen kannst, ist die Zahl falsch. Beginne mit der Sicherheit, die du vertreten kannst.

Liegt die Sicherheit unter ca. 70 %, hänge in derselben Zeile eine kurze Begründung an: was noch ungeklärt ist oder fehlt. Das zeigt dem Nutzer genau, was das Interview klären muss, und verhindert, dass die Zahl ein vages Signal bleibt.

### Step 2: Stelle jeweils eine Frage, jede mit einer Vermutung

Format:

```
Q: <one focused question>
GUESS: <your hypothesis for the answer, with the reasoning that produced it>
```

Warte auf die Reaktion des Nutzers, bevor du die nächste Frage stellst.

**Warum eine Frage nach der anderen statt eines Stapels:**

- Der Nutzer kann auf deine Hypothesen nicht reagieren, wenn du sie in einer Liste vergräbst
- Stapel verleiten zum Überfliegen und zu oberflächlichen Antworten
- Die dritte Frage hängt oft von der Antwort auf die erste ab; alle auf einmal zu stellen zementiert den falschen Rahmen
- Die Energie des Nutzers für sorgfältiges Nachdenken ist begrenzt; setze sie Frage für Frage ein

**Warum eine Vermutung anhängen:**

- Der Nutzer reagiert schneller auf eine falsche Vermutung, als er eine Antwort von Grund auf formuliert
- Es verpflichtet dich auf eine Hypothese, mit der du sichtbar falschliegen kannst, was dich ehrlich hält
- Es macht *deine* Annahmen sichtbar, und genau das soll das Interview offenlegen

Das Risiko dabei ist ein höflicher Nutzer, der deiner Vermutung zustimmt, um verträglich zu sein. Begegne dem, indem du sichtbar bereit bist, falschzuliegen, und gelegentlich in eine Richtung rätst, bei der du Widerspruch erwartest.

### Step 3: Achte auf „wollen vs. wollen sollen“

Die gefährlichsten Antworten sind die, in denen der Nutzer sagt, wie eine durchdachte Antwort *klingt*, statt was er tatsächlich will. Achte auf:

- Antworten, die Best-Practice-Floskeln bedienen („es soll skalierbar sein“, „saubere Architektur“), ohne Konkretes
- Antworten, die sich auf Konventionen berufen („so wie die meisten Apps es machen“, „der Standardansatz“)
- Formulierungen wie „Ich sollte wahrscheinlich …“, „Ich soll vermutlich …“, „gute Engineering-Praxis sagt …“
- Buzzwords als Ziele, wenn „modern“, „skalierbar“, „robust“ die Antwort sind statt eines konkreten Ergebnisses

Wenn du das hörst, lautet die Frage:

> *„Wenn du das vor niemandem rechtfertigen müsstest, was würdest du dann tatsächlich wollen?“*

Diese eine Frage leistet oft mehr als die fünf davor.

### Step 4: Gib die Absicht in den Worten des Nutzers wieder

Wenn deine Sicherheit hoch ist, schreibe zurück, was du jetzt für den Wunsch des Nutzers hältst. Halte es knapp (5–8 Zeilen), nutze möglichst seine Sprache und strukturiere es so, dass der Nutzer Zeile für Zeile bestätigen oder korrigieren kann:

```
Here's what I now think you want:

- Outcome:      <one line>
- User:         <one line — who benefits>
- Why now:      <one line — what changed>
- Success:      <one line — how we know it worked>
- Constraint:   <one line — the binding limit>
- Out of scope: <one line — what we're explicitly not doing>

Yes / no / refine?
```

„Out of scope“ aufzunehmen ist nicht verhandelbar. Die Hälfte aller Fehlabstimmungen ist stiller Dissens darüber, was *nicht* gebaut wird.

### Step 5: Bestätigen — ein ausdrückliches Ja, nicht „was du für richtig hältst“

Das Gate ist ein ausdrückliches „Ja“. Folgendes ist **kein** Ja:

- „Was du für am besten hältst.“ → Der Nutzer delegiert, also hat auch er keine 95 % Sicherheit. Frage erneut mit zwei konkreten Optionen, formuliert als Entscheidung.
- „Klingt gut.“ → Mehrdeutig. Frage: „Gibt es etwas, das du schärfen würdest?“ Schweigen ist keine Bestätigung.
- „Klar, legen wir los.“ → Oft ein höflicher Ausstieg, keine Zustimmung. Gleiche Nachfrage.
- Schweigen, gefolgt von „okay, fangen wir an“. → Der Nutzer hat das Interview aufgegeben, nicht zu einem Ergebnis gefunden. Halte an und frage, ob dir etwas entgangen ist.

Korrigiert er dich, arbeite die Korrektur ein und gib die Absicht erneut wieder. Wiederhole das, bis du ein ausdrückliches Ja bekommst.

### Step 6: Terminal Turn & Stop Rule (CRITICAL)

Wenn der Nutzer die Absichtserklärung mit einem ausdrücklichen „Ja“ bestätigt:

1. **Liefere die bestätigte Absichtserklärung (Statement of Intent).**
2. **Biete nachgelagerte Wege an** (biete an, sie in `docs/intent/[topic].md` zu speichern, mit `spec-driven-development` eine Spec zu entwerfen oder nach der Spec zur Aufgabenplanung überzugehen).
3. **BEENDE DEINEN ZUG SOFORT.** Rufe in diesem Zug KEINE Tools auf und beginne KEINE nachgelagerte Arbeit. Gib die Kontrolle an den Nutzer zurück, damit er den nächsten Schritt wählt.

### The 95% Confidence Stop

Du bist fertig, wenn du dies mit Ja beantworten kannst:

> *Kann ich die Reaktion des Nutzers auf die nächsten drei Fragen vorhersagen, die ich stellen würde?*

Wenn ja, besteht ein gemeinsames Verständnis. Beende das Interview und erstelle die Wiedergabe. Wenn nein, bist du nicht fertig; stelle die nächste Frage.

Das ist ein überprüfbarer Test, kein Bauchgefühl. Er hat auch eine Untergrenze: Wenn du mehrere Runden hinter dir hast und immer noch nichts vorhersagen kannst, ist das eine Information über die Anfrage, kein Grund, sich weiter abzumühen. Halte an und sage dem Nutzer: „Ich habe X Fragen gestellt und kann deine Reaktionen immer noch nicht vorhersagen. Etwas Grundlegendes fehlt. Wollen wir einen Schritt zurücktreten?“

## Output

Das Ergebnis dieses Skills ist eine **bestätigte Absichtserklärung**: die Wiedergabe aus Step 4, mit einem ausdrücklichen Ja aus Step 5. Das ist das Deliverable. Specs, Pläne und Aufgabenlisten sind nachgelagert; sie verbrauchen die Absicht, die dieser Skill liefert.

Soll die Absicht erhalten bleiben (mehrere Sessions, Übergabe an einen anderen Mitarbeiter), biete an, sie in `docs/intent/[topic].md` zu speichern. Speichere nur, wenn der Nutzer zustimmt.

## Example

Ein kurzes Vorher-Nachher.

**Ohne `interview-me`:**

```
User:  build me a dashboard for our metrics
Agent: <starts proposing chart libraries and layouts>
```

Der Agent hat angenommen: für wen es ist, welche Metriken, was „für unser Team“ bedeutet, wie Erfolg aussieht. Nichts davon wurde gesagt. Jede Annahme ist eine Stelle, an der der Nutzer später sagen kann: „Das habe ich nicht gemeint.“

**Mit `interview-me`:**

```
User: build me a dashboard for our metrics

Agent:
HYPOTHESIS: You want a way to answer "how are we doing?" in standup, and "dashboard" came to mind because that's the conventional answer.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" are, and what success looks like

Q:     When you say "how are we doing?", who's asking — you alone, the engineering team in standup, or up the chain (e.g., your manager, an exec, a board)?
GUESS: engineering team in standup, because "we" usually scopes that way and standups are where this question gets asked. If it's for execs the metrics and the framing change a lot.

User: It's actually for me. I keep losing track of which experiments are running and what their early signal looks like.

Agent:
Updated read: not a team dashboard at all. It's a personal experiment tracker. Confidence: ~60% — still missing: what "early signal" means and what done looks like.

Q:     Is the gap that you don't know which experiments exist, or that you can't see their results in one place?
GUESS: the second one. You have a list of experiments somewhere, but their results live in five different tools, and reconciling them by hand is what you're tired of.

User: First one actually. I literally don't have a list. They're spread across different docs.

Agent: <continues>
```

Nach zwei Fragen hat der Agent entdeckt, dass die eigentliche Anfrage nicht „ein Dashboard“ lautet, sondern „eine Liste“. Anderes Artefakt, anderer Umfang, andere Arbeit. Das Dashboard wäre falsch gewesen.

## Interaction with Other Skills

- **`idea-refine`**: nachgelagert. Lautet die bestätigte Absicht „Ich will X, weiß aber nicht, wie ich es zuschneiden soll“, übergib an `idea-refine`, um Varianten gegen die nun explizite Absicht zu erzeugen.
- **`spec-driven-development`**: nachgelagert. Ist die bestätigte Absicht konkret („Ich will X für Y Nutzer mit Z als Erfolgskriterien“), übergib an `spec-driven-development`, um sie aufzuschreiben.
- **`planning-and-task-breakdown`**: zwei Schritte nachgelagert zu diesem Skill (nach der Spec).
- **`doubt-driven-development`**: das andere Ende der Zeitleiste. Interview-me ist Absichtsermittlung vor der Entscheidung; doubt-driven ist Artefakt-Review nach der Entscheidung. Beide fangen Abweichungen ab, aber zu unterschiedlichen Zeitpunkten.
- **`source-driven-development`**: orthogonal. Interview-me klärt, was der Nutzer will; SDD verifiziert Framework-Fakten. Sie konkurrieren nicht.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| „Die Anfrage ist klar genug“ | Wenn du das gewünschte Ergebnis des Nutzers nicht jetzt in einem Satz aufschreiben kannst, ist die Anfrage nicht klar. Führe Step 1 aus, bevor du entscheidest. |
| „Zu viele Fragen verschwenden seine Zeit“ | Die Zeit für 4–6 gezielte Fragen ist gering. Die Zeit für das Bauen des Falschen ist enorm, und der Nutzer trägt diese Kosten. |
| „Ich finde es beim Bauen heraus“ | Wechselkosten nach der Existenz von Code sind das 10-Fache von heute. Erkenntnisse während der Implementierung sind Nacharbeit. |
| „Er hat ‚was du für richtig hältst‘ gesagt, also entscheide ich einfach“ | „Was du für richtig hältst“ ist Delegation, keine Entscheidung. Frage erneut mit zwei konkreten Optionen als Wahl. |
| „Ich sollte ihm mehrere Optionen zur Auswahl geben“ | Optionen funktionieren, wenn der Nutzer weiß, was er will, und zwischen Trade-offs wählt. Er weiß noch nicht, was er will. Optionen aufzulisten weitet die Suche; Fragen engt sie ein. |
| „Wenn ich meine Vermutung anhänge, steuere ich ihn“ | Steuern ist der Sinn. Reagieren ist schneller als von Grund auf zu formulieren. Das Risiko ist Anbiederung, nicht Steuerung; begegne ihm, indem du sichtbar bereit bist, falschzuliegen. |
| „Wir haben genug geredet, ich verstehe es“ | Teste es: Kannst du seine Reaktion auf die nächsten drei Fragen vorhersagen? Wenn nicht, verstehst du es noch nicht. |
| „Der Nutzer hat Ja gesagt, wir sind fertig“ | Folgte das Ja auf eine vage Wiedergabe oder ein offenes „klingt gut“, ist das Ja hohl. Gib konkret wieder und bestätige erneut. |

## Red Flags

- Drei oder mehr Fragen in einer einzigen Nachricht: das ist Stapeln, kein Interview
- Eine Frage ohne angehängte Hypothese: das ist Befragung, kein Festlegen
- „Was du für am besten hältst“ als endgültige Antwort akzeptieren
- Eine Spec, einen Plan oder eine Aufgabenliste erstellen, bevor der Nutzer deine Wiedergabe ausdrücklich bestätigt hat
- Tools aufrufen oder nachgelagerte Arbeit beginnen, sobald die Absicht bestätigt ist, statt den Zug zu beenden
- Fragen der Form „Was wäre Best Practice?“ statt „Was willst du tatsächlich?“
- Der Nutzer gibt eine Antwort, die Sophistication signalisiert („skalierbar“, „sauber“, „modern“), und du akzeptierst sie, ohne nachzuhaken, ob es das ist, was er wirklich will
- Drei oder mehr Runden, ohne dass deine Sicherheit sichtbar steigt: du stellst die falschen Fragen, tritt einen Schritt zurück und formuliere neu
- Eine Sicherheitszahl unter ca. 70 % ohne Begründung: der Nutzer kann die Lücke nicht schließen helfen, wenn er nicht weiß, was fehlt
- Das Intent-Dokument speichern, bevor der Nutzer bestätigt hat (das Dokument selbst unterstellt ein Ja, das der Nutzer nicht gegeben hat)
- Die Zeile „Out of scope“ in der Wiedergabe auslassen (stiller Dissens über Nicht-Ziele ist die Hälfte aller Fehlabstimmungen)

## Verification

Nach der Anwendung von interview-me:

- [ ] Im ersten Zug wurde eine explizite Hypothese mit Sicherheitszahl genannt
- [ ] Jede Sicherheitszahl unter ca. 70 % wurde von einer einzeiligen Begründung begleitet (was noch ungeklärt ist oder fehlt)
- [ ] Fragen wurden einzeln gestellt, jeweils mit der Vermutung des Agents
- [ ] Mindestens eine „Was würdest du tatsächlich wollen, wenn du es nicht rechtfertigen müsstest?“-Nachfrage lief, wenn der Nutzer eine Sophistication- oder Konventions-signalisierende Antwort gab
- [ ] Eine konkrete Wiedergabe (Outcome / User / Why now / Success / Constraint / Out of scope) wurde dem Nutzer zurückgespielt
- [ ] Der Nutzer hat die Wiedergabe mit einem ausdrücklichen Ja bestätigt (nicht „was du für richtig hältst“, nicht „klingt gut“, nicht Schweigen)
- [ ] Am Stopp-Punkt konnte der Agent die Reaktionen auf die nächsten drei Fragen vorhersagen, die er gestellt hätte
- [ ] Nach der ausdrücklichen Bestätigung wurde der Zug sofort beendet, ohne Tools aufzurufen oder nachgelagerte Arbeit zu beginnen
- [ ] Jede Übergabe an einen nachgelagerten Skill (`idea-refine`, `spec-driven-development`) wurde anhand der bestätigten Absicht formuliert, nicht anhand der ursprünglichen unterspezifizierten Anfrage
