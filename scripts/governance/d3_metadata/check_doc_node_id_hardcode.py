# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_doc_node_id_hardcode.py | §gate-doc-id
# [MODULE] governance.d3_metadata.check_doc_node_id_hardcode
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] _shared.constants; _shared.walk
# [CONSUMERS] pre-commit GATE-DOC-NODE-ID; manual audit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 正则扫描 .md 文件检测 node_id/edge_id 物理ID硬编码（自增易变，文档禁写，查DB获取）
# [MODIFY-GUARD] 修改需同步 .pre-commit-config.yaml GATE-DOC-NODE-ID 注册与 gate_registry.yaml 登记
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无违规或 warn-only）；EXIT_FINDINGS=1（--ci 模式有违规）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动：已知违规文件被检出；干净文件 exit 0
# [A_module] module_id=MOD-INF-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  pre-commit hook脚本按需调用,非cron/daemon常驻服务
"""GATE-DOC-NODE-ID: 文档物理ID硬编码检测（文档引用铁律，2026-08-04）

检测 docs/ 下 .md 文件中硬编码的 depgraph 物理 ID（node_id/edge_id）。
物理 ID 是 PostgreSQL 自增主键，删除重建即变；文档硬编码=死引用温床。
文档引用 depgraph 时只写稳定逻辑标识（module_id/blueprint_id/path），
需要 node_id/edge_id 时查 DB（SELECT node_id FROM nodes WHERE blueprint_id='MOD-XXX'）。

背景：8个 blueprint.md 曾硬编码 node_id（如 position_tracker node_id=<7位物理ID>），
DB 节点消失后成死引用，误导人/AI，差点引发错误裁定（2026-08-04 审查）。
（本 docstring 不写真实数字——自身派生入 56_d_gov_scripts.md 后会被本 gate 自引用检出）

模式:
  --warn-only（默认）: print 违规清单，exit 0
  --ci: print 违规清单，有违规则 exit 1（hard block）
  --files: 只扫描指定文件（供 pre-commit staged 调用）

Usage::

    # 全量扫描（warn-only，默认）
    python scripts/governance/d3_metadata/check_doc_node_id_hardcode.py

    # CI 模式（有违规则 exit 1）
    python scripts/governance/d3_metadata/check_doc_node_id_hardcode.py --ci
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'GATE-DOC-NODE-ID: 文档物理ID硬编码检测（文档引用铁律）'
dimensions:
- D3
priority: P2
timeout_seconds: 30
warn_only: false
"""


import os
import re
import sys
from pathlib import Path

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402


def _iter_md_files(root: Path, exclude_dirs: frozenset[str]) -> list[Path]:
    """递归扫描 root 下的 .md 文件（独立实现，不依赖 _shared.walk）。

    独立于 _shared.walk（2026-08-04：walk.py 被 _shared.staged_files 未完成变更
    间接破坏，本脚本自包含 os.walk 避免传递依赖）。
    """
    if not root.exists():
        return []
    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs and not d.startswith(".")]
        for filename in sorted(filenames):
            if filename.endswith(".md"):
                result.append(Path(dirpath) / filename)
    return sorted(result)


# ── 检测模式：node_id=数字 / edge_id=数字（含可选空格）──
# 匹配文档里硬编码物理ID的典型形式：node_id=7451163, node_id = 123
# 不匹配 SQL 查询形式（node_id FROM ... / WHERE node_id IN ...）——无 = 号
_PHYSICAL_ID_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("node_id", re.compile(r"\bnode_id\s*=\s*\d+")),
    ("edge_id", re.compile(r"\bedge_id\s*=\s*\d+")),
]

# ── 排除目录（_archive 含历史文档，_working 草稿区同豁免，对齐 N-16 skip_dirs_docs）──
_SCAN_EXCLUDE: frozenset[str] = EXCLUDE_DIRS | {"_archive", "_working"}


def _check_file(filepath: Path) -> list[tuple[int, str]]:
    """检查单个 .md 文件的 node_id/edge_id 硬编码。

    Args:
        filepath: .md 文件绝对路径。

    Returns:
        (行号, 违规描述) 列表（空列表 = 通过）。
    """
    issues: list[tuple[int, str]] = []
    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [(0, "cannot read file")]
    for lineno, line in enumerate(source.splitlines(), 1):
        for id_type, pattern in _PHYSICAL_ID_PATTERNS:
            if pattern.search(line):
                issues.append(
                    (
                        lineno,
                        f"硬编码 {id_type}=数字（物理ID易变，文档只写 module_id/blueprint_id，需要时查 depgraph）",
                    )
                )
                break  # 一行一个违规足够，避免同一行 node_id+edge_id 重复报
    return issues


def _collect_files(args_files: list[str] | None) -> list[Path]:
    """收集待扫描的 .md 文件列表。

    --files 模式只扫指定文件（供 pre-commit staged 调用）；
    默认模式全量扫描 docs/ 下 .md。
    """
    if args_files:
        return [Path(f) for f in args_files if f.endswith(".md")]
    scan_dir = REPO_ROOT / "docs"
    if not scan_dir.exists():
        return []
    return _iter_md_files(scan_dir, _SCAN_EXCLUDE)


def _print_issues(all_issues: list[tuple[Path, int, str]], checked: int) -> None:
    """输出违规清单或 OK 摘要。"""
    if all_issues:
        for filepath, lineno, issue in all_issues:
            try:
                rel = filepath.relative_to(REPO_ROOT)
            except ValueError:
                rel = filepath
            print(f"  WARN: {rel}:{lineno} {issue}")
        print(f"\nFOUND: {len(all_issues)} physical ID hardcode issue(s) in {checked} files checked")
    else:
        print(f"OK: No physical ID hardcode issues found ({checked} files checked)")


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="GATE-DOC-NODE-ID: 文档物理ID硬编码检测（文档引用铁律）")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        default=True,
        help="仅警告不阻断（默认，exit 0 即使有违规）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 模式，有违规则 exit 1（hard block）",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=None,
        help="只扫描指定文件（相对/绝对路径），供 pre-commit staged 调用",
    )
    args = parser.parse_args()

    md_files = _collect_files(args.files)

    all_issues: list[tuple[Path, int, str]] = []
    checked = 0
    for filepath in md_files:
        checked += 1
        for lineno, issue in _check_file(filepath):
            all_issues.append((filepath, lineno, issue))

    _print_issues(all_issues, checked)

    if args.ci and all_issues:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
