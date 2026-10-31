---
name: ci-cd-and-automation
description: Automatisiert die Einrichtung von CI/CD-Pipelines. Verwenden, wenn Build- und Deployment-Pipelines aufgesetzt oder geändert werden. Verwenden, wenn Quality Gates automatisiert, Test-Runner in CI konfiguriert oder Deployment-Strategien festgelegt werden sollen. Typische Formulierungen „richte die CI-Pipeline ein“, „automatisiere Lint und Tests im Build“, „bau mir eine GitHub-Actions-Pipeline“, „warum schlägt die CI fehl“, „plane einen gestaffelten Rollout mit Rollback“.
---

# CI/CD und Automatisierung

## Überblick

Automatisiere Quality Gates, damit keine Änderung ohne bestandene Tests, Lint, Typprüfung und Build in Produktion gelangt. CI/CD ist der Durchsetzungsmechanismus für jeden anderen Skill: Es fängt ab, was Menschen und Agents übersehen, und das konsistent bei jeder einzelnen Änderung.

**Shift Left:** Finde Probleme so früh wie möglich in der Pipeline. Ein Bug, der beim Linting auffällt, kostet Minuten; derselbe Bug in Produktion kostet Stunden. Verlagere Prüfungen nach vorn: statische Analyse vor Tests, Tests vor Staging, Staging vor Produktion.

**Schneller ist sicherer:** Kleinere Batches und häufigere Releases senken das Risiko, statt es zu erhöhen. Ein Deployment mit 3 Änderungen ist leichter zu debuggen als eines mit 30. Häufige Releases schaffen Vertrauen in den Release-Prozess selbst.

## Wann verwenden

- Beim Einrichten der CI-Pipeline eines neuen Projekts
- Beim Hinzufügen oder Ändern automatisierter Prüfungen
- Beim Konfigurieren von Deployment-Pipelines
- Wenn eine Änderung eine automatisierte Verifikation auslösen soll
- Beim Debuggen von CI-Fehlern

## Die Quality-Gate-Pipeline

Jede Änderung durchläuft vor dem merge diese Gates:

```
Pull Request Opened
    │
    ▼
┌─────────────────┐
│   LINT CHECK     │  eslint, prettier
│   ↓ pass         │
│   TYPE CHECK     │  tsc --noEmit
│   ↓ pass         │
│   UNIT TESTS     │  jest/vitest
│   ↓ pass         │
│   BUILD          │  npm run build
│   ↓ pass         │
│   INTEGRATION    │  API/DB tests
│   ↓ pass         │
│   E2E (optional) │  Playwright/Cypress
│   ↓ pass         │
│   SECURITY AUDIT │  npm audit
│   ↓ pass         │
│   BUNDLE SIZE    │  bundlesize check
└─────────────────┘
    │
    ▼
  Ready for review
```

**Kein Gate darf übersprungen werden.** Wenn Lint fehlschlägt, behebe die Lint-Befunde, statt die Regel zu deaktivieren. Wenn ein Test fehlschlägt, repariere den Code, statt den Test zu überspringen.

## GitHub-Actions-Konfiguration

### Einfache CI-Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npx tsc --noEmit

      - name: Test
        run: npm test -- --coverage

      - name: Build
        run: npm run build

      - name: Security audit
        run: npm audit --audit-level=high
```

### Mit Datenbank-Integrationstests

```yaml
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: ci_user
          POSTGRES_PASSWORD: ${{ secrets.CI_DB_PASSWORD }}
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - name: Run migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://ci_user:${{ secrets.CI_DB_PASSWORD }}@localhost:5432/testdb
      - name: Integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://ci_user:${{ secrets.CI_DB_PASSWORD }}@localhost:5432/testdb
```

> **Hinweis:** Verwende auch für reine CI-Testdatenbanken GitHub Secrets für Zugangsdaten, statt Werte fest zu verdrahten. Das schafft gute Gewohnheiten und verhindert, dass Test-Zugangsdaten versehentlich in anderen Kontexten wiederverwendet werden.

### E2E-Tests

```yaml
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps chromium
      - name: Build
        run: npm run build
      - name: Run E2E tests
        run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## CI-Fehler an Agents zurückspielen

Die Stärke von CI mit KI-Agents ist die Feedback-Schleife. Wenn CI fehlschlägt:

```
CI fails
    │
    ▼
Copy the failure output
    │
    ▼
Feed it to the agent:
"The CI pipeline failed with this error:
[paste specific error]
Fix the issue and verify locally before pushing again."
    │
    ▼
Agent fixes → pushes → CI runs again
```

**Zentrale Muster:**

```
Lint failure → Agent runs `npm run lint -- --fix` and commits
Type error  → Agent reads the error location and fixes the type
Test failure → Agent follows debugging-and-error-recovery skill
Build error → Agent checks config and dependencies
```

## Deployment-Strategien

### Preview-Deployments

Jeder PR bekommt ein Preview-Deployment für manuelles Testen:

```yaml
# Deploy preview on PR (Vercel/Netlify/etc.)
deploy-preview:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    - name: Deploy preview
      run: npx vercel --token=${{ secrets.VERCEL_TOKEN }}
```

### Feature-Flags

Feature-Flags entkoppeln Deployment vom Release. Deploye unfertige oder riskante Features hinter Flags, damit du:

- **Code ausliefern kannst, ohne ihn zu aktivieren.** Merge früh nach main, aktiviere, wenn es so weit ist.
- **ohne Redeployment zurückrollen kannst.** Deaktiviere das Flag, statt Code zu reverten.
- **neue Features als Canary ausrollen kannst.** Aktiviere sie für 1 % der Nutzer, dann 10 %, dann 100 %.
- **A/B-Tests durchführen kannst.** Vergleiche das Verhalten mit und ohne das Feature.

```typescript
// Simple feature flag pattern
if (featureFlags.isEnabled('new-checkout-flow', { userId })) {
  return renderNewCheckout();
}
return renderLegacyCheckout();
```

**Lebenszyklus eines Flags:** Anlegen → Für Tests aktivieren → Canary → Vollständiger Rollout → Flag und toten Code entfernen. Flags, die ewig leben, werden zu technischen Schulden – lege beim Anlegen ein Datum für das Aufräumen fest.

### Gestaffelte Rollouts

```
PR merged to main
    │
    ▼
  Staging deployment (auto)
    │ Manual verification
    ▼
  Production deployment (manual trigger or auto after staging)
    │
    ▼
  Monitor for errors (15-minute window)
    │
    ├── Errors detected → Rollback
    └── Clean → Done
```

### Rollback-Plan

Jedes Deployment sollte umkehrbar sein:

```yaml
# Manual rollback workflow
name: Rollback
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Rollback deployment
        env:
          VERSION: ${{ inputs.version }}
        run: |
          # Deploy the specified previous version. Pass the input through env,
          # never interpolate it into the script (shell injection).
          npx vercel rollback "$VERSION"
```

## Umgebungsverwaltung

```
.env.example       → Committed (template for developers)
.env                → NOT committed (local development)
.env.test           → Committed (test environment, no real secrets)
CI secrets          → Stored in GitHub Secrets / vault
Production secrets  → Stored in deployment platform / vault
```

CI sollte niemals Produktions-Secrets haben. Verwende separate Secrets für CI-Tests.

## Automatisierung jenseits von CI

### Dependabot / Renovate

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
```

### Rolle des Build Cop

Benenne jemanden, der dafür verantwortlich ist, CI grün zu halten. Wenn der Build bricht, ist es die Aufgabe des Build Cop, ihn zu reparieren oder zu reverten – nicht die der Person, deren Änderung den Bruch verursacht hat. So häufen sich keine kaputten Builds an, weil alle annehmen, jemand anderes kümmere sich darum.

### PR-Checks

- **Erforderliche Reviews:** Mindestens 1 Freigabe vor dem merge
- **Erforderliche Status-Checks:** CI muss vor dem merge bestehen
- **Branch-Schutz:** Keine Force-Pushes auf main
- **Auto-Merge:** Wenn alle Checks bestehen und freigegeben ist, automatisch mergen

## CI-Optimierung

Wenn die Pipeline länger als 10 Minuten dauert, wende diese Strategien in der Reihenfolge ihrer Wirkung an:

```
Slow CI pipeline?
├── Cache dependencies
│   └── Use the setup-node cache option (or actions/cache) for the package manager cache, not node_modules
├── Run jobs in parallel
│   └── Split lint, typecheck, test, build into separate parallel jobs
├── Only run what changed
│   └── Use path filters to skip unrelated jobs (e.g., skip e2e for docs-only PRs)
├── Use matrix builds
│   └── Shard test suites across multiple runners
├── Optimize the test suite
│   └── Remove slow tests from the critical path, run them on a schedule instead
└── Use larger runners
    └── GitHub-hosted larger runners or self-hosted for CPU-heavy builds
```

**Beispiel: Caching und Parallelisierung**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm test -- --coverage
```

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „CI ist zu langsam“ | Optimiere die Pipeline (siehe CI-Optimierung weiter oben), statt sie zu überspringen. Eine Pipeline von 5 Minuten erspart Stunden an Debugging. |
| „Diese Änderung ist trivial, CI überspringen“ | Triviale Änderungen brechen Builds. CI ist bei trivialen Änderungen ohnehin schnell. |
| „Der Test ist flaky, einfach neu starten“ | Flaky Tests verdecken echte Bugs und verschwenden die Zeit aller. Beseitige die Flakiness. |
| „CI richten wir später ein“ | Projekte ohne CI sammeln kaputte Zustände an. Richte es am ersten Tag ein. |
| „Manuelles Testen reicht“ | Manuelles Testen skaliert nicht und ist nicht wiederholbar. Automatisiere, was du kannst. |

## Warnsignale

- Keine CI-Pipeline im Projekt
- CI-Fehler werden ignoriert oder stummgeschaltet
- Tests in CI deaktiviert, damit die Pipeline durchläuft
- Produktions-Deploys ohne Verifikation im Staging
- Kein Rollback-Mechanismus
- Secrets in Code oder CI-Konfigurationsdateien gespeichert (nicht im Secrets-Manager)
- Lange CI-Laufzeiten ohne Optimierungsbemühungen

## Verifikation

Nach dem Einrichten oder Ändern von CI:

- [ ] Alle Quality Gates sind vorhanden (Lint, Typen, Tests, Build, Audit)
- [ ] Die Pipeline läuft bei jedem PR und jedem Push auf main
- [ ] Fehler blockieren den merge (Branch-Schutz ist konfiguriert)
- [ ] CI-Ergebnisse fließen in die Entwicklungsschleife zurück
- [ ] Secrets liegen im Secrets-Manager, nicht im Code
- [ ] Das Deployment hat einen Rollback-Mechanismus
- [ ] Die Pipeline läuft für die Test-Suite in unter 10 Minuten
