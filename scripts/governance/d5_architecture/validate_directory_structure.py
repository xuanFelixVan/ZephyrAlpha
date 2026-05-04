#!/usr/bin/env python3
"""
validate_directory_structure.py — LPC 双轨目录结构合规性扫描器
==============================================================
依据：GOV-DOC-002 §三（src/zephyr/ 双轨结构）+ §二（docs/ 目录结构）
GOV-DOC-002 §5.1.2 防幻觉路径映射表的自动化执行器。

检查项
------
1. src/zephyr/ 下的所有一级子目录是否在 LPC 双轨受控列表中
2. src/zephyr/ 下的所有一级 .py 文件（孤儿文件）报告
3. docs/ 下的所有一级子目录是否在受控列表中

问题背景（根因）
--------------
项目曾出现 7 处违规：script_system/、config/、core/、dashboard/、
hooks/、rules/、schemas.py 等目录/文件不在规范定义的受控列表中，
原因是施工时未参考 GOV-DOC-002 的目录定义。本扫描器作为门禁，
防止此类问题再次发生。

Usage:
    python scripts/governance/d5_architecture/validate_directory_structure.py
    python scripts/governance/d5_architecture/validate_directory_structure.py --warn-only

输出
----
- exit 0: 全部合规
- exit 1: 发现违规（--warn-only 下仅打印警告，exit 0）
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

from _shared.constants import REPO_ROOT

SRC_ZEPHYR = REPO_ROOT / "src" / "zephyr"
DOCS = REPO_ROOT / "docs"

C_TRACK_DIRS: set[str] = {
    "l00_data_source",
    "l01_infrastructure",
    "l02_alpha_factor",
    "l03_signal_generation",
    "l04_risk_management",
    "l05_portfolio_construction",
    "l06_trade_execution",
    "l07_post_trade_analytics",
    "l08_human_ai_interface",
    "l09_research_innovation",
    "l10_compliance",
    "l11_ml_platform",
    "l12_system_telemetry",
    "l13_experimentation",
}

B_TRACK_DIRS: set[str] = {
    "llm_security",
    "vector_memory",
    "context_engine",
    "orchestrator",
    "feedback_loop",
    "gates",
    "db",
    "kb",
    "mcp",
    "shared",
}

ALLOWED_SRC_ZEPHYR_DIRS: set[str] = C_TRACK_DIRS | B_TRACK_DIRS

ALLOWED_DOCS_DIRS: set[str] = {
    "01_policies_and_standards",
    "02_enterprise_architecture",
    "03_modules",
    "08_knowledge",
    "09_audit",
    "99_archive",
}

DOCS_ROOT_ALLOWED_FILES: set[str] = {
    "migration-declaration.md",
    "index.md",
}

SRC_ZEPHYR_ALLOWED_FILES: set[str] = {
    "__init__.py",
}


def _scan_directory(path: Path, allowed_dirs: set[str], allowed_files: set[str], label: str) -> list[str]:
    violations: list[str] = []
    if not path.exists():
        violations.append(f"\u274c {label}: 路径不存在: {path}")
        return violations

    for item in sorted(path.iterdir()):
        name = item.name
        if name.startswith("_"):
            continue
        if item.is_dir():
            if name not in allowed_dirs:
                violations.append(f"\u274c [{label}] 未授权的目录: {name}/ " f"\u2192 GOV-DOC-002 §三/§二 未定义此目录")
        elif item.is_file():
            if name.endswith(".pyc") or name == "__pycache__":
                continue
            if name not in allowed_files:
                violations.append(
                    f"\u26a0\ufe0f [{label}] 孤儿文件: {name} " f"\u2192 一级 .py 文件应归入 shared/ 或对应模块目录"
                )
    return violations


def main() -> None:
    """入口函数."""
    warn_only = "--warn-only" in sys.argv
    all_violations: list[str] = []

    src_violations = _scan_directory(SRC_ZEPHYR, ALLOWED_SRC_ZEPHYR_DIRS, SRC_ZEPHYR_ALLOWED_FILES, "src/zephyr")
    all_violations.extend(src_violations)

    docs_violations = _scan_directory(DOCS, ALLOWED_DOCS_DIRS, DOCS_ROOT_ALLOWED_FILES, "docs")
    all_violations.extend(docs_violations)

    if not all_violations:
        print("\u2705 目录结构合规: src/zephyr/ 和 docs/ 下无违规目录/文件", file=sys.stderr)
        sys.exit(0)

    print(f"\u274c 发现 {len(all_violations)} 处目录结构违规:\n", file=sys.stderr)
    for v in all_violations:
        print(f"  {v}", file=sys.stderr)

    if warn_only:
        print("\n\u26a0\ufe0f  --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
        sys.exit(0)

    print("\n\u274c 阻断: 请将违规目录/文件迁移到正确位置。参考 GOV-DOC-002 §三/§二 + §四 决策树。", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
