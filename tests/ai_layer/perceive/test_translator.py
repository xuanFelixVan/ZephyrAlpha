# [MODULE] tests.ai_layer.perceive.test_translator
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""施工项 6 验收机检面：五探测器各注入合成信号→正确开单；同矿脉冷却期生效；共享预算扣减正确。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from zephyr.ai_layer.perceive.search_orders import SearchOrderError, SearchOrderJournal
from zephyr.ai_layer.perceive.translator import (
    BEAT_PRIORITY,
    CHANNEL_VEINS,
    DETECTOR_PRIORITY,
    DETECTOR_RESERVE_FLOOR,
    BudgetExhaustedError,
    BudgetLedger,
    DetectorSignal,
    PerceiveTranslator,
)

FIXED_NOW: datetime = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)


def _signal(channel: str, **attributes: str) -> DetectorSignal:
    return DetectorSignal(
        channel=channel,
        signal_name=f"synthetic-{channel}",
        trigger_ref=f"test://{channel}/signal-001",
        occurred_at=FIXED_NOW,
        attributes=dict(attributes),
    )


def _translator(tmp_path: Path, **ledger_kwargs: object) -> PerceiveTranslator:
    journal = SearchOrderJournal(tmp_path / "orders")
    return PerceiveTranslator(journal, ledger=BudgetLedger(journal.state_dir, **ledger_kwargs))


def test_five_channels_open_correct_orders(tmp_path: Path) -> None:
    """验收原文：五探测器各注入合成信号→正确开单（vein/family/trigger/priority 逐项断言）。"""
    translator = _translator(tmp_path)
    channels = {
        "strategy_decay": {"decay_cause": "crowding"},
        "e9_attribution": {"style_family": "momentum"},
        "monthly_deviation": {"breach_kind": "gap_rel"},
        "commit_block": {"gate_id": "SYNTAX-GATE"},
        "feedback_loop": {"detector_kind": "flapping"},
    }
    for channel, attrs in channels.items():
        outcome = translator.translate(_signal(channel, **attrs), now=FIXED_NOW)
        assert outcome.action == "opened", f"{channel} 应开单: {outcome.reason}"
        assert outcome.order is not None
        expected_vein, expected_family, _ = CHANNEL_VEINS[channel]
        assert outcome.order.vein_id == expected_vein
        assert outcome.order.vein_family == expected_family
        assert outcome.order.trigger == "detector"
        assert outcome.order.priority == DETECTOR_PRIORITY
    assert len(translator.journal.list_orders()) == 5
    # 共享预算扣减：5 单 × expected_cards=6 = 30（≤ 总量闸 40）
    assert translator.ledger.reserved(now=FIXED_NOW) == 30


def test_decay_cause_direction_keywords(tmp_path: Path) -> None:
    """§2.2 定向映射：decay_cause 四向枚举→双语关键词组进单。"""
    translator = _translator(tmp_path)
    outcome = translator.translate(_signal("strategy_decay", decay_cause="crowding"), now=FIXED_NOW)
    assert "同类因子拥挤度监控" in outcome.order.keyword_groups
    assert "factor crowding monitoring" in outcome.order.keyword_groups
    # 未知方向键：只落通道基础词组（贫信息留痕不失败）
    translator2 = _translator(tmp_path / "b")
    bare = translator2.translate(_signal("strategy_decay"), now=FIXED_NOW)
    assert "策略衰减 定向搜索" in bare.order.keyword_groups
    assert all("拥挤" not in k for k in bare.order.keyword_groups)


def test_same_vein_cooldown_merges_advisor_line(tmp_path: Path) -> None:
    """验收原文：同矿脉冷却期生效（E6 认证线+顾问线合并节流，30 天防重复开单）。"""
    translator = _translator(tmp_path)
    first = translator.translate(
        _signal("strategy_decay", decay_cause="regime"), now=FIXED_NOW
    )
    assert first.action == "opened"
    # 顾问线 DECAY_SUSPECT：同通道同矿脉→冷却拦截
    advisor = translator.translate(
        DetectorSignal(
            channel="strategy_decay",
            signal_name="DECAY_SUSPECT",
            trigger_ref="test://advisor/line",
            occurred_at=FIXED_NOW,
        ),
        now=FIXED_NOW + timedelta(days=5),
    )
    assert advisor.action == "skipped_cooldown"
    assert translator.journal.list_orders()[0].order_id in advisor.reason
    # 冷却窗外（31 天）→可再开
    later = translator.translate(
        _signal("strategy_decay", decay_cause="regime"),
        now=FIXED_NOW + timedelta(days=31),
    )
    assert later.action == "opened"


