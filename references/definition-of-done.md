# Definition of Done

Ein projektweiter, fester Maßstab, den jede Änderung erfüllen muss, bevor sie als erledigt gilt. Anders als Akzeptanzkriterien, die pro Aufgabe variieren und die Frage „Haben wir das Richtige gebaut?“ beantworten, ist die Definition of Done jedes Mal dieselbe und beantwortet die Frage „Ist das nach unserem Standard fertig?“. Nutze sie als letztes Gate in `planning-and-task-breakdown`, `incremental-implementation` und `shipping-and-launch`.

## Definition of Done vs. Akzeptanzkriterien

| | Akzeptanzkriterien | Definition of Done |
|---|---|---|
| Geltungsbereich | Spezifisch für eine Aufgabe oder ein Spec | Gilt für jedes Inkrement |
| Änderungen | Für jedes Element anders | Fest und wiederverwendet |
| Beantwortet | „Haben wir *dieses Ding* gebaut?“ | „Ist es *bereit*?“ |
| Verantwortlich | Wird bei der Planung der Aufgabe festgelegt | Wird einmal für das Projekt festgelegt |
| Beispiel | „Nutzer kann das Passwort über einen E-Mail-Link zurücksetzen“ | „Tests laufen durch, keine Regressionen, Doku aktualisiert“ |

Beides ergänzt sich. Eine Aufgabe ist erst dann erledigt, wenn **ihre** Akzeptanzkriterien erfüllt sind **und** die feste Definition of Done erfüllt ist. Wer eines von beiden überspringt, hinterlässt Arbeit, die fertig aussieht, es aber nicht ist.

## Die feste Checkliste

Wende sie auf jede Änderung an, bevor du sie für erledigt erklärst.

### Korrektheit
- [ ] Alle Akzeptanzkriterien der Aufgabe sind erfüllt
- [ ] Der Code läuft und verhält sich wie vorgesehen, zur Laufzeit verifiziert, nicht nur kompiliert oder typgeprüft
- [ ] Neues Verhalten ist durch Tests abgedeckt, die ohne die Änderung fehlschlagen und mit ihr durchlaufen
- [ ] Bestehende Tests laufen weiterhin durch; es wurden keine Regressionen eingeführt
- [ ] Randfälle und Fehlerpfade sind behandelt, nicht nur der Happy Path

### Qualität
- [ ] Der Code macht seine Absicht durch Benennung und Struktur deutlich; es braucht keine Kommentare, die erklären, *was* er tut
- [ ] Keine duplizierte Geschäftslogik
- [ ] Kein toter Code, keine Debug-Ausgaben und keine auskommentierten Blöcke zurückgelassen
- [ ] Änderungen beschränken sich auf die Aufgabe; keine fachfremden Refaktorierungen eingeschmuggelt
- [ ] Linting und Formatierung laufen durch

Die Tiefe hinter diesen Punkten steckt in `code-review-and-quality` (das Fünf-Achsen-Review) und `code-simplification` (Komplexität reduzieren, ohne das Verhalten zu ändern).

### Integration
- [ ] Die Änderung funktioniert mit dem Rest des Systems, nicht nur isoliert
- [ ] Datenbank-Migrationen, Konfigurationsänderungen und Feature-Flags sind berücksichtigt
- [ ] Abwärtskompatibilität ist für jede Änderung an einer öffentlichen Schnittstelle oder API bedacht

### Dokumentation
- [ ] Öffentliche Schnittstellen, APIs und nutzersichtbares Verhalten sind dokumentiert
- [ ] Erhaltenswerte Architekturentscheidungen sind festgehalten (siehe `documentation-and-adrs`)
- [ ] Die Dokumentation beschreibt den aktuellen Stand in zeitloser Sprache, nicht die Änderungshistorie

### Ship-Bereitschaft
- [ ] Sicherheitsauswirkungen sind bei nicht vertrauenswürdigen Eingaben, Authentifizierung oder Datenverarbeitung geprüft (siehe `security-and-hardening`)
- [ ] Observability ist für neue kritische Pfade vorhanden (Logs, Metriken, Traces) (siehe `observability-and-instrumentation`)
- [ ] Für alles Riskante existiert ein Rollback-Pfad (siehe `shipping-and-launch`)
- [ ] Ein Mensch hat die Änderung geprüft und freigegeben, bevor sie gemergt oder deployt wird

## Anwendung

- **Pro Aufgabe**: Bestätige die Abschnitte Korrektheit und Qualität, bevor du die Aufgabe abhakst.
- **Pro Feature**: Bestätige Integration und Dokumentation, bevor du das Feature als abgeschlossen betrachtest.
- **Pro Release**: Die vollständige Checkliste ist die Untergrenze; `shipping-and-launch` ergänzt darüber hinaus die deploy-spezifischen Gates.

Passe die Liste einmal an das Projekt an und nutze sie dann unverändert weiter. Eine Definition of Done, die in jedem Sprint neu verhandelt wird, ist keine Definition of Done.

## Warnsignale

- „Es ist fertig, ich habe es nur noch nicht ausgeführt“: Nicht verifizierte Arbeit ist nicht erledigt.
- „Tests laufen durch“ als Synonym für erledigt, während Doku, Regressionen oder Laufzeitverifikation übersprungen werden.
- Ein anderer Maßstab je nach Termindruck.
- Akzeptanzkriterien werden als der gesamte Maßstab behandelt, ohne festen Qualitätsboden.
- „Fertig“ wird erklärt, bevor ein Mensch eine Änderung geprüft hat, die das braucht.
