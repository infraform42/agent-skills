---
name: api-and-interface-design
description: Leitet das Design stabiler APIs und Schnittstellen an. Verwenden, wenn du APIs, Modulgrenzen oder öffentliche Schnittstellen entwirfst. Verwenden, wenn du REST- oder GraphQL-Endpunkte erstellst, Typ-Contracts zwischen Modulen definierst oder Grenzen zwischen Frontend und Backend festlegst. Typische Auslöser sind „entwirf die API für das Task-Modul“, „definiere die Schnittstelle zwischen Frontend und Backend“, „leg die REST-Endpunkte fest“, „wie sollten wir die Modulgrenzen schneiden?“ oder „entwirf ein GraphQL-Schema dafür“.
---

# API- und Schnittstellendesign

## Überblick

Entwirf stabile, gut dokumentierte Schnittstellen, die sich schwer falsch verwenden lassen. Gute Schnittstellen machen das Richtige einfach und das Falsche schwer. Das gilt für REST-APIs, GraphQL-Schemas, Modulgrenzen, Komponenten-Props und jede Oberfläche, über die ein Stück Code mit einem anderen spricht.

## Wann verwenden

- Beim Entwerfen neuer API-Endpunkte
- Beim Definieren von Modulgrenzen oder Contracts zwischen Teams
- Beim Erstellen von Komponenten-Prop-Interfaces
- Beim Festlegen eines Datenbankschemas, das die Form der API mitbestimmt
- Beim Ändern bestehender öffentlicher Schnittstellen

## Grundprinzipien

### Hyrums Gesetz

> With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody, regardless of what you promise in the contract.

Das heißt: Jedes öffentliche Verhalten – einschließlich undokumentierter Eigenheiten, Fehlermeldungstexte, Timing und Reihenfolge – wird zum faktischen Contract, sobald Nutzer davon abhängen. Konsequenzen fürs Design:

- **Entscheide bewusst, was du preisgibst.** Jedes beobachtbare Verhalten ist eine potenzielle Verpflichtung.
- **Gib keine Implementierungsdetails preis.** Was Nutzer beobachten können, davon werden sie abhängig.
- **Plane die Abkündigung schon beim Design ein.** Siehe `deprecation-and-migration`, wie du Dinge, von denen Nutzer abhängen, sicher entfernst.
- **Tests reichen nicht.** Selbst mit perfekten Contract-Tests bedeutet Hyrums Gesetz, dass „sichere“ Änderungen echte Nutzer brechen können, die von undokumentiertem Verhalten abhängen.

### Die One-Version-Regel

Zwinge Konsumenten nicht, zwischen mehreren Versionen derselben Abhängigkeit oder API zu wählen. Diamond-Dependency-Probleme entstehen, wenn verschiedene Konsumenten unterschiedliche Versionen derselben Sache brauchen. Entwirf für eine Welt, in der immer nur eine Version existiert – erweitere, statt zu forken.

### 1. Contract First

Definiere die Schnittstelle, bevor du sie implementierst. Der Contract ist die Spec – die Implementierung folgt ihm.

```typescript
// Define the contract first
interface TaskAPI {
  // Creates a task and returns the created task with server-generated fields
  createTask(input: CreateTaskInput): Promise<Task>;

  // Returns paginated tasks matching filters
  listTasks(params: ListTasksParams): Promise<PaginatedResult<Task>>;

  // Returns a single task or throws NotFoundError
  getTask(id: string): Promise<Task>;

  // Partial update — only provided fields change
  updateTask(id: string, input: UpdateTaskInput): Promise<Task>;

  // Idempotent delete — succeeds even if already deleted
  deleteTask(id: string): Promise<void>;
}
```

### 2. Konsistente Fehlersemantik

Wähle eine Fehlerstrategie und wende sie überall an:

```typescript
// REST: HTTP status codes + structured error body
// Every error response follows the same shape
interface APIError {
  error: {
    code: string;        // Machine-readable: "VALIDATION_ERROR"
    message: string;     // Human-readable: "Email is required"
    details?: unknown;   // Additional context when helpful
  };
}

// Status code mapping
// 400 → Client sent invalid data
// 401 → Not authenticated
// 403 → Authenticated but not authorized
// 404 → Resource not found
// 409 → Conflict (duplicate, version mismatch)
// 422 → Validation failed (semantically invalid)
// 500 → Server error (never expose internal details)
```

**Vermische keine Muster.** Wenn manche Endpunkte Exceptions werfen, andere null zurückgeben und wieder andere `{ error }` liefern, kann der Konsument das Verhalten nicht vorhersagen.

