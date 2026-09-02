# [BLUEPRINT] MOD-SIG-038 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/90_methodology_open_questions.md §22.3（supplement：GAP-F-24 通道映射规则层）
# [MODULE] tests.signal_ashare.test_foreign_impact_judge
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.foreign_impact_judge
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网（query_fn 桩）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=外盘对A股影响判定逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-038_judge_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-038 supplement 外盘对A股影响判定引擎 单元测试（GAP-F-24，合成数据）。

覆盖：12 标的方向约定（美股/A50 涨=利好、美元/离岸人民币/美债/WTI 涨=利空、
黄金=中性观察）、三档强度（1%/2% 与 MOD-SIG-038 同带）、6 通道映射、
覆盖门控（missing 标的不参评+留痕）、综合判定（偏多/偏空/中性 × 强/中/弱影响）、
us_index 变动加载（query_fn 桩）、输入校验 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.foreign_impact_judge import (
    CHANNEL_CAPITAL,
    CHANNEL_COST,
    CHANNEL_HEDGE,
    CHANNEL_INDUSTRY,
    CHANNEL_RATE,
    CHANNEL_SENTIMENT,
    ForeignImpactConfig,
    available_keys_from_coverage,
    compute_changes_from_us_index,
    judge_foreign_impact,
)


def _cfg(**kw) -> ForeignImpactConfig:
    return ForeignImpactConfig(**kw)


ALL_KEYS = {
    "dow_jones",
    "nasdaq",
    "sp500",
    "hsi",
    "nikkei",
    "kospi",
    "a50",
    "dxy",
    "usdcnh",
    "wti",
    "gold",
    "ust10y",
}


# ------------------------------------------------------------------
# 单标的方向/强度/通道
# ------------------------------------------------------------------


def test_us_index_up_is_positive() -> None:
    out = judge_foreign_impact({"dow_jones": 1.5}, available_keys=ALL_KEYS, config=_cfg())
    v = out.verdicts[0]
    assert v.label == "利好"
    assert v.channel == CHANNEL_SENTIMENT
    assert v.strength == "中"  # 1.5% ∈ [1%,2%)


def test_a50_highest_weight() -> None:
    out = judge_foreign_impact({"a50": -2.5}, available_keys=ALL_KEYS, config=_cfg())
    v = out.verdicts[0]
    assert v.label == "利空"
    assert v.strength == "强"
    assert v.weight >= 1.2


def test_dxy_up_is_negative_capital_channel() -> None:
    out = judge_foreign_impact({"dxy": 0.8}, available_keys=ALL_KEYS, config=_cfg())
    v = out.verdicts[0]
    assert v.label == "利空"
    assert v.channel == CHANNEL_CAPITAL
    assert v.strength == "弱"


def test_usdcnh_up_is_negative() -> None:
    out = judge_foreign_impact({"usdcnh": 1.2}, available_keys=ALL_KEYS, config=_cfg())
    assert out.verdicts[0].label == "利空"


def test_ust10y_up_is_negative_rate_channel() -> None:
    out = judge_foreign_impact({"ust10y": 2.0}, available_keys=ALL_KEYS, config=_cfg())
    v = out.verdicts[0]
    assert v.label == "利空"
    assert v.channel == CHANNEL_RATE
    assert v.strength == "强"


def test_wti_up_is_negative_cost_channel_with_note() -> None:
    out = judge_foreign_impact({"wti": 3.0}, available_keys=ALL_KEYS, config=_cfg())
    v = out.verdicts[0]
    assert v.label == "利空"
    assert v.channel == CHANNEL_COST
    assert "油气" in v.note or "成本" in v.note


def test_gold_is_neutral_watch() -> None:
    out = judge_foreign_impact({"gold": 2.5}, available_keys=ALL_KEYS, config=_cfg())
    v = out.verdicts[0]
    assert v.label == "中性"
    assert v.channel == CHANNEL_HEDGE
    assert "避险" in v.note


def test_zero_change_is_neutral() -> None:
    out = judge_foreign_impact({"dow_jones": 0.0}, available_keys=ALL_KEYS, config=_cfg())
    assert out.verdicts[0].label == "中性"


def test_unknown_target_ignored_with_note() -> None:
    out = judge_foreign_impact({"unknown_x": 5.0}, available_keys=ALL_KEYS, config=_cfg())
    assert out.verdicts == []
    assert any("未知标的" in n for n in out.notes)


