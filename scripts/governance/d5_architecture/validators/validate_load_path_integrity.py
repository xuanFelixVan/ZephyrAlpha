# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_load_path_integrity.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_load_path_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
#!/usr/bin/env python3
"""
GATE-22: validate_load_path_integrity.py
"""

__manifest__ = """
args:
- --check
- --fix
- --warn-only
- --jsonl
description: "parse AGENTS.md §8.2 task menu (SKIP until §8.2 authored), verify referenced files exist. Anchored to AI加载路径不可漂移铁律"
dimensions:
- D5
priority: P0
timeout_seconds: 15
warn_only: false
"""

"""
Parses AGENTS.md §8.2 task menu (when authored), extracts all file
path references, and verifies each one exists on disk.

Authority: AI加载路径不可漂移铁律 (planned anchoring in AGENTS.md §6
关键路径). §8.2 task menu is intended as the single entry point
for AI to find rule files; path references there must never drift
from actual file locations.

Note: §8.2 is not yet authored -- when section 8.2 is absent the
checker SKIPs (returns EXIT_PASS with no parseable paths). Once
§8.2 is补建, this gate will enforce path integrity automatically.

Usage:
    python validate_load_path_integrity.py --check
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

AGENTS_PATH = REPO_ROOT / "AGENTS.md"

BASE_PATH = REPO_ROOT / "docs" / "01_policies_and_standards"

PATH_MAP = {
    "config/": REPO_ROOT,
    "docs/": REPO_ROOT,
    "scripts/": REPO_ROOT,
    "src/": REPO_ROOT,
    "pyproject.toml": REPO_ROOT,
    ".pre_commit-config.yaml": REPO_ROOT,
}


def extract_paths_from_agents_md() -> list[str]:
    """extract_paths_from_agents_md implementation."""
    content = AGENTS_PATH.read_text(encoding="utf-8")
    paths: set[str] = set()
    pattern = re.compile(r"`([a-zA-Z0-9_/.\-]+)`")
    blacklist = frozenset({".md", ".py", ".yaml", ".yml", ".md/.yaml/.yml", ".pre_commit-config"})

    in_section82 = False
    for line in content.split("\n"):
        if "8.2" in line and line.strip().startswith("###"):
            in_section82 = True
            continue
        if in_section82 and line.strip().startswith("###") and "8.2" not in line:
            break
        if not in_section82:
            continue

        for match in pattern.finditer(line):
            raw = match.group(1)
            if raw in blacklist:
                continue
            if "/" not in raw:
                continue
            if raw.endswith((".md", ".yaml", ".yml", ".py", ".toml")):
                paths.add(raw)

    return list(paths)


def resolve_path(ref: str) -> Path:
    """resolve_path implementation."""
    for prefix, root in PATH_MAP.items():
        if ref.startswith(prefix) or ref == prefix.rstrip("/"):
            return root / ref
    return BASE_PATH / ref.lstrip("/")


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="GATE-22: AGENTS.md §8.2 path drift check")
    parser.add_argument("--check", action="store_true", help="显式检查（历史兼容，默认同理）")
    parser.add_argument("--fix", action="store_true", help="无自动修复，仅保留接口")
    parser.add_argument("--warn-only", action="store_true", help="告警模式")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON 摘要")
    args = parser.parse_args()
    _ = (args.check, args.fix)
    paths = extract_paths_from_agents_md()

    if not paths:
        print("GATE-22 SKIP: no parseable path references found in section 8.2.")
        if args.jsonl:
            print(
                json.dumps(
                    {"severity": "INFO", "check_id": "GATE-22", "missing": 0, "note": "skip"},
                    ensure_ascii=False,
                )
            )
        return EXIT_PASS
    missing = []
    found = 0
    for p in sorted(paths):
        resolved = resolve_path(p)
        if resolved.exists():
            found += 1
        else:
            missing.append(str(p))

    total = len(paths)
    if not missing:
        print(f"GATE-22 PASS: all {total} paths in section 8.2 are reachable.")
        if args.jsonl:
            print(
                json.dumps(
                    {"severity": "INFO", "check_id": "GATE-22", "missing": 0, "total": total},
                    ensure_ascii=False,
                )
            )
        return EXIT_PASS
    print(f"GATE-22 FAIL: {len(missing)}/{total} paths are missing:")
    print(f"  passed: {found}")
    for m in missing[:10]:
        print(f"  missing: {m}")
    if len(missing) > 10:
        print(f"  ... and {len(missing) - 10} more")

    if args.jsonl:
        print(
            json.dumps(
                {
                    "severity": "HIGH",
                    "check_id": "GATE-22",
                    "missing": len(missing),
                    "total": total,
                },
                ensure_ascii=False,
            )
        )
    if args.warn_only:
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
