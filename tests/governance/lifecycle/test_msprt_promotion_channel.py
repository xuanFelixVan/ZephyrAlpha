# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.lifecycle.test_msprt_promotion_channel
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-TEST-GOV-MSPRTCH | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""mSPRT 晋升编排层单元测试（61 号 §3.3 纪律 1 通道化，内核 MOD-PF-008 仅消费不改）。

覆盖:
  - 预注册纪律（SR 26-02）：feed 前须 register；重复注册/空 ID/自配对 → PromotionChannelError
  - 状态机推进：PENDING（已登记未投喂）→ OBSERVING（留观）→ PROMOTED / ELIMINATED（终局）
  - 满窗最小样本门直通：n<30 一律 OBSERVING（内核裁定 2，编排层不加戏）
  - 裁决输出：晋升（PROMOTE_CHALLENGER）/ 留观（RETAIN_CHAMPION）/ 回退淘汰（ELIMINATE_CHALLENGER）
  - 终局幂等重入：PROMOTED/ELIMINATED 后重复 feed/feed_batch 零副作用，裁决快照不变
  - feed_batch 早停：达终局即停（序贯检验语义），n 停在终局步
  - 空输入：空批 → 当前快照（新通道 PENDING / n=0 / M=1.0）
  - 参数透传：内核 ValueError 契约不上包（alpha 越界注册即抛）
  - delta 非法（NaN/inf）→ PromotionChannelError（编排层边界自查）
