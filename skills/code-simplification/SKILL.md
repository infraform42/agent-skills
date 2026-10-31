---
name: code-simplification
description: "Vereinfacht Code ohne Verhaltensänderung (agent-skills). Nur verwenden, wenn der Nutzer /agent-skills-de:code-simplify aufruft oder diesen Skill ausdrücklich nennt. Im Alltag gilt der eingebaute Skill simplify."
---

# Code-Vereinfachung

> Inspiriert vom [Claude Code Simplifier plugin](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md). Hier angepasst als modellunabhängiger, prozessgetriebener Skill für jeden KI-Coding-Agenten.

## Überblick

Vereinfache Code, indem du die Komplexität reduzierst und das Verhalten exakt beibehältst. Ziel sind nicht weniger Zeilen, sondern Code, der sich leichter lesen, verstehen, ändern und debuggen lässt. Jede Vereinfachung muss einen einfachen Test bestehen: „Würde ein neues Teammitglied das schneller verstehen als das Original?"

## Wann verwenden

- Nachdem ein Feature funktioniert und die Tests grün sind, die Implementierung sich aber schwerer anfühlt als nötig
- Im Code-Review, wenn Lesbarkeits- oder Komplexitätsprobleme angemerkt werden
- Wenn du auf tief verschachtelte Logik, lange Funktionen oder unklare Namen stößt
- Beim Refaktorieren von Code, der unter Zeitdruck entstanden ist
- Wenn zusammengehörige Logik, die über mehrere Dateien verstreut ist, zusammengeführt werden soll
- Nach Merges, die Duplikate oder Inkonsistenzen eingeführt haben

**Wann NICHT verwenden:**

- Der Code ist bereits sauber und lesbar – vereinfache nicht um der Vereinfachung willen
- Du verstehst noch nicht, was der Code tut – erst verstehen, dann vereinfachen
- Der Code ist performancekritisch und die „einfachere" Version wäre messbar langsamer
- Du bist kurz davor, das Modul komplett neu zu schreiben – Wegwerf-Code zu vereinfachen ist verschwendeter Aufwand

## Die fünf Prinzipien

### 1. Verhalten exakt beibehalten

Ändere nicht, was der Code tut, sondern nur, wie er es ausdrückt. Alle Eingaben, Ausgaben, Seiteneffekte, das Fehlerverhalten und alle Randfälle müssen identisch bleiben. Wenn du nicht sicher bist, dass eine Vereinfachung das Verhalten erhält, nimm sie nicht vor.

```
ASK BEFORE EVERY CHANGE:
→ Does this produce the same output for every input?
→ Does this maintain the same error behavior?
→ Does this preserve the same side effects and ordering?
→ Do all existing tests still pass without modification?
```

### 2. Projektkonventionen befolgen

Vereinfachen heißt, Code konsistenter mit der Codebasis zu machen, nicht, externe Vorlieben durchzusetzen. Bevor du vereinfachst:

```
1. Read CLAUDE.md / project conventions
2. Study how neighboring code handles similar patterns
3. Match the project's style for:
   - Import ordering and module system
   - Function declaration style
   - Naming conventions
   - Error handling patterns
   - Type annotation depth
```

Eine Vereinfachung, die die Konsistenz im Projekt bricht, ist keine Vereinfachung, sondern Churn.

### 3. Klarheit vor Cleverness

Expliziter Code ist besser als kompakter Code, wenn die kompakte Version beim Lesen ein gedankliches Innehalten erfordert.

```typescript
// UNCLEAR: Dense ternary chain
const label = isNew ? 'New' : isUpdated ? 'Updated' : isArchived ? 'Archived' : 'Active';

// CLEAR: Readable mapping
function getStatusLabel(item: Item): string {
  if (item.isNew) return 'New';
  if (item.isUpdated) return 'Updated';
  if (item.isArchived) return 'Archived';
  return 'Active';
}
```

```typescript
// UNCLEAR: Chained reduces with inline logic
const result = items.reduce((acc, item) => ({
  ...acc,
  [item.id]: { ...acc[item.id], count: (acc[item.id]?.count ?? 0) + 1 }
}), {});

// CLEAR: Named intermediate step
const countById = new Map<string, number>();
for (const item of items) {
  countById.set(item.id, (countById.get(item.id) ?? 0) + 1);
}
```

