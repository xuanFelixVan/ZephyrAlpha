# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [TTL] permanent
"""MOD-SIG-137 negative_veto 单元测试（红蓝对抗：红-边界/红-契约/红-故障）。"""

from __future__ import annotations

import pytest

from zephyr.signal_fundamental.negative_veto import (
    NegativeFacts,
    NegativeVetoConfig,
    NegativeVetoError,
    apply_negative_veto,
)


class TestOneVoteVeto:
    """六项清单一票否决：命中任一即出池。"""

    @pytest.mark.parametrize("facts,expect_reason", [
        (NegativeFacts(earnings_forecast_loss=True), "业绩暴雷"),
        (NegativeFacts(under_investigation=True), "立案调查"),
        (NegativeFacts(major_shareholder_reduction_pending=True), "大股东减持"),
        (NegativeFacts(goodwill_impairment_risk=True), "商誉减值风险"),
        (NegativeFacts(rights_issue_pending=True), "配股圈钱"),
        (NegativeFacts(blacklisted=True), "黑名单"),
        (NegativeFacts(unlock_ratio=0.06), "解禁"),
    ])
    def test_each_item_vetoes_alone(self, facts, expect_reason):
        v = apply_negative_veto(facts)
        assert v.vetoed is True
        assert any(expect_reason in r for r in v.reasons)

    def test_unlock_at_threshold_not_triggered(self):
        # 恰好 5% 不触发（严格大于）
        v = apply_negative_veto(NegativeFacts(unlock_ratio=0.05))
        assert v.vetoed is False

    def test_clean_facts_pass(self):
        v = apply_negative_veto(
            NegativeFacts(
                earnings_forecast_loss=False,
                under_investigation=False,
                major_shareholder_reduction_pending=False,
                unlock_ratio=0.01,
                goodwill_impairment_risk=False,
                rights_issue_pending=False,
                blacklisted=False,
            )
        )
        assert v.vetoed is False and v.reasons == ()

    def test_all_missing_facts_pass(self):
        # 红-故障：证据全缺不否决（筛选漏斗 fail-open，由打分池兜底）
        v = apply_negative_veto(NegativeFacts())
        assert v.vetoed is False


class TestDisclosure:
    """全量披露：多命中不短路。"""

    def test_multiple_hits_all_disclosed(self):
        v = apply_negative_veto(
            NegativeFacts(
                earnings_forecast_loss=True,
                under_investigation=True,
                unlock_ratio=0.12,
            )
        )
        assert v.vetoed is True
        assert len(v.reasons) == 3

    def test_custom_threshold(self):
        cfg = NegativeVetoConfig(unlock_ratio_threshold=0.03)
        v = apply_negative_veto(NegativeFacts(unlock_ratio=0.04), cfg)
        assert v.vetoed is True
        assert any("3%" in r for r in v.reasons)


class TestFailClosed:
    """红-契约：越界 fail-closed。"""

    @pytest.mark.parametrize("bad", [-0.01, 1.5, float("nan")])
    def test_unlock_ratio_out_of_range_rejected(self, bad):
        with pytest.raises(NegativeVetoError):
            NegativeFacts(unlock_ratio=bad)

    def test_bad_config_rejected(self):
        with pytest.raises(NegativeVetoError):
            NegativeVetoConfig(unlock_ratio_threshold=0.0)

    def test_determinism(self):
        f = NegativeFacts(unlock_ratio=0.2, under_investigation=True)
        assert apply_negative_veto(f) == apply_negative_veto(f)

    def test_verdict_frozen(self):
        v = apply_negative_veto(NegativeFacts(under_investigation=True))
        with pytest.raises(Exception):
            v.vetoed = False
