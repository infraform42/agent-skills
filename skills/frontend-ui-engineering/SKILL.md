---
name: frontend-ui-engineering
description: Baut produktionsreife, barrierefreie und responsive Benutzeroberflächen. Verwenden, wenn Oberflächen und Seiten gebaut oder geändert, Komponenten erstellt, Layouts umgesetzt, WCAG-Barrierefreiheitsanforderungen erfüllt oder State verwaltet werden oder wenn das Ergebnis nach Produktion statt nach KI-Generat aussehen und sich so anfühlen soll. Auch bei „baue die Komponente für die Aufgabenliste“, „mach das Layout responsive“, „die Seite muss barrierefrei sein“, „die UI sieht zu sehr nach KI aus“.
---

# Frontend UI Engineering

## Überblick

Baue produktionsreife Benutzeroberflächen, die barrierefrei, performant und optisch sauber ausgearbeitet sind. Ziel ist eine UI, die aussieht, als hätte ein designbewusster Engineer bei einem Top-Unternehmen sie gebaut – nicht, als wäre sie von einer KI generiert worden. Das heißt: echte Einhaltung des Design Systems, saubere Barrierefreiheit, durchdachte Interaktionsmuster und keine generische „KI-Ästhetik“.

## Wann verwenden

- Neue UI-Komponenten oder Seiten bauen
- Bestehende nutzerseitige Oberflächen ändern
- Responsive Layouts umsetzen
- Interaktivität oder State-Management hinzufügen
- Visuelle oder UX-Probleme beheben

## Komponentenarchitektur

### Dateistruktur

Lege alles, was zu einer Komponente gehört, am selben Ort ab:

```
src/components/
  TaskList/
    TaskList.tsx          # Component implementation
    TaskList.test.tsx     # Tests
    TaskList.stories.tsx  # Storybook stories (if using)
    use-task-list.ts      # Custom hook (if complex state)
    types.ts              # Component-specific types (if needed)
```

### Komponentenmuster

**Bevorzuge Komposition gegenüber Konfiguration:**

```tsx
// Good: Composable
<Card>
  <CardHeader>
    <CardTitle>Tasks</CardTitle>
  </CardHeader>
  <CardBody>
    <TaskList tasks={tasks} />
  </CardBody>
</Card>

// Avoid: Over-configured
<Card
  title="Tasks"
  headerVariant="large"
  bodyPadding="md"
  content={<TaskList tasks={tasks} />}
/>
```

**Halte Komponenten fokussiert:**

```tsx
// Good: Does one thing
export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className="flex items-center gap-3 p-3">
      <Checkbox checked={task.done} onChange={() => onToggle(task.id)} />
      <span className={task.done ? 'line-through text-muted' : ''}>{task.title}</span>
      <Button variant="ghost" size="sm" onClick={() => onDelete(task.id)}>
        <TrashIcon />
      </Button>
    </li>
  );
}
```

**Trenne Datenabruf von Darstellung:**

```tsx
// Container: handles data
export function TaskListContainer() {
  const { tasks, isLoading, error, refetch, toggleTask, deleteTask } = useTasks();

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="Failed to load tasks" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="No tasks yet" />;

  return <TaskList tasks={tasks} onToggle={toggleTask} onDelete={deleteTask} />;
}

// Presentation: handles rendering
export function TaskList({ tasks, onToggle, onDelete }: { tasks: Task[] } & Pick<TaskItemProps, 'onToggle' | 'onDelete'>) {
  return (
    <ul role="list" className="divide-y">
      {tasks.map(task => <TaskItem key={task.id} task={task} onToggle={onToggle} onDelete={onDelete} />)}
    </ul>
  );
}
```

## State-Management

**Wähle den einfachsten Ansatz, der funktioniert:**

```
Local state (useState)           → Component-specific UI state
Lifted state                     → Shared between 2-3 sibling components
Context                          → Theme, auth, locale (read-heavy, write-rare)
URL state (searchParams)         → Filters, pagination, shareable UI state
Server state (React Query, SWR)  → Remote data with caching
Global store (Zustand, Redux)    → Complex client state shared app-wide
```

**Vermeide Prop Drilling über mehr als 3 Ebenen.** Wenn du Props durch Komponenten reichst, die sie selbst nicht verwenden, führe Context ein oder strukturiere den Komponentenbaum um.

## Einhaltung des Design Systems

### Referenzgeleitete UI-Qualität

Wenn das Produkt eine eigenständige visuelle Richtung braucht, sammle Belege, bevor du ein Layout wählst:

1. Durchsuche einen vertrauenswürdigen Referenzkatalog oder nutze Referenzen des Produktteams.
2. Analysiere zwei oder drei relevante Screens. Halte Entscheidungen zu Hierarchie, Dichte, Navigation, Bedienelementen, responsivem Verhalten und Interaktionszuständen fest.
3. Überführe diese Entscheidungen vor der Implementierung in einen kurzen Design-Vertrag. Benenne die Aufgabe des Screens, die primäre Aktion, die erforderlichen Zustände, die responsiven Regeln und die Muster, die du ablehnst.
4. Baue die nützliche Struktur mit den eigenen Komponenten, Tokens, Inhalten und der visuellen Sprache des Produkts nach. Kopiere nie Branding, proprietäre Texte, Bildmaterial oder das exakte Layout eines anderen Produkts.

Nutze Referenzen als Beleg, nicht als Vorlage. Sind keine Referenzen verfügbar, dokumentiere die Annahmen und prüfe das Ergebnis gegen das bestehende Design System des Produkts.

### Vermeide die KI-Ästhetik

KI-generierte UI hat wiedererkennbare Muster. Vermeide sie alle:

| KI-Standard | Warum das ein Problem ist | Produktionsqualität |
|---|---|---|
| Alles in Violett/Indigo | Modelle greifen standardmäßig zu optisch „sicheren“ Paletten, wodurch jede App gleich aussieht | Die tatsächliche Farbpalette des Projekts verwenden |
| Übermäßige Verläufe | Verläufe erzeugen visuelles Rauschen und beißen sich mit den meisten Design Systems | Flache oder dezente Verläufe passend zum Design System |
| Alles abgerundet (rounded-2xl) | Maximale Rundung signalisiert „freundlich“, ignoriert aber die Hierarchie der Eckenradien in echten Designs | Konsistenter border-radius aus dem Design System |
| Generische Hero-Sections | Template-getriebenes Layout ohne Bezug zum tatsächlichen Inhalt oder Nutzerbedarf | Inhaltsorientierte Layouts |
| Lorem-ipsum-artige Texte | Platzhaltertext verdeckt Layoutprobleme, die echter Inhalt aufdeckt (Länge, Umbruch, Overflow) | Realistische Platzhalterinhalte |
| Überdimensioniertes Padding überall | Gleichmäßig großzügiges Padding zerstört die visuelle Hierarchie und verschwendet Bildschirmfläche | Konsistente Abstandsskala |
| Standard-Karten-Raster | Uniforme Raster sind eine Layout-Abkürzung, die Informationspriorität und Scan-Muster ignoriert | Zweckgetriebene Layouts |
| Schattenlastiges Design | Gestapelte Schatten erzeugen Tiefe, die mit dem Inhalt konkurriert und auf schwachen Geräten das Rendering verlangsamt | Dezente oder keine Schatten, sofern das Design System nichts anderes vorgibt |

### Abstände und Layout

Verwende eine konsistente Abstandsskala. Erfinde keine Werte:

```css
/* Use the scale: 0.25rem increments (or whatever the project uses) */
/* Good */  padding: 1rem;      /* 16px */
/* Good */  gap: 0.75rem;       /* 12px */
/* Bad */   padding: 13px;      /* Not on any scale */
/* Bad */   margin-top: 2.3rem; /* Not on any scale */
```

### Typografie

Respektiere die Typografie-Hierarchie:

```
h1 → Page title (one per page)
h2 → Section title
h3 → Subsection title
body → Default text
small → Secondary/helper text
```

Überspringe keine Überschriftenebenen. Verwende Überschriftenstile nicht für Inhalte, die keine Überschriften sind.

### Farbe

- Verwende semantische Farb-Tokens: `text-primary`, `bg-surface`, `border-default` – keine rohen Hex-Werte
- Stelle ausreichenden Kontrast sicher (4,5:1 für normalen Text, 3:1 für großen Text)
- Verlass dich nicht allein auf Farbe, um Informationen zu vermitteln (nutze zusätzlich Icons, Text oder Muster)

## Barrierefreiheit (WCAG 2.1 AA)

Jede Komponente muss diese Standards erfüllen:

### Tastaturnavigation

```tsx
// Every interactive element must be keyboard accessible
<button onClick={handleClick}>Click me</button>        // ✓ Focusable by default
<div onClick={handleClick}>Click me</div>               // ✗ Not focusable
<div role="button" tabIndex={0} onClick={handleClick}    // ✓ But prefer <button>
     onKeyDown={e => {
       if (e.key === 'Enter') handleClick();
       if (e.key === ' ') e.preventDefault();
     }}
     onKeyUp={e => {
       if (e.key === ' ') handleClick();
     }}>
  Click me
</div>
```

### ARIA-Labels