# ------------------------------------------------------------------
# 覆盖门控
# ------------------------------------------------------------------


def test_coverage_gating_excludes_missing() -> None:
    out = judge_foreign_impact(
        {"dow_jones": 1.5, "hsi": 2.0},
        available_keys={"dow_jones"},  # hsi missing
        config=_cfg(),
    )
    assert len(out.verdicts) == 1
    assert any("hsi" in n for n in out.notes)


def test_available_keys_from_coverage() -> None:
    class _Item:
        def __init__(self, key, status):
            self.key, self.status = key, status

    class _Report:
        items = [_Item("dow_jones", "covered"), _Item("hsi", "stale"), _Item("gold", "missing")]

    keys = available_keys_from_coverage(_Report())
    assert keys == {"dow_jones", "hsi"}  # stale 仍参评（时效留痕由调用方），missing 剔除


# ------------------------------------------------------------------
# 综合判定
# ------------------------------------------------------------------


def test_aggregate_bullish_strong() -> None:
    changes = {"dow_jones": 2.0, "nasdaq": 2.5, "sp500": 2.0, "a50": 2.0, "usdcnh": -1.5}
    out = judge_foreign_impact(changes, available_keys=ALL_KEYS, config=_cfg())
    assert out.direction == "偏多"
    assert out.impact in {"强影响", "中影响"}
    assert out.summary.startswith("偏多")


def test_aggregate_bearish() -> None:
    changes = {"dow_jones": -2.0, "nasdaq": -2.5, "usdcnh": 1.5, "ust10y": 2.0}
    out = judge_foreign_impact(changes, available_keys=ALL_KEYS, config=_cfg())
    assert out.direction == "偏空"


def test_aggregate_neutral_when_mixed_weak() -> None:
    changes = {"dow_jones": 0.4, "dxy": 0.3}
    out = judge_foreign_impact(changes, available_keys=ALL_KEYS, config=_cfg())
    assert out.direction == "中性"
    assert out.impact == "弱影响"
    assert out.summary == "中性·弱影响"


def test_empty_verdicts_degraded() -> None:
    out = judge_foreign_impact({}, available_keys=ALL_KEYS, config=_cfg())
    assert out.degraded is True
    assert out.direction == "中性"


def test_channel_breakdown_counts() -> None:
    changes = {"dow_jones": 1.5, "dxy": 1.2, "gold": 0.5, "wti": 2.0, "ust10y": 0.2}
    out = judge_foreign_impact(changes, available_keys=ALL_KEYS, config=_cfg())
    channels = {v.channel for v in out.verdicts}
    assert CHANNEL_SENTIMENT in channels
    assert CHANNEL_CAPITAL in channels
    assert CHANNEL_COST in channels
    assert CHANNEL_RATE in channels
    assert out.channel_scores  # 分通道得分非空


def test_json_serializable() -> None:
    out = judge_foreign_impact({"dow_jones": 1.5}, available_keys=ALL_KEYS, config=_cfg())
    json.dumps(asdict(out), ensure_ascii=False)


# ------------------------------------------------------------------
# us_index 变动加载（query_fn 桩）
# ------------------------------------------------------------------


def test_compute_changes_from_us_index() -> None:
    def fake_query(sql: str) -> str:
        assert "us_index" in sql
        # TSV: symbol \t trade_date \t close（按 symbol, trade_date DESC）
        return (
            "DJI\t2026-08-21\t45000.0\nDJI\t2026-08-20\t44500.0\n"
            "IXIC\t2026-08-21\t15000.0\nIXIC\t2026-08-19\t14800.0\n"
            "SPX\t2026-08-21\t6000.0\n"
        )

    changes = compute_changes_from_us_index(fake_query)
    assert changes["dow_jones"] == pytest.approx((45000.0 / 44500.0 - 1.0) * 100.0, abs=1e-3)
    assert changes["nasdaq"] == pytest.approx((15000.0 / 14800.0 - 1.0) * 100.0, abs=1e-3)
    assert "sp500" not in changes  # 单行无法算变动 → 不出（留痕由调用方）


def test_compute_changes_query_error_raises_valueerror() -> None:
    def bad_query(sql: str) -> str:
        raise RuntimeError("boom")

    with pytest.raises(ValueError, match="us_index"):
        compute_changes_from_us_index(bad_query)