"""

from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.msprt_promotion_channel import (
    PromotionChannelError,
    PromotionChannelManager,
    PromotionState,
)
from zephyr.pf_core.core.msprt_champion_challenger import ChampionChallengerDecision

CHAMPION = "model_champion_v1"
CHALLENGER = "model_challenger_v2"


def _manager(**kwargs) -> PromotionChannelManager:
    m = PromotionChannelManager(**kwargs)
    m.register(CHAMPION, CHALLENGER)
    return m


# ---------------------------------------------------------------------------
# 预注册纪律
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_feed_requires_preregistered_pair(self):
        """SR 26-02 预注册假设纪律：并行期开始前通道须文档化登记，未注册拒喂。"""
        m = PromotionChannelManager()
        with pytest.raises(PromotionChannelError):
            m.feed(CHAMPION, CHALLENGER, 0.01)

    def test_duplicate_registration_rejected(self):
        m = _manager()
        with pytest.raises(PromotionChannelError):
            m.register(CHAMPION, CHALLENGER)

    def test_empty_ids_rejected(self):
        m = PromotionChannelManager()
        with pytest.raises(PromotionChannelError):
            m.register("", CHALLENGER)
        with pytest.raises(PromotionChannelError):
            m.register(CHAMPION, " ")

    def test_self_pairing_rejected(self):
        m = PromotionChannelManager()
        with pytest.raises(PromotionChannelError):
            m.register(CHAMPION, CHAMPION)

    def test_distinct_pairs_independent(self):
        m = _manager()
        m.register(CHAMPION, "challenger_b")
        assert set(m.pairs()) == {(CHAMPION, CHALLENGER), (CHAMPION, "challenger_b")}

    def test_verdict_unknown_pair_raises(self):
        with pytest.raises(PromotionChannelError):
            PromotionChannelManager().verdict(CHAMPION, CHALLENGER)


# ---------------------------------------------------------------------------
# 状态机推进（PENDING → OBSERVING → PROMOTED/ELIMINATED）
# ---------------------------------------------------------------------------


class TestStateAdvancement:
    def test_fresh_channel_pending(self):
        v = _manager().verdict(CHAMPION, CHALLENGER)
        assert v.state is PromotionState.PENDING
        assert v.n == 0
        assert v.decision is None
        assert v.m_value == 1.0  # M_0 = 1（e-process 起点）

    def test_first_feed_enters_observing(self):
        v = _manager().feed(CHAMPION, CHALLENGER, 0.01)
        assert v.state is PromotionState.OBSERVING
        assert v.n == 1
        assert v.decision is ChampionChallengerDecision.RETAIN_CHAMPION  # 留观

    def test_window_gate_keeps_observing_before_30(self):
        """窗满（n=30）前不终局判定——内核裁定 2 直通，编排层不得提前终局。"""
        v = None
        m = _manager()
        for _ in range(29):
            v = m.feed(CHAMPION, CHALLENGER, 1.0)  # 持续显著为正也不提前晋升
        assert v.state is PromotionState.OBSERVING
        assert v.n == 29

    def test_promotion_at_full_window(self):
        m = _manager()
        v = m.feed_batch(CHAMPION, CHALLENGER, [1.0] * 30)
        assert v.state is PromotionState.PROMOTED
        assert v.decision is ChampionChallengerDecision.PROMOTE_CHALLENGER
        assert v.n == 30
        assert v.m_value >= 20.0  # Ville 边界 1/α

    def test_elimination_on_significant_negative(self):
        v = _manager().feed_batch(CHAMPION, CHALLENGER, [-1.0] * 30)
        assert v.state is PromotionState.ELIMINATED
        assert v.decision is ChampionChallengerDecision.ELIMINATE_CHALLENGER

    def test_elimination_on_zero_effect(self):
        """满窗无效应证据（M ≤ α 下界）→ 淘汰回退（memo：证据不足保留 Champion）。"""
        v = _manager().feed_batch(CHAMPION, CHALLENGER, [0.0] * 30)
        assert v.state is PromotionState.ELIMINATED
        assert v.decision is ChampionChallengerDecision.ELIMINATE_CHALLENGER


# ---------------------------------------------------------------------------
# 终局幂等重入
# ---------------------------------------------------------------------------


class TestTerminalIdempotency:
    def test_feed_after_terminal_is_noop(self):
        m = _manager()
        v1 = m.feed_batch(CHAMPION, CHALLENGER, [1.0] * 30)
        assert v1.state is PromotionState.PROMOTED
        v2 = m.feed(CHAMPION, CHALLENGER, -5.0)  # 反向数据不得翻盘已定格裁决
        assert v2 == v1
        assert v2.n == 30  # 内核冻结，n 不推进

    def test_batch_after_terminal_unchanged(self):
        m = _manager()
        m.feed_batch(CHAMPION, CHALLENGER, [-1.0] * 30)
        v1 = m.verdict(CHAMPION, CHALLENGER)
        v2 = m.feed_batch(CHAMPION, CHALLENGER, [1.0] * 10)
        assert v2 == v1
        assert v2.state is PromotionState.ELIMINATED


# ---------------------------------------------------------------------------
# feed_batch 早停与空输入
# ---------------------------------------------------------------------------


class TestFeedBatch:
    def test_batch_early_stops_at_terminal(self):
        """序贯检验核心语义：达边界即停——40 笔投喂在第 30 笔终局即截断。"""
        v = _manager().feed_batch(CHAMPION, CHALLENGER, [1.0] * 40)
        assert v.state is PromotionState.PROMOTED
        assert v.n == 30  # 早停，不吃满 40

    def test_empty_batch_returns_snapshot(self):
        v = _manager().feed_batch(CHAMPION, CHALLENGER, [])
        assert v.state is PromotionState.PENDING
        assert v.n == 0
        assert v.m_value == 1.0

    def test_empty_batch_on_observing_keeps_state(self):
        m = _manager()
        m.feed_batch(CHAMPION, CHALLENGER, [0.01] * 10)
        v = m.feed_batch(CHAMPION, CHALLENGER, [])
        assert v.state is PromotionState.OBSERVING
        assert v.n == 10

    def test_batch_unknown_pair_raises(self):
        with pytest.raises(PromotionChannelError):
            PromotionChannelManager().feed_batch(CHAMPION, CHALLENGER, [0.01])


# ---------------------------------------------------------------------------
# 输入与参数契约
# ---------------------------------------------------------------------------


class TestContracts:
    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_illegal_delta_rejected(self, bad):
        m = _manager()
        with pytest.raises(PromotionChannelError):
            m.feed(CHAMPION, CHALLENGER, bad)
        assert m.verdict(CHAMPION, CHALLENGER).n == 0  # 非法投喂不污染内核

    def test_kernel_value_error_passthrough(self):
        """内核参数契约（ValueError）原样上抛，编排层不包装不吞噬。"""
        with pytest.raises(ValueError):
            _manager(alpha=1.5)
