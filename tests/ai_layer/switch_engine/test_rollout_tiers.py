"""S8 rollout_tiers 验收测试：三档升降机检/五前置缺一拒/grandfather 渐进收敛/留痕可回退。"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.switch_engine.rollout_tiers import (
    TIER_BEHAVIORS,
    TIER_BLOCK,
    TIER_SHADOW,
    TIER_WARN,
    GrandfatherResult,
    TierLedger,
    grandfather_filter,
)


def test_tier_behaviors_match_design() -> None:
    assert TIER_BEHAVIORS[TIER_SHADOW].startswith("record_only")
    assert TIER_BEHAVIORS[TIER_WARN].startswith("audit_notify_only")
    assert TIER_BEHAVIORS[TIER_BLOCK].startswith("block")


def test_upgrade_shadow_to_warn_records_entry() -> None:
    ledger = TierLedger("gate.demo")
    entry = ledger.upgrade_to(
        TIER_WARN,
        evidence_ref="stats-30d",
        windows_in_tier=1,
        false_positives=0,
        owner_ack=True,
        ruling_ref="",
        grandfather_enforced=False,
    )
    assert ledger.tier == TIER_WARN
    assert entry["action"] == "rollout_tier_upgrade"
    assert entry["from_tier"] == TIER_SHADOW and entry["to_tier"] == TIER_WARN
    assert entry["at"].endswith("+00:00")


def test_upgrade_requires_residency_window() -> None:
    ledger = TierLedger("gate.demo")
    with pytest.raises(ValueError, match="驻留不足"):
        ledger.upgrade_to(
            TIER_WARN, evidence_ref="e", windows_in_tier=0, false_positives=0,
            owner_ack=True, ruling_ref="", grandfather_enforced=False,
        )


def test_upgrade_requires_zero_false_positives() -> None:
    ledger = TierLedger("gate.demo")
    with pytest.raises(ValueError, match="误报"):
        ledger.upgrade_to(
            TIER_WARN, evidence_ref="e", windows_in_tier=1, false_positives=2,
            owner_ack=True, ruling_ref="", grandfather_enforced=False,
        )


def test_upgrade_requires_owner_ack() -> None:
    ledger = TierLedger("gate.demo")
    with pytest.raises(ValueError, match="Owner 知情"):
        ledger.upgrade_to(
            TIER_WARN, evidence_ref="e", windows_in_tier=1, false_positives=0,
            owner_ack=False, ruling_ref="", grandfather_enforced=False,
        )


def test_upgrade_to_block_five_prerequisites() -> None:
    """warn→block 五前置：驻留+误报0+Owner+裁定登记+grandfather，缺一拒。"""
    ledger = TierLedger("gate.demo")
    ledger.upgrade_to(
        TIER_WARN, evidence_ref="e1", windows_in_tier=1, false_positives=0,
        owner_ack=True, ruling_ref="", grandfather_enforced=False,
    )
    with pytest.raises(ValueError, match="裁定登记"):
        ledger.upgrade_to(
            TIER_BLOCK, evidence_ref="e2", windows_in_tier=1, false_positives=0,
            owner_ack=True, ruling_ref="", grandfather_enforced=True,
        )
    with pytest.raises(ValueError, match="grandfather"):
        ledger.upgrade_to(
            TIER_BLOCK, evidence_ref="e2", windows_in_tier=1, false_positives=0,
            owner_ack=True, ruling_ref="RULING-1", grandfather_enforced=False,
        )
    entry = ledger.upgrade_to(
        TIER_BLOCK, evidence_ref="e2", windows_in_tier=1, false_positives=0,
        owner_ack=True, ruling_ref="RULING-1", grandfather_enforced=True,
    )
    assert ledger.tier == TIER_BLOCK
    assert entry["ruling_ref"] == "RULING-1"  # 升档载荷含裁定登记挂接


def test_skip_tier_rejected() -> None:
    ledger = TierLedger("gate.demo")
    with pytest.raises(ValueError, match="逐级"):
        ledger.upgrade_to(
            TIER_BLOCK, evidence_ref="e", windows_in_tier=9, false_positives=0,
            owner_ack=True, ruling_ref="R", grandfather_enforced=True,
        )


def test_downgrade_requires_owner_and_leaves_trail() -> None:
    """降档（放松）同走 Owner 门位；留痕可回退（验收锚 S8）。"""
    ledger = TierLedger("gate.demo")
    ledger.upgrade_to(
        TIER_WARN, evidence_ref="e1", windows_in_tier=1, false_positives=0,
        owner_ack=True, ruling_ref="", grandfather_enforced=False,
    )
    with pytest.raises(ValueError, match="Owner 门位"):
        ledger.downgrade_to(TIER_SHADOW, evidence_ref="e2", owner_ack=False)
    entry = ledger.downgrade_to(TIER_SHADOW, evidence_ref="e2", owner_ack=True)
    assert ledger.tier == TIER_SHADOW  # 回退生效
    assert entry["action"] == "rollout_tier_downgrade"
    assert [item["to_tier"] for item in ledger.entries] == [TIER_WARN, TIER_SHADOW]


def test_ledger_append_only() -> None:
    ledger = TierLedger("gate.demo")
    ledger.upgrade_to(
        TIER_WARN, evidence_ref="e1", windows_in_tier=1, false_positives=0,
        owner_ack=True, ruling_ref="", grandfather_enforced=False,
    )
    snapshot = ledger.entries
    snapshot.append({"forged": True})  # 外部篡改不影响台账
    snapshot[0]["to_tier"] = TIER_BLOCK
    assert len(ledger.entries) == 1
    assert ledger.entries[0]["to_tier"] == TIER_WARN


def test_grandfather_filter_existing_allowed_new_blocked() -> None:
    result = grandfather_filter(
        ["legacy_violation_a", "new_violation_b", "legacy_violation_c"],
        baseline_inventory={"legacy_violation_a", "legacy_violation_c"},
    )
    assert isinstance(result, GrandfatherResult)
    assert result.allowed_existing == ["legacy_violation_a", "legacy_violation_c"]
    assert result.blocked_new == ["new_violation_b"]  # 新引入阻断（渐进收敛）
    assert result.all_clear is False
    clean = grandfather_filter([], {"anything"})
    assert clean.all_clear is True


def test_grandfather_rejects_non_string() -> None:
    with pytest.raises(ValueError, match="字符串"):
        grandfather_filter([123], set())  # type: ignore[list-item]
