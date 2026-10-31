---
name: observability-and-instrumentation
description: Instrumentiert Code, sodass das Verhalten in Produktion sichtbar und diagnostizierbar wird (Observability, Logging, Metriken, Tracing, Alerting). Verwenden, wenn du Logging, Metriken, Tracing oder Alerting ergänzt, wenn du ein Feature auslieferst, das in Produktion läuft und einen Nachweis braucht, dass es funktioniert, oder wenn Produktionsprobleme gemeldet werden, du aus den vorhandenen Daten aber nicht erkennen kannst, was passiert ist. Typische Anfragen „füge Logging hinzu“, „bau Metriken und Tracing ein“, „richte Alerting dafür ein“, „in Produktion sehen wir nicht, was passiert“, „schreib ein Runbook zum Alert“.
---

# Observability und Instrumentierung

## Überblick

Code, den du nicht beobachten kannst, kannst du nicht betreiben. Observability ist die Fähigkeit, die Frage „Was tut das System gerade und warum?“ von außen zu beantworten, anhand der Telemetrie, die der Code ausgibt. Instrumentierung ist kein Add-on nach dem Launch, sondern entsteht zusammen mit dem Feature, genau wie Tests. Wird ein Feature ohne Telemetrie ausgeliefert, wird der erste vom Nutzer gemeldete Bug zur Archäologie statt zu einer Abfrage.

## Wann verwenden

- Beim Bauen jedes Features, das in Produktion laufen wird
- Beim Hinzufügen eines neuen Service, Endpoints, Hintergrundjobs oder einer externen Integration
- Wenn ein Produktionsvorfall zu lange zur Diagnose brauchte („wir konnten nicht erkennen, was passiert ist“)
- Beim Einrichten oder Reviewen von Alerting-Regeln
- Beim Review eines PR, der I/O, Retries, Queues oder servicegrenzenübergreifende Aufrufe hinzufügt

**NICHT für:**
- Die Diagnose eines Fehlers, der gerade auftritt: nutze den Skill `debugging-and-error-recovery` (Observability macht diesen Skill beim nächsten Mal schnell)
- Profiling und Optimierung gemessener Langsamkeit: nutze den Skill `performance-optimization`
- Monitoring-Checklisten für den Launch-Tag und Rollback-Trigger: siehe den Skill `shipping-and-launch`; dieser Skill behandelt die Instrumentierung, die sie speist

## Vorgehen

### 1. Definiere „funktioniert“, bevor du instrumentierst

Telemetrie ohne Fragestellung ist Rauschen. Schreibe vor jeder Instrumentierung 2–4 Fragen auf, die ein On-Call-Engineer zu diesem Feature stellen wird:

```
FEATURE: checkout payment retry
QUESTIONS ON-CALL WILL ASK:
1. What fraction of payments succeed on first attempt vs after retry?
2. When a payment fails permanently, why? (provider error? timeout? validation?)
3. Is the payment provider slower than usual?
→ Every signal below must help answer one of these.
```

Wenn du die Fragen nicht benennen kannst, bist du noch nicht bereit zu instrumentieren: Du loggst alles und lernst nichts.

### 2. Wähle für jede Frage das passende Signal

| Signal | Beantwortet | Kostenprofil | Beispiel |
|---|---|---|---|
| **Strukturiertes Log** | „Was ist in diesem konkreten Fall passiert?“ | Pro Event; wächst mit dem Traffic | `payment_failed` mit Fehlercode des Providers |
| **Metrik** | „Wie oft / wie schnell, aggregiert?“ | Fix pro Serie; günstig abzufragen | p99-Latenz der Provider-Aufrufe |
| **Trace** | „Wo ist die Zeit über Services hinweg geblieben?“ | Pro Request; meist gesampelt | Ein langsamer Checkout, aufgeschlüsselt nach Hops |

Faustregel: Metriken sagen dir, **dass** etwas nicht stimmt, Traces sagen dir **wo**, Logs sagen dir **warum**.

### 3. Strukturiertes Logging

Logge Events, keine Prosa. Jede Logzeile ist ein JSON-Objekt mit stabilem Event-Namen und maschinenlesbaren Feldern:

```typescript
// BAD: string interpolation — unqueryable, inconsistent
logger.info(`Payment ${id} failed for user ${userId} after ${n} retries`);

// GOOD: stable event name + structured fields
logger.warn({
  event: 'payment_failed',
  paymentId: id,
  provider: 'stripe',
  errorCode: err.code,
  attempt: n,
}, 'payment failed');
```

**Log-Level: Nutze sie konsistent:**

