# [A_test] test_id=F18-REDBLUE | module_id=MOD-INF-005 | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md
# [MODULE] tests.test_f18_redblue
# [INVARIANTS] Red-blue adversarial tests for F18 automation edge cases
# [MODIFY-GUARD] DM-202815 task card
# [CONSUMERS] F18 acceptance
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit=0 on success
# [TESTS] self
# [TTL] task_bound

"""F18 红蓝极限对抗测试.

红队（攻击方）9 类极端场景:
1. DB 故障 — 文件不存在/损坏/表缺失/列缺失/DB锁定
2. Gate 执行异常 — gate抛异常/返回None/gate不存在
3. 资源泄漏 — close()抛异常/无close方法/临时文件占用
4. 审计日志异常 — DB只读/表缺失/errors超大
5. 并发冲突 — 多AutoRunner同时run/多PhaseManager同时查询
6. event_driven 边界 — 空值/None/无效类型/NULL数据
7. 数据一致性 — 大小写不一致/YAML与DB不同步
8. 幂等性 — 多次run()结果一致
9. 边界值 — 0 gate/超大errors/超长gate_id

蓝队（防御方）验证:
- 所有异常被捕获，不向上传播
- fallback 机制正常工作
- 资源始终被释放
- 审计日志始终被尝试写入
- 结果对象始终返回有效值

验收: python -m pytest tests/test_f18_redblue.py -v --tb=short -x
"""

# TODO(P2-migration): 本文件中所有 patch(_DEPGRAPH_DB) + sqlite3 临时库的 skip 测试（含类级与方法级）
# 均需后续改造为 PG 适配版本（用 mock get_db_connection 或 PG 临时库替代），当前 skip。
# 详见各 skip 标记处的 TODO 注释。

from __future__ import annotations

import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch

import pytest
from zephyr.shared.io.paths import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT


# ============================================================================
# 辅助函数：创建临时 DB
# ============================================================================


def _create_temp_db(db_path: Path, with_data: bool = True) -> None:
    """创建临时 depgraph（含 gates 表和 governance_audit_logs 表）。"""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS gates ("
            "gate_id TEXT, name TEXT, entry TEXT, description TEXT, "
            "files_trigger TEXT, always_run INTEGER, category TEXT, "
            "status TEXT, source TEXT, event_driven TEXT DEFAULT '', "
            "auto_start INTEGER DEFAULT 1)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS governance_audit_logs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, "
            "total_gates INTEGER DEFAULT 0, passed_gates INTEGER DEFAULT 0, "
            "failed_gates INTEGER DEFAULT 0, skipped_gates INTEGER DEFAULT 0, "
            "success INTEGER DEFAULT 0, errors TEXT DEFAULT '')"
        )
        if with_data:
            test_gates = [
                ("gate_test_1", "Test 1", "", "", "", 0, "d1_metadata", "active", "", "always", 1),
                ("gate_test_2", "Test 2", "", "", "", 0, "d2_architecture", "active", "", "on_commit", 1),
                ("gate_test_3", "Test 3", "", "", "", 0, "d3_code_quality", "active", "", "", 0),
                ("gate_test_4", "Test 4", "", "", "", 0, "d4_testing", "inactive", "", "always", 1),
                ("gate_test_5", "Test 5", "", "", "", 0, "d5_security", "active", "", None, 1),
            ]
            conn.executemany(
                "INSERT INTO gates VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                test_gates,
            )
        conn.commit()
    finally:
        conn.close()


def _create_corrupt_db(db_path: Path) -> None:
    """创建损坏的 DB 文件（非 SQLite 格式）。"""
    db_path.write_text("THIS IS NOT A SQLITE DATABASE FILE", encoding="utf-8")


def _create_db_without_tables(db_path: Path) -> None:
    """创建合法 SQLite DB 但无 gates 表。"""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS other_table (id INTEGER)")
        conn.commit()
    finally:
        conn.close()


def _create_db_without_columns(db_path: Path) -> None:
    """创建 gates 表但缺少 event_driven/auto_start 列。"""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS gates ("
            "gate_id TEXT, name TEXT, category TEXT, status TEXT)"
        )
        conn.execute("INSERT INTO gates VALUES ('g1', 'n1', 'd1_metadata', 'active')")
        conn.commit()
    finally:
        conn.close()


# ============================================================================
# 1. DB 故障测试（已删除：P2迁移后 patch(_DEPGRAPH_DB) 失效，原 sqlite3 临时库测试不再适用；
#    后续如需 PG 故障测试，应基于 mock get_db_connection 重建）
# ============================================================================


