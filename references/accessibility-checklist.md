# Accessibility-Checkliste

Kurze Referenz für die Konformität mit WCAG 2.1 AA. Verwende sie zusammen mit dem Skill `frontend-ui-engineering`.

## Inhaltsverzeichnis

- [Wesentliche Prüfpunkte](#essential-checks)
- [Gängige HTML-Muster](#common-html-patterns)
- [Test-Tools](#testing-tools)
- [Kurzreferenz: ARIA Live Regions](#quick-reference-aria-live-regions)
- [Gängige Anti-Patterns](#common-anti-patterns)

## Essential Checks

### Keyboard Navigation
- [ ] Alle interaktiven Elemente sind per Tab-Taste fokussierbar
- [ ] Die Fokusreihenfolge folgt der visuellen bzw. logischen Reihenfolge
- [ ] Der Fokus ist sichtbar (Outline/Ring an fokussierten Elementen)
- [ ] Eigene Widgets unterstützen die Tastatur (Enter zum Aktivieren, Escape zum Schließen)
- [ ] Keine Tastaturfallen (Nutzer können per Tab immer aus einer Komponente herausspringen)
- [ ] Skip-to-content-Link am Seitenanfang – sichtbar (mindestens) bei Tastaturfokus
- [ ] Modale Dialoge halten den Fokus gefangen, solange sie offen sind, und geben ihn beim Schließen zurück

### Screen Readers
- [ ] Alle Bilder haben `alt`-Text (oder `alt=""` bei dekorativen Bildern)
- [ ] Alle Formularfelder haben zugeordnete Labels (`<label>` oder `aria-label`)
- [ ] Buttons und Links haben aussagekräftigen Text (nicht „Hier klicken“)
- [ ] Buttons nur mit Icon haben `aria-label`
- [ ] Die Seite hat genau ein `<h1>`, und Überschriften überspringen keine Ebenen
- [ ] Dynamische Inhaltsänderungen werden angekündigt (`aria-live`-Regionen)
- [ ] Tabellen haben `<th>`-Kopfzellen mit scope

### Visual
- [ ] Textkontrast ≥ 4,5:1 bei normalem Text bzw. ≥ 3:1 bei großem Text (mindestens 18 pt / 24 CSS-px, bei Fettdruck 14 pt / etwa 18,67 CSS-px). Runde ein nicht erreichtes Kontrastverhältnis nicht auf den Schwellenwert auf.
- [ ] Kontrast von UI-Komponenten ≥ 3:1 gegenüber dem Hintergrund
- [ ] Farbe ist nicht das einzige Mittel, um Informationen zu vermitteln
- [ ] Text lässt sich auf 200 % vergrößern, ohne das Layout zu zerstören
- [ ] Keine Inhalte, die öfter als dreimal pro Sekunde blinken

### Forms
- [ ] Jedes Eingabefeld hat ein sichtbares Label
- [ ] Pflichtfelder sind gekennzeichnet (nicht allein durch Farbe)
- [ ] Fehlermeldungen sind spezifisch und dem Feld zugeordnet
- [ ] Der Fehlerzustand ist nicht nur durch Farbe erkennbar (Icon, Text, Rahmen)
- [ ] Fehler beim Absenden des Formulars werden zusammengefasst und sind fokussierbar
- [ ] Bekannte Felder nutzen Autocomplete (zum Beispiel `type="email" autocomplete="email"`)

### Content
- [ ] Sprache ist deklariert (`<html lang="en">`)
- [ ] Die Seite hat einen aussagekräftigen `<title>`
- [ ] Links heben sich vom umgebenden Text ab (nicht allein durch Farbe)
- [ ] Touch-Ziele ≥ 44x44 px auf Mobilgeräten
- [ ] Sinnvolle Leerzustände (keine leeren Bildschirme)

## Common HTML Patterns

### Buttons vs. Links

```html
<!-- Use <button> for actions -->
<button onClick={handleDelete}>Delete Task</button>

<!-- Use <a> for navigation -->
<a href="/tasks/123">View Task</a>

<!-- NEVER use div/span as buttons -->
<div onClick={handleDelete}>Delete</div>  <!-- BAD -->
```

### Form Labels

```html
<!-- Explicit label association -->
<label for="email">Email address</label>
<input id="email" type="email" required />

<!-- Implicit wrapping -->
<label>
  Email address
  <input type="email" required />
</label>

<!-- Hidden label (visible label preferred) -->
<input type="search" aria-label="Search tasks" />
```

### ARIA Roles

```html
<!-- Navigation -->
<nav aria-label="Main navigation">...</nav>
<nav aria-label="Footer links">...</nav>

<!-- Status messages -->
<div role="status" aria-live="polite">Task saved</div>

<!-- Alert messages -->
<div role="alert">Error: Title is required</div>

<!-- Modal dialogs -->
<dialog aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Delete</h2>
  ...
</dialog>

<!-- Loading states -->
<div role="status" aria-busy="true" aria-label="Loading tasks">
  <Spinner />
</div>
```

### Accessible Lists

```html
<ul role="list" aria-label="Tasks">
  <li>
    <input type="checkbox" id="task-1" aria-label="Complete: Buy groceries" />
    <label for="task-1">Buy groceries</label>
  </li>
</ul>
```

## Testing Tools

```bash
# Automated audit
npx --package=@axe-core/cli axe http://localhost:3000
npx pa11y             # CLI accessibility checker

# In browser
# Chrome DevTools → Lighthouse → Accessibility
# Chrome DevTools → Elements → Accessibility tree

# Screen reader testing
# macOS: VoiceOver (Cmd + F5)
# Windows: NVDA (free) or JAWS
# Linux: Orca
```

## Quick Reference: ARIA Live Regions

| Wert | Verhalten | Verwendung für |
|-------|----------|---------|
| `aria-live="polite"` | Wird bei der nächsten Pause angekündigt | Statusmeldungen, Speicherbestätigungen |
| `aria-live="assertive"` | Wird sofort angekündigt | Fehler, zeitkritische Hinweise |
| `role="status"` | Wie `polite` | Statusmeldungen |
| `role="alert"` | Wie `assertive` | Fehlermeldungen |

## Common Anti-Patterns

| Anti-Pattern | Problem | Lösung |
|---|---|---|
| `div` als Button | Nicht fokussierbar, keine Tastaturunterstützung | `<button>` verwenden |
| Fehlender `alt`-Text | Bilder sind für Screen Reader unsichtbar | Aussagekräftiges `alt` ergänzen |
| Zustände nur durch Farbe | Für Farbenblinde unsichtbar | Icons, Text oder Muster ergänzen |
| Automatisch startende Medien | Irritierend, nicht stoppbar | Steuerelemente ergänzen, nicht automatisch abspielen |
| Eigenes Dropdown ohne ARIA | Per Tastatur/Screen Reader unbenutzbar | Natives `<select>` oder korrekte ARIA-Listbox verwenden |
| Fokus-Outlines entfernen | Nutzer sehen nicht, wo sie sind | Outlines gestalten, nicht entfernen |
| Leere Links/Buttons | „Link“ wird ohne Beschreibung angekündigt | Text oder `aria-label` ergänzen |
| `tabindex > 0` | Zerstört die natürliche Tab-Reihenfolge | Nur `tabindex="0"` oder `-1` verwenden |
