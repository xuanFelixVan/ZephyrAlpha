#!/usr/bin/env python3
# [BLUEPRINT] MOD-REMEDIATION_PROGRESS_SMOKE | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §smoke-test
# [MODULE] scripts.governance.test_remediation_progress_smoke
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.remediation_progress_reconciler (RemediationProgressRecord, record_remediation_progress, query_all_dimensions, query_stale_dimensions, make_remediation_progress_reconciler)
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 真实写入 temp governance.db 验证三要素（持久化+可发现+可阻断）；隔离生产 governance.db（TRAE-054 测试隔离铁律）；main() 返回 0=成功 1=失败
# [MODIFY-GUARD] _test_* 函数签名；_BLOCK_SECONDS 阈值（与 remediation_progress_reconciler.py 一致）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] main() 返回 0=ALL PASSED 1=FAILED；不抛异常（failures 列表收集）
# [TESTS] —
# [TTL] permanent
# [A_module] module_id=MOD-REMEDIATION_PROGRESS_SMOKE | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
"""test_remediation_progress_smoke.py — Phase 3.1 治本进度 reconciler end-to-end smoke test。

真实调用 record_remediation_progress / query_all_dimensions / query_stale_dimensions /
make_remediation_progress_reconciler，真实写入 temp governance.db，验证三要素：
1. 持久化：写入后能查到
2. 可发现：query_all_dimensions 返回完整数据
3. 可阻断：stale 维度 → block_next

使用临时目录隔离生产 governance.db（TRAE-054 测试隔离铁律）。
"""

