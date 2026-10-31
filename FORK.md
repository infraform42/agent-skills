# Fork infraform42/agent-skills (Branch `de`)

Fork von [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), angepasst an die infraform42-Umgebung. `main` folgt Upstream unverändert, `de` trägt die Anpassungen und ist Standard-Branch.

## Installation

```bash
claude plugin marketplace add infraform42/agent-skills
claude plugin install agent-skills-de@infraform42-agent-skills
```

## Anpassungen

Alle Anpassungen setzt `tools/fork_manifest.py`:

- Pluginname `agent-skills-de`, Marketplace `infraform42-agent-skills`, keine `version` (Updates folgen dem Commit).
- Nur `./.claude/commands` als Commands; `./commands` enthält Gemini-TOML.
- Commands rufen Skills als `agent-skills-de:<skill>` auf.
- `brew install` → `sudo port install` (MacPorts).
- Skills, die sich mit `mattpocock-skills-de` oder eingebauten Skills überschneiden, bekommen eine enge `description` aus `.i18n/overrides.yaml` und lösen nicht mehr automatisch aus. Die Commands rufen sie weiterhin auf.
- `git-workflow-and-versioning`: Übersetzung ohne den Upstream-Satz „Verwenden bei jeder Codeänderung“ (ebenfalls `.i18n/overrides.yaml`). Eine freie Neufassung hatte das Auslösen bei Commit-Nachrichten verhindert; Änderungen an dieser description immer mit den gitflow-Evals prüfen (nächster Abschnitt).
- Feste deutsche H1-Titel aus `.i18n/titles.yaml` (erste `# `-Zeile außerhalb von Codeblöcken).
- Die Hooks unter `hooks/` sind nicht eingebunden (wie upstream).

## Evals

Die Upstream-Evals liegen unter `evals/plugin/`; die Fälle `*-de` sind Fork-eigene deutsche Fälle. Fälle, die ein automatisches Auslösen von Skills erwarten, die der Fork bewusst nur per Command zulässt (z. B. `tdd-fires-*`, `code-review-fires`), schlagen im Fork erwartungsgemäß fehl.

```bash
claude plugin eval agent-skills-de@infraform42-agent-skills --case 'gitflow-*' --runs 2 \
  --ablation none --model sonnet --no-publish --trust-plugin --max-cost-usd 2
```

## Upstream beobachten

`tools/upstream-check.sh` holt nur `upstream/main` und meldet neue Commits als macOS-Mitteilung; Branches und Arbeitsverzeichnis bleiben unberührt. `tools/install-upstream-check.sh` richtet das als launchd-Job ein (montags 09:00, Log `~/Library/Logs/agent-skills-upstream.log`), `--remove` entfernt ihn.

## Weitere Hosts

opencode v2 lädt die Skills über `"skills": ["~/src/agent-skills-de/skills"]` in `~/.config/opencode/opencode.jsonc` (alle `**/SKILL.md`). Die Commands und Agents gibt es dort nicht; die nur per Command gedachten Skills verweisen auf `/agent-skills-de:*`-Commands von Claude Code.

## Upstream übernehmen

```bash
git fetch upstream
git switch main && git merge --ff-only upstream/main && git push origin main
git switch de && git merge main
/opt/local/bin/python3.14 -I tools/fork_manifest.py
claude plugin validate .
```

Konflikte in `description`-Zeilen, Manifesten oder Commands: Upstream-Fassung nehmen, dann `tools/fork_manifest.py` erneut ausführen. Danach geänderte Dateien neu übersetzen (nächster Abschnitt).

## Übersetzung

Alle `SKILL.md`, Commands (`.claude/commands/*.md`), Agents (`agents/*.md`) und Unterlagen (`references/*.md`, weitere `.md` in `skills/`) sind ins Deutsche übersetzt, nach dem Muster von `infraform42/skills`; zusammen 51 Dateien.

```bash
~/venvs/skills-i18n/bin/python -I tools/i18n.py stale   # neu oder veraltet gegenüber main
tools/translate-stale.sh                                # übersetzt alles Offene (4 parallel), dann fork_manifest.py
```

- Übersetzt wird mit `claude -p` (Sonnet), Regeln und Glossar in `.i18n/translator-prompt.md`, Stand in `.i18n/translations.lock.json`.
- `i18n.py` setzt Codeblöcke und Inline-Code positionsgenau auf die Originale zurück und prüft danach Frontmatter, Codeblöcke und Inline-Code. Unterlagen ohne Frontmatter müssen wie das Original mit einer Überschrift beginnen. Meldet es trotzdem „Inline-Code verändert“ (abweichende Anzahl), die Rohausgabe (`$TMPDIR/i18n_<pfad>`) prüfen oder erneut übersetzen.
- Ist eine `description` mit deutschen Triggern länger als 1024 Zeichen, eine feste Fassung in `.i18n/overrides.yaml` setzen.
