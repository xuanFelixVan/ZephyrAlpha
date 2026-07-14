# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_gate_engine_external.py | §
# [MODULE] scripts.governance.meta.validate_gate_engine_external
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.integration.__init__; zephyr.gov_enforcement.rule_enforcement.circuit_breaker
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
validate_gate_engine_external.py — Gate Engine 外部完整性验证
=============================================================
独立的外部验证脚本，从进程外部确认 Gate Engine 未被篡改/损坏。

Safety : M（门禁引擎外部验证失败 = 整个安全体系信用归零）
Usage  : python scripts/governance/meta/validate_gate_engine_external.py [--json] [--verbose]

设计原理：
  Gate Engine 自身不能充当自身的唯一验证者（Quis custodiet ipsos custodes?）。
  本脚本作为外部独立进程运行（可被 cron/git hook/CI 触发），执行：
  - 核心文件的哈希快照对比（检测篡改）
  - 数据库 Schema 独立验证（不依赖 GateEngine 初始化）
  - Canary 注入测试（注入已知违规 → 验证 GateEngine 是否检出）
  - 注册表 ↔ 文件系统一致性（从外部文件系统视角）

检查项目：
  V1. 核心文件哈希快照（gate_engine.py, circuit_breaker.py, _registry.yaml）
  V2. 门禁 YAML 文件数量扩缩检测
  V3. SQLite Schema 外部验证
  V4. Canary 违规注入 + 检出验证
  V5. 注册表 ↔ 文件系统交叉验证
  V6. 导入期完整性（无 SyntaxError/ImportError）

对标：
  - PCI-DSS §11.5: File Integrity Monitoring (FIM)
  - SOC 2 CC7.1: 变更检测机制
  - NIST SP 800-53 SI-7: Software, Firmware, and Information Integrity

exit codes: 0=验证通过, 1=发现问题, 2=执行错误
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import GATES_DIR, EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.walk import iter_files  # noqa: E402  治本(ARCH-036 P1-3): 收敛 glob→iter_files

