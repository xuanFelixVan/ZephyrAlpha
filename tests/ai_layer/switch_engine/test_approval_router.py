"""S6 approval_router 验收测试：risk_tier 九域映射零漏/四债类路由/建议卡形状。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.ai_layer.switch_engine.approval_router import (
    ADVISORY_KIND,
    DEBT_LOGIC,
    DEBT_MECHANICAL,
    DEBT_RULE,
    DEBT_SKELETON,
    ROUTE_AUTO,
    ROUTE_INDEPENDENT_REVIEW,
    ROUTE_OBJ_R_PIPELINE,
    ROUTE_OWNER_ONE_CLICK,
    RiskTierRegistryError,
    build_switch_advisory,
    load_domain_tiers,
    route,
)


@pytest.fixture(scope="module")
def domain_tiers() -> dict[str, str]:
    return load_domain_tiers()  # 真 REG-RISK-TIER-001（只读）


def test_nine_high_domains_owner_route_zero_miss(domain_tiers: dict[str, str]) -> None:
    """验收锚 S6：逻辑债·high 域（9 域）→ owner_one_click 零漏（tier 现查，不写死）。"""
    high_domains = sorted(d for d, t in domain_tiers.items() if t == "high")
    assert len(high_domains) == 9  # DESIGN §②-E 九域
    for domain in high_domains:
        decision = route(DEBT_LOGIC, domain)
        assert decision.route == ROUTE_OWNER_ONE_CLICK, domain
        assert decision.requires_owner_gate is True


def test_low_medium_logic_independent_review_zero_miss(
    domain_tiers: dict[str, str],
) -> None:
    for domain, tier in domain_tiers.items():
        if tier == "high":
            continue
        decision = route(DEBT_LOGIC, domain)
        assert decision.route == ROUTE_INDEPENDENT_REVIEW, domain


def test_mechanical_auto_all_domains(domain_tiers: dict[str, str]) -> None:
    """机械债类（行为零变化）全域全自动。"""
    for domain in domain_tiers:
        decision = route(DEBT_MECHANICAL, domain)
        assert decision.route == ROUTE_AUTO


def test_rule_and_skeleton_routes() -> None:
    assert route(DEBT_RULE, "D_GOVERNANCE").route == ROUTE_OBJ_R_PIPELINE
    skeleton = route(DEBT_SKELETON, "D_FACTOR")
    assert skeleton.route == ROUTE_OWNER_ONE_CLICK
    assert skeleton.requires_owner_gate is True


def test_unknown_debt_rejected() -> None:
    with pytest.raises(ValueError, match="debt_class"):
        route("vibes", "D_GOVERNANCE")


def test_registry_missing_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(RiskTierRegistryError, match="缺失"):
        load_domain_tiers(tmp_path / "nope.yaml")


def test_registry_bad_shape_fails_closed(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"tiers": {}}), encoding="utf-8")
    with pytest.raises(RiskTierRegistryError, match="形状非法"):
        load_domain_tiers(bad)


def test_unknown_domain_defaults_low(tmp_path: Path) -> None:
    empty = tmp_path / "empty.yaml"
    empty.write_text(yaml.safe_dump({"domain_tiers": []}), encoding="utf-8")
    decision = route(DEBT_LOGIC, "D_UNKNOWN", registry_path=empty)
    assert decision.tier == "low"
    assert decision.route == ROUTE_INDEPENDENT_REVIEW


def test_advisory_card_shape() -> None:
    card = build_switch_advisory(
        switch_id="SW-1",
        object_ref="zephyr.demo.module",
        a_summary="champion：延迟 p95=120ms，分歧率 2%",
        b_summary="challenger：延迟 p95=90ms，分歧率 2%，成本 +3%",
        evidence_link="docs/_working/ai_layer_vision/L6_ab_switch/evidence/SW-1",
    )
    assert card["kind"] == ADVISORY_KIND  # promotion 页复用（零新页面）
    assert card["confirm_required"] is True  # 二次确认（S13 先例）
    assert set(card["actions"]) == {"promote", "revert"}
    assert "champion" in card["a_vs_b"] and "challenger" in card["a_vs_b"]


def test_advisory_card_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError, match="证据"):
        build_switch_advisory(
            switch_id="", object_ref="x", a_summary="a", b_summary="b", evidence_link="",
        )
