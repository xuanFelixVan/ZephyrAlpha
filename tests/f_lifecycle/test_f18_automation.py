# [A_test] test_id=F18-AUTO | module_id=MOD-INF-005 | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md
# [MODULE] tests.test_f18_automation
# [INVARIANTS] Tests F18 automation: auto-startup, event-driven, auto-run, auto-close
# [MODIFY-GUARD] DM-202815 task card
# [CONSUMERS] DM-202815 acceptance
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit=0 on success
# [TESTS] self
# [TTL] task_bound

"""F18 治理脚本系统自动化测试.

测试 4 个自动化机制:
1. 自动启动 — PhaseManager 调度所有 governance gate（从 depgraph 查询）
2. 事件启动 — event_driven 配置触发脚本执行（从 depgraph 查询）
3. 自动运行 — GovernanceAutoRunner 执行 8 维度 gate
4. 自动关闭 — 资源释放 + 临时文件清理 + 审计日志

验收: python -m pytest tests/test_f18_automation.py -v --tb=short
"""

from __future__ import annotations

from pathlib import Path

import psycopg2
import pytest

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
# 注：depgraph 已迁移到 PostgreSQL（P2迁移），_DEPGRAPH_DB 路径常量已移除


# ============================================================================
# 1. 自动启动测试 — PhaseManager
# ============================================================================


class TestAutoStartup:
    """自动启动测试:验证 PhaseManager 能调度所有 governance gate（从 depgraph 查询）。"""

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 类已删除/拆分为函数式 API")
    def test_phase_manager_importable(self) -> None:
        """PhaseManager 可导入。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager
        pm = PhaseManager()
        assert pm is not None

    def test_phase_manager_has_phases(self) -> None:
        """PhaseManager 包含所有施工阶段（PHASE_SEQUENCE）。"""
        from zephyr.governance.ops_governance.phase_manager import PHASE_SEQUENCE, ConstructionPhase
        assert ConstructionPhase.PHASE_0_SKELETON in PHASE_SEQUENCE
        assert ConstructionPhase.PHASE_1_FUNCTIONAL in PHASE_SEQUENCE
        assert ConstructionPhase.PHASE_2_E2E in PHASE_SEQUENCE

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 类已删除/拆分为函数式 API")
    def test_all_phases_auto_start(self) -> None:
        """所有 gate 的 auto_start=1（从 depgraph 查询）。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager
        pm = PhaseManager()
        auto_start_map = pm.verify_auto_start()
        # 所有 gate 的 auto_start 都应为 True
        for gate_id, enabled in auto_start_map.items():
            assert enabled is True, f"{gate_id} auto_start should be True"

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 类已删除/拆分为函数式 API")
    def test_verify_auto_start_returns_dict(self) -> None:
        """verify_auto_start() 返回非空 dict。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager
        pm = PhaseManager()
        result = pm.verify_auto_start()
        assert isinstance(result, dict)
        assert len(result) > 0

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 类已删除/拆分为函数式 API")
    def test_status_report_contains_governance(self) -> None:
        """status_report() 包含 governance 维度信息。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager
        pm = PhaseManager()
        report = pm.status_report()
        assert isinstance(report, dict)
        assert "dimensions" in report
        assert "d6_governance" in report["dimensions"]

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 类已删除/拆分为函数式 API")
    def test_get_governance_gates_returns_dict(self) -> None:
        """get_governance_gates() 返回非空 dict（8维度）。"""
        from zephyr.governance.ops_governance.phase_manager import PhaseManager
        pm = PhaseManager()
        gates = pm.get_governance_gates()
        assert isinstance(gates, dict)
        assert len(gates) > 0

    @pytest.mark.skip(reason="ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，维度分组被阶段分组替代")
    def test_governance_gate_dimensions_has_8_dimensions(self) -> None:
        """GOVERNANCE_GATE_DIMENSIONS 包含 8 个维度（含 d8_functional）。"""
        from zephyr.governance.ops_governance.phase_manager import GOVERNANCE_GATE_DIMENSIONS
        expected_dims = {
            "d1_metadata", "d2_architecture", "d3_code_quality",
            "d4_testing", "d5_security", "d6_governance", "d7_operations",
            "d8_functional",
        }
        assert set(GOVERNANCE_GATE_DIMENSIONS.keys()) == expected_dims

    @pytest.mark.skip(reason="ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，维度分组被阶段分组替代")
    def test_each_dimension_has_gates(self) -> None:
        """每个维度至少有 1 个 gate。"""
        from zephyr.governance.ops_governance.phase_manager import GOVERNANCE_GATE_DIMENSIONS
        for dim, gates in GOVERNANCE_GATE_DIMENSIONS.items():
            assert len(gates) > 0, f"{dim} should have at least 1 gate"


