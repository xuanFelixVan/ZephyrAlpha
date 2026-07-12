# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.gitignore_auditor
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; tests/audit/test_gitignore_auditor.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计结果不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_gitignore_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
.gitignore Integrity Auditor — gitignore完整性审计 D-023-32 · §6.24。





module_id: MOD-INF-023


untracked_generated_files: 扫描可能生成的文件(*.pkl/*.joblib/*.cache)检查gitignore


over_ignored_critical_files: 规则模拟检查误匹配


gitignore_pattern_coverage: 新文件类型未被覆盖建议添加


对标 blueprint.md §6.24。"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import fnmatch
import os
from dataclasses import dataclass, field

GENERATED_FILE_EXTENSIONS: Final[set[str]] = {
    ".pkl",
    ".joblib",
    ".cache",
    ".pyc",
    ".pyo",
    ".egg",
    ".whl",
    ".tar.gz",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".log",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".lock",
}


CRITICAL_FILE_EXTENSIONS: Final[set[str]] = {
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".cfg",
    ".ini",
    ".env",
    ".md",
}


CRITICAL_FILE_PATTERNS: Final[list[str]] = [
    "project.godot",
    "AGENTS.md",
    "*.py",
    "*.yaml",
    "*.yml",
    "*.json",
    "*.toml",
    ".env",
]


@dataclass
class GitignoreAudit:
    project_root: str = ""

    gitignore_rules: list[str] = field(default_factory=list)

    untracked_generated: list[str] = field(default_factory=list)

    over_ignored: list[str] = field(default_factory=list)

    uncovered_types: list[str] = field(default_factory=list)

    suggestions: list[str] = field(default_factory=list)


def parse_gitignore(project_root: str) -> list[str]:
    rules: list[str] = []

    gi_path = os.path.join(project_root, ".gitignore")

    if not os.path.exists(gi_path):
        return rules

    try:
        with open(gi_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if line and not line.startswith("#"):
                    rules.append(line.rstrip("/"))

    except Exception as e:
        logger.warning("suppressed error in gitignore_auditor", exc_info=True)

    return rules


def _is_ignored(filepath: str, rules: list[str]) -> bool:
    rel_path = filepath.replace("\\", "/")

    for rule in rules:
        if fnmatch.fnmatch(rel_path, rule):
            return True

        if fnmatch.fnmatch(os.path.basename(rel_path), rule):
            return True

    return False


def find_untracked_generated(
    project_root: str,
    rules: list[str],
) -> list[str]:
    untracked: list[str] = []

    skip_dirs: set[str] = {".git", "__pycache__", "node_modules", ".venv", "venv"}

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()

            if ext in GENERATED_FILE_EXTENSIONS or fname.endswith(".db"):
                full_path = os.path.join(root, fname)

                rel = os.path.relpath(full_path, project_root)

                if not _is_ignored(rel, rules):
                    untracked.append(rel)

    return untracked


def find_over_ignored_critical(
    project_root: str,
    rules: list[str],
) -> list[str]:
    over_ignored: list[str] = []

    skip_dirs: set[str] = {".git", "__pycache__", "node_modules", ".venv", "venv"}

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()

            if ext in CRITICAL_FILE_EXTENSIONS:
                full_path = os.path.join(root, fname)

                rel = os.path.relpath(full_path, project_root)

                if _is_ignored(rel, rules):
                    over_ignored.append(rel)

    return over_ignored


def find_uncovered_types(
    project_root: str,
    rules: list[str],
) -> list[str]:
    uncovered: set[str] = set()

    skip_dirs: set[str] = {".git", "__pycache__", "node_modules", ".venv", "venv"}

    seen_exts: set[str] = set()

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()

            if ext:
                seen_exts.add(ext)

    for ext in seen_exts:
        pattern = f"*{ext}"

        if not _is_ignored(pattern, rules):
            uncovered.add(pattern)

    return sorted(list(uncovered))


def audit_gitignore(project_root: str) -> GitignoreAudit:
    rules = parse_gitignore(project_root)

    untracked = find_untracked_generated(project_root, rules)

    over_ignored = find_over_ignored_critical(project_root, rules)

    uncovered = find_uncovered_types(project_root, rules)

    suggestions: list[str] = []

    ext_counts: dict[str, int] = {}

    for f in untracked:
        ext = os.path.splitext(f)[1].lower()

        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

    for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
        suggestions.append(f"Consider adding *{ext} to .gitignore ({count} files)")

    for crit in over_ignored[:5]:
        suggestions.append(f"WARNING: critical file {crit} is over-ignored")

    return GitignoreAudit(
        project_root=project_root,
        gitignore_rules=rules,
        untracked_generated=untracked,
        over_ignored=over_ignored,
        uncovered_types=uncovered,
        suggestions=suggestions[:10],
    )
