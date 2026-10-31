---
name: code-review-and-quality
description: "Fünf-Achsen-Code-Review aus agent-skills (Korrektheit, Lesbarkeit, Architektur, Sicherheit, Performance). Nur verwenden, wenn der Nutzer /agent-skills-de:review aufruft oder diesen Skill ausdrücklich nennt. Für Reviews im Alltag gilt der Skill code-review."
---

# Code-Review und Qualität

## Überblick

Mehrdimensionales Code-Review mit Quality Gates. Jede Änderung wird vor dem Merge geprüft – keine Ausnahmen. Das Review deckt fünf Achsen ab: Korrektheit, Lesbarkeit, Architektur, Security und Performance.

**Der Freigabemaßstab:** Gib eine Änderung frei, wenn sie die Gesamtqualität des Codes eindeutig verbessert, auch wenn sie nicht perfekt ist. Perfekten Code gibt es nicht – das Ziel ist kontinuierliche Verbesserung. Blockiere eine Änderung nicht, nur weil sie nicht genau so geschrieben ist, wie du sie geschrieben hättest. Wenn sie die Codebasis verbessert und den Konventionen des Projekts folgt, gib sie frei.

## Wann verwenden

- Vor dem Merge jedes PR oder jeder Änderung
- Nach Abschluss einer Feature-Implementierung
- Wenn ein anderer Agent oder ein anderes Modell Code erzeugt hat, den du bewerten musst
- Beim Refaktorieren von bestehendem Code
- Nach jedem Bugfix (prüfe sowohl den Fix als auch den Regressionstest)

## Das Fünf-Achsen-Review

Jedes Review bewertet den Code anhand dieser Dimensionen:

### 1. Korrektheit

Tut der Code, was er vorgibt zu tun?

- Entspricht er der Spec bzw. den Anforderungen der Aufgabe?
- Sind Grenzfälle behandelt (null, leer, Grenzwerte)?
- Sind Fehlerpfade behandelt (nicht nur der Happy Path)?
- Bestehen alle Tests? Testen die Tests tatsächlich das Richtige?
- Gibt es Off-by-one-Fehler, Race Conditions oder Zustandsinkonsistenzen?

### 2. Lesbarkeit & Einfachheit

Kann ein anderer Engineer (oder Agent) diesen Code verstehen, ohne dass der Autor ihn erklärt?

- Sind Namen aussagekräftig und konsistent mit den Projektkonventionen? (Kein `temp`, `data`, `result` ohne Kontext)
- Ist der Kontrollfluss geradlinig (verschachtelte Ternaries und tiefe Callbacks vermeiden)?
- Ist der Code logisch organisiert (zusammengehöriger Code gruppiert, klare Modulgrenzen)?
- Gibt es „clevere“ Tricks, die vereinfacht werden sollten?
- **Ginge das in weniger Zeilen?** (1000 Zeilen, wo 100 genügen, sind ein Versagen)
- **Rechtfertigen die Abstraktionen ihre Komplexität?** (Verallgemeinere nicht vor dem dritten Anwendungsfall)
- Würden Kommentare helfen, nicht offensichtliche Absichten zu klären? (Kommentiere aber keinen offensichtlichen Code.)
- Gibt es Überreste von totem Code: No-op-Variablen (`_unused`), Abwärtskompatibilitäts-Shims oder `// removed`-Kommentare?
- **Wird eine neue Bedingung an einen unzusammenhängenden Ablauf angeflanscht?** Das ist ein Design-Smell, kein Nit – verlagere die Logik in einen eigenen Helper, Zustand oder eine eigene Policy, statt einen bestehenden Pfad zu verwirren.
- **Tauchen wiederholte Bedingungen auf derselben Struktur auf?** Sie deuten auf ein fehlendes Modell oder einen fehlenden Dispatcher hin. Ein „temporärer“ Zweig ist meist dauerhafte Schuld.

### 3. Architektur

Passt die Änderung zum Design des Systems?