### 4. Balance halten

Vereinfachung hat einen Fehlermodus: Übervereinfachung. Achte auf diese Fallen:

- **Zu aggressives Inlining** – wer einen Helper entfernt, der einem Konzept einen Namen gab, macht die Aufrufstelle schwerer lesbar
- **Unzusammenhängende Logik zusammenlegen** – zwei einfache Funktionen zu einer komplexen zu verschmelzen ist nicht einfacher
- **„Unnötige" Abstraktion entfernen** – manche Abstraktionen existieren für Erweiterbarkeit oder Testbarkeit, nicht aus Komplexität
- **Auf Zeilenzahl optimieren** – weniger Zeilen sind nicht das Ziel; leichteres Verständnis ist es

### 5. Auf das Geänderte beschränken

Vereinfache standardmäßig kürzlich geänderten Code. Vermeide Drive-by-Refactorings von unbeteiligtem Code, es sei denn, der Scope soll ausdrücklich erweitert werden. Unbegrenzte Vereinfachung erzeugt Rauschen in Diffs und riskiert unbeabsichtigte Regressionen.

## Der Vereinfachungsprozess

### Schritt 1: Erst verstehen, dann anfassen (Chesterton's Fence)

Bevor du etwas änderst oder entfernst, verstehe, warum es existiert. Das ist Chesterton's Fence: Wenn du einen Zaun quer über einer Straße siehst und nicht verstehst, warum er dort steht, reiß ihn nicht ein. Verstehe zuerst den Grund und entscheide dann, ob er noch gilt.

```
BEFORE SIMPLIFYING, ANSWER:
- What is this code's responsibility?
- What calls it? What does it call?
- What are the edge cases and error paths?
- Are there tests that define the expected behavior?
- Why might it have been written this way? (Performance? Platform constraint? Historical reason?)
- Check git blame: what was the original context for this code?
```

Wenn du diese Fragen nicht beantworten kannst, bist du noch nicht bereit zum Vereinfachen. Lies zuerst mehr Kontext.

### Schritt 2: Vereinfachungsmöglichkeiten identifizieren

Suche nach diesen Mustern – jedes ist ein konkretes Signal, kein vager Geruch:

**Strukturelle Komplexität:**

| Muster | Signal | Vereinfachung |
|--------|--------|---------------|
| Tiefe Verschachtelung (3+ Ebenen) | Kontrollfluss schwer nachzuvollziehen | Bedingungen in Guard Clauses oder Hilfsfunktionen auslagern |
| Lange Funktionen (50+ Zeilen) | Mehrere Verantwortlichkeiten | In fokussierte Funktionen mit aussagekräftigen Namen aufteilen |
| Verschachtelte Ternaries | Erfordern beim Lesen einen gedanklichen Stack | Durch if/else-Ketten, switch oder Lookup-Objekte ersetzen |
| Boolesche Parameter-Flags | `doThing(true, false, true)` | Durch Options-Objekte oder getrennte Funktionen ersetzen |
| Wiederholte Bedingungen | Dieselbe `if`-Prüfung an mehreren Stellen | In eine gut benannte Prädikat-Funktion extrahieren |

**Benennung und Lesbarkeit:**

| Muster | Signal | Vereinfachung |
|--------|--------|---------------|
| Generische Namen | `data`, `result`, `temp`, `val`, `item` | Umbenennen, sodass der Inhalt beschrieben wird: `userProfile`, `validationErrors` |
| Abgekürzte Namen | `usr`, `cfg`, `btn`, `evt` | Ganze Wörter verwenden, außer die Abkürzung ist allgemein üblich (`id`, `url`, `api`) |
| Irreführende Namen | Funktion namens `get`, die auch Zustand verändert | Umbenennen, sodass sie das tatsächliche Verhalten widerspiegelt |
| Kommentare, die das „Was" erklären | `// increment counter` über `count++` | Kommentar löschen – der Code ist klar genug |
| Kommentare, die das „Warum" erklären | `// Retry because the API is flaky under load` | Behalten – sie tragen Absicht, die der Code nicht ausdrücken kann |

**Redundanz:**

