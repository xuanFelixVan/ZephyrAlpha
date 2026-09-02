# [BLUEPRINT] MOD-AU-004 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/16_ai_security_ops.md | §4.4-P2-3
# [MODULE] tests.autonomy_core.test_killswitch_response_levels
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/autonomy_core/test_killswitch_response_levels.py -q
# [TTL] permanent
"""test_killswitch_response_levels.py — KILLSWITCH 三级响应策略层（MOD-AU-004）单元测试.

覆盖 16号文 §4.4 P2-3 验收口径：
①三级各注入探针事件验证触发链——level_1 P1(high)→自治降级(IM 模式=auto_guard,
读/查询放行写操作人审)+技能熔断；level_2 P0(critical)→系统级单 Agent 阻断；
level_3 global_critical→系统级全局熔断+交易级联动（含传播未覆盖时的显式兜底）。
②level_3 触发后收敛状态一致（check_consistency，无「只停次要回路」）。
③复位需 Owner 批准（15号文不变量）：approver 为空三级全拒，状态零改变。
④KILLSWITCH.md 独立文件渲染/落盘 + 变更记录写审计链（§3.13）。
⑤响应/复位动作留痕（16号文 §4.2 P0-1 统一事件 schema）；动作面永不抛异常。

被测对象：src/zephyr/autonomy_core/killswitch_response_levels.py
MOD-AU-002 编排器源文件零改动——经其公开 API 消费（合成开关注入）。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.autonomy_core.kill_switch_orchestrator import KillSwitchOrchestrator
from zephyr.autonomy_core.killswitch_response_levels import (
    TARGET_MODE_IM,
    KillSwitchResponseLayer,
    ResponseIncident,
    ResponseLevel,
    render_killswitch_md,
)


class _SyntheticSwitch:
    """合成开关：内存态 trip/reset/is_tripped，用于探针事件仿真."""

    def __init__(self, name: str, supports_global: bool = True) -> None:
        self.name = name
        self.supports_global_trip = supports_global
        self.tripped: set[str] = set()
        self.trip_calls: list[tuple[str, str]] = []

    def trip(self, scope: str, reason: str) -> None:
        self.trip_calls.append((scope, reason))
        self.tripped.add(scope or "*")

    def reset(self, scope: str) -> None:
        self.tripped.discard(scope or "*")

    def is_tripped(self, scope: str) -> bool:
        if scope == "":
            return bool(self.tripped)
        return "*" in self.tripped or scope in self.tripped


class _SyntheticSystemSwitch:
    """合成系统级总开关：单 Agent 阻断粒度（对齐 MOD-INF-018 manual_trip_agent 面）."""

    def __init__(self) -> None:
        self.blocked_agents: set[str] = set()

    def manual_trip_agent(self, agent_id: str) -> None:
        self.blocked_agents.add(agent_id)

    def owner_release_agent(self, agent_id: str) -> None:
        self.blocked_agents.discard(agent_id)

    def is_agent_blocked(self, agent_id: str) -> bool:
        return agent_id in self.blocked_agents


class _RecordingDowngrader:
    """合成自治降级钩子：记录 (agent_id, target_mode, reason) 调用."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def __call__(self, agent_id: str, target_mode: str, reason: str) -> None:
        self.calls.append((agent_id, target_mode, reason))


@pytest.fixture
def switches():
    return {
        "system": _SyntheticSwitch("system"),
        "skills": _SyntheticSwitch("skills", supports_global=False),
        "trading": _SyntheticSwitch("trading"),
        "capacity": _SyntheticSwitch("capacity"),
    }


@pytest.fixture
def orchestrator(tmp_path, switches):
    orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
    orch.register_system(switches["system"])
    orch.register_domain("skills", switches["skills"])
    orch.register_domain("trading", switches["trading"])
    orch.register_domain("capacity", switches["capacity"])
    yield orch
    orch.close()


@pytest.fixture
def system_switch():
    return _SyntheticSystemSwitch()


@pytest.fixture
def downgrader():
    return _RecordingDowngrader()


