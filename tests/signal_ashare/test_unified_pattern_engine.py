# [A_test] module_id: MOD-SIG-091 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-091 | docs/03_modules/_domain_signal/unified_pattern_engine/blueprint.md
# [MODULE] tests.signal_ashare.test_unified_pattern_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""统一图形识别引擎（MOD-SIG-091，B1-01010）施工验证测试。

覆盖：
- 统一契约：PatternEvent 六类封闭集/关键点位/方向/历史胜率注入；
- 规则腿：双顶/双底反转、平台突破持续、支撑阻力（收编 MOD-SIG-069）、
  缠论（收编 MOD-SIG-072）事件产出；
- DTW 模板匹配：命中产出、距离越界不产出、置信度随距离递减；
- 去重与排序：同 (name, anchor) 单事件、置信度降序；
- fail-closed：不等长/空输入/非正价；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.unified_pattern_engine import (
    PatternClass,
    PatternDirection,
    PatternEngineConfig,
    PatternTemplate,
    UnifiedPatternEngine,
)


def _mk(ohlc: list[float], spread: float = 0.05):
    closes = list(ohlc)
    highs = [c + spread for c in closes]
    lows = [c - spread for c in closes]
    return highs, lows, closes


def _double_top():
    # 上涨→顶11→回落10.4→再顶11.01→回落
    closes = (
        [10.0 + 0.1 * i for i in range(10)]          # 升至 10.9
        + [11.0, 10.7, 10.5, 10.4, 10.5, 10.7]        # 顶1 + 谷
        + [10.9, 11.01, 10.8, 10.6, 10.4, 10.3]       # 顶2 + 回落
    )
    return _mk(closes)


def _double_bottom():
    closes = (
        [11.0 - 0.1 * i for i in range(10)]
        + [10.0, 10.3, 10.5, 10.6, 10.5, 10.3]
        + [10.1, 9.99, 10.2, 10.4, 10.6, 10.7]
    )
    return _mk(closes)


def _consolidation_breakout():
    closes = [10.0 + (0.05 if i % 2 else -0.05) for i in range(30)] + [10.8]
    return _mk(closes)


def _swing_support():
    # 三次下探 9.5 附近 → 支撑位
    closes = []
    for k in range(3):
        closes += [10.5, 10.2, 9.95, 9.5 + 0.03 * k, 9.95, 10.2]
    closes += [10.5, 10.6]
    return _mk(closes, spread=0.02)


def _zigzag(n: int = 48):
    closes = []
    c, d = 10.0, 0.25
    for i in range(n):
        c += d
        closes.append(c)
        if i % 6 == 5:
            d = -d
    return _mk(closes, spread=0.02)


def _cfg(**kw) -> PatternEngineConfig:
    base = {"chanlun_min_bi_bars": 3}
    base.update(kw)
    return PatternEngineConfig(**base)


class TestContract:
    def test_six_classes_closed_set(self) -> None:
        assert len(PatternClass) == 6

    def test_invalid_input_fail_closed(self) -> None:
        eng = UnifiedPatternEngine(_cfg())
        h, l, c = _double_top()
        with pytest.raises(ValueError):
            eng.recognize("X", h, l, c[:-1])  # 不等长
        with pytest.raises(ValueError):
            eng.recognize("X", [], [], [])  # 空
        bad_h, bad_l, bad_c = _mk([10.0, -1.0, 10.0])
        with pytest.raises(ValueError):
            eng.recognize("X", bad_h, bad_l, bad_c)  # 非正价

    def test_empty_symbol_rejected(self) -> None:
        h, l, c = _double_top()
        with pytest.raises(ValueError):
            UnifiedPatternEngine(_cfg()).recognize("", h, l, c)


