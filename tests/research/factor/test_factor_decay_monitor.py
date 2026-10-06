# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""D-FACTOR-ANA-08 衰减监控测试——纯函数模块（无 IO 依赖）。

覆盖：
- monitor_decay: 数据不足 / 半衰期长=正常 / 半衰期短=衰减 / 传入预计算 series / trend 描述
"""

from __future__ import annotations

import pandas as pd
import pytest

decay_monitor = pytest.importorskip("zephyr.factor.analysis.decay_monitor")

monitor_decay = decay_monitor.monitor_decay
DecayStatus = decay_monitor.DecayStatus


class TestMonitorDecay:
    def test_insufficient_data_returns_decaying(self):
        # 不传 ic_decay_series 且缺 symbols/start/end → 数据不足
        status = monitor_decay("factor_x")
        assert isinstance(status, DecayStatus)
        assert status.factor_id == "factor_x"
        assert status.half_life == 0.0
        assert status.is_decaying is True
        assert status.trend == "数据不足"

    def test_insufficient_partial_args(self):
        # 只传 symbols 不传 start/end → 数据不足
        status = monitor_decay("factor_y", symbols=["000001"])
        assert status.half_life == 0.0
        assert status.is_decaying is True
        assert status.trend == "数据不足"

    def test_long_half_life_normal(self):
        # IC 衰减慢——所有 lag 都保持高 IC，半衰期 = 最大 lag = 20 >= 10 → 正常
        ic_decay = pd.Series([0.1] * 20, index=range(1, 21), name="ic_decay")
        status = monitor_decay("factor_long", ic_decay_series=ic_decay)
        assert status.factor_id == "factor_long"
        assert status.half_life == 20.0
        assert status.is_decaying is False
        assert "衰减正常" in status.trend

    def test_short_half_life_decaying(self):
        # IC 从 0.1 快速降到 0.01，半衰期约 1.83 < 10 → 衰减
        ic_decay = pd.Series([0.1, 0.04, 0.01], index=[1, 2, 3], name="ic_decay")
        status = monitor_decay("factor_short", ic_decay_series=ic_decay)
        assert status.factor_id == "factor_short"
        assert status.half_life < 10.0
        assert status.is_decaying is True
        assert "衰减过快" in status.trend

    def test_precomputed_series_used(self):
        # 传入预计算 series，跳过 symbols/start/end 路径
        ic_decay = pd.Series([0.2] * 15, index=range(1, 16), name="ic_decay")
        status = monitor_decay("factor_pre", ic_decay_series=ic_decay)
        # 半衰期 = 15 >= 10 → 正常
        assert status.half_life == 15.0
        assert status.is_decaying is False

    def test_trend_description_normal(self):
        ic_decay = pd.Series([0.1] * 20, index=range(1, 21), name="ic_decay")
        status = monitor_decay("f", ic_decay_series=ic_decay)
        # 格式: 衰减正常（半衰期 20.0 >= 10）
        assert status.trend == "衰减正常（半衰期 20.0 >= 10）"

    def test_trend_description_decaying(self):
        # 半衰期 1.833... → 趋势字符串包含 1.8
        ic_decay = pd.Series([0.1, 0.04, 0.01], index=[1, 2, 3], name="ic_decay")
        status = monitor_decay("f", ic_decay_series=ic_decay)
        assert status.trend.startswith("衰减过快（半衰期 1.8 < 10）")

    def test_decaying_status_is_dataclass(self):
        status = monitor_decay("f")
        # frozen dataclass——字段可读不可变
        assert hasattr(status, "factor_id")
        assert hasattr(status, "half_life")
        assert hasattr(status, "is_decaying")
        assert hasattr(status, "trend")

    def test_threshold_boundary(self):
        # 半衰期正好 = 10（min_half_life）→ is_decaying=False（< 10 才衰减）
        # 构造 ic_decay 使半衰期恰好 10
        ic_decay = pd.Series([0.1] * 10, index=range(1, 11), name="ic_decay")
        status = monitor_decay("f", ic_decay_series=ic_decay)
        # IC 全程 0.1，未衰减到一半 → 半衰期 = 最大 lag = 10
        assert status.half_life == 10.0
        assert status.is_decaying is False  # 10 < 10 为 False
