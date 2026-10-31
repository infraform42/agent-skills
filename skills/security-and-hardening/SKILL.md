---
name: security-and-hardening
description: "Härtung gegen Schwachstellen (agent-skills). Nur verwenden, wenn ein agent-skills-de-Command oder -Agent darauf verweist oder der Nutzer diesen Skill ausdrücklich nennt. Im Alltag gilt der eingebaute Skill security-review."
---

# Sicherheit und Härtung

## Überblick

Security-first-Entwicklungspraktiken für Webanwendungen. Behandle jede externe Eingabe als feindlich, jedes Secret als heilig und jede Autorisierungsprüfung als zwingend. Sicherheit ist keine Phase, sondern ein Constraint für jede Codezeile, die Nutzerdaten, Authentifizierung oder externe Systeme berührt.

## Wann verwenden

- Bei allem, was Nutzereingaben entgegennimmt
- Bei der Implementierung von Authentifizierung oder Autorisierung
- Beim Speichern oder Übertragen sensibler Daten
- Bei der Integration externer APIs oder Dienste
- Beim Hinzufügen von Datei-Uploads, Webhooks oder Callbacks
- Bei der Verarbeitung von Zahlungsdaten oder PII

## Vorgehen: Zuerst das Threat Model

Controls, die ohne Threat Model aufgesetzt werden, sind Raten. Denke vor dem Härten fünf Minuten lang wie ein Angreifer:

1. **Trust Boundaries kartieren.** Wo gelangen unvertrauenswürdige Daten in dein System? HTTP-Requests, Formularfelder, Datei-Uploads, Webhooks, Drittanbieter-APIs, Message Queues und **LLM-Output** – dazu lokale Werte, die intern wirken, weil das Betriebssystem sie dir übergeben hat: die Kommandozeile oder Umgebung eines anderen Prozesses, Dateinamen auf einem geteilten Volume, ein Pfad in einem Job-Payload. Vertrauen richtet sich danach, wer einen Wert *geschrieben* hat, nicht danach, über welchen Kanal er ankam. Jede Boundary ist Angriffsfläche.
2. **Assets benennen.** Was lohnt sich zu stehlen oder zu zerstören? Zugangsdaten, PII, Zahlungsdaten, Admin-Aktionen, Geldbewegungen.
3. **STRIDE über jede Boundary laufen lassen** – eine schnelle Linse, keine Zeremonie:

| Bedrohung | Frage | Typische Gegenmaßnahme |
|---|---|---|
| **S**poofing | Kann sich jemand als Nutzer/Dienst ausgeben? | Authentifizierung, Signaturprüfung |
| **T**ampering | Können Daten bei der Übertragung oder im Ruhezustand verändert werden? | Integritätsprüfungen, parametrisierte Queries, HTTPS |
| **R**epudiation | Kann eine Aktion später abgestritten werden? | Audit-Logging von Sicherheitsereignissen |
| **I**nformation disclosure | Können Daten abfließen? | Verschlüsselung, Feld-Allowlists, generische Fehlermeldungen |
| **D**enial of service | Kann das System überlastet werden? | Rate Limiting, Größenlimits für Eingaben, Timeouts |
| **E**levation of privilege | Kann ein Nutzer Rechte erlangen, die er nicht haben darf? | Autorisierungsprüfungen, Least Privilege |

4. **Missbrauchsfälle neben die Anwendungsfälle schreiben.** Frage bei jedem Feature „Wie würde ich das missbrauchen?“ – und mach daraus deinen ersten Test.

Wenn du die Trust Boundaries eines Features nicht benennen kannst, bist du noch nicht bereit, es abzusichern. Das ist OWASP **A04: Insecure Design** – die meisten Sicherheitsvorfälle beginnen im Design, nicht im Code.

## Das dreistufige Boundary-System

### Immer tun (keine Ausnahmen)

