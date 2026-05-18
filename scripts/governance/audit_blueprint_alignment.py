# [BLUEPRINT] MOD-INF-005 | scripts/governance/audit_blueprint_alignment.py | §
"""audit_blueprint_alignment.py — 蓝图↔任务卡↔代码 三维对齐审计工具

扫描 blueprints → task cards → downstream_outputs → 磁盘文件，
逐文件检查：存在性、内容质量（AST解析）、GCT桥接、蓝图符号落地。

对标 DOM-GOV-001 蓝图 D5 架构对齐 + RULE-TWO 反孤儿功能 + RULE-EIGHT 复用发现。

Usage:
    python scripts/governance/audit_blueprint_alignment.py
    python scripts/governance/audit_blueprint_alignment.py --warn-only
    python scripts/governance/audit_blueprint_alignment.py --module MOD-INF-017
    python scripts/governance/audit_blueprint_alignment.py --json
"""

from __future__ import annotations
from _shared.encoding import ensure_utf8_stdout
ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS


import ast
import argparse
import json
import re
import sys
from pathlib import Path

__manifest__ = """
args:
- {flag: --warn-only, type: bool, description: 仅报告不退出非零码}
- {flag: --json, type: bool, description: JSON输出（AI消费）}
- {flag: --module, type: str, description: 限定审计单个模块}
dimensions:
- D5
- D1
priority: P1
timeout_seconds: 30
warn_only: false
description: >
  蓝图↔任务卡↔代码三维对齐审计——扫描downstream_outputs、检查文件存在性、
  AST内容质量校验、GCT桥接验证、蓝图符号落地检测。
"""

ROOT = Path(__file__).resolve().parents[2]

TC_DIRS = {
    "MOD-INF-017": ROOT / "docs/03_modules/l01_infrastructure/code-dedup-engine/changes/MOD-INF-017",
    "MOD-INF-018": ROOT / "docs/03_modules/l01_infrastructure/agent-rbac/changes/MOD-INF-018",
    "DOM-GOV-001": ROOT / "docs/03_modules/_domain-governance/_domain-governance/changes/DOM-GOV-001",
}
BP = {
    "MOD-INF-017": ROOT / "docs/03_modules/l01_infrastructure/code-dedup-engine/blueprint.md",
    "MOD-INF-018": ROOT / "docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md",
    "DOM-GOV-001": ROOT / "docs/03_modules/_domain-governance/blueprint.md",
}
SRC = {
    "MOD-INF-017": ROOT / "src/zephyr/l01_infrastructure/code_dedup_engine",
    "MOD-INF-018": ROOT / "src/zephyr/agent_rbac",
    "DOM-GOV-001": ROOT / "src/zephyr/governance",
}

GCT_MAP = {
    "G-CT-001": ("agent_rbac", "audit_trail"),
    "G-CT-002": ("audit_trail", "rollback"),
    "G-CT-003": ("rollback", "escalation"),
    "G-CT-004": ("escalation", "agent_rbac"),
    "G-CT-005": ("drift_detector", "rollback"),
    "G-CT-006": ("budget_enforcer", "escalation"),
    "G-CT-007": ("agent_spec", "audit_trail"),
    "G-CT-008": ("a2a", "agent_rbac"),
}


def extract_outputs(fp: Path) -> list[str]:
    """extract_outputs implementation."""
    results = []
    try:
        content = fp.read_text(encoding="utf-8")
    except OSError:
        return results
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("- path:"):
            results.append(s.split('"')[1])
    return results


def check_py(fp: Path) -> tuple[str, int, int]:
    """Check compliance and report findings."""
    try:
        src = fp.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (SyntaxError, OSError):
        return ("PARSE_ERROR", 0, 0)
    lines = [l for l in src.split("\n") if l.strip() and not l.strip().startswith("#")]
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    has_body = len(classes) + len(funcs) > 0
    if not has_body:
        return ("NO_SYMBOL", len(lines), 0)
    body_lines = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            body_lines += len(node.body)
    if body_lines < 5:
        return ("THIN", len(lines), body_lines)
    return ("OK", len(lines), body_lines)


