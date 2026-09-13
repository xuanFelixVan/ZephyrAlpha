# [BLUEPRINT] MOD-SIG-145 | tests/signal_ashare/test_engine_classic2_leg.py
# [MODULE] tests.signal_ashare.test_engine_classic2_leg
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.unified_pattern_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 合成价格路径，禁触 CH/生产路径
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/test_engine_classic2_leg.py
# [TTL] permanent
"""引擎 classic2 腿单测（P2-b）——头肩顶/底、三重顶/底的检测与颈线确认。"""

from __future__ import annotations

from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import (
    PatternEngineConfig,
    UnifiedPatternEngine,
)


def _ramp(values: list[float]) -> list[float]:
    """线性爬升序列（不含端点，用于拼接）。"""
    return values


def _hs_top_path() -> list[float]:
    """上升→左肩10.20→谷9.70→头10.80→谷9.75→右肩10.25→破颈线9.65。"""
    closes: list[float] = [9.20]
    def ramp(a, b, n):
        step = (b - a) / (n + 1)
        return [round(a + step * (i + 1), 3) for i in range(n)]

    closes += ramp(9.20, 10.20, 6)          # 升至左肩
    closes += [10.20, 10.18]                # 左肩平台（形成摆动高点）
    closes += ramp(10.18, 9.70, 4)          # 回落至谷1
    closes += [9.70, 9.71]
    closes += ramp(9.71, 10.80, 6)          # 升至头
    closes += [10.80, 10.78]
    closes += ramp(10.78, 9.75, 4)          # 回落至谷2
    closes += [9.75, 9.76]
    closes += ramp(9.76, 10.25, 6)          # 升至右肩
    closes += [10.25, 10.23]
    closes += ramp(10.23, 9.55, 6)          # 跌破颈线（9.70）
    return closes


def test_head_and_shoulders_top_detected():
    closes = _hs_top_path()
    engine = UnifiedPatternEngine(
        PatternEngineConfig(swing_window=2, double_extreme_min_gap=4)
    )
    n = len(closes)
    result = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    hs = [e for e in result.events if e.name == "头肩顶"]
    assert hs, "头肩顶未检出"
    ev = hs[0]
    assert ev.direction.value == "向下"
    assert ev.anchor_idx < n
    roles = {kp.role for kp in ev.key_points}
    assert {"左肩", "头", "右肩", "颈线破位"} <= roles


def test_head_and_shoulders_bottom_mirror():
    closes = [round(12.0 - x + 9.2, 3) for x in _hs_top_path()]  # 镜像翻转
    engine = UnifiedPatternEngine(
        PatternEngineConfig(swing_window=2, double_extreme_min_gap=4)
    )
    result = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    hs = [e for e in result.events if e.name == "头肩底"]
    assert hs, "头肩底未检出"
    assert hs[0].direction.value == "向上"


def _triple_top_path() -> list[float]:
    """平台三峰 10.2 等高，两谷 9.7，末段破颈线。"""
    closes: list[float] = [9.20]
    def ramp(a, b, n):
        step = (b - a) / (n + 1)
        return [round(a + step * (i + 1), 3) for i in range(n)]

    closes += ramp(9.20, 10.20, 6)
    closes += [10.20, 10.19]
    closes += ramp(10.19, 9.70, 4) + [9.70, 9.71]
    closes += ramp(9.71, 10.20, 6) + [10.20, 10.19]
    closes += ramp(10.19, 9.70, 4) + [9.70, 9.71]
    closes += ramp(9.71, 10.20, 6) + [10.20, 10.19]
    closes += ramp(10.19, 9.55, 6)  # 破颈线
    return closes


def test_triple_top_detected():
    closes = _triple_top_path()
    engine = UnifiedPatternEngine(
        PatternEngineConfig(swing_window=2, double_extreme_min_gap=4)
    )
    result = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    tt = [e for e in result.events if e.name == "三重顶"]
    assert tt, "三重顶未检出"
    assert tt[0].direction.value == "向下"


def test_classic2_disabled_no_events():
    closes = _hs_top_path()
    engine = UnifiedPatternEngine(
        PatternEngineConfig(swing_window=2, double_extreme_min_gap=4, enable_classic2=False)
    )
    result = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    assert all(e.name not in ("头肩顶", "头肩底", "三重顶", "三重底") for e in result.events)
