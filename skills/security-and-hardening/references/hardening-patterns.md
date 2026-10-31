# Härtungsmuster

Code-Patterns und Entscheidungshilfen für den Skill `security-and-hardening`. Der Skill nennt jede Regel; diese Datei zeigt eine konkrete Umsetzung dazu. Öffne den Abschnitt, den du brauchst, wenn du an der betreffenden Stelle im Code angekommen bist – die Datei ist nicht dafür gedacht, von oben nach unten durchgelesen zu werden.

Gemeinsame Checklisten (Threat Modeling, Pre-commit-Prüfungen, Security-Header, CORS, Package-Manager-Matrix, Install-Script-Gate und die OWASP-Kurzreferenztabellen) befinden sich in `../../../references/security-checklist.md`.

## Präventionsmuster für die OWASP Top 10

Das sind Präventionsmuster, kein Ranking. Die Reihenfolge von 2021 findest du in der Kurzreferenztabelle in `../../../references/security-checklist.md#owasp-top-10-quick-reference`.

### Injection

```typescript
// BAD: SQL injection via string concatenation
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// GOOD: Parameterized query
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// GOOD: ORM with parameterized input
const user = await prisma.user.findUnique({ where: { id: userId } });
```

### Broken Authentication

```typescript
// Password hashing
import { hash, compare } from 'bcrypt';

const SALT_ROUNDS = 12;
const hashedPassword = await hash(plaintext, SALT_ROUNDS);
const isValid = await compare(plaintext, hashedPassword);

// Session management
app.use(session({
  secret: process.env.SESSION_SECRET,  // From environment, not code
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,     // Not accessible via JavaScript
    secure: true,       // HTTPS only
    sameSite: 'lax',    // CSRF protection
    maxAge: 24 * 60 * 60 * 1000,  // 24 hours
  },
}));
```

### Cross-Site Scripting (XSS)

```typescript
// BAD: Rendering user input as HTML
element.innerHTML = userInput;

// GOOD: Use framework auto-escaping (React does this by default)
return <div>{userInput}</div>;

// If you MUST render HTML, sanitize first
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

### Broken Access Control

```typescript
// Always check authorization, not just authentication
app.patch('/api/tasks/:id', authenticate, async (req, res) => {
  const task = await taskService.findById(req.params.id);
  if (!task) {
    return res.status(404).json({
      error: { code: 'NOT_FOUND', message: 'Task not found' }
    });
  }

  // Check that the authenticated user owns this resource
  if (task.ownerId !== req.user.id) {
    return res.status(403).json({
      error: { code: 'FORBIDDEN', message: 'Not authorized to modify this task' }
    });
  }

  // Proceed with update
  const updated = await taskService.update(req.params.id, req.body);
  return res.json(updated);
});
```

### Security Misconfiguration

```typescript
// Security headers (use helmet for Express)
import helmet from 'helmet';
app.use(helmet());

// Content Security Policy
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],  // Tighten if possible
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'"],
  },
}));

// CORS — restrict to known origins
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true,
}));
```

### Sensitive Data Exposure

```typescript
// Never return sensitive fields in API responses
function sanitizeUser(user: UserRecord): PublicUser {
  const { passwordHash, resetToken, ...publicFields } = user;
  return publicFields;
}

// Use environment variables for secrets
const API_KEY = process.env.STRIPE_API_KEY;
if (!API_KEY) throw new Error('STRIPE_API_KEY not configured');
```

### Server-Side Request Forgery (SSRF)

Sobald der Server eine URL abruft, die der Nutzer beeinflusst hat – Webhooks, „Import von URL“, Bild-Proxys, Link-Vorschauen –, kann ein Angreifer ihn auf interne Dienste lenken (Cloud-Metadaten, `localhost`, private IPs).

```typescript
// BAD: fetch whatever the user gives you
await fetch(req.body.webhookUrl);

// GOOD: allowlist scheme + host, reject if ANY resolved IP is private, forbid redirects
import { lookup } from 'node:dns/promises';
import ipaddr from 'ipaddr.js';

const ALLOWED_HOSTS = new Set(['hooks.example.com']);

async function assertSafeUrl(raw: string): Promise<URL> {
  const url = new URL(raw);
  if (url.protocol !== 'https:') throw new Error('https only');
  if (!ALLOWED_HOSTS.has(url.hostname)) throw new Error('host not allowed');
  // Resolve ALL records; a single private/reserved address fails the check.
  const addrs = await lookup(url.hostname, { all: true });
  if (addrs.some((a) => ipaddr.parse(a.address).range() !== 'unicast')) {
    throw new Error('private/reserved IP');
  }
  return url;
}