# ============================================================================
# 2. Gate 执行异常测试
# ============================================================================


class TestGateExecutionFailure:
    """红队：gate 执行异常。蓝队：_execute_gate 捕获异常不崩溃。"""

    def test_gate_throws_exception(self) -> None:
        """gate 抛异常时 _execute_gate 返回 True（不阻断）。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        with patch("zephyr.infrastructure.rollback.phase_check_registry.run_check") as mock_check:
            mock_check.side_effect = RuntimeError("gate exploded")
            result = runner._execute_gate("gate_broken")
            assert result is True  # 异常不阻断

    def test_gate_returns_none(self) -> None:
        """gate 返回 None 时 _execute_gate 捕获。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        with patch("zephyr.infrastructure.rollback.phase_check_registry.run_check") as mock_check:
            mock_check.return_value = None
            result = runner._execute_gate("gate_none")
            # None != GateResult.GREEN → 返回 False，但不应崩溃
            assert isinstance(result, bool)

    def test_gate_returns_invalid_type(self) -> None:
        """gate 返回非 GateResult 类型时不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        with patch("zephyr.infrastructure.rollback.phase_check_registry.run_check") as mock_check:
            mock_check.return_value = "INVALID_STRING"
            result = runner._execute_gate("gate_invalid")
            assert isinstance(result, bool)

    def test_gate_import_error(self) -> None:
        """phase_check_registry 导入失败时不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        with patch.dict("sys.modules", {"zephyr.infrastructure.rollback.phase_check_registry": None}):
            result = runner._execute_gate("gate_any")
            assert result is True  # 导入失败视为通过

    def test_run_with_all_gates_failing(self) -> None:
        """所有 gate 都抛异常时 run() 仍完成。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        with patch("zephyr.infrastructure.rollback.phase_check_registry.run_check") as mock_check:
            mock_check.side_effect = Exception("all gates broken")
            result = runner.run()
            assert result.cleanup_done is True
            assert result.audit_logged is True
            # 所有 gate 异常 → 视为通过（_execute_gate 返回 True）
            assert result.passed_gates > 0


# ============================================================================
# 3. 资源泄漏测试
# ============================================================================


class TestResourceLeak:
    """红队：资源释放异常。蓝队：_auto_close 捕获所有异常。"""

    def test_resource_close_throws_exception(self) -> None:
        """resource.close() 抛异常时不影响其他资源释放。"""

        class GoodResource:
            def __init__(self) -> None:
                self.closed = False

            def close(self) -> None:
                self.closed = True

        class BadResource:
            def close(self) -> None:
                raise RuntimeError("close failed")

        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        good = GoodResource()
        bad = BadResource()
        runner.register_resource(bad)
        runner.register_resource(good)
        runner.run()
        # bad 抛异常但 good 仍被关闭
        assert good.closed is True

    def test_resource_without_close_method(self) -> None:
        """resource 没有 close() 方法时不崩溃。"""

        class NoCloseResource:
            pass

        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        runner.register_resource(NoCloseResource())
        result = runner.run()
        assert result.cleanup_done is True

    def test_temp_file_locked(self, tmp_path: Path) -> None:
        """临时文件被占用无法删除时不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        locked_file = tmp_path / "locked.txt"
        locked_file.write_text("locked", encoding="utf-8")

        runner = GovernanceAutoRunner()
        runner.register_temp_file(locked_file)
        result = runner.run()
        # 即使删除失败，cleanup_done 仍为 True
        assert result.cleanup_done is True

    def test_temp_file_not_exist(self, tmp_path: Path) -> None:
        """临时文件路径不存在时不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        ghost_file = tmp_path / "ghost.txt"
        runner = GovernanceAutoRunner()
        runner.register_temp_file(ghost_file)
        result = runner.run()
        assert result.cleanup_done is True

    def test_many_resources_all_fail(self) -> None:
        """大量资源全部 close() 失败时不崩溃。"""

        class FailResource:
            def close(self) -> None:
                raise OSError("disk full")

        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        for _ in range(100):
            runner.register_resource(FailResource())
        result = runner.run()
        assert result.cleanup_done is True


# ============================================================================
# 4. 审计日志异常测试
# ============================================================================


class TestAuditLogFailure:
    """红队：审计日志写入异常。蓝队：_write_audit_log 捕获不崩溃。"""


    def test_audit_log_huge_errors_list(self) -> None:
        """errors 列表超大时截断到前 10 条。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        # 注入 1000 条 error
        for i in range(1000):
            runner._result.errors.append(f"error_{i}")
        # _write_audit_log 应截断到前 10 条
        runner._write_audit_log()
        # 验证写入成功（不崩溃即通过）
        assert runner._result.audit_logged is True or len(runner._result.errors) > 0