def check_data(fp: Path) -> tuple[str, int]:
    """Check compliance and report findings."""
    size = fp.stat().st_size
    if fp.suffix in (".yaml", ".yml", ".json"):
        return ("OK" if size > 20 else "TINY", size)
    if fp.suffix == ".md":
        return ("OK" if size > 100 else "TINY", size)
    return ("OK", size)


def check_gct(gov_dir: Path) -> list[str]:
    """Check compliance and report findings."""
    issues = []
    bp_path = BP["DOM-GOV-001"]
    if bp_path.exists():
        gcts_from_bp = set(re.findall(r'G-CT-\d+', bp_path.read_text(encoding="utf-8")))
        if len(gcts_from_bp) < 8:
            issues.append(f"蓝图 GCT 引用不满 8 条（实际 {len(gcts_from_bp)}）")
    for gct, (src_m, dst_m) in GCT_MAP.items():
        dst = gov_dir / dst_m
        found = False
        if dst.exists():
            for pyf in dst.rglob("*.py"):
                try:
                    c = pyf.read_text(encoding="utf-8")
                except OSError:
                    continue
                if f"governance.{src_m}" in c or f"from zephyr.governance.{src_m}" in c:
                    found = True
                    break
        if not found:
            issues.append(f"{gct}: {dst_m} 未 import {src_m}")
    return issues


def check_blueprint_symbols(mod_ids: list[str]) -> dict[str, list[str]]:
    """Check compliance and report findings."""
    results: dict[str, list[str]] = {}
    for mod_id in mod_ids:
        bp_path = BP.get(mod_id)
        if not bp_path or not bp_path.exists():
            results[mod_id] = ["蓝图缺失"]
            continue
        content = bp_path.read_text(encoding="utf-8")
        bp_classes = set(re.findall(
            r'\b([A-Z][a-zA-Z0-9]+(?:Guard|Manager|Detector|Core|Switch|Bridge|Handler|Auditor|Verifier|Simulator|Registry|Checker|Validator|Tracker|Writer|Generator|Runner|Isolator|Enforcer|Hook|Policy|Lock|Event|Context|Request|Result|Alert|Contract|Fix))\b',
            content,
        ))
        src_dir = SRC.get(mod_id)
        code_classes: set[str] = set()
        if src_dir and src_dir.exists():
            for pyf in src_dir.rglob("*.py"):
                if pyf.name.startswith("_"):
                    continue
                try:
                    tree = ast.parse(pyf.read_text(encoding="utf-8"))
                    for n in ast.walk(tree):
                        if isinstance(n, ast.ClassDef):
                            code_classes.add(n.name)
                except (SyntaxError, OSError):
                    pass
        missing = bp_classes - code_classes
        if missing:
            results[mod_id] = sorted(missing)
        else:
            results[mod_id] = []
    return results