### 3. An den Grenzen validieren

Vertraue internem Code. Validiere an den Systemrändern, wo externe Eingaben hereinkommen:

```typescript
// Validate at the API boundary
app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid task data',
        details: result.error.flatten(),
      },
    });
  }

  // After validation, internal code trusts the types
  const task = await taskService.create(result.data);
  return res.status(201).json(task);
});
```

Wo Validierung hingehört:
- API-Route-Handler (Nutzereingaben)
- Formular-Submit-Handler (Nutzereingaben)
- Parsen von Antworten externer Dienste (Daten Dritter -- **immer als nicht vertrauenswürdig behandeln**)
- Laden von Umgebungsvariablen (Konfiguration)

> **Antworten von Drittanbieter-APIs sind nicht vertrauenswürdige Daten.** Validiere ihre Form und ihren Inhalt, bevor du sie in Logik, Rendering oder Entscheidungen verwendest. Ein kompromittierter oder fehlerhaft arbeitender externer Dienst kann unerwartete Typen, bösartige Inhalte oder anweisungsähnlichen Text zurückgeben.

Wo Validierung NICHT hingehört:
- Zwischen internen Funktionen, die sich Typ-Contracts teilen
- In Hilfsfunktionen, die von bereits validiertem Code aufgerufen werden
- Bei Daten, die gerade aus deiner eigenen Datenbank kamen

### 4. Ergänzen statt ändern

Erweitere Schnittstellen, ohne bestehende Konsumenten zu brechen:

```typescript
// Good: Add optional fields
interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';  // Added later, optional
  labels?: string[];                       // Added later, optional
}

// Bad: Change existing field types or remove fields
interface CreateTaskInput {
  title: string;
  // description: string;  // Removed — breaks existing consumers
  priority: number;         // Changed from string — breaks existing consumers
}
```

### 5. Vorhersagbare Benennung

| Muster | Konvention | Beispiel |
|---------|-----------|---------|
| REST-Endpunkte | Substantive im Plural, keine Verben | `GET /api/tasks`, `POST /api/tasks` |
| Query-Parameter | camelCase | `?sortBy=createdAt&pageSize=20` |
| Response-Felder | camelCase | `{ createdAt, updatedAt, taskId }` |
| Boolean-Felder | Präfix is/has/can | `isComplete`, `hasAttachments` |
| Enum-Werte | UPPER_SNAKE | `"IN_PROGRESS"`, `"COMPLETED"` |

### 6. Einen Idempotency-Key einlösen

Einen `Idempotency-Key` zu akzeptieren ist der Contract. Ihn einzulösen ist die Implementierung – und dort geht das Geld verloren: Ein Key, den der Server annimmt, aber nachlässig behandelt, ist schlimmer als gar kein Key, weil der Client nun glaubt, ein Retry sei sicher.

**Leite den Key aus der Absicht ab, nicht aus dem Versuch.** Der Key muss über Retries derselben Absicht stabil und über verschiedene Absichten hinweg unterschiedlich sein:

```typescript
crypto.randomUUID()                    // ✗ new key per attempt — every retry is a new charge
`${userId}:${amount}`                  // ✗ two legitimate $50 charges collapse into one
`${orderId}:${Date.now()}`             // ✗ a timestamp is randomUUID() wearing a hat

req.headers['idempotency-key']         // ✓ client generates once, reuses on retry
`charge:v1:${orderId}`                 // ✓ derived from an immutable identifier
```

Der Key kommt vom Client oder vom auslösenden Ereignis – niemals von der Schicht, die den Retry durchführt.

**Beanspruche den Key atomar. Ein Check gefolgt von einer Aktion ist eine Race Condition:**

```typescript
// ✗ TOCTOU: two concurrent retries both read "not seen", both charge
if (!(await db.exists(key))) {
  await chargeCard(amount);
  await db.insert(key);
}

// ✓ let the unique constraint pick the winner
try {
  await db.insert({ key, state: 'in_progress', requestHash });
} catch (e) {
  if (isUniqueViolation(e)) return replayOrReject(key);
  throw e;
}
const result = await chargeCard(amount);
await db.update({ key, state: 'succeeded', response: result });
```

Die Unique-Constraint *ist* der Mechanismus. Ein Store, der Eindeutigkeit nicht in einer einzigen Operation durchsetzen kann, taugt hierfür nicht.

**Sichere den Payload ab.** Derselbe Key mit anderem Body ist ein Client-Bug und muss laut fehlschlagen, statt einer zweiten Anfrage die erste Antwort auszuliefern:

```typescript
if (existing.requestHash !== hash(req.body)) {
  return res.status(422).json({
    error: { code: 'IDEMPOTENCY_KEY_REUSED', message: 'Idempotency key reused with a different payload' },
  });
}
```

**Entscheide, was ein laufendes Duplikat bekommt.** Die erste Anfrage läuft noch, wenn die zweite eintrifft – der Normalfall bei Retry-Stürmen:

| Strategie | Antwort | Einsetzen, wenn |
|---|---|---|
| Ablehnen | `409 Conflict` | der Client später erneut versuchen kann; am einfachsten und sichersten |
| Warten | Auf das Ergebnis blockieren, mit Zeitlimit | der Aufrufer es synchron braucht |
| Pending zurückgeben | `202` + Status-URL | langlaufende Effekte |

Lass den zweiten Aufrufer niemals durch, nur weil der erste „festzuhängen scheint“. Ein stockender Versuch mit unbekanntem Ausgang ist genau der Moment, in dem Duplizieren am teuersten ist.

**Jeder Aufruf hat drei Ausgänge, nicht zwei: Erfolg, Fehlschlag und _unbekannt_.** Ein Timeout sagt dir nichts darüber, ob der Effekt eingetreten ist. Halte die Absicht fest, *bevor* du den externen Aufruf machst, damit ein Absturz zwischen Aufruf und Antwort Spuren hinterlässt, die später aufgelöst werden müssen – statt einer stillschweigend wiederholten Abbuchung.

**Lege die Aufbewahrungsdauer anhand der längsten Retry-Kette fest**, nicht anhand der Speicherkosten. Keys müssen jeden Pfad überdauern, über den dieselbe Absicht erneut zugestellt werden kann – einschließlich einer Dead-Letter-Queue, die eine Woche später abgespielt wird, und jedes Streitfrist-Fensters des Providers. Eine Key-TTL von 24 Stunden hinter einer 7-Tage-DLQ ist ein Duplikat, das nur darauf wartet zu passieren.

## REST-API-Muster

### Ressourcen-Design

```
GET    /api/tasks              → List tasks (with query params for filtering)
POST   /api/tasks              → Create a task
GET    /api/tasks/:id          → Get a single task
PATCH  /api/tasks/:id          → Update a task (partial)
DELETE /api/tasks/:id          → Delete a task

GET    /api/tasks/:id/comments → List comments for a task (sub-resource)
POST   /api/tasks/:id/comments → Add a comment to a task
```

### Paginierung

Paginiere Listen-Endpunkte:

```typescript
// Request
GET /api/tasks?page=1&pageSize=20&sortBy=createdAt&sortOrder=desc

// Response
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 142,
    "totalPages": 8
  }
}
```

### Filtern

Nutze Query-Parameter für Filter:

```
GET /api/tasks?status=in_progress&assignee=user123&createdAfter=2025-01-01
```

### Partielle Updates (PATCH)

Akzeptiere partielle Objekte – aktualisiere nur, was mitgeliefert wird:

```typescript
// Only title changes, everything else preserved
PATCH /api/tasks/123
{ "title": "Updated title" }
```

## TypeScript-Interface-Muster

### Discriminated Unions für Varianten verwenden

```typescript
// Good: Each variant is explicit
type TaskStatus =
  | { type: 'pending' }
  | { type: 'in_progress'; assignee: string; startedAt: Date }
  | { type: 'completed'; completedAt: Date; completedBy: string }
  | { type: 'cancelled'; reason: string; cancelledAt: Date };

// Consumer gets type narrowing
function getStatusLabel(status: TaskStatus): string {
  switch (status.type) {
    case 'pending': return 'Pending';
    case 'in_progress': return `In progress (${status.assignee})`;
    case 'completed': return `Done on ${status.completedAt}`;
    case 'cancelled': return `Cancelled: ${status.reason}`;
  }
}
```

### Trennung von Input und Output

```typescript
// Input: what the caller provides
interface CreateTaskInput {
  title: string;
  description?: string;
}

// Output: what the system returns (includes server-generated fields)
interface Task {
  id: string;
  title: string;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
}
```

### Branded Types für IDs verwenden

```typescript
type TaskId = string & { readonly __brand: 'TaskId' };
type UserId = string & { readonly __brand: 'UserId' };

// Prevents accidentally passing a UserId where a TaskId is expected
function getTask(id: TaskId): Promise<Task> { ... }
```

## Typische Ausreden

