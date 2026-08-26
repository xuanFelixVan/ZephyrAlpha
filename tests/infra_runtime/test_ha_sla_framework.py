# [BLUEPRINT] MOD-INF-076 | docs/03_modules/_domain_infrastructure_runtime/ha_sla_framework/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-076 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_ha_sla_framework
# [TESTS] src/zephyr/infra_runtime/ha_sla_framework.py
"""MOD-INF-076 单元测试：ha_sla_framework 高性能高可用保障框架。

蓝图验收（B10-02366/CAND-H1FS-009，A9运维架构）：
SLA 注册表（register_sla）+ 健康探针编排（register_probe 周期/超时）
+ 自动重启编排（注入 restart 回调，连续失败 N 次触发 + 冷却期抑制）
+ SLA 违约判定与升级链路。严格单机；时钟/restart/升级回调全注入内存替身。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.ha_sla_framework",
    reason="ha_sla_framework not importable",
)

from zephyr.infra_runtime.ha_sla_framework import (  # noqa: E402
    HaSlaError,
    HaSlaFramework,
    SlaReport,
)


class _FakeClock:
    """确定性单调时钟替身。"""

    def __init__(self, t0: float = 10_000.0) -> None:
        self.now = t0

    def __call__(self) -> float:
        return self.now

    def advance(self, dt: float) -> None:
        self.now += dt


def _framework(clock: _FakeClock | None = None, escalations: list | None = None) -> HaSlaFramework:
    return HaSlaFramework(
        clock=clock or _FakeClock(),
        escalation_sink=(lambda r: escalations.append(r)) if escalations is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注册校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_sla_ok(self) -> None:
        fw = _framework()
        sla = fw.register_sla("trading_core", 99.9, 300.0)
        assert sla.name == "trading_core"
        assert sla.target_pct == 99.9
        assert sla.window == 300.0

    def test_register_sla_invalid_raise(self) -> None:
        fw = _framework()
        with pytest.raises(HaSlaError):
            fw.register_sla("", 99.0, 60.0)
        with pytest.raises(HaSlaError):
            fw.register_sla("a", 0.0, 60.0)
        with pytest.raises(HaSlaError):
            fw.register_sla("a", 100.1, 60.0)
        with pytest.raises(HaSlaError):
            fw.register_sla("a", 99.0, 0.0)
        with pytest.raises(HaSlaError):
            fw.register_sla("a", 99.0, -5.0)

    def test_duplicate_registration_raises(self) -> None:
        fw = _framework()
        fw.register_sla("dup", 99.0, 60.0)
        with pytest.raises(HaSlaError):
            fw.register_sla("dup", 99.0, 60.0)
        fw.register_probe("dup_p", lambda: True, 1.0, 1.0)
        with pytest.raises(HaSlaError):
            fw.register_probe("dup_p", lambda: True, 1.0, 1.0)

    def test_register_probe_invalid_raise(self) -> None:
        fw = _framework()
        with pytest.raises(HaSlaError):
            fw.register_probe("", lambda: True, 1.0, 1.0)
        with pytest.raises(HaSlaError):
            fw.register_probe("p", None, 1.0, 1.0)  # type: ignore[arg-type]
        with pytest.raises(HaSlaError):
            fw.register_probe("p", lambda: True, 0.0, 1.0)
        with pytest.raises(HaSlaError):
            fw.register_probe("p", lambda: True, 1.0, -1.0)

    def test_bind_restart_validation(self) -> None:
        fw = _framework()
        with pytest.raises(HaSlaError):
            fw.bind_restart("ghost", lambda n: None, 3, 60.0)  # 未知探针
        fw.register_probe("p", lambda: True, 1.0, 1.0)
        with pytest.raises(HaSlaError):
            fw.bind_restart("p", lambda n: None, 0, 60.0)
        with pytest.raises(HaSlaError):
            fw.bind_restart("p", lambda n: None, 3, -1.0)
        with pytest.raises(HaSlaError):
            fw.bind_restart("p", None, 3, 60.0)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 探针编排（周期/超时/异常）
# ──────────────────────────────────────────────────────────────────────────────


class TestProbe:
    def test_run_probe_ok(self) -> None:
        clock = _FakeClock()
        fw = _framework(clock)
        fw.register_probe("p", lambda: True, 5.0, 2.0)
        result = fw.run_probe("p")
        assert result.ok is True
        assert result.timed_out is False
        assert result.at == clock.now

    def test_run_probe_unhealthy(self) -> None:
        fw = _framework()
        fw.register_probe("p", lambda: False, 5.0, 2.0)
        assert fw.run_probe("p").ok is False

    def test_run_probe_exception_counts_unhealthy(self) -> None:
        def _boom() -> bool:
            raise RuntimeError("probe crashed")

        fw = _framework()
        fw.register_probe("p", _boom, 5.0, 2.0)
        assert fw.run_probe("p").ok is False  # 异常按不健康计不抛

    def test_run_probe_timeout(self) -> None:
        clock = _FakeClock()

        def _slow() -> bool:
            clock.advance(3.0)  # 模拟耗时 3s > timeout=2s
            return True

        fw = _framework(clock)
        fw.register_probe("p", _slow, 5.0, 2.0)
        result = fw.run_probe("p")
        assert result.ok is False
        assert result.timed_out is True
        assert result.elapsed == 3.0

    def test_run_probe_unknown_raises(self) -> None:
        fw = _framework()
        with pytest.raises(HaSlaError):
            fw.run_probe("ghost")

    def test_due_probes_schedule(self) -> None:
        clock = _FakeClock()
        fw = _framework(clock)
        fw.register_probe("fast", lambda: True, 5.0, 1.0)
        fw.register_probe("slow", lambda: True, 60.0, 1.0)
        assert fw.due_probes() == ("fast", "slow")  # 未运行全部到期
        fw.run_probe("fast")
        assert fw.due_probes() == ("slow",)
        clock.advance(5.0)
        assert fw.due_probes() == ("fast", "slow")
        fw.run_probe("slow")
        clock.advance(5.0)
        assert fw.due_probes() == ("fast",)  # slow 周期 60s 未到期


# ──────────────────────────────────────────────────────────────────────────────
# 自动重启编排（阈值 + 冷却期）
# ──────────────────────────────────────────────────────────────────────────────


class TestRestart:
    def _flaky_fw(self, clock: _FakeClock, restarts: list[str], threshold: int = 3, cooldown: float = 60.0):
        fw = _framework(clock)
        fw.register_probe("svc", lambda: False, 1.0, 5.0)  # 恒不健康
        fw.bind_restart("svc", lambda n: restarts.append(n), threshold, cooldown)
        return fw

    def test_restart_after_threshold_failures(self) -> None:
        clock = _FakeClock()
        restarts: list[str] = []
        fw = self._flaky_fw(clock, restarts)
        fw.run_probe("svc")
        fw.run_probe("svc")
        assert restarts == []  # 未达阈值
        fw.run_probe("svc")  # 第 3 次连续失败
        assert restarts == ["svc"]
        events = fw.restart_events("svc")
        assert len(events) == 1
        assert events[0].invoked is True
        assert events[0].consecutive_failures == 3

    def test_restart_cooldown_suppressed(self) -> None:
        clock = _FakeClock()
        restarts: list[str] = []
        fw = self._flaky_fw(clock, restarts, threshold=2, cooldown=60.0)
        fw.run_probe("svc")
        fw.run_probe("svc")  # 触发重启
        assert restarts == ["svc"]
        clock.advance(10.0)  # 冷却期内
        fw.run_probe("svc")
        fw.run_probe("svc")  # 再次达阈值但被抑制
        assert restarts == ["svc"]
        events = fw.restart_events("svc")
        assert len(events) == 2
        assert events[1].invoked is False
        assert "冷却期" in events[1].detail

    def test_restart_after_cooldown(self) -> None:
        clock = _FakeClock()
        restarts: list[str] = []
        fw = self._flaky_fw(clock, restarts, threshold=2, cooldown=60.0)
        fw.run_probe("svc")
        fw.run_probe("svc")
        clock.advance(61.0)  # 过冷却期
        fw.run_probe("svc")
        fw.run_probe("svc")
        assert restarts == ["svc", "svc"]

    def test_success_resets_consecutive_failures(self) -> None:
        clock = _FakeClock()
        restarts: list[str] = []
        healthy = {"v": False}
        fw = _framework(clock)
        fw.register_probe("svc", lambda: healthy["v"], 1.0, 5.0)
        fw.bind_restart("svc", lambda n: restarts.append(n), 3, 60.0)
        fw.run_probe("svc")
        fw.run_probe("svc")
        healthy["v"] = True
        fw.run_probe("svc")  # 成功重置计数
        healthy["v"] = False
        fw.run_probe("svc")
        fw.run_probe("svc")
        assert restarts == []  # 重新计数未达阈值

    def test_restart_callback_exception_not_blocking(self) -> None:
        fw = _framework()
        fw.register_probe("svc", lambda: False, 1.0, 5.0)

        def _boom(name: str) -> None:
            raise RuntimeError("restart failed")

        fw.bind_restart("svc", _boom, 1, 60.0)
        fw.run_probe("svc")  # 回调异常不阻断
        events = fw.restart_events("svc")
        assert len(events) == 1
        assert events[0].invoked is True
        assert "异常" in events[0].detail


# ──────────────────────────────────────────────────────────────────────────────
# SLA 评估（窗口统计 + 违约升级）
# ──────────────────────────────────────────────────────────────────────────────


class TestSla:
    def _fw_with_probe(self, clock: _FakeClock, outcomes: list[bool]) -> HaSlaFramework:
        seq = {"i": 0}

        def _probe() -> bool:
            v = outcomes[seq["i"] % len(outcomes)]
            seq["i"] += 1
            return v

        fw = _framework(clock)
        fw.register_probe("svc", _probe, 1.0, 5.0)
        fw.register_sla("svc", 99.0, 100.0)
        return fw

    def test_sla_report_healthy(self) -> None:
        clock = _FakeClock()
        fw = self._fw_with_probe(clock, [True, True, True])
        for _ in range(3):
            fw.run_probe("svc")
        report = fw.sla_report("svc")
        assert report.actual_pct == 100.0
        assert report.breached is False
        assert report.total == 3
        assert report.healthy == 3

    def test_sla_report_breached_and_escalated(self) -> None:
        clock = _FakeClock()
        escalations: list[SlaReport] = []
        outcomes = iter([True, False, False])
        fw = HaSlaFramework(clock=clock, escalation_sink=lambda r: escalations.append(r))
        fw.register_probe("svc", lambda: next(outcomes), 1.0, 5.0)
        fw.register_sla("svc", 99.0, 100.0)
        for _ in range(3):
            fw.run_probe("svc")
        report = fw.evaluate_sla("svc")
        assert report.breached is True  # 33.3% < 99%
        assert len(escalations) == 1
        assert escalations[0].name == "svc"

    def test_sla_window_excludes_old_samples(self) -> None:
        clock = _FakeClock()
        fw = self._fw_with_probe(clock, [False])
        fw.run_probe("svc")  # t=10000 失败样本
        clock.advance(200.0)  # 移出 window=100s
        with pytest.raises(HaSlaError):
            fw.sla_report("svc")  # 窗口内无样本

    def test_sla_no_samples_raises(self) -> None:
        fw = _framework()
        fw.register_probe("svc", lambda: True, 1.0, 5.0)
        fw.register_sla("svc", 99.0, 100.0)
        with pytest.raises(HaSlaError):
            fw.sla_report("svc")

    def test_sla_unknown_or_unbound_raises(self) -> None:
        fw = _framework()
        with pytest.raises(HaSlaError):
            fw.sla_report("ghost")
        fw.register_sla("no_probe", 99.0, 100.0)
        with pytest.raises(HaSlaError):
            fw.sla_report("no_probe")  # 无同名探针

    def test_evaluate_sla_healthy_no_escalation(self) -> None:
        escalations: list[SlaReport] = []
        fw = HaSlaFramework(clock=_FakeClock(), escalation_sink=lambda r: escalations.append(r))
        fw.register_probe("svc", lambda: True, 1.0, 5.0)
        fw.register_sla("svc", 99.0, 100.0)
        fw.run_probe("svc")
        report = fw.evaluate_sla("svc")
        assert report.breached is False
        assert escalations == []


# ──────────────────────────────────────────────────────────────────────────────
# 查询与确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_probe_history_order(self) -> None:
        fw = _framework()
        outcomes = iter([True, False, True])
        fw.register_probe("svc", lambda: next(outcomes), 1.0, 5.0)
        fw.run_probe("svc")
        fw.run_probe("svc")
        fw.run_probe("svc")
        assert [r.ok for r in fw.probe_history("svc")] == [True, False, True]

    def test_history_unknown_probe_raises(self) -> None:
        fw = _framework()
        with pytest.raises(HaSlaError):
            fw.probe_history("ghost")
        with pytest.raises(HaSlaError):
            fw.restart_events("ghost")

    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            clock = _FakeClock(500.0)
            restarts: list[str] = []
            outcomes = iter([True, False, False, False, True])
            fw = HaSlaFramework(clock=clock)
            fw.register_probe("svc", lambda: next(outcomes), 1.0, 5.0)
            fw.bind_restart("svc", lambda n: restarts.append(n), 2, 30.0)
            fw.register_sla("svc", 50.0, 1000.0)
            for _ in range(5):
                fw.run_probe("svc")
            report = fw.sla_report("svc")
            return (
                tuple(r.ok for r in fw.probe_history("svc")),
                tuple(e.invoked for e in fw.restart_events("svc")),
                (report.actual_pct, report.breached, report.evaluated_at),
            )

        assert _run() == _run()
