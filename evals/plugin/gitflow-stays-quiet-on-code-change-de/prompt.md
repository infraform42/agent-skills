---
description: Eine gewöhnliche Codeänderung auf Deutsch, ohne Bezug zu Commits, Branches oder Releases. Prüft die Fork-Eingrenzung von git-workflow-and-versioning, die nicht mehr bei jeder Codeänderung auslösen soll.
expected_outcome: Eine geänderte slug-Funktion, die Umlaute ersetzt; git-workflow-and-versioning wird nicht aufgerufen.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Ändere diese Funktion so, dass Umlaute zu ae, oe, ue und ss werden, bevor die übrigen Sonderzeichen entfernt werden. Gib mir nur die neue Fassung.

```js
export function slug(s) {
  return s.toLowerCase().replace(/ /g, "-").replace(/[^a-z0-9-]/g, "");
}
```
