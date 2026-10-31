# Optimierungsmuster

Ausgearbeitete Lösungen für die Anti-Patterns aus Schritt 3 des Skills `performance-optimization`. Der Skill nennt die Regel und die Signatur, nach der du suchst; diese Datei zeigt jeweils eine konkrete Umsetzung. Öffne den Abschnitt, den du brauchst, nachdem Schritt 2 den Engpass identifiziert hat – sie ist nicht dafür gedacht, von oben nach unten gelesen zu werden.

Checklisten, Messbefehle, TTFB-Diagnose und Lese-/Schreibstrategien für Caching findest du in `../../../references/performance-checklist.md`.

## N+1-Queries (Backend)

```typescript
// BAD: N+1 — one query per task for the owner
const tasks = await db.tasks.findMany();
for (const task of tasks) {
  task.owner = await db.users.findUnique({ where: { id: task.ownerId } });
}

// GOOD: Single query with join/include
const tasks = await db.tasks.findMany({
  include: { owner: true },
});
```

## Unbegrenztes Laden von Daten

```typescript
// BAD: Fetching all records
const allTasks = await db.tasks.findMany();

// GOOD: Paginated with limits
const tasks = await db.tasks.findMany({
  take: 20,
  skip: (page - 1) * 20,
  orderBy: { createdAt: 'desc' },
});
```

## Queries, die ihren Index ignorieren

„Einen Index anlegen“ ist die Vermutung. Der Query-Plan ist die Messung:

```sql
EXPLAIN ANALYZE
SELECT id, title FROM tasks
WHERE owner_id = 42 ORDER BY created_at DESC LIMIT 20;
```

Drei Dinge in der Ausgabe entscheiden über die Lösung:

| Was du siehst | Was es bedeutet |
|---|---|
| `Seq Scan` auf einer großen Tabelle, obwohl du einen Index erwartet hast | Kein nutzbarer Index für dieses Prädikat |
| Geschätztes `rows=` weicht um eine Größenordnung vom tatsächlichen Wert ab | Veraltete Statistiken; der Planner entscheidet auf Basis schlechter Informationen |
| Ein `Sort`-Knoten oberhalb des Scans | Der Index deckt den Filter ab, aber nicht das `ORDER BY` |

Lege den Index für die **Form der Query** an, nicht für die einzelne Spalte. In einem zusammengesetzten Index stehen die Gleichheitsspalten zuerst, danach die Bereichs- oder Sortierspalte:

```sql
CREATE INDEX idx_tasks_owner_created ON tasks (owner_id, created_at DESC);
```

**Wenn ein Index nicht hilft:**

| Situation | Grund |
|---|---|
| Geringe Selektivität, Abfrage des dominanten Werts (eine `status`-Spalte, die zu 95 % `active` ist, gefiltert auf `active`) | Ein Sequential Scan ist tatsächlich günstiger; der Planner ignoriert den Index. Beim Filtern auf den seltenen Wert ist es umgekehrt, und ein partieller Index bedient ihn gut |
| Führendes Wildcard (`LIKE '%term'`) | Ein B-Tree kann ohne Präfix nicht gezielt suchen; es braucht Trigram oder Volltext |
| Funktion auf der Spalte (`WHERE lower(email) = ?`) | Der einfache Spaltenindex ist unbrauchbar; indiziere stattdessen den Ausdruck |
| Schreiblastige Tabelle | Jeder Index belastet jedes `INSERT`/`UPDATE`; miss die Schreibkosten, nicht nur den Lesegewinn |

Führe danach erneut `EXPLAIN ANALYZE` aus. Ein Index, der den Plan nicht verändert hat, ist ein Revert (Schritt 4) – und er ist nicht kostenlos: Er kostet weiterhin bei jedem Schreibzugriff.

## Erschöpfter Connection-Pool

Die Signatur ist eindeutig: **Alle** Endpoints werden gleichzeitig langsam, die Zeit geht fürs Warten auf eine Verbindung statt fürs Ausführen drauf, und die Datenbank meldet überwiegend inaktive Sessions.