- Folgt sie bestehenden Mustern oder führt sie ein neues ein? Falls neu: Ist das begründet?
- Bleiben saubere Modulgrenzen erhalten?
- Gibt es Code-Duplikation, die geteilt werden sollte?
- Fließen Abhängigkeiten in die richtige Richtung (keine zirkulären Abhängigkeiten)?
- Ist das Abstraktionsniveau angemessen (nicht überengineered, nicht zu stark gekoppelt)?
- **Reduziert dieses Refactoring die Komplexität oder verlagert es sie nur?** Zähle die Konzepte, die ein Leser im Kopf behalten muss, um der Änderung zu folgen. Bleibt diese Zahl bei einer „saubereren“ Version gleich, ist sie nicht sauberer – bevorzuge die Umstrukturierung, die ganze Zweige, Modi oder Schichten verschwinden lässt, gegenüber einer, die dieselbe Logik nur neu zentralisiert. Lösche lieber eine Abstraktion, als sie zu polieren.
- **Sickert featurespezifische Logik in ein geteiltes oder allgemeines Modul?** Halte Logik in der Schicht, der sie gehört, verwende den bestehenden kanonischen Helper statt eines Beinahe-Duplikats und normalisiere keine architektonische Drift.
- **Sind Typgrenzen explizit?** Hinterfrage unnötiges `any`/`unknown`/Optional/Casts und stille Fallbacks, die eine unklare Invariante übertünchen – eine explizite Grenze vereinfacht oft den umgebenden Kontrollfluss.

### 4. Security

Detaillierte Security-Hinweise findest du in `security-and-hardening`. Führt die Änderung Schwachstellen ein?

- Werden Nutzereingaben validiert und bereinigt?
- Bleiben Secrets aus Code, Logs und Versionskontrolle heraus?
- Werden Authentifizierung/Autorisierung dort geprüft, wo nötig?
- Sind SQL-Abfragen parametrisiert (keine String-Konkatenation)?
- Werden Ausgaben kodiert, um XSS zu verhindern?
- Stammen Abhängigkeiten aus vertrauenswürdigen Quellen und haben keine bekannten Schwachstellen?
- Werden Daten aus externen Quellen (APIs, Logs, Nutzerinhalte, Konfigurationsdateien) als nicht vertrauenswürdig behandelt?
- Werden externe Datenflüsse an Systemgrenzen validiert, bevor sie in Logik oder Rendering verwendet werden?

### 5. Performance

Detailliertes Profiling und Optimierung findest du in `performance-optimization`. Führt die Änderung Performance-Probleme ein?

- Gibt es N+1-Query-Muster?
- Gibt es unbegrenzte Schleifen oder unbeschränktes Laden von Daten?
- Gibt es synchrone Operationen, die asynchron sein sollten?
- Gibt es unnötige Re-Renders in UI-Komponenten?
- Fehlt Pagination bei Listen-Endpunkten?
- Werden große Objekte in Hot Paths erzeugt?

## Strukturelle Abhilfen

Wenn du ein strukturelles Problem markierst, schlage den Umbau vor – nicht nur das Problem. Ein Review, das nur sagt „das ist komplex“, lässt den Autor im Ungewissen. Greife zu einer benannten Umstrukturierung:

- **Ersetze eine Kette von Bedingungen** durch ein typisiertes Modell oder einen expliziten Dispatcher.
- **Fasse doppelte Zweige** zu einem einzigen, klareren Ablauf zusammen.
- **Trenne Orchestrierung von Geschäftslogik**, sodass sich beide für sich lesen lassen.
- **Verschiebe featurespezifische Logik** aus einem geteilten Modul in das Paket, dem das Konzept gehört.
- **Verwende den kanonischen Helper** statt eines maßgeschneiderten Beinahe-Duplikats.
- **Mache eine Typgrenze explizit**, damit nachgelagerte Verzweigungen entfallen.
- **Lösche einen Pass-through-Wrapper**, der Indirektion hinzufügt, ohne die API zu klären.
- **Extrahiere einen Helper oder teile eine große Datei** in fokussierte Module auf.

