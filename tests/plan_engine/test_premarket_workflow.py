# [BLUEPRINT] MOD-PLAN-021 | docs/03_modules/_domain_plan_engine/premarket_workflow/blueprint.md | §test
# [MODULE] tests.plan_engine.test_premarket_workflow
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.premarket_workflow
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_premarket_workflow.py
# [A_test] module_id: MOD-PLAN-021 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-PLAN-021 单元测试: D-TRADING-15 A股盘前标准化工作流。

覆盖: 默认 SOP 三段式排程窗口/依赖拓扑/DAG 模型字段/进度状态机非法迁移拒绝/
mandatory 失败阻断与人工接管点/ready 口径/state_sink 回调容错/畸形输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.plan_engine.premarket_workflow import (
    PremarketWorkflowError,
    PremarketWorkflowTracker,
    StageSpec,
    StageStatus,
    build_premarket_dag,
    default_stages,
)
from zephyr.trading.work_dag import WorkDAG


class TestDefaultStages:
    def test_three_phases_cover_window(self) -> None:
        stages = default_stages()
        assert {s.phase for s in stages} == {1, 2, 3}
        for s in stages:
            assert "08:00" <= s.scheduled_at <= "09:15"
            assert "08:00" <= s.deadline <= "09:15"
            assert s.scheduled_at <= s.deadline

    def test_phase_order_monotonic(self) -> None:
        stages = default_stages()
        latest_end = {1: "08:30", 2: "09:00", 3: "09:15"}
        for s in stages:
            assert s.deadline <= latest_end[s.phase]

    def test_mandatory_core_stages_present(self) -> None:
        stages = {s.stage_id: s for s in default_stages()}
        assert stages["premarket_check"].mandatory is True
        assert stages["readiness_confirm"].mandatory is True
        assert stages["llm_premarket"].mandatory is False

    def test_dependencies_exist(self) -> None:
        stages = default_stages()
        ids = {s.stage_id for s in stages}
        for s in stages:
            assert set(s.depends_on) <= ids

    def test_premarket_check_depends_on_analysis(self) -> None:
        stages = {s.stage_id: s for s in default_stages()}
        assert "scenario_plan" in stages["premarket_check"].depends_on


class TestBuildDag:
    def test_dag_model_fields(self) -> None:
        dag = build_premarket_dag("2026-08-26")
        assert isinstance(dag, WorkDAG)
        assert "2026-08-26" in dag.dag_id
        node_ids = {n.node_id for n in dag.nodes}
        assert {"data_sync", "quality_gate", "premarket_check", "readiness_confirm"} <= node_ids
        edge_pairs = {(e.from_node, e.to_node) for e in dag.edges}
        assert ("data_sync", "quality_gate") in edge_pairs
        assert ("premarket_check", "readiness_confirm") in edge_pairs

    def test_stage_params_carry_schedule(self) -> None:
        dag = build_premarket_dag("2026-08-26")
        by_id = {n.node_id: n for n in dag.nodes}
        assert by_id["premarket_check"].params["scheduled_at"] == "09:00"
        assert by_id["premarket_check"].params["mandatory"] is True

    def test_missing_mandatory_rejected(self) -> None:
        stages = tuple(s for s in default_stages() if s.stage_id != "premarket_check")
        with pytest.raises(PremarketWorkflowError):
            build_premarket_dag("2026-08-26", stages=stages)

    def test_bad_trading_date_rejected(self) -> None:
        with pytest.raises(PremarketWorkflowError):
            build_premarket_dag("2026/08/26")

    def test_unknown_dependency_rejected(self) -> None:
        bad = StageSpec(
            stage_id="x",
            name="x",
            phase=1,
            scheduled_at="08:05",
            deadline="08:10",
            capability_id="cap.x",
            mandatory=False,
            depends_on=("ghost",),
        )
        with pytest.raises(PremarketWorkflowError):
            build_premarket_dag("2026-08-26", stages=default_stages() + (bad,))


class TestTracker:
    def _tracker(self) -> PremarketWorkflowTracker:
        return PremarketWorkflowTracker(trading_date="2026-08-26", stages=default_stages())

    def test_happy_path_ready(self) -> None:
        t = self._tracker()
        for s in default_stages():
            t.mark_running(s.stage_id)
            t.mark_done(s.stage_id)
        assert t.ready is True
        assert t.blocked is False
        snap = t.progress()
        assert snap["done"] == len(default_stages())
        assert snap["ready"] is True

    def test_optional_failure_not_blocking(self) -> None:
        t = self._tracker()
        for s in default_stages():
            if s.stage_id == "llm_premarket":
                t.mark_running(s.stage_id)
                t.mark_failed(s.stage_id, reason="llm timeout")
            else:
                t.mark_running(s.stage_id)
                t.mark_done(s.stage_id)
        assert t.blocked is False
        assert t.ready is True

    def test_mandatory_failure_blocks_with_takeover(self) -> None:
        t = self._tracker()
        t.mark_running("data_sync")
        t.mark_failed("data_sync", reason="feed down")
        assert t.blocked is True
        assert t.takeover_point == "data_sync"
        assert t.ready is False

    def test_illegal_transitions_rejected(self) -> None:
        t = self._tracker()
        with pytest.raises(PremarketWorkflowError):
            t.mark_done("data_sync")  # 未 RUNNING 不得 DONE
        t.mark_running("data_sync")
        with pytest.raises(PremarketWorkflowError):
            t.mark_running("data_sync")  # 重复 RUNNING

    def test_unknown_stage_rejected(self) -> None:
        t = self._tracker()
        with pytest.raises(PremarketWorkflowError):
            t.mark_running("ghost")

    def test_skip_only_optional(self) -> None:
        t = self._tracker()
        with pytest.raises(PremarketWorkflowError):
            t.mark_skipped("data_sync")  # mandatory 不可跳过
        t.mark_skipped("llm_premarket", reason="disabled")
        assert t.progress()["by_stage"]["llm_premarket"] == StageStatus.SKIPPED.value

    def test_state_sink_callback_and_fault_tolerance(self) -> None:
        seen: list[dict] = []
        t = PremarketWorkflowTracker(
            trading_date="2026-08-26", stages=default_stages(), state_sink=seen.append
        )
        t.mark_running("data_sync")
        assert seen and seen[-1]["trading_date"] == "2026-08-26"

        def _boom(_snap: dict) -> None:
            raise RuntimeError("store down")

        t2 = PremarketWorkflowTracker(
            trading_date="2026-08-26", stages=default_stages(), state_sink=_boom
        )
        t2.mark_running("data_sync")  # sink 异常不阻断
        assert t2.progress()["by_stage"]["data_sync"] == StageStatus.RUNNING.value
