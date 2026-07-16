# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_implementation_docs.py | §
# [MODULE] scripts.governance.d5_architecture.validators.blueprint.validate_blueprint_implementation_docs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.blueprint.__init__
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
"""
AGENTS.md 6.4 铁律五 + 铁律六：construction_progress 必须 LS 磁盘验证，
蓝图中声称的文件路径必须在磁盘上真实存在。

用法：
  python scripts/governance/d5_architecture/validate_blueprint_implementation_docs.py
  python scripts/governance/d5_architecture/validate_blueprint_implementation_docs.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args:
- --warn-only
- --jsonl
description: "validate that blueprint-claimed file paths actually exist on disk"
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import BLUEPRINTS_DIR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.walk import iter_files
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file

ensure_utf8_stdout()
COMPLETED_PROGRESS_VALUES = {"phase_0_completed", "phase_1_complete", "phase_1_partial", "phase_2_complete"}
NOT_STARTED_VALUES = {"not_started", "skeleton"}
IMPLEMENTATION_SECTION_TITLES = [
    "实际代码实现情况",
    "Code Implementation Status",
    "代码实现情况",
    "已实现代码完整路径索引",
]
SECTION_RE = re.compile(
    "^##\\s+(?:\\d+\\.\\s+)?" + "(?:" + "|".join(re.escape(t) for t in IMPLEMENTATION_SECTION_TITLES) + ")",
    re.IGNORECASE | re.MULTILINE,
)

FILE_PATH_RE = re.compile(
    r"`(src/zephyr/[^`*]+\.(?:py|yaml|yml|json|toml))`|`(tests/[^`*]+\.py)`|`(config/[^`*]+\.(?:yaml|yml|json))`"
)


def _has_negative_indicator(content: str, path: str) -> bool:
    """检查文件路径的所有出现位置附近是否有 ❌ 或 未实现 等否定标记。"""
    start = 0
    while True:
        idx = content.find(path, start)
        if idx == -1:
            return False
        window = content[max(0, idx - 500) : idx + len(path) + 200]
        if re.search(
            r"❌|未实现|not.implemented|待实现|待创建|待建|not.started|Phase\s*[2-9]|📋|新模块|计划|规划|新增|⚪",
            window,
            re.IGNORECASE,
        ):
            return True
        start = idx + len(path)


def find_blueprints() -> list[Path]:
    """find_blueprints implementation."""
    if not BLUEPRINTS_DIR.exists():
        return []
    return iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md")


def extract_claimed_file_paths(content: str) -> list[str]:
    """extract_claimed_file_paths implementation."""
    matches = FILE_PATH_RE.findall(content)
    paths: list[str] = []
    for m in matches:
        for g in m:
            if g:
                paths.append(g)
    return list(dict.fromkeys(paths))


def resolve_source_dir_from_claimed_paths(paths: list[str]) -> str | None:
    """resolve_source_dir_from_claimed_paths implementation."""
    for p in paths:
        if p.startswith("src/zephyr/"):
            parts = p.split("/")
            if len(parts) >= 3:
                return "/".join(parts[:3])
    return None


def check_blueprint(bp_path: Path) -> dict:
    """Check compliance and report findings."""
    fm = parse_frontmatter_from_file(bp_path)
    content = bp_path.read_text(encoding="utf-8")
    has_impl_section = bool(SECTION_RE.search(content))
    c_progress = None
    if fm:
        c_progress = fm.get("construction_progress")
    rel = str(bp_path.relative_to(REPO_ROOT))

    claimed_paths = extract_claimed_file_paths(content)

    disk_results: list[tuple[str, bool]] = []
    for cp in claimed_paths:
        full = REPO_ROOT / cp
        disk_results.append((cp, full.exists()))

    return {
        "rel": rel,
        "progress": c_progress or "missing",
        "has_impl": has_impl_section,
        "claimed_paths": claimed_paths,
        "disk_results": disk_results,
        "content": content,
    }


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="GATE-IMPL-DOC — blueprint ↔ disk consistency")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()
    warn_only = args.warn_only

    blueprints = find_blueprints()
    if not blueprints:
        print("No blueprints found under docs/03_modules/")
        if args.jsonl:
            print(
                json.dumps(
                    {
                        "severity": "INFO",
                        "check_id": "IMPL-DOC",
                        "errors": 0,
                        "warnings": 0,
                        "note": "no_blueprints",
                    },
                    ensure_ascii=False,
                )
            )
        return EXIT_PASS
    errors: list[str] = []
    warnings: list[str] = []

    for bp in sorted(blueprints):
        result = check_blueprint(bp)
        bp_rel = result["rel"]
        progress = result["progress"]
        has_impl = result["has_impl"]
        claimed = result["claimed_paths"]
        disk = result["disk_results"]
        content = result["content"]

        is_completed = progress in COMPLETED_PROGRESS_VALUES
        is_not_started = progress in NOT_STARTED_VALUES
        is_missing = progress == "missing"
        has_nonstandard_progress = not is_completed and not is_not_started and not is_missing

        if has_nonstandard_progress and has_impl:
            msg = (
                f"NON-STANDARD construction_progress: {bp_rel}\n"
                f"  construction_progress = '{progress}' (non-standard value).\n"
                f"  Standard values: not_started | skeleton | phase_1_partial | phase_1_complete | phase_2_complete\n"
                f"  Hint: LS the source directory and set the correct value."
            )
            warnings.append(msg)

        if is_completed and not has_impl:
            msg = (
                f"BLUEPRINT IMPL DOC MISSING: {bp_rel}\n"
                f"  construction_progress = '{progress}' but no implementation status section found.\n"
                f"  Required: ## 实际代码实现情况 (Code Implementation Status)"
            )
            errors.append(msg)

        if is_not_started and has_impl and claimed:
            existing_files = sum(1 for _, exists in disk if exists)
            if existing_files > 0:
                msg = (
                    f"BLUEPRINT PROGRESS-CONTENT MISMATCH: {bp_rel}\n"
                    f"  construction_progress = '{progress}' but implementation section lists code files.\n"
                    f"  Disk verification: {existing_files}/{len(claimed)} claimed files actually exist on disk.\n"
                    f"  Action: Set construction_progress to reflect actual state (phase_1_partial or phase_1_complete)."
                )
                errors.append(msg)

        missing_files = [(p, exists) for p, exists in disk if not exists and not _has_negative_indicator(content, p)]
        if missing_files and is_completed:
            for mp, _ in missing_files:
                msg = (
                    f"BLUEPRINT PATH DRIFT: {bp_rel}\n"
                    f"  construction_progress = '{progress}' but claimed file does NOT exist on disk:\n"
                    f"    {mp}\n"
                    f"  Either: (a) remove the non-existent file from the blueprint table,\n"
                    f"          (b) create the file, or\n"
                    f"          (c) downgrade construction_progress to reflect reality."
                )
                errors.append(msg)

        if is_not_started and claimed:
            existing_files = sum(1 for _, e in disk if e)
            missing_files_count = len(missing_files)
            if existing_files > 0:
                msg = (
                    f"BLUEPRINT NOT_STARTED WITH FILES: {bp_rel}\n"
                    f"  construction_progress = 'not_started' but {existing_files}/{len(claimed)} claimed files exist on disk.\n"
                    f"  Expected: 0 files on disk for not_started.\n"
                    f"  Action: Set construction_progress to phase_1_partial or phase_1_complete."
                )
                errors.append(msg)

        phantom_files = [(p, e) for p, e in disk if not e and not _has_negative_indicator(content, p)]
        for pf, _ in phantom_files:
            msg = (
                f"BLUEPRINT FICTION FILE: {bp_rel}\n"
                f"  Claimed as implemented but NOT on disk: {pf}\n"
                f"  Action: Remove from table or create the file."
            )
            warnings.append(msg)

        if is_missing and claimed:
            existing_files = sum(1 for _, e in disk if e)
            if existing_files > 0:
                msg = (
                    f"BLUEPRINT MISSING construction_progress WITH CODE: {bp_rel}\n"
                    f"  No construction_progress in frontmatter, but {existing_files}/{len(claimed)} claimed files exist on disk.\n"
                    f"  Action: Add construction_progress to frontmatter (e.g., phase_1_partial or phase_1_complete)."
                )
                errors.append(msg)

    if errors:
        print(f"\n{'=' * 60}")
        print(f"BLUEPRINT IMPLEMENTATION DOC ERRORS: {len(errors)}")
        print(f"{'=' * 60}\n")
        for e in errors:
            print(e)
            print()
    if warnings:
        print(f"\n{'=' * 60}")
        print(f"BLUEPRINT IMPLEMENTATION DOC WARNINGS: {len(warnings)}")
        print(f"{'=' * 60}\n")
        for w in warnings:
            print(w)
            print()
    blob = {
        "severity": "HIGH" if errors else "INFO",
        "check_id": "IMPL-DOC",
        "errors": len(errors),
        "warnings": len(warnings),
    }

    if not errors and not warnings:
        print(
            f"OK: All {len(blueprints)} blueprints have consistent construction_progress ↔ implementation documentation + verified file paths."
        )
        if args.jsonl:
            print(json.dumps(blob, ensure_ascii=False))
        return EXIT_PASS
    if warn_only:
        print(f"\n[--warn-only] {len(errors)} error(s) suppressed, {len(warnings)} warning(s)")
        if args.jsonl:
            print(json.dumps(blob, ensure_ascii=False))
        return EXIT_PASS
    if errors:
        print(f"\nFAIL: {len(errors)} blueprint(s) with implementation documentation or path drift issues.")
        if args.jsonl:
            print(json.dumps(blob, ensure_ascii=False))
        return EXIT_FINDINGS
    if args.jsonl:
        print(json.dumps(blob, ensure_ascii=False))
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
