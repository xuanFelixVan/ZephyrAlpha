# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §3 复考周期（§3.1 窗口与逾期 / §3.2 双通道禁 sleep-loop）
# [MODULE] tests.governance.meta_question.test_exam_loop_scheduler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] conftest 夹具 env/mq/claimed; zephyr.governance.meta_question.exam_loop.reexam_scheduler（窗册加载+到期判定+对账落账）
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 红腿：①词表漂移（窗册缺档/多档）必 fail-closed 抛错，禁静默按"不逾期"出结论；
#                ②跨自然月未考必判逾期并落 reexam 到期账（分母不记账=执行率无从复考）；
#                ③终态（merged/retired）不得进台账（13§4.3 第 3 条）；
#              蓝腿：窗内不产欠账、同日重跑幂等不冲刷账、事件驱动/静态档逾期不适用、执行率分母为零报 None 不按 100% 假绿
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红
# [TESTS] self
# [TTL] task_bound
"""复考调度测试（新鲜窗到期/逾期台账，PQ-0054/0057/0108 载体）。"""

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.governance.meta_question.exam_loop import reexam_scheduler
from zephyr.governance.meta_question.exam_loop.reexam_scheduler import (
    ReexamScheduler,
    due_state,
    load_window_rules,
)

# 同文 SQL 逐处独立常量：对拍尺按多重集计数，共用常量会使字面量 2→1 判 RED
SQL_SET_LAST_EXAM_BY_QID = "UPDATE main.meta_question SET last_exam=? WHERE q_id=?"
SQL_SET_LAST_EXAM_EPOCH_BY_QID = "UPDATE main.meta_question SET last_exam=? WHERE q_id=?"


class TestWindowRules:
    def test_rules_cover_frequency_vocabulary(self, mq: SimpleNamespace) -> None:
        rules = load_window_rules()
        from zephyr.shared.io.yaml_utils import load_vocabulary_values

        vocab = load_vocabulary_values("meta_question_frequencies_vocabulary.yaml")
        assert set(rules) == set(vocab), "窗册档集必须与频度词表全等（缺档=该频度永不复考）"

    def test_drift_fails_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """红腿①：窗册与词表不等（少一档）必须抛，禁静默把该档当"不逾期"。"""
        real = reexam_scheduler.load_vocabulary_values

        def _drifted(name: str, **kw: Any) -> set[str]:
            values = set(real(name, **kw))
            return values - {"quarterly"} if "frequencies" in str(name) else values

        monkeypatch.setattr(reexam_scheduler, "load_vocabulary_values", _drifted)
        with pytest.raises(ValueError):
            load_window_rules()

    def test_unknown_frequency_rejected(self) -> None:
        with pytest.raises(ValueError):
            due_state("hourly", None)


class TestDueState:
    def test_static_and_event_driven_are_not_applicable(self) -> None:
        for freq in ("static", "event_driven", "realtime"):
            state = due_state(freq, None, today=date(2026, 9, 24))
            assert state["applicable"] is False and state["overdue"] is False

    def test_never_examined_is_overdue(self) -> None:
        state = due_state("weekly", None, today=date(2026, 9, 24))
        assert (state["due"], state["overdue"]) == (True, True)

    def test_within_window_not_due(self) -> None:
        state = due_state("weekly", "2026-09-22T00:00:00+00:00", today=date(2026, 9, 24))
        assert state["due"] is False and state["overdue"] is False

    def test_monthly_rolling_20_day_fresh_window(self) -> None:
        """PQ-0108：月度档新鲜窗=20 日，窗内未跨月不算到期，跨月即逾期。"""
        inside = due_state("monthly", "2026-09-10T00:00:00+00:00", today=date(2026, 9, 24))
        assert inside["due"] is False and inside["overdue"] is False
        crossed = due_state("monthly", "2026-08-10T00:00:00+00:00", today=date(2026, 9, 24))
        assert crossed["overdue"] is True and crossed["fresh_window_days"] == 20
        beyond = due_state("monthly", "2026-09-01T00:00:00+00:00", today=date(2026, 9, 24))
        assert beyond["due"] is True and beyond["overdue"] is True  # 23 日 > 20 日新鲜窗

    def test_naive_timestamp_rejected(self) -> None:
        with pytest.raises(ValueError):
            due_state("daily", "2026-09-20T00:00:00")


class TestReconcile:
    def test_overdue_lands_ledger_and_is_idempotent(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿②+蓝腿：逾期必落 reexam 到期账；同日重跑不冲刷（幂等）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)  # → answered + last_exam=now
        stale = (mq.now_utc() - timedelta(days=90)).isoformat()
        env["raw"].execute(SQL_SET_LAST_EXAM_BY_QID, (stale, q_id))
        env["raw"].commit()
        sched = ReexamScheduler(env["registry"], ledger=env["ledger"])
        report = sched.reconcile(actor=mq.SESSION)
        assert report["overdue_count"] >= 1 and any(r["q_id"] == q_id for r in report["overdue"])
        events = [r for r in mq.audit_rows(env, q_id) if r["what"] == "reexam"]
        assert len(events) == 1 and events[0]["after"]["overdue"] is True
        again = sched.reconcile(actor=mq.SESSION)
        assert again["booked"] == 0, "同日重跑必须幂等（日切事件重复触发不冲刷账）"
        assert len([r for r in mq.audit_rows(env, q_id) if r["what"] == "reexam"]) == 1

    def test_terminal_states_excluded_from_ledger(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿③：退役/合并问不进复考台账（13§4.3）。"""
        registry = env["registry"]
        q_id = registry.register(mq.question(title="退役问台账排除"), actor=mq.SESSION)
        registry.transition(q_id, "retired", actor="Owner", evidence="零消费退役批")
        env["raw"].execute(SQL_SET_LAST_EXAM_EPOCH_BY_QID, ("2020-01-01 00:00:00+00:00", q_id))
        env["raw"].commit()
        sched = ReexamScheduler(registry, ledger=env["ledger"])
        assert q_id not in {r["q_id"] for r in sched.candidates()}
        assert q_id not in {r["q_id"] for r in sched.reconcile()["overdue"]}

    def test_fresh_exam_not_overdue(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """蓝腿对照：刚回填过的周频问不得被判逾期（否则台账全是假红）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)
        sched = ReexamScheduler(env["registry"], ledger=env["ledger"])
        report = sched.reconcile(actor=mq.SESSION, book=False)
        assert q_id not in {r["q_id"] for r in report["overdue"]}

    def test_execution_rate_none_when_no_denominator(self, env: dict[str, Any]) -> None:
        """分母为零必报 None（禁把"无到期"混报成"执行率 100%"）。"""
        assert reexam_scheduler._execution_rate(0, 0) is None
        assert reexam_scheduler._execution_rate(10, 2) == 80.0
