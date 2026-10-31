---
description: Zerlegt Arbeit in kleine, verifizierbare Aufgaben mit Akzeptanzkriterien und Abhängigkeitsreihenfolge
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:planning-and-task-breakdown auf.

Lies die vorhandene Spec (SPEC.md oder Äquivalent) und die relevanten Abschnitte der Codebasis. Danach:

1. Wechsle in den Plan Mode — nur lesen, keine Codeänderungen
2. Ermittle den Abhängigkeitsgraphen zwischen den Komponenten
3. Zerlege die Arbeit vertikal in Scheiben (ein vollständiger Pfad pro Aufgabe, keine horizontalen Schichten)
4. Schreibe Aufgaben mit Akzeptanzkriterien und Verifikationsschritten
5. Füge Checkpoints zwischen den Phasen ein
6. Lege den Plan zur menschlichen Prüfung vor

Speichere den Plan in tasks/plan.md und die Aufgabenliste in tasks/todo.md.

Falls tasks/plan.md oder tasks/todo.md bereits mit offenen Aufgaben für andere Arbeit existiert, halte an und frage nach, bevor du schreibst — überschreibe einen unvollständigen Plan niemals stillschweigend.