Bevorzuge die Abhilfe, die bewegliche Teile entfernt, gegenüber einer, die dieselbe Komplexität nur verteilt.

## Änderungsgröße

Kleine, fokussierte Änderungen sind leichter zu prüfen, schneller zu mergen und sicherer auszurollen. Ziele für die Größen:

```
~100 lines changed   → Good. Reviewable in one sitting.
~300 lines changed   → Acceptable if it's a single logical change.
~1000 lines changed  → Too large. Split it.
```

**Achte auf die Dateigröße, nicht nur auf die Diff-Größe.** Ein kleiner Diff kann eine Datei dennoch über eine gesunde Grenze schieben – rund 1000 *Gesamt*zeilen in einer einzelnen Datei (nicht zu verwechseln mit der Schwelle von ~1000 *geänderten* Zeilen oben) sind ein gängiges Prüfsignal, keine harte Obergrenze. Wenn eine Änderung eine ohnehin große Datei spürbar vergrößert, frage dich, ob du *zuerst* Helper, Teilkomponenten oder Module extrahieren solltest, bevor du noch mehr daraufpackst. Erst zerlegen, dann hinzufügen.

**Was als „eine Änderung“ zählt:** Eine einzelne, in sich geschlossene Modifikation, die eine Sache adressiert, zugehörige Tests enthält und das System nach dem Einreichen funktionsfähig hält. Ein Teil eines Features – nicht das ganze Feature.

**Strategien zum Aufteilen, wenn eine Änderung zu groß ist:**

| Strategie | Vorgehen | Wann |
|----------|-----|------|
| **Stack** | Eine kleine Änderung einreichen, die nächste darauf aufbauend beginnen | Sequenzielle Abhängigkeiten |
| **Nach Dateigruppe** | Getrennte Änderungen für Gruppen, die unterschiedliche Reviewer brauchen | Querschnittsthemen |
| **Horizontal** | Zuerst geteilten Code/Stubs erstellen, dann die Konsumenten | Geschichtete Architektur |
| **Vertikal** | In kleinere Full-Stack-Scheiben des Features aufteilen | Feature-Arbeit |

**Wann große Änderungen akzeptabel sind:** Vollständige Dateilöschungen und automatisiertes Refaktorieren, bei denen der Reviewer nur die Absicht prüfen muss, nicht jede Zeile.

**Trenne Refaktorieren von Feature-Arbeit.** Eine Änderung, die bestehenden Code refaktoriert und neues Verhalten hinzufügt, sind zwei Änderungen – reiche sie getrennt ein. Kleine Aufräumarbeiten (Variablen umbenennen) können nach Ermessen des Reviewers enthalten sein.

## Änderungsbeschreibungen

Jede Änderung braucht eine Beschreibung, die in der Versionsverwaltungshistorie für sich allein steht.

**Erste Zeile:** Kurz, im Imperativ, eigenständig. „Delete the FizzBuzz RPC“ statt „Deleting the FizzBuzz RPC.“ Sie muss aussagekräftig genug sein, dass jemand, der die Historie durchsucht, die Änderung versteht, ohne den Diff zu lesen.

**Body:** Was sich ändert und warum. Nimm Kontext, Entscheidungen und Begründungen auf, die im Code selbst nicht sichtbar sind. Verlinke Bug-Nummern, Benchmark-Ergebnisse oder Design-Dokumente, wo relevant. Benenne Schwächen des Ansatzes, wenn es sie gibt.

**Anti-Patterns:** „Fix bug“, „Fix build“, „Add patch“, „Moving code from A to B“, „Phase 1“, „Add convenience functions“.

## Review-Ablauf

### Schritt 1: Den Kontext verstehen

Verstehe die Absicht, bevor du den Code ansiehst:

```
- What is this change trying to accomplish?
- What spec or task does it implement?
- What is the expected behavior change?
```

### Schritt 2: Zuerst die Tests prüfen

