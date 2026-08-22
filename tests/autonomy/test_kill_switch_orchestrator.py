"""tests/autonomy/test_kill_switch_orchestrator.py — KillSwitchOrchestrator（MOD-AU-002）单元测试.

覆盖 15号文（15_autonomy_boundary_risk.md）§4.1 S0.3 验收口径：
①三类事故仿真（合成开关：系统级拉闸 / 域级拉闸 / 编排器故障）各拉对开关
②系统级 TRIPPED 时域级开关状态一致性检查通过（含静默未生效检出）
③复位须 Owner 批准（approver 为空拒绝，既有不变量不破）
④编排器自身故障时各开关保持独立可用（编排器只编排不持有状态，fail-open 分散态）
⑤编排动作留痕（16号文 §4.2 P0-1 统一事件 schema）。

被测对象：src/zephyr/autonomy_core/kill_switch_orchestrator.py
既有 5 套 Kill Switch 本体零改动——真实接线冒烟仅经适配器调用其公开接口。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.autonomy_core.kill_switch_orchestrator import KillSwitchOrchestrator


class _SyntheticSwitch:
    """合成开关：内存态 trip/reset/is_tripped，用于事故仿真."""

    def __init__(self, name: str, supports_global: bool = True) -> None:
        self.name = name
        self.supports_global_trip = supports_global
        self.tripped: set[str] = set()
        self.trip_calls: list[tuple[str, str]] = []
        self.reset_calls: list[str] = []

    def trip(self, scope: str, reason: str) -> None:
        self.trip_calls.append((scope, reason))
        self.tripped.add(scope or "*")

    def reset(self, scope: str) -> None:
        self.reset_calls.append(scope)
        self.tripped.discard(scope or "*")

    def is_tripped(self, scope: str) -> bool:
        # 空 scope 查询 = "该开关有任何生效拉闸吗"（对齐真实适配器空目标语义）
        if scope == "":
            return bool(self.tripped)
        return "*" in self.tripped or scope in self.tripped


class _RaisingSwitch(_SyntheticSwitch):
    """故障开关：trip/reset 抛异常（模拟开关本体故障）."""

    def trip(self, scope: str, reason: str) -> None:
        raise RuntimeError(f"{self.name} 硬件故障")

    def reset(self, scope: str) -> None:
        raise RuntimeError(f"{self.name} 硬件故障")


class _SilentSwitch(_SyntheticSwitch):
    """静默开关：trip 不抛异常但也不生效（模拟传播被吞）."""

    def trip(self, scope: str, reason: str) -> None:
        self.trip_calls.append((scope, reason))  # 不写入 tripped


@pytest.fixture
def switches():
    return {
        "system": _SyntheticSwitch("system"),
        "alpha": _SyntheticSwitch("alpha"),
        "beta": _SyntheticSwitch("beta"),
        "granular": _SyntheticSwitch("granular", supports_global=False),
    }


@pytest.fixture
def orchestrator(tmp_path, switches):
    orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
    orch.register_system(switches["system"])
    orch.register_domain("alpha", switches["alpha"])
    orch.register_domain("beta", switches["beta"])
    orch.register_domain("granular", switches["granular"])
    yield orch
    orch.close()


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestAccidentSimulation:
    """三类事故仿真（S0.3 验收①）：各拉对开关."""

    def test_global_accident_trips_system_and_propagates(self, orchestrator, switches):
        """事故一·系统级拉闸：全局事故只拉系统级，域级一致生效（传播+跳过粒度型）."""
        result = orchestrator.trip("system", "global", "全局事故演练")
        assert result.success is True
        assert set(result.tripped) == {"system", "alpha", "beta"}
        assert result.skipped == ("granular",)  # 粒度型开关不支持全域拉闸
        assert switches["system"].is_tripped("") is True
        assert switches["alpha"].is_tripped("") is True
        assert switches["beta"].is_tripped("") is True
        assert switches["granular"].is_tripped("") is False

    def test_domain_accident_trips_only_that_domain(self, orchestrator, switches):
        """事故二·域级拉闸：域内故障域级先行，系统级与其他域保持正常."""
        result = orchestrator.trip("domain", "alpha:skill-9", "域内故障演练")
        assert result.success is True
        assert result.tripped == ("alpha",)
        assert switches["alpha"].is_tripped("skill-9") is True
        assert switches["system"].is_tripped("") is False
        assert switches["beta"].is_tripped("") is False
        assert orchestrator.is_tripped("domain", "alpha:skill-9") is True
        assert orchestrator.is_tripped("system") is False

    def test_orchestrator_failure_leaves_switches_independent(
        self, tmp_path, switches, orchestrator
    ):
        """事故三·编排器故障：各开关独立可用（fail-open 分散态，编排器不持态）."""
        # (a) 状态分散在开关本体：另一编排器实例看到同一状态
        orchestrator.trip("domain", "alpha:x", "先拉一次")
        second = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        second.register_system(switches["system"])
        second.register_domain("alpha", switches["alpha"])
        assert second.is_tripped("domain", "alpha:x") is True
        second.close()
        # (b) 编排器故障/销毁后，开关本体直接操作不受影响
        broken = _RaisingSwitch("broken")
        orchestrator.register_domain("broken", broken)
        result = orchestrator.trip("domain", "broken:y", "故障开关")
        assert result.success is False
        assert "broken" in result.errors
        # 其余开关照常可用
        ok = orchestrator.trip("domain", "beta:z", "其余开关不受影响")
        assert ok.success is True
        switches["alpha"].trip("direct", "旁路直接拉闸")  # 无编排器直驱
        assert switches["alpha"].is_tripped("direct") is True

    def test_system_trip_with_raising_domain_still_trips_system(self, tmp_path, switches):
        """系统级拉闸时某域传播失败：系统级与其余域仍生效，失败入 errors."""
        orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        orch.register_system(switches["system"])
        orch.register_domain("alpha", switches["alpha"])
        orch.register_domain("bad", _RaisingSwitch("bad"))
        try:
            result = orch.trip("system", "global", "传播失败演练")
            assert result.success is False
            assert "bad" in result.errors
            assert switches["system"].is_tripped("") is True
            assert switches["alpha"].is_tripped("") is True
        finally:
            orch.close()


class TestConsistency:
    """系统级 TRIPPED 时域级一致性检查（S0.3 验收②）."""

    def test_consistency_passes_after_system_trip(self, orchestrator):
        orchestrator.trip("system", "global", "一致性演练")
        report = orchestrator.check_consistency()
        assert report["system_tripped"] is True
        assert report["consistent"] is True
        assert report["domains"]["alpha"]["own_tripped"] is True
        assert report["domains"]["granular"]["supports_global_trip"] is False

    def test_consistency_detects_silent_propagation_failure(self, tmp_path, switches):
        """静默吞传播的域级开关（trip 无异常但未生效）被一致性检查检出."""
        orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        orch.register_system(switches["system"])
        orch.register_domain("silent", _SilentSwitch("silent"))
        try:
            result = orch.trip("system", "global", "静默失败演练")
            assert result.success is True  # 无异常，编排面成功
            report = orch.check_consistency()
            assert report["consistent"] is False  # 物理状态未一致生效，被检出
        finally:
            orch.close()

    def test_consistency_passes_when_normal(self, orchestrator):
        assert orchestrator.check_consistency()["consistent"] is True


class TestResetApproval:
    """复位审批（S0.3 验收③：复位仍需 Owner 批准，既有不变量不破）."""

    def test_reset_requires_approver(self, orchestrator, switches):
        orchestrator.trip("system", "global", "复位审批演练")
        for bad_approver in ("", "   ", None):
            result = orchestrator.reset("system", "global", bad_approver)
            assert result.success is False
            assert "approver" in result.errors
            assert switches["system"].is_tripped("") is True  # 未复位

    def test_system_reset_with_approver_resets_domains(self, orchestrator, switches):
        orchestrator.trip("system", "global", "复位演练")
        result = orchestrator.reset("system", "global", "Owner")
        assert result.success is True
        assert "system" in result.tripped
        assert switches["system"].is_tripped("") is False
        assert switches["alpha"].is_tripped("") is False
        assert switches["beta"].is_tripped("") is False
        assert orchestrator.check_consistency()["consistent"] is True

    def test_domain_reset_blocked_while_system_tripped(self, orchestrator, switches):
        """系统级 TRIPPED 时域级一致生效：域级不可单独复位."""
        orchestrator.trip("system", "global", "域级复位阻断演练")
        result = orchestrator.reset("domain", "alpha:x", "Owner")
        assert result.success is False
        assert "state" in result.errors
        assert switches["alpha"].is_tripped("") is True

    def test_domain_reset_with_approver_when_system_normal(self, orchestrator, switches):
        orchestrator.trip("domain", "alpha:x", "域级复位演练")
        result = orchestrator.reset("domain", "alpha:x", "Owner")
        assert result.success is True
        assert switches["alpha"].is_tripped("x") is False


class TestRouteIncident:
    """收敛规则路由（§3.4）：资金→交易级先行/系统级兜底；代码库→系统级；全局→只拉系统级."""

    def test_route_funds_to_trading_first(self, tmp_path, switches):
        orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        orch.register_system(switches["system"])
        orch.register_domain("trading", switches["alpha"])
        try:
            result = orch.route_incident("funds", "日亏超限", "DAILY_LOSS")
            assert result.success is True
            assert switches["alpha"].is_tripped("DAILY_LOSS") is True
            assert switches["system"].is_tripped("") is False  # 系统级未动
        finally:
            orch.close()

    def test_route_funds_fallback_to_system_when_trading_fails(self, tmp_path, switches):
        orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        orch.register_system(switches["system"])
        orch.register_domain("trading", _RaisingSwitch("trading"))
        try:
            result = orch.route_incident("funds", "日亏超限")
            assert switches["system"].is_tripped("") is True  # 系统级兜底
            assert "trading_first_attempt" in result.errors
        finally:
            orch.close()

    def test_route_codebase_to_system(self, orchestrator, switches):
        result = orchestrator.route_incident("codebase", "工作区越权写入")
        assert result.success is True
        assert switches["system"].is_tripped("") is True

    def test_route_global_only_system(self, orchestrator, switches):
        result = orchestrator.route_incident("global", "全局事故")
        assert result.success is True
        assert set(result.tripped) == {"system", "alpha", "beta"}
        assert result.skipped == ("granular",)

    def test_route_unknown_kind_fails_closed(self, orchestrator):
        result = orchestrator.route_incident("unknown_kind", "x")
        assert result.success is False
        assert "incident_kind" in result.errors


class TestTrace:
    """编排动作留痕（16号文 §4.2 P0-1 统一事件 schema）."""

    def test_trip_and_reset_traced(self, orchestrator, tmp_path):
        orchestrator.trip("system", "global", "留痕演练")
        orchestrator.reset("system", "global", "Owner")
        records = _read_jsonl(tmp_path / "audit" / "kill_switch_orchestrator.jsonl")
        assert len(records) == 2
        trip_record, reset_record = records
        for record in records:
            assert record["schema_version"] == "1.0"
            assert record["source_domain"] == "access_control"
            assert record["event_type"] == "kill_switch_orchestration"
            assert record["event_id"]
            assert record["timestamp"]
        assert trip_record["action"] == "trip"
        assert trip_record["severity"] == "critical"
        assert "system" in trip_record["evidence"]["tripped"]
        assert reset_record["action"] == "reset"
        assert reset_record["approver"] == "Owner"


class TestRealSwitchWiring:
    """真实接线冒烟：适配器只调用既有开关公开接口，本体零改动."""

    def test_default_registration_and_system_trip(self, tmp_path):
        from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch
        from zephyr.security.access_control.kill_switch import KillSwitch
        from zephyr.trading.trading_contracts.risk import trading_kill_switch

        SkillKillSwitch.clear_all()
        orch = KillSwitchOrchestrator(
            runtime_dir=tmp_path, system_switch=KillSwitch(), project_root=tmp_path
        )
        try:
            result = orch.trip("system", "global", "真实接线冒烟")
            assert result.success is True
            assert set(result.skipped) == {"rollback", "skills"}  # token-gated / 粒度型跳过
            assert orch.is_tripped("system") is True
            assert orch.is_tripped("domain", "trading:") is True
            assert orch.check_consistency()["consistent"] is True
            reset = orch.reset("system", "global", "Owner")
            assert reset.success is True
            assert orch.is_tripped("system") is False
            assert trading_kill_switch.active_switches() == []
        finally:
            orch.close()
            SkillKillSwitch.clear_all()
            for level in trading_kill_switch.KillSwitchLevel:
                trading_kill_switch.reset(level)

    def test_real_skill_domain_trip_and_reset(self, tmp_path):
        from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch

        SkillKillSwitch.clear_all()
        orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        orch.register_domain("skills", _make_skill_adapter())
        try:
            result = orch.trip("domain", "skills:smoke-skill", "技能异常")
            assert result.success is True
            assert SkillKillSwitch.is_killed("smoke-skill") is True
            reset = orch.reset("domain", "skills:smoke-skill", "Owner")
            assert reset.success is True
            assert SkillKillSwitch.is_killed("smoke-skill") is False
        finally:
            orch.close()
            SkillKillSwitch.clear_all()


def _make_skill_adapter():
    """经编排器私有适配器包装真实 SkillKillSwitch（验证适配器与真实接口对齐）."""
    from zephyr.autonomy_core.kill_switch_orchestrator import _SkillSwitchAdapter
    from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch

    return _SkillSwitchAdapter(SkillKillSwitch)
