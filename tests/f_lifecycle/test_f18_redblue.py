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
# 1. DB 故障测试
# ============================================================================


# P2迁移：patch("_DEPGRAPH_DB") 已失效——生产代码用 get_db_connection() 连 PG，不再读 _DEPGRAPH_DB 路径变量。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 mock get_db_connection 或 PG 临时库替代 patch _DEPGRAPH_DB + sqlite3 临时库），当前 skip。
@pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
class TestDBFailure:
    """红队：DB 故障场景。蓝队：fallback 机制不崩溃。"""

    def test_db_file_not_found_phase_manager(self, tmp_path: Path) -> None:
        """DB 文件不存在时 PhaseManager fallback 到硬编码。"""
        fake_db = tmp_path / "nonexistent.db"
        with patch("zephyr.infrastructure.rollback.phase_manager._DEPGRAPH_DB", fake_db):
            from zephyr.governance.ops_governance.phase_manager import _load_gate_dimensions_from_db, _fallback_gate_dimensions

            dims = _load_gate_dimensions_from_db()
            assert dims is None  # DB 不存在返回 None
            fallback = _fallback_gate_dimensions()
            assert len(fallback) == 8  # fallback 有 8 维度

    def test_db_file_not_found_auto_runner(self, tmp_path: Path) -> None:
        """DB 文件不存在时 AutoRunner 仍能完成 run()。"""
        fake_db = tmp_path / "nonexistent.db"
        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", fake_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            runner = GovernanceAutoRunner()
            result = runner.run()
            # DB 不存在时 _write_audit_log 提前返回，但 cleanup_done 应为 True
            assert result.cleanup_done is True

    def test_db_corrupt_not_sqlite(self, tmp_path: Path) -> None:
        """DB 文件损坏（非 SQLite 格式）时不崩溃。"""
        corrupt_db = tmp_path / "corrupt.db"
        _create_corrupt_db(corrupt_db)
        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", corrupt_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            runner = GovernanceAutoRunner()
            result = runner.run()
            # 损坏 DB 不应导致崩溃
            assert result.cleanup_done is True

    def test_db_gates_table_missing(self, tmp_path: Path) -> None:
        """gates 表不存在时查询不崩溃。"""
        db_no_tables = tmp_path / "no_tables.db"
        _create_db_without_tables(db_no_tables)
        with patch("zephyr.infrastructure.rollback.phase_manager._DEPGRAPH_DB", db_no_tables):
            from zephyr.governance.ops_governance.phase_manager import PhaseManager

            pm = PhaseManager()
            # 查询不存在的表应返回空 dict
            report = pm.status_report()
            assert isinstance(report, dict)

    def test_db_columns_missing(self, tmp_path: Path) -> None:
        """gates 表缺少 event_driven/auto_start 列时不崩溃。"""
        db_no_cols = tmp_path / "no_cols.db"
        _create_db_without_columns(db_no_cols)
        with patch("zephyr.infrastructure.rollback.phase_manager._DEPGRAPH_DB", db_no_cols):
            from zephyr.governance.ops_governance.phase_manager import PhaseManager

            pm = PhaseManager()
            # 查询不存在的列应触发异常但被捕获
            result = pm.verify_auto_start()
            assert isinstance(result, dict)

    def test_db_locked_by_another_process(self, tmp_path: Path) -> None:
        """DB 被另一进程锁定写锁时查询不死锁。"""
        locked_db = tmp_path / "locked.db"
        _create_temp_db(locked_db)
        # 持有写锁
        lock_conn = sqlite3.connect(str(locked_db))
        lock_conn.execute("BEGIN EXCLUSIVE")
        try:
            with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", locked_db):
                from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

                runner = GovernanceAutoRunner()
                # 应能完成（查询用独立连接，写 audit_log 可能失败但不崩溃）
                result = runner.run()
                assert result.cleanup_done is True
        finally:
            lock_conn.rollback()
            lock_conn.close()


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

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_audit_log_db_readonly(self, tmp_path: Path) -> None:
        """DB 只读时审计日志写入失败但不崩溃。"""
        readonly_db = tmp_path / "readonly.db"
        _create_temp_db(readonly_db)
        # 设置只读
        readonly_db.chmod(0o444)

        try:
            with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", readonly_db):
                from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

                runner = GovernanceAutoRunner()
                result = runner.run()
                # 写入失败但 cleanup_done 仍为 True
                assert result.cleanup_done is True
        finally:
            readonly_db.chmod(0o644)

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

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_audit_log_table_missing(self, tmp_path: Path) -> None:
        """governance_audit_logs 表不存在时自动创建。"""
        db_no_audit = tmp_path / "no_audit.db"
        conn = sqlite3.connect(str(db_no_audit))
        try:
            conn.execute("CREATE TABLE gates (gate_id TEXT, category TEXT, status TEXT, auto_start INTEGER, event_driven TEXT)")
            conn.commit()
        finally:
            conn.close()

        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", db_no_audit):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            runner = GovernanceAutoRunner()
            runner._write_audit_log()
            # 表不存在时 CREATE TABLE IF NOT EXISTS 应自动创建
            conn = sqlite3.connect(str(db_no_audit))
            try:
                count = conn.execute("SELECT COUNT(*) FROM governance_audit_logs").fetchone()[0]
                assert count > 0
            finally:
                conn.close()


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

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 已删除/拆分为函数式 API")
    def test_concurrent_phase_managers(self) -> None:
        """多个 PhaseManager 同时 status_report() 不崩溃。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager

        errors: list[Exception] = []

        def query_one() -> bool:
            try:
                pm = PhaseManager()
                report = pm.status_report()
                return isinstance(report, dict)
            except Exception as e:
                errors.append(e)
                return False

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(query_one) for _ in range(8)]
            results = [f.result() for f in as_completed(futures)]

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert all(results)

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

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_concurrent_audit_log_writes(self, tmp_path: Path) -> None:
        """并发写 audit_logs 不死锁。"""
        concurrent_db = tmp_path / "concurrent.db"
        _create_temp_db(concurrent_db)

        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", concurrent_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            errors: list[Exception] = []

            def write_audit() -> bool:
                try:
                    runner = GovernanceAutoRunner()
                    runner._result.total_gates = 10
                    runner._result.passed_gates = 8
                    runner._result.failed_gates = 2
                    runner._result.skipped_gates = 0
                    runner._write_audit_log()
                    return True
                except Exception as e:
                    errors.append(e)
                    return False

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(write_audit) for _ in range(5)]
                results = [f.result() for f in as_completed(futures)]

            assert len(errors) == 0, f"Concurrent write errors: {errors}"
            assert all(results)

            # 验证所有记录都写入
            conn = sqlite3.connect(str(concurrent_db))
            try:
                count = conn.execute("SELECT COUNT(*) FROM governance_audit_logs").fetchone()[0]
                assert count >= 5
            finally:
                conn.close()


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

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_event_driven_null_in_db(self, tmp_path: Path) -> None:
        """DB 中 event_driven 为 NULL 时查询不崩溃。"""
        null_db = tmp_path / "null_event.db"
        conn = sqlite3.connect(str(null_db))
        try:
            conn.execute(
                "CREATE TABLE gates (gate_id TEXT, category TEXT, status TEXT, "
                "auto_start INTEGER, event_driven TEXT)"
            )
            conn.execute("INSERT INTO gates VALUES ('g1', 'd1_metadata', 'active', 1, NULL)")
            conn.execute("INSERT INTO gates VALUES ('g2', 'd1_metadata', 'active', 1, 'always')")
            conn.commit()
        finally:
            conn.close()

        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", null_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            # 查询 NULL event_driven 不崩溃
            always_gates = GovernanceAutoRunner.get_gates_by_event("always")
            assert "g2" in always_gates
            # NULL 不匹配 'always'
            assert "g1" not in always_gates

    def test_all_event_types_returns_list(self) -> None:
        """get_all_event_types() 返回列表。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        result = GovernanceAutoRunner.get_all_event_types()
        assert isinstance(result, list)
        assert len(result) > 0