@pytest.fixture
def layer(tmp_path, orchestrator, system_switch, downgrader):
    return KillSwitchResponseLayer(
        orchestrator=orchestrator,
        runtime_dir=tmp_path,
        system_switch=system_switch,
        downgrader=downgrader,
    )


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestLevel1Response:
    """level_1 P1(high) 探针：自治降级(IM 模式)+技能熔断."""

    def test_level1_trips_skills_and_downgrades_to_im(self, layer, switches, downgrader):
        incident = ResponseIncident(
            severity="P1",
            agent_id="agent-1",
            reason="单 Agent 可疑调用链",
            skill_ids=("skill-x", "skill-y"),
        )
        result = layer.respond(incident)
        assert result.success is True
        assert result.level == ResponseLevel.LEVEL_1.value
        # 技能熔断：两个技能均经编排器域级拉闸
        assert tuple(scope for scope, _ in switches["skills"].trip_calls) == ("skill-x", "skill-y")
        # 自治降级：暂降 IM 模式（读/查询放行，写操作人审 = auto_guard）
        assert result.target_mode == TARGET_MODE_IM
        assert downgrader.calls == [("agent-1", TARGET_MODE_IM, "单 Agent 可疑调用链")]
        # 爆炸半径：系统级与交易级不动
        assert switches["system"].is_tripped("") is False
        assert switches["trading"].is_tripped("") is False

    def test_level1_severity_alias_high(self, layer):
        incident = ResponseIncident(severity="high", agent_id="agent-1", reason="r")
        result = layer.respond(incident)
        assert result.success is True
        assert result.level == ResponseLevel.LEVEL_1.value

    def test_level1_without_skills_still_downgrades(self, layer, switches, downgrader):
        incident = ResponseIncident(severity="P1", agent_id="agent-2", reason="r")
        result = layer.respond(incident)
        assert result.success is True
        assert switches["skills"].trip_calls == []
        assert downgrader.calls[0][1] == TARGET_MODE_IM


class TestLevel2Response:
    """level_2 P0(critical) 探针：系统级单 Agent 阻断."""

    def test_level2_blocks_single_agent_at_system_level(self, layer, switches, system_switch, downgrader):
        incident = ResponseIncident(severity="P0", agent_id="agent-9", reason="越权写生产库", skill_ids=("skill-z",))
        result = layer.respond(incident)
        assert result.success is True
        assert result.level == ResponseLevel.LEVEL_2.value
        # 系统级单 Agent 阻断：只停涉事 Agent，不全局熔断
        assert system_switch.is_agent_blocked("agent-9") is True
        assert system_switch.is_agent_blocked("agent-other") is False
        assert switches["system"].is_tripped("") is False
        assert switches["trading"].is_tripped("") is False
        # IM 模式基线叠加（术语统一 §3.13：level_2=IM 基线上叠加暂停涉事 Agent）
        assert result.target_mode == TARGET_MODE_IM
        assert downgrader.calls[0][1] == TARGET_MODE_IM

    def test_level2_severity_alias_critical(self, layer, system_switch):
        incident = ResponseIncident(severity="critical", agent_id="agent-9", reason="r")
        result = layer.respond(incident)
        assert result.success is True
        assert system_switch.is_agent_blocked("agent-9") is True


class TestLevel3Response:
    """level_3 global_critical 探针：系统级全局熔断+交易级联动+收敛一致."""

    def test_level3_global_trip_with_trading_linkage(self, layer, switches):
        incident = ResponseIncident(severity="global_critical", agent_id="agent-1", reason="全局失控演练")
        result = layer.respond(incident)
        assert result.success is True
        assert result.level == ResponseLevel.LEVEL_3.value
        # 系统级总开关 + 全域型域级一致生效
        assert switches["system"].is_tripped("") is True
        assert switches["trading"].is_tripped("") is True
        assert switches["capacity"].is_tripped("") is True
        # 交易级联动：trading 在最终生效集合内（无「只停次要回路」）
        assert "trading" in result.tripped
        # 收敛状态一致
        report = layer.consistency_report()
        assert report["consistent"] is True

    def test_level3_explicit_trading_linkage_when_propagation_skips(self, tmp_path, system_switch, downgrader):
        """交易开关为粒度型（不支持全域传播）时，策略层显式兜底拉交易级."""
        granular_trading = _SyntheticSwitch("trading", supports_global=False)
        orch = KillSwitchOrchestrator(runtime_dir=tmp_path, register_defaults=False)
        orch.register_system(_SyntheticSwitch("system"))
        orch.register_domain("trading", granular_trading)
        layer = KillSwitchResponseLayer(
            orchestrator=orch,
            runtime_dir=tmp_path,
            system_switch=system_switch,
            downgrader=downgrader,
        )
        incident = ResponseIncident(severity="global_critical", agent_id="agent-1", reason="全局失控演练")
        result = layer.respond(incident)
        orch.close()
        assert result.success is True
        assert granular_trading.is_tripped("") is True
        assert "trading" in result.tripped
        assert any(a.startswith("trading_link") for a in result.actions)