| Level | Bedeutung | On-Call-Aktion |
|---|---|---|
| `error` | Invariante verletzt; jemand muss eventuell handeln | Untersuchen |
| `warn` | Beeinträchtigt, aber behandelt (Retry erfolgreich, Fallback genutzt) | Auf Trends achten |
| `info` | Bedeutsames Business-Event (Bestellung aufgegeben, Job beendet) | Keine |
| `debug` | Diagnosedetails | In Produktion standardmäßig aus |

**Correlation-IDs sind Pflicht.** Erzeuge (oder übernimm) an der Systemgrenze eine Request-ID und hänge sie an jede Logzeile, jeden Span und jeden ausgehenden Aufruf. Ohne sie kannst du einen einzelnen Request nicht aus verschachtelten Logs rekonstruieren:

```typescript
// Express: child logger per request, ID propagated downstream
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] ?? crypto.randomUUID();
  req.log = logger.child({ requestId: req.id });
  res.setHeader('x-request-id', req.id);
  next();
});
```

**Wenn mehrere Einstiegspunkte in ein Log schreiben, benenne den Einstiegspunkt.** Eine Correlation-ID identifiziert einen Lauf, sagt aber nicht, welcher Codepfad ihn gestartet hat. Derselbe Job, ausgelöst durch einen Scheduler, einen Replay-Endpoint und einen manuellen CLI-Lauf, erzeugt in einer Senke austauschbare Zeilen. Die Zuordnung einer Zeile läuft dann per Ausschlussverfahren: Du liest die Historie des Schedulers, die Prozesstabelle und ein Deploy-Log gegeneinander, und dieses Argument gilt nur so lange, wie diese externen Aufzeichnungen noch existieren. Setze den Einstiegspunkt dort, wo der Lauf beginnt, neben die Correlation-ID und propagiere beide auf dieselbe Weise:

```typescript
// One helper for every entry point: the run's own logger carries both fields.
// `entryPoint`, not `source` — ECS reserves `source.*` for network fields.
export const runLog = (entryPoint: 'scheduler' | 'replay_endpoint' | 'cli', runId: string) =>
  logger.child({ entryPoint, requestId: runId });

// scheduler tick        -> runLog('scheduler', crypto.randomUUID())
// POST /jobs/:id/replay -> runLog('replay_endpoint', req.id)
// CLI invocation        -> runLog('cli', process.env.RUN_ID ?? crypto.randomUUID())
```

Beide Felder müssen dieselben Grenzen überqueren wie die Correlation-ID (Queue-Metadaten, HTTP-Header), sonst leitet ein Worker den Einstiegspunkt neu ab und rät. Ein Feld, das lediglich mit einem Einstiegspunkt korreliert, ist ein Hinweis, keine Zuordnung: Alles, was den Job aufrufen kann, kann es reproduzieren.

**Logge niemals Secrets, Tokens, Passwörter oder vollständige PII.** Das ist eine harte Regel aus dem Skill `security-and-hardening`: Telemetrie-Pipelines sind ein klassischer Pfad für Datenlecks. Lege Felder per Allowlist fest; logge keine kompletten Request-Bodys.

### 4. Metriken

Instrumentiere bei request-getriebenen Services **RED** für jeden Endpoint und jede externe Abhängigkeit: **R**ate (Requests/s), **E**rrors (Fehlerrate), **D**uration (Latenz-Histogramm, nicht Durchschnitt). Für Ressourcen (Queues, Pools, Hosts) nutze **USE**: **U**tilization (Auslastung), **S**aturation (Sättigung), **E**rrors (Fehler).

Wie beim Tracing ist der herstellerneutrale Weg die OpenTelemetry-Metrics-API (gleiches SDK und gleicher Kontext wie in Schritt 5). Das Beispiel unten verwendet `prom-client` von Prometheus, eine verbreitete Backend-Wahl, aber nicht die einzige; die Regeln für RED/USE und Kardinalität sind in beiden Fällen identisch.

```typescript
import { Histogram } from 'prom-client';

const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'route', 'status_class'],  // '2xx', not '200'
  buckets: [0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
});
```

**Kardinalität ist der Fehlermodus.** Jede eindeutige Label-Kombination ist eine eigene Zeitreihe. Labels müssen aus kleinen, festen Mengen stammen (Route-Template, Statusklasse, Providername). Verwende niemals Nutzer-IDs, rohe URLs, Fehlermeldungen oder andere unbegrenzte Werte als Labels; das gehört in Logs und Traces.

```
OK as label:    route="/api/tasks/:id"   status_class="5xx"   provider="stripe"
NEVER a label:  user_id, email, request_id, full URL, error message text
```

