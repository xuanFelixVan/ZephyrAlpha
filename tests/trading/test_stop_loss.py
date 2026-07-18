# [A_test] module_id: SRC-TST-2073 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-690 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_stop_loss
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/risk/stop_loss.py
======================================================

Phase C 升级后测试——验证四种止损模式的实际行为。

覆盖矩阵：
  evaluate_stop_loss:
    - fixed_pct 止损 × 3（触发 / 未触发 / 边界）
    - trailing 止损 × 2（触发 / 未触发）
    - time_based 止损 × 2（触发 / 未触发）
    - volatility 止损 × 2（触发 / 未触发）
    - 空持仓 × 1
  trigger_kill_switch:
    - 正常激活 × 1
    - scope='symbol' × 1
  reset_kill_switch:
    - 正常重置 × 1

Safety: HIGH | Phase C 升级
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.risk.stop_loss import (
    evaluate_stop_loss,
    reset_kill_switch,
    trigger_kill_switch,
)


class TestEvaluateStopLossFixedPct:
    """固定比例止损测试"""

    def test_triggers_below_stop(self):
        position = {"entry_price": 10.0, "qty": 100, "entry_date": datetime.now(UTC)}
        rules = {"method": "fixed_pct", "stop_loss_pct": 0.05}
        assert evaluate_stop_loss(position, current_price=9.4, rules=rules) is True

    def test_no_trigger_above_stop(self):
        position = {"entry_price": 10.0, "qty": 100}
        rules = {"method": "fixed_pct", "stop_loss_pct": 0.05}
        assert evaluate_stop_loss(position, current_price=9.6, rules=rules) is False

    def test_boundary_at_stop_price(self):
        position = {"entry_price": 10.0, "qty": 100}
        rules = {"method": "fixed_pct", "stop_loss_pct": 0.05}
        assert evaluate_stop_loss(position, current_price=9.5, rules=rules) is True


class TestEvaluateStopLossTrailing:
    """移动止损测试"""

    def test_triggers_from_peak(self):
        position = {"entry_price": 10.0, "qty": 100, "highest_since_entry": 12.0}
        rules = {"method": "trailing", "trailing_pct": 0.03}
        assert evaluate_stop_loss(position, current_price=11.5, rules=rules) is True

    def test_no_trigger_near_peak(self):
        position = {"entry_price": 10.0, "qty": 100, "highest_since_entry": 12.0}
        rules = {"method": "trailing", "trailing_pct": 0.03}
        assert evaluate_stop_loss(position, current_price=11.7, rules=rules) is False


class TestEvaluateStopLossTimeBased:
    """时间止损测试"""

    def test_triggers_past_max_hold(self):
        position = {"entry_price": 10.0, "qty": 100, "entry_date": datetime.now(UTC) - timedelta(days=25)}
        rules = {"method": "time_based", "max_hold_days": 20}
        assert evaluate_stop_loss(position, current_price=10.0, rules=rules) is True

    def test_no_trigger_within_hold(self):
        position = {"entry_price": 10.0, "qty": 100, "entry_date": datetime.now(UTC)}
        rules = {"method": "time_based", "max_hold_days": 20}
        assert evaluate_stop_loss(position, current_price=10.0, rules=rules) is False


class TestEvaluateStopLossVolatility:
    """波动率止损测试"""

    def test_triggers_vol_stop(self):
        position = {"entry_price": 10.0, "qty": 100}
        rules = {"method": "volatility", "current_volatility": 0.05, "vol_multiplier": 2.0}
        assert evaluate_stop_loss(position, current_price=8.9, rules=rules) is True

    def test_no_trigger_in_range(self):
        position = {"entry_price": 10.0, "qty": 100}
        rules = {"method": "volatility", "current_volatility": 0.05, "vol_multiplier": 2.0}
        assert evaluate_stop_loss(position, current_price=9.1, rules=rules) is False


class TestEvaluateStopLossEdgeCases:
    """边界条件测试"""

    def test_zero_entry_price_no_trigger(self):
        position = {"entry_price": 0, "qty": 100}
        rules = {"method": "fixed_pct", "stop_loss_pct": 0.05}
        assert evaluate_stop_loss(position, current_price=5.0, rules=rules) is False

    def test_default_method_fallback(self):
        position = {"entry_price": 10.0, "qty": 100}
        rules = {}  # defaults to fixed_pct
        assert evaluate_stop_loss(position, current_price=9.4, rules=rules) is True


class TestTriggerKillSwitch:
    """Kill Switch 激活测试"""

    @pytest.mark.security
    def test_activates_correctly(self):
        result = trigger_kill_switch(reason="max drawdown exceeded")
        assert result["status"] == "triggered"
        assert result["scope"] == "all"
        assert result["requires_manual_reset"] is True
        assert "event_id" in result

    @pytest.mark.security
    def test_symbol_scope(self):
        result = trigger_kill_switch(reason="suspicious activity", scope="symbol")
        assert result["scope"] == "symbol"


class TestResetKillSwitch:
    """Kill Switch 重置测试"""

    @pytest.mark.security
    def test_resets_with_confirm(self):
        confirmation = {"confirmed_by": "trader1", "override_reason": "false alarm"}
        assert reset_kill_switch(confirmation) is True