| Muster | Signal | Vereinfachung |
|--------|--------|---------------|
| Duplizierte Logik | Dieselben 5+ Zeilen an mehreren Stellen | In eine gemeinsame Funktion extrahieren |
| Toter Code | Unerreichbare Zweige, ungenutzte Variablen, auskommentierte Blöcke | Entfernen (nachdem du bestätigt hast, dass er wirklich tot ist) |
| Unnötige Abstraktionen | Wrapper ohne Mehrwert | Wrapper inlinen, die darunterliegende Funktion direkt aufrufen |
| Überengineerte Patterns | Factory für eine Factory, Strategy mit nur einer Strategie | Durch den einfachen, direkten Ansatz ersetzen |
| Redundante Typ-Assertions | Cast auf einen Typ, der ohnehin inferiert wird | Assertion entfernen |

### Schritt 3: Änderungen inkrementell anwenden

Nimm immer nur eine Vereinfachung auf einmal vor. Führe nach jeder Änderung die Tests aus. **Reiche Refactoring-Änderungen getrennt von Feature- oder Bugfix-Änderungen ein.** Ein PR, der refaktoriert und ein Feature hinzufügt, sind zwei PRs – teile sie auf.

```
FOR EACH SIMPLIFICATION:
1. Make the change
2. Run the test suite
3. If tests pass → commit (or continue to next simplification)
4. If tests fail → revert and reconsider
```

Bündle nicht mehrere Vereinfachungen in einer ungetesteten Änderung. Wenn etwas kaputtgeht, musst du wissen, welche Vereinfachung es verursacht hat.

**Die 500er-Regel:** Würde ein Refactoring mehr als 500 Zeilen berühren, investiere in Automatisierung (Codemods, sed-Skripte, AST-Transformationen), statt die Änderungen von Hand vorzunehmen. Manuelle Edits in diesem Umfang sind fehleranfällig und mühsam zu reviewen.

### Schritt 4: Das Ergebnis verifizieren

Tritt nach allen Vereinfachungen einen Schritt zurück und bewerte das Ganze:

```
COMPARE BEFORE AND AFTER:
- Is the simplified version genuinely easier to understand?
- Did you introduce any new patterns inconsistent with the codebase?
- Is the diff clean and reviewable?
- Would a teammate approve this change?
```

Wenn die „vereinfachte" Version schwerer zu verstehen oder zu reviewen ist, mach sie rückgängig. Nicht jeder Vereinfachungsversuch gelingt.

## Sprachspezifische Hinweise

### TypeScript / JavaScript

```typescript
// SIMPLIFY: Unnecessary async wrapper
// Before
async function getUser(id: string): Promise<User> {
  return await userService.findById(id);
}
// After
function getUser(id: string): Promise<User> {
  return userService.findById(id);
}

// SIMPLIFY: Verbose conditional assignment
// Before
let displayName: string;
if (user.nickname) {
  displayName = user.nickname;
} else {
  displayName = user.fullName;
}
// After
const displayName = user.nickname || user.fullName;

// SIMPLIFY: Manual array building
// Before
const activeUsers: User[] = [];
for (const user of users) {
  if (user.isActive) {
    activeUsers.push(user);
  }
}
// After
const activeUsers = users.filter((user) => user.isActive);

// SIMPLIFY: Redundant boolean return
// Before
function isValid(input: string): boolean {
  if (input.length > 0 && input.length < 100) {
    return true;
  }
  return false;
}
// After
function isValid(input: string): boolean {
  return input.length > 0 && input.length < 100;
}
```

### Python

```python
# SIMPLIFY: Verbose dictionary building
# Before
result = {}
for item in items:
    result[item.id] = item.name
# After
result = {item.id: item.name for item in items}

# SIMPLIFY: Nested conditionals with early return
# Before
def process(data):
    if data is not None:
        if data.is_valid():
            if data.has_permission():
                return do_work(data)
            else:
                raise PermissionError("No permission")
        else:
            raise ValueError("Invalid data")
    else:
        raise TypeError("Data is None")
# After
def process(data):
    if data is None:
        raise TypeError("Data is None")
    if not data.is_valid():
        raise ValueError("Invalid data")
    if not data.has_permission():
        raise PermissionError("No permission")
    return do_work(data)
```

