# [BLUEPRINT] MOD-PLAN-023 | docs/03_modules/_domain_plan_engine/premarket_workflow_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-PLAN-023 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.plan_engine.test_premarket_workflow_engine
# [TESTS] src/zephyr/plan_engine/premarket_workflow_engine.py
"""MOD-PLAN-023 单元测试：premarket_workflow_engine 盘前标准化工作流引擎。

蓝图验收（B14-04681/CAND-PLAN-017，A9 D-TRADING-15）：
数据同步→隔夜复盘→情绪扫描→预案生成→盘前检查→就绪确认六工序编排
（handler注入）+ 失败阻断（后续跳过）+ 人工接管点（暂停等确认）+ 耗时统计。
handler/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import dataclasses
import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.plan_engine.premarket_workflow_engine",
    reason="premarket_workflow_engine not importable",
)

from zephyr.plan_engine.premarket_workflow_engine import (  # noqa: E402
    PremarketWorkflowEngine,
    PremarketWorkflowError,
    StepStatus,
    WorkflowStepId,
)

_T0 = datetime.datetime(2026, 8, 26, 8, 0, 0)
_ORDER = tuple(WorkflowStepId)


class _StepClock:
    """步进时钟（每调用+60秒，供耗时统计断言）。"""

    def __init__(self, step_seconds: int = 60) -> None:
        self._t = _T0
        self._step = datetime.timedelta(seconds=step_seconds)

    def __call__(self) -> datetime.datetime:
        t = self._t
        self._t += self._step
        return t


def _make_handler(step: WorkflowStepId, fail: bool):
    if fail:
        def _handler(_ctx) -> str:
            raise RuntimeError(f"{step.value} boom")
        return _handler
    return lambda _ctx, _s=step: f"{_s.value} ok"


def _handlers(fail_at: WorkflowStepId | None = None) -> dict:
    return {step: _make_handler(step, step == fail_at) for step in _ORDER}


def _engine(clock=None, fail_at: WorkflowStepId | None = None, **kwargs) -> PremarketWorkflowEngine:
    kwargs.setdefault("handlers", _handlers(fail_at))
    kwargs.setdefault("clock", clock or (lambda: _T0))
    return PremarketWorkflowEngine(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 初始化
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_default_ok(self) -> None:
        assert _engine() is not None

    def test_missing_handler_raises(self) -> None:
        handlers = _handlers()
        del handlers[WorkflowStepId.SENTIMENT_SCAN]
        with pytest.raises(PremarketWorkflowError):
            _engine(handlers=handlers)

    def test_extra_handler_key_raises(self) -> None:
        handlers = dict(_handlers())
        handlers["ghost_step"] = lambda ctx: None
        with pytest.raises(PremarketWorkflowError):
            _engine(handlers=handlers)

    def test_non_callable_handler_raises(self) -> None:
        handlers = dict(_handlers())
        handlers[WorkflowStepId.DATA_SYNC] = "not-a-handler"
        with pytest.raises(PremarketWorkflowError):
            _engine(handlers=handlers)

    def test_unknown_manual_step_raises(self) -> None:
        with pytest.raises(PremarketWorkflowError):
            _engine(manual_steps={"ghost_step"})


# ──────────────────────────────────────────────────────────────────────────────
# 六工序编排
# ──────────────────────────────────────────────────────────────────────────────


class TestRun:
    def test_full_auto_all_done(self) -> None:
        report = _engine(manual_steps=()).run("2026-08-26")
        assert report.ready is True
        assert report.blocked_step is None
        assert report.waiting_step is None
        assert all(r.status is StepStatus.DONE for r in report.steps)
        assert report.finished_at is not None

    def test_step_order_deterministic(self) -> None:
        report = _engine(manual_steps=()).run("2026-08-26")
        assert [r.step_id for r in report.steps] == list(_ORDER)
        assert [r.detail for r in report.steps] == [f"{s.value} ok" for s in _ORDER]

    def test_default_manual_waits_at_readiness(self) -> None:
        report = _engine().run("2026-08-26")  # 默认人工接管点=就绪确认
        assert report.ready is False
        assert report.waiting_step is WorkflowStepId.READINESS_CONFIRM
        done = [r for r in report.steps if r.status is StepStatus.DONE]
        assert len(done) == 5
        waiting = report.steps[-1]
        assert waiting.status is StepStatus.WAITING_MANUAL
        assert waiting.started_at is not None
        assert waiting.finished_at is None

    def test_confirm_approved_ready(self) -> None:
        engine = _engine()
        engine.run("2026-08-26")
        report = engine.confirm_manual(True)
        assert report.ready is True
        assert all(r.status is StepStatus.DONE for r in report.steps)
        assert report.steps[-1].detail == "人工确认通过"

    def test_confirm_rejected_blocked(self) -> None:
        engine = _engine()
        engine.run("2026-08-26")
        report = engine.confirm_manual(False)
        assert report.ready is False
        assert report.blocked_step is WorkflowStepId.READINESS_CONFIRM
        assert report.steps[-1].status is StepStatus.FAILED

    def test_failure_blocks_rest(self) -> None:
        report = _engine(fail_at=WorkflowStepId.SENTIMENT_SCAN).run("2026-08-26")
        assert report.ready is False
        assert report.blocked_step is WorkflowStepId.SENTIMENT_SCAN
        statuses = {r.step_id: r.status for r in report.steps}
        assert statuses[WorkflowStepId.DATA_SYNC] is StepStatus.DONE
        assert statuses[WorkflowStepId.OVERNIGHT_REVIEW] is StepStatus.DONE
        assert statuses[WorkflowStepId.SENTIMENT_SCAN] is StepStatus.FAILED
        assert statuses[WorkflowStepId.PLAN_GENERATION] is StepStatus.SKIPPED
        assert statuses[WorkflowStepId.PREMARKET_CHECK] is StepStatus.SKIPPED
        assert statuses[WorkflowStepId.READINESS_CONFIRM] is StepStatus.SKIPPED

    def test_failure_detail_recorded(self) -> None:
        report = _engine(fail_at=WorkflowStepId.DATA_SYNC).run("2026-08-26")
        failed = report.steps[0]
        assert failed.status is StepStatus.FAILED
        assert "RuntimeError" in failed.detail
        assert "data_sync boom" in failed.detail


# ──────────────────────────────────────────────────────────────────────────────
# 人工接管点
# ──────────────────────────────────────────────────────────────────────────────


class TestManualTakeover:
    def test_confirm_without_waiting_raises(self) -> None:
        engine = _engine(manual_steps=())
        engine.run("2026-08-26")
        with pytest.raises(PremarketWorkflowError):
            engine.confirm_manual(True)

    def test_run_while_waiting_raises(self) -> None:
        engine = _engine()
        engine.run("2026-08-26")  # 停在就绪确认
        with pytest.raises(PremarketWorkflowError):
            engine.run("2026-08-27")

    def test_rerun_after_finish_allowed(self) -> None:
        engine = _engine(manual_steps=())
        engine.run("2026-08-26")
        report = engine.run("2026-08-27")  # 已完结可重跑
        assert report.trading_date == "2026-08-27"
        assert report.ready is True

    def test_custom_manual_mid_pipeline(self) -> None:
        engine = _engine(manual_steps={WorkflowStepId.SENTIMENT_SCAN})
        report = engine.run("2026-08-26")
        assert report.waiting_step is WorkflowStepId.SENTIMENT_SCAN
        statuses = {r.step_id: r.status for r in report.steps}
        assert statuses[WorkflowStepId.DATA_SYNC] is StepStatus.DONE
        assert statuses[WorkflowStepId.PLAN_GENERATION] is StepStatus.PENDING
        report2 = engine.confirm_manual(True)
        assert report2.ready is True

    def test_two_manual_steps_pause_twice(self) -> None:
        engine = _engine(manual_steps={WorkflowStepId.OVERNIGHT_REVIEW, WorkflowStepId.READINESS_CONFIRM})
        engine.run("2026-08-26")
        r1 = engine.confirm_manual(True)  # 第一接管点通过 → 停在就绪确认
        assert r1.waiting_step is WorkflowStepId.READINESS_CONFIRM
        r2 = engine.confirm_manual(True)
        assert r2.ready is True

    def test_non_bool_approved_raises(self) -> None:
        engine = _engine()
        engine.run("2026-08-26")
        with pytest.raises(PremarketWorkflowError):
            engine.confirm_manual("yes")


# ──────────────────────────────────────────────────────────────────────────────
# 耗时统计 / 产出流转
# ──────────────────────────────────────────────────────────────────────────────


class TestDurationAndContext:
    def test_step_durations_from_clock(self) -> None:
        report = _engine(clock=_StepClock(60), manual_steps=()).run("2026-08-26")
        assert all(r.duration_seconds == Decimal("60.0") for r in report.steps)
        assert report.total_duration_seconds == Decimal("360.0")

    def test_manual_wait_duration_counted(self) -> None:
        engine = _engine(clock=_StepClock(60))
        engine.run("2026-08-26")  # 5工序×2次 + 启动 + 等待点进入
        report = engine.confirm_manual(True)  # 就绪确认等待耗时=60
        last = report.steps[-1]
        assert last.duration_seconds == Decimal("60.0")

    def test_outputs_flow_downstream(self) -> None:
        seen: dict = {}

        def _plan_handler(ctx) -> str:
            seen.update(ctx.step_outputs)
            return "plan ok"

        handlers = _handlers()
        handlers[WorkflowStepId.PLAN_GENERATION] = _plan_handler
        _engine(handlers=handlers, manual_steps=()).run("2026-08-26")
        assert seen[WorkflowStepId.DATA_SYNC] == "data_sync ok"
        assert seen[WorkflowStepId.SENTIMENT_SCAN] == "sentiment_scan ok"
        assert WorkflowStepId.PLAN_GENERATION not in seen  # 本工序尚未产出

    def test_empty_trading_date_raises(self) -> None:
        with pytest.raises(PremarketWorkflowError):
            _engine().run("")

    def test_started_at_and_frozen(self) -> None:
        report = _engine(manual_steps=()).run("2026-08-26")
        assert report.started_at == _T0
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.ready = False


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        r1 = _engine(manual_steps=()).run("2026-08-26")
        r2 = _engine(manual_steps=()).run("2026-08-26")
        assert r1 == r2
