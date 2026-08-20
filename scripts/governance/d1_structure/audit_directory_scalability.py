# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/audit_directory_scalability.py | §
# [MODULE] scripts.governance.d1_structure.audit_directory_scalability
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
"""audit_directory_scalability.py -- 物理结构可扩展性审计 [1500模块支撑能力检查]

对标: Problem VII -- 新增物理容量/可扩展性审计维度
职责: 检查 03_modules/ 和 src/zephyr/ 的目录结构是否具备1500模块的物理承载能力
exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = {
    "args": [],
    "description": "物理结构可扩展性审计 [目录文件数上限/模块隔离/文件数阈值检查]",
    "dimensions": ["D1"],
    "priority": "P1",
    "timeout_seconds": 30,
    "warn_only": True,
}

import argparse
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.thresholds import get as _get_threshold  # noqa: E402  治本(ARCH-036 P3-A5): 目录容量阈值读SSoT

ensure_utf8_stdout()

# 治本（2026-07-18）：拆分为两棵树各自的目录列表。
# 原先 C_TRACK_LAYERS 对 docs/03_modules/ 和 src/zephyr/ 用同一个列表，
# 但两棵树命名约定不同（docs 用 _domain_<full_name> 前缀，src 用短名），
# 导致 17 个误报 finding（FIND-D1-20260706-*）和 18 个 CP 任务阻塞。
# 同时移除重复的 pf_core 条目和不存在的 observability 目录。
C_DOCS_MODULES_DIRS = [  # noqa: gate-vocab  层目录名，非 domain 值
    "_domain_data",
    "_domain_infrastructure_runtime",
    "_domain_integration",
    "_domain_factor",
    "_domain_signal",
    "_domain_risk",
    "_domain_portfolio_core",
    "_domain_execution_core",
    "_domain_frontend",
    "_domain_research",
    "_domain_compliance",
    "_domain_machine_learning_train",
]

C_SRC_ZEPHYR_DIRS = [  # noqa: gate-vocab  层目录名，非 domain 值
    "data",
    "infrastructure",
    "integration",
    "factor",
    "signal_ashare",
    "signal_fundamental",
    "signal_quality",
    "risk",
    "pf_core",
    "ex_core",
    "frontend",
    "research",
    "compliance",
    "ml_train",
]

THRESHOLD_DOCS_MD_WARN = _get_threshold("directory_scalability.docs_md_warn", 5)  # 治本(ARCH-036 P3-A5): 从SSoT读取
THRESHOLD_DOCS_MD_ERROR = _get_threshold("directory_scalability.docs_md_error", 20)  # 治本(ARCH-036 P3-A5): 从SSoT读取
THRESHOLD_SRC_PY_WARN = _get_threshold(
    "directory_scalability.src_py_warn", 60
)  # 治本(ARCH-036 P3-A5): 从SSoT读取(原硬编码10与SSoT 60漂移)
THRESHOLD_SRC_PY_ERROR = _get_threshold(
    "directory_scalability.src_py_error", 120
)  # 治本(ARCH-036 P3-A5): 从SSoT读取(原硬编码50与SSoT 120漂移)
THRESHOLD_DIR_CHILDREN_WARN = _get_threshold(
    "directory_scalability.dir_children_warn", 100
)  # 治本(ARCH-036 P3-A5): 从SSoT读取
THRESHOLD_DIR_CHILDREN_ERROR = _get_threshold(
    "directory_scalability.dir_children_error", 500
)  # 治本(ARCH-036 P3-A5): 从SSoT读取


def count_direct_items(path: Path, suffix: str | None = None) -> int:
    """count_direct_items implementation."""
    if not path.exists() or not path.is_dir():
        return EXIT_PASS
    items = list(path.iterdir())
    if suffix:
        return sum(1 for i in items if i.is_file() and i.suffix == suffix)
    return len(items)


def check_docs_modules_scalability(findings: list[dict[str, Any]]) -> None:
    """Check compliance and report findings."""
    docs_modules = REPO_ROOT / "docs" / "03_modules"
    for layer_name in C_DOCS_MODULES_DIRS:
        layer_dir = docs_modules / layer_name
        if not layer_dir.exists():
            findings.append(
                {
                    "path": str(layer_dir),
                    "issue": "missing_layer_dir",
                    "severity": "ERROR",
                    "msg": f"缺少: {layer_dir}",
                }
            )
            continue
        # 治本（2026-07-18）：移除 flat_blueprint 检查。
        # 原检查假设 blueprint.md 是模块级文件（1500模块不可行），但实际
        # _domain_*/blueprint.md 是域级蓝图（每域1个，约20个，不受1500模块约束）。
        # 模块蓝图有不同文件名（如 <module>_blueprint.md），由 flat_md 计数检查覆盖。
        md_count = count_direct_items(layer_dir, ".md")
        if md_count >= THRESHOLD_DOCS_MD_ERROR:
            findings.append(
                {
                    "path": str(layer_dir),
                    "issue": "flat_md",
                    "severity": "ERROR",
                    "msg": f"{md_count} 个直接 .md 文件 (上限 {THRESHOLD_DOCS_MD_ERROR})",
                }
            )
        elif md_count >= THRESHOLD_DOCS_MD_WARN:
            findings.append(
                {
                    "path": str(layer_dir),
                    "issue": "flat_md",
                    "severity": "WARNING",
                    "msg": f"{md_count} 个直接 .md 文件 (建议上限 {THRESHOLD_DOCS_MD_WARN})",
                }
            )

    all_children = count_direct_items(docs_modules)
    if all_children >= THRESHOLD_DIR_CHILDREN_WARN:
        findings.append(
            {
                "path": str(docs_modules),
                "issue": "dir_size",
                "severity": "WARNING",
                "msg": f"{all_children} 个子项 (估算1500模块后可能 >5000)",
            }
        )


def check_src_zephyr_scalability(findings: list[dict[str, Any]]) -> None:
    """Check compliance and report findings."""
    src_zephyr = REPO_ROOT / "src" / "zephyr"
    for layer_name in C_SRC_ZEPHYR_DIRS:
        layer_dir = src_zephyr / layer_name
        if not layer_dir.exists():
            findings.append(
                {
                    "path": str(layer_dir),
                    "issue": "missing_layer_dir",
                    "severity": "ERROR",
                    "msg": f"缺少: {layer_dir}",
                }
            )
            continue
        py_files = [f for f in layer_dir.iterdir() if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"]
        py_count = len(py_files)
        if py_count >= THRESHOLD_SRC_PY_ERROR:
            findings.append(
                {
                    "path": str(layer_dir),
                    "issue": "flat_py",
                    "severity": "ERROR",
                    "msg": f"{py_count} 个直接 .py 文件 (上限 {THRESHOLD_SRC_PY_ERROR}) -- 应采用 <module>/ 子目录隔离",
                }
            )
        elif py_count >= THRESHOLD_SRC_PY_WARN:
            findings.append(
                {
                    "path": str(layer_dir),
                    "issue": "flat_py",
                    "severity": "WARNING",
                    "msg": f"{py_count} 个直接 .py 文件 (建议上限 {THRESHOLD_SRC_PY_WARN}) -- 建议采用 <module>/ 子目录隔离",
                }
            )

    all_children = count_direct_items(src_zephyr)
    if all_children >= THRESHOLD_DIR_CHILDREN_WARN:
        findings.append(
            {
                "path": str(src_zephyr),
                "issue": "dir_size",
                "severity": "WARNING",
                "msg": f"{all_children} 个子项在 src/zephyr/ 下 (估算1500模块后可能 >3000)",
            }
        )


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="物理结构可扩展性审计")
    parser.add_argument("--warn-only", action="store_true", help="警告模式: 失败不阻塞 (exit 0)")
    args = parser.parse_args()

    findings: list[dict[str, Any]] = []
    check_docs_modules_scalability(findings)
    check_src_zephyr_scalability(findings)

    errors = [f for f in findings if f["severity"] == "ERROR"]
    warnings = [f for f in findings if f["severity"] == "WARNING"]

    print(f"Scalability Audit: {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        print("--- ERRORS ---")
        for e in errors:
            print(f"  [{e['severity']}] {e['path']}: {e['msg']}")
    if warnings:
        print("--- WARNINGS ---")
        for w in warnings:
            print(f"  [{w['severity']}] {w['path']}: {w['msg']}")

    has_errors = len(errors) > 0
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
