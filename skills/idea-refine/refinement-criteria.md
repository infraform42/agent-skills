# Kriterien für Verfeinerung & Bewertung

Nutze diese Bewertungsmatrix in Phase 2 (Evaluate & Converge), um Ideenrichtungen auf die Probe zu stellen. Nicht jedes Kriterium trifft auf jede Idee zu – entscheide nach Ermessen, welche Dimensionen im jeweiligen Kontext am wichtigsten sind.

## Zentrale Bewertungsdimensionen

### 1. Nutzerwert

Die wichtigste Dimension. Wenn der Wert nicht klar ist, spielt alles andere keine Rolle.

**Painkiller vs. Vitamin:**
- **Painkiller:** Löst ein akutes, häufiges Problem. Nutzer suchen aktiv danach. Sie wechseln von ihrer bisherigen Lösung. Anzeichen: Menschen beschreiben das Problem emotional, haben Workarounds gebaut und würden für eine Lösung zahlen.
- **Vitamin:** Nice-to-have. Macht etwas nur marginal besser. Nutzer nehmen dafür keine Umwege in Kauf. Anzeichen: Menschen nicken höflich, sagen „klingt cool“ und ändern dann ihr Verhalten nicht.

**Fragen, die du stellen solltest:**
- Kannst du 3 konkrete Personen nennen, die dieses Problem gerade jetzt haben?
- Was tun sie heute stattdessen? (Der eigentliche Wettbewerber ist immer der aktuelle Workaround.)
- Würden sie von ihrem bisherigen Vorgehen wechseln? Was würde sie zum Wechsel bewegen?
- Wie oft stoßen sie auf dieses Problem? (Tägliche Probleme > monatliche Probleme)
- Ist das ein „Pull“-Problem (Nutzer fragen danach) oder ein „Push“-Problem (du denkst, sie sollten es wollen)?

**Warnsignale:**
- „Das kann jeder gebrauchen“ – wenn du keinen konkreten Nutzer nennen kannst, ist der Wert unklar
- „Wie X, nur besser“ – marginale Verbesserungen treiben selten die Adoption
- Das Problem ist real, aber selten – hohe Intensität bei niedriger Frequenz rechtfertigt selten ein Produkt

### 2. Machbarkeit

Kannst du das tatsächlich bauen? Nicht nur technisch, sondern auch praktisch.

**Technische Machbarkeit:**
- Existiert die Kerntechnologie und funktioniert sie zuverlässig?
- Was ist das schwierigste technische Problem? Ist es ein bekanntermaßen schwieriges oder ein neuartiges?
- Gibt es Abhängigkeiten von Dritten, APIs oder Datenquellen, die du nicht kontrollierst?
- Welcher Tech-Stack ist mindestens nötig? (Lautet die Antwort „ein ziemlich großer“, ist das ein Signal.)

**Machbarkeit der Ressourcen:**
- Welches Team bzw. welcher Aufwand ist für einen MVP mindestens nötig?
- Erfordert es Spezialwissen, das du nicht hast?
- Gibt es regulatorische, rechtliche oder Compliance-Anforderungen?

**Time-to-Value:**
- Wie schnell kannst du Nutzern etwas vorlegen?
- Gibt es eine Version, die in Tagen oder Wochen statt Monaten Wert liefert?
- Was ist der kritische Pfad? Was muss zuerst passieren?

**Warnsignale:**
- „Wir müssen nur erst [sehr schweres Forschungsproblem] lösen“
- Mehrere Abhängigkeiten, die alle gleichzeitig funktionieren müssen
- Der MVP erfordert immer noch monatelange Arbeit – vermutlich nicht minimal genug

### 3. Differenzierung

Was macht das wirklich anders? Nicht besser – *anders*.

**Fragen, die du stellen solltest:**
- Wenn ein Nutzer das einem Freund beschreibt, was würde er sagen? Ist diese Beschreibung überzeugend?
- Was ist das eine, das dies kann und nichts anderes? (Wenn du nichts nennen kannst, ist das ein Problem.)
- Ist diese Differenzierung dauerhaft? Kann ein Wettbewerber sie in einer Woche kopieren?
- Ist der Unterschied etwas, das Nutzern tatsächlich wichtig ist, oder nur etwas, das Entwickler interessant finden?