class TestResetInvariant:
    """复位需 Owner 批准（15号文不变量）：三级 approver 为空全拒且状态零改变."""

    def test_level1_reset_requires_owner(self, layer, switches):
        layer.respond(ResponseIncident(severity="P1", agent_id="a", reason="r", skill_ids=("s1",)))
        result = layer.reset_response(ResponseLevel.LEVEL_1, approver="", skill_ids=("s1",))
        assert result.success is False
        assert "approver" in result.errors
        assert switches["skills"].is_tripped("s1") is True  # 状态零改变

    def test_level2_reset_requires_owner(self, layer, system_switch):
        layer.respond(ResponseIncident(severity="P0", agent_id="a9", reason="r"))
        result = layer.reset_response(ResponseLevel.LEVEL_2, approver="", agent_id="a9")
        assert result.success is False
        assert system_switch.is_agent_blocked("a9") is True  # 状态零改变

    def test_level3_reset_requires_owner(self, layer, switches):
        layer.respond(ResponseIncident(severity="global_critical", agent_id="a", reason="r"))
        result = layer.reset_response(ResponseLevel.LEVEL_3, approver="")
        assert result.success is False
        assert switches["system"].is_tripped("") is True  # 状态零改变

    def test_level3_reset_with_owner_approval(self, layer, switches):
        layer.respond(ResponseIncident(severity="global_critical", agent_id="a", reason="r"))
        result = layer.reset_response(ResponseLevel.LEVEL_3, approver="Owner")
        assert result.success is True
        assert result.approver == "Owner"
        assert switches["system"].is_tripped("") is False
        assert switches["trading"].is_tripped("") is False

    def test_level2_reset_with_owner_approval(self, layer, system_switch):
        layer.respond(ResponseIncident(severity="P0", agent_id="a9", reason="r"))
        result = layer.reset_response(ResponseLevel.LEVEL_2, approver="Owner", agent_id="a9")
        assert result.success is True
        assert system_switch.is_agent_blocked("a9") is False


class TestAuditTrail:
    """动作留痕（16号文 §4.2 P0-1 统一事件 schema）+ KILLSWITCH.md 变更写审计链."""

    def test_respond_and_reset_write_audit_records(self, layer, tmp_path):
        layer.respond(ResponseIncident(severity="P1", agent_id="a", reason="r"))
        layer.reset_response(ResponseLevel.LEVEL_1, approver="Owner", agent_id="a")
        records = _read_jsonl(tmp_path / "audit" / "killswitch_response_levels.jsonl")
        assert len(records) == 2
        respond_rec, reset_rec = records
        assert respond_rec["event_type"] == "killswitch_response"
        assert respond_rec["source_domain"] == "access_control"
        assert respond_rec["level"] == "level_1"
        assert respond_rec["severity"] == "high"
        assert reset_rec["event_type"] == "killswitch_response_reset"
        assert reset_rec["approver"] == "Owner"

    def test_killswitch_md_change_writes_audit(self, layer, tmp_path):
        target = tmp_path / "KILLSWITCH.md"
        layer.write_killswitch_md(target, author="AI-K3-T4-H1")
        records = _read_jsonl(tmp_path / "audit" / "killswitch_response_levels.jsonl")
        assert len(records) == 1
        assert records[0]["event_type"] == "killswitch_md_change"
        assert records[0]["author"] == "AI-K3-T4-H1"
        assert records[0]["path"].endswith("KILLSWITCH.md")


class TestKillSwitchMd:
    """KILLSWITCH.md 独立文件（§3.13）：8 要素齐全+三级响应定义+复位不变量."""

    def test_render_contains_all_elements(self):
        content = render_killswitch_md()
        for key in (
            "cost_limit_usd",
            "error_rate_threshold",
            "consecutive_failures",
            "level_1_throttle",
            "level_2_pause",
            "level_3_shutdown",
        ):
            assert key in content
        assert "IM" in content  # 暂降 IM 模式术语
        assert "Owner" in content  # 复位需 Owner 批准

    def test_write_killswitch_md(self, layer, tmp_path):
        target = tmp_path / "KILLSWITCH.md"
        written = layer.write_killswitch_md(target, author="AI-K3-T4-H1")
        assert written == target
        assert target.read_text(encoding="utf-8") == render_killswitch_md()

    def test_write_requires_author(self, layer, tmp_path):
        with pytest.raises(ValueError, match="author"):
            layer.write_killswitch_md(tmp_path / "KILLSWITCH.md", author="")


class TestNeverRaise:
    """ERROR_CONTRACT：respond()/reset_response() 永不抛异常."""

    def test_unknown_severity_fails_closed(self, layer, switches):
        incident = ResponseIncident(severity="P9", agent_id="a", reason="r")
        result = layer.respond(incident)
        assert result.success is False
        assert result.errors
        assert switches["system"].is_tripped("") is False

    def test_orchestrator_failure_collected_not_raised(self, tmp_path):
        class _RaisingOrchestrator:
            def trip(self, *args, **kwargs):
                raise RuntimeError("编排器故障")

            def reset(self, *args, **kwargs):
                raise RuntimeError("编排器故障")

            def check_consistency(self):
                raise RuntimeError("编排器故障")

        layer = KillSwitchResponseLayer(
            orchestrator=_RaisingOrchestrator(),
            runtime_dir=tmp_path,
            system_switch=_SyntheticSystemSwitch(),
        )
        result = layer.respond(ResponseIncident(severity="P1", agent_id="a", reason="r", skill_ids=("s",)))
        assert result.success is False
        assert result.errors