Tracke Durchschnitte nie, Perzentile immer: Ein Durchschnitt verdeckt das 1 % der Nutzer, die eine miserable Erfahrung machen. Nutze Histogramme und lies p50/p95/p99 ab.

### 5. Verteiltes Tracing

Nutze OpenTelemetry: Es ist der herstellerneutrale Standard, und die Auto-Instrumentierung deckt HTTP, gRPC und gängige DB-Clients mit nahezu keinem Code ab:

```typescript
// tracing.ts — must be imported before anything else
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

const sdk = new NodeSDK({
  serviceName: 'checkout-service',
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();
```

Füge manuelle Spans nur um sinnvolle interne Arbeitseinheiten hinzu (z. B. `applyDiscounts`, `chargeProvider`) und hänge die Attribute an, nach denen On-Call filtern wird. Propagiere den Kontext über jede asynchrone Grenze hinweg (HTTP-Header, Queue-Nachrichten-Metadaten), sonst bricht der Trace an der Lücke ab. Sample standardmäßig head-basiert mit niedriger Rate; behalte 100 % der Fehler, wenn dein Backend Tail-Sampling unterstützt.

### 6. Alerting

Alarmiere bei **Symptomen, die Nutzer spüren**, nicht bei Ursachen:

```
SYMPTOM (page-worthy):           CAUSE (dashboard, not a page):
error rate > 1% for 5 min        CPU at 85%
p99 latency > 2s                 one pod restarted
queue age > 10 min               disk at 70%
```

Ursachenbasierte Alerts feuern, wenn nichts falsch ist, und verpassen Fehler, die du nicht vorhergesehen hast. Symptombasierte Alerts feuern genau dann, wenn Nutzer betroffen sind, unabhängig von der Ursache.

Regeln für jeden Alert, den du anlegst:

1. **Er muss handlungsrelevant sein.** Lautet die Reaktion „ignorieren, das heilt sich selbst“, lösche den Alert.
2. **Er verlinkt auf ein Runbook**, und seien es nur drei Zeilen: was er bedeutet, die erste Abfrage, Eskalationsweg.
3. **Er hat Schwellwert und Dauer**, begründet durch das SLO oder historische Daten, nicht durch eine Schätzung.
4. Nutze nur zwei Schweregrade: **page** (nutzerrelevant, sofort handeln) und **ticket** (Beeinträchtigung, diese Woche handeln). Eine dritte Stufe wird zu Rauschen, das Leute darauf trainiert, alles zu ignorieren.

#### Runbooks schreiben

Regel 2 oben verlangt, dass jeder Alert auf ein Runbook verlinkt. Die Aufgabe eines Runbooks ist es, drei Fragen zu beantworten, ohne dass der Leser nachdenken muss: Was passiert gerade, was ist zuerst zu prüfen, und wen ruft man an, wenn das nicht hilft. Lege es in `docs/runbooks/` ab, benannt nach dem Alert.

**Minimal brauchbares Runbook (drei Zeilen):**

```markdown
# Runbook: High Error Rate on /api/tasks
**Means:** DB connection pool likely exhausted, or a bad deploy.
**First check:** `SELECT count(*) FROM pg_stat_activity WHERE backend_type = 'client backend';`
  — if count > pool limit, see Step 2. (Swap in the equivalent for your database.)
**Escalate to:** #db-oncall or engineering on-call rotation.
```

**Wann über drei Zeilen hinaus erweitern:** Füge Schritte nur hinzu, wenn die erste Prüfung allein nicht reicht, um zu entscheiden. Ein Runbook mit fünf Schritten, das die drei häufigsten Ursachen abdeckt, ist besser als ein Dokument mit zwanzig Schritten, das jeden Sonderfall abdeckt und nur überflogen wird.

**Halte Runbooks aktuell.** Aktualisiere das Runbook als Teil des Abschlusses jedes Incidents, in dem es verwendet wurde: Ein veraltetes Runbook erzeugt falsche Sicherheit. War ein Schritt falsch oder fehlte er, behebe das, bevor du den Incident als gelöst markierst.

### 7. Verifiziere die Telemetrie selbst

Instrumentierung ist Code; sie kann falsch sein. Löse die Pfade aus und sieh dir die tatsächliche Ausgabe an, bevor du die Arbeit für abgeschlossen erklärst:

- Erzwinge einen Fehler in Staging → finde ihn in den Logs über `requestId` und prüfe, dass die Felder strukturiert sind (nicht `[object Object]`)
- Sende Testtraffic → prüfe, dass Metrikserien mit den erwarteten Labels und plausiblen Werten erscheinen
- Verfolge einen Request über Services hinweg in der Tracing-UI → keine gebrochenen Spans
- Feuere jeden neuen Alert einmal (Schwellwert vorübergehend senken) → prüfe, dass er den richtigen Kanal erreicht und der Runbook-Link funktioniert

## Typische Ausreden

| Ausrede | Realität |
|---|---|
| „Logging baue ich ein, wenn es läuft“ | „Später“ wird zu „nach dem ersten Incident“, dem teuersten Moment, um zu merken, dass du blind bist. Instrumentiere beim Bauen. |
| „Mehr Logs = mehr Observability“ | Unstrukturiertes Rauschen macht Incidents langsamer, nicht schneller. Drei abfragbare Events schlagen dreihundert Prosazeilen. |
| „console.log reicht erstmal“ | Unstrukturierte Ausgabe lässt sich nicht filtern, korrelieren oder alarmieren. Der strukturierte Logger kostet einmalig fünf Minuten extra. |
| „Wir schauen einfach in die Dashboards, wenn etwas kaputtgeht“ | Dashboards ohne definierte Fragen zeigen dir alles außer der Antwort. Beginne bei den On-Call-Fragen. |
| „Wir alarmieren bei allem Wichtigen, getunt wird später“ | Ein lauter Pager trainiert Leute, ihn zu ignorieren. Das Tuning findet nie statt; der verpasste echte Page schon. |
| „Nutzer-ID als Metrik-Label erleichtert das Debugging“ | Es bringt auch dein Metrik-Backend zum Absturz. Lookups mit hoher Kardinalität gehören in Logs und Traces. |
| „Tracing ist Overkill für unsere zwei Services“ | Zwei Services bedeuten schon Latenzfragen über Servicegrenzen hinweg, die Logs nicht beantworten können. Auto-Instrumentierung macht die Kosten trivial. |

## Warnsignale

- Ein Feature-PR mit Retries, Queues oder externen Aufrufen und null neuer Telemetrie
- Logzeilen, die per String-Interpolation statt aus strukturierten Feldern gebaut werden
- Keine Correlation-/Request-ID: Jede Logzeile ist eine Waise
- Ein Log-Stream, der von einem Scheduler, einem Webhook und manuellen Läufen gespeist wird, ohne ein Feld, das benennt, wer die Zeile erzeugt hat
- Metriken mit Nutzer-IDs, rohen URLs oder Fehlermeldungstexten als Labels (Kardinalitätsbombe)
- Latenz als Durchschnitt getrackt, ohne Perzentile
- Alerts, die täglich feuern und ohne Aktion quittiert werden
- Alerts auf Ursachen (CPU, Speicher) wecken Menschen, während die nutzerseitige Fehlerrate nicht überwacht wird
- Secrets, Tokens oder vollständige Request-Bodys tauchen in Logs auf
- „Bei mir läuft es“ als einziger Beleg dafür, dass ein Produktions-Feature gesund ist

## Verifikation

Bestätige nach der Instrumentierung eines Features:

- [ ] Die On-Call-Fragen für dieses Feature sind aufgeschrieben, und jedes Signal ist einer Frage zugeordnet
- [ ] Die gesamte Log-Ausgabe ist strukturiert (JSON), mit stabilen Event-Namen und einer Correlation-ID in jeder Zeile
- [ ] Jede Log-Senke, in die mehr als ein Einstiegspunkt schreibt, trägt ein Einstiegspunkt-Feld, das dort gesetzt wird, wo der Lauf beginnt, und mit der Correlation-ID propagiert statt weiter unten abgeleitet wird
- [ ] Keine Secrets, Tokens oder unmaskierte PII in irgendeiner Logzeile (tatsächliche Ausgabe stichprobenartig prüfen)
- [ ] RED-Metriken existieren für jeden neuen Endpoint und jede externe Abhängigkeit, mit begrenzten Label-Mengen
- [ ] Latenz ist ein Histogramm; p95/p99 sind abfragbar
- [ ] Ein einzelner Request lässt sich in der Tracing-UI durchgängig ohne gebrochene Spans verfolgen
- [ ] Jeder neue Alert ist symptombasiert, hat einen Runbook-Link und wurde einmal testweise gefeuert
- [ ] Ein in Staging herbeigeführter Fehler wurde allein anhand der Telemetrie lokalisiert, ohne den Quellcode zu lesen

Die Kurzfassung dieser Liste, einschließlich des Instrumentierungs-Gates vor dem Launch, findest du in `../../references/observability-checklist.md`.
