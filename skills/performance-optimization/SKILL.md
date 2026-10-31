---
name: performance-optimization
description: Optimiert die Performance von Anwendungen in Frontend, Backend, Abfragen und Datenbanken. Verwenden, wenn Performance-Anforderungen bestehen, wenn Performance-Regressionen vermutet werden, wenn Core Web Vitals oder Ladezeiten verbessert werden müssen, wenn N+1-Query-Muster behoben werden müssen oder wenn Profiling Engpässe aufdeckt. Typische Auslöser sind „mach die Seite schneller“, „die API ist zu langsam“, „finde den Performance-Engpass“, „behebe die N+1-Queries“ oder „verbessere den LCP-Wert“.
---

# Performance Optimization

## Überblick

Miss, bevor du optimierst. Performance-Arbeit ohne Messung ist Raten, und Raten führt zu vorzeitiger Optimierung, die Komplexität hinzufügt, ohne das zu verbessern, worauf es ankommt. Profiliere zuerst, identifiziere den tatsächlichen Engpass, behebe ihn, miss erneut. Optimiere nur, was Messungen als relevant belegen.

## Wann verwenden

- Performance-Anforderungen existieren in der Spec (Ladezeit-Budgets, Antwortzeit-SLAs)
- Nutzer oder Monitoring melden langsames Verhalten
- Core-Web-Vitals-Werte liegen unter den Schwellenwerten
- Du vermutest, dass eine Änderung eine Regression eingeführt hat
- Du baust Features, die große Datenmengen oder hohen Traffic verarbeiten

**Wann NICHT verwenden:** Optimiere nicht, bevor du Belege für ein Problem hast. Vorzeitige Optimierung fügt Komplexität hinzu, die mehr kostet, als die Performance einbringt.

## Core-Web-Vitals-Ziele

| Metrik | Gut | Verbesserungsbedarf | Schlecht |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## Der Optimierungs-Workflow

```
1. MEASURE  → Establish baseline with real data
2. IDENTIFY → Find the actual bottleneck (not assumed)
3. FIX      → Address the specific bottleneck
4. VERIFY   → Measure again; keep or revert
5. GUARD    → Add monitoring or tests to prevent regression
```

### Schritt 1: Messen

Zwei sich ergänzende Ansätze, nutze beide:

- **Synthetisch (Lighthouse, DevTools-Performance-Tab):** Kontrollierte Bedingungen, reproduzierbar. Am besten geeignet für die Erkennung von Regressionen in CI und zum Isolieren einzelner Probleme.
- **RUM (web-vitals-Bibliothek, CrUX):** Echte Nutzerdaten unter realen Bedingungen. Erforderlich, um zu belegen, dass ein Fix die Nutzererfahrung tatsächlich verbessert hat.

**Frontend:**
```javascript
// Synthetic: Lighthouse in Chrome DevTools (or CI)
// Chrome DevTools → Performance tab → Record
// Chrome DevTools MCP → Performance trace

// RUM: Web Vitals library in code
import { onLCP, onINP, onCLS } from 'web-vitals';

onLCP(console.log);
onINP(console.log);
onCLS(console.log);
```

**Backend:**
```javascript
// Response time logging
// Application Performance Monitoring (APM)
// Database query logging with timing

// Simple timing
console.time('db-query');
const result = await db.query(...);
console.timeEnd('db-query');
```

### Wo du mit dem Messen beginnst

Entscheide anhand des Symptoms, was du zuerst misst:

```
What is slow?
├── First page load
│   ├── Large bundle? --> Measure bundle size, check code splitting
│   ├── Slow server response? --> Measure TTFB in DevTools Network waterfall
│   │   ├── DNS long? --> Add dns-prefetch / preconnect for known origins
│   │   ├── TCP/TLS long? --> Enable HTTP/2, check edge deployment, keep-alive
│   │   └── Waiting (server) long? --> Profile backend, check queries and caching
│   └── Render-blocking resources? --> Check network waterfall for CSS/JS blocking
├── Interaction feels sluggish
│   ├── UI freezes on click? --> Profile main thread, look for long tasks (>50ms)
│   ├── Form input lag? --> Check re-renders, controlled component overhead
│   └── Animation jank? --> Check layout thrashing, forced reflows
├── Page after navigation
│   ├── Data loading? --> Measure API response times, check for waterfalls
│   └── Client rendering? --> Profile component render time, check for N+1 fetches
└── Backend / API
    ├── Single endpoint slow? --> Profile database queries, check indexes
    ├── All endpoints slow? --> Check connection pool, memory, CPU
    └── Intermittent slowness? --> Check for lock contention, GC pauses, external deps
```

