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
- Die Hooks unter `hooks/` sind nicht eingebunden (wie upstream).

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

Alle `SKILL.md`, Commands (`.claude/commands/*.md`) und Agents (`agents/*.md`) sind ins Deutsche übersetzt, nach dem Muster von `infraform42/skills`. Unterlagen von Skills (`references/`, `examples.md` usw.) bleiben englisch.

```bash
~/venvs/skills-i18n/bin/python -I tools/i18n.py stale   # neu oder veraltet gegenüber main
tools/translate-stale.sh                                # übersetzt alles Offene (4 parallel), dann fork_manifest.py
```

- Übersetzt wird mit `claude -p` (Sonnet), Regeln und Glossar in `.i18n/translator-prompt.md`, Stand in `.i18n/translations.lock.json`.
- `i18n.py` prüft Frontmatter, Codeblöcke und Inline-Code. Bei „Inline-Code verändert“ die Rohausgabe (`$TMPDIR/i18n_<pfad>`) korrigieren oder erneut übersetzen.
- Ist eine `description` mit deutschen Triggern länger als 1024 Zeichen, eine feste Fassung in `.i18n/overrides.yaml` setzen.
