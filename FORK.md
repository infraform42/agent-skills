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

Konflikte in `description`-Zeilen, Manifesten oder Commands: Upstream-Fassung nehmen, dann `tools/fork_manifest.py` erneut ausführen.

## Offen

- Phase 2: Übersetzung ins Deutsche nach dem Muster von `infraform42/skills` (`tools/i18n.py`, `.i18n/translator-prompt.md`).