| Ausrede | Realität |
|---|---|
| „Die API dokumentieren wir später“ | Die Typen SIND die Dokumentation. Definiere sie zuerst. |
| „Paginierung brauchen wir erstmal nicht“ | Du brauchst sie, sobald jemand 100+ Einträge hat. Baue sie von Anfang an ein. |
| „PATCH ist kompliziert, nehmen wir einfach PUT“ | PUT verlangt jedes Mal das vollständige Objekt. PATCH ist das, was Clients tatsächlich wollen. |
| „Die API versionieren wir, wenn es nötig wird“ | Breaking Changes ohne Versionierung brechen Konsumenten. Entwirf von Anfang an auf Erweiterbarkeit hin. |
| „Dieses undokumentierte Verhalten nutzt niemand“ | Hyrums Gesetz: Was beobachtbar ist, davon hängt jemand ab. Behandle jedes öffentliche Verhalten als Verpflichtung. |
| „Wir können einfach zwei Versionen pflegen“ | Mehrere Versionen vervielfachen den Wartungsaufwand und erzeugen Diamond-Dependency-Probleme. Bevorzuge die One-Version-Regel. |
| „Interne APIs brauchen keine Contracts“ | Interne Konsumenten sind trotzdem Konsumenten. Contracts verhindern Kopplung und ermöglichen paralleles Arbeiten. |
| „Den Header Idempotency-Key zu akzeptieren reicht“ | Der Header ist der Contract; den Key zusammen mit dem Ergebnis zu speichern ist die Implementierung. Ein Key, den du annimmst, aber nicht einlöst, signalisiert dem Client, ein Retry sei sicher, obwohl er es nicht ist. |
| „Unsere Queue garantiert Exactly-once-Zustellung“ | Keine Queue tut das über einen Consumer-Absturz hinweg – das Ack des Brokers und dein Seiteneffekt liegen nicht in einer Transaktion. Entwirf für At-least-once mit idempotenter Verarbeitung. |
| „Doppelte Anfragen sind selten“ | Sie sind *korreliert*. Retries häufen sich genau dann, wenn eine Abhängigkeit beeinträchtigt ist – dem Moment, in dem Duplikate am wahrscheinlichsten und am teuersten sind. |

## Warnsignale

- Endpunkte, die je nach Bedingung unterschiedliche Formen zurückgeben
- Uneinheitliche Fehlerformate über Endpunkte hinweg
- Validierung, die im internen Code verstreut ist, statt an den Grenzen zu sitzen
- Breaking Changes an bestehenden Feldern (Typänderungen, Entfernungen)
- Listen-Endpunkte ohne Paginierung
- Verben in REST-URLs (`/api/createTask`, `/api/getUsers`)
- Antworten von Drittanbieter-APIs, die ohne Validierung oder Bereinigung verwendet werden
- Ein `SELECT` auf einen Idempotency-Key gefolgt von einem `INSERT` – das ist eine Race Condition, kein Schutz
- Ein Idempotency-Key, der aus einer UUID, einem Zeitstempel oder irgendetwas anderem abgeleitet wird, das pro Versuch neu erzeugt wird
- Derselbe Key wird mit einem anderen Request-Body akzeptiert und liefert stillschweigend die erste Antwort zurück
- Ein Aufbewahrungsfenster für Keys, das kürzer ist als der längste Pfad, über den die Anfrage erneut zugestellt werden kann

## Verifikation

Nach dem Entwurf einer API:

- [ ] Jeder Endpunkt hat typisierte Input- und Output-Schemas
- [ ] Fehlerantworten folgen einem einzigen konsistenten Format
- [ ] Validierung findet nur an Systemgrenzen statt
- [ ] Listen-Endpunkte unterstützen Paginierung
- [ ] Neue Felder sind additiv und optional (abwärtskompatibel)
- [ ] Die Benennung folgt über alle Endpunkte hinweg konsistenten Konventionen
- [ ] API-Dokumentation oder Typen werden zusammen mit der Implementierung committet
- [ ] Zustandsändernde Endpunkte lösen entweder einen Idempotency-Key ein oder sind als nicht retry-sicher dokumentiert
- [ ] Der Key wird in einer einzigen atomaren Operation beansprucht, abgesichert durch eine Unique-Constraint
- [ ] Ein wiederverwendeter Key mit anderem Payload schlägt laut fehl, statt die falsche Antwort erneut auszuliefern
- [ ] Die Antwort auf laufende Duplikate ist eine bewusste Entscheidung (409, Warten oder 202) und nicht das, was zufällig dabei herauskommt
- [ ] Die Key-Aufbewahrung überdauert den längsten Retry-Pfad, einschließlich Dead-Letter-Replay