Tests offenbaren Absicht und Abdeckung:

```
- Do tests exist for the change?
- Do they test behavior (not implementation details)?
- Are edge cases covered?
- Do tests have descriptive names?
- Would the tests catch a regression if the code changed?
```

Beantworte die letzte Frage per Experiment, nicht durch Lesen. Invertiere eine Bedingung, die die Änderung hinzufügt (Negation weglassen, `&&` gegen `||` tauschen), führe die Suite aus und stelle die Datei danach aus einer Kopie wieder her. Eine Mutation, die grün bleibt, ist ein Befund: Benenne den fehlenden Testfall. Für einen projektweiten Mutation Score siehe `constraint-driven-development`.

### Schritt 3: Die Implementierung prüfen

Gehe den Code mit den fünf Achsen im Kopf durch:

```
For each file changed:
1. Correctness: Does this code do what the test says it should?
2. Readability: Can I understand this without help?
3. Architecture: Does this fit the system?
4. Security: Any vulnerabilities?
5. Performance: Any bottlenecks?
```

### Schritt 4: Befunde kategorisieren

Versieh jeden Kommentar mit seinem Schweregrad, damit der Autor weiß, was verpflichtend und was optional ist:

| Präfix | Bedeutung | Aktion des Autors |
|--------|---------|---------------|
| *(kein Präfix)* | Erforderliche Änderung | Muss vor dem Merge behoben werden |
| **Critical:** | Blockiert den Merge | Sicherheitslücke, Datenverlust, defekte Funktionalität |
| **Nit:** | Geringfügig, optional | Autor darf ignorieren – Formatierung, Stilvorlieben |
| **Optional:** / **Consider:** | Vorschlag | Erwägenswert, aber nicht erforderlich |
| **FYI** | Nur zur Information | Keine Aktion nötig – Kontext für später |

So behandeln Autoren nicht jedes Feedback als verpflichtend und verschwenden keine Zeit mit optionalen Vorschlägen.

**Beginne mit dem, was zählt.** Ordne die Befunde nach Hebelwirkung: zuerst Korrektheit und Security, dann strukturelle Regressionen und verpasste Vereinfachungen, dann alles andere. Begrabe ein echtes Problem nicht unter kosmetischen Nits – wenige Kommentare mit hoher Überzeugung schlagen eine lange Liste. Wenn du ein strukturelles Problem und zehn Nits hast, *ist* das strukturelle Problem das Review.

### Schritt 5: Die Verifikation verifizieren

Prüfe die Verifikationsgeschichte des Autors:

```
- What tests were run?
- Did the build pass?
- Was the change tested manually?
- Are there screenshots for UI changes?
- Is there a before/after comparison?
```

## Multi-Modell-Review-Muster

Nutze unterschiedliche Modelle für unterschiedliche Review-Perspektiven:

```
Model A writes the code
    │
    ▼
Model B reviews for correctness and architecture
    │
    ▼
Model A addresses the feedback
    │
    ▼
Human makes the final call
```

So werden Probleme gefunden, die einem einzelnen Modell entgehen könnten – verschiedene Modelle haben unterschiedliche blinde Flecken.

**Beispiel-Prompt für einen Review-Agenten:**
```
Review this code change for correctness, security, and adherence to
our project conventions. The spec says [X]. The change should [Y].
Flag any issues as Critical, Required, Optional, or Nit.
```

## Hygiene bei totem Code

Prüfe nach jedem Refaktorieren oder jeder Implementierungsänderung auf verwaisten Code:

1. Identifiziere Code, der jetzt unerreichbar oder ungenutzt ist
2. Liste ihn explizit auf
3. **Frage vor dem Löschen:** „Soll ich diese jetzt ungenutzten Elemente entfernen: [Liste]?“

Lass keinen toten Code herumliegen – er verwirrt künftige Leser und Agenten. Lösche aber nichts stillschweigend, bei dem du dir nicht sicher bist. Im Zweifel frage nach.