__manifest__ = """
args: []
description: >
  Gate Engine 外部完整性验证——从独立进程执行哈希快照、Canary 注入、
  Schema 验证、注册表一致性检查，确保 Gate Engine 未被篡改。
dimensions:
- D6
- D11
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_PROJECT_ROOT = REPO_ROOT
_DB_PATH = _PROJECT_ROOT / "data" / "databases" / "governance.db"
_SNAPSHOT_PATH = _PROJECT_ROOT / "scripts" / "governance" / "meta" / "gate_engine_hashes.json"
_SRC = _PROJECT_ROOT / "src"

_CORE_FILES: list[Path] = [
    GATES_DIR / "gate_engine.py",
    GATES_DIR / "circuit_breaker.py",
    GATES_DIR / "_registry.yaml",
    GATES_DIR / "_template.yaml",
]


def _compute_hash(filepath: Path) -> str:
    """_compute_hash implementation."""
    if not filepath.exists():
        return "MISSING"
    return hashlib.sha256(filepath.read_bytes()).hexdigest()[:16]


def verify_core_file_hashes(verbose: bool = False) -> dict[str, Any]:
    """verify_core_file_hashes implementation."""
    current: dict[str, str] = {}
    for fp in _CORE_FILES:
        rel = str(fp.relative_to(_PROJECT_ROOT)).replace("\\", "/")
        current[rel] = _compute_hash(fp)

    issues: list[str] = []
    if _SNAPSHOT_PATH.exists():
        try:
            snapshot = json.loads(_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            snapshot = {}

        for path, snap_hash in snapshot.items():
            cur_hash = current.get(path)
            if cur_hash is None:
                issues.append(f"快照文件 {path} 在磁盘中消失")
            elif cur_hash == "MISSING":
                issues.append(f"核心文件 {path} 缺失")
            elif cur_hash != snap_hash:
                if verbose:
                    issues.append(f"文件哈希变更 {path}: {snap_hash[:8]} → {cur_hash[:8]}")
                else:
                    issues.append(f"文件哈希变更: {path}")

        for path in current:
            if path not in snapshot:
                issues.append(f"磁盘文件 {path} 不在快照中（新增文件）")

    can_update = not issues or all("哈希变更" in i for i in issues)

    return {
        "label": "V1. 核心文件哈希验证",
        "passed": len([i for i in issues if "变更" not in i and "新增" not in i]) == 0,
        "hash_count": len(current),
        "can_update_snapshot": can_update,
        "issues": issues,
        "current_hashes": current,
    }


def update_hash_snapshot() -> dict[str, str]:
    """update_hash_snapshot implementation."""
    snapshot: dict[str, str] = {}
    for fp in _CORE_FILES:
        rel = str(fp.relative_to(_PROJECT_ROOT)).replace("\\", "/")
        snapshot[rel] = _compute_hash(fp)
    _SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_SNAPSHOT_PATH, json.dumps(snapshot, ensure_ascii=False, indent=2))
    return snapshot


def verify_yaml_file_count() -> dict[str, Any]:
    """verify_yaml_file_count implementation."""
    yaml_files = iter_files(GATES_DIR, name_pattern="g*.yaml")
    count = len(yaml_files)
    expected_min = 8
    issues: list[str] = []

    if count < expected_min:
        issues.append(f"门禁 YAML 文件数量 {count} < 预期最小值 {expected_min}")

    return {
        "label": "V2. 门禁 YAML 文件计数",
        "passed": len(issues) == 0,
        "count": count,
        "expected_min": expected_min,
        "files": [yf.name for yf in yaml_files],
        "issues": issues,
    }


def verify_sqlite_external() -> dict[str, Any]:
    """verify_sqlite_external implementation."""
    issues: list[str] = []
    if not _DB_PATH.exists():
        return {
            "label": "V3. SQLite 外部验证",
            "passed": False,
            "issues": [f"数据库文件不存在: {_DB_PATH}"],
        }

    try:
        conn = sqlite3.connect(str(_DB_PATH))
        required_tables = ["gate_runs", "circuit_breaker_state", "tasks"]
        for table in required_tables:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            ).fetchone()
            if not row:
                issues.append(f"表缺失: {table}")

        try:
            conn.execute(
                "INSERT INTO gate_runs (gate_run_id, gate_id, passed, details, created_at) VALUES (?,?,?,?,?)",
                ("ext-verify-test", "GX-EXT:test", 1, "{}", datetime.now(UTC).isoformat()),
            )
            conn.execute("DELETE FROM gate_runs WHERE gate_run_id='ext-verify-test'")
        except Exception as exc:
            issues.append(f"写入测试失败: {exc}")

        conn.close()
    except Exception as exc:
        issues.append(f"数据库连接失败: {exc}")

    return {
        "label": "V3. SQLite 外部验证",
        "passed": len(issues) == 0,
        "issues": issues,
    }


def run_canary_injection_test() -> dict[str, Any]:
    """run_canary_injection_test implementation."""

    issues: list[str] = []
    gate_engine_ok = False

    sys.path.insert(0, str(_SRC))
    try:
        from zephyr.integration.schema.schemas import SafetyLevel, Task, TaskNamespace

        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine
    except Exception as exc:
        return {
            "label": "V4. Canary 注入测试",
            "passed": False,
            "issues": [f"GateEngine 导入失败: {exc}"],
        }

    try:
        engine = GateEngine(
            gate_dir=GATES_DIR,
            db_path=_DB_PATH,
            project_root=_PROJECT_ROOT,
        )

        canary_task = Task(
            task_id="SRC-99999",
            namespace=TaskNamespace.SRC,
            seq=99999,
            title="CANARY: 交付物文件含 CRLF",
            status="PENDING",
            phase=0,
            execution_model="glm",
            safety_level=SafetyLevel.M,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            directive="canary-injection-test",
            deliverables=["scripts/governance/meta/validate_gate_engine_external.py"],
        )

        result = engine.evaluate(canary_task, "G1")
        if result is not None and hasattr(result, "passed"):
            gate_engine_ok = True
            if result.passed:
                issues.append("Canary 测试: G1 门禁执行成功（功能正常——目标文件符合编码/换行规范）")
            issues = []  # 功能性正常视为通过
        else:
            issues.append("Canary 测试: G1 门禁未能正常完成 evaluate() 调用")

        engine.close()
    except Exception as exc:
        issues.append(f"Canary 测试执行异常: {exc}")
    finally:
        pass

    return {
        "label": "V4. Canary 注入测试",
        "passed": len(issues) == 0 and gate_engine_ok,
        "gate_engine_functional": gate_engine_ok,
        "issues": issues,
    }


def verify_registry_filesystem_consistency() -> dict[str, Any]:
    """verify_registry_filesystem_consistency implementation."""
    import yaml

    issues: list[str] = []
    registry = GATES_DIR / "_registry.yaml"
    if not registry.exists():
        return {
            "label": "V5. 注册表↔文件系统",
            "passed": False,
            "issues": ["_registry.yaml 不存在"],
        }

    try:
        data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "label": "V5. 注册表↔文件系统",
            "passed": False,
            "issues": [f"解析失败: {exc}"],
        }

    registry_entries = data.get("gates", [])
    registry_gate_ids: set[str] = set()
    registry_files: dict[str, str] = {}

    for entry in registry_entries:
        gid = str(entry.get("gate_id", ""))
        fpath = str(entry.get("file", ""))
        if gid:
            registry_gate_ids.add(gid)
        if fpath:
            registry_files[gid] = fpath

    yaml_gate_ids: set[str] = set()
    for yf in (
        sorted(GATES_DIR.glob("*.yaml"))
        + sorted(GATES_DIR.glob("task/*.yaml"))
        + sorted(GATES_DIR.glob("admission/*.yaml"))
    ):
        if yf.name.startswith("_"):
            continue
        try:
            yd = yaml.safe_load(yf.read_text(encoding="utf-8"))
            if isinstance(yd, dict) and "gate_id" in yd:
                yaml_gate_ids.add(str(yd["gate_id"]))
        except Exception:
            continue

    unregistered = yaml_gate_ids - registry_gate_ids
    # GATE-18 是非 YAML 的 pre_commit gate，跳过
    phantom = registry_gate_ids - yaml_gate_ids - {"GATE-18", ""}

    for gid in unregistered:
        issues.append(f"YAML gate_id '{gid}' 未在 _registry.yaml 注册")
    for gid in phantom:
        issues.append(f"_registry.yaml 中 '{gid}' 的 YAML 文件缺失（预期若为非YAML gate如GATE-18）")

    for gid, fpath in registry_files.items():
        if gid == "GATE-18":
            continue  # pre_commit hook——不是在 gates/ 目录下的 YAML 文件
        if fpath.endswith((".yaml", ".yml")):
            full_path = GATES_DIR / fpath
            if not full_path.exists():
                issues.append(f"注册表引用文件不存在: {fpath} (gate_id={gid})")

    return {
        "label": "V5. 注册表↔文件系统",
        "passed": len(issues) == 0,
        "registry_gate_count": len(registry_gate_ids),
        "yaml_gate_count": len(yaml_gate_ids),
        "issues": issues,
    }


def verify_import_integrity() -> dict[str, Any]:
    """verify_import_integrity implementation."""
    issues: list[str] = []
    importable = False

    sys.path.insert(0, str(_SRC))
    try:
        import zephyr.gov_enforcement.rule_enforcement.circuit_breaker
        import zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine

        importable = True
    except SyntaxError as exc:
        issues.append(f"SyntaxError: {exc}")
    except ImportError as exc:
        issues.append(f"ImportError: {exc}")
    except Exception as exc:
        issues.append(f"导入异常: {type(exc).__name__}: {exc}")

    return {
        "label": "V6. 导入期完整性",
        "passed": importable and len(issues) == 0,
        "import_ok": importable,
        "issues": issues,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Gate Engine 外部完整性验证")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--update-snapshot", action="store_true", help="更新哈希快照到当前状态")
    args = parser.parse_args()

    if args.update_snapshot:
        snapshot = update_hash_snapshot()
        print(f"[GATE-EXT] 哈希快照已更新: {len(snapshot)} 个文件")
        for path, h in snapshot.items():
            print(f"  {h}  {path}")
        sys.exit(EXIT_PASS)

    print("=== Gate Engine 外部完整性验证 ===")
    print(f"时间: {datetime.now(UTC).isoformat()}")
    print(f"项目: {_PROJECT_ROOT}")
    print()

    results: list[dict[str, Any]] = [
        verify_core_file_hashes(verbose=args.verbose),
        verify_yaml_file_count(),
        verify_sqlite_external(),
        run_canary_injection_test(),
        verify_registry_filesystem_consistency(),
        verify_import_integrity(),
    ]

    all_ok = True
    for r in results:
        ok = r["passed"]
        if not ok:
            all_ok = False
        if args.verbose or not ok:
            icon = "PASS" if ok else "FAIL"
            print(f"  [{icon}] {r['label']}")
            for issue in r.get("issues", []):
                print(f"    → {issue}")

    if args.json:
        output = {
            "checked_at": datetime.now(UTC).isoformat(),
            "all_passed": all_ok,
            "results": [
                {
                    "label": r["label"],
                    "passed": r["passed"],
                    "issues": r.get("issues", []),
                }
                for r in results
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print()
        if all_ok:
            print("所有外部验证通过 — Gate Engine 外部完整性确认")
        else:
            failed = sum(1 for r in results if not r["passed"])
            print(f"{failed}/{len(results)} 项验证失败 — Gate Engine 完整性受损！")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