### React / JSX

```tsx
// SIMPLIFY: Verbose conditional rendering
// Before
function UserBadge({ user }: Props) {
  if (user.isAdmin) {
    return <Badge variant="admin">Admin</Badge>;
  } else {
    return <Badge variant="default">User</Badge>;
  }
}
// After
function UserBadge({ user }: Props) {
  const variant = user.isAdmin ? 'admin' : 'default';
  const label = user.isAdmin ? 'Admin' : 'User';
  return <Badge variant={variant}>{label}</Badge>;
}

// SIMPLIFY: Prop drilling through intermediate components
// Before — consider whether context or composition solves this better.
// This is a judgment call — flag it, don't auto-refactor.
```

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Es funktioniert, da muss man nichts anfassen" | Funktionierender Code, der schwer lesbar ist, ist auch schwer zu reparieren, wenn er kaputtgeht. Jetzt zu vereinfachen spart bei jeder künftigen Änderung Zeit. |
| „Weniger Zeilen sind immer einfacher" | Ein verschachtelter Einzeiler-Ternary ist nicht einfacher als ein if/else über fünf Zeilen. Bei Einfachheit geht es um die Verständnisgeschwindigkeit, nicht um die Zeilenzahl. |
| „Ich vereinfache mal eben noch diesen unbeteiligten Code" | Unbegrenzte Vereinfachung erzeugt verrauschte Diffs und riskiert Regressionen in Code, den du gar nicht ändern wolltest. Bleib fokussiert. |
| „Die Typen dokumentieren sich selbst" | Typen dokumentieren Struktur, nicht Absicht. Eine gut benannte Funktion erklärt das *Warum* besser, als eine Typsignatur das *Was* erklärt. |
| „Diese Abstraktion könnte später nützlich sein" | Erhalte keine spekulativen Abstraktionen. Wird sie jetzt nicht genutzt, ist sie Komplexität ohne Mehrwert. Entferne sie und füge sie wieder hinzu, wenn sie gebraucht wird. |
| „Der ursprüngliche Autor muss einen Grund gehabt haben" | Vielleicht. Prüfe git blame – wende Chesterton's Fence an. Aber angesammelte Komplexität hat oft keinen Grund; sie ist nur der Rückstand von Iterationen unter Druck. |
| „Ich refaktoriere, während ich dieses Feature hinzufüge" | Trenne Refactoring von Feature-Arbeit. Vermischte Änderungen sind schwerer zu reviewen, zurückzunehmen und in der Historie nachzuvollziehen. |

## Warnsignale

- Eine Vereinfachung, für die Tests geändert werden müssen, damit sie durchlaufen (du hast vermutlich das Verhalten geändert)
- „Vereinfachter" Code, der länger und schwerer nachzuvollziehen ist als das Original
- Umbenennungen nach deinen Vorlieben statt nach Projektkonventionen
- Entfernen von Fehlerbehandlung, weil „der Code dadurch sauberer wird"
- Vereinfachen von Code, den du nicht vollständig verstehst
- Viele Vereinfachungen in einem großen, schwer zu reviewenden commit bündeln
- Refaktorieren von Code außerhalb des Scopes der aktuellen Aufgabe, ohne dass jemand darum gebeten hat

## Verifikation

Nach Abschluss eines Vereinfachungsdurchgangs:

- [ ] Alle bestehenden Tests laufen ohne Änderung durch
- [ ] Der Build ist erfolgreich und erzeugt keine neuen Warnungen
- [ ] Linter/Formatter laufen durch (keine Stil-Regressionen)
- [ ] Jede Vereinfachung ist eine reviewbare, inkrementelle Änderung
- [ ] Der Diff ist sauber – keine unbeteiligten Änderungen untergemischt
- [ ] Der vereinfachte Code folgt den Projektkonventionen (geprüft gegen CLAUDE.md oder Entsprechendes)
- [ ] Es wurde keine Fehlerbehandlung entfernt oder abgeschwächt
- [ ] Es wurde kein toter Code zurückgelassen (ungenutzte Imports, unerreichbare Zweige)
- [ ] Ein Teammitglied oder Review-Agent würde die Änderung als Nettoverbesserung freigeben
