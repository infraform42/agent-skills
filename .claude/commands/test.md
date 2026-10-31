---
description: Führt den TDD-Workflow aus – fehlschlagende Tests schreiben, implementieren, verifizieren. Bei Bugs gilt das Prove-It-Muster.
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:test-driven-development auf.

Für neue Features:
1. Schreibe Tests, die das erwartete Verhalten beschreiben (sie sollten FEHLSCHLAGEN)
2. Implementiere den Code so, dass die Tests bestehen
3. Refaktoriere, während die Tests grün bleiben

Für Bugfixes (Prove-It-Muster):
1. Schreibe einen Test, der den Bug reproduziert (muss FEHLSCHLAGEN)
2. Bestätige, dass der Test fehlschlägt
3. Implementiere den Fix
4. Bestätige, dass der Test besteht
5. Führe die gesamte Test-Suite aus, um Regressionen zu erkennen

Bei browserbezogenen Problemen rufe zusätzlich agent-skills-de:browser-testing-with-devtools auf, um mit dem Chrome DevTools MCP zu verifizieren.
