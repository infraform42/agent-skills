# Observability-Checkliste

Kurzreferenz für die Instrumentierung von Produktionscode. Verwende sie zusammen mit dem Skill `observability-and-instrumentation`.

## Inhaltsverzeichnis

- [On-Call-Fragen (hier beginnen)](#on-call-questions-start-here)
- [Strukturiertes Logging](#structured-logging)
- [Metriken](#metrics)
- [Distributed Tracing](#distributed-tracing)
- [Alerting](#alerting)
- [Dashboards](#dashboards)
- [Telemetrie verifizieren](#verify-the-telemetry)
- [Pre-Launch-Gate](#pre-launch-gate)

## On-Call-Fragen (hier beginnen)

Telemetrie ohne Frage ist Rauschen. Bevor du irgendetwas instrumentierst:

- [ ] 2–4 Fragen, die ein On-Call-Engineer zu diesem Feature stellen wird, sind aufgeschrieben
- [ ] Jedes Signal unten lässt sich einer dieser Fragen zuordnen
- [ ] Jede Frage ist dem passenden Signaltyp zugeordnet: Metriken zeigen, **dass** etwas falsch läuft, Traces zeigen, **wo**, Logs zeigen, **warum**

## Strukturiertes Logging

- [ ] Logs sind strukturiert (JSON) und haben stabile Event-Namen – keine freien Strings
- [ ] Jede Logzeile trägt eine Correlation-/Request-ID, die an der Systemgrenze erzeugt oder übernommen wird
- [ ] Die Correlation-ID wird bei jedem ausgehenden Aufruf und an jeder asynchronen Grenze weitergegeben (HTTP-Header, Queue-Metadaten)
- [ ] Jeder Log-Stream, in den mehr als ein Einstiegspunkt schreibt (Scheduler, Replay-Endpunkt, manueller Lauf), enthält ein Einstiegspunkt-Feld, das dort gesetzt wird, wo der Lauf startet, und zusammen mit der Correlation-ID weitergegeben wird
- [ ] Log-Level sind konsistent: `error` = Invariante verletzt, jemand muss ggf. handeln; `warn` = beeinträchtigt, aber behandelt; `info` = bedeutsames Geschäftsereignis; `debug` = in Produktion aus
- [ ] Keine Secrets, Tokens, Passwörter oder unmaskierten personenbezogenen Daten (PII) in irgendeiner Logzeile (harte Regel aus `security-and-hardening`)
- [ ] Felder sind per Allowlist festgelegt – keine vollständigen Request-/Response-Bodies, keine Auth-Header
- [ ] Aufrufe externer Dienste werden nur mit Metadaten geloggt: Endpunkt, Status, Latenz, Anzahl der Versuche, bereinigte Identifier
- [ ] Tatsächliche Log-Ausgabe stichprobenartig geprüft: strukturierte Felder, nicht `[object Object]`

## Metriken

- [ ] **RED** ist für jeden Endpunkt und jede externe Abhängigkeit instrumentiert: Rate, Errors, Duration
- [ ] **USE** ist für jede Ressource (Queues, Pools, Hosts) instrumentiert: Utilization, Saturation, Errors
- [ ] Latenz ist ein Histogramm; p50/p95/p99 sind abfragbar – niemals ein Durchschnitt
- [ ] Alle Labels stammen aus kleinen, festen Mengen (Route-Template, Statusklasse, Provider-Name)
- [ ] Keine unbegrenzten Label-Werte: keine User-IDs, Tenant-IDs, E-Mail-Adressen, rohen URLs, Request-IDs oder Fehlermeldungstexte
- [ ] Statuscodes nach Klasse gruppiert (`5xx`, nicht `503`)
- [ ] Queue-Tiefe und Verarbeitungsdauer werden für jeden Worker und jede Queue erfasst

## Distributed Tracing

- [ ] OpenTelemetry (oder Äquivalent) wird beim Service-Start initialisiert, vor anderen Imports
- [ ] Auto-Instrumentierung ist für HTTP-, gRPC- und DB-Clients aktiviert
- [ ] Der Trace-Kontext wird bei jedem ausgehenden Aufruf weitergegeben (W3C `traceparent`/`tracestate`) und aus jedem eingehenden Request extrahiert
- [ ] Der Kontext übersteht asynchrone Grenzen – Queue-Nachrichten tragen Trace-Metadaten
- [ ] Manuelle Spans nur um sinnvolle interne Arbeitseinheiten, mit den Attributen, nach denen On-Call filtern wird
- [ ] Keine Secrets oder PII als Span-Attribute
- [ ] Head-based Sampling mit niedriger Standardrate; 100 % der Fehler bleiben erhalten, falls Tail-Sampling verfügbar ist

## Alerting

- [ ] Jeder Alert ist symptombasiert (Fehlerrate, p99-Latenz, Queue-Alter) – Ursachen (CPU, Disk, Neustarts) gehören in Dashboards, nicht auf Pager
- [ ] Jeder Alert ist umsetzbar; Alerts nach dem Muster „ignorieren, heilt sich selbst" werden gelöscht
- [ ] Jeder Alert verlinkt auf ein Runbook – mindestens drei Zeilen: was er bedeutet, die erste auszuführende Abfrage, Eskalationspfad
- [ ] Schwellenwerte und Dauern sind durch ein SLO oder historische Daten begründet, nicht geraten
- [ ] Nur zwei Schweregrade: **Page** (nutzersichtbar, sofort handeln) und **Ticket** (Beeinträchtigung, diese Woche handeln)
- [ ] Jeder neue Alert wurde einmal testweise ausgelöst: Er hat den richtigen Kanal erreicht und der Runbook-Link funktioniert
- [ ] Keine Alerts, die täglich feuern und ohne Aktion quittiert werden

## Dashboards

- [ ] Ein Service-Health-Dashboard existiert: Fehlerrate, p99-Latenz, Traffic, Saturation
- [ ] Das Dependency-Health-Panel zeigt Fehlerraten und Latenz pro Service
- [ ] Das Dashboard beantwortet die On-Call-Fragen vom Anfang dieser Checkliste – nicht „alles außer der Antwort"
- [ ] Der Standard-Zeitraum ist sinnvoll (1 h–6 h, nicht 30 d)

## Telemetrie verifizieren

Instrumentierung ist Code; sie kann falsch sein:

- [ ] Einen Fehler in Staging erzwungen → ihn anhand der Correlation-ID in den Logs gefunden
- [ ] Test-Traffic gesendet → Metrik-Serien erscheinen mit den erwarteten Labels und plausiblen Werten
- [ ] Einen Request in der Tracing-UI Ende-zu-Ende verfolgt → keine abgebrochenen Spans
- [ ] Einen herbeigeführten Ausfall allein anhand der Telemetrie diagnostiziert, ohne den Quellcode zu lesen

## Pre-Launch-Gate

Bevor ein Feature in Produktion geht, trifft alles Folgende zu:

- [ ] Strukturierte Logs fließen in den Log-Aggregator
- [ ] RED-Metriken sind in Dashboards für jeden neuen Endpunkt und jede neue Abhängigkeit sichtbar
- [ ] Mindestens ein symptombasierter Alert ist konfiguriert, mit Runbook und testweise ausgelöst
- [ ] Ein Request lässt sich über jeden Service nachverfolgen, den er berührt
- [ ] On-Call weiß, wo die Runbooks liegen

Die Abfolge für das Monitoring am Launch-Tag und die Rollback-Trigger findest du im Skill `shipping-and-launch`.