def run_audit(module_filter: str | None = None) -> dict:
    """run_audit implementation."""
    stats = {"total": 0, "ok": 0, "thin": 0, "missing": 0, "tiny": 0, "error": 0}
    all_issues: list[str] = []
    module_results: list[dict] = []

    mod_ids = [module_filter] if module_filter else list(TC_DIRS.keys())
    mod_ids = [m for m in mod_ids if m in TC_DIRS]

    for mod_id in mod_ids:
        tc_dir = TC_DIRS[mod_id]
        if not tc_dir.exists():
            continue
        bp_path = BP.get(mod_id)
        bp_ok = bp_path and bp_path.exists()
        tc_count = len(list(tc_dir.glob("*.md")))

        for tc in sorted(tc_dir.glob("*.md")):
            outs = extract_outputs(tc)
            if not outs:
                continue
            for pstr in outs:
                stats["total"] += 1
                fp = Path(pstr)
                exists = fp.exists()
                if not exists:
                    stats["missing"] += 1
                    all_issues.append(f"MISSING [{mod_id}] {tc.stem}: {fp}")
                    continue
                ext = fp.suffix.lower()
                if ext == ".py":
                    status, lines, body = check_py(fp)
                    if status == "OK":
                        stats["ok"] += 1
                    elif status == "THIN":
                        stats["thin"] += 1
                        all_issues.append(f"THIN [{mod_id}] {tc.stem}: {fp.relative_to(ROOT)} ({lines}L/{body} body)")
                    else:
                        stats["error"] += 1
                        all_issues.append(f"{status} [{mod_id}] {tc.stem}: {fp.relative_to(ROOT)}")
                else:
                    status, size = check_data(fp)
                    if status == "OK":
                        stats["ok"] += 1
                    else:
                        stats["tiny"] += 1
                        all_issues.append(f"TINY [{mod_id}] {tc.stem}: {fp.relative_to(ROOT)} ({size}B)")

        module_results.append({
            "module_id": mod_id,
            "blueprint_ok": bp_ok,
            "task_cards": tc_count,
        })

    gct_issues: list[str] = []
    gov_dir = SRC.get("DOM-GOV-001")
    if gov_dir and gov_dir.exists():
        gct_issues = check_gct(gov_dir)

    symbol_results = check_blueprint_symbols(["MOD-INF-017", "MOD-INF-018"])

    py_counts: dict[str, dict] = {}
    for mod_id, d in SRC.items():
        if d and d.exists():
            py = list(d.rglob("*.py"))
            lines = sum(len(f.read_text(encoding="utf-8").split("\n")) for f in py if f.name != "__init__.py")
            py_counts[mod_id] = {"files": len(py), "loc": lines}

    return {
        "stats": stats,
        "issues": all_issues,
        "gct_issues": gct_issues,
        "symbol_missing": symbol_results,
        "modules": module_results,
        "code_stats": py_counts,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="蓝图↔任务卡↔代码三维对齐审计")
    parser.add_argument("--warn-only", action="store_true", help="仅报告不退出非零码")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--module", type=str, help="限定审计单个模块")
    args = parser.parse_args()

    result = run_audit(module_filter=args.module)
    stats = result["stats"]
    all_issues = result["issues"]

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("ZephyrAlpha 蓝图↔任务卡↔代码 三维对齐审计")
        print("=" * 60)

        for mod in result["modules"]:
            bp_mark = "✅" if mod["blueprint_ok"] else "❌ MISSING"
            print(f"\n{'─'*60}")
            print(f"  {mod['module_id']}  蓝图: {bp_mark}  ({mod['task_cards']} 任务卡)")
            print(f"{'─'*60}")

        print(f"\n{'─'*60}")
        print(f"  GCT 桥接审计")
        print(f"{'─'*60}")
        for gi in result["gct_issues"]:
            print(f"  ❌ {gi}")
        if not result["gct_issues"]:
            print(f"  ✅ 8/8 GCT bridged")

        print(f"\n{'─'*60}")
        print(f"  蓝图符号 → 代码落地")
        print(f"{'─'*60}")
        for mod_id, missing in result["symbol_missing"].items():
            if missing and missing[0] != "蓝图缺失":
                print(f"  [{mod_id}] 蓝图声明但未实现: {missing[:15]}...")
            elif missing and missing[0] == "蓝图缺失":
                print(f"  [{mod_id}] 蓝图缺失")
            else:
                print(f"  [{mod_id}] 蓝图类名全部落地 ✅")

        print(f"\n{'='*60}")
        print(f"  审计总结")
        print(f"{'='*60}")
        print(f"  总文件: {stats['total']}")
        print(f"  ✅ OK: {stats['ok']}  ❌ 缺失: {stats['missing']}  ⚠️ THIN: {stats['thin']}  📄 TINY: {stats['tiny']}  💥 ERR: {stats['error']}")
        if all_issues:
            print(f"\n  ⚠️ 问题列表 ({len(all_issues)}):")
            for iss in all_issues[:30]:
                print(f"    {iss}")
            if len(all_issues) > 30:
                print(f"    ... 还有 {len(all_issues)-30} 条")
        else:
            print(f"\n  🎉 全部对齐，无任何问题！")

        print(f"\n--- 代码量 ---")
        for mod_id, cs in result["code_stats"].items():
            print(f"  {mod_id}: {cs['files']} .py, {cs['loc']} LOC")

    has_issues = stats["missing"] > 0 or stats["error"] > 0 or len(result["gct_issues"]) > 0
    if has_issues and not args.warn_only:
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