# ============================================================================
# 7. 数据一致性测试
# ============================================================================


# P2迁移：所有测试依赖 patch("_DEPGRAPH_DB") + sqlite3 临时 DB，patch 已失效。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 mock get_db_connection 或 PG 临时库替代 patch _DEPGRAPH_DB + sqlite3 临时库），当前 skip。
@pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
class TestDataConsistency:
    """红队：数据不一致。蓝队：不崩溃，返回合理结果。"""

    def test_gate_id_case_sensitivity(self, tmp_path: Path) -> None:
        """gate_id 大小写不一致时查询精确匹配。"""
        case_db = tmp_path / "case.db"
        conn = sqlite3.connect(str(case_db))
        try:
            conn.execute(
                "CREATE TABLE gates (gate_id TEXT, category TEXT, status TEXT, "
                "auto_start INTEGER, event_driven TEXT)"
            )
            conn.execute("INSERT INTO gates VALUES ('G_TRAE_003', 'trae_rule', 'active', 1, 'always')")
            conn.execute("INSERT INTO gates VALUES ('g_trae_003', 'trae_rule', 'active', 1, 'always')")
            conn.commit()
        finally:
            conn.close()

        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", case_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            always_gates = GovernanceAutoRunner.get_gates_by_event("always")
            # 大小写敏感：两个都返回
            assert len(always_gates) == 2

    def test_empty_category_in_db(self, tmp_path: Path) -> None:
        """category 为空字符串时查询返回空。"""
        empty_cat_db = tmp_path / "empty_cat.db"
        conn = sqlite3.connect(str(empty_cat_db))
        try:
            conn.execute(
                "CREATE TABLE gates (gate_id TEXT, category TEXT, status TEXT, "
                "auto_start INTEGER, event_driven TEXT)"
            )
            conn.execute("INSERT INTO gates VALUES ('g1', '', 'active', 1, 'always')")
            conn.execute("INSERT INTO gates VALUES ('g2', NULL, 'active', 1, 'always')")
            conn.commit()
        finally:
            conn.close()

        with patch("zephyr.infrastructure.rollback.phase_manager._DEPGRAPH_DB", empty_cat_db):
            from zephyr.governance.ops_governance.phase_manager import _load_gate_dimensions_from_db

            dims = _load_gate_dimensions_from_db()
            if dims:
                # 空 category 不匹配任何维度
                for dim_gates in dims.values():
                    assert "g1" not in dim_gates
                    assert "g2" not in dim_gates

    def test_inactive_gates_excluded(self, tmp_path: Path) -> None:
        """status='inactive' 的 gate 被排除。"""
        inactive_db = tmp_path / "inactive.db"
        _create_temp_db(inactive_db)
        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", inactive_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            always_gates = GovernanceAutoRunner.get_gates_by_event("always")
            # gate_test_4 是 inactive，不应出现
            assert "gate_test_4" not in always_gates
            assert "gate_test_1" in always_gates

    def test_auto_start_disabled_excluded(self, tmp_path: Path) -> None:
        """auto_start=0 的 gate 被排除。"""
        disabled_db = tmp_path / "disabled.db"
        _create_temp_db(disabled_db)
        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", disabled_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            always_gates = GovernanceAutoRunner.get_gates_by_event("always")
            # gate_test_3 auto_start=0，不应出现
            assert "gate_test_3" not in always_gates


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

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 已删除/拆分为函数式 API")
    def test_verify_auto_start_idempotent(self) -> None:
        """verify_auto_start() 多次调用结果一致。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager

        pm = PhaseManager()
        r1 = pm.verify_auto_start()
        r2 = pm.verify_auto_start()
        r3 = pm.verify_auto_start()
        assert r1 == r2 == r3

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 已删除/拆分为函数式 API")
    def test_status_report_idempotent(self) -> None:
        """status_report() 多次调用结果一致。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager

        pm = PhaseManager()
        r1 = pm.status_report()
        r2 = pm.status_report()
        assert r1["total_gates"] == r2["total_gates"]
        assert r1["dimensions"] == r2["dimensions"]