await fetch(await assertSafeUrl(req.body.webhookUrl), { redirect: 'error' });
```

Die Prüfung `range() !== 'unicast'` deckt Loopback, Link-Local `169.254.169.254` (Cloud-Metadaten, das SSRF-Ziel Nr. 1), private sowie Unique-Local-Bereiche in IPv4 und IPv6 ab.

**Einschränkung – hier bleibt eine TOCTOU-Lücke.** `fetch` löst DNS nach der Prüfung erneut auf. Ein Angreifer mit einem Record mit kurzer TTL kann daher zwischen Validierung und Verbindungsaufbau auf eine interne IP umschwenken (DNS-Rebinding). Löse bei Angriffsflächen mit hohem Risiko einmal auf und verbinde dich mit der fixierten IP, oder schalte einen filternden Agent davor (`request-filtering-agent` / `ssrf-req-filter`).

## Muster für die Eingabevalidierung

### Schema-Validierung an den Grenzen

```typescript
import { z } from 'zod';

const CreateTaskSchema = z.object({
  title: z.string().max(200).trim().min(1),
  description: z.string().max(2000).optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  dueDate: z.string().datetime().optional(),
});

// Validate at the route handler
app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
        details: result.error.flatten(),
      },
    });
  }
  // result.data is now typed and validated
  const task = await taskService.create(result.data);
  return res.status(201).json(task);
});
```

### Sicherheit bei Datei-Uploads

```typescript
// Restrict file types and sizes
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

function validateUpload(file: UploadedFile) {
  if (!ALLOWED_TYPES.includes(file.mimetype)) {
    throw new ValidationError('File type not allowed');
  }
  if (file.size > MAX_SIZE) {
    throw new ValidationError('File too large (max 5MB)');
  }
  // Don't trust the file extension — check magic bytes if critical
}
```

### Destruktive Operationen auf abgeleiteten Pfaden

Ein Löschen, Verschieben oder Überschreiben ist nur so sicher wie der Wert, der sein Ziel benennt. Dass du diesen Wert vom Kernel, aus einem Job-Payload oder von einem Nachbardienst liest, beweist nur, *woher er kam* – nicht, *wer ihn geschrieben hat*: Die Kommandozeile eines anderen Prozesses ist genauso angreiferkontrolliert wie ein Formularfeld. Eine Formprüfung („absoluter Pfad, mindestens ein Verzeichnis tief“) belegt nur die Wohlgeformtheit und wird fälschlich für eine Autorisierung gehalten – so löscht eine Cleanup-Routine die Wurzel statt des Blatts.

Verlange vor einem destruktiven Aufruf alle drei Bedingungen: Das aufgelöste Ziel liegt unter einer **Root auf der Allowlist** (vergleiche nach dem Auflösen von Symlinks, nie auf dem rohen String); es liegt mindestens eine Ebene **unterhalb** dieser Root, sodass eine Root nie selbst das Ziel ist; und es trägt einen **Nachweis, dass es dir gehört**, der *vor* der Operation und vor jedem Teardown gelesen wird, der ihn entfernt – sonst sind „nicht vorhanden“ und „nicht meins“ nicht zu unterscheiden. Protokolliere bei einer Ablehnung das abgelehnte Ziel und brich ab: Ein Cleanup, der auf einen breiteren Standardpfad zurückfällt, ist genau der Fehler, den diese Prüfung verhindern soll. Ein durchgespieltes Beispiel steht in `../../../references/security-checklist.md#destructive-path-operations`.

Zwei Einschränkungen, weil die Prüfung stärker wirkt, als sie ist. Ein Marker im Verzeichnisbaum ist Selbstbeglaubigung – wer dort schreiben kann, kann auch den Marker schreiben –, daher muss der erwartete Eigentümer aus authentifiziertem Zustand stammen, und der Marker braucht Integritätsschutz (restriktive Eigentümerschaft oder einen MAC), bevor er als Autorisierung zählt. Und einen Pfad aufzulösen und dann auf dem *Namen* zu operieren, ist überall dort ein Check/Use-Race, wo ein nicht vertrauenswürdiger Prozess einen übergeordneten Ordner austauschen kann: Halte das Ziel auf einem geteilten Volume per Descriptor fest und nutze No-Follow-Operationen, die unterhalb der Root bleiben – oder stelle sicher, dass sich die Hierarchie für die Dauer nicht ändern kann.

## Triage von Dependency-Audits

Audits des Package-Managers melden bekannte Advisories; sie beweisen weder, dass ein Paket vertrauenswürdig ist, noch, dass verwundbarer Code erreichbar ist. Nutze diesen Entscheidungsbaum:

