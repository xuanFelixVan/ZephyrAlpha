# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_precommit_id_uniqueness
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
check_precommit_id_uniqueness.py — GATE-ID-UNIQ

检测 .pre-commit-config.yaml 内 hook id 唯一性,重复即阻断。

历史教训 (commit a09e510ec6): 两个不同 SSoT 门禁用了同一 `id: gate-ssot`
(line 324 for src/zephyr/*.py, line 388 for docs/*.md),导致后者覆盖前者。
已手动把第二个改为 gate-ssot-docs,但缺自动化门禁——未来 AI 可能再造一对重复 id。
本门禁治本:自动扫描 .pre-commit-config.yaml,发现重复 id 即 hard block。

检测规则:
  - 同一 repo 块内重复 id → hard block (exit 1 in --ci)
    pre-commit 在同一 repo 内要求 id 唯一,重复会直接报错或后者覆盖前者。
  - 跨 repo 块重复 id → warn (exit 0)
    pre-commit 允许跨 repo 同 id(两个 hook 都会运行),但本项目视为覆盖风险,
    提示人工裁定。多个 `local` 块按 repo 声明行号区分。

模式:
  --ci (默认): same-repo 重复 → exit 1; cross-repo 重复 → exit 0 + WARN
  --warn-only: 全部 exit 0 (仅报告,不阻断)

实现:
  - yaml.safe_load 做 YAML 语法校验(结构异常 fail fast)
  - 文本行扫描收集 (line_no, hook_id, repo_url, repo_line) 以输出精确行号
  - 按 id 分组,按 repo_line 判定 same/cross repo
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import re
from collections import defaultdict

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

__manifest__ = """
args:
- --ci
- --warn-only
description: GATE-ID-UNIQ - 检测 .pre-commit-config.yaml 内 hook id 唯一性,重复即阻断
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

CONFIG_PATH: Path = REPO_ROOT / ".pre-commit-config.yaml"

# hook id 声明行: "      - id: gate-ssot" (允许行尾注释,只取首个非空白 token)
_HOOK_ID_RE = re.compile(r"^(\s*)-\s+id:\s+(\S+)")
# repo 声明行: "  - repo: local" 或 "  - repo: https://github.com/..."
_REPO_RE = re.compile(r"^(\s*)-\s+repo:\s+(.+?)\s*$")


def _scan_hook_ids(text: str) -> list[tuple[int, str, str, int]]:
    """扫描 .pre-commit-config.yaml 文本,返回 (line_no, hook_id, repo_url, repo_line) 列表。

    repo_line 用作 repo 块的唯一标识——多个 `local` repo 块同 URL 但行号不同,
    据此区分两个独立的 local repo(跨块同 id 视为 cross-repo 警告)。
    """
    results: list[tuple[int, str, str, int]] = []
    current_repo_url: str | None = None
    current_repo_line: int = 0
    for i, raw_line in enumerate(text.splitlines(), start=1):
        m_repo = _REPO_RE.match(raw_line)
        if m_repo:
            current_repo_url = m_repo.group(2).strip().strip('"').strip("'")
            current_repo_line = i
            continue
        m_id = _HOOK_ID_RE.match(raw_line)
        if m_id:
            # 剥离 yaml 字符串引号('foo'/"foo" → foo),对齐 _REPO_RE L94 的引号处理。
            # 防御引号绕过(红蓝对抗攻击3): id: foo 与 id: 'foo' 在 yaml 解析下是同一
            # id,但正则 \S+ 会把引号当 id 一部分 → 视为不同 → 漏检。pre-commit id
            # 规范是 bare word,但防御性处理引号避免人为绕过(第一性原理治本)。
            hook_id = m_id.group(2).strip("'\"")
            repo_url = current_repo_url if current_repo_url is not None else "<orphan>"
            repo_line = current_repo_line if current_repo_url is not None else 0
            results.append((i, hook_id, repo_url, repo_line))
    return results


def _classify_duplicates(
    hooks: list[tuple[int, str, str, int]],
) -> tuple[list[list[tuple[int, str, str, int]]], list[list[tuple[int, str, str, int]]]]:
    """按 id 分组,返回 (same_repo_dups, cross_repo_dups)。

    每个元素是该 id 的所有出现位置列表。same_repo = 全部在同一 repo 块内
    (repo_line 相同);cross_repo = 跨多个 repo 块。
    """
    by_id: dict[str, list[tuple[int, str, str, int]]] = defaultdict(list)
    for entry in hooks:
        by_id[entry[1]].append(entry)
    same_repo: list[list[tuple[int, str, str, int]]] = []
    cross_repo: list[list[tuple[int, str, str, int]]] = []
    for entries in by_id.values():
        if len(entries) < 2:
            continue
        repo_keys = {e[3] for e in entries}
        (same_repo if len(repo_keys) == 1 else cross_repo).append(entries)
    return same_repo, cross_repo


def _format_entries(entries: list[tuple[int, str, str, int]]) -> str:
    parts = []
    for line_no, hook_id, repo_url, repo_line in entries:
        parts.append(
            f"line {line_no} (id='{hook_id}', repo={repo_url}@line{repo_line})"
        )
    return ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GATE-ID-UNIQ: 检测 .pre-commit-config.yaml 内 hook id 唯一性"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--ci",
        action="store_true",
        help="硬阻断模式 (默认行为,显式传递以兼容 pre-commit args 配置)",
    )
    mode.add_argument(
        "--warn-only", action="store_true", help="仅警告: 全部 exit 0 (不阻断)"
    )
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        print(f"ERROR: config not found: {CONFIG_PATH}")
        return EXIT_ERROR

    try:
        text = CONFIG_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {CONFIG_PATH}: {exc}")
        return EXIT_ERROR

    # yaml.safe_load 仅做语法校验(不使用其结构数据——文本扫描才能给出精确行号)
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed (yaml.safe_load required for syntax validation)")
        return EXIT_ERROR
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"ERROR: .pre-commit-config.yaml 语法异常,无法解析:\n{exc}")
        return EXIT_ERROR

    hooks = _scan_hook_ids(text)
    same_repo_dups, cross_repo_dups = _classify_duplicates(hooks)

    total_ids = len(hooks)
    unique_ids = len({h[1] for h in hooks})
    print(f"[GATE-ID-UNIQ] scanned {total_ids} hook declarations, {unique_ids} unique ids")

    if same_repo_dups:
        print(f"\nFAIL: {len(same_repo_dups)} same-repo duplicate id(s):")
        for entries in same_repo_dups:
            print(f"  - {_format_entries(entries)}")

    if cross_repo_dups:
        print(
            f"\nWARN: {len(cross_repo_dups)} cross-repo duplicate id(s) "
            "(pre-commit 允许跨 repo 同 id,但本项目视为覆盖风险,请人工裁定):"
        )
        for entries in cross_repo_dups:
            print(f"  - {_format_entries(entries)}")

    if not same_repo_dups and not cross_repo_dups:
        print("OK: all hook ids unique")
        return EXIT_PASS

    if args.warn_only:
        print("\nWARN-ONLY: 不阻断 (--warn-only)")
        return EXIT_PASS

    if same_repo_dups:
        print("\nBLOCK: same-repo duplicate id(s) found (--ci)")
        return EXIT_FINDINGS

    # 仅 cross-repo 警告 → 不阻断
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