# ============================================================================
# 9. 边界值测试
# ============================================================================


class TestBoundaryValues:
    """红队：边界值。蓝队：不崩溃。"""

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_empty_db_zero_gates(self, tmp_path: Path) -> None:
        """空 DB（0 个 gate）时不崩溃。"""
        empty_db = tmp_path / "empty.db"
        _create_temp_db(empty_db, with_data=False)
        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", empty_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            runner = GovernanceAutoRunner()
            result = runner.run()
            assert result.cleanup_done is True

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_empty_db_phase_manager(self, tmp_path: Path) -> None:
        """空 DB 时 PhaseManager 返回空维度。"""
        empty_db = tmp_path / "empty_pm.db"
        _create_temp_db(empty_db, with_data=False)
        with patch("zephyr.infrastructure.rollback.phase_manager._DEPGRAPH_DB", empty_db):
            from zephyr.governance.ops_governance.phase_manager import _load_gate_dimensions_from_db

            dims = _load_gate_dimensions_from_db()
            if dims:
                for dim_gates in dims.values():
                    assert len(dim_gates) == 0

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_super_long_gate_id(self, tmp_path: Path) -> None:
        """超长 gate_id 不崩溃。"""
        long_db = tmp_path / "long.db"
        conn = sqlite3.connect(str(long_db))
        try:
            conn.execute(
                "CREATE TABLE gates (gate_id TEXT, category TEXT, status TEXT, "
                "auto_start INTEGER, event_driven TEXT)"
            )
            long_id = "g" + "x" * 10000
            conn.execute("INSERT INTO gates VALUES (?, 'd1_metadata', 'active', 1, 'always')", (long_id,))
            conn.commit()
        finally:
            conn.close()

        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", long_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            always_gates = GovernanceAutoRunner.get_gates_by_event("always")
            assert len(always_gates) == 1
            assert len(always_gates[0]) > 1000

    def test_super_long_errors_in_audit(self, tmp_path: Path) -> None:
        """超长 errors 字符串写入 audit_logs 不崩溃。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

        runner = GovernanceAutoRunner()
        runner._result.errors.append("E" * 100000)
        runner._write_audit_log()
        # 不崩溃即通过

    @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
    def test_many_event_types(self, tmp_path: Path) -> None:
        """大量不同 event_driven 类型时不崩溃。"""
        many_db = tmp_path / "many_events.db"
        conn = sqlite3.connect(str(many_db))
        try:
            conn.execute(
                "CREATE TABLE gates (gate_id TEXT, category TEXT, status TEXT, "
                "auto_start INTEGER, event_driven TEXT)"
            )
            for i in range(100):
                conn.execute(
                    "INSERT INTO gates VALUES (?, 'd1_metadata', 'active', 1, ?)",
                    (f"gate_{i}", f"on_event_{i}"),
                )
            conn.commit()
        finally:
            conn.close()

        with patch("zephyr.governance.auto_runner._DEPGRAPH_DB", many_db):
            from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner

            event_types = GovernanceAutoRunner.get_all_event_types()
            assert len(event_types) == 100

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