**Arten der Differenzierung (von stark nach schwach):**
1. **Neue Fähigkeit:** Leistet etwas, das zuvor unmöglich war
2. **10x-Verbesserung:** So viel besser in einer zentralen Dimension, dass sich das Verhalten ändert
3. **Neue Zielgruppe:** Bringt eine bestehende Fähigkeit zu Menschen, die bisher ausgeschlossen waren
4. **Neuer Kontext:** Funktioniert in Situationen, in denen bestehende Lösungen versagen
5. **Bessere UX:** Dieselbe Fähigkeit, aber ein drastisch einfacheres Erlebnis
6. **Günstiger:** Dasselbe, nur zu geringeren Kosten (am schwächsten – wird leicht wegkonkurriert)

**Warnsignale:**
- Die Differenzierung liegt ausschließlich in der Technologie, nicht in der User Experience
- „Wir sind schneller/günstiger/hübscher“ ohne strukturellen Grund dafür
- Das differenzierende Feature ist nicht das Feature, das Nutzern am wichtigsten ist

## Annahmen-Audit

Liste für jede Ideenrichtung die Annahmen explizit in drei Kategorien auf:

### Must Be True (Dealbreaker)
Annahmen, die die Idee komplett kippen, wenn sie falsch sind. Diese müssen vor dem Bauen validiert werden.

Beispiel: „Nutzer geben uns ihre Daten“ – wenn sie es nicht tun, funktioniert das gesamte Produkt nicht.

### Should Be True (wichtig)
Annahmen, die den Erfolg erheblich beeinflussen, die Idee aber nicht kippen. Du kannst den Ansatz anpassen, wenn sie falsch sind.

Beispiel: „Nutzer bevorzugen Self-Service gegenüber dem Gespräch mit einer Person“ – wenn das nicht stimmt, brauchst du eine andere Go-to-Market-Strategie, aber das Kernprodukt kann trotzdem funktionieren.

### Might Be True (Nice-to-have)
Annahmen über sekundäre Features oder Optimierungen. Validiere diese erst, wenn der Kern bewiesen ist.

Beispiel: „Nutzer möchten ihre Ergebnisse mit Teamkollegen teilen“ – ein Wachstums-Feature, kein zentrales Wertversprechen.

## Entscheidungsrahmen

Wenn du zwischen Richtungen wählst, ordne sie in dieser Matrix ein:

|                    | Hohe Machbarkeit  | Niedrige Machbarkeit |
|--------------------|-------------------|----------------------|
| **Hoher Wert**     | Zuerst angehen    | Das Risiko wert      |
| **Niedriger Wert** | Nur wenn trivial  | Nicht angehen        |

Nutze dann die Differenzierung als Tiebreaker zwischen Optionen im selben Quadranten.

## Prinzipien für das MVP-Scoping

Beim Festlegen des MVP-Umfangs für die gewählte Richtung:

1. **Eine Aufgabe, richtig gut.** Der MVP sollte genau einen Job des Nutzers meistern. Nicht drei Jobs halb.
2. **Die riskanteste Annahme zuerst.** Der Hauptzweck des MVP ist es, die Annahme zu testen, die am wahrscheinlichsten falsch ist.
3. **Zeitbox statt Feature-Liste.** „Was können wir in [Zeitraum] bauen und testen?“ ist besser als „Welche Features brauchen wir?“
4. **Die „Not Doing“-Liste ist Pflicht.** Benenne explizit, was du streichst und warum. Das verhindert Scope Creep und erzwingt ehrliches Priorisieren.
5. **Wenn es dir nicht peinlich ist, hast du zu lange gewartet.** Die erste Version sollte sich für den Entwickler unfertig anfühlen. Tut sie das nicht, hast du zu viel gebaut.