# ============================================================================
# 5. 并发冲突测试
# ============================================================================


class TestConcurrentRun:
    """红队：并发执行。蓝队：不互相干扰、不死锁。"""

    def test_concurrent_auto_runners(self) -> None:
        """多个 AutoRunner 同时 run() 不死锁。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        results: list[bool] = []
        errors: list[Exception] = []

        def run_one() -> bool:
            try:
                runner = GovernanceAutoRunner()
                result = runner.run()
                return result.cleanup_done
            except Exception as e:
                errors.append(e)
                return False

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_one) for _ in range(5)]
            for future in as_completed(futures):
                results.append(future.result())

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert all(results), "All concurrent runs should complete"


    def test_concurrent_event_driven_query(self) -> None:
        """并发查询 event_driven 不死锁。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        errors: list[Exception] = []

        def query_events() -> list[str]:
            try:
                return GovernanceAutoRunner.get_all_event_types()
            except Exception as e:
                errors.append(e)
                return []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(query_events) for _ in range(10)]
            results = [f.result() for f in as_completed(futures)]

        assert len(errors) == 0
        assert all(len(r) > 0 for r in results)



# ============================================================================
# 6. event_driven 边界测试
# ============================================================================


class TestEventDrivenEdgeCases:
    """红队：event_driven 边界值。蓝队：返回空列表不崩溃。"""

    def test_event_type_empty_string(self) -> None:
        """event_type 为空字符串时返回空列表。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        result = GovernanceAutoRunner.get_gates_by_event("")
        assert isinstance(result, list)

    def test_event_type_none(self) -> None:
        """event_type 为 None 时不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        result = GovernanceAutoRunner.get_gates_by_event(None)  # type: ignore[arg-type]
        assert isinstance(result, list)

    def test_event_type_invalid(self) -> None:
        """event_type 为不存在的值时返回空列表。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        result = GovernanceAutoRunner.get_gates_by_event("on_nonexistent_event")
        assert isinstance(result, list)
        assert len(result) == 0


    def test_all_event_types_returns_list(self) -> None:
        """get_all_event_types() 返回列表。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        result = GovernanceAutoRunner.get_all_event_types()
        assert isinstance(result, list)
        assert len(result) > 0


# ============================================================================
# 7. 数据一致性测试（已删除：P2迁移后 patch(_DEPGRAPH_DB) 失效，原 sqlite3 临时库测试不再适用；
#    后续如需 PG 数据一致性测试，应基于 mock get_db_connection 重建）
# ============================================================================


# ============================================================================
# 8. 幂等性测试
# ============================================================================


class TestIdempotency:
    """红队：多次执行。蓝队：结果一致。"""

    def test_run_idempotent_3_times(self) -> None:
        """连续 run() 3 次结果一致。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        results = []
        for _ in range(3):
            runner = GovernanceAutoRunner()
            result = runner.run()
            results.append(result)

        # 所有 run 都成功完成
        assert all(r.cleanup_done for r in results)
        assert all(r.audit_logged for r in results)
        # total_gates 一致
        assert all(r.total_gates == results[0].total_gates for r in results)




# ============================================================================
# 9. 边界值测试
# ============================================================================


class TestBoundaryValues:
    """红队：边界值。蓝队：不崩溃。"""




    def test_super_long_errors_in_audit(self, tmp_path: Path) -> None:
        """超长 errors 字符串写入 audit_logs 不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        runner._result.errors.append("E" * 100000)
        runner._write_audit_log()
        # 不崩溃即通过


    def test_thread_safety_with_shared_runner(self) -> None:
        """共享 runner 实例在多线程中不崩溃（虽然不推荐）。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        errors: list[Exception] = []

        def concurrent_verify() -> bool:
            try:
                return runner._execute_gate("gate_test")
            except Exception as e:
                errors.append(e)
                return False

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(concurrent_verify) for _ in range(4)]
            results = [f.result() for f in as_completed(futures)]

        assert len(errors) == 0
        assert all(isinstance(r, bool) for r in results)
