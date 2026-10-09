# [BLUEPRINT] MOD-BT-155 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_mine_numerics
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.factor.technical_indicators.trend
# [CONSUMERS] MOD-BT-155 lane_c_formula_miner E1 夜修数值回归（红绿证据=docs/_working/lane_c_chain_night_20261001/e1_mine_repair.md）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 CH：纯数值回归；断层序列为合成数据（真实形态 44→12.6 单日 -71%）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-155 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""E1 车道C 夜修（2026-10-01）数值回归——MCGINLEY 断层自愈。

病根：价格单日大跌 >3.5 倍（44→12.6）后 prev 转负，钳位分支 max(ratio**4, 1e-12)
成为指数放大器（|prev| 每轮 ×~1e11），约 29 个交易日后 float64 上溢产出 Inf 写入 md_14。
修复：递推前 prev 非有限或 ≤0 → 重置播种 prev=c[i]（与 NaN 播种同语义）；输出前非有限→NaN 终防护。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.trend import MCGINLEY


def _gap_close() -> np.ndarray:
    """真实断层形态：44 → 12.6 单日 -71%，断后正常波动 40 个交易日。"""
    rng = np.random.default_rng(42)
    tail = 12.75 * np.cumprod(1.0 + rng.normal(0.0, 0.02, 40))
    return np.concatenate([[44.0, 44.45, 43.98, 12.6], tail])


def _frame(close: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame({"close": close}, index=pd.bdate_range("2026-01-05", periods=len(close)))


class TestMcGinleyGapSelfHeal:
    """断层=基期失效，重置播种是 McGinley 递推的标准自愈。"""

    def test_gap_sequence_all_finite(self):
        md = MCGINLEY().compute(_frame(_gap_close()))["md_14"].to_numpy()
        assert np.isfinite(md).all()  # 修复前红：断层后 i=4→1.6e8、i=5→-1.9e19、i=32 起 overflow 产出 Inf/NaN

    def test_gap_sequence_reseeds_to_price_scale(self):
        close = _gap_close()
        md = MCGINLEY().compute(_frame(close))["md_14"].to_numpy()
        # 断层 bar 次日起重置播种：md 回到价格量纲（旧逻辑此处 1e8→1e19→Inf 怪物值）
        assert (md[4:] > 0).all()
        assert (md[4:] < 100.0).all()


class TestMcGinleyRegression:
    """常规序列回归（与 tests/zephyr/factor/technical_indicators/test_trend.py::TestMcGinleyNumeric 同语义，零 talib 依赖）。"""

    def test_constant_price_constant_line(self):
        md = MCGINLEY().compute(_frame(np.full(40, 100.0)))["md_14"].to_numpy()
        assert (md == 100.0).all()

    def test_uptrend_lags_behind_close(self):
        close = np.linspace(100.0, 160.0, 60)
        md = MCGINLEY().compute(_frame(close))["md_14"].to_numpy()
        assert np.isfinite(md).all()
        assert (md[1:] < close[1:]).all()  # 首行 md=C，其余在价格下方


if __name__ == "__main__":  # pragma: no cover
    import pytest

    pytest.main([__file__, "-v"])