- **Alle externen Eingaben validieren** an der Systemgrenze (API-Routen, Formular-Handler)
- **Alle Datenbankabfragen parametrisieren** – Nutzereingaben niemals in SQL konkatenieren
- **Ausgaben encodieren**, um XSS zu verhindern (Auto-Escaping des Frameworks nutzen, nicht umgehen)
- **HTTPS verwenden** für jede externe Kommunikation
- **Passwörter hashen** mit bcrypt/scrypt/argon2 (niemals im Klartext speichern)
- **Security-Header setzen** (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- **httpOnly-, secure- und sameSite-Cookies** für Sessions verwenden
- **Das native Audit des erkannten Paketmanagers** gegen das committete Lockfile vor jedem Release ausführen

### Zuerst fragen (erfordert menschliche Freigabe)

- Neue Authentifizierungs-Flows hinzufügen oder Auth-Logik ändern
- Neue Kategorien sensibler Daten speichern (PII, Zahlungsinformationen)
- Neue Integrationen externer Dienste hinzufügen
- CORS-Konfiguration ändern
- Upload-Handler hinzufügen
- Rate Limiting oder Throttling ändern
- Erhöhte Berechtigungen oder Rollen vergeben

### Niemals tun

- **Niemals Secrets committen** in die Versionskontrolle (API-Keys, Passwörter, Tokens)
- **Niemals sensible Daten loggen** (Passwörter, Tokens, vollständige Kreditkartennummern)
- **Niemals Client-seitiger Validierung vertrauen** als Sicherheitsgrenze
- **Niemals Security-Header deaktivieren**, nur weil es bequemer ist
- **Niemals `eval()` oder `innerHTML`** mit nutzerseitig gelieferten Daten verwenden
- **Niemals Sessions in clientseitig zugänglichem Speicher ablegen** (localStorage für Auth-Tokens)
- **Niemals Stack Traces** oder interne Fehlerdetails gegenüber Nutzern offenlegen

## Härtungsmaßnahmen

Die folgenden Regeln sind der Workflow; eine konkrete Implementierung zu jeder Regel findest du in [references/hardening-patterns.md](references/hardening-patterns.md). Öffne den benötigten Abschnitt erst, wenn du an diesem Code arbeitest, nicht vorher.

### Injection, XSS und Zugriffskontrolle

- Parametrisiere jede Query. Baue niemals SQL-, NoSQL- oder Shell-Befehle aus Eingabestrings.
- Encodiere Ausgaben über das Auto-Escaping des Frameworks. Ist rohes HTML unvermeidbar, sanitize es vorher mit einem Allowlist-Sanitizer.
- Prüfe die **Autorisierung** bei jedem Request, nicht nur die Authentifizierung: Der authentifizierte Nutzer muss die konkrete Ressource besitzen oder darauf berechtigt sein (A01, IDOR).

Patterns: [Injection](references/hardening-patterns.md#injection), [XSS](references/hardening-patterns.md#cross-site-scripting-xss), [Zugriffskontrolle](references/hardening-patterns.md#broken-access-control).

### Authentifizierung und Sessions

- Hashe Passwörter mit bcrypt (≥12 Runden), scrypt oder argon2. Das Session-Secret stammt aus der Umgebung, niemals aus dem Code.
- Session-Cookies sind `httpOnly`, `secure` und `sameSite: 'lax'` oder `'strict'` (die CSRF-Abwehr; `'none'` sendet das Cookie bei Cross-Site-Requests mit), mit begrenztem `maxAge`.

Pattern: [Authentifizierung](references/hardening-patterns.md#broken-authentication).

### Header, CORS und Responses

- Security-Header bei jeder Response (helmet oder das Äquivalent des Frameworks); CSP beginnt mit `default-src 'self'` und wird verschärft, nicht gelockert.
- CORS auf eine explizite Origin-Liste aus der Konfiguration beschränken. Niemals `*` zusammen mit Credentials.
- Entferne sensible Felder (`passwordHash`, Reset-Tokens) vor jeder Response. Fehler-Bodies sind generisch; Interna gehören nur in die Server-Logs.

Patterns: [Fehlkonfiguration](references/hardening-patterns.md#security-misconfiguration), [Offenlegung sensibler Daten](references/hardening-patterns.md#sensitive-data-exposure).

### Eingabevalidierung und Uploads

- Validiere an der Boundary mit einem Schema: Allowlist für Struktur, Längen, Enums, Formate. Lehne mit 422 und strukturierten Details ab; nachgelagerter Code verwendet ausschließlich den geparsten, typisierten Wert.
- Uploads: MIME-Typen per Allowlist, Größe begrenzen, Inhalt (Magic Bytes) prüfen, wenn es darauf ankommt. Die Dateiendung beweist nichts.

Patterns: [Schema-Validierung](references/hardening-patterns.md#schema-validation-at-boundaries), [Datei-Upload](references/hardening-patterns.md#file-upload-safety).

### Serverseitige Fetches (SSRF)

Jede URL, die der Nutzer beeinflusst – Webhooks, Import-from-URL, Bild-Proxys, Link-Vorschauen –, kann auf interne Dienste gerichtet werden. Setze Schema und Host auf eine Allowlist, löse **alle** DNS-Records auf und lehne jede private oder reservierte Adresse ab (Loopback, Link-Local `169.254.169.254`, privat, Unique-Local, jeweils für IPv4 und IPv6), und verbiete Redirects. Diese Prüfung hat weiterhin eine DNS-Rebinding-TOCTOU-Lücke: Pinne bei Hochrisiko-Oberflächen die aufgelöste IP oder schalte einen filternden Agent davor.

Pattern: [SSRF](references/hardening-patterns.md#server-side-request-forgery-ssrf).

### Destruktive Operationen auf abgeleiteten Pfaden

Ein Löschen, Verschieben oder Überschreiben ist nur so sicher wie der Wert, der sein Ziel benennt, und Vertrauen richtet sich danach, wer diesen Wert *geschrieben* hat, nicht danach, über welchen Kanal er ankam: Die Kommandozeile eines anderen Prozesses ist genauso angreiferkontrolliert wie ein Formularfeld. Eine Formprüfung beweist Wohlgeformtheit, nicht Autorisierung. Verlange vor dem Aufruf alle drei Punkte: Das aufgelöste Ziel (Symlinks aufgelöst) liegt unter einem **Allowlist-Root**; es liegt mindestens eine Ebene **unterhalb** dieses Roots; und es trägt einen **Eigentumsnachweis, der vor der Operation gelesen wurde**. Protokolliere bei einer Ablehnung das abgelehnte Ziel und brich ab; falle niemals auf einen breiteren Standardpfad zurück.

Warum die Prüfung schwächer ist, als sie klingt (Selbstattestierung durch Marker, Check/Use-Races): [Destruktive Pfade](references/hardening-patterns.md#destructive-operations-on-derived-paths). Ausgearbeiteter Code: `../../references/security-checklist.md`.

### Rate Limiting

Begrenze die API allgemein und Auth-Endpunkte streng (etwa 10 Versuche pro 15 Minuten). Sobald mehr als ein Prozess Traffic bedient, werden In-Memory-Zähler stillschweigend zu `max × instances` oder greifen auf Serverless nie: Stütze den Limiter mit einem gemeinsamen Store.

Pattern: [Rate Limiting](references/hardening-patterns.md#rate-limiting).

### Secrets

Secrets kommen aus der Umgebung. `.env.example` wird mit Platzhaltern committet; echte `.env*`-Dateien und Schlüsselmaterial stehen in der `.gitignore`; durchsuche den gestagten Diff per grep, bevor du committest. **Ein Secret, das ein Remote erreicht, ist in dem Moment kompromittiert: zuerst rotieren, dann die Historie bereinigen.**

Pattern: [Secrets-Management](references/hardening-patterns.md#secrets-management).

### Abhängigkeiten und Supply Chain

1. **Installationsgrenze und Manager finden.** Nutze das Workspace-Root, dem das Lockfile gehört, oder ein unabhängiges verschachteltes Projekt nur dann, wenn es außerhalb dieses Workspace liegt. Gleiche `packageManager` (falls vorhanden), das Lockfile und CI gegeneinander ab; brich bei Widerspruch oder konkurrierenden Lockfiles ab. Pinne die Manager-Version.
2. **Dependency-Skripte vor der ersten Ausführung blockieren.** Bootstrappe mit deaktivierten Skripten oder einer dokumentierten Fail-closed-Policy, prüfe den Quelltext der ausstehenden Skripte, genehmige nur das Minimum, committe die Policy und verifiziere dann mit einer sauberen Frozen-/Immutable-Installation. Niemals pauschal genehmigen.
3. **Das native Audit vor jedem Release gegen das committete Lockfile ausführen.** Priorisiere Critical/High nach **Erreichbarkeit** (Runtime-, Build-, Test- und Deploy-Pfade) und behebe die Verfügbarkeit. Wende erzwungene Behebungen (`npm audit fix --force` oder Äquivalent) niemals automatisch an, da erzwungene Fixes deklarierte Abhängigkeitsbereiche überschreiten können; sieh dir eine Vorschau an, lies die Changelogs, teste jedes Upgrade. Dokumentiere jede Zurückstellung mit Begründung und Wiedervorlagedatum.
4. **Audits erkennen nur bekannte Advisories.** Sie fangen kein neu eingeschleustes bösartiges oder Typosquatting-Paket (`cross-env` vs. `crossenv`). Prüfe neue Abhängigkeiten, Lockfile-Diffs und Änderungen an der Skript-Policy gemeinsam: Eigentümerschaft, Wartung, Release-Alter, Provenance, transitiver Graph. Verifiziere Registry-Signaturen, wo unterstützt (`npm audit signatures`, `pnpm audit signatures`), und werte deren Fehlen als Anlass zur Untersuchung, nicht als automatischen Beweis einer Kompromittierung (A06, LLM03).

Entscheidungsbaum zur Triage: [Dependency-Audit-Triage](references/hardening-patterns.md#dependency-audit-triage). Manager-Matrix und Install-Script-Gate: `../../references/security-checklist.md`.

### Personenbezogene Daten und Datenschutz

Härtung fragt: „Kann ein Angreifer es lesen?“ Datenschutz fragt: „Sollten *wir* es überhaupt halten, und wie lange?“ Die Daten, die du nie erhoben hast, sind am günstigsten zu schützen, bei einem Vorfall zu verantworten und rechtlich abzusichern; behandle personenbezogene Daten als Last, die es zu minimieren gilt.

- **Klassifiziere Felder, sobald du sie hinzufügst** (nicht personenbezogen, PII, sensibel) und behandle jede Klasse entsprechend. Daten, die du nicht findest, kannst du weder schützen noch für einen Löschantrag berücksichtigen.
- **Erhebe nur mit angegebenem Zweck.** „Könnte später nützlich sein“ ist latenter Breach-Umfang, kein Zweck. Halte PII aus der Telemetrie heraus (der Skill `observability-and-instrumentation` macht denselben Punkt von der Betriebsseite aus).
- **Lege die Aufbewahrung vorab fest und lösche dann tatsächlich.** Jeder Speicher für personenbezogene Daten braucht eine TTL und einen funktionierenden Löschpfad, einschließlich Backups, Caches, Suchindizes und Analytics-Kopien.
- **Unterstütze die Betroffenenrechte, die deine Jurisdiktion verlangt** (GDPR, CCPA und verwandte): Export, Berichtigung, Löschung. Entwirf das Schema so, dass die Daten eines Nutzers auffindbar und löschbar sind, nicht unwiederbringlich über Systeme verstreut.
- **Einwilligung steuert Erhebung und Weitergabe an Dritte und ist nachweisbar.** PII an einen Analytics-, Werbe- oder LLM-Anbieter zu senden ist Weitergabe; der Anbieter braucht einen Auftragsverarbeitungsvertrag. Mache die Region zu einer konfigurierbaren Policy, nicht zu einer hartkodierten Annahme.

Klassifizierungstabelle: [Datenklassifizierung](references/hardening-patterns.md#data-classification). Ein Datenschutzvorfall startet die Meldefrist; führe das Postmortem mit dem Skill `debugging-and-error-recovery` durch.

### KI-/LLM-Features

Der Aufruf eines LLM – Chatbots, Zusammenfasser, Agents, RAG – schafft eine neue Angriffsfläche; ordne sie den [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/) zu:

- **Modell-Output ist unvertrauenswürdige Eingabe** (LLM05). Niemals in `eval`, SQL, eine Shell, `innerHTML` oder einen Dateipfad; defensiv parsen, gegen ein Schema validieren, dann encodieren.
- **Prompts können gekapert werden** (LLM01). Unvertrauenswürdiger Text im Kontext – eine Nutzernachricht, eine abgerufene Seite, ein PDF – kann Anweisungen enthalten. Der System-Prompt ist keine Sicherheitsgrenze; erzwinge Berechtigungen im Code.
- **Halte Secrets, Daten anderer Mandanten und den vollständigen System-Prompt aus dem Kontextfenster heraus** (LLM02, LLM07); begrenze Tool-Berechtigungen, validiere jedes Tool-Argument und bestätige destruktive Aktionen (LLM06); begrenze Tokens, Request-Rate und Rekursionstiefe (LLM10); partitioniere RAG-Embeddings pro Mandant und validiere Dokumente vor dem Indexieren (LLM08).

Pattern: [Umgang mit LLM-Output](references/hardening-patterns.md#llm-output-handling).

## Review-Checkliste

Gehe vor der Freigabe `../../references/security-checklist.md` durch: Sie deckt Authentifizierung, Autorisierung, Eingaben, Datenschutz und Datenschutz-Compliance, Header und CORS, Abhängigkeiten und Supply Chain, KI/LLM und Fehlerbehandlung ab, dazu die OWASP-Kurzreferenztabellen.

## Typische Ausreden

| Ausrede | Realität |
|---|---|
| „Das ist ein internes Tool, Sicherheit spielt keine Rolle“ | Interne Tools werden kompromittiert. Angreifer zielen auf das schwächste Glied. |
| „Sicherheit bauen wir später ein“ | Sicherheit nachzurüsten ist zehnmal schwerer, als sie von Anfang an einzubauen. Mach es jetzt. |
| „Niemand würde versuchen, das auszunutzen“ | Automatisierte Scanner finden es. Security by Obscurity ist keine Sicherheit. |
| „Das Framework kümmert sich um Sicherheit“ | Frameworks liefern Werkzeuge, keine Garantien. Du musst sie trotzdem korrekt einsetzen. |
| „Das ist nur ein Prototyp“ | Prototypen werden zu Produktion. Sicherheitsgewohnheiten ab dem ersten Tag. |
| „Threat Modeling ist hier übertrieben“ | Fünf Minuten „Wie würde ich das angreifen?“ verhindern die Designfehler, die später keine Control mehr beheben kann. |
| „Das ist nur LLM-Output, nur Text“ | Dieser „Text“ kann ein SQL-Statement, ein Script-Tag oder ein Shell-Befehl sein. Behandle ihn wie jede unvertrauenswürdige Eingabe. |
| „Das Audit ist durchgelaufen, also ist die Abhängigkeit sicher“ | Audits gleichen bekannte Advisories ab. Sie erkennen kein neu eingeschleustes bösartiges Paket und machen ungeprüfte Install-Skripte nicht sicher ausführbar. |
| „Erheben wir es jetzt, wir brauchen es vielleicht später“ | Daten, die du nicht hältst, können nicht abfließen, beschlagnahmt oder falsch gelöscht werden. „Vielleicht brauchen wir es“ ist Breach-Umfang, kein Zweck. |
| „Löschanfragen bearbeiten wir manuell“ | Manuelles Löschen übersieht Backups, Caches und Analytics-Kopien. Wenn das Schema die Daten eines Nutzers nicht finden kann, kannst du die Anfrage nicht erfüllen – entwirf dafür vor. |
| „Compliance ist das Problem der Rechtsabteilung, nicht unseres“ | Export, Löschung, Aufbewahrung und Einwilligung sind Schema und Code. Die Rechtsabteilung kann sie nicht nachrüsten, wenn du PII über zehn Systeme verstreut hast. |

## Warnsignale

- Nutzereingaben werden direkt an Datenbankabfragen, Shell-Befehle oder HTML-Rendering übergeben
- Ein Löschen, Verschieben oder Überschreiben, dessen Ziel aus einem Payload, einem Konfigurationswert oder der Kommandozeile eines anderen Prozesses stammt und nur durch eine Formprüfung des Pfads abgesichert ist
- Secrets im Quellcode oder in der Commit-Historie
- API-Endpunkte ohne Authentifizierungs- oder Autorisierungsprüfung
- Fehlende CORS-Konfiguration oder Wildcard-Origins (`*`)
- Kein Rate Limiting auf Authentifizierungs-Endpunkten oder ein In-Memory-Limiter vor mehr als einer Instanz
- Stack Traces oder interne Fehler werden Nutzern angezeigt
- Abhängigkeiten mit bekannten kritischen Schwachstellen, konkurrierende Lockfiles an einer Installationsgrenze, nicht reproduzierbare Installationen oder pauschal genehmigte Skripte
- Der Server ruft nutzerseitig gelieferte URLs ohne Allowlist ab (SSRF)
- LLM-/Modell-Output wird in eine Query, das DOM, eine Shell oder `eval` übergeben
- Secrets, PII oder der vollständige System-Prompt liegen im Kontextfenster eines LLM
- Personenbezogene Daten werden ohne angegebenen Zweck, Aufbewahrungsgrenze oder Löschpfad erhoben
- PII wird ohne Einwilligung oder Auftragsverarbeitungsvertrag an Analytics-/Werbe-/LLM-Anbieter gesendet
- „Mein Konto löschen“ setzt nur ein Flag, während die personenbezogenen Daten in Speichern und Backups verbleiben

## Verifikation

Nach der Implementierung sicherheitsrelevanten Codes:

- [ ] Das native Audit hat keine nicht mitigierten, erreichbaren Critical/High-Befunde; CI bewahrt das maßgebliche Lockfile und blockiert ungeprüfte Dependency-Skripte
- [ ] Keine Secrets im Quellcode oder in der Git-Historie
- [ ] Alle Nutzereingaben an den Systemgrenzen validiert
- [ ] Destruktive Dateisystemoperationen lösen Symlinks auf und verifizieren Allowlist-Root, Mindesttiefe und Eigentum, bevor sie laufen
- [ ] Authentifizierung und Autorisierung bei jedem geschützten Endpunkt geprüft
- [ ] Security-Header in der Response vorhanden (mit den Browser-DevTools prüfen)
- [ ] Fehlerantworten legen keine internen Details offen
- [ ] Rate Limiting auf Auth-Endpunkten aktiv, mit gemeinsamem Store, wenn mehr als eine Instanz Traffic bedient
- [ ] Serverseitige URL-Fetches gegen eine Allowlist validiert (kein SSRF)
- [ ] LLM-/Modell-Output vor der Verwendung validiert und encodiert (falls KI-Features vorhanden)
- [ ] Personenbezogene Daten sind klassifiziert, auf einen angegebenen Zweck minimiert und haben eine Aufbewahrungsgrenze
- [ ] Lösch- und Exportanfragen funktionieren Ende-zu-Ende (einschließlich Backups, Caches und Analytics-Kopien)
