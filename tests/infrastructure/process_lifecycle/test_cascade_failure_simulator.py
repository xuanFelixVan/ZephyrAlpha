# [BLUEPRINT] MOD-INF-089 | docs/03_modules/_domain_infrastructure_operations/cascade_failure_simulator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-089 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_cascade_failure_simulator
# [TESTS] src/zephyr/infrastructure/rollback/cascade_failure_simulator.py
"""MOD-INF-089 单元测试：cascade_failure_simulator 级联失效仿真器。

蓝图验收（B14-04693/CAND-DR-002，A9运维架构）：
进程崩溃/Redis中断/GPU失效组合场景脚本化 + run 编排经注入 injector 回调执行
（不真杀进程）+ 失效传播有向事件链记录 + 恢复时间测量（注入时钟）+ 安全护栏
三件套（交易时段拒绝/备份确认前置/30min 超时终止）。回调全注入内存替身。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.rollback.cascade_failure_simulator",
    reason="cascade_failure_simulator not importable",
)

from zephyr.infrastructure.rollback.cascade_failure_simulator import (  # noqa: E402
    CascadeFailureSimulator,
    CascadeSimError,
    FailureKind,
    FailureScenario,
    RunStatus,
    SimStep,
)

_T0 = datetime.datetime(2026, 8, 25, 21, 0, 0)


class _Clock:
    """可变注入时钟（确定性推进）。"""

    def __init__(self, t: datetime.datetime) -> None:
        self._t = t

    def __call__(self) -> datetime.datetime:
        return self._t

    def advance(self, **kw) -> None:
        self._t += datetime.timedelta(**kw)


def _scenario(scenario_id: str = "sc-1") -> FailureScenario:
    return FailureScenario(
        scenario_id=scenario_id,
        steps=(
            SimStep("s1", FailureKind.PROCESS_CRASH, "signal_engine"),
            SimStep("s2", FailureKind.REDIS_OUTAGE, "redis_main"),
            SimStep("s3", FailureKind.GPU_FAILURE, "gpu0"),
        ),
    )


def _sim(injected: list | None = None, clock=None, **kw) -> CascadeFailureSimulator:
    return CascadeFailureSimulator(
        injector=(lambda s: injected.append(s)) if injected is not None else (lambda s: None),
        clock=clock or _Clock(_T0),
        **kw,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 场景校验
# ──────────────────────────────────────────────────────────────────────────────


class TestScenarioValidation:
    def test_empty_scenario_id_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim().run(FailureScenario("", (SimStep("s1", FailureKind.GPU_FAILURE, "gpu0"),)))

    def test_empty_steps_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim().run(FailureScenario("sc-1", ()))

    def test_duplicate_step_id_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim().run(
                FailureScenario(
                    "sc-1",
                    (
                        SimStep("s1", FailureKind.GPU_FAILURE, "gpu0"),
                        SimStep("s1", FailureKind.REDIS_OUTAGE, "redis"),
                    ),
                )
            )

    def test_empty_step_id_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim().run(FailureScenario("sc-1", (SimStep("", FailureKind.GPU_FAILURE, "gpu0"),)))

    def test_invalid_kind_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim().run(FailureScenario("sc-1", (SimStep("s1", "gpu_failure", "gpu0"),)))

    def test_empty_target_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim().run(FailureScenario("sc-1", (SimStep("s1", FailureKind.GPU_FAILURE, ""),)))


# ──────────────────────────────────────────────────────────────────────────────
# 安全护栏三件套
# ──────────────────────────────────────────────────────────────────────────────


class TestGuardrails:
    def test_trading_hours_refused(self) -> None:
        injected: list = []
        sim = _sim(injected, is_trading_hours=lambda: True)
        with pytest.raises(CascadeSimError):
            sim.run(_scenario())
        assert injected == []  # 未执行任何注入

    def test_backup_not_confirmed_refused(self) -> None:
        injected: list = []
        sim = _sim(injected, backup_confirmed=lambda: False)
        with pytest.raises(CascadeSimError):
            sim.run(_scenario())
        assert injected == []

    def test_injector_none_construction_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            CascadeFailureSimulator(injector=None, clock=_Clock(_T0))

    def test_timeout_invalid_raises(self) -> None:
        with pytest.raises(CascadeSimError):
            _sim(timeout_minutes=0)
        with pytest.raises(CascadeSimError):
            _sim(timeout_minutes=-5)


# ──────────────────────────────────────────────────────────────────────────────
# 编排运行（事件链 / 传播路径 / 恢复时间）
# ──────────────────────────────────────────────────────────────────────────────


class TestRun:
    def test_run_happy_path(self) -> None:
        injected: list = []
        result = _sim(injected).run(_scenario())
        assert result.status is RunStatus.COMPLETED
        assert [s.step_id for s in injected] == ["s1", "s2", "s3"]  # 逐步经回调执行
        assert result.scenario_id == "sc-1"

    def test_events_chain(self) -> None:
        result = _sim().run(_scenario())
        assert len(result.events) == 3
        assert [e.seq for e in result.events] == [0, 1, 2]
        assert result.events[0].kind is FailureKind.PROCESS_CRASH
        assert result.events[0].target == "signal_engine"
        assert all(e.ts == _T0 for e in result.events)

    def test_propagation_path(self) -> None:
        result = _sim().run(_scenario())
        assert result.propagation_path == (
            ("signal_engine", "redis_main"),
            ("redis_main", "gpu0"),
        )  # 失效传播有向边链

    def test_recovery_ms_measured(self) -> None:
        clock = _Clock(_T0)
        injected: list = []

        def _inject(step) -> None:
            injected.append(step)
            clock.advance(milliseconds=250)  # 注入时钟推进模拟恢复耗时

        sim = CascadeFailureSimulator(injector=_inject, clock=clock)
        result = sim.run(_scenario())
        assert result.recovery_ms == pytest.approx(750.0)  # 3 步 × 250ms
        assert result.started_at == _T0
        assert result.finished_at == _T0 + datetime.timedelta(milliseconds=750)

    def test_history_accumulates(self) -> None:
        sim = _sim()
        sim.run(_scenario("sc-1"))
        sim.run(_scenario("sc-2"))
        assert [r.scenario_id for r in sim.history()] == ["sc-1", "sc-2"]

    def test_determinism(self) -> None:
        r1 = _sim(clock=_Clock(_T0)).run(_scenario())
        r2 = _sim(clock=_Clock(_T0)).run(_scenario())
        assert r1.events == r2.events
        assert r1.propagation_path == r2.propagation_path
        assert r1.recovery_ms == r2.recovery_ms

    def test_timeout_aborts(self) -> None:
        clock = _Clock(_T0)
        injected: list = []

        def _inject(step) -> None:
            injected.append(step)
            clock.advance(minutes=31)  # 注入后时钟跳过 30min 超时线

        sim = CascadeFailureSimulator(injector=_inject, clock=clock, timeout_minutes=30)
        result = sim.run(_scenario())
        assert result.status is RunStatus.ABORTED_TIMEOUT
        assert [s.step_id for s in injected] == ["s1"]  # 剩余步骤未执行
        assert len(result.events) == 1

    def test_injector_exception_fail_closed(self) -> None:
        def _bad(step) -> None:
            raise RuntimeError("注入原语故障")

        sim = CascadeFailureSimulator(injector=_bad, clock=_Clock(_T0))
        with pytest.raises(CascadeSimError):
            sim.run(_scenario())
        assert sim.history() == ()  # 失败运行不留结果
