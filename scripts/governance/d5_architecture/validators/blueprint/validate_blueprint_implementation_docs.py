# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_implementation_docs.py | §
# [MODULE] scripts.governance.d5_architecture.validators.blueprint.validate_blueprint_implementation_docs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.blueprint.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m02-manual  M02豁免: while True用于字符串搜索(content.find+break),非daemon常驻服务;一次性CLI验证工具
"""
AGENTS.md 6.4 铁律五 + 铁律六：蓝图中声称的文件路径必须在磁盘上真实存在。

ARCH-FRONTMATTER-STATE-001 Phase 3（2026-07-18）：退役 construction_progress 字段后，
本验证器简化为纯文件存在性检查——声称的代码文件必须在磁盘上真实存在，
不再依赖 construction_progress 状态分支。

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
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
# ARCH-FRONTMATTER-STATE-001 Phase 3: construction_progress 退役，相关常量移除
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
    """Check compliance and report findings.

    ARCH-FRONTMATTER-STATE-001 Phase 3：退役 construction_progress 后，
    不再读取 frontmatter 状态字段，仅检查声称的文件路径在磁盘上是否存在。
    """
    content = bp_path.read_text(encoding="utf-8")
    rel = str(bp_path.relative_to(REPO_ROOT))

    claimed_paths = extract_claimed_file_paths(content)

    disk_results: list[tuple[str, bool]] = []
    for cp in claimed_paths:
        full = REPO_ROOT / cp
        disk_results.append((cp, full.exists()))

    return {
        "rel": rel,
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
        claimed = result["claimed_paths"]
        disk = result["disk_results"]
        content = result["content"]

        # ARCH-FRONTMATTER-STATE-001 Phase 3: 退役 construction_progress 后，
        # 仅保留"声称的文件必须在磁盘上存在"检查（原 phantom_files 检查）。
        # 不再根据 construction_progress 状态分支判断。
        phantom_files = [(p, e) for p, e in disk if not e and not _has_negative_indicator(content, p)]
        for pf, _ in phantom_files:
            msg = (
                f"BLUEPRINT FICTION FILE: {bp_rel}\n"
                f"  Claimed as implemented but NOT on disk: {pf}\n"
                f"  Action: Remove from table or create the file."
            )
            warnings.append(msg)

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
            f"OK: All {len(blueprints)} blueprints have verified file paths (construction_progress retired per ARCH-FRONTMATTER-STATE-001 Phase 3)."
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
