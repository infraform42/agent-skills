# Performance-Checkliste

Kurze Referenz-Checkliste für die Performance von Webanwendungen. Verwende sie zusammen mit dem Skill `performance-optimization`.

## Inhaltsverzeichnis

- [Core Web Vitals Targets](#core-web-vitals-targets)
- [TTFB Diagnosis](#ttfb-diagnosis)
- [Frontend Checklist](#frontend-checklist)
- [Backend Checklist](#backend-checklist)
- [Caching Strategies](#caching-strategies)
- [Measurement Commands](#measurement-commands)
- [Common Anti-Patterns](#common-anti-patterns)

## Core Web Vitals Targets

| Metrik | Gut | Verbesserungsbedarf | Schlecht |
|--------|------|------------|------|
| LCP (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| INP (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## TTFB Diagnosis

Wenn TTFB langsam ist (> 800ms), prüfe jede Komponente im Network-Waterfall der DevTools:

- [ ] **DNS-Auflösung** langsam → `<link rel="dns-prefetch">` oder `<link rel="preconnect">` für bekannte Origins ergänzen
- [ ] **TCP/TLS-Handshake** langsam → HTTP/2 aktivieren, Edge-Deployment erwägen, Keep-Alive verifizieren
- [ ] **Server-Verarbeitung** langsam → Backend profilen, langsame Queries prüfen, Caching ergänzen

## Frontend Checklist

### Images
- [ ] Bilder verwenden moderne Formate (WebP, AVIF)
- [ ] Bilder sind responsiv dimensioniert (`srcset` und `sizes`)
- [ ] Bilder und `<source>`-Elemente haben explizite `width` und `height` (verhindert CLS bei Art Direction)
- [ ] Bilder unterhalb des sichtbaren Bereichs verwenden `loading="lazy"` und `decoding="async"`
- [ ] Hero-/LCP-Bilder verwenden `fetchpriority="high"` und kein Lazy Loading

### JavaScript
- [ ] Bundle-Größe unter 200KB gzipped (initiales Laden)
- [ ] Code Splitting mit dynamischem `import()` für Routen und schwergewichtige Features
- [ ] Tree Shaking aktiviert (verifizieren, dass die Dependency ESM ausliefert und `sideEffects: false` setzt)
- [ ] Kein blockierendes JavaScript im `<head>` (`defer` oder `async` verwenden)
- [ ] Rechenintensive Berechnungen in Web Workers auslagern (falls zutreffend)
- [ ] `React.memo()` bei teuren Komponenten, die mit denselben Props neu rendern
- [ ] `useMemo()` / `useCallback()` nur dort, wo Profiling einen Nutzen zeigt
- [ ] Long Tasks (> 50ms) aufteilen, damit der Main Thread verfügbar bleibt — wichtigster Hebel für INP
- [ ] `yieldToMain`-Pattern in lang laufenden Schleifen verwenden, damit Input-Events zwischen den Chunks laufen können
- [ ] Moderne Scheduling-APIs verwenden, wo verfügbar: `scheduler.yield()` (bevorzugt), `scheduler.postTask()` mit Prioritäten, `isInputPending()`, um nur bei Bedarf abzugeben
- [ ] `requestIdleCallback` für aufschiebbare, nicht dringende Arbeit (Analytics-Flush, Prefetch, Warmup)
- [ ] Nicht kritische Arbeit (z. B. Analytics, Logging) aus Event-Handlern auslagern, damit die Reaktion auf die Interaktion nicht verzögert wird
- [ ] Third-Party-Skripte mit `async` / `defer` laden, auf Größe prüfen und bei hohem Gewicht hinter einer Facade laden (Chat-Widgets, Embeds)

### CSS
- [ ] Kritisches CSS inline einbinden oder per Preload laden
- [ ] Kein render-blockierendes CSS für nicht kritische Styles
- [ ] Keine Laufzeitkosten durch CSS-in-JS in Produktion (Extraktion verwenden)

### Fonts
- [ ] Auf 2–3 Schriftfamilien mit je 2–3 Schnitten begrenzen (jeder zusätzliche Schnitt ist ein weiterer Request)
- [ ] Ausschließlich WOFF2-Format (kleinste Größe, universelle Unterstützung — WOFF/TTF/EOT weglassen)
- [ ] Wenn möglich selbst hosten (Font-CDNs von Drittanbietern fügen DNS-, TCP- und TLS-Roundtrips hinzu)
- [ ] LCP-kritische Fonts per Preload laden: `<link rel="preload" as="font" type="font/woff2" crossorigin>`
- [ ] `font-display: swap` (oder `optional` für nicht kritische Fonts), damit FOIT das Rendern nicht blockiert
- [ ] Per `unicode-range` subsetten, damit jede Seite nur die benötigten Glyphen ausliefert
- [ ] Variable Fonts erwägen, wenn mehrere Schnitte/Stile benötigt werden (eine Datei ersetzt viele)
- [ ] Metriken der Fallback-Schrift mit `size-adjust`, `ascent-override`, `descent-override` anpassen, um CLS beim Font-Swap zu verringern
- [ ] Vor jeder Custom Font einen System-Font-Stack erwägen

### Network
- [ ] Statische Assets mit langem `max-age` + Content-Hashing cachen
- [ ] API-Antworten dort cachen, wo es sinnvoll ist (`Cache-Control`)
- [ ] HTTP/2 oder HTTP/3 aktiviert
- [ ] Ressourcen per Preconnect (`<link rel="preconnect">`) für bekannte Origins vorverbinden
- [ ] `fetchpriority` bei kritischen Nicht-Bild-Ressourcen verwenden (z. B. wichtiges `<link rel="preload">`, `<script>` im sichtbaren Bereich) — nicht nur bei `<img>`
- [ ] Keine unnötigen Redirects

### Rendering
- [ ] Kein Layout Thrashing (erzwungene synchrone Layouts)
- [ ] Animationen verwenden `transform` und `opacity` (GPU-beschleunigt)
- [ ] Lange Listen verwenden Virtualisierung (z. B. `react-window`)
- [ ] Keine unnötigen Re-Renders der gesamten Seite
- [ ] Bereiche außerhalb des Viewports verwenden `content-visibility: auto` mit `contain-intrinsic-size`, um Layout/Paint nicht sichtbarer Bereiche zu überspringen
- [ ] Keine `unload`-Event-Handler und kein `Cache-Control: no-store` bei HTML-Antworten — erhält die Eignung für den Back/Forward-Cache (bfcache)

## Backend Checklist

### Database
- [ ] Keine N+1-Query-Muster (Eager Loading / Joins verwenden)
- [ ] Queries haben passende Indizes
- [ ] Listen-Endpunkte paginiert (niemals `SELECT * FROM table`)
- [ ] Connection Pooling konfiguriert
- [ ] Logging langsamer Queries aktiviert

#### Query plans
- [ ] `EXPLAIN ANALYZE` **vor** dem Fix erfasst, nicht erst danach — er ist die Baseline
- [ ] `Seq Scan` auf einer großen Tabelle verstanden: Index fehlt, ist nicht nutzbar oder lohnt sich tatsächlich nicht
- [ ] Geschätzte vs. tatsächliche `rows=` innerhalb einer Größenordnung (falls nicht, Statistiken aktualisieren, bevor du Indizes anfasst)
- [ ] Kein `Sort`-Knoten, den ein Composite-Index übernehmen könnte
- [ ] Plan nach der Änderung erneut geprüft — ein Index, der den Plan nicht verändert hat, wird zurückgenommen

#### Index strategy
- [ ] Spaltenreihenfolge im Composite-Index: erst Gleichheit, dann Range/Sort
- [ ] Index deckt die Form der Query ab (Filter + Sortierung), nicht nur eine einzelne Spalte isoliert
- [ ] Covering Index für heiße Lesepfade erwägen (ein Index-Only-Scan vermeidet den Heap-Zugriff)
- [ ] Spalten mit niedriger Selektivität *für den dominanten Wert* nicht indizieren; ein partieller Index bedient weiterhin die Query auf seltene Werte (`WHERE status = 'failed'`)
- [ ] Expression-Index verwenden, wo die Query eine Funktion anwendet (`lower(email)`)
- [ ] Volltext- oder Trigram-Index für Suche mit führendem Wildcard verwenden, kein B-Tree
- [ ] Schreibkosten bei schreiblastigen Tabellen messen (jeder Index belastet jedes `INSERT`/`UPDATE`)
- [ ] Ungenutzte und doppelte Indizes entfernen (sie kosten Schreibleistung und bringen nichts)

#### Connection pooling
- [ ] Ein Pool pro Prozess, nicht pro Request oder pro Modul
- [ ] `instances × pool max` bleibt unter `max_connections` der Datenbank
- [ ] `connectionTimeoutMillis` gesetzt, damit Erschöpfung schnell fehlschlägt, statt ewig in der Warteschlange zu hängen
- [ ] Erschöpfung diagnostizieren, bevor du die Größe anpasst: finde heraus, was Verbindungen festhält (lange Transaktionen, fehlendes `await`, geleakte Clients)
- [ ] Serverless / Autoscaling hinter einen Multiplexing-Proxy schalten (pgbouncer, RDS Proxy), statt den Pool zu vergrößern

### API
- [ ] Antwortzeiten < 200ms (p95)
- [ ] Keine synchrone, rechenintensive Verarbeitung in Request-Handlern
- [ ] Bulk-Operationen statt Schleifen mit einzelnen Aufrufen
- [ ] Response-Kompression (gzip/brotli)
- [ ] Passendes Caching (In-Memory, Redis, CDN)

### Infrastructure
- [ ] CDN für statische Assets
- [ ] Server nah bei den Nutzern (oder Edge-Deployment)
- [ ] Horizontale Skalierung konfiguriert (falls nötig)
- [ ] Health-Check-Endpunkt für den Load Balancer

## Caching Strategies

Die Entscheidungsgrundlagen (welche Schicht, welche Invalidierungsstrategie, was nie gecacht werden darf) stehen im Skill `performance-optimization`. Dieser Abschnitt behandelt die Lese-/Schreibmuster und die Checkliste.

### Read and write patterns

| Muster | Funktionsweise | Verwenden, wenn | Worauf achten |
|---|---|---|---|
| **Cache-aside** (lazy) | App prüft den Cache, liest bei einem Miss vom Origin und befüllt den Cache | Standardwahl; leselastig, toleriert einen kalten ersten Zugriff | Jeder Miss trifft den Origin, daher ist Stampede-Schutz nötig |
| **Read-through** | Die Cache-Schicht selbst lädt bei einem Miss | Du willst den Ladepfad an einer Stelle statt an jeder Aufrufstelle | Verbirgt die Latenz des Origins; ein langsamer Origin wirkt wie ein langsamer Cache |
| **Write-through** | Schreibzugriff geht synchron gleichzeitig an Cache und Origin | Lesezugriffe dürfen nach einem Schreibzugriff nie einen veralteten Wert sehen | Fügt jedem Schreibzugriff Cache-Latenz hinzu |
| **Write-behind** (write-back) | Schreibzugriff trifft den Cache, der Origin wird asynchron aktualisiert | Schreiblastig, und der Origin ist der Flaschenhals | Zeitfenster für Datenverlust, falls der Cache vor dem Flush ausfällt. Erfordert Durability, die du vertreten kannst |

### Negative caching

Cache auch die *Abwesenheit* eines Ergebnisses. Ein Key, der bei jedem Lookup verfehlt (eine nicht existierende User-ID, die in einer Schleife abgefragt wird, ein 404-Asset), schickt jeden Request an den Origin — das ist ein Cache, der nur den Happy Path schützt.

- Einen expliziten „Not found"-Sentinel mit **kürzerer** TTL als bei positiven Einträgen speichern
- Die negative TTL so kurz halten, dass ein neu angelegter Datensatz zeitnah erscheint
- Einen *Fehler* des Origins niemals zu einem negativen Cache-Eintrag werden lassen, sonst wird aus einer fehlerhaften Minute eine ganze Reihe

### Request coalescing (stampede protection)

Eine Neuberechnung, N Wartende. Verhindert, dass der Ablauf eines heißen Keys die volle gleichzeitige Last an den Origin weiterreicht:

```typescript
const inFlight = new Map<string, Promise<unknown>>();

function loadOnce<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const existing = inFlight.get(key) as Promise<T> | undefined;
  if (existing) return existing;
  const p = fetcher().finally(() => inFlight.delete(key));
  inFlight.set(key, p);
  return p;
}
```

Bei einem geteilten Cache braucht dieselbe Idee einen verteilten Lock oder `stale-while-revalidate`, damit Wartende den veralteten Wert ausliefern, statt zu blockieren.

### Cache checklist
- [ ] Der gecachte Aufruf wurde zuerst als teuer gemessen (einen schnellen Aufruf zu cachen fügt einen Hop hinzu und bringt nichts)
- [ ] Das Lese-/Schreibverhältnis rechtfertigt den Cache (wird weit häufiger gelesen als geschrieben)
- [ ] Der Cache-Key enthält jede Eingabe, von der die Antwort abhängt: Tenant, Betrachter, Locale, Berechtigungen, Feature-Flags
- [ ] Keine nutzerspezifischen Daten unter einem Key gecacht, der den Nutzer nicht identifiziert
- [ ] Eine Invalidierungsstrategie gewählt (TTL, Event/Tag oder versionierte Keys), keine zufällige Mischung
- [ ] Akzeptables Zeitfenster für Veralterung aufgeschrieben, nicht von einer zufällig getippten TTL impliziert
- [ ] Stampede-Schutz bei heißen Keys (Coalescing, Lock oder `stale-while-revalidate`)
- [ ] Negative Ergebnisse mit kürzerer TTL gecacht; Fehler des Origins nie gecacht
- [ ] Eviction-Policy und Speicherobergrenze gesetzt (ein unbegrenzter Cache ist ein Memory Leak)
- [ ] Hit Rate überwacht — ein Cache, den niemand misst, ist eine Annahme, und eine niedrige Hit Rate ist reiner Overhead
- [ ] Nichts gecacht, dessen Veralterung ein Korrektheitsfehler ist (Kontostände, Berechtigungen, Lagerbestand beim Checkout)

## Measurement Commands

### INP field data and DevTools workflow

1. **Zuerst Felddaten** — prüfe [CrUX Vis](https://developer.chrome.com/docs/crux/vis) oder dein RUM-Tool auf echte Nutzer-INP, bevor du optimierst
2. **Langsame Interaktionen identifizieren** — öffne DevTools → Performance-Panel → zeichne auf, während du interagierst; achte auf Long Tasks, die durch Klicks/Tastenanschläge ausgelöst werden
3. **Auf Mittelklasse-Android testen** — INP-Probleme zeigen sich oft erst auf langsamerer Hardware; verwende ein echtes Gerät oder CPU-Throttling in den DevTools (4×–6× Verlangsamung)

```bash
# Lighthouse CLI
npx lighthouse http://localhost:3000 --output json --output-path ./report.json

# Bundle analysis
npx webpack-bundle-analyzer stats.json
# or for Vite:
npx vite-bundle-visualizer

# Check bundle size
npx bundlesize
```

```javascript
// Web Vitals in code
import { onLCP, onINP, onCLS } from 'web-vitals';
onLCP(console.log);
onINP(console.log);
onCLS(console.log);

// INP with interaction-level detail (attribution build). The attribution build
// exports the same names, so alias it when both builds share a module.
import { onINP as onINPWithAttribution } from 'web-vitals/attribution';
onINPWithAttribution(({ value, attribution }) => {
  const { interactionTarget, inputDelay, processingDuration, presentationDelay } = attribution;
  console.log({ value, interactionTarget, inputDelay, processingDuration, presentationDelay });
});
```

## Common Anti-Patterns

| Anti-Pattern | Auswirkung | Behebung |
|---|---|---|
| N+1-Queries | Lineares Wachstum der DB-Last | Joins, Includes oder Batch Loading verwenden |
| Unbegrenzte Queries | Speichererschöpfung, Timeouts | Immer paginieren, LIMIT ergänzen |
| Fehlende Indizes | Langsame Lesezugriffe bei wachsenden Daten | Indizes für gefilterte/sortierte Spalten ergänzen |
| Indizieren ohne den Plan zu lesen | Schreibkosten werden gezahlt, Lesegewinn unbewiesen | `EXPLAIN ANALYZE` vorher und nachher; zurücknehmen, wenn der Plan unverändert ist |
| Redundante / ungenutzte Indizes | Jeder Schreibzugriff zahlt dafür | Nutzungsstatistiken prüfen, entfernen, was niemand liest |
| Connection Pool pro Request | Erschöpft `max_connections` unter Last | Ein Pool pro Prozess; Proxy für Serverless |
| Cache-Key ohne den Betrachter | Daten eines Nutzers werden an einen anderen ausgeliefert | Key auf Tenant, Betrachter, Locale, Berechtigungen bilden |
| Unbegrenzter Cache | Memory Leak im Gewand einer Optimierung | Eviction-Policy und Speicherobergrenze setzen |
| Cache Stampede bei einem heißen Key | Origin bekommt beim Ablauf die volle gleichzeitige Last | Misses koaleszieren oder `stale-while-revalidate` |
| Layout Thrashing | Ruckeln, verlorene Frames | DOM-Lesezugriffe bündeln, dann Schreibzugriffe bündeln |
| Nicht optimierte Bilder | Langsamer LCP, verschwendete Bandbreite | WebP, responsive Größen, Lazy Load verwenden |
| Große Bundles | Langsame Time to Interactive | Code Splitting, Tree Shaking, Dependencies prüfen |
| Blockierter Main Thread | Schlechter INP, nicht reagierende UI | Long Tasks mit `scheduler.yield()` / `yieldToMain` aufteilen, an Web Workers auslagern |
| Memory Leaks | Wachsender Speicher, irgendwann Absturz | Listener, Intervalle, Refs aufräumen |