class TestClassicLeg:
    def test_double_top(self) -> None:
        h, l, c = _double_top()
        rep = UnifiedPatternEngine(_cfg(enable_chanlun=False, enable_sr=False, enable_dtw=False)).recognize("600000.SH", h, l, c)
        tops = [e for e in rep.events if e.name == "双顶"]
        assert tops, f"未识别双顶: {[e.name for e in rep.events]}"
        assert tops[0].pattern_class is PatternClass.REVERSAL
        assert tops[0].direction is PatternDirection.DOWN
        assert len(tops[0].key_points) >= 2

    def test_double_bottom(self) -> None:
        h, l, c = _double_bottom()
        rep = UnifiedPatternEngine(_cfg(enable_chanlun=False, enable_sr=False, enable_dtw=False)).recognize("600000.SH", h, l, c)
        bots = [e for e in rep.events if e.name == "双底"]
        assert bots
        assert bots[0].direction is PatternDirection.UP

    def test_consolidation_breakout(self) -> None:
        h, l, c = _consolidation_breakout()
        rep = UnifiedPatternEngine(_cfg(enable_chanlun=False, enable_sr=False, enable_dtw=False)).recognize("600000.SH", h, l, c)
        brk = [e for e in rep.events if e.name == "平台突破"]
        assert brk
        assert brk[0].pattern_class is PatternClass.CONTINUATION
        assert brk[0].direction is PatternDirection.UP


class TestIncorporatedLegs:
    def test_sr_leg_support_event(self) -> None:
        h, l, c = _swing_support()
        rep = UnifiedPatternEngine(_cfg(enable_chanlun=False, enable_classic=False, enable_dtw=False)).recognize("600000.SH", h, l, c)
        sr = [e for e in rep.events if e.pattern_class is PatternClass.SR]
        assert sr, f"未产出支撑阻力事件: {[e.name for e in rep.events]}"

    def test_chanlun_leg_bi_event(self) -> None:
        h, l, c = _zigzag()
        rep = UnifiedPatternEngine(_cfg(enable_sr=False, enable_classic=False, enable_dtw=False)).recognize("600000.SH", h, l, c)
        cll = [e for e in rep.events if e.pattern_class is PatternClass.CHANLUN]
        assert cll, f"未产出缠论事件: {[e.name for e in rep.events]}"


class TestDtwLeg:
    def test_template_hit(self) -> None:
        h, l, c = _zigzag(30)
        tail = c[-15:]
        lo, hi = min(tail), max(tail)
        norm = [(x - lo) / (hi - lo) for x in tail]
        tpl = PatternTemplate(
            name="测试楔形",
            series=tuple(norm),
            pattern_class=PatternClass.CONTINUATION,
            direction=PatternDirection.UP,
        )
        eng = UnifiedPatternEngine(
            _cfg(enable_chanlun=False, enable_sr=False, enable_classic=False),
            templates=(tpl,),
        )
        rep = eng.recognize("600000.SH", h, l, c)
        hits = [e for e in rep.events if e.name.startswith("DTW模板")]
        assert hits
        assert hits[0].confidence == pytest.approx(1.0, abs=1e-6)

    def test_template_miss_no_event(self) -> None:
        h, l, c = _zigzag(30)
        tpl = PatternTemplate(
            name="反向模板",
            series=tuple([0.0, 1.0] * 8),
            pattern_class=PatternClass.REVERSAL,
            direction=PatternDirection.DOWN,
        )
        eng = UnifiedPatternEngine(
            _cfg(enable_chanlun=False, enable_sr=False, enable_classic=False),
            templates=(tpl,),
        )
        rep = eng.recognize("600000.SH", h, l, c)
        assert not [e for e in rep.events if e.name.startswith("DTW模板")]


class TestDedupSortWinrate:
    def test_dedup_and_sorted(self) -> None:
        h, l, c = _double_top()
        rep = UnifiedPatternEngine(_cfg()).recognize("600000.SH", h, l, c)
        keys = [(e.name, e.anchor_idx) for e in rep.events]
        assert len(keys) == len(set(keys))
        confs = [e.confidence for e in rep.events]
        assert confs == sorted(confs, reverse=True)

    def test_win_rate_injected(self) -> None:
        h, l, c = _double_top()
        eng = UnifiedPatternEngine(
            _cfg(enable_chanlun=False, enable_sr=False, enable_dtw=False),
            win_rate_provider=lambda name: 0.62 if name == "双顶" else None,
        )
        rep = eng.recognize("600000.SH", h, l, c)
        tops = [e for e in rep.events if e.name == "双顶"]
        assert tops and tops[0].historical_win_rate == pytest.approx(0.62)


class TestSerialization:
    def test_frozen_and_json(self) -> None:
        h, l, c = _double_top()
        rep = UnifiedPatternEngine(_cfg()).recognize("600000.SH", h, l, c)
        assert rep.events
        with pytest.raises(dataclasses.FrozenInstanceError):
            rep.events[0].confidence = 0.0  # type: ignore[misc]
        json.dumps(rep.to_dict(), ensure_ascii=False)
