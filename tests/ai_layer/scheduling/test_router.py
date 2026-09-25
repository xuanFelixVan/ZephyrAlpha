# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_router
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_router — C6 验收：R1-R3 三证据全枚举；骨架级必 owner_gate=true；自指命中必 Owner。"""

from __future__ import annotations

from typing import Any

from zephyr.ai_layer.scheduling.router import (
    TIER_MODULE,
    TIER_SKELETON,
    classify_risk,
    classify_scope,
    classify_selfref,
    route,
)

RISK_MAP = {"governance": "low", "trading_algo": "high"}
REGISTERED = ["src/zephyr/governance/foo.py", "src/zephyr/governance/bar.py"]


def _route(**over: Any) -> Any:
    kwargs = {
        "target_files": ["src/zephyr/governance/foo.py"],
        "registered_files": REGISTERED,
        "domain_id": "governance",
        "risk_tier_map": RISK_MAP,
    }
    kwargs.update(over)
    return route(**kwargs)


# ---------------------------------------------------------------------------
# R1 作用域
# ---------------------------------------------------------------------------

def test_r1_all_targets_registered_is_module_level() -> None:
    ok, why = classify_scope(["src/zephyr/governance/foo.py"], REGISTERED)
    assert ok and why == []


def test_r1_outside_registered_is_skeleton() -> None:
    ok, why = classify_scope(["src/zephyr/governance/new_knob.py"], REGISTERED)
    assert not ok and any("超出已登记范围" in w for w in why)


def test_r1_new_top_level_file_is_skeleton() -> None:
    ok, why = classify_scope(["src/zephyr/newtop.py"], ["src/zephyr/old/old.py"])
    assert not ok and any("新顶层文件" in w for w in why)


def test_r1_cross_domain_edge_is_skeleton() -> None:
    ok, why = classify_scope(
        ["src/zephyr/governance/foo.py"],
        REGISTERED,
        module_domain="governance",
        file_domains={"src/zephyr/governance/foo.py": "trading_algo"},
    )
    assert not ok and any("跨域新依赖边" in w for w in why)


def test_r1_empty_registered_is_skeleton_fail_closed() -> None:
    ok, why = classify_scope(["src/zephyr/governance/foo.py"], [])
    assert not ok and any("无登记图" in w for w in why)


# ---------------------------------------------------------------------------
# R2 风险
# ---------------------------------------------------------------------------

def test_r2_high_domain_is_skeleton() -> None:
    ok, why = classify_risk("trading_algo", RISK_MAP, ["src/zephyr/governance/foo.py"])
    assert not ok and any("high 九域" in w for w in why)


def test_r2_unlisted_domain_defaults_low() -> None:
    ok, why = classify_risk("tooling", RISK_MAP, ["src/zephyr/governance/foo.py"])
    assert ok and why == []  # 未列域默认 low（risk_tier_registry 口径）


def test_r2_constitution_touch_is_skeleton() -> None:
    ok, why = classify_risk("governance", RISK_MAP, ["AGENTS.md"])
    assert not ok and any("宪法" in w for w in why)


def test_r2_rule_yaml_touch_is_skeleton() -> None:
    ok, why = classify_risk("governance", RISK_MAP, ["docs/01_policies_and_standards/rules/trae_065.yaml"])
    assert not ok and any("规则权限语义" in w for w in why)


# ---------------------------------------------------------------------------
# R3 自指（定调 #9：先他指后自指，v1 自指一律 Owner）
# ---------------------------------------------------------------------------

def test_r3_ai_layer_selfref_is_skeleton() -> None:
    ok, why = classify_selfref(["src/zephyr/ai_layer/scheduling/dispatcher.py"])
    assert not ok and any("自指" in w for w in why)


def test_r3_gate_system_selfref_is_skeleton() -> None:
    ok, why = classify_selfref(["src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py"])
    assert not ok and any("自指" in w for w in why)


def test_r3_schedule_registry_selfref_is_skeleton() -> None:
    for target in (
        "config/resource_profile_registry.yaml",
        "config/evolution_schedule_seeds.yaml",
        "config/schedule_gate_policy.yaml",
    ):
        ok, why = classify_selfref([target])
        assert not ok and any("自指" in w for w in why)


def test_r3_external_target_is_module_level() -> None:
    ok, why = classify_selfref(["src/zephyr/governance/foo.py"])
    assert ok and why == []


# ---------------------------------------------------------------------------
# 三证据合流 + 路由不变量
# ---------------------------------------------------------------------------

def test_route_module_level_auto_dispatch() -> None:
    d = _route()
    assert d.tier == TIER_MODULE and d.owner_gate is False and d.reasons == []


def test_route_any_skeleton_evidence_sets_owner_gate() -> None:
    """任一命中骨架级即骨架级；骨架级必置 owner_gate=true（C6 验收原文）。"""
    d = _route(target_files=["src/zephyr/governance/unregistered.py"])
    assert d.tier == TIER_SKELETON and d.owner_gate is True


def test_route_selfref_always_owner() -> None:
    """自指命中必 Owner（R3 定调 #9）。"""
    d = _route(
        target_files=["src/zephyr/ai_layer/scheduling/router.py"],
        registered_files=["src/zephyr/ai_layer/scheduling/router.py"],
    )
    assert d.tier == TIER_SKELETON
    assert d.owner_gate is True
    assert any("自指" in r for r in d.reasons)


def test_route_mixed_evidence_skeleton_wins() -> None:
    d = _route(
        target_files=["src/zephyr/governance/foo.py", "src/zephyr/governance/new.py"],
        domain_id="trading_algo",  # R2 high + R1 超范围双命中
    )
    assert d.tier == TIER_SKELETON and d.owner_gate is True
    assert len(d.reasons) >= 2