def test_shared_budget_deduction_and_refusal(tmp_path: Path) -> None:
    """验收原文：共享预算扣减正确（每单扣 expected_cards=6，耗尽拒单留痕不落单）。"""
    translator = _translator(tmp_path)
    # 预载共享预算至 36（5 通道冷却互斥下，用账本预载构造耗尽场景）
    translator.ledger.reserve("preload-1", 36, detector=True, now=FIXED_NOW)
    outcome = translator.translate(_signal("e9_attribution"), now=FIXED_NOW)
    assert outcome.action == "refused_budget"
    assert "daily_budget_exhausted" in outcome.reason
    assert translator.ledger.reserved(now=FIXED_NOW) == 36  # 拒单不扣减
    assert translator.journal.list_orders() == []  # 拒单不落 journal
    # 正常扣减：余量 4 不够一单，但手动小单可过（账本级语义）
    translator.ledger.reserve("preload-2", 4, detector=True, now=FIXED_NOW)
    assert translator.ledger.reserved(now=FIXED_NOW) == 40
    assert translator.ledger.remaining(now=FIXED_NOW) == 0


def test_detector_priority_beats_cannot_touch_reserve_floor(tmp_path: Path) -> None:
    """内监开单优先级高于节拍：beat/manual 不得动用内监保留底（实现解读留痕）。"""
    journal = SearchOrderJournal(tmp_path / "orders")
    ledger = BudgetLedger(journal.state_dir)  # cap=40, floor=8 → beat 上限 32
    translator = PerceiveTranslator(journal, ledger=ledger)
    from zephyr.ai_layer.perceive.search_orders import validate_order

    beat_order = journal.open_order(
        vein_id="VEIN-BEAT-PROBE",
        vein_family="E1",
        trigger="beat",
        trigger_ref="test://beat",
        keyword_groups=("节拍扫", "beat scan"),
        expected_cards=6,
        priority=BEAT_PRIORITY,
        now=FIXED_NOW,
    )
    validate_order(beat_order)
    ledger.reserve(beat_order.order_id, 6, detector=False, now=FIXED_NOW)
    assert ledger.reserved(now=FIXED_NOW) == 6
    # beat 想吃满到 40 → 越保留底被拒（beat ceiling=40-8=32，6+27=33>32）
    with pytest.raises(BudgetExhaustedError, match="ceiling"):
        ledger.reserve("beat-overfloor", 27, detector=False, now=FIXED_NOW)
    # 内监（detector=True）可用到总量闸 40：翻译器再开一单扣 6 → 12
    outcome = translator.translate(_signal("commit_block", gate_id="G"), now=FIXED_NOW)
    assert outcome.action == "opened"
    assert ledger.reserved(now=FIXED_NOW) == 12
    assert ledger.detector_floor == DETECTOR_RESERVE_FLOOR
    assert ledger.daily_cap == 40


def test_unknown_channel_raises(tmp_path: Path) -> None:
    translator = _translator(tmp_path)
    with pytest.raises(SearchOrderError, match="未知内监通道"):
        translator.translate(_signal("twitter_vibes"), now=FIXED_NOW)


def test_source_scope_validated_against_registry(tmp_path: Path) -> None:
    from zephyr.ai_layer.perceive.source_registry import load_source_registry

    registry = load_source_registry()
    translator = _translator(tmp_path)
    translator.registry = registry
    with pytest.raises(SearchOrderError, match="未知 slug"):
        translator.translate(_signal("feedback_loop", source_scope="ghost-src"), now=FIXED_NOW)
    ok = translator.translate(_signal("feedback_loop", source_scope="qlib,hf-papers"), now=FIXED_NOW)
    assert ok.action == "opened"
    assert ok.order.source_scope == ("qlib", "hf-papers")
