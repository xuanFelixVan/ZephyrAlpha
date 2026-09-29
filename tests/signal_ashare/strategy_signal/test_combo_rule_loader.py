# [BLUEPRINT] MOD-SIG-147 | 待统筹登记（supplement：组合规则卡加载/匹配单测）
# [MODULE] tests.signal_ashare.strategy_signal.test_combo_rule_loader
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.combo_rule_loader, zephyr.signal_ashare.strategy_signal.unified_pattern_engine
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] tmp_path fixture 零写生产盘；fail-closed 全覆盖；引擎装配端到端一例
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=组合规则卡加载/匹配/装配缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-147_combo_rule_loader_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""组合规则 YAML 卡单测：load/validate fail-closed、match 三要素匹配、引擎端到端装配。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.strategy_signal import combo_rule_loader as crl
from zephyr.signal_ashare.strategy_signal.combo_rule_loader import ComboRule, load, match, validate
from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import UnifiedPatternEngine
from zephyr.signal_ashare.trendline_sr_detector import SRBar

_YAML = """
ttl: permanent
schema_version: "1.0"
rules:
  - rule_id: r_support
    pattern_id: "双底"
    sr_side: "support"
    sr_proximity_pct_max: 2.0
    volume_ratio_min: 1.2
    direction: "向上"
    strength_delta: 0.1
    enabled: true
  - rule_id: r_resist
    pattern_id: "双顶"
    sr_side: "resistance"
    sr_proximity_pct_max: 1.0
    volume_ratio_min: 0.0
    direction: "向下"
    strength_delta: 0.2
    enabled: false
"""


class _Ev:
    """duck 型事件（只暴露 loader 读的两个字段）。"""

    def __init__(self, pattern_id: str, name: str = "") -> None:
        self.pattern_id = pattern_id
        self.name = name


def _rules() -> tuple[ComboRule, ...]:
    return (
        ComboRule("r1", "CDLENGULFING", "support", 2.0, 1.2, "向上", 0.1),
        ComboRule("r2", "CDLSHOOTINGSTAR", "resistance", 1.5, 0.0, "向下", 0.2, enabled=False),
    )


def test_load_valid(tmp_path) -> None:
    p = tmp_path / "combo.yaml"
    p.write_text(_YAML, encoding="utf-8")
    rules = load(str(p))
    assert len(rules) == 2
    assert rules[0].rule_id == "r_support" and rules[0].enabled is True


def test_load_missing_file_fail_closed(tmp_path) -> None:
    with pytest.raises(ValueError, match="不可读"):
        load(str(tmp_path / "nope.yaml"))


def test_load_bad_structure_fail_closed(tmp_path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("rules: 42\n", encoding="utf-8")
    with pytest.raises(ValueError, match="结构非法"):
        load(str(p))


def test_validate_fail_closed() -> None:
    with pytest.raises(ValueError, match="sr_side"):
        validate((ComboRule("x", "p", "ward", 1.0, 0.0, "向上", 0.1),))
    with pytest.raises(ValueError, match="direction"):
        validate((ComboRule("x", "p", "any", 1.0, 0.0, "横盘", 0.1),))
    with pytest.raises(ValueError, match="非负"):
        validate((ComboRule("x", "p", "any", -1.0, 0.0, "向上", 0.1),))
    with pytest.raises(ValueError, match="重复"):
        validate(
            (
                ComboRule("d", "p", "any", 1.0, 0.0, "向上", 0.1),
                ComboRule("d", "p", "any", 1.0, 0.0, "向上", 0.1),
            )
        )


def test_match_support_proximity_and_volume_gate() -> None:
    events = [_Ev("CDLENGULFING", "看涨吞没")]
    # 支撑位 9.8，现价 10.0 → 近位 2.04% > 2.0 上限 → 量能条件都到不了
    hits = match(_rules(), events, [9.8], 10.0, volume_ratio=2.0)
    assert hits == ()
    # 支撑位 9.9 → 近位 1.01% ≤2.0，量能比 2.0 ≥1.2 → 命中
    hits = match(_rules(), events, [9.9], 10.0, volume_ratio=2.0)
    assert len(hits) == 1
    assert hits[0].rule_id == "r1" and hits[0].direction == "向上"
    # 量能不足 → 拒
    assert match(_rules(), events, [9.9], 10.0, volume_ratio=1.0) == ()
    # 量能 None=跳过量能条件 → 命中（SKIP 口径）
    assert len(match(_rules(), events, [9.9], 10.0, volume_ratio=None)) == 1


def test_match_disabled_and_side_filter() -> None:
    # r2 enabled=False 即使形态命中也不出
    events = [_Ev("CDLSHOOTINGSTAR")]
    assert match(_rules(), events, [10.2], 10.0, volume_ratio=None) == ()
    # resistance 侧过滤：水平位在现价下方时不作阻力判
    events2 = [_Ev("CDLENGULFING")]
    assert match((ComboRule("r3", "CDLENGULFING", "resistance", 5.0, 0.0, "向下", 0.1),), events2, [9.9], 10.0) == ()


def test_engine_assembly_end_to_end() -> None:
    """SR 腿水平位 × 组合规则 → 引擎输出含「组合:」事件（stats 计 combo）。"""
    bars = [
        SRBar("d1", 100.5, 98.0, 99.0),
        SRBar("d2", 99.0, 96.5, 97.0),
        SRBar("d3", 98.0, 95.0, 96.0),
        SRBar("d4", 100.0, 99.0, 99.5),
        SRBar("d5", 105.0, 99.5, 104.0),
        SRBar("d6", 104.0, 100.0, 101.0),
        SRBar("d7", 101.5, 98.0, 98.5),
        SRBar("d8", 99.0, 96.0, 97.0),
        SRBar("d9", 97.5, 95.2, 96.0),
        SRBar("d10", 100.0, 96.5, 99.5),
        SRBar("d11", 105.2, 99.0, 104.5),
        SRBar("d12", 104.0, 100.0, 101.0),
        SRBar("d13", 102.0, 99.0, 100.5),
    ]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    closes = [b.close for b in bars]
    rule = ComboRule("e2e", "支撑位", "any", 50.0, 0.0, "向上", 0.15)
    eng = UnifiedPatternEngine(combo_rules=(rule,))
    result = eng.recognize("TEST", highs, lows, closes)
    combo_events = [e for e in result.events if e.name.startswith("组合:")]
    assert len(combo_events) >= 1
    assert combo_events[0].direction.value == "向上"
    assert result.detector_stats.get("combo", 0) >= 1


def test_engine_rejects_bad_volumes() -> None:
    eng = UnifiedPatternEngine()
    with pytest.raises(ValueError, match="volumes 不等长"):
        eng.recognize("T", [1.0], [1.0], [1.0], volumes=[1.0, 2.0])
    with pytest.raises(ValueError, match="量须非负"):
        eng.recognize("T", [10.0], [9.0], [9.5], volumes=[-1.0])