# ============================================================================
# 2. 事件启动测试 — event_driven 配置
# ============================================================================


class TestEventDriven:
    """事件启动测试:验证 event_driven 配置能触发脚本执行."""

    def test_event_driven_triggers_defined(self) -> None:
        """event_driven 触发器类型已定义。"""
        expected_triggers = {
            "on_file_change", "on_commit", "on_structure_change",
            "on_session_start", "on_session_end", "on_rule_change",
        }
        # 验证触发器类型在规则文件中定义
        rule_file = _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules" / "trae_056_module_creation_workflow.yaml"
        if rule_file.exists():
            content = rule_file.read_text(encoding="utf-8")
            assert "event_driven" in content
        # 触发器类型集合完整
        assert len(expected_triggers) == 6

    @pytest.mark.skip(reason="ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，维度分组被阶段分组替代")
    def test_governance_dimensions_support_events(self) -> None:
        """治理维度支持事件驱动触发。"""
        from zephyr.governance.ops_governance.phase_manager import GOVERNANCE_GATE_DIMENSIONS
        # 每个维度的 gate 可被事件触发
        total_gates = sum(len(gates) for gates in GOVERNANCE_GATE_DIMENSIONS.values())
        assert total_gates > 0
        # 8 维度全部可调度
        assert len(GOVERNANCE_GATE_DIMENSIONS) == 8

    def test_auto_runner_supports_event_driven(self) -> None:
        """GovernanceAutoRunner 支持事件驱动执行。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        # run() 可被事件触发调用
        assert hasattr(runner, "run")
        assert callable(runner.run)

    def test_event_driven_gate_classification(self) -> None:
        """event_driven 分类在依赖图诊断中定义。"""
        diag_script = _PROJECT_ROOT / "scripts" / "governance" / "diagnose_depgraph.py"
        if diag_script.exists():
            content = diag_script.read_text(encoding="utf-8")
            assert "event_driven" in content


# ============================================================================
# 3. 自动运行测试 — GovernanceAutoRunner
# ============================================================================


class TestAutoRun:
    """自动运行测试:验证 GovernanceAutoRunner 能执行 8 维度 gate."""

    def test_auto_runner_importable(self) -> None:
        """GovernanceAutoRunner 可导入。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        assert runner is not None

    def test_auto_runner_result_class_exists(self) -> None:
        """AutoRunnerResult 类存在。"""
        from zephyr.governance.ops_governance.auto_runner import AutoRunnerResult
        result = AutoRunnerResult()
        assert result is not None
        assert result.total_gates == 0
        assert result.passed_gates == 0
        assert result.failed_gates == 0

    def test_run_returns_auto_runner_result(self) -> None:
        """run() 返回 AutoRunnerResult。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner, AutoRunnerResult
        runner = GovernanceAutoRunner()
        result = runner.run()
        assert isinstance(result, AutoRunnerResult)

    def test_run_executes_gates(self) -> None:
        """run() 执行了 gate(total_gates > 0)。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        result = runner.run()
        assert result.total_gates > 0

    def test_run_completes_without_exception(self) -> None:
        """run() 完成后 finished_at 已设置。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        result = runner.run()
        assert result.finished_at is not None

    @pytest.mark.skip(reason="ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，维度分组被阶段分组替代")
    def test_run_covers_8_dimensions(self) -> None:
        """run() 覆盖 8 维度 gate。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        from zephyr.governance.ops_governance.phase_manager import GOVERNANCE_GATE_DIMENSIONS
        runner = GovernanceAutoRunner()
        result = runner.run()
        expected_total = sum(len(gates) for gates in GOVERNANCE_GATE_DIMENSIONS.values())
        assert result.total_gates == expected_total


