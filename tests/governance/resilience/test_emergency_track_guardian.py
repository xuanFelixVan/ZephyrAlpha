# [A_test] module_id: MOD-GOV_emergency_track_guardian | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §tests
# [MODULE] tests.governance.resilience.test_emergency_track_guardian
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.emergency_track_guardian
# [CONSUMERS] pytest
# [STARTUP] n/a
# [MATURITY] testing
# [INVARIANTS] 判据缺证据不得动作（unknown≠stale）; 保命动作唯一入口=route_incident;
#   配置读不懂=失能且出声，绝不静默降级为缺省值; 测试禁写生产路径（全 tmp_path）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] self
# [TESTS] self
# [TTL] permanent
"""test_emergency_track_guardian — 应急保命轨最小实体（BRK-078/004/005）+ 熔断入口唯一性（BRK-066 附带）.

钉的是三件真缺陷：
1. `emergency` 决策轨有登记有优先级但零节点 → 判据必须能判、动作必须能下；
2. last_resort 旗标只写不读（静默兜底）→ 现在必须有读方；
3. 熔断入口不唯一 → 生产代码不得绕过编排器直接 manual_trip_*。

**这些断言不是恒真的**：把 guardian 的 `all_confirmed_dead` 改成 `stale>0`、或把
`unknown` 也计入失效，本文件立刻红（变异证据见交付报告）。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from zephyr.governance.resilience_governance.emergency_track_guardian import (
    STATE_ARMING,
    STATE_ACTIVATED,
    STATE_DISABLED,
    STATE_INSUFFICIENT,
    STATE_NORMAL,
    STATE_OUTSIDE_WINDOW,
    EmergencyTrackConfig,
    EmergencyTrackGuardian,
    TrackLeg,
    load_emergency_track_config,
)

_LEG_SPECS = (("signal", "tmp/sig.heartbeat", 600), ("strategy", "tmp/stg.heartbeat", 600),
              ("model", "tmp/mdl.heartbeat", 600))


class _FakeOrchestrator:
    """替身编排器——只记录下单，不碰任何真开关。"""

    def __init__(self, *, fail: bool = False) -> None:
        self.calls: list[tuple[str, str]] = []
        self._fail = fail

    def route_incident(self, incident_kind: str, reason: str = "", target: str = "") -> object:
        self.calls.append((incident_kind, reason))
        if self._fail:
            raise RuntimeError("编排器故障")
        return type(
            "R", (), {"success": True, "level": "system", "tripped": ["system:global"],
                      "skipped": [], "errors": {}}
        )()


class _FakeWatchdog:
    def __init__(self, active: bool) -> None:
        self.active = active


def _repo(tmp_path: Path, ages: dict[str, float | None], base_ts: float | None = None) -> Path:
    """按 leg_id → 文件年龄（秒；None=不建文件即 unknown）铺心跳。

    base_ts：以该时刻为"现在"铺文件（注入固定 now_fn 的窗口测试必须与墙钟解耦）。
    """
    root = tmp_path / "repo"
    (root / "tmp").mkdir(parents=True, exist_ok=True)
    now = base_ts if base_ts is not None else time.time()
    for leg_id, rel, _max in _LEG_SPECS:
        age = ages.get(leg_id, "missing")
        if age is None or age == "missing":
            continue
        target = root / rel
        target.write_text("hb", encoding="utf-8")
        os.utime(target, (now - age, now - age))
    return root


def _cfg(**over: object) -> EmergencyTrackConfig:
    base = dict(
        legs=tuple(TrackLeg(i, p, m) for i, p, m in _LEG_SPECS),
        consecutive_confirmations=2,
        audit_path=".runtime/audit/emergency_track.jsonl",
        window_enabled=False,  # 行为测试与墙钟解耦（窗口本身另有专测）
    )
    base.update(over)
    return EmergencyTrackConfig(**base)  # type: ignore[arg-type]


def _guardian(root: Path, orch: _FakeOrchestrator | None = None, *, active: bool = False,
              cfg: EmergencyTrackConfig | None = None) -> EmergencyTrackGuardian:
    return EmergencyTrackGuardian(
        config=cfg or _cfg(),
        repo_root=root,
        orchestrator_provider=lambda: orch or _FakeOrchestrator(),
        last_resort_provider=lambda: _FakeWatchdog(active),
    )


def test_all_legs_stale_arms_then_trips_once(tmp_path: Path) -> None:
    """三腿全过期：第一次只 arming，第二次才下单（防抖），且动作走唯一入口."""
    root = _repo(tmp_path, {"signal": 7200.0, "strategy": 7200.0, "model": 7200.0})
    orch = _FakeOrchestrator()
    guardian = _guardian(root, orch)
    first = guardian.evaluate(dry_run=True)
    assert first.state == STATE_ARMING
    assert first.stale_count == 3 and first.unknown_count == 0
    assert orch.calls == []
    second = guardian.evaluate(dry_run=True)
    assert second.state == STATE_ACTIVATED
    assert [c[0] for c in orch.calls] == ["global"], "确认满额即经 route_incident 下单"
    assert second.action["entry"] == "kill_switch_orchestrator.route_incident"
    assert second.action["executed"] is True


def test_fresh_leg_never_trips(tmp_path: Path) -> None:
    """任一条腿仍活着 → 不构成"所有模型/策略/信号失效"，绝不拉闸."""
    root = _repo(tmp_path, {"signal": 1.0, "strategy": 7200.0, "model": 7200.0})
    orch = _FakeOrchestrator()
    guardian = _guardian(root, orch)
    for _ in range(5):
        verdict = guardian.evaluate(dry_run=True)
    assert verdict.state == STATE_NORMAL
    assert orch.calls == [] and verdict.confirmations == 0


def test_missing_heartbeat_is_unknown_not_dead(tmp_path: Path) -> None:
    """心跳文件缺失=未启动≠已失效：必须判证据不足，绝不因夜间空档误熔断."""
    root = _repo(tmp_path, {"signal": 7200.0, "strategy": 7200.0, "model": None})
    orch = _FakeOrchestrator()
    verdict = _guardian(root, orch).evaluate(dry_run=True)
    assert verdict.unknown_count == 1 and verdict.stale_count == 2
    assert verdict.state == STATE_INSUFFICIENT
    assert orch.calls == []
    assert any(b.startswith("leg_unknown:") for b in verdict.breaches), "缺证据本身要出声"


def test_last_resort_flag_is_consumed(tmp_path: Path) -> None:
    """BRK-005 消费端：终极逃生舱旗标点亮时计入一条失效腿（不再只写不读）."""
    root = _repo(tmp_path, {"signal": 7200.0, "strategy": 7200.0, "model": 1.0})
    orch = _FakeOrchestrator()
    guardian = _guardian(root, orch, active=True)
    verdict = guardian.evaluate(dry_run=True)
    assert verdict.last_resort_active is True
    assert verdict.stale_count == 3, "两腿过期 + 旗标 = 三腿齐"
    assert verdict.state == STATE_ARMING
    assert verdict.confirmations == 1


def test_trip_failure_is_loud_not_silent(tmp_path: Path) -> None:
    """⑥失败会响：编排器抛异常 → action.failed + errors + breach，不外炸也不静默."""
    root = _repo(tmp_path, {"signal": 7200.0, "strategy": 7200.0, "model": 7200.0})
    orch = _FakeOrchestrator(fail=True)
    guardian = _guardian(root, orch, cfg=_cfg(consecutive_confirmations=1))
    verdict = guardian.evaluate(dry_run=True)
    assert verdict.state == STATE_ACTIVATED
    assert verdict.action["failed"] is True
    assert "action" in verdict.errors
    assert "killswitch_trip_failed" in verdict.breaches


def test_audit_lands_on_disk(tmp_path: Path) -> None:
    """③出口有货：评估必落 JSONL（dry_run 不落，禁污染生产审计面）."""
    root = _repo(tmp_path, {"signal": 1.0, "strategy": 1.0, "model": 1.0})
    guardian = _guardian(root)
    guardian.evaluate(dry_run=True)
    audit = root / _cfg().audit_path
    assert not audit.exists(), "dry-run 不得留痕"
    guardian.evaluate(dry_run=False)
    lines = audit.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["source"] == "emergency_track" and record["state"] == STATE_NORMAL
    assert len(record["legs"]) == 3


def test_unreadable_config_disables_and_shouts(tmp_path: Path) -> None:
    """配置含未知键 → 保命轨失能（绝不用缺省值蒙混）且每次评估出声."""
    cfg_path = tmp_path / "emergency_track.yaml"
    cfg_path.write_text("enabled: true\nlegsx: []\n", encoding="utf-8")
    guardian = EmergencyTrackGuardian(
        config_path=cfg_path,
        repo_root=tmp_path,
        orchestrator_provider=lambda: pytest.fail("失能态不得下单"),
        last_resort_provider=lambda: _FakeWatchdog(False),
    )
    assert guardian.config_error
    verdict = guardian.evaluate()
    assert verdict.state == STATE_DISABLED
    assert "config" in verdict.errors
    assert "emergency_track_config_unreadable" in verdict.breaches


def test_config_unknown_key_is_hard_error(tmp_path: Path) -> None:
    from zephyr.governance.resilience_governance.emergency_track_guardian import (
        EmergencyTrackConfigError,
    )

    path = tmp_path / "bad.yaml"
    path.write_text("consecutive_confirmations: 0\n", encoding="utf-8")
    with pytest.raises(EmergencyTrackConfigError):
        load_emergency_track_config(path, repo_root=tmp_path)


def test_production_config_and_default_leg_paths_exist_in_repo() -> None:
    """钉住"默认判据腿指向真实存在的文件"——路径打错=判据永 unknown=假闸."""
    cfg = load_emergency_track_config()
    assert cfg.enabled is True
    assert len(cfg.legs) >= 3
    repo = Path(__file__).resolve().parents[3]
    for leg in cfg.legs:
        assert (repo / leg.path).parent.exists(), f"腿 {leg.leg_id} 目录不存在: {leg.path}"


def test_outside_active_window_judges_but_never_trips(tmp_path: Path) -> None:
    """盘后三腿集体"过期"是干净收市的常态——窗口闸门必须压住动作，同时留痕出声."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    night = datetime(2026, 9, 18, 22, 5, tzinfo=ZoneInfo("Asia/Shanghai"))
    root = _repo(tmp_path, {"signal": 7200.0, "strategy": 7200.0, "model": 7200.0},
                 base_ts=night.timestamp())
    orch = _FakeOrchestrator()
    guardian = EmergencyTrackGuardian(
        config=_cfg(window_enabled=True, consecutive_confirmations=1),
        repo_root=root,
        now_fn=lambda: night,
        orchestrator_provider=lambda: orch,
        last_resort_provider=lambda: _FakeWatchdog(False),
    )
    verdict = guardian.evaluate(dry_run=True)
    assert verdict.state == STATE_OUTSIDE_WINDOW
    assert orch.calls == [] and verdict.action.get("suppressed") is True
    assert "trip_suppressed_outside_active_window" in verdict.breaches