__manifest__ = """
args: []
description: test_remediation_progress_smoke.py — Phase 3.1 治本进度 reconciler end-to-end
  smoke test。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from _shared.constants import EXIT_FINDINGS, EXIT_PASS

if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

_SQL_INSERT_STALE_TEST = (
    "INSERT OR REPLACE INTO remediation_progress "
    "(dimension_id, dimension_kind, title, status, last_updated, "
    "last_session_id, last_commit_sha, target_completion_date, "
    "blocker_reason, details_json) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SQL_UPDATE_TIMESTAMP = (
    "UPDATE remediation_progress SET last_updated = ? WHERE dimension_id = ?"
)


class _FakeGateway:
    """模拟 GitCommitGateway（仅用 project_root 属性）。"""

    def __init__(self, root):
        """__init__ implementation."""
        self.project_root = root


def _test_record_and_query(project_root, record_cls, record_fn, query_fn, failures):
    """测试 1-2：record + query_all_dimensions（持久化 + 可发现）。"""
    print("[2/6] test record_remediation_progress (in_progress)...")
    ok = record_fn(
        project_root,
        record_cls(
            dimension_id="ARCH-TEST-001",
            dimension_kind="issue",
            title="smoke test dimension",
            status="in_progress",
            session_id="smoke-test-session",
            details={"phase": "3.1", "test": True},
        ),
    )
    if not ok:
        failures.append("record_remediation_progress returned False")
        return
    print("  OK: record returned True")

    print("[3/6] test query_all_dimensions...")
    all_dims = query_fn(project_root)
    if len(all_dims) != 1:
        failures.append(f"expected 1 dimension, got {len(all_dims)}")
        return
    d = all_dims[0]
    if d["dimension_id"] != "ARCH-TEST-001":
        failures.append(f"dimension_id mismatch: {d['dimension_id']}")
    if d["status"] != "in_progress":
        failures.append(f"status mismatch: {d['status']}")
    if d["details"] != {"phase": "3.1", "test": True}:
        failures.append(f"details mismatch: {d['details']}")
    print(f"  OK: found dimension {d['dimension_id']} status={d['status']}")


def _test_fresh_stale(project_root, db_path, old_time, query_stale_fn, failures):
    """测试 3-4：fresh 维度无 stale + 手动插入 stale 维度检测。"""
    print("[4/6] test query_stale_dimensions (fresh, expect empty)...")
    stale = query_stale_fn(project_root)
    if stale:
        failures.append(f"expected no stale dimensions, got {len(stale)}")
    else:
        print("  OK: no stale dimensions (fresh)")

    print("[5/6] test stale dimension detection (>90 days)...")
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        _SQL_INSERT_STALE_TEST,
        ("ARCH-TEST-STALE", "issue", "stale test dimension",
         "in_progress", old_time, "", "", None, None, None),
    )
    conn.commit()
    conn.close()

    stale = query_stale_fn(project_root)
    if len(stale) != 1:
        failures.append(f"expected 1 stale dimension, got {len(stale)}")
    elif stale[0]["dimension_id"] != "ARCH-TEST-STALE":
        failures.append(f"stale dimension_id mismatch: {stale[0]['dimension_id']}")
    else:
        print(f"  OK: detected stale dimension {stale[0]['dimension_id']}")


def _test_completed_exclusion(project_root, db_path, record_cls, record_fn, query_stale_fn, old_time, failures):
    """测试 5b：completed 维度即使过期也不算 stale。"""
    print("[5b/6] test completed dimension not flagged stale...")
    record_fn(
        project_root,
        record_cls(
            dimension_id="ARCH-TEST-COMPLETED",
            dimension_kind="issue",
            title="completed test dimension",
            status="completed",
        ),
    )
    conn = sqlite3.connect(str(db_path))
    conn.execute(_SQL_UPDATE_TIMESTAMP, (old_time, "ARCH-TEST-COMPLETED"))
    conn.commit()
    conn.close()
    stale = query_stale_fn(project_root)
    if len(stale) != 1:
        failures.append(
            f"expected 1 stale (completed should be excluded), got {len(stale)}"
        )
    else:
        print("  OK: completed dimension excluded from stale")


def _test_reconciler(project_root, record_cls, record_fn, make_reconciler_fn, failures):
    """测试 6：reconciler factory + block_next + clean。"""
    from zephyr.governance.audit.reconciliation_registry import ReconcileResult

    print("[6/6] test make_remediation_progress_reconciler (block_next)...")
    spec = make_reconciler_fn(_FakeGateway(project_root))
    if spec.gate_id != "GATE-REMEDIATION-PROGRESS":
        failures.append(f"gate_id mismatch: {spec.gate_id}")
    if spec.priority != 900:
        failures.append(f"priority mismatch: {spec.priority}")
    if not spec.trigger(["any_file.py"]):
        failures.append("trigger should always return True")

    result = spec.reconcile(["any_file.py"], "smoke-session")
    if not isinstance(result, ReconcileResult):
        failures.append(f"result type mismatch: {type(result)}")
    elif result.action != "block_next":
        failures.append(f"expected block_next (stale exists), got {result.action}")
    elif "ARCH-TEST-STALE" not in result.detail:
        failures.append(f"detail missing stale dimension: {result.detail}")
    else:
        print("  OK: reconciler returned block_next with detail")
        print(f"  gate_id={result.gate_id}")

    record_fn(
        project_root,
        record_cls(
            dimension_id="ARCH-TEST-STALE",
            dimension_kind="issue",
            title="stale test dimension (now updated)",
            status="completed",
        ),
    )
    result2 = spec.reconcile(["any_file.py"], "smoke-session")
    if result2.action != "clean":
        failures.append(f"expected clean after updating stale, got {result2.action}")
    else:
        print("  OK: reconciler returned clean after stale resolved")


def main() -> int:
    """入口：编排全部 smoke test。"""
    from zephyr.governance.audit.remediation_progress_reconciler import (
        RemediationProgressRecord,
        make_remediation_progress_reconciler,
        query_all_dimensions,
        query_stale_dimensions,
        record_remediation_progress,
    )

    failures: list[str] = []
    print("=== Phase 3.1 remediation_progress smoke test ===")

    old_time = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    with tempfile.TemporaryDirectory(prefix="remediation_smoke_") as tmpdir:
        project_root = Path(tmpdir)
        db_path = project_root / "data" / "databases" / "governance.db"
        print(f"[1/6] temp project_root: {project_root}")

        _test_record_and_query(
            project_root, RemediationProgressRecord,
            record_remediation_progress, query_all_dimensions, failures,
        )
        _test_fresh_stale(
            project_root, db_path, old_time, query_stale_dimensions, failures,
        )
        _test_completed_exclusion(
            project_root, db_path, RemediationProgressRecord,
            record_remediation_progress, query_stale_dimensions, old_time, failures,
        )
        _test_reconciler(
            project_root, RemediationProgressRecord,
            record_remediation_progress, make_remediation_progress_reconciler, failures,
        )

    print("\n=== Summary ===")
    if failures:
        print(f"FAILED ({len(failures)} failures):")
        for f in failures:
            print(f"  - {f}")
        return EXIT_FINDINGS
    print("ALL PASSED (6/6 tests)")
    return EXIT_PASS
if __name__ == "__main__":
    sys.exit(main())
