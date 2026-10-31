---
name: shipping-and-launch
description: Bereitet Produktions-Launches vor (Pre-Launch-Checkliste, Monitoring, gestaffelter Rollout, Rollback-Strategie). Verwenden, wenn ein Deployment in die Produktion vorbereitet wird oder wenn geklärt werden soll, was vor dem Shipping vorhanden sein muss. Verwenden bei Pre-Launch-Checkliste, Monitoring-Einrichtung, gestaffeltem Rollout oder Rollback-Strategie. Typische Formulierungen „bereite den Launch vor“, „was brauchen wir vor dem Go-live?“, „erstell eine Pre-Launch-Checkliste“, „plane den gestaffelten Rollout“, „schreib einen Rollback-Plan“.
---

# Auslieferung und Launch

## Überblick

Liefere mit Zuversicht aus. Das Ziel ist nicht nur zu deployen, sondern sicher zu deployen: mit eingerichtetem Monitoring, einem bereitliegenden Rollback-Plan und einem klaren Verständnis davon, wie Erfolg aussieht. Jeder Launch sollte umkehrbar, beobachtbar und inkrementell sein.

## Wann verwenden

- Ein Feature zum ersten Mal in die Produktion deployen
- Eine wesentliche Änderung für Nutzer veröffentlichen
- Daten oder Infrastruktur migrieren
- Ein Beta- oder Early-Access-Programm eröffnen
- Jedes Deployment, das ein Risiko birgt (also alle)

## Die Pre-Launch-Checkliste

### Codequalität

- [ ] Alle Tests bestehen (Unit, Integration, e2e)
- [ ] Der Build läuft ohne Warnungen durch
- [ ] Lint und Typprüfung bestehen
- [ ] Code wurde geprüft und freigegeben
- [ ] Keine TODO-Kommentare, die vor dem Launch erledigt werden sollten
- [ ] Keine `console.log`-Debugging-Anweisungen im Produktionscode
- [ ] Die Fehlerbehandlung deckt die erwarteten Fehlerfälle ab

### Sicherheit

- [ ] Keine Secrets im Code oder in der Versionsverwaltung
- [ ] Das Dependency-Audit des Ökosystems (`npm audit`, `pip-audit`, `cargo audit`, ...) zeigt keine kritischen oder hohen Schwachstellen
- [ ] Eingabevalidierung an allen nutzerseitigen Endpunkten
- [ ] Authentifizierungs- und Autorisierungsprüfungen sind vorhanden
- [ ] Security-Header sind konfiguriert (CSP, HSTS usw.)
- [ ] Rate Limiting an Authentifizierungs-Endpunkten
- [ ] CORS ist auf konkrete Origins konfiguriert (kein Wildcard)

### Performance

- [ ] Core Web Vitals innerhalb der „Good“-Schwellenwerte
- [ ] Keine N+1-Queries in kritischen Pfaden
- [ ] Bilder sind optimiert (Kompression, responsive Größen, Lazy Loading)
- [ ] Bundle-Größe innerhalb des Budgets
- [ ] Datenbankabfragen haben passende Indizes
- [ ] Caching ist für statische Assets und wiederholte Abfragen konfiguriert

### Barrierefreiheit

- [ ] Tastaturnavigation funktioniert für alle interaktiven Elemente
- [ ] Ein Screenreader kann Inhalt und Struktur der Seite vermitteln
- [ ] Farbkontrast erfüllt WCAG 2.1 AA (4,5:1 für Text)
- [ ] Fokusmanagement ist für Modals und dynamische Inhalte korrekt
- [ ] Fehlermeldungen sind aussagekräftig und mit den Formularfeldern verknüpft
- [ ] Keine Barrierefreiheits-Warnungen in axe-core oder Lighthouse

### Infrastruktur

- [ ] Umgebungsvariablen sind in der Produktion gesetzt
- [ ] Datenbank-Migrationen sind angewendet (oder anwendungsbereit)
- [ ] DNS und SSL sind konfiguriert
- [ ] CDN ist für statische Assets konfiguriert
- [ ] Logging und Error Reporting sind konfiguriert
- [ ] Ein Health-Check-Endpunkt existiert und antwortet

### Dokumentation

- [ ] README um neue Setup-Anforderungen ergänzt
- [ ] API-Dokumentation ist aktuell
- [ ] ADRs für alle Architekturentscheidungen geschrieben
- [ ] Changelog aktualisiert
- [ ] Nutzerdokumentation aktualisiert (falls zutreffend)

## Feature-Flag-Strategie

Liefere hinter Feature-Flags aus, um Deployment und Release zu entkoppeln:

```typescript
// Feature flag check
const flags = await getFeatureFlags(userId);

if (flags.taskSharing) {
  // New feature: task sharing
  return <TaskSharingPanel task={task} />;
}

// Default: existing behavior
return null;
```