def test_in_window_trips(tmp_path: Path) -> None:
    """同一份 stale 证据，落在盘内就必须真下单（窗口闸不是永久哑闸）."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    noon = datetime(2026, 9, 18, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    root = _repo(tmp_path, {"signal": 7200.0, "strategy": 7200.0, "model": 7200.0},
                 base_ts=noon.timestamp())
    orch = _FakeOrchestrator()
    guardian = EmergencyTrackGuardian(
        config=_cfg(window_enabled=True, consecutive_confirmations=1),
        repo_root=root,
        now_fn=lambda: noon,
        orchestrator_provider=lambda: orch,
        last_resort_provider=lambda: _FakeWatchdog(False),
    )
    verdict = guardian.evaluate(dry_run=True)
    assert verdict.state == STATE_ACTIVATED and len(orch.calls) == 1


def test_ancient_heartbeat_is_absence_not_death(tmp_path: Path) -> None:
    """心跳老到超出证据视界（默认 4h）= 该系统今日未运行，绝不计入"失效"（防隔夜误熔断）."""
    ages = {leg[0]: 5.0 * 86400.0 for leg in _LEG_SPECS}
    root = _repo(tmp_path, ages)
    orch = _FakeOrchestrator()
    guardian = _guardian(root, orch, cfg=_cfg(consecutive_confirmations=1))
    for _ in range(3):
        verdict = guardian.evaluate(dry_run=True)
    assert verdict.stale_count == 0 and verdict.unknown_count == 3
    assert verdict.state == STATE_NORMAL and orch.calls == []
    assert sum(1 for b in verdict.breaches if b.startswith("leg_unknown:")) == 3


def test_killswitch_trip_entry_is_unique() -> None:
    """BRK-066/064 附带哨兵：生产代码不得绕过编排器/策略层直接 manual_trip_*."""
    src = Path(__file__).resolve().parents[3] / "src"
    allow = {
        "security/access_control/kill_switch.py",  # 开关本体（定义处）
        "autonomy_core/killswitch_response_levels.py",  # 策略层=唯一裁决者
    }
    offenders: list[str] = []
    for path in src.rglob("*.py"):
        rel = path.relative_to(src / "zephyr").as_posix()
        if rel in allow or "__pycache__" in rel:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "manual_trip_global(" in text or "manual_trip_agent(" in text:
            offenders.append(rel)
    assert offenders == [], f"绕过唯一 dispatcher 的拉闸点：{offenders}"
