---
description: Vereinfacht Code für mehr Klarheit und Wartbarkeit — reduziert Komplexität, ohne das Verhalten zu ändern
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:code-simplification auf.

Vereinfache kürzlich geänderten Code (oder den angegebenen Bereich) und erhalte dabei exakt das Verhalten:

1. Lies CLAUDE.md und arbeite dich in die Projektkonventionen ein
2. Bestimme den Zielcode — kürzliche Änderungen, sofern kein größerer Bereich angegeben ist
3. Verstehe Zweck, Aufrufer, Randfälle und Testabdeckung des Codes, bevor du ihn anfasst
4. Suche nach Vereinfachungsmöglichkeiten:
   - Tiefe Verschachtelung → Guard Clauses oder ausgelagerte Hilfsfunktionen
   - Lange Funktionen → nach Verantwortlichkeit aufteilen
   - Verschachtelte Ternary-Ausdrücke → if/else oder switch
   - Generische Namen → aussagekräftige Namen
   - Duplizierte Logik → gemeinsame Funktionen
   - Toter Code → nach Bestätigung entfernen
5. Wende jede Vereinfachung schrittweise an — führe nach jeder Änderung die Tests aus
6. Prüfe, dass alle Tests bestehen, der Build erfolgreich ist und der Diff sauber ist

Wenn Tests nach einer Vereinfachung fehlschlagen, mache diese Änderung rückgängig und überdenke sie. Nutze `code-review-and-quality`, um das Ergebnis zu reviewen.
