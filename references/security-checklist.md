# Security-Checkliste

Kurzreferenz für die Sicherheit von Webanwendungen. Verwende sie zusammen mit dem Skill `security-and-hardening`.

## Inhaltsverzeichnis

- [Threat Modeling (Hier beginnen)](#threat-modeling-start-here)
- [Prüfungen vor dem Commit](#pre-commit-checks)
- [Authentifizierung](#authentication)
- [Autorisierung](#authorization)
- [Eingabevalidierung](#input-validation)
- [Security-Header](#security-headers)
- [CORS-Konfiguration](#cors-configuration)
- [Datenschutz](#data-protection)
- [Sicherheit von Abhängigkeiten](#dependency-security)
- [KI-/LLM-Sicherheit](#ai--llm-security)
- [Fehlerbehandlung](#error-handling)
- [OWASP Top 10 – Kurzreferenz](#owasp-top-10-quick-reference)
- [OWASP Top 10 für LLMs – Kurzreferenz](#owasp-top-10-for-llms-quick-reference)

## Threat Modeling (Hier beginnen)

Bevor du zu Schutzmaßnahmen greifst, nimm dir fünf Minuten und denke wie ein Angreifer:

- [ ] Vertrauensgrenzen erfasst (Requests, Uploads, Webhooks, Drittanbieter-APIs, LLM-Ausgabe und lokale Werte, die von Prozessen geschrieben werden, die du nicht kontrollierst)
- [ ] Schutzgüter benannt (Zugangsdaten, PII, Zahlungsdaten, Admin-Aktionen, Geldbewegungen)
- [ ] STRIDE pro Vertrauensgrenze durchgespielt (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)
- [ ] Missbrauchsfälle neben den Anwendungsfällen festgehalten („Wie würde ich das missbrauchen?")

## Prüfungen vor dem Commit

- [ ] Keine Secrets im Code (`git diff --cached -i -G'password|secret|api_key|token' --name-only` – listet nur die Namen der Dateien, deren gestagter Diff passt, niemals den Wert selbst; jede Ausgabe bedeutet: Prüfe diese Dateien vor dem commit)
- [ ] `.gitignore` deckt ab: `.env`, `.env.local`, `*.pem`, `*.key`
- [ ] `.env.example` enthält Platzhalterwerte (keine echten Secrets)

## Authentifizierung

- [ ] Passwörter mit bcrypt (≥12 Runden), scrypt oder argon2 gehasht
- [ ] Session-Cookies: `httpOnly`, `secure`, `sameSite: 'lax'`
- [ ] Session-Ablauf konfiguriert (sinnvolles max-age)
- [ ] Rate Limiting am Login-Endpoint (≤10 Versuche pro 15 Minuten)
- [ ] Tokens zum Zurücksetzen von Passwörtern: zeitlich begrenzt (≤1 Stunde), einmalig verwendbar
- [ ] Konto-Sperre nach wiederholten Fehlversuchen (optional, mit Benachrichtigung)
- [ ] MFA für sensible Operationen unterstützt (optional, aber empfohlen)

## Autorisierung

- [ ] Jeder geschützte Endpoint prüft die Authentifizierung
- [ ] Jeder Ressourcenzugriff prüft Eigentümerschaft bzw. Rolle (verhindert IDOR)
- [ ] Admin-Endpoints erfordern eine Prüfung der Admin-Rolle
- [ ] API-Keys auf die minimal nötigen Berechtigungen beschränkt
- [ ] JWT-Tokens validiert (Signatur, Ablauf, Issuer)

## Eingabevalidierung

- [ ] Alle Nutzereingaben an den Systemgrenzen validiert (API-Routen, Formular-Handler)
- [ ] Validierung nutzt Allowlists (keine Denylists)
- [ ] String-Längen begrenzt (min/max)
- [ ] Zahlenbereiche validiert
- [ ] E-Mail-, URL- und Datumsformate mit geeigneten Bibliotheken validiert
- [ ] Datei-Uploads: Typ eingeschränkt, Größe begrenzt, Inhalt geprüft
- [ ] SQL-Queries parametrisiert (keine String-Konkatenation)
- [ ] HTML-Ausgabe kodiert (nutze das Auto-Escaping des Frameworks)
- [ ] URLs vor Redirects validiert (verhindert Open Redirect)
- [ ] Serverseitige URL-Abrufe per Allowlist eingeschränkt; private/reservierte IPs blockiert (verhindert SSRF)
- [ ] Destruktive Pfadoperationen (löschen/verschieben/überschreiben): Symlinks aufgelöst, Root per Allowlist, Mindesttiefe, Eigentümernachweis vor dem Aufruf gelesen

### Destruktive Pfadoperationen

Eingrenzung für ein Ziel, das durch Daten bestimmt wird. Löse zuerst auf, entscheide dann – und behandle das Ergebnis als Kandidaten, nicht als Autorisierung:

```typescript
import { realpath, readFile } from 'node:fs/promises';
import { resolve, relative, isAbsolute, join, sep } from 'node:path';

const ALLOWED_ROOTS = ['/var/lib/myapp/sessions']; // an allowlist, not a pattern
const MIN_DEPTH = 1;                               // so a root is never the target

async function resolveDeletable(candidate: string, expectedOwner: string) {
  const target = await realpath(resolve(candidate)); // symlinks resolved BEFORE the check
  const inRoot = ALLOWED_ROOTS.some((root) => {
    const rel = relative(root, target);
    // `rel === '..'` / `'../'` only — a plain `startsWith('..')` would also
    // reject a legitimate child named `..cache`.
    if (rel === '' || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) return false;
    return rel.split(sep).length >= MIN_DEPTH;
  });
  if (!inRoot) throw new Error(`refusing: outside allowed roots (${target})`);

  const owner = await readFile(join(target, '.owner'), 'utf8').catch(() => null);
  if (owner?.trim() !== expectedOwner) throw new Error(`refusing: unproven owner (${target})`);
  return target;
}
```

Was dieser Code nicht leistet – und das muss an der Stelle gesagt werden, von der das Snippet kopiert wird:

- **Der Marker ist Selbstauskunft.** Alles, was innerhalb der Root schreiben kann, kann auch `.owner` schreiben. `expectedOwner` muss aus authentifiziertem Zustand stammen, und der Marker braucht Integritätsschutz (restriktive Eigentumsrechte oder ein MAC), damit er eine Autorisierung ist und nicht bloß ein Konsistenzcheck gegen ein falsch abgeleitetes Ziel.
- **Die Rückgabe eines Pfads hinterlässt eine Check/Use-Race-Condition.** Wenn ein nicht vertrauenswürdiger Prozess zwischen Prüfung und Aufruf einen übergeordneten Ordner austauschen kann, arbeite mit einem Deskriptor mit No-Follow- und Beneath-the-Root-Semantik oder stelle sicher, dass die Hierarchie für die Dauer unveränderlich ist.

## Security-Header

```
Content-Security-Policy: default-src 'self'; script-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0  (disabled, rely on CSP)
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## CORS-Konfiguration

```typescript
// Restrictive (recommended)
cors({
  origin: ['https://yourdomain.com', 'https://app.yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
})

// NEVER use in production:
cors({ origin: '*' })  // Allows any origin
```

## Datenschutz

- [ ] Sensible Felder aus API-Responses ausgeschlossen (`passwordHash`, `resetToken` usw.)
- [ ] Sensible Daten werden nicht geloggt (Passwörter, Tokens, vollständige Kreditkartennummern)
- [ ] PII im Ruhezustand verschlüsselt (sofern gesetzlich gefordert)
- [ ] HTTPS für die gesamte externe Kommunikation
- [ ] Datenbank-Backups verschlüsselt
- [ ] Personenbezogene Daten sind klassifiziert, werden zweckgebunden erhoben und minimiert
- [ ] Personenbezogene Daten haben eine Aufbewahrungsfrist und einen funktionierenden Löschpfad (inkl. Backups, Caches, Indizes)
- [ ] Auskunfts- und Löschanfragen (Betroffenenrechte) werden unterstützt, wo erforderlich; die Weitergabe an Dritte erfolgt mit Einwilligung und Auftragsverarbeitungsvertrag

## Sicherheit von Abhängigkeiten

Ermittle zuerst die **Installationsgrenze**. Wird das Paket von einer übergeordneten `workspaces`-Deklaration erfasst, nutze die Workspace-Root; andernfalls das nächstgelegene Projekt-Root, das sowohl sein Manifest als auch seinen Abhängigkeitsgraphen besitzt. Gleiche an dieser Grenze `packageManager` (falls vorhanden), die Lockfile und die CI-Befehle gegeneinander ab. Brich ab, wenn sie sich widersprechen oder dort konkurrierende Lockfiles verschiedener Manager liegen. Ein verschachteltes Projekt ist nur dann unabhängig, wenn es außerhalb des übergeordneten Workspaces liegt; unabhängige Teilprojekte dürfen legitim unterschiedliche Manager verwenden.

| Manager-/Versionssignal | Eingefrorene/unveränderliche CI-Installation | Audit bekannter Advisories |
|---|---|---|
| npm (`package-lock.json` oder `npm-shrinkwrap.json`) | `npm ci` | `npm audit` |
| pnpm | `pnpm install --frozen-lockfile` | `pnpm audit` |
| Yarn 2+ | `yarn install --immutable` | `yarn npm audit -A -R` |
| Yarn 1 | `yarn install --frozen-lockfile` | `yarn audit` |

Für einen nicht aufgeführten Manager oder eine nicht aufgeführte Version konsultiere die offizielle Dokumentation; ersetze nicht die Befehle eines anderen Managers und übernimm keine neueren Defaults.

### Install-Script-Gate

Ermittle Lifecycle-Skripte von Abhängigkeiten niemals, indem du zuerst eine gewöhnliche Installation auf einem Client ausführst, dessen Defaults nicht verifiziert sind.

1. Bootstrappe mit deaktivierten Abhängigkeits-Skripten oder mit einer dokumentierten Default-Deny-Policy samt Fail-Closed-Durchsetzung.
2. Prüfe den genauen Skriptquelltext und die Paketversion vor der Freigabe.
3. Halte die engstmögliche native Allow/Deny-Policy an der Installationsgrenze fest und committe sie.
4. Führe eine saubere eingefrorene/unveränderliche Installation mit dieser Policy aus und verifiziere, dass die benötigten Pakete weiterhin bauen.

**Momentaufnahme:** Defaults und Befehlsnamen der Paketmanager ändern sich schnell. Verifiziere diese Matrix gegen die aktuelle offizielle Dokumentation des gepinnten Clients, bevor du dich darauf verlässt.

| Manager-Version | Native Policy |
|---|---|
| npm ohne verifizierte granulare Freigaben | Bootstrappe mit `npm ci --ignore-scripts` oder lege `ignore-scripts=true` dauerhaft fest, wenn projektweit blockiert werden soll. Lass Skripte deaktiviert oder aktualisiere bewusst, bevor du ein geprüftes Abhängigkeits-Skript erlaubst. |
| npm 11.18.x (verifiziert mit 11.18.0) | Ungeprüfte Abhängigkeits-Skripte laufen standardmäßig mit einer Warnung. Erzwinge `strict-allow-scripts=true` vor einer normalen Installation und nutze dann das workspace-unabhängige `npm install-scripts ls` von der Installationsgrenze aus; halte Freigaben versionsgepinnt und Ablehnungen paketnamenweit. |
| npm 12.x (verifiziert mit 12.0.1) | Ungeprüfte Abhängigkeits-Skripte werden standardmäßig übersprungen; `strict-allow-scripts=true` lässt die Installation scheitern, bevor sie ausgeführt würden. Nutze denselben Prüf- und Freigabe-Ablauf mit `npm install-scripts`. |
| pnpm 11+ | Nutze `pnpm approve-builds` und committe die `allowBuilds`-Entscheidungen; `strictDepBuilds` ist standardmäßig `true`, ungeprüfte Builds schlagen also fehl. |
| pnpm 10.26–10.x | Konfiguriere `allowBuilds` explizit oder nutze `pnpm approve-builds` mit den Legacy-Listen `onlyBuiltDependencies` / `ignoredBuiltDependencies`. Setze `strictDepBuilds: true`; der Default in v10 ist `false`. |
| pnpm 10.1–10.25 | `pnpm approve-builds` schreibt die Legacy-Listen; aktiviere `strictDepBuilds`, wo unterstützt (ab 10.3). |
| Ältere oder unbekannte pnpm-Version | Bootstrappe mit `pnpm install --frozen-lockfile --ignore-scripts`. Lass Skripte deaktiviert, sofern die gepinnte Version keine durchsetzbare Policy dokumentiert. |
| Yarn 4.14+ | Postinstall-Skripte von Abhängigkeiten sind standardmäßig deaktiviert. Gewähre nur nötige Ausnahmen mit `dependenciesMeta.<package>.built: true` auf oberster Ebene. |
| Yarn 2–4.13 | Setze `enableScripts: false` in `.yarnrc.yml` und gewähre dann nur nötige Ausnahmen mit `dependenciesMeta.<package>.built: true` auf oberster Ebene; aktiviere Skripte nicht global. |
| Yarn 1 | Bootstrappe mit `yarn install --ignore-scripts`; lass Skripte deaktiviert, sofern nicht jede nötige Ausnahme nach dem dokumentierten Workflow des gepinnten Clients geprüft wurde. |

Maßgebliche Quellen: [npm install-scripts](https://docs.npmjs.com/cli/v11/commands/npm-install-scripts/), [install policy](https://docs.npmjs.com/cli/v11/commands/npm-install/) und [CLI releases](https://github.com/npm/cli/releases); [pnpm approve-builds](https://pnpm.io/cli/approve-builds) und [build settings](https://pnpm.io/settings#allowbuilds); [Yarn security](https://yarnpkg.com/features/security) und [manifest](https://yarnpkg.com/configuration/manifest#dependenciesMeta).

**Supply-Chain-Hygiene** (Advisory-Audits erkennen keine neu eingeschleusten bösartigen Pakete):
- [ ] Genau eine maßgebliche Lockfile pro Projekt-/Workspace-Root ist committet, und CI schreibt sie niemals um
- [ ] Critical-/High-Befunde werden auf Erreichbarkeit triagiert; Zurückstellungen haben eine Begründung und ein Review-Datum
- [ ] Erzwungene Audit-Behebung (`npm audit fix --force` oder Entsprechendes) läuft nie automatisch; Diffs und Changelogs der Behebung werden geprüft
- [ ] Registry-Signaturen/Provenance werden verifiziert, wo der Manager das unterstützt
- [ ] Lifecycle-Skripte von Abhängigkeiten werden vor der ersten Ausführung blockiert und nur über die native Policy des gepinnten Managers freigegeben
- [ ] Neue Abhängigkeiten werden auf Eigentümerschaft, Pflege, Alter des Releases, Provenance, transitiven Graphen und Typosquatting geprüft

## KI-/LLM-Sicherheit

Für jedes Feature, das ein LLM aufruft (Chatbots, Zusammenfasser, Agents, RAG):

- [ ] Modellausgabe gilt als nicht vertrauenswürdig – niemals in `eval`/SQL/Shell/`innerHTML`/Dateipfade
- [ ] Prompt Injection wird vorausgesetzt; Berechtigungen werden im Code durchgesetzt, nicht im System-Prompt
- [ ] Secrets, mandantenübergreifende Daten und vollständige System-Prompts bleiben aus dem Kontextfenster heraus
- [ ] Tool-/Agent-Berechtigungen eingegrenzt; destruktive oder irreversible Aktionen erfordern eine Bestätigung
- [ ] Limits für Token, Rate und Rekursion/Schleifen gesetzt (Verbrauch begrenzen)

## Fehlerbehandlung

```typescript
// Production: generic error, no internals
res.status(500).json({
  error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' }
});

// NEVER in production:
res.status(500).json({
  error: err.message,
  stack: err.stack,         // Exposes internals
  query: err.sql,           // Exposes database details
});
```

## OWASP Top 10 – Kurzreferenz

| # | Schwachstelle | Prävention |
|---|---|---|
| 1 | Broken Access Control | Auth-Prüfungen an jedem Endpoint, Verifikation der Eigentümerschaft |
| 2 | Cryptographic Failures | HTTPS, starkes Hashing, keine Secrets im Code |
| 3 | Injection | Parametrisierte Queries, Eingabevalidierung |
| 4 | Insecure Design | Threat Modeling, Spec-driven Development |
| 5 | Security Misconfiguration | Security-Header, minimale Berechtigungen, Abhängigkeiten auditieren |
| 6 | Vulnerable Components | Das Dependency-Audit des Ökosystems (`npm audit`, `pip-audit`, ...), Abhängigkeiten aktuell halten, möglichst wenige Abhängigkeiten |
| 7 | Auth Failures | Starke Passwörter, Rate Limiting, Session-Management |
| 8 | Data Integrity Failures | Updates/Abhängigkeiten verifizieren, signierte Artefakte |
| 9 | Logging Failures | Sicherheitsereignisse loggen, keine Secrets loggen |
| 10 | SSRF | URLs validieren/per Allowlist einschränken, ausgehende Requests begrenzen |

## OWASP Top 10 für LLMs – Kurzreferenz

Für Apps mit LLM-Features. Siehe das [OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/).

| ID | Risiko | Prävention |
|---|---|---|
| LLM01 | Prompt Injection | Vertraue dem System-Prompt nicht als Grenze; setze Berechtigungen im Code durch |
| LLM02 | Sensitive Information Disclosure | Halte Secrets/PII aus Prompts heraus; filtere Ausgaben |
| LLM03 | Supply Chain | Prüfe Modelle, Datensätze und Plugins wie jede andere Abhängigkeit |
| LLM04 | Data and Model Poisoning | Nutze vertrauenswürdige Modellquellen, verifiziere die Integrität; prüfe Fine-Tuning- und RAG-Daten |
| LLM05 | Improper Output Handling | Behandle Modellausgabe als nicht vertrauenswürdig; validieren, parametrisieren, kodieren |
| LLM06 | Excessive Agency | Begrenze Tool-Berechtigungen; bestätige destruktive Aktionen |
| LLM07 | System Prompt Leakage | Gehe davon aus, dass der System-Prompt durchsickern kann; lege keine Secrets darin ab |
| LLM08 | Vector and Embedding Weaknesses | Partitioniere RAG-Embeddings pro Mandant; validiere Dokumente vor der Indexierung |
| LLM09 | Misinformation | Untermauere Antworten mit Quellenangaben; validiere kritische Aussagen; behalte einen Menschen im Loop |
| LLM10 | Unbounded Consumption | Begrenze Token, Request-Rate und Schleifen-/Rekursionstiefe |
