# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/audit_directory_scalability.py | §
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

ensure_utf8_stdout()

C_TRACK_LAYERS = [
    "l00_data_source", "l01_infrastructure", "l02_alpha_factor",
    "l03_signal_generation", "l04_risk_management",
    "l05_portfolio_construction", "l06_trade_execution",
    "l07_post_trade_analytics", "l08_human_ai_interface",
    "l09_research_innovation", "l10_compliance",
    "l11_ml_platform", "system_telemetry", "l13_experimentation",
]

THRESHOLD_DOCS_MD_WARN = 5
THRESHOLD_DOCS_MD_ERROR = 20
THRESHOLD_SRC_PY_WARN = 10
THRESHOLD_SRC_PY_ERROR = 50
THRESHOLD_DIR_CHILDREN_WARN = 100
THRESHOLD_DIR_CHILDREN_ERROR = 500


def count_direct_items(path: Path, suffix: str | None = None) -> int:
    """count_direct_items implementation."""
    if not path.exists() or not path.is_dir():
        return EXIT_PASS
    items = list(path.iterdir())
    if suffix:
        return sum(1 for i in items if i.is_file() and i.suffix == suffix)
    return len(items)


def has_direct_file(path: Path, filename: str) -> bool:
    """has_direct_file implementation."""
    return (path / filename).exists()


def check_docs_modules_scalability(findings: list[dict[str, Any]]) -> None:
    """Check compliance and report findings."""
    docs_modules = REPO_ROOT / "docs" / "03_modules"
    for layer_name in C_TRACK_LAYERS:
        layer_dir = docs_modules / layer_name
        if not layer_dir.exists():
            findings.append({
                "path": str(layer_dir),
                "issue": "missing_layer_dir",
                "severity": "ERROR",
                "msg": f"缺少: {layer_dir}",
            })
            continue
        if has_direct_file(layer_dir, "blueprint.md"):
            findings.append({
                "path": str(layer_dir / "blueprint.md"),
                "issue": "flat_blueprint",
                "severity": "ERROR",
                "msg": f"blueprint.md 应在 <module>/ 子目录下,而非层目录平铺 (1500模块不可行)",
            })
        md_count = count_direct_items(layer_dir, ".md")
        if md_count >= THRESHOLD_DOCS_MD_ERROR:
            findings.append({
                "path": str(layer_dir),
                "issue": "flat_md",
                "severity": "ERROR",
                "msg": f"{md_count} 个直接 .md 文件 (上限 {THRESHOLD_DOCS_MD_ERROR})",
            })
        elif md_count >= THRESHOLD_DOCS_MD_WARN:
            findings.append({
                "path": str(layer_dir),
                "issue": "flat_md",
                "severity": "WARNING",
                "msg": f"{md_count} 个直接 .md 文件 (建议上限 {THRESHOLD_DOCS_MD_WARN})",
            })

    all_children = count_direct_items(docs_modules)
    if all_children >= THRESHOLD_DIR_CHILDREN_WARN:
        findings.append({
            "path": str(docs_modules),
            "issue": "dir_size",
            "severity": "WARNING",
            "msg": f"{all_children} 个子项 (估算1500模块后可能 >5000)",
        })


def check_src_zephyr_scalability(findings: list[dict[str, Any]]) -> None:
    """Check compliance and report findings."""
    src_zephyr = REPO_ROOT / "src" / "zephyr"
    for layer_name in C_TRACK_LAYERS:
        layer_dir = src_zephyr / layer_name
        if not layer_dir.exists():
            findings.append({
                "path": str(layer_dir),
                "issue": "missing_layer_dir",
                "severity": "ERROR",
                "msg": f"缺少: {layer_dir}",
            })
            continue
        py_files = [f for f in layer_dir.iterdir() if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"]
        py_count = len(py_files)
        if py_count >= THRESHOLD_SRC_PY_ERROR:
            findings.append({
                "path": str(layer_dir),
                "issue": "flat_py",
                "severity": "ERROR",
                "msg": f"{py_count} 个直接 .py 文件 (上限 {THRESHOLD_SRC_PY_ERROR}) -- 应采用 <module>/ 子目录隔离",
            })
        elif py_count >= THRESHOLD_SRC_PY_WARN:
            findings.append({
                "path": str(layer_dir),
                "issue": "flat_py",
                "severity": "WARNING",
                "msg": f"{py_count} 个直接 .py 文件 (建议上限 {THRESHOLD_SRC_PY_WARN}) -- 建议采用 <module>/ 子目录隔离",
            })

    all_children = count_direct_items(src_zephyr)
    if all_children >= THRESHOLD_DIR_CHILDREN_WARN:
        findings.append({
            "path": str(src_zephyr),
            "issue": "dir_size",
            "severity": "WARNING",
            "msg": f"{all_children} 个子项在 src/zephyr/ 下 (估算1500模块后可能 >3000)",
        })


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
