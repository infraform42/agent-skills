#!/usr/bin/env python3
"""i18n-Werkzeug für den de-Branch von infraform42/agent-skills.

  python tools/i18n.py list             # ausgelieferte SKILL.md, Commands, Agents (auf main)
  python tools/i18n.py stale            # neu oder veraltet → zu übersetzen
  python tools/i18n.py translate PFAD   # genau eine Datei übersetzen

Danach immer tools/fork_manifest.py ausführen (Namespace, MacPorts, Overrides).
"""
import fcntl
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / ".i18n" / "translations.lock.json"
PROMPT = ROOT / ".i18n" / "translator-prompt.md"
EN_REF = "main"
MODEL = "sonnet"
FENCE = re.compile(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", re.S | re.M)
INLINE = re.compile(r"`[^`\n]+`")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def en(path: str) -> str:
    return git("show", f"{EN_REF}:{path}")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def shipped_skill_files() -> list[str]:
    roots = json.loads(en(".claude-plugin/plugin.json")).get("skills")
    if not roots:
        sys.exit("plugin.json ohne skills-Feld – Skill-Liste manuell prüfen")
    roots = [roots] if isinstance(roots, str) else roots
    paths = [r.removeprefix("./").rstrip("/") for r in roots]
    files = git("ls-tree", "-r", "--name-only", EN_REF, "--", *paths).splitlines()
    extra = git("ls-tree", "-r", "--name-only", EN_REF, "--", ".claude/commands", "agents", "references").splitlines()
    # Unterlagen der Skills (references/, examples.md usw.) ohne Frontmatter
    docs = [f for f in files if f.endswith(".md") and not f.endswith("/SKILL.md")]
    return sorted([f for f in files if f.endswith("/SKILL.md")] + docs +
                  [f for f in extra if f.endswith(".md")])


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n")


def split(text: str) -> tuple[dict, str]:
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError("Frontmatter fehlt oder beginnt nicht in Zeile 1")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def fences(body: str) -> list[str]:
    return [m.group(0) for m in FENCE.finditer(body)]


def verify(src: str, dst: str) -> None:
    if not has_frontmatter(src):
        verify_body(src, dst)
        return
    fs, bs = split(src)
    fd, bd = split(dst)
    if list(fs) != list(fd):
        raise ValueError(f"Frontmatter-Schlüssel geändert: {list(fs)} → {list(fd)}")
    changed = [k for k in fs if k != "description" and fs[k] != fd[k]]
    if changed:
        raise ValueError(f"Felder dürfen nicht übersetzt werden: {changed}")
    if len(str(fd.get("description", ""))) > 1024:
        raise ValueError("description > 1024 Zeichen")
    verify_body(bs, bd)


def verify_body(bs: str, bd: str) -> None:
    if has_frontmatter(bd) and not has_frontmatter(bs):
        raise ValueError("Frontmatter hinzugefügt")
    first = lambda t: t.lstrip().split("\n", 1)[0]
    if first(bs).startswith("#") and not first(bd).startswith("#"):
        raise ValueError(f"Beginnt nicht mit Überschrift (Vorrede?): {first(bd)[:60]!r}")
    if fences(bs) != fences(bd):
        raise ValueError("Codeblöcke verändert")
    lost = set(INLINE.findall(FENCE.sub("", bs))) - set(INLINE.findall(FENCE.sub("", bd)))
    if lost:
        raise ValueError(f"Inline-Code fehlt/verändert: {sorted(lost)[:8]}")


def load_lock() -> dict:
    return json.loads(LOCK.read_text()) if LOCK.exists() else {}


def save_lock(lock: dict) -> None:
    LOCK.write_text(json.dumps(lock, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def stale() -> None:
    lock, files = load_lock(), shipped_skill_files()
    for p in files:
        if lock.get(p, {}).get("source_sha256") != sha(en(p)):
            print(p)
    for p in sorted(set(lock) - set(files)):
        print(f"ENTFERNT/UMBENANNT upstream: {p}", file=sys.stderr)


def claude_cmd() -> list[str]:
    help_text = subprocess.run(["claude", "--help"], capture_output=True, text=True).stdout
    if "--tools" not in help_text:
        sys.exit("claude kennt --tools nicht – Claude Code aktualisieren")
    return ["claude", "-p", "--output-format", "json", "--model", MODEL,
            "--tools", "", "--permission-mode", "default",
            "--system-prompt", PROMPT.read_text()]


def clean(raw: str, frontmatter: bool = True) -> str:
    """Entfernt Vorrede und umschließenden Markdown-Fence (auch mit 4+ Backticks)."""
    out = raw.strip()
    if not frontmatter:
        # Ohne Frontmatter kein Anker für eine Vorrede; nur einen Fence um die ganze Datei entfernen
        m = re.match(r"\A(`{3,}|~{3,})[a-z]*\n(.*)\n\1\Z", out, re.S)
        return (m.group(2) if m else out).rstrip() + "\n"
    lead = re.search(r"^---\n", out, re.M)
    if lead and lead.start() > 0:
        prefix, out = out[:lead.start()], out[lead.start():]
        if re.search(r"`{3,}", prefix):
            out = re.sub(r"\n`{3,}[ \t]*\Z", "", out.rstrip())
    return out.rstrip() + "\n"


def restore_fences(src: str, dst: str) -> str:
    """Ersetzt die Codeblöcke der Übersetzung der Reihe nach durch die Originale."""
    orig, got = fences(src), fences(dst)
    if len(orig) != len(got):
        raise ValueError(f"Anzahl Codeblöcke geändert: {len(orig)} → {len(got)}")
    it = iter(orig)
    return FENCE.sub(lambda m: next(it), dst)


def restore_inline(src: str, dst: str) -> str:
    """Setzt Inline-Code außerhalb von Codeblöcken der Reihe nach auf die Originale zurück.

    Sonnet übersetzt gelegentlich Wörter in Inline-Code (z. B. `max × instances`). Stimmt die
    Anzahl nicht überein, bleibt die Übersetzung unverändert und verify() meldet den Fehler.
    """
    orig = INLINE.findall(FENCE.sub("", src))
    # Text zwischen den Codeblöcken (gerade Indizes) und Codeblöcke selbst (ungerade) im Wechsel
    parts, pos = [], 0
    for m in FENCE.finditer(dst):
        parts += [dst[pos:m.start()], m.group(0)]
        pos = m.end()
    parts.append(dst[pos:])
    if sum(len(INLINE.findall(t)) for t in parts[0::2]) != len(orig):
        return dst
    it = iter(orig)
    for i in range(0, len(parts), 2):
        parts[i] = INLINE.sub(lambda m: next(it), parts[i])
    return "".join(parts)


OVERRIDES = ROOT / ".i18n" / "overrides.yaml"


def apply_override(path: str, text: str) -> str:
    """Setzt eine feste description aus .i18n/overrides.yaml (einzeilige description vorausgesetzt)."""
    if not OVERRIDES.exists():
        return text
    ov = (yaml.safe_load(OVERRIDES.read_text()) or {}).get(path) or {}
    if "description" not in ov:
        return text
    if ov.get("source_sha256") and ov["source_sha256"] != sha(en(path)):
        print(f"HINWEIS {path}: englische Quelle seit Override geändert – description prüfen", file=sys.stderr)
    line = "description: " + json.dumps(ov["description"], ensure_ascii=False)
    new, n = re.subn(r"^description:.*$", lambda m: line, text, count=1, flags=re.M)
    if n != 1:
        raise ValueError("description-Zeile für Override nicht gefunden")
    return new


def translate(path: str) -> None:
    src = en(path)
    res = subprocess.run(
        [*claude_cmd(), f"Übersetze die über stdin gelieferte Datei `{path}` gemäß den Regeln."],
        input=src, capture_output=True, text=True, cwd=tempfile.gettempdir())
    if res.returncode:
        raise RuntimeError(res.stderr.strip() or res.stdout[:500])
    data = json.loads(res.stdout)
    if data.get("is_error"):
        raise RuntimeError(str(data.get("result")))
    out = clean(data["result"], has_frontmatter(src))
    out = restore_fences(src, out)
    out = restore_inline(src, out)
    out = apply_override(path, out)
    Path(tempfile.gettempdir(), "i18n_" + path.replace("/", "_")).write_text(data["result"])
    verify(src, out)
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out)
    # Sperre, damit parallele Läufe (xargs -P) das Lockfile nicht überschreiben
    with open(LOCK.with_suffix(".flock"), "w") as fl:
        fcntl.flock(fl, fcntl.LOCK_EX)
        lock = load_lock()
        lock[path] = {"source_sha256": sha(src),
                      "upstream_commit": git("rev-parse", EN_REF).strip(),
                      "translated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        save_lock(lock)
    print(f"OK {path}  (Kosten: {data.get('total_cost_usd', '?')} USD)")


def main() -> None:
    cmd, *rest = sys.argv[1:] or ["stale"]
    try:
        if cmd == "list":
            print(*shipped_skill_files(), sep="\n")
        elif cmd in ("stale", "stale-ci"):
            stale()
        elif cmd == "translate" and len(rest) == 1:
            translate(rest[0])
        else:
            sys.exit(__doc__)
    except (ValueError, RuntimeError, yaml.YAMLError) as e:
        sys.exit(f"FEHLER {rest[0] if rest else cmd}: {e}")


if __name__ == "__main__":
    main()