```
The native package-manager audit reports a vulnerability
├── Severity: critical or high
│   ├── Is the vulnerable code reachable in runtime, build, test, or deployment paths?
│   │   ├── YES --> Fix immediately (update, patch, or replace the dependency)
│   │   └── NO (confirmed unused across those paths) --> Fix soon, but not a blocker
│   └── Is a fix available?
│       ├── YES --> Update to the patched version
│       └── NO --> Check for workarounds, consider replacing the dependency, or add to allowlist with a review date
├── Severity: moderate
│   ├── Reachable in production? --> Fix in the next release cycle
│   └── Dev-only? --> Fix when convenient, track in backlog
└── Severity: low
    └── Track and fix during regular dependency updates
```

**Schlüsselfragen:**
- Wird die verwundbare Funktion in deinem Codepfad tatsächlich aufgerufen?
- Ist die Dependency eine Laufzeit-Dependency oder nur für die Entwicklung?
- Ist die Schwachstelle in deinem Deployment-Kontext ausnutzbar (z. B. eine serverseitige Schwachstelle in einer reinen Client-App)?

Wenn du einen Fix aufschiebst, dokumentiere den Grund und setze ein Review-Datum.

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

// General API rate limit
app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
}));

// Stricter limit for auth endpoints
app.use('/api/auth/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,  // 10 attempts per 15 minutes
}));
```

**Zähle in einem gemeinsamen Store, sobald mehr als ein Prozess läuft.** `express-rate-limit` hält seine Zähler standardmäßig im Prozessspeicher. Hinter einem Load Balancer führt jede Instanz ihren eigenen Zähler, das effektive Limit beträgt also `max × instances`; auf Serverless- oder Edge-Runtimes startet jeder frische Aufruf bei null, sodass das Auth-Limit oben womöglich nie greift. Übergib einen gemeinsamen `store` (Redis über `rate-limit-redis`) oder nutze einen HTTP-basierten Limiter, der dort funktioniert, wo eine langlebige TCP-Verbindung nicht möglich ist (zum Beispiel `@upstash/ratelimit`):

```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const authLimiter = new Ratelimit({
  redis: Redis.fromEnv(),                       // UPSTASH_REDIS_REST_URL + _TOKEN
  limiter: Ratelimit.slidingWindow(10, '15 m'), // 10 attempts per 15 minutes, across all instances
});
const { success } = await authLimiter.limit(`login:${req.ip}`);
if (!success) return res.status(429).end();
```

## Secrets-Management

```
.env files:
  ├── .env.example  → Committed (template with placeholder values)
  ├── .env          → NOT committed (contains real secrets)
  └── .env.local    → NOT committed (local overrides)

.gitignore must include:
  .env
  .env.local
  .env.*.local
  *.pem
  *.key
```

**Prüfe immer vor dem commit:**
```bash
# Check for accidentally staged secrets — prints only the names of files whose
# staged diff matches, so the raw value never lands in terminal output or agent
# tool logs. Any output means review those files before committing.
git diff --cached -i -G'password|secret|api_key|token' --name-only
```

**Wenn ein Secret jemals committed wurde, rotiere es.** Die Zeile zu löschen oder die Historie umzuschreiben reicht nicht – geh davon aus, dass es kompromittiert ist, sobald es ein Remote erreicht. Widerrufe den Schlüssel zuerst und stelle einen neuen aus, dann entferne ihn aus der Historie.

## Datenklassifizierung

Klassifiziere personenbezogene Daten, sobald du Felder hinzufügst, damit Export- und Löschanfragen sie später finden:

| Klasse | Beispiele | Umgang |
|---|---|---|
| **Nicht personenbezogen** | Aggregate, anonymisierte Zählwerte | Normaler Umgang |
| **Personenbezogen (PII)** | Name, E-Mail, IP, Geräte-/Nutzer-IDs | Minimieren, Zugriff beschränken, in Export/Löschung einbeziehen |
| **Sensibel** | Gesundheit, Finanzen, Standort, Biometrie, amtliche IDs, alles über Minderjährige | Zusätzliche Rechtsgrundlage für die Erhebung, strengerer Zugriff, oft Verschlüsselung + Audit-Logging |

## Umgang mit LLM-Ausgaben

```typescript
// BAD: trusting model output as a command or as markup
const sql = await llm.generate(`Write SQL for: ${userQuestion}`);
await db.query(sql);                                   // arbitrary query execution
container.innerHTML = await llm.reply(userMessage);   // stored XSS, via the model

// GOOD: model output is data — parse defensively, then validate, then encode
let intent;
try {
  intent = CommandSchema.parse(JSON.parse(await llm.replyJson(userMessage)));
} catch {
  throw new ValidationError('unexpected model output'); // JSON.parse or schema failed
}
await runAllowlistedAction(intent.action, intent.params);
container.textContent = await llm.reply(userMessage);
```
