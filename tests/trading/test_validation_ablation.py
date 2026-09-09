# [BLUEPRINT] MOD-TDMVAL-001 | docs/03_modules/_domain_trading/validation/blueprint.md
# [A_module] module_id=MOD-TDMVAL-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-TDMVAL-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.test_validation_ablation
# [DOMAIN] D_TRADING
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/trading/test_validation_ablation.py
# [TTL] permanent
"""T2 信号消融对照器单测（X 流验证批）。

覆盖（Owner 指令 T2 验收两条）:
  - 合成数据下双净值差正确性（同面板连跑两支 run rescued≡0；剥离清仓后差额非零）。
  - 空剥越（无风控动作时对照=全量）。
外加: 剥算子纯函数语义（保 Σw=1/回滚式分摊/非法动作拒绝）、AblationReport 契约。
纯内存合成数据，不触网不触库不连 CH。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.trading.validation.ablation import (
    AblationReport,
    ValidationError,
    XFlowAction,
    ablate_weight_panel,
    run_ablation,
    sell_signals_to_xflow_actions,
)


# ── 合成夹具 ─────────────────────────────────────────────────────────────

@pytest.fixture()
def panel() -> pd.DataFrame:
    idx = pd.date_range("2026-01-05", periods=6, freq="B")
    return pd.DataFrame(
        {"AAA": [0.5] * 6, "BBB": [0.3] * 6, "CCC": [0.2] * 6},
        index=idx,
    )


@pytest.fixture()
def data() -> pd.DataFrame:
    rows = []
    rng = pd.date_range("2026-01-05", periods=6, freq="B")
    for i, d in enumerate(rng):
        for sym, base in (("AAA", 10.0), ("BBB", 20.0), ("CCC", 5.0)):
            rows.append({"date": d, "symbol": sym, "close": base + i * 0.1, "volume": 100000})
    return pd.DataFrame(rows)


# ── 剥算子纯函数 ─────────────────────────────────────────────────────────

def test_ablate_no_actions_identity(panel: pd.DataFrame):
    """空剥越: 无动作时输出与输入恒等（对照=全量）。"""
    out = ablate_weight_panel(panel, [])
    pd.testing.assert_frame_equal(out, panel)


def test_ablate_clear_rolls_back_and_keeps_sum(panel: pd.DataFrame):
    """clear 回滚: 被清标的归零、缺口按比例分摊、Σw==1 保持。"""
    d = panel.index[2]
    out = ablate_weight_panel(panel, [XFlowAction(date=d, symbol="CCC", action="clear", source="TDM-X-S1-02")])
    row = out.loc[d]
    assert row["CCC"] == 0.0
    assert abs(row["AAA"] - 0.625) < 1e-9   # 0.5/(0.8) 分摊
    assert abs(row["BBB"] - 0.375) < 1e-9
    assert abs(out.loc[d].sum() - 1.0) < 1e-9
    # 其他日不受影响
    pd.testing.assert_series_equal(out.loc[panel.index[0]], panel.loc[panel.index[0]])


def test_ablate_reduce_partial(panel: pd.DataFrame):
    """reduce: 权重削减至 reduce_to，削减份额分摊给其余标的。"""
    d = panel.index[1]
    out = ablate_weight_panel(panel, [XFlowAction(date=d, symbol="BBB", action="reduce", reduce_to=0.1)])
    row = out.loc[d]
    assert abs(row["BBB"] - 0.1) < 1e-9
    assert abs(out.loc[d].sum() - 1.0) < 1e-9
    assert row["AAA"] > panel.loc[d, "AAA"]   # 分摊方向


def test_ablate_reduce_to_above_current_ignored(panel: pd.DataFrame):
    """reduce_to >= 现权重=非减仓动作，忽略。"""
    d = panel.index[0]
    out = ablate_weight_panel(panel, [XFlowAction(date=d, symbol="AAA", action="reduce", reduce_to=0.9)])
    pd.testing.assert_frame_equal(out, panel)


def test_ablate_invalid_actions_rejected(panel: pd.DataFrame):
    """非法动作/越界 reduce_to 拒绝。"""
    d = panel.index[0]
    with pytest.raises(ValidationError):
        ablate_weight_panel(panel, [XFlowAction(date=d, symbol="AAA", action="buy")])
    with pytest.raises(ValidationError):
        ablate_weight_panel(panel, [XFlowAction(date=d, symbol="AAA", action="reduce", reduce_to=None)])
    with pytest.raises(ValidationError):
        ablate_weight_panel(pd.DataFrame(), [])


def test_ablate_action_off_panel_ignored(panel: pd.DataFrame):
    """日期/标的不在面板的动作忽略（告警不炸）。"""
    out = ablate_weight_panel(panel, [XFlowAction(date="1999-01-01", symbol="ZZZ", action="clear")])
    pd.testing.assert_frame_equal(out, panel)


# ── 端到端（引擎零改动重放）────────────────────────────────────────────

def test_run_ablation_identical_panels_zero_rescued(data: pd.DataFrame, panel: pd.DataFrame):
    """幂等基线: 同一面板连跑两支 run（引擎每次 run 新建 Portfolio），差额恒 0。"""
    report = run_ablation(data=data, panel_full=panel, actions=[])
    assert isinstance(report, AblationReport)
    assert len(report.rescued) == len(panel.index)
    assert float(np.abs(report.rescued).max()) < 1e-6
    assert report.rescued_total == pytest.approx(0.0, abs=1e-6)
    assert report.result_full.map_snapshot   # 快照绑定自动带上


def test_run_ablation_clear_action_changes_nav(data: pd.DataFrame, panel: pd.DataFrame):
    """剥离清仓后净值路径改变，rescued 序列有限值（方向不预设——二阶效应披露）。"""
    d = panel.index[2]
    actions = [XFlowAction(date=d, symbol="CCC", action="clear", source="TDM-X-S1-02")]
    report = run_ablation(data=data, panel_full=panel, actions=actions)
    assert len(report.rescued) == len(panel.index)
    assert np.isfinite(report.rescued).all()
    assert report.rescued_total == round(float(report.rescued.iloc[-1]), 2)
    assert len(report.actions) == 1
    assert "二阶效应" in report.notes


def test_run_ablation_empty_panel_rejected(data: pd.DataFrame):
    with pytest.raises(ValidationError):
        run_ablation(data=data, panel_full=pd.DataFrame(), actions=[])

# ── SellSignal→XFlowAction 转换助手（遗留③）──────────────────────────────

class TestSellSignalsToXFlowActions:
    """sell_decision.SellSignal → XFlowAction 映射（真实 SellSignal dataclass 构造）。"""

    def _sig(self, symbol="000001.SZ", direction="CLEAR", confidence=0.8, source="TDM-X-S1-02", ts="2026-01-06"):
        from zephyr.sell_decision.core.sell_signal_collector import (
            SellDirection,
            SellSignal,
            SellSignalType,
        )

        return SellSignal(
            symbol=symbol,
            signal_type=SellSignalType.TECHNICAL,
            direction=SellDirection(direction),
            confidence=confidence,
            source=source,
            metadata={"reason": "test"},
            timestamp=ts,
        )

    def test_clear_maps_to_clear(self):
        actions = sell_signals_to_xflow_actions([self._sig(direction="CLEAR")])
        assert len(actions) == 1
        a = actions[0]
        assert a.symbol == "000001.SZ" and a.action == "clear"
        assert a.source == "TDM-X-S1-02" and str(a.date) == "2026-01-06"

    def test_reduce_maps_with_confidence(self):
        actions = sell_signals_to_xflow_actions([self._sig(direction="REDUCE", confidence=0.6)])
        assert len(actions) == 1
        a = actions[0]
        assert a.action == "reduce"
        assert a.reduce_to == pytest.approx(0.4)   # 1.0 - confidence

    def test_reduce_zero_confidence_skipped(self):
        """conf<=0 的 REDUCE 保守忽略（不产动作）。"""
        assert sell_signals_to_xflow_actions([self._sig(direction="REDUCE", confidence=0.0)]) == []

    def test_replace_maps_to_clear(self):
        """REPLACE=先清仓（v1 无建仓动作位）。"""
        actions = sell_signals_to_xflow_actions([self._sig(direction="REPLACE")])
        assert len(actions) == 1 and actions[0].action == "clear"

    def test_source_fallback_default(self):
        """source 空 → 默认 TDM-X-S1。"""
        actions = sell_signals_to_xflow_actions([self._sig(source="")])
        assert actions[0].source == "TDM-X-S1"

    def test_missing_symbol_or_ts_rejected(self):
        """防御层：字段被外部破坏（绕过 SellSignal 构造期校验）时转换器拒绝。"""
        import dataclasses

        s1 = dataclasses.replace(self._sig())
        object.__setattr__(s1, "symbol", "")
        with pytest.raises(ValidationError):
            sell_signals_to_xflow_actions([s1])
        s2 = dataclasses.replace(self._sig())
        object.__setattr__(s2, "timestamp", None)
        with pytest.raises(ValidationError):
            sell_signals_to_xflow_actions([s2])

    def test_end_to_end_with_ablate(self):
        """转换产物直接可喂 ablate_weight_panel（接口贯通）。"""
        panel = pd.DataFrame(
            {"AAA": [0.5, 0.5], "BBB": [0.3, 0.3], "CCC": [0.2, 0.2]},
            index=pd.date_range("2026-01-05", periods=2, freq="B"),
        )
        sigs = [self._sig(symbol="CCC", direction="CLEAR", ts=str(panel.index[1].date()))]
        actions = sell_signals_to_xflow_actions(sigs)
        out = ablate_weight_panel(panel, actions)
        assert out.loc[panel.index[1], "CCC"] == 0.0
        assert abs(out.loc[panel.index[1]].sum() - 1.0) < 1e-9
