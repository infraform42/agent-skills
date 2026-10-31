#!/usr/bin/env python3
"""Setzt die Fork-Anpassungen für infraform42/agent-skills (Branch de).

Nach jedem Upstream-Merge ausführen; das Skript ist idempotent:
  /opt/local/bin/python3.14 -I tools/fork_manifest.py
"""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / ".claude-plugin"
PLUGIN = "agent-skills-de"
MARKET = "infraform42-agent-skills"
REPO = "https://github.com/infraform42/agent-skills"
DESC = "Addy Osmanis Agent-Skills, angepasst für infraform42 (Fork von addyosmani/agent-skills)."
OVERRIDES = ROOT / ".i18n" / "overrides.yaml"
# Homebrew-Installationen → MacPorts
PORTS = {"brew install gitleaks": "sudo port install gitleaks",
         "brew install osv-scanner": "sudo port install osv-scanner"}


def rw(name, fn):
    p = DIR / name
    data = json.loads(p.read_text())
    fn(data)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def plugin(m):
    m.update(name=PLUGIN, description=DESC, repository=REPO, homepage=REPO)
    m.update(author={"name": "Addy Osmani", "url": "https://github.com/addyosmani"})
    m["commands"] = ["./.claude/commands"]  # ./commands enthält nur Gemini-TOML
    m.pop("version", None)


def market(m):
    m["name"] = MARKET
    m["owner"] = {"name": "infraform42"}
    m["description"] = DESC
    m["plugins"] = [{"name": PLUGIN, "source": "./", "description": DESC,
                     "homepage": REPO, "license": "MIT",
                     "keywords": ["skills", "engineering", "spec", "review", "ship"]}]


def namespace():
    """Commands rufen Skills als agent-skills:<name> auf → Pluginname des Forks."""
    for p in (ROOT / ".claude" / "commands").glob("*.md"):
        text = p.read_text()
        new = re.sub(r"\bagent-skills:", f"{PLUGIN}:", text)
        if new != text:
            p.write_text(new)


def macports():
    for p in (ROOT / "skills").rglob("*.md"):
        text = p.read_text()
        new = text
        for a, b in PORTS.items():
            new = new.replace(a, b)
        if new != text:
            p.write_text(new)


def overrides():
    """Setzt feste descriptions (einzeilige description vorausgesetzt)."""
    for path, ov in (yaml.safe_load(OVERRIDES.read_text()) or {}).items():
        if "description" not in ov:
            continue
        p = ROOT / path
        line = "description: " + json.dumps(ov["description"], ensure_ascii=False)
        text, n = re.subn(r"^description:.*$", lambda m: line, p.read_text(), count=1, flags=re.M)
        if n != 1:
            raise SystemExit(f"description-Zeile nicht gefunden: {path}")
        if len(ov["description"]) > 1024:
            raise SystemExit(f"description > 1024 Zeichen: {path}")
        p.write_text(text)


if __name__ == "__main__":
    rw("plugin.json", plugin)
    rw("marketplace.json", market)
    namespace()
    macports()
    overrides()