```
DEAD CODE IDENTIFIED:
- formatLegacyDate() in src/utils/date.ts — replaced by formatDate()
- OldTaskCard component in src/components/ — replaced by TaskCard
- LEGACY_API_URL constant in src/config.ts — no remaining references
→ Safe to remove these?
```

## Review-Geschwindigkeit

Langsame Reviews blockieren ganze Teams. Die Kosten des Kontextwechsels für ein Review sind geringer als die Wartekosten, die anderen entstehen.

- **Antworte innerhalb eines Werktags** – das ist das Maximum, nicht das Ziel
- **Idealer Rhythmus:** Antworte kurz nach Eingang einer Review-Anfrage, außer du steckst tief in konzentrierter Programmierarbeit. Eine typische Änderung sollte mehrere Review-Runden an einem Tag abschließen
- **Priorisiere schnelle Einzelantworten** vor schneller finaler Freigabe. Schnelles Feedback verringert Frust, auch wenn mehrere Runden nötig sind
- **Große Änderungen:** Bitte den Autor, sie aufzuteilen, statt einen riesigen Changeset zu prüfen

## Umgang mit Meinungsverschiedenheiten

Wende bei der Klärung von Review-Streitfragen diese Hierarchie an:

1. **Technische Fakten und Daten** haben Vorrang vor Meinungen und Vorlieben
2. **Style Guides** sind die absolute Autorität in Stilfragen
3. **Software-Design** muss nach Engineering-Prinzipien bewertet werden, nicht nach persönlicher Vorliebe
4. **Konsistenz der Codebasis** ist akzeptabel, wenn sie die Gesamtqualität nicht verschlechtert

**Akzeptiere kein „Ich räume das später auf.“** Die Erfahrung zeigt, dass aufgeschobenes Aufräumen selten passiert. Verlange das Aufräumen vor dem Einreichen, außer es handelt sich um einen echten Notfall. Wenn umliegende Probleme in dieser Änderung nicht behoben werden können, verlange, dass ein Bug angelegt und sich selbst zugewiesen wird.

## Ehrlichkeit im Review

Beim Review von Code – egal ob von dir, einem anderen Agenten oder einem Menschen geschrieben:

- **Stempel nicht ab.** „LGTM“ ohne Nachweis eines Reviews hilft niemandem.
- **Schwäche echte Probleme nicht ab.** „Das könnte ein kleines Problem sein“, wenn es ein Bug ist, der in Produktion auftreten wird, ist unehrlich.
- **Beziffere Probleme, wenn möglich.** „Diese N+1-Query fügt pro Listeneintrag ~50 ms hinzu“ ist besser als „das könnte langsam sein“.
- **Widersprich Ansätzen mit klaren Problemen.** Anbiederung ist ein Fehlermodus in Reviews. Hat die Implementierung Probleme, sag es direkt und schlage Alternativen vor.
- **Akzeptiere ein Überstimmen mit Anstand.** Wenn der Autor den vollen Kontext hat und anderer Meinung ist, folge seinem Urteil. Kommentiere den Code, nicht die Person – formuliere persönliche Kritik so um, dass sie sich auf den Code bezieht.

## Disziplin bei Abhängigkeiten

Zum Code-Review gehört auch das Review von Abhängigkeiten:

**Bevor du eine Abhängigkeit hinzufügst:**
1. Löst der bestehende Stack das Problem? (Oft ist das der Fall.)
2. Wie groß ist die Abhängigkeit? (Prüfe den Bundle-Einfluss.)
3. Wird sie aktiv gepflegt? (Prüfe letzten Commit, offene Issues.)
4. Hat sie bekannte Schwachstellen? (`npm audit`)
5. Welche Lizenz hat sie? (Muss mit dem Projekt kompatibel sein.)

**Regel:** Bevorzuge die Standardbibliothek und bestehende Utilities gegenüber neuen Abhängigkeiten. Jede Abhängigkeit ist eine Belastung.