```typescript
// BAD: a pool per request or per module — under serverless this multiplies
// by instance count and exhausts the database's connection limit
// GOOD: one pool per process, sized against the database's ceiling
const pool = new Pool({
  max: 10,                        // instances × max must stay under max_connections
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000, // fail fast instead of queueing forever
});
```

**Größer ist nicht schneller.** Ein Pool, der größer ist als das, was die Datenbank gleichzeitig ausführen kann, verlagert die Warteschlange nur von deiner App in die Datenbank, wo sie schwerer zu sehen ist. Wenn die Anzahl der Instanzen unbegrenzt ist (Serverless, Autoscaling), ist ein Proxy, der Verbindungen bündelt (pgbouncer, RDS Proxy), die Lösung – nicht ein höheres `max`.

## Fehlende Bildoptimierung (Frontend)

```html
<!-- BAD: No dimensions, no format optimization -->
<img src="/hero.jpg" />

<!-- GOOD: Hero / LCP image — art direction + resolution switching, high priority -->
<!--
  Two techniques combined:
  - Art direction (media): different crop/composition per breakpoint
  - Resolution switching (srcset + sizes): right file size per screen density
-->
<picture>
  <!-- Mobile: portrait crop (8:10) -->
  <source
    media="(max-width: 767px)"
    srcset="/hero-mobile-400.avif 400w, /hero-mobile-800.avif 800w"
    sizes="100vw"
    width="800"
    height="1000"
    type="image/avif"
  />
  <source
    media="(max-width: 767px)"
    srcset="/hero-mobile-400.webp 400w, /hero-mobile-800.webp 800w"
    sizes="100vw"
    width="800"
    height="1000"
    type="image/webp"
  />
  <!-- Desktop: landscape crop (2:1) -->
  <source
    srcset="/hero-800.avif 800w, /hero-1200.avif 1200w, /hero-1600.avif 1600w"
    sizes="(max-width: 1200px) 100vw, 1200px"
    width="1200"
    height="600"
    type="image/avif"
  />
  <source
    srcset="/hero-800.webp 800w, /hero-1200.webp 1200w, /hero-1600.webp 1600w"
    sizes="(max-width: 1200px) 100vw, 1200px"
    width="1200"
    height="600"
    type="image/webp"
  />
  <img
    src="/hero-desktop.jpg"
    width="1200"
    height="600"
    fetchpriority="high"
    alt="Hero image description"
  />
</picture>

<!-- GOOD: Below-the-fold image — lazy loaded + async decoding -->
<img
  src="/content.webp"
  width="800"
  height="400"
  loading="lazy"
  decoding="async"
  alt="Content image description"
/>
```

## Unnötige Re-Renders (React)

```tsx
// BAD: Creates new object on every render, causing children to re-render
function TaskList() {
  return <TaskFilters options={{ sortBy: 'date', order: 'desc' }} />;
}

// GOOD: Stable reference
const DEFAULT_OPTIONS = { sortBy: 'date', order: 'desc' } as const;
function TaskList() {
  return <TaskFilters options={DEFAULT_OPTIONS} />;
}

// Use React.memo for expensive components
const TaskItem = React.memo(function TaskItem({ task }: Props) {
  return <div>{/* expensive render */}</div>;
});

// Use useMemo for expensive computations
function TaskStats({ tasks }: Props) {
  const stats = useMemo(() => calculateStats(tasks), [tasks]);
  return <div>{stats.completed} / {stats.total}</div>;
}
```

## Zu große Bundle-Größe

```typescript
// Modern bundlers (Vite, webpack 5+) handle named imports with tree-shaking automatically,
// provided the dependency ships ESM and is marked `sideEffects: false` in package.json.
// Profile before changing import styles — the real gains come from splitting and lazy loading.

// GOOD: Dynamic import for heavy, rarely-used features
const ChartLibrary = lazy(() => import('./ChartLibrary'));

// GOOD: Route-level code splitting wrapped in Suspense
const SettingsPage = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <SettingsPage />
    </Suspense>
  );
}
```

