# [BLUEPRINT] MOD-BT-195 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_kronos_adapter
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas
# [CONSUMERS] MOD-BT-195 kronos_adapter 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 torch：合成 K 线验证 naive 分位/样本分位/日期去重；Kronos 真模型
#   不在单测（实驱走 CLI eval）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-195 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Kronos 适配器单测——naive 分位/样本分位/K 线去重/仓缺失 fail-closed，零网络零 torch。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


class TestNaiveQuantiles:
    def _kdf(self, n: int = 40):
        dates = list(pd.date_range("2026-01-01", periods=n).date)
        close = 100 + np.cumsum(np.random.default_rng(3).normal(0, 1, n))
        return pd.DataFrame({"date": dates, "close": close})

    def test_coverage_monotonic(self):
        from scripts.backtest.kronos_adapter import naive_quantiles

        kdf = self._kdf()
        dates = list(kdf["date"].iloc[-5:])
        q = naive_quantiles(kdf, dates, (0.05, 0.5, 0.95))
        for i in range(len(dates)):
            assert q[0.05][i] < q[0.5][i] < q[0.95][i]  # 分位单调

    def test_center_is_prev_close(self):
        from scripts.backtest.kronos_adapter import naive_quantiles

        kdf = self._kdf()
        d = list(kdf["date"].iloc[-1:])[0]
        q = naive_quantiles(kdf, [d], (0.5,))
        # 随机游走中位=上一日收盘（hist 不含当日——PIT 无前视）
        assert q[0.5][0] == pytest.approx(float(kdf["close"].iloc[-2]))


class TestKlineDedup:
    def test_fetch_kline_dedups_dates(self, monkeypatch):
        # 重复日期行（真实数据出现过）→ keep=last
        import scripts.backtest.kronos_adapter as ka

        dates = list(pd.date_range("2026-01-01", periods=60).date)
        dup = dates + [dates[-1]]  # 最后一天重复
        rows = [(d, 10.0, 11.0, 9.0, 10.5, 1000, 10000) for d in dup]
        captured = {}

        class _FakeCli:
            def execute(self, sql, params=None):
                captured["sql"] = sql
                return rows

        monkeypatch.setattr(ka, "_make_cli", lambda: _FakeCli())
        df = ka.fetch_kline("600519.SH", 250)
        assert df["date"].is_unique
        assert df["close"].iloc[-1] == 10.5


class TestRepoGuard:
    def test_missing_repo_fails_closed(self, monkeypatch, tmp_path):
        from scripts.backtest.kronos_adapter import _load_kronos_classes

        monkeypatch.setattr("scripts.backtest.kronos_adapter.KRONOS_REPO",
                            tmp_path / "nope")
        with pytest.raises(RuntimeError, match="官方仓缺失"):
            _load_kronos_classes()


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
