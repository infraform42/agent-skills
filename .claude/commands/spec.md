---
description: Startet spec-driven development – schreibt eine strukturierte Spezifikation, bevor Code entsteht
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:spec-driven-development auf.

Beginne damit, zu verstehen, was der Nutzer bauen möchte. Stelle Rückfragen zu:
1. Ziel und Zielgruppe der Nutzer
2. Kernfunktionen und Akzeptanzkriterien
3. Präferenzen und Constraints beim Tech-Stack
4. Bekannte Grenzen (was immer zu tun ist, wobei zuerst nachgefragt werden soll und was nie getan werden darf)

Erstelle dann eine strukturierte Spec, die alle sechs Kernbereiche abdeckt: Ziel, Befehle, Projektstruktur, Code-Stil, Teststrategie und Grenzen.

Bündelt die Anfrage mehrere unabhängig testbare Fähigkeiten, schlage zuerst gemäß Phase 0 des Skills eine Capability Map vor (Modul-IDs, Abhängigkeitsrichtung, Build-Reihenfolge) und lasse sie freigeben. Schreibe anschließend für jedes Modul in Abhängigkeitsreihenfolge eine eigene Spec.

Speichere die Spec als SPEC.md im Projektstamm und lass sie vom Nutzer bestätigen, bevor du fortfährst.