### Schritt 2: Den Engpass identifizieren

Häufige Engpässe nach Kategorie:

**Frontend:**

| Symptom | Wahrscheinliche Ursache | Untersuchung |
|---------|-------------|---------------|
| Langsamer LCP | Große Bilder, render-blockierende Ressourcen, langsamer Server | Network-Waterfall und Bildgrößen prüfen |
| Hoher CLS | Bilder ohne Abmessungen, spät ladende Inhalte, Font-Shifts | Layout-Shift-Attribution prüfen |
| Schlechter INP | Aufwendiges JavaScript im Main Thread, große DOM-Updates | Long Tasks im Performance-Trace prüfen |
| Langsamer initialer Ladevorgang | Großes Bundle, viele Netzwerk-Requests | Bundle-Größe und Code Splitting prüfen |

**Backend:**

| Symptom | Wahrscheinliche Ursache | Untersuchung |
|---------|-------------|---------------|
| Langsame API-Antworten | N+1-Queries, fehlende Indizes, nicht optimierte Queries | Datenbank-Query-Log prüfen |
| Wachsender Speicherverbrauch | Geleakte Referenzen, unbegrenzte Caches, große Payloads | Heap-Snapshot analysieren |
| CPU-Spitzen | Synchrone aufwendige Berechnungen, Regex-Backtracking | CPU-Profiling |
| Hohe Latenz | Fehlendes Caching, redundante Berechnungen, Netzwerk-Hops | Requests durch den Stack tracen |

### Schritt 3: Den Engpass beheben

Behebe genau das eine, was Schritt 2 identifiziert hat, sonst nichts. Die folgenden Anti-Patterns sind die üblichen Verdächtigen; jeder Eintrag nennt die Regel und die Signatur, an der du es erkennst, und verlinkt auf einen ausgearbeiteten Fix in [references/optimization-patterns.md](references/optimization-patterns.md). Öffne den Eintrag, den du brauchst, wenn du bei diesem Code angekommen bist, nicht vorher.

**Backend**

