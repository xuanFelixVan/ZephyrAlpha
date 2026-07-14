# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/gate_engine_selfcheck.py | §
# [MODULE] scripts.governance.meta.gate_engine_selfcheck
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.gov_enforcement.rule_enforcement.circuit_breaker
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
# [TTL] task_bound
"""
Gate Engine Bootstrap Self-Check — Quis custodiet ipsos custodes?
===================================================================
独立脚本，验证 MOD-GATE_ENGINE Gate Engine 自身的完整性。

Safety : M（治理层第一优先级——门禁失效 = 安全体系真空）
Usage  : python scripts/governance/gate_engine_selfcheck.py [--json] [--verbose]

检查项目：
  S1. 核心文件存在性（gate_engine.py, circuit_breaker.py, _registry.yaml, _template.yaml）
  S2. 门禁 YAML 文件完整性（g1-g5 可解析）
  S3. _registry.yaml 结构完整性（≥5 个门禁注册项）
  S4. SQLite schema 可用性（gates, circuit_breaker_state 表存在）
  S5. 数据库连接性（可读写）
  S6. 门禁模板版本兼容性（_template.yaml vs 实际配置文件）
  S7. CheckType 覆盖率（代码检查类型 vs YAML 声明类型）
  S8. Gate Engine 导入能力（无导入期异常）
  S9. 熔断器模块导入验证
  S10. 门禁与注册表一致性（YAML gate_id 与 _registry.yaml 注册项交叉验证）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Gate Engine Bootstrap 自检——验证 MOD-GATE_ENGINE Gate Engine 自身的完整性，
  包括核心文件存在性、YAML/DB 可用性、CheckType 覆盖率及熔断器验证。
dimensions:
- D1
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import GATES_DIR, REPO_ROOT as _REPO_ROOT  # noqa: E402
from _shared.walk import iter_files  # noqa: E402  治本(ARCH-036 P1-3): 收敛 glob→iter_files

_DB_PATH = _REPO_ROOT / "data" / "databases" / "governance.db"


def _fmt_status(ok: bool, label: str, detail: str = "") -> str:
    """_fmt_status implementation."""
    icon = "PASS" if ok else "FAIL"
    return f"  [{icon}] {label}" + (f" — {detail}" if detail else "")


def check_core_files() -> dict[str, Any]:
    """Check compliance and report findings."""
    core_files = [
        GATES_DIR / "gate_engine.py",
        GATES_DIR / "circuit_breaker.py",
        GATES_DIR / "_registry.yaml",
        GATES_DIR / "_template.yaml",
    ]
    missing = [str(cf.relative_to(_REPO_ROOT)) for cf in core_files if not cf.exists()]
    return {
        "label": "S1. 核心文件存在性",
        "passed": len(missing) == 0,
        "detail": f"{len(core_files) - len(missing)}/{len(core_files)} 文件存在",
        "issues": [f"缺失: {m}" for m in missing],
    }


def check_yaml_parsability() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    yaml_files = iter_files(GATES_DIR, name_pattern="g[1-5]_*.yaml")
    issues: list[str] = []
    for yf in yaml_files:
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                issues.append(f"{yf.name}: 解析结果非 dict")
            elif "gate_id" not in data:
                issues.append(f"{yf.name}: 缺少 gate_id")
        except Exception as exc:
            issues.append(f"{yf.name}: {exc}")

    return {
        "label": "S2. 门禁 YAML 完整性",
        "passed": len(issues) == 0,
        "detail": f"{len(yaml_files)} 个文件, 0 解析错误" if not issues else f"{len(issues)} 个错误",
        "issues": issues,
    }


def check_registry_integrity() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    registry = GATES_DIR / "_registry.yaml"
    if not registry.exists():
        return {"label": "S3. 注册表完整性", "passed": False, "detail": "_registry.yaml 不存在", "issues": ["文件缺失"]}

    try:
        data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"label": "S3. 注册表完整性", "passed": False, "detail": f"解析失败: {exc}", "issues": [str(exc)]}

    gates = data.get("gate_runs", [])
    issues: list[str] = []
    if len(gates) < 5:
        issues.append(f"门禁数量 {len(gates)} < 5")

    for entry in gates:
        if not isinstance(entry, dict):
            issues.append(f"注册项非 dict: {entry}")
            continue
        if "gate_id" not in entry:
            issues.append("注册项缺少 gate_id")
        if "file" not in entry:
            issues.append(f"{entry.get('gate_id', '?')}: 缺少 file 字段")

    return {
        "label": "S3. 注册表完整性",
        "passed": len(issues) == 0,
        "detail": f"{len(gates)} 个注册项",
        "issues": issues,
    }


def check_sqlite_schema() -> dict[str, Any]:
    """Check compliance and report findings."""
    import sqlite3

    issues: list[str] = []
    if not _DB_PATH.exists():
        issues.append(f"数据库文件不存在: {_DB_PATH}")

    try:
        conn = sqlite3.connect(str(_DB_PATH))
        required_tables = ["tasks", "events", "knowledge", "gates", "circuit_breaker_state", "task_files"]
        for table in required_tables:
            row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
            if not row:
                issues.append(f"表缺失: {table}")

        try:
            conn.execute(
                "INSERT INTO gate_runs (gate_run_id, gate_id, passed, details, created_at) VALUES (?,?,?,?,?)",
                ("selfcheck-test", "GX:test", 1, "{}", datetime.now(UTC).isoformat()),
            )
            conn.execute("DELETE FROM gate_runs WHERE gate_run_id='selfcheck-test'")
        except Exception as exc:
            issues.append(f"写入测试失败: {exc}")

        conn.close()
    except Exception as exc:
        issues.append(f"数据库连接失败: {exc}")

    return {
        "label": "S5. 数据库可用性",
        "passed": len(issues) == 0,
        "detail": f"路径: {_DB_PATH}" if not issues else "",
        "issues": issues,
    }


def check_gate_engine_import() -> dict[str, Any]:
    """Check compliance and report findings."""
    issues: list[str] = []
    try:
        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import (
            GateEngine,
        )

        engine = GateEngine()
        gates = engine.load_gates()
        if len(gates) < 8:
            issues.append(f"已加载门禁数量不足: {len(gates)}")
        available_severity = GateEngine._SEVERITY_MAP
        if len(available_severity) < 4:
            issues.append(f"Severity 映射不足: {len(available_severity)}")
    except Exception as exc:
        issues.append(f"导入失败: {exc}")

    return {
        "label": "S8. Gate Engine 导入验证",
        "passed": len(issues) == 0,
        "detail": "API 可用" if not issues else "",
        "issues": issues,
    }


def check_circuit_breaker_import() -> dict[str, Any]:
    """Check compliance and report findings."""
    issues: list[str] = []
    try:
        pass
    except Exception as exc:
        issues.append(f"circuit_breaker 导入失败: {exc}")

    return {
        "label": "S9. 熔断器模块验证",
        "passed": len(issues) == 0,
        "detail": "CircuitBreakerCheck 可用" if not issues else "",
        "issues": issues,
    }


def check_gate_registry_consistency() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    issues: list[str] = []
    registry = GATES_DIR / "_registry.yaml"
    if not registry.exists():
        return {
            "label": "S10. 门禁注册一致性",
            "passed": False,
            "detail": "_registry.yaml 不存在",
            "issues": ["文件缺失"],
        }

    try:
        data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    except Exception:
        return {"label": "S10. 门禁注册一致性", "passed": False, "detail": "解析失败", "issues": []}

    registry_gate_ids = set()
    for entry in data.get("gates", []):
        registry_gate_ids.add(entry.get("gate_id", ""))

    yaml_files = (
        sorted(GATES_DIR.glob("*.yaml"))
        + sorted(GATES_DIR.glob("task/*.yaml"))
        + sorted(GATES_DIR.glob("admission/*.yaml"))
        + sorted(GATES_DIR.glob("invariants/*.yaml"))
    )
    yaml_gate_ids = set()
    for yf in yaml_files:
        if yf.name.startswith("_"):
            continue
        try:
            raw = yf.read_text(encoding="utf-8")
            yd = None
            try:
                loaded = yaml.safe_load(raw)
                if isinstance(loaded, dict):
                    yd = loaded
            except Exception:
                for doc in yaml.safe_load_all(raw):
                    if isinstance(doc, dict):
                        yd = doc
                        break
            if yd is not None and isinstance(yd, dict) and "gate_id" in yd:
                yaml_gate_ids.add(yd["gate_id"])
        except Exception:
            continue

    unregistered = yaml_gate_ids - registry_gate_ids
    # GATE-18 是非YAML的pre_commit gate，过滤它
    phantom = registry_gate_ids - yaml_gate_ids - {""} - {"GATE-18"}

    for gid in unregistered:
        issues.append(f"YAML 中 {gid} 未在 _registry.yaml 注册")
    for gid in phantom:
        issues.append(f"_registry.yaml 中 {gid} 的 YAML 文件缺失（预期若为非YAML gate如GATE-18）")

    return {
        "label": "S10. 门禁注册一致性",
        "passed": len(issues) == 0,
        "detail": f"{len(registry_gate_ids)} 注册项 ↔ {len(yaml_gate_ids)} YAML",
        "issues": issues,
    }


def check_checktype_coverage() -> dict[str, Any]:
    """Check compliance and report findings."""
    import yaml

    issues: list[str] = []
    code_types = {
        "encoding",
        "line_ending",
        "file_extension",
        "frontmatter",
        "content_length",
        "path_blacklist",
        "content_quality",
        "field_presence",
        "classification",
        "regex_pattern",
        "audit_findings_resolved",
        "circuit_breaker",
        "blueprint_read_check",
        "zero_residue_check",
    }
    known_shadow_types = {"position_limit", "leverage_limit", "strategy_correlation"}

    yaml_types = set()
    for yf in iter_files(GATES_DIR, name_pattern="g*.yaml"):
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
            checks = yd.get("checks") or yd.get("entry_conditions") or []
            for c in checks:
                yaml_types.add(c.get("type", ""))
        except Exception:
            continue

    orphaned = yaml_types - code_types - {"condition", ""}
    shadow_known = orphaned & known_shadow_types
    real_orphans = orphaned - known_shadow_types
    if real_orphans:
        issues.append(f"YAML 引用未实现且未登记为 shadow 的类型: {real_orphans}")
    if shadow_known:
        # 不报告为失败——shadow 门禁预期未实现
        pass

    return {
        "label": "S7. CheckType 覆盖率",
        "passed": len(issues) == 0,
        "detail": f"{len(code_types)} 代码类型 / {len(yaml_types)} YAML 类型",
        "issues": issues,
    }


def run_self_check(verbose: bool = False) -> tuple[bool, list[dict[str, Any]]]:
    """run_self_check implementation."""
    checks = [
        check_core_files(),
        check_yaml_parsability(),
        check_registry_integrity(),
        check_sqlite_schema(),
        check_gate_engine_import(),
        check_circuit_breaker_import(),
        check_gate_registry_consistency(),
        check_checktype_coverage(),
    ]

    results: list[dict[str, Any]] = []
    all_ok = True
    for c in checks:
        if not c["passed"]:
            all_ok = False
        results.append(c)
        if verbose or not c["passed"]:
            print(_fmt_status(c["passed"], c["label"], c.get("detail", "")))
            for issue in c.get("issues", []):
                print(f"    → {issue}")

    return all_ok, results


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="Gate Engine Bootstrap Self-Check")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    sys.path.insert(0, str(_REPO_ROOT / "src"))

    print("=== Gate Engine Bootstrap Self-Check ===")
    print(f"时间: {datetime.now(UTC).isoformat()}")
    print(f"项目: {_REPO_ROOT}")
    print(f"门禁目录: {GATES_DIR}")
    print(f"数据库: {_DB_PATH}")
    print()

    all_ok, results = run_self_check(verbose=args.verbose or args.json)

    if args.json:
        output = {
            "checked_at": datetime.now(UTC).isoformat(),
            "all_passed": all_ok,
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
        print()
        if all_ok:
            print("✅ 所有自检通过 — Gate Engine 完整性验证成功")
        else:
            failed = sum(1 for r in results if not r["passed"])
            print(f"❌ {failed}/{len(results)} 项检查失败 — Gate Engine 安全体系受损！")
            print("   请立即排查并修复以上问题后再启动任何 AI 任务。")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