**Das Upgrade einer bestehenden Abhängigkeit** ist eine Codeänderung wie jede andere, und die riskantesten Upgrades sind die, die gebündelt mit einer Nachricht wie „bump deps“ gemergt werden. Prüfe sie mit derselben Disziplin:

1. **Lies das Changelog, nicht nur die Versionsnummer.** Semver ist ein Versprechen, das der Maintainer vielleicht nicht gehalten hat – ein „Patch“ kann eine Verhaltensänderung enthalten. Lies bei einem Major-Bump die Migrationshinweise und finde heraus, was bricht.
2. **Eine Abhängigkeit pro Änderung.** Aktualisiere und merge sie einzeln (oder in kleinen zusammengehörigen Gruppen). Bricht ein gebündelter Bump den Build, weißt du nicht mehr, welches Paket es war; eine Änderung mit einem einzelnen Paket macht die Ursache offensichtlich und den Revert sauber.
3. **Lass die Tests entscheiden.** Das Upgrade wird durch eine grüne Suite *vor* und *nach* dem Update verifiziert, nicht dadurch, dass „es installiert wurde“. Ist die Abdeckung des Verhaltens der Abhängigkeit dünn, ist diese Lücke der eigentliche Befund – schreibe zuerst einen Test.
4. **Beachte den transitiven Graphen.** Die meisten installierten Pakete hat niemand direkt gewählt. Prüfe den Lockfile-Diff, nicht nur `package.json`; ein einzelner direkter Bump kann Dutzende indirekter Änderungen nach sich ziehen.
5. **Halte das Lockfile ehrlich.** Committe es, prüfe seinen Diff und bearbeite es nie von Hand. Das Lockfile legt tatsächlich fest, was ausgeliefert wird.

Für die Triage von `npm audit`-Befunden und Supply-Chain-Risiken (Typosquatting, kompromittierte Maintainer) folge dem Skill `security-and-hardening` – dieser Abschnitt behandelt den *Workflow* des Upgrades, jener das Security-Urteil.

## Die Review-Checkliste

```markdown
## Review: [PR/Change title]

### Context
- [ ] I understand what this change does and why

### Correctness
- [ ] Change matches spec/task requirements
- [ ] Edge cases handled
- [ ] Error paths handled
- [ ] Tests cover the change adequately

### Readability
- [ ] Names are clear and consistent
- [ ] Logic is straightforward
- [ ] No unnecessary complexity

### Architecture
- [ ] Follows existing patterns
- [ ] No unnecessary coupling or dependencies
- [ ] Appropriate abstraction level
- [ ] Refactors reduce complexity rather than relocate it
- [ ] No feature logic in shared modules; file stays within a healthy size

### Security
- [ ] No secrets in code
- [ ] Input validated at boundaries
- [ ] No injection vulnerabilities
- [ ] Auth checks in place
- [ ] External data sources treated as untrusted

### Performance
- [ ] No N+1 patterns
- [ ] No unbounded operations
- [ ] Pagination on list endpoints

### Verification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] Manual verification done (if applicable)

### Verdict
- [ ] **Approve** — Ready to merge
- [ ] **Request changes** — Issues must be addressed
```
## Siehe auch

