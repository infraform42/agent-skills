---
description: Führt ein Code-Review über fünf Achsen durch – Korrektheit, Lesbarkeit, Architektur, Sicherheit, Performance
disable-model-invocation: true
---

Rufe den Skill agent-skills-de:code-review-and-quality auf.

Prüfe die aktuellen Änderungen (staged oder letzte commits) anhand aller fünf Achsen:

1. **Korrektheit** — Entspricht es der Spec? Sind Randfälle abgedeckt? Sind die Tests ausreichend?
2. **Lesbarkeit** — Klare Namen? Nachvollziehbare Logik? Gut strukturiert?
3. **Architektur** — Folgt es den bestehenden Mustern? Saubere Grenzen? Passende Abstraktionsebene?
4. **Sicherheit** — Eingaben validiert? Secrets geschützt? Authentifizierung geprüft? (Nutze den Skill security-and-hardening)
5. **Performance** — Keine N+1-Queries? Keine unbegrenzten Operationen? (Nutze den Skill performance-optimization)

Ordne die Befunde als Critical, Required, Optional oder Nit ein.
Gib ein strukturiertes Review mit konkreten file:line-Referenzen und Empfehlungen zur Behebung aus.