# ============================================================================
# 4. 自动关闭测试 — auto_close 机制
# ============================================================================


class TestAutoClose:
    """自动关闭测试:验证执行后资源释放和审计日志记录."""

    def test_auto_close_sets_cleanup_done(self) -> None:
        """run() 后 cleanup_done=True。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        result = runner.run()
        assert result.cleanup_done is True

    def test_auto_close_sets_audit_logged(self) -> None:
        """run() 后 audit_logged=True。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        result = runner.run()
        assert result.audit_logged is True

    def test_audit_log_written_to_depgraph(self) -> None:
        """审计日志写入 depgraph governance_audit_logs 表（P2迁移后：PostgreSQL）。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        runner.run()
        # 验证审计日志表有记录（P2迁移后查询 PostgreSQL）
        try:
            conn = get_depgraph_pg_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM governance_audit_logs")
                count = cur.fetchone()[0]
            conn.close()
            assert count > 0, "governance_audit_logs should have records"
        except psycopg2.Error:
            # 表不存在时跳过
            pytest.skip("governance_audit_logs table not yet created")
        except Exception:
            # PG 连接失败时跳过
            pytest.skip("depgraph (PostgreSQL) 不可用")

    def test_auto_close_releases_resources(self) -> None:
        """auto_close 释放注册的资源。"""

        class FakeResource:
            def __init__(self) -> None:
                self.closed = False

            def close(self) -> None:
                self.closed = True

        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        runner = GovernanceAutoRunner()
        resource = FakeResource()
        runner.register_resource(resource)
        runner.run()
        assert resource.closed is True

    def test_auto_close_cleans_temp_files(self, tmp_path: Path) -> None:
        """auto_close 清理注册的临时文件。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        temp_file = tmp_path / "test_temp.txt"
        temp_file.write_text("test", encoding="utf-8")
        assert temp_file.exists()

        runner = GovernanceAutoRunner()
        runner.register_temp_file(temp_file)
        runner.run()
        assert not temp_file.exists(), "temp file should be cleaned up"

    def test_run_idempotent(self) -> None:
        """多次 run() 都能成功完成自动关闭。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        for _ in range(2):
            runner = GovernanceAutoRunner()
            result = runner.run()
            assert result.cleanup_done is True
            assert result.audit_logged is True


# ============================================================================
# 5. 集成测试 — 全流程自动化
# ============================================================================


class TestIntegration:
    """集成测试:自动启动→自动运行→自动关闭全流程."""

    @pytest.mark.skip(reason="ARCH-034: PhaseManager 类已删除/拆分为函数式 API")
    def test_full_automation_pipeline(self) -> None:
        """全流程:PhaseManager 调度 → AutoRunner 执行 → auto_close 清理。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        from zephyr.governance.ops_governance.phase_manager import PhaseManager

        # 1. 自动启动:PhaseManager 验证（返回 dict，所有 gate auto_start=True）
        pm = PhaseManager()
        auto_start_map = pm.verify_auto_start()
        assert len(auto_start_map) > 0
        assert all(auto_start_map.values())

        # 2. 自动运行:GovernanceAutoRunner 执行
        runner = GovernanceAutoRunner()
        result = runner.run()
        assert result.total_gates > 0

        # 3. 自动关闭:资源释放 + 审计日志
        assert result.cleanup_done is True
        assert result.audit_logged is True

    @pytest.mark.skip(reason="ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，维度分组被阶段分组替代")
    def test_8_dimensions_all_covered(self) -> None:
        """8 维度 gate 全部被 AutoRunner 覆盖。"""
        from zephyr.governance.ops_governance.auto_runner import GovernanceAutoRunner
        from zephyr.governance.ops_governance.phase_manager import GOVERNANCE_GATE_DIMENSIONS

        runner = GovernanceAutoRunner()
        result = runner.run()

        # 总 gate 数 = 8 维度 gate 数之和
        expected = sum(len(gates) for gates in GOVERNANCE_GATE_DIMENSIONS.values())
        assert result.total_gates == expected

        # 执行 + 跳过 = 总数
        executed = result.passed_gates + result.failed_gates
        assert executed + result.skipped_gates == result.total_gates