```tsx
// Label interactive elements that lack visible text
<button aria-label="Close dialog"><XIcon /></button>

// Label form inputs
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// Or use aria-label when no visible label exists
<input aria-label="Search tasks" type="search" />
```

### Fokusverwaltung

```tsx
// Move focus when content changes
function Dialog({ isOpen, onClose }: DialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) closeRef.current?.focus();
  }, [isOpen]);

  // Trap focus inside dialog when open
  return (
    <dialog open={isOpen}>
      <button ref={closeRef} onClick={onClose}>Close</button>
      {/* dialog content */}
    </dialog>
  );
}
```

### Aussagekräftige Leer- und Fehlerzustände

```tsx
// Don't show blank screens
function TaskList({ tasks, onCreateTask }: { tasks: Task[]; onCreateTask: () => void }) {
  if (tasks.length === 0) {
    return (
      <div role="status" className="text-center py-12">
        <TasksEmptyIcon className="mx-auto h-12 w-12 text-muted" />
        <h3 className="mt-2 text-sm font-medium">No tasks</h3>
        <p className="mt-1 text-sm text-muted">Get started by creating a new task.</p>
        <Button className="mt-4" onClick={onCreateTask}>Create Task</Button>
      </div>
    );
  }

  return <ul role="list">...</ul>;
}
```

## Responsive Design

Entwirf zuerst für Mobilgeräte (Mobile First) und erweitere dann:

```tsx
// Tailwind: mobile-first responsive
<div className="
  grid grid-cols-1      /* Mobile: single column */
  sm:grid-cols-2        /* Small: 2 columns */
  lg:grid-cols-3        /* Large: 3 columns */
  gap-4
">
```

Teste bei diesen Breakpoints: 320px, 768px, 1024px, 1440px.

## Laden und Übergänge

```tsx
// Skeleton loading (not spinners for content)
function TaskListSkeleton() {
  return (
    <div className="space-y-3" role="status" aria-busy="true" aria-label="Loading tasks">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-12 bg-muted animate-pulse rounded" />
      ))}
    </div>
  );
}

// Optimistic updates for perceived speed
function useToggleTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData(['tasks']);

      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(t => t.id === taskId ? { ...t, done: !t.done } : t)
      );

      return { previous };
    },
    onError: (_err, _taskId, context) => {
      queryClient.setQueryData(['tasks'], context?.previous);
    },
  });
}
```

## Siehe auch

Detaillierte Anforderungen an die Barrierefreiheit und Testwerkzeuge findest du in `../../references/accessibility-checklist.md`.

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Barrierefreiheit ist nur ein Nice-to-have“ | In vielen Rechtsordnungen ist sie eine gesetzliche Pflicht und zugleich ein Qualitätsstandard der Softwareentwicklung. |
| „Responsive machen wir später“ | Responsive Design nachzurüsten ist dreimal so aufwendig, wie es von Anfang an einzubauen. |
| „Das Design ist noch nicht final, also überspringe ich das Styling“ | Nutze die Standardwerte des Design Systems. Eine ungestylte UI hinterlässt bei Reviewern einen kaputten ersten Eindruck. |
| „Das ist nur ein Prototyp“ | Prototypen werden zu Produktionscode. Baue das Fundament richtig. |
| „Die KI-Ästhetik reicht für den Moment“ | Sie signalisiert niedrige Qualität. Verwende von Anfang an das tatsächliche Design System des Projekts. |

## Warnsignale

- Komponenten mit mehr als 200 Zeilen (aufteilen)
- Inline-Styles oder beliebige Pixelwerte
- Fehlende Fehler-, Lade- oder Leerzustände
- Keine Tests der Tastaturnavigation
- Farbe als einziger Indikator für einen Zustand (Rot/Grün ohne Text oder Icons)
- Generischer „KI-Look“ (violette Verläufe, überdimensionierte Karten, Standard-Layouts)

## Verifikation

Nach dem Bauen der UI:

- [ ] Komponente rendert ohne Konsolenfehler
- [ ] Alle interaktiven Elemente sind per Tastatur bedienbar (mit Tab durch die Seite navigieren)
- [ ] Ein Screenreader kann Inhalt und Struktur der Seite vermitteln
- [ ] Responsive: funktioniert bei 320px, 768px, 1024px, 1440px
- [ ] Lade-, Leer-, Fehler-, Erfolgs- und Berechtigungszustände sind behandelt, sofern zutreffend
- [ ] Folgt dem Design System des Projekts (Abstände, Farben, Typografie)
- [ ] Das gerenderte Ergebnis besteht ein abschließendes UI-spezifisches Finish-Gate-Review
- [ ] Keine Barrierefreiheitswarnungen in den Dev-Tools oder in axe-core
