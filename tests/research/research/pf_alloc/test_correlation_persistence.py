# [BLUEPRINT] MOD-PA-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_test_correlation_persistence | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.pf_alloc.test_correlation_persistence
# [TESTS] src/zephyr/pf_alloc/core/strategy_correlation_gate.py（90 号 Phase2 持久化段）
# [TTL] task_bound
"""90 号 Phase2 项（#20 工程细节）：相关性门禁"持续 30 天"持久化条件 toy 断言。

裁定真源：90_methodology_open_questions.md §20（v2.0.0 B-010 补充）——
  90 天滚动相关性剔除规则与现有 0.85/0.90 阈值口径统一：补"持续 30 天"持久化
  条件（避免单日噪声误剔除）。未提供持续天数数据时维持现行立即否决（向后兼容）。
"""

from __future__ import annotations

import pytest

from zephyr.pf_alloc.core.strategy_correlation_gate import (
    CorrelationGateConfig,
    GateVerdict,
    InvalidCorrelationInputError,
    StrategyCorrelationGate,
    StrategyPairMetrics,
)


class TestPersistenceCondition:
    def test_sustained_30d_reject(self):
        """0.88 相关持续 35 天 ≥30 → REJECT（持久化达标，维持否决）。"""
        gate = StrategyCorrelationGate()
        res = gate.check([StrategyPairMetrics("S1", "S2", correlation=0.88, correlation_sustained_days=35)])
        assert res.overall_verdict == GateVerdict.REJECT

    def test_unsustained_downgrades_to_warn(self):
        """0.88 相关仅持续 10 天 <30 → 降级 WARN（防单日噪声误剔除）。"""
        gate = StrategyCorrelationGate()
        res = gate.check([StrategyPairMetrics("S1", "S2", correlation=0.88, correlation_sustained_days=10)])
        assert res.overall_verdict == GateVerdict.WARN

    def test_hard_reject_unsustained_also_downgrades(self):
        """0.95 硬否决相关未达持续条件同样降级 WARN。"""
        gate = StrategyCorrelationGate()
        res = gate.check([StrategyPairMetrics("S1", "S2", correlation=0.95, correlation_sustained_days=3)])
        assert res.overall_verdict == GateVerdict.WARN

    def test_no_sustained_data_legacy_behavior(self):
        """未提供持续天数 → 维持现行立即否决（向后兼容既有调用方）。"""
        gate = StrategyCorrelationGate()
        res = gate.check([StrategyPairMetrics("S1", "S2", correlation=0.88)])
        assert res.overall_verdict == GateVerdict.REJECT

    def test_custom_sustained_threshold(self):
        cfg = CorrelationGateConfig(correlation_reject_sustained_days=60)
        gate = StrategyCorrelationGate(cfg)
        res = gate.check([StrategyPairMetrics("S1", "S2", correlation=0.88, correlation_sustained_days=45)])
        assert res.overall_verdict == GateVerdict.WARN

    def test_negative_sustained_days_raises(self):
        gate = StrategyCorrelationGate()
        with pytest.raises(InvalidCorrelationInputError):
            gate.check([StrategyPairMetrics("S1", "S2", correlation=0.88, correlation_sustained_days=-1)])

    def test_default_config_30d(self):
        assert CorrelationGateConfig().correlation_reject_sustained_days == 30