## Fehlendes Caching (Backend)

Cache, was aufwendig zu erzeugen ist und viel häufiger gelesen als geändert wird. Wer eine Query cacht, die ohnehin schnell war, handelt sich einen Netzwerk-Hop, einen Staleness-Bug und eine zu pflegende Eviction-Policy ein – und bekommt dafür nichts.

**Wähle die Ebene bewusst:**

| Ebene | Sichtbar für | Einsatz, wenn | Kosten |
|---|---|---|---|
| In-Process (`Map`, LRU) | Eine Instanz | Klein, häufig genutzt, Staleness pro Instanz ist akzeptabel | Jede Instanz driftet unabhängig; die Invalidierung erreicht nur eine |
| Shared (Redis, Memcached) | Alle Instanzen | Instanzen müssen sich einig sein, oder der Wert ist teuer neu zu berechnen | Ein Netzwerk-Hop und ein weiterer Dienst, der betrieben und überwacht werden muss |
| CDN / Edge | Alle, pro URL | Antworten sind öffentlich und für einen gegebenen Key identisch | Die Invalidierung ist der schwierige Teil; geh davon aus, dass du eine fehlerhafte Antwort nicht schnell zurückholen kannst |

```typescript
// Cache frequently-read, rarely-changed data
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
let cachedConfig: AppConfig | null = null;
let cacheExpiry = 0;

async function getAppConfig(): Promise<AppConfig> {
  if (cachedConfig && Date.now() < cacheExpiry) {
    return cachedConfig;
  }
  cachedConfig = await db.config.findFirst();
  cacheExpiry = Date.now() + CACHE_TTL;
  return cachedConfig;
}

// HTTP caching headers for static assets
app.use('/static', express.static('public', {
  maxAge: '1y',           // Cache for 1 year
  immutable: true,        // Never revalidate (use content hashing in filenames)
}));

// Cache-Control for API responses
res.set('Cache-Control', 'public, max-age=300'); // 5 minutes
```

**Das Key-Design entscheidet über die Korrektheit.** Jede Eingabe, die die Antwort verändert, gehört in den Key: Tenant, Locale, Berechtigungen, Feature-Flags. Ein Key ohne den Betrachter ist der Weg, auf dem Daten eines Nutzers an einen anderen ausgeliefert werden – und das geht dann als Performance-Gewinn live.

**Wähle eine Invalidierungsstrategie, nicht drei:**

| Strategie | Trade-off |
|---|---|
| TTL | Am einfachsten. Du akzeptierst Staleness bis zur Dauer der TTL, also lege das akzeptable Zeitfenster explizit fest |
| Event- oder Tag-basiert | Beim Schreiben aktuell, aber Schreibende müssen jetzt die Cache-Topologie kennen |
| Versionierte Keys (`user:42:profile:v7`) | Nie invalidieren, einfach alte Keys nicht mehr lesen. Kostet Speicher bis zur Eviction |

**Schütze dich vor dem Stampede.** Ein häufig genutzter Key läuft ab, alle gleichzeitigen Requests verfehlen den Cache gemeinsam, und der Origin bekommt die volle Last auf einmal – so wird aus einem Cache ein Ausfall statt dessen Vermeidung. Liefere veraltete Daten aus, während ein einzelner Request neu berechnet (`stale-while-revalidate`), oder bündle gleichzeitige Misses hinter einem einzigen laufenden Promise, sodass N Wartende nur eine Neuberechnung auslösen.

**Nicht cachen:** alles, dessen Staleness ein Korrektheitsfehler ist (Kontostände, Berechtigungen, Lagerbestand beim Checkout), sowie nutzerspezifische Daten unter einem Key, der den Nutzer nicht identifiziert. Request Coalescing, Schreibstrategien, Negative Caching und die Cache-Checkliste findest du unter `../../../references/performance-checklist.md#caching-strategies`.
