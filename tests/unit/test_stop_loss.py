"""
单元测试：src/zephyr/l04_risk_management/stop_loss.py
======================================================
覆盖矩阵：
  evaluate_stop_loss:
    - STUB 验证 × 1（确认 raise NotImplementedError）
  trigger_kill_switch:
    - STUB 验证 × 1（确认 raise NotImplementedError）
  reset_kill_switch:
    - STUB 验证 × 1（确认 raise NotImplementedError）

注意：stop_loss.py 当前为 beta 骨架（raise NotImplementedError），
本测试文件验证 stub 标记正确生效，不测试实际业务逻辑。
beta 实现完成后应添加完整业务测试。

Task: l04-stop-loss | Safety: HIGH | beta
"""

from __future__ import annotations

import pytest
from zephyr.l04_risk_management.stop_loss import (
    evaluate_stop_loss,
    reset_kill_switch,
    trigger_kill_switch,
)

class TestEvaluateStopLossStub:
    """验证 evaluate_stop_loss stub 正确抛出 NotImplementedError。"""

    @pytest.mark.financial
    def test_raises_not_implemented(self):
        position = {"symbol": "SSE:600000", "entry_price": 10.0, "quantity": 100}
        rules = {"max_loss_pct": 0.05}
        with pytest.raises(NotImplementedError, match="STUB"):
            evaluate_stop_loss(position, current_price=9.0, rules=rules)

class TestTriggerKillSwitchStub:
    """验证 trigger_kill_switch stub 正确抛出 NotImplementedError。"""

    @pytest.mark.security
    def test_raises_not_implemented(self):
        with pytest.raises(NotImplementedError, match="STUB"):
            trigger_kill_switch(reason="max drawdown exceeded")

class TestResetKillSwitchStub:
    """验证 reset_kill_switch stub 正确抛出 NotImplementedError。"""

    @pytest.mark.security
    def test_raises_not_implemented(self):
        confirmation = {"approved_by": "human", "timestamp": "2026-05-02T00:00:00Z"}
        with pytest.raises(NotImplementedError, match="STUB"):
            reset_kill_switch(confirmation)
