# [BLUEPRINT] MOD-BT-089 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_lane_e_enhanced
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; sklearn; scripts.backtest.lane_e_enhanced
# [CONSUMERS] lane_e_enhanced 质量守卫（增强件补齐批 2026-09-16：原会话只交主件未交测试，本件补齐消除头注 [TESTS] 漂移）
# [STARTUP] manual
# [INVARIANTS] 合成数据测试（不连 CH、零生产 IO）；断言结构不变量（特征列齐/覆盖率∈[0,1]/预测数>0）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-089 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道 E 增强件（LightGBM/GBR/线性 QR 对比）质量守卫——特征工程+滚动前推实验冒烟。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys_path = str(Path(__file__).resolve().parents[2] / "scripts" / "backtest")
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from lane_e_enhanced import _load_features, run_experiment  # noqa: E402


class _SyntheticEngine:
    """合成行情引擎：随机游走 close + 随机涨跌家数（load_index 契约桩，零 CH 依赖）。"""

    def load_index(self, symbol, start, end, fields):
        rng = np.random.default_rng(42)
        n = 220
        idx = pd.date_range("2025-01-01", periods=n, freq="B")
        close = 4000.0 + np.cumsum(rng.normal(0, 20, n))
        adv = rng.integers(1000, 3000, n)
        dec = rng.integers(1000, 3000, n)
        return pd.DataFrame(
            {"close": close, "advance_count": adv, "decline_count": dec}, index=idx
        )


def test_load_features_columns_and_nonempty():
    f = _load_features(_SyntheticEngine(), "2025-01-01", "2025-12-31")
    assert not f.empty
    for col in ("ret", "lag_1", "lag_20", "vol_5", "vol_20", "breadth", "ret_fwd"):
        assert col in f.columns
    # PIT 不变量抽样：dropna 后帧内 lag_1[i] == ret[i-1]（特征只用 ≤T-1 信息）
    np.testing.assert_allclose(f["lag_1"].values[1:], f["ret"].values[:-1])


def test_run_experiment_linear_smoke():
    res = run_experiment(_SyntheticEngine(), "2025-01-01", "2025-12-31", ["linear"], train_window=80)
    m = res["models"]["linear"]
    assert m["n_preds"] > 0
    assert 0.0 <= m["coverage_inside"] <= 1.0
    assert m["interval_mean_width"] >= 0.0