- Für detaillierte Hinweise zum Security-Review siehe `../../references/security-checklist.md`
- Für Performance-Prüfpunkte im Review siehe `../../references/performance-checklist.md`

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Es funktioniert, das reicht“ | Funktionierender Code, der unlesbar, unsicher oder architektonisch falsch ist, erzeugt Schulden, die sich aufsummieren. |
| „Ich habe es geschrieben, also weiß ich, dass es korrekt ist“ | Autoren sind blind für ihre eigenen Annahmen. Jede Änderung profitiert von einem zweiten Paar Augen. |
| „Wir räumen das später auf“ | Später kommt nie. Das Review ist das Quality Gate – nutze es. Verlange das Aufräumen vor dem Merge, nicht danach. |
| „KI-generierter Code ist wahrscheinlich in Ordnung“ | KI-Code braucht mehr Prüfung, nicht weniger. Er wirkt selbstsicher und plausibel, auch wenn er falsch ist. |
| „Die Tests laufen durch, also ist es gut“ | Tests sind notwendig, aber nicht hinreichend. Sie fangen keine Architekturprobleme, Security-Probleme oder Lesbarkeitsmängel ab. |
| „Das Refactoring macht es sauberer“ | Komplexität zu verlagern heißt nicht, sie zu reduzieren. Muss der Leser noch dieselbe Zahl an Konzepten im Kopf behalten, hat sich die Struktur nicht verbessert – suche die Version, in der Zweige verschwinden. |
| „Es ist nur eine kleine Ergänzung in dieser Datei“ | Auch kleine Diffs schieben Dateien über eine gesunde Größe und flanschen Zweige an unzusammenhängende Abläufe an. Beurteile die resultierende Struktur, nicht die Diff-Größe. |
| „Es ist nur ein Versions-Bump“ | Ein Bump ist eine Verhaltensänderung, die du nicht geschrieben hast. Lies das Changelog; Semver garantiert keine Bruchfreiheit. |
| „Ich aktualisiere alles in einem PR, um Zeit zu sparen“ | Ein gebündelter Bump, der den Build bricht, verbirgt, welches Paket es war. Eine Abhängigkeit pro Änderung hält Ursache und Revert sauber. |

## Warnsignale

- PRs, die ganz ohne Review gemergt werden
- Review, das nur prüft, ob die Tests durchlaufen (und die anderen Achsen ignoriert)
- „LGTM“ ohne Nachweis eines tatsächlichen Reviews
- Sicherheitsrelevante Änderungen ohne sicherheitsfokussiertes Review
- Große PRs, die „zu groß für ein ordentliches Review“ sind (aufteilen)
- Keine Regressionstests bei Bugfix-PRs
- Review-Kommentare ohne Schweregrad-Labels – unklar, was erforderlich und was optional ist
- „Ich fixe es später“ zu akzeptieren – es passiert nie
- Ein Refactoring, das Code verschiebt, ohne die Zahl der Konzepte zu verringern, die ein Leser im Kopf behalten muss
- Eine Änderung, die eine ohnehin große Datei vergrößert, statt sie zu zerlegen
- Neue Bedingungen, die in unzusammenhängende Codepfade gestreut werden (eine fehlende Abstraktion)
- Ein maßgeschneiderter Helper, der einen bestehenden kanonischen dupliziert, oder featurespezifische Logik in einem geteilten Modul
- Ein gebündelter PR „Abhängigkeiten aktualisieren“ ohne Changelog-Review und ohne Isolierung pro Paket
- Eine Lockfile-Änderung, die von Hand bearbeitet, nicht committet oder ohne Prüfung ihres Diffs gemergt wurde

## Verifikation

Nach Abschluss des Reviews:

- [ ] Alle Critical-Issues sind behoben
- [ ] Alle Required-Änderungen (ohne Präfix) sind behoben oder mit Begründung ausdrücklich zurückgestellt
- [ ] Tests bestehen
- [ ] Build ist erfolgreich
- [ ] Die Verifikationsgeschichte ist dokumentiert (was sich geändert hat, wie es verifiziert wurde)
- [ ] Abhängigkeits-Upgrades wurden gegen ihr Changelog geprüft, pro Paket isoliert und durch eine grüne Suite verifiziert, wobei der Lockfile-Diff geprüft wurde

**Vermutliche Blocker:** Benenne jeweils das Problem und schlage das einfachere Design vor; eskaliere nur dann zu Required, wenn die Änderung die Struktur aktiv verschlechtert: ein Refactoring, das Komplexität verlagert statt reduziert; eine Änderung, die eine Datei ohne Zerlegung über die Größengrenze schiebt; featurespezifische Logik, die einem geteilten Modul hinzugefügt wird; ein Beinahe-Duplikat eines bestehenden kanonischen Helpers; ein stiller Fallback, der eine unklare Invariante verbirgt.
