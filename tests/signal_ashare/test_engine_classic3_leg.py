# [BLUEPRINT] MOD-SIG-145 | tests/signal_ashare/test_engine_classic3_leg.py
# [MODULE] tests.signal_ashare.test_engine_classic3_leg
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
# [TESTS] pytest tests/signal_ashare/test_engine_classic3_leg.py
# [TTL] permanent
"""引擎 classic3 腿单测（P2-b）——三角形/矩形/楔形的边界与突破确认。"""

from __future__ import annotations

from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import (
    PatternEngineConfig,
    UnifiedPatternEngine,
)


def _ramp(seq: list[float], a: float, b: float, n: int) -> None:
    """从 a 到 b 插入 n 根线性爬升（不含 b 本身）。"""
    step = (b - a) / (n + 1)
    for i in range(1, n + 1):
        seq.append(round(a + step * i, 3))


def _cfg() -> PatternEngineConfig:
    return PatternEngineConfig(swing_window=2, double_extreme_min_gap=4)


def _ascending_triangle_path() -> list[float]:
    """水平上沿 10.20/10.22 + 低点抬升 9.60→10.05 → 上破。"""
    seq: list[float] = [9.0]
    _ramp(seq, 9.0, 10.20, 5)
    seq.append(10.20)                 # 顶1
    seq += [10.18]
    _ramp(seq, 10.18, 9.60, 4)
    seq.append(9.60)                  # 谷1
    seq += [9.62]
    _ramp(seq, 9.62, 10.22, 6)
    seq.append(10.22)                 # 顶2
    seq += [10.20]
    _ramp(seq, 10.20, 10.05, 4)
    seq.append(10.05)                 # 谷2（抬升）
    seq += [10.06]
    _ramp(seq, 10.06, 10.35, 4)       # 上破 10.22*1.005≈10.27
    return seq


def test_ascending_triangle_breakout_up():
    closes = _ascending_triangle_path()
    engine = UnifiedPatternEngine(_cfg())
    res = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    hits = [e for e in res.events if e.name == "上升三角形"]
    assert hits, "上升三角形未检出"
    assert hits[0].direction.value == "向上"


def test_descending_triangle_breakout_down():
    closes = [round(12.0 - x + 9.0, 3) for x in _ascending_triangle_path()]
    engine = UnifiedPatternEngine(_cfg())
    res = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    hits = [e for e in res.events if e.name == "下降三角形"]
    assert hits, "下降三角形未检出"
    assert hits[0].direction.value == "向下"


def test_rectangle_both_breakouts():
    # 上沿 10.2 平、下沿 9.6 平（两轮），末段先上破
    seq: list[float] = [9.0]
    _ramp(seq, 9.0, 10.20, 5)
    seq += [10.20, 10.19]
    _ramp(seq, 10.19, 9.60, 4)
    seq += [9.60, 9.61]
    _ramp(seq, 9.61, 10.20, 6)
    seq += [10.20, 10.19]
    _ramp(seq, 10.19, 9.62, 4)
    seq += [9.62, 9.63]
    _ramp(seq, 9.63, 9.64, 2)
    _ramp(seq, 9.64, 9.62, 2)
    seq += [9.61, 9.55]              # 下破 9.60*0.995≈9.55
    engine = UnifiedPatternEngine(_cfg())
    res = engine.recognize("TEST", list(seq), list(seq), list(seq), timeframe="day")
    hits = [e for e in res.events if e.name == "矩形箱体"]
    assert hits, "矩形箱体未检出"
    assert hits[0].direction.value == "向下"


def test_classic3_disabled_no_events():
    closes = _ascending_triangle_path()
    engine = UnifiedPatternEngine(PatternEngineConfig(swing_window=2, double_extreme_min_gap=4, enable_classic3=False))
    res = engine.recognize("TEST", list(closes), list(closes), list(closes), timeframe="day")
    assert all(e.name not in ("上升三角形", "下降三角形", "对称三角形", "矩形箱体", "上升楔形", "下降楔形") for e in res.events)
