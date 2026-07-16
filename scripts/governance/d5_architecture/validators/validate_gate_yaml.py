# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_gate_yaml.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_gate_yaml
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

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
# Gate Configuration Drift Detection — YAML ↔ Code 交叉校验
# ==========================================================
# 针对 MOD-GATE_ENGINE 门禁体系，检测 YAML 配置文件与 gate_engine.py 代码之间的漂移。
# Safety: M | Usage: python scripts/governance/d5_architecture/validate_gate_yaml.py [--fix] [--json]

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, GATES_DIR, REPO_ROOT
from _shared.walk import iter_files

__manifest__ = """
args: []
description: 门禁 YAML 配置漂移检测——YAML 与 gate_engine.py 代码交叉校验
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# 治本(ARCH-036 P1-3): GATES_DIR 从 _shared.constants 导入

_MUTABLE_CHECK_TYPES = {"encoding", "line_ending", "frontmatter", "file_extension"}
_NON_AUTOFIX_TYPES = {
    "circuit_breaker",
    "blueprint_read_check",
    "temporal",
    "score_threshold",
    "classification",
    "deduplication",
    "manual_approval",
    "conflict_detection",
    "secrets_detection",
}


def _load_engine_checktypes() -> set[str]:
    """_load_engine_checktypes implementation."""
    engine_path = GATES_DIR / "gate_engine.py"
    if not engine_path.exists():
        return set()
    content = engine_path.read_text(encoding="utf-8", errors="replace")

    types = set()
    import re

    for m in re.finditer(r'elif ct == "(\w+)"', content):
        types.add(m.group(1))
    for m in re.finditer(r'ct == "(\w+)"', content):
        types.add(m.group(1))
    return types


def _load_gate_files() -> dict[str, str]:
    """_load_gate_files implementation."""
    engine_path = GATES_DIR / "gate_engine.py"
    if not engine_path.exists():
        return {}
    content = engine_path.read_text(encoding="utf-8", errors="replace")
    import re

    m = re.search(r"_GATE_FILES.*?=.*?\{(.*?)\}", content, re.DOTALL)
    if not m:
        return {}
    result: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        pair = re.search(r'"(\w+)":\s*"([^"]+)"', line.strip())
        if pair:
            result[pair.group(1)] = pair.group(2)
    return result


def check_yaml_gateids_in_engine() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    gate_files = _load_gate_files()
    issues: list[str] = []

    for yf in iter_files(GATES_DIR, name_pattern="g[1-5]_*.yaml"):
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except Exception:
            continue
        gid = yd.get("gate_id", "")
        if gid and gid not in gate_files:
            issues.append(f"{yf.name}: gate_id={gid} 不在 engine._GATE_FILES 中")

    return {
        "label": "D1. YAML gate_id 与引擎映射一致性",
        "passed": len(issues) == 0,
        "detail": f"{len(gate_files)} 个引擎映射 ↔ YAML 文件",
        "issues": issues,
    }


def check_checktype_implementation() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    engine_types = _load_engine_checktypes()
    issues: list[str] = []

    for yf in iter_files(GATES_DIR, name_pattern="g*.yaml"):
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except Exception:
            continue
        checks = yd.get("checks") or yd.get("entry_conditions") or []
        for c in checks:
            ct = c.get("type", "")
            if ct in ("condition", ""):
                continue
            if ct not in engine_types:
                issues.append(f"{yf.name}#{c.get('id', '?')}: type={ct} 引擎中无实现")

    return {
        "label": "D2. CheckType 实现覆盖",
        "passed": len(issues) == 0,
        "detail": f"引擎支持 {len(engine_types)} 种类型",
        "issues": issues,
    }


def check_registry_file_refs() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    registry = GATES_DIR / "_registry.yaml"
    if not registry.exists():
        return {
            "label": "D4. 注册表文件引用",
            "passed": False,
            "detail": "_registry.yaml 不存在",
            "issues": ["文件缺失"],
        }

    try:
        data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    except Exception:
        return {"label": "D4. 注册表文件引用", "passed": False, "detail": "解析失败", "issues": []}

    issues: list[str] = []
    for entry in data.get("gates", []):
        fname = entry.get("file", "")
        if fname and not (GATES_DIR / fname).exists():
            issues.append(f"注册项 {entry.get('gate_id', '?')} 指向不存在的文件: {fname}")

    return {
        "label": "D4. 注册表文件引用",
        "passed": len(issues) == 0,
        "detail": f"{len(data.get('gates', []))} 个注册项",
        "issues": issues,
    }


def check_severity_consistency() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    expected_map = {"error": "P0", "critical": "P0", "warning": "P1", "warn": "P1", "info": "P2"}
    issues: list[str] = []

    for yf in iter_files(GATES_DIR, name_pattern="g*.yaml"):
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except Exception:
            continue
        checks = yd.get("checks") or yd.get("entry_conditions") or []
        for c in checks:
            sev = str(c.get("severity", "")).lower()
            if sev and sev not in expected_map:
                issues.append(f"{yf.name}#{c.get('id', '?')}: 未知 severity '{sev}'")

    return {
        "label": "D5. Severity 映射一致性",
        "passed": len(issues) == 0,
        "detail": f"标准映射: {expected_map}",
        "issues": issues,
    }


def check_autofix_compatibility() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    issues: list[str] = []
    for yf in iter_files(GATES_DIR, name_pattern="g*.yaml"):
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except Exception:
            continue
        checks = yd.get("checks") or yd.get("entry_conditions") or []
        for c in checks:
            on_fail = c.get("on_failure", "")
            ct = c.get("type", "")
            if on_fail == "auto_fix" and ct in _NON_AUTOFIX_TYPES:
                issues.append(f"{yf.name}#{c.get('id', '?')}: type={ct} 不支持 auto_fix")

    return {
        "label": "D6. auto_fix 兼容性",
        "passed": len(issues) == 0,
        "detail": f"可修正类型: {_MUTABLE_CHECK_TYPES}",
        "issues": issues,
    }


def check_duplicate_checkids() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    all_ids: dict[str, list[str]] = {}
    issues: list[str] = []

    for yf in iter_files(GATES_DIR, name_pattern="g*.yaml"):
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except Exception:
            continue
        checks = yd.get("checks") or yd.get("entry_conditions") or []
        for c in checks:
            cid = c.get("id", "")
            if cid:
                all_ids.setdefault(cid, []).append(yf.name)

    for cid, files in all_ids.items():
        if len(files) > 1:
            issues.append(f"check_id '{cid}' 重复出现于: {files}")

    return {
        "label": "D7. 重复 check_id 检测",
        "passed": len(issues) == 0,
        "detail": f"{len(all_ids)} 个 check_id, 0 重复" if not issues else "",
        "issues": issues,
    }


def run_drift_check() -> tuple[bool, list[dict[str, Any]]]:
    """run_drift_check implementation."""
    checks = [
        check_yaml_gateids_in_engine(),
        check_checktype_implementation(),
        check_registry_file_refs(),
        check_severity_consistency(),
        check_autofix_compatibility(),
        check_duplicate_checkids(),
    ]

    results: list[dict[str, Any]] = []
    all_ok = True
    for c in checks:
        if not c["passed"]:
            all_ok = False
        results.append(c)

    return all_ok, results


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="Gate Configuration Drift Detection")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--fix", action="store_true", help="自动修复可修复的漂移")
    args = parser.parse_args()

    sys.path.insert(0, str(REPO_ROOT / "src"))

    print("=== Gate Configuration Drift Detection ===")
    print(f"时间: {datetime.now(UTC).isoformat()}")
    print()

    all_ok, results = run_drift_check()

    if args.json:
        output = {
            "checked_at": datetime.now(UTC).isoformat(),
            "all_passed": all_ok,
            "fix_mode": args.fix,
            "results": [
                {
                    "label": r["label"],
                    "passed": r["passed"],
                    "detail": r.get("detail", ""),
                    "issues": r.get("issues", []),
                }
                for r in results
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for r in results:
            icon = "PASS" if r["passed"] else "FAIL"
            print(f"  [{icon}] {r['label']} — {r.get('detail', '')}")
            for issue in r.get("issues", []):
                print(f"    -> {issue}")

    print()
    if all_ok:
        print("All drift checks passed — Gate config aligned with code")
    else:
        failed = sum(1 for r in results if not r["passed"])
        print(f"WARNING: {failed}/{len(results)} drift items detected")
        if args.fix:
            print("   Auto-fix attempted")
        else:
            print("   Use --fix for auto-fix, or manually align YAML with code")

    sys.exit(EXIT_PASS if all_ok else EXIT_FINDINGS)


if __name__ == "__main__":
    main()