**Lebenszyklus eines Feature-Flags:**

```
1. DEPLOY with flag OFF     → Code is in production but inactive
2. ENABLE for team/beta     → Internal testing in production environment
3. GRADUAL ROLLOUT          → 5% → 25% → 50% → 100% of users
4. MONITOR at each stage    → Watch error rates, performance, user feedback
5. CLEAN UP                 → Remove flag and dead code path after full rollout
```

**Regeln:**
- Jedes Feature-Flag hat einen Verantwortlichen und ein Ablaufdatum
- Räume Flags innerhalb von 2 Wochen nach dem vollständigen Rollout auf
- Verschachtele Feature-Flags nicht (erzeugt exponentiell viele Kombinationen)
- Teste beide Flag-Zustände (an und aus) in CI

## Gestaffelter Rollout

### Die Rollout-Abfolge

```
1. DEPLOY to staging
   └── Full test suite in staging environment
   └── Manual smoke test of critical flows

2. DEPLOY to production (feature flag OFF)
   └── Verify deployment succeeded (health check)
   └── Check error monitoring (no new errors)

3. ENABLE for team (flag ON for internal users)
   └── Team uses the feature in production
   └── 24-hour monitoring window

4. CANARY rollout (flag ON for 5% of users)
   └── Monitor error rates, latency, user behavior
   └── Compare metrics: canary vs. baseline
   └── 24-48 hour monitoring window
   └── Advance only if all thresholds pass (see table below)

5. GRADUAL increase (25% -> 50% -> 100%)
   └── Same monitoring at each step
   └── Ability to roll back to previous percentage at any point

6. FULL rollout (flag ON for all users)
   └── Monitor for 1 week
   └── Clean up feature flag
```

### Schwellenwerte für Rollout-Entscheidungen

Nutze diese Schwellenwerte, um in jeder Phase zu entscheiden, ob du fortfährst, anhältst oder zurückrollst:

| Metrik | Fortfahren (grün) | Anhalten und untersuchen (gelb) | Zurückrollen (rot) |
|--------|-------------------|---------------------------------|--------------------|
| Fehlerrate | Innerhalb von 10 % der Baseline | 10–100 % über der Baseline | >2x Baseline |
| P95-Latenz | Innerhalb von 20 % der Baseline | 20–50 % über der Baseline | >50 % über der Baseline |
| Client-JS-Fehler | Keine neuen Fehlertypen | Neue Fehler bei <0,1 % der Sessions | Neue Fehler bei >0,1 % der Sessions |
| Geschäftsmetriken | Neutral oder positiv | Rückgang <5 % (kann Rauschen sein) | Rückgang >5 % |

### Wann du zurückrollst

Rolle sofort zurück, wenn:
- die Fehlerrate um mehr als das 2-Fache der Baseline steigt
- die P95-Latenz um mehr als 50 % steigt
- von Nutzern gemeldete Issues sprunghaft zunehmen
- Datenintegritätsprobleme erkannt werden
- eine Sicherheitslücke entdeckt wird

## Monitoring und Observability

### Was du überwachst

```
Application metrics:
├── Error rate (total and by endpoint)
├── Response time (p50, p95, p99)
├── Request volume
├── Active users
└── Key business metrics (conversion, engagement)

Infrastructure metrics:
├── CPU and memory utilization
├── Database connection pool usage
├── Disk space
├── Network latency
└── Queue depth (if applicable)

Client metrics:
├── Core Web Vitals (LCP, INP, CLS)
├── JavaScript errors
├── API error rates from client perspective
└── Page load time
```

### Error Reporting

```typescript
// Set up error boundary with reporting
class ErrorBoundary extends React.Component<React.PropsWithChildren> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Report to error tracking service
    reportError(error, {
      componentStack: info.componentStack,
      userId: getCurrentUser()?.id,
      page: window.location.pathname,
    });
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback onRetry={() => this.setState({ hasError: false })} />;
    }
    return this.props.children;
  }
}

// Server-side error reporting
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  reportError(err, {
    method: req.method,
    url: req.url,
    userId: req.user?.id,
  });

  // Don't expose internals to users
  res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' },
  });
});
```

### Verifikation nach dem Launch

In der ersten Stunde nach dem Launch:

```
1. Check health endpoint returns 200
2. Check error monitoring dashboard (no new error types)
3. Check latency dashboard (no regression)
4. Test the critical user flow manually
5. Verify logs are flowing and readable
6. Confirm rollback mechanism works (dry run if possible)
```

## Error-Budget als Release-Gate

Das Error-Budget deines Services – der Anteil an Requests oder Zeit, den dein SLO als fehlgeschlagen zulässt – bestimmt, ob Shipping sicher ist. Nutze es als objektives Gate, nicht als Verhandlungssache:

```
Budget remaining > 20%  →  Ship normally; monitor closely
Budget remaining 0–20%  →  Slow rollouts only; no high-risk changes
Budget exhausted        →  Freeze feature work; focus entirely on reliability
Budget resets           →  Resume normal pace; bake in the fix that recovered it
```

Eine hohe Burn Rate während eines Canary (das Budget wird schneller verbraucht als im Baseline-Tempo) ist in der obigen Tabelle der Rollout-Schwellenwerte ein **Anhalten**-Signal – behandle sie genauso wie eine erhöhte Fehlerrate.

## Rollback-Strategie

Jedes Deployment braucht einen Rollback-Plan, bevor es stattfindet:

```markdown
## Rollback Plan for [Feature/Release]

### Trigger Conditions
- Error rate > 2x baseline
- P95 latency > [X]ms
- User reports of [specific issue]

### Rollback Steps
1. Disable feature flag (if applicable)
   OR
1. Deploy previous version: `git revert <commit> && git push`
2. Verify rollback: health check, error monitoring
3. Communicate: notify team of rollback

### Database Considerations
- Migration [X] has a rollback: <verified command or runbook link>
- Data inserted by new feature: [preserved / cleaned up]

### Time to Rollback
- Feature flag: < 1 minute
- Redeploy previous version: < 5 minutes
- Database rollback: < 15 minutes
```
## Siehe auch

- Die projektweite Definition of Done, die jede Änderung vor dieser Checkliste erfüllen muss, findest du in `../../references/definition-of-done.md`
- Sicherheitsprüfungen vor dem Launch findest du in `../../references/security-checklist.md`
- Die Performance-Checkliste vor dem Launch findest du in `../../references/performance-checklist.md`
- Die Verifikation der Barrierefreiheit vor dem Launch findest du in `../../references/accessibility-checklist.md`
- Alerting-Regeln und SLO-gebundene Schwellenwerte findest du in `observability-and-instrumentation`

## Häufige Ausreden

| Ausrede | Realität |
|---|---|
| „Es funktioniert im Staging, also funktioniert es auch in der Produktion“ | Die Produktion hat andere Daten, Traffic-Muster und Randfälle. Überwache nach dem Deployment. |
| „Dafür brauchen wir keine Feature-Flags“ | Jedes Feature profitiert von einem Kill-Switch. Selbst „einfache“ Änderungen können etwas kaputt machen. |
| „Monitoring ist Overhead“ | Ohne Monitoring erfährst du von Problemen durch Nutzerbeschwerden statt durch Dashboards. |
| „Monitoring ergänzen wir später“ | Richte es vor dem Launch ein. Du kannst nicht debuggen, was du nicht siehst. |
| „Ein Rollback ist ein Eingeständnis des Scheiterns“ | Ein Rollback ist verantwortungsvolles Engineering. Das Scheitern ist, ein kaputtes Feature auszuliefern. |
| „Die Fehlerrate sieht gut aus, liefern wir weiter aus“ | Prüfe die Burn Rate, nicht nur die aktuelle Fehlerrate. Ein schnellerer Budgetverbrauch als die Baseline ist ein Anhalten-Signal, auch wenn einzelne Schwellenwerte grün sind. |

## Warnsignale

- Deployment ohne Rollback-Plan
- Kein Monitoring oder Error Reporting in der Produktion
- Big-Bang-Releases (alles auf einmal, kein Staging)
- Feature-Flags ohne Ablaufdatum oder Verantwortlichen
- Niemand überwacht das Deployment in der ersten Stunde
- Konfiguration der Produktionsumgebung aus dem Gedächtnis statt als Code
- „Es ist Freitagnachmittag, liefern wir es aus“
- Error-Budget ist aufgebraucht, aber die Feature-Arbeit läuft unverändert weiter

## Verifikation

Vor dem Deployment:

- [ ] Pre-Launch-Checkliste abgeschlossen (alle Abschnitte grün)
- [ ] Feature-Flag konfiguriert (falls zutreffend)
- [ ] Rollback-Plan dokumentiert
- [ ] Monitoring-Dashboards eingerichtet
- [ ] Team über das Deployment informiert

Nach dem Deployment:

- [ ] Health-Check liefert 200
- [ ] Fehlerrate ist normal
- [ ] Latenz ist normal
- [ ] Kritischer Nutzerfluss funktioniert
- [ ] Logs fließen
- [ ] Rollback getestet oder als bereit verifiziert

Für jeden ausgelieferten Service:

- [ ] Error-Budget-Policy ist vorhanden: Du weißt, welche Maßnahme greift, wenn das Budget unter 20 % fällt und wenn es aufgebraucht ist
