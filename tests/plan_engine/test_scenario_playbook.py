# [BLUEPRINT] MOD-PLAN-019 | docs/03_modules/_domain_plan_engine/scenario_playbook/blueprint.md | §test
# [MODULE] tests.plan_engine.test_scenario_playbook
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.scenario_playbook
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_scenario_playbook.py
# [A_test] module_id: MOD-PLAN-019 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-PLAN-019 单元测试: C-005 多情景对策（预案模板库+盘中匹配+确认流）。

覆盖: 默认库 9 情景全覆盖、触发匹配与保守优先、确认流状态机非法迁移拒绝、
确认留痕 confirmed_by、复盘 Beta 平滑与 review_sink 回调、畸形输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.plan_engine.scenario_playbook import (
    HoldingAction,
    PlaybookConfirmation,
    PlaybookError,
    PlaybookLibrary,
    PlaybookStatus,
    PlaybookTemplate,
    OperationBoundary,
    default_library,
)


class TestDefaultLibrary:
    def test_covers_all_nine_scenarios(self) -> None:
        lib = default_library()
        assert set(lib.scenarios) == set(SCENARIO_LIST)

    def test_template_ids_unique(self) -> None:
        lib = default_library()
        ids = [t.template_id for t in lib.templates]
        assert len(ids) == len(set(ids))

    def test_boundary_invariants(self) -> None:
        for t in default_library().templates:
            assert 0.0 <= t.operation_boundary.max_add_position <= 1.0
            assert t.risk_escalation in (0, 1, 2)
            assert t.ttl_bars >= 1


class TestMatch:
    def test_standing_template_matches_without_trigger(self) -> None:
        lib = default_library()
        m = lib.match(
            market_state="ANY",
            active_scenario="HIGH_OPEN_WASH",
            events=(),
            bar_index=10,
        )
        assert m is not None
        assert m.template.scenario == "HIGH_OPEN_WASH"
        assert m.proposed_at_bar == 10

    def test_triggered_template_requires_state_and_event(self) -> None:
        lib = default_library()
        # HIGH_OPEN_REAL_UP 模板触发: state=TREND_UP + event=VOLUME_CONFIRM
        miss = lib.match(
            market_state="TREND_DOWN",
            active_scenario="HIGH_OPEN_REAL_UP",
            events=("VOLUME_CONFIRM",),
            bar_index=1,
        )
        hit = lib.match(
            market_state="TREND_UP",
            active_scenario="HIGH_OPEN_REAL_UP",
            events=("VOLUME_CONFIRM",),
            bar_index=1,
        )
        assert hit is not None
        assert hit.template.holding_action == HoldingAction.ADD
        if miss is not None:  # 若存在常配模板则不得是触发型 ADD
            assert miss.template.holding_action != HoldingAction.ADD or miss.matched_trigger == "standing"

    def test_conservative_priority_on_multi_hit(self) -> None:
        lib = PlaybookLibrary(
            templates=(
                PlaybookTemplate(
                    template_id="t_aggr",
                    scenario="HIGH_OPEN_REAL_UP",
                    operation_boundary=OperationBoundary(max_add_position=0.3),
                    holding_action=HoldingAction.ADD,
                    risk_escalation=0,
                    trigger_states=frozenset({"TREND_UP"}),
                    trigger_events=frozenset({"E1"}),
                    ttl_bars=5,
                ),
                PlaybookTemplate(
                    template_id="t_cons",
                    scenario="HIGH_OPEN_REAL_UP",
                    operation_boundary=OperationBoundary(max_add_position=0.0),
                    holding_action=HoldingAction.REDUCE,
                    risk_escalation=2,
                    trigger_states=frozenset({"TREND_UP"}),
                    trigger_events=frozenset({"E1"}),
                    ttl_bars=5,
                ),
            )
        )
        m = lib.match(
            market_state="TREND_UP",
            active_scenario="HIGH_OPEN_REAL_UP",
            events=("E1",),
            bar_index=0,
        )
        assert m is not None
        assert m.template.template_id == "t_cons"

    def test_unknown_scenario_rejected(self) -> None:
        lib = default_library()
        with pytest.raises(PlaybookError):
            lib.match(market_state="X", active_scenario="NO_SUCH", events=(), bar_index=0)


class TestConfirmationFlow:
    def _proposed(self):
        lib = default_library()
        m = lib.match(market_state="ANY", active_scenario="FLAT_OPEN_WASH", events=(), bar_index=0)
        assert m is not None
        return PlaybookConfirmation(match=m)

    def test_happy_path(self) -> None:
        c = self._proposed()
        assert c.status == PlaybookStatus.PROPOSED
        c.confirm(confirmed_by="owner", bar_index=1)
        assert c.status == PlaybookStatus.CONFIRMED
        assert c.confirmed_by == "owner"
        c.mark_executed(bar_index=2)
        assert c.status == PlaybookStatus.EXECUTED

    def test_confirm_requires_operator(self) -> None:
        c = self._proposed()
        with pytest.raises(PlaybookError):
            c.confirm(confirmed_by="", bar_index=1)

    def test_illegal_transitions_rejected(self) -> None:
        c = self._proposed()
        with pytest.raises(PlaybookError):
            c.mark_executed(bar_index=1)  # 未 CONFIRMED 不得执行
        c.reject(bar_index=1)
        with pytest.raises(PlaybookError):
            c.confirm(confirmed_by="owner", bar_index=2)  # 已 REJECTED

    def test_ttl_expire(self) -> None:
        lib = default_library()
        m = lib.match(market_state="ANY", active_scenario="FLAT_OPEN_WASH", events=(), bar_index=0)
        c = PlaybookConfirmation(match=m)
        expired = c.tick(bar_index=m.template.ttl_bars + 1)
        assert expired is True
        assert c.status == PlaybookStatus.EXPIRED
        with pytest.raises(PlaybookError):
            c.confirm(confirmed_by="owner", bar_index=m.template.ttl_bars + 2)


class TestSettle:
    def test_beta_smoothing_and_sink_payload(self) -> None:
        lib = default_library()
        tid = lib.templates[0].template_id
        seen: list[dict] = []
        lib.settle(tid, hit=True, review_sink=seen.append)
        lib.settle(tid, hit=False, review_sink=seen.append)
        assert len(seen) == 2
        payload = seen[-1]
        assert payload["template_id"] == tid
        assert payload["samples"] == 2
        # Beta(1,1) 先验: hit_rate = (1+1)/(2+2) = 0.5
        assert payload["hit_rate"] == pytest.approx(0.5)

    def test_sink_exception_not_raised(self) -> None:
        lib = default_library()
        tid = lib.templates[0].template_id

        def _boom(_payload: dict) -> None:
            raise RuntimeError("sink down")

        payload = lib.settle(tid, hit=True, review_sink=_boom)
        assert payload["samples"] == 1  # 统计照常更新

    def test_unknown_template_rejected(self) -> None:
        lib = default_library()
        with pytest.raises(PlaybookError):
            lib.settle("ghost", hit=True)