- **N+1-Queries.** Eine Query pro Zeile ist der häufigste Backend-Engpass. Hole die Relation in derselben Query (join/include), statt in der Schleife. [Muster](references/optimization-patterns.md#n1-queries-backend).
- **Unbegrenztes Laden von Daten.** Jeder List-Endpoint paginiert mit einem Limit und stabiler Sortierung. [Muster](references/optimization-patterns.md#unbounded-data-fetching).
- **Queries, die ihren Index ignorieren.** „Index hinzufügen“ ist die Vermutung; `EXPLAIN ANALYZE` ist die Messung. Ein `Seq Scan`, wo du einen Index erwartet hast, eine um eine Größenordnung danebenliegende `rows=`-Schätzung und ein `Sort`-Knoten oberhalb des Scans verlangen jeweils einen anderen Fix; eine schlechte `rows=`-Schätzung bedeutet veraltete Statistiken, führe also `ANALYZE` aus, statt einen Index hinzuzufügen. Indiziere für die Form der Query (zuerst die Gleichheitsspalten, dann die Bereichs- oder Sortierspalte). Ein einfacher Index hilft nicht bei einer Query auf einen dominanten Wert mit niedriger Selektivität (ein partieller Index bedient den seltenen Wert), bei einem führenden Wildcard (braucht Trigram oder Volltext) oder bei einer auf die Spalte angewendeten Funktion (indiziere den Ausdruck, wie in `WHERE lower(email) = ?`), und jeder Index belastet jeden Schreibvorgang. Führe den Plan danach erneut aus; ein Index, der ihn nicht verändert hat, wird zurückgenommen. [Muster](references/optimization-patterns.md#queries-that-ignore-their-index).
- **Erschöpfter Connection-Pool.** Signatur: *Jeder* Endpoint wird gleichzeitig langsam, die Zeit geht ins Warten auf eine Verbindung statt ins Ausführen, und die Datenbank zeigt überwiegend inaktive Sessions. Ein Pool pro Prozess, so dimensioniert, dass `instances × max` unter dem Verbindungslimit der Datenbank bleibt. Größer ist nicht schneller; es verlagert die Warteschlange in die Datenbank, wo sie schwerer zu sehen ist. Bei unbegrenzter Instanzanzahl (Serverless, Autoscaling) multiplexe über einen Proxy (pgbouncer, RDS Proxy), statt `max` zu erhöhen. [Muster](references/optimization-patterns.md#connection-pool-exhaustion).
- **Fehlendes Caching.** Cache, was teuer zu erzeugen ist und weit häufiger gelesen als geändert wird; eine ohnehin schnelle Query zu cachen erkauft einen Netzwerk-Hop und einen Staleness-Bug für nichts. Wähle die Ebene bewusst (In-Process, geteilt, CDN). Jeder Input, der die Antwort verändert, gehört in den Key (Tenant, Locale, Berechtigungen, Feature-Flags): Ein Key, der den Betrachter auslässt, ist der Weg, auf dem die Daten eines Nutzers an einen anderen ausgeliefert werden. Wähle eine Invalidierungsstrategie (TTL, Event- oder Tag-basiert, versionierte Keys) und nenne das akzeptable Staleness-Fenster explizit. Schütze Hot Keys vor dem Stampede: liefere veraltete Daten aus, während ein Request neu berechnet, oder fasse gleichzeitige Misses hinter einem einzigen laufenden Promise zusammen. Cache nie, was aktuell sein muss (Kontostände, Berechtigungen, Lagerbestand beim Checkout). [Muster](references/optimization-patterns.md#missing-caching-backend); Request Coalescing, Schreibstrategien und Negative Caching stehen in `../../references/performance-checklist.md`.

**Frontend**

- **Fehlende Bildoptimierung.** Jedes Bild deklariert `width` und `height` (CLS). Das LCP-Bild bekommt `fetchpriority="high"`, moderne Formate (AVIF, WebP) über `<picture>` und `srcset`/`sizes` für die Auflösungsauswahl; Bilder unterhalb des sichtbaren Bereichs bekommen `loading="lazy"` und `decoding="async"`. [Muster](references/optimization-patterns.md#missing-image-optimization-frontend).
- **Unnötige Re-Renders.** Ein Objekt oder eine Funktion, die im Render erzeugt wird, ist jedes Mal eine neue Referenz und rendert jedes Kind neu, das sie erhält. Ziehe Konstanten heraus; hebe `React.memo` und `useMemo` für Arbeit auf, die laut Profil teuer ist, denn übermäßiger Einsatz hat seine eigenen Kosten. [Muster](references/optimization-patterns.md#unnecessary-re-renders-react).
- **Große Bundle-Größe.** Moderne Bundler tree-shaken benannte ESM-Imports von allein; die echten Gewinne liegen in Code Splitting auf Route-Ebene und im Lazy Loading aufwendiger, selten genutzter Features hinter `Suspense`. Profiliere, bevor du Import-Stile änderst. [Muster](references/optimization-patterns.md#large-bundle-size).

### Schritt 4: Verifizieren (behalten oder zurücknehmen)

Ein Fix ist eine Hypothese, bis du erneut gemessen hast. Dieser Schritt entscheidet, ob er überlebt.

**Miss so erneut, wie du die Baseline gemessen hast:** gleicher Befehl, gleiche Bedingungen, gleiches festes Budget (Wall-Clock-Zeit, Anzahl Samples oder Anzahl Requests). Eine Baseline mit kaltem Cache gegen ein Ergebnis mit warmem Cache misst den Cache, nicht deine Änderung.

**Ändere jeweils nur eine Sache.** Drei zusammen eingespielte Optimierungen liefern eine Zahl, und du kannst sie nicht zuordnen. Wenn sie zusammen ausgeliefert werden müssen, miss jede zuerst isoliert.

**Schlage das Rauschen, nicht nur den Mittelwert.** Wiederhole die Messung und vergleiche das Delta mit der Varianz zwischen den Läufen. Ein Gewinn von 3 % innerhalb von ±5 % Varianz ist kein Gewinn, sondern ein anderes Sample.

Entscheide dann strikt:

| Ergebnis vs. Baseline | Aktion |
|---|---|
| Über der Schwelle, Tests grün | **Behalten.** Commit mit den Vorher-/Nachher-Zahlen in der Nachricht. |
| Innerhalb des Rauschens (keine messbare Änderung) | **Zurücknehmen.** |
| Schlechter | **Zurücknehmen.** |
| Verbessert, aber ein Test ist rot geworden | **Zurücknehmen.** Eine Regression im Gewand eines Gewinns. |

**„Neutral“ bedeutet zurücknehmen, nicht behalten.** Diesen Schritt überspringen Teams: Die Änderung ist schon geschrieben, sie wegzuwerfen fühlt sich verschwenderisch an, also landet sie ungemessen im Code, und die Codebasis sammelt Komplexität an, die nie etwas gebracht hat. Code, den du behältst, pflegst du für immer. Sorge dafür, dass er sich selbst bezahlt macht.

**Korrektheit bestimmt die Metrik.** Die Suite bleibt grün *und* die Zahl bewegt sich. Eine „Optimierung“, die gewinnt, indem sie Arbeit weglässt, die das Produkt brauchte (eine Validierung überspringen, etwas cachen, das aktuell sein muss, ein tragendes `await` entfernen), ist eine Regression, kein Gewinn.

#### Protokolliere jeden Versuch, auch die zurückgenommenen

Zurückgenommene Arbeit hinterlässt keine Spur in der Git-Historie, und genau deshalb wird dieselbe tote Idee im nächsten Quartal erneut versucht. Führe ein kurzes Logbuch, damit eine verworfene Idee verworfen bleibt:

| Idee | Baseline → Ergebnis | Urteil | Begründung |
|---|---|---|---|
| Row-Komponente memoizen | INP 240ms → 235ms | zurückgenommen | Innerhalb des Rauschens (±15ms). Die Rows waren nicht der Engpass. |
| Liste virtualisieren | INP 240ms → 90ms | behalten | Long Tasks sind aus dem Trace verschwunden. |
| Preconnect zum API-Origin | LCP 2.8s → 2.8s | zurückgenommen | Ist bereits Same-Origin. |

Ein Abschnitt in der PR-Beschreibung oder eine `PERF.md` im Repo funktionieren beide. Entscheidend ist, dass die nächste Person (oder der nächste Agent) das liest, bevor sie ein Experiment vorschlägt, und keines wiederholt, das bereits fehlgeschlagen ist.

### Schritt 5: Gegen Regression absichern

Sichere die Metrik ab, die der Nutzer tatsächlich spürt, nicht jede verfügbare Zahl. Verwende denselben LCP, INP, p95-Latenz oder eine andere primäre Metrik, die den Fix gerechtfertigt hat.

Nutze zwei sich ergänzende Ebenen, wenn die Oberfläche nutzernah ist:

- **Synthetisches CI-Gate:** Fange reproduzierbare Regressionen vor dem merge mit einem Performance-Budget ab. Wiederhole verrauschte Messungen oder vergleiche einen Median/Trend, damit normale Varianz zwischen den Läufen das Gate nicht zu einem flaky Check macht.
- **Field-Monitoring:** Alarmiere bei einer bedeutsamen p75-Bewegung in den RUM-Daten. Nutze attribuierte `web-vitals`-Daten, um die Ursache zu lokalisieren; behandle das rollierende Fenster von CrUX als Bestätigung statt als sofortigen Alarm.

Wenn eine der beiden Absicherungen auslöst, kehre zu Schritt 1 zurück und stelle eine frische Baseline her, bevor du einen weiteren Fix vorschlägst.

**Lege Budgets fest und erzwinge sie:**

```
JavaScript bundle: < 200KB gzipped (initial load)
CSS: < 50KB gzipped
Images: < 200KB per image (above the fold)
Fonts: < 100KB total
API response time: < 200ms (p95)
Time to Interactive: < 3.5s on 4G
Lighthouse Performance score: ≥ 90
```

**In CI erzwingen:**
```bash
# Bundle size check
npx bundlesize --config bundlesize.config.json

# Lighthouse CI. The CLI package is @lhci/cli; unscoped `lhci` on npm is not it.
npx --package=@lhci/cli lhci autorun
```

## Siehe auch

Detaillierte Performance-Checklisten, Optimierungsbefehle und eine Anti-Pattern-Referenz findest du in `../../references/performance-checklist.md`.


## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Wir optimieren später“ | Performance-Schulden wachsen mit Zinseszins. Behebe offensichtliche Anti-Patterns jetzt, schiebe Mikro-Optimierungen auf. |
| „Auf meinem Rechner ist es schnell“ | Dein Rechner ist nicht der des Nutzers. Profiliere auf repräsentativer Hardware und in repräsentativen Netzwerken. |
| „Diese Optimierung ist offensichtlich“ | Wenn du nicht gemessen hast, weißt du es nicht. Profiliere zuerst. |
| „Nutzer merken 100ms nicht“ | Studien zeigen, dass Verzögerungen von 100ms die Conversion-Raten beeinflussen. Nutzer bemerken mehr, als du denkst. |
| „Das Framework kümmert sich um Performance“ | Frameworks verhindern manche Probleme, können aber keine N+1-Queries oder überdimensionierten Bundles beheben. |
| „Die Query ist langsam, füg einen Index hinzu“ | Lies zuerst den Plan. Der Index existiert womöglich schon und ist nicht nutzbar, und jeder Index belastet Schreibvorgänge für immer. |
| „Cach das einfach“ | Einen ohnehin billigen Aufruf zu cachen bringt nichts und fügt einen Staleness-Bug hinzu. Cache, was teuer ist *und* weit häufiger gelesen als geschrieben wird. |
| „Erhöh die Pool-Größe, uns gehen die Verbindungen aus“ | Ein Pool, der größer ist als die Datenbank bedienen kann, verlagert die Warteschlange an eine weniger sichtbare Stelle. Finde heraus, was die Verbindungen hält. |
| „Es hat nicht viel gebracht, schadet aber auch nicht“ | Neutrale Änderungen werden zurückgenommen. Du zahlst dafür dauerhaft Wartungsaufwand und hast nichts zurückbekommen. |
| „Wir haben es schon geschrieben, also können wir es auch behalten“ | Sunk Cost. Die Messung interessiert sich nicht dafür, wie lange das Schreiben der Änderung gedauert hat. |
| „Die Verbesserung ist offensichtlich, kein Grund neu zu messen“ | Dann ist das erneute Messen billig und belegt es. Ungemessene Gewinne sind der Weg, auf dem neutrale Komplexität landet. |

## Warnsignale

- Optimierung ohne Profiling-Daten, die sie rechtfertigen
- N+1-Query-Muster beim Laden von Daten
- Ein Index, der ohne Query-Plan davor und danach hinzugefügt wurde
- Ein Cache-Key, der einen Input auslässt, von dem die Antwort abhängt (Tenant, Locale, Betrachter)
- Ein Cache ohne angegebenes Staleness-Fenster und ohne Invalidierungsstrategie
- Connection-Pool-Größe wurde als Reaktion auf Erschöpfung erhöht, ohne herauszufinden, was die Verbindungen hält
- List-Endpoints ohne Pagination
- Bilder ohne Abmessungen, Lazy Loading oder responsive Größen
- Bundle-Größe wächst ohne Review
- Kein Performance-Monitoring in Produktion
- `React.memo` und `useMemo` überall (übermäßiger Einsatz ist genauso schlecht wie zu geringer)
- Optimierungen, die ohne rechtfertigende Neumessung behalten wurden
- Mehrere Optimierungen in einer Messung gebündelt, sodass sich keine einzelne Änderung zuordnen lässt
- Ein „Gewinn“, für den ein Test geändert, übersprungen oder gelöscht werden musste
- Derselbe fehlgeschlagene Optimierungsversuch wurde mehrfach unternommen, weil niemand den ersten Versuch festgehalten hat

## Verifikation

Nach jeder Performance-bezogenen Änderung:

- [ ] Messungen vorher und nachher liegen vor (konkrete Zahlen)
- [ ] Das Ergebnis wurde genauso neu gemessen wie die Baseline (gleicher Befehl, gleiche Bedingungen)
- [ ] Die Verbesserung übersteigt die Varianz zwischen den Läufen, nicht nur den Mittelwert
- [ ] Änderungen, die die Baseline nicht geschlagen haben, wurden zurückgenommen und nicht als neutral behalten
- [ ] Versuche sind protokolliert, behaltene wie zurückgenommene, damit eine tote Idee nicht erneut ausgeführt wird
- [ ] Der konkrete Engpass ist identifiziert und behoben
- [ ] Core Web Vitals liegen innerhalb der „Gut“-Schwellenwerte
- [ ] Die Bundle-Größe ist nicht wesentlich gewachsen
- [ ] Keine N+1-Queries im neuen Code zum Laden von Daten
- [ ] Jeder neue Index ist durch einen Query-Plan vorher und nachher begründet, und seine Schreibkosten wurden berücksichtigt
- [ ] Jeder neue Cache gibt an, worauf er keyt und wie er veraltet
- [ ] Die gemessene nutzernahe Metrik hat ein synthetisches Budget oder einen Field-Monitor, der Regressionen erkennen kann
- [ ] Bestehende Tests laufen weiterhin durch (die Optimierung hat das Verhalten nicht gebrochen)
