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
        with pytest.raises(RuntimeError, match="官方代码缺失"):
            _load_kronos_classes()

    def test_dir_without_code_fails_closed(self, monkeypatch, tmp_path):
        # 2026-09-16 事故形态：目录存在但 model/kronos.py 被批删——
        # 目录存在性检查假绿，必须检查真实模块文件
        from scripts.backtest.kronos_adapter import _load_kronos_classes

        (tmp_path / "empty_repo").mkdir()
        monkeypatch.setattr("scripts.backtest.kronos_adapter.KRONOS_REPO",
                            tmp_path / "empty_repo")
        with pytest.raises(RuntimeError, match="官方代码缺失"):
            _load_kronos_classes()


class TestResolveWeightDirs:
    def test_daily_ft_is_paired_finetuned_tier(self):
        # 2026-09-16 审计治本：daily_ft 档=微调 tokenizer+predictor 成对目录
        # （predictor 训练时用微调 tokenizer，推理必须同源防 token 空间错位）
        from scripts.backtest.kronos_adapter import _resolve_weight_dirs

        tok, mod = _resolve_weight_dirs("daily_ft")
        assert tok.name == "kronos_tokenizer_daily_ft"
        assert mod.name == "kronos_daily_ft"

    def test_small_tier_official_base(self):
        from scripts.backtest.kronos_adapter import _resolve_weight_dirs

        tok, mod = _resolve_weight_dirs("small")
        assert tok.name == "kronos_tokenizer_base"
        assert mod.name == "kronos_small"

    def test_mini_tier_official_mini(self):
        from scripts.backtest.kronos_adapter import _resolve_weight_dirs

        tok, mod = _resolve_weight_dirs("mini")
        assert tok.name == "kronos_tokenizer_mini"
        assert mod.name == "kronos_mini"


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])


class TestAggregateSymbolReports:
    def _rep(self, sym, ksharp, nsharp, kcal, ncal):
        return {"symbol": sym, "n_test": 15,
                "kronos": {"sharpness": ksharp, "calibrated_share": kcal, "pit_ks": 0.2},
                "naive_rw": {"sharpness": nsharp, "calibrated_share": ncal, "pit_ks": 0.3}}

    def test_win_counting_and_medians(self):
        from scripts.backtest.kronos_adapter import aggregate_symbol_reports
        reps = [
            self._rep("A", 100.0, 300.0, 0.4, 0.2),   # kronos 胜锐度+胜校准
            self._rep("B", 200.0, 300.0, 0.4, 0.2),   # 胜锐度
            self._rep("C", 400.0, 300.0, 0.3, 0.2),   # 负锐度
        ]
        agg = aggregate_symbol_reports(reps)
        assert agg["symbols_ok"] == 3
        assert agg["kronos_sharp_wins"] == 2
        assert agg["kronos_cal_wins"] == 3  # 三票 kronos 校准 share 均高于 naive
        assert agg["win_rate_sharpness"] == pytest.approx(2 / 3, abs=1e-3)  # round(4)
        assert agg["median_kronos_sharpness"] == 200.0

    def test_error_symbols_counted(self):
        from scripts.backtest.kronos_adapter import aggregate_symbol_reports
        reps = [{"symbol": "A", "error": "boom"}]
        agg = aggregate_symbol_reports(reps)
        assert agg["symbols_error"] == 1 and agg["symbols_ok"] == 0
        assert agg["win_rate_sharpness"] is None
