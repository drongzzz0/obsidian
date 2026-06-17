from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {".git", ".pytest_cache", ".ruff_cache", ".mypy_cache", "__pycache__", ".venv", "tmp", ".runtime"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".pyc", ".sqlite", ".sqlite3", ".db"}
LOCAL_DENY_FILE = ".public-scan-local.txt"


@dataclass(frozen=True)
class PatternRule:
    label: str
    pattern: re.Pattern[str]


GENERIC_PATH_PATTERNS = [
    r"[A-Za-z]:" + re.escape("\\"),
    re.escape("/home/"),
    re.escape("/Users/"),
]


BASE_RULES = [
    PatternRule(
        "absolute path",
        re.compile("|".join(GENERIC_PATH_PATTERNS)),
    ),
    PatternRule(
        "concrete secret",
        re.compile(
            r"sk-[A-Za-z0-9]|BEGIN [A-Z ]*PRIVATE KEY|bearer\s+[A-Za-z0-9._-]+|"
            r"(api[_-]?key|auth[_-]?token|password|secret)\s*[:=]\s*['\"][^'\"]+",
            re.IGNORECASE,
        ),
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan public repository files for local paths, secrets, and private traces."
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()

    matches = scan(args.root)
    for label, path, line_no, line in matches:
        print(f"{label}: {path}:{line_no}: {line}")
    if matches:
        print(f"Found {len(matches)} public hygiene issue(s).")
        return 1
    print("NO_MATCH")
    return 0


def scan(root: Path) -> list[tuple[str, Path, int, str]]:
    root = root.resolve()
    rules = [*BASE_RULES, *local_deny_rules(root / LOCAL_DENY_FILE)]
    matches: list[tuple[str, Path, int, str]] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        rel_path = path.relative_to(root)
        for line_no, line in enumerate(text.splitlines(), start=1):
            for rule in rules:
                if rule.pattern.search(line):
                    if is_allowed_internal_rule_definition(rel_path, rule.label, line):
                        continue
                    matches.append((rule.label, rel_path, line_no, line.strip()))
    return matches


def is_allowed_internal_rule_definition(rel_path: Path, label: str, line: str) -> bool:
    if rel_path.as_posix() != "scripts/public_repo_scan.py" or label != "absolute path":
        return False
    return 're.escape("/home/")' in line or 're.escape("/Users/")' in line


def local_deny_rules(path: Path) -> list[PatternRule]:
    if not path.exists():
        return []
    terms = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        term = raw.strip()
        if not term or term.startswith("#"):
            continue
        terms.append(term)
    if not terms:
        return []
    return [PatternRule("local deny term", re.compile("|".join(re.escape(term) for term in terms), re.IGNORECASE))]


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if path.name == LOCAL_DENY_FILE:
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        yield path


if __name__ == "__main__":
    raise SystemExit(main())
