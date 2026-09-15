# [BLUEPRINT] MOD-BT-159 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_factor_strategy_template
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas
# [CONSUMERS] MOD-BT-159 factor_strategy_template 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络：模板内容/ID/权重装配语义合成数据验证；生成件编译自检
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-159 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E3→E4 公式轨桥单测——模板/ID/权重装配/生成件编译自检，零网络。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.factor_strategy_template import (
    assemble_weights,
    compute_features_importable,
    generate_strategy_file,
    strategy_id_for,
)
from scripts.backtest.lane_c2_agentic_miner import validate_expr

EXPR = "ts_zscore_20(ret_5d)"


class TestStrategyId:
    def test_content_addressed_and_prefix(self):
        assert strategy_id_for(EXPR, "CAND-a") == strategy_id_for(EXPR, "CAND-a")
        assert strategy_id_for(EXPR, "CAND-a").startswith("FACT-")
        assert strategy_id_for(EXPR, "CAND-a") != strategy_id_for(EXPR, "CAND-b")


class TestGenerateStrategyFile:
    def test_generated_file_compiles_and_contract_complete(self, tmp_path):
        out = generate_strategy_file(EXPR, "CAND-x", top_n=20,
                                     out_path=tmp_path / "c4_fact_test.py")
        content = out.read_text(encoding="utf-8")
        for token in ("STRATEGY_ID", "WINDOW_KIND", "def build(s, e):",
                      "build_factor_weights", EXPR):
            assert token in content
        compile(content, "c4_fact_test.py", "exec")  # 编译自检

    def test_different_expr_different_module(self, tmp_path):
        a = generate_strategy_file("add(ret_1d, ret_5d)", "CAND-a",
                                   out_path=tmp_path / "a.py")
        b = generate_strategy_file("log(abs(ret_1d))", "CAND-a",
                                   out_path=tmp_path / "b.py")
        assert a.read_text() != b.read_text()


class TestValidateIntegration:
    def test_rejects_nonwhitelist_before_generation(self):
        ok, why = validate_expr("sin(ret_1d)", ["ret_1d"], {"add"})
        assert not ok and "sin" in why


class TestAssembleWeights:
    def _feats(self):
        dates = list(pd.date_range("2026-01-01", periods=3).date)
        rows = []
        for d in dates:
            rows.append({"date": d, "s": "000001.SZ", "close": 10.0, "factor": 1.0})
            rows.append({"date": d, "s": "000002.SZ", "close": 20.0, "factor": 2.0})
        return pd.DataFrame(rows)

    def test_top_n_equal_weight(self):
        weights, closes = assemble_weights(self._feats(), top_n=1)
        assert (weights["000002.SZ"] == 1.0).all()  # factor 高者恒入选
        assert (weights.sum(axis=1) == 1.0).all()   # 等权归一
        assert closes.shape == (3, 2)

    def test_top_n_two_half_half(self):
        weights, _ = assemble_weights(self._feats(), top_n=2)
        assert (weights == 0.5).all().all()

    def test_nan_factor_row_excluded(self):
        feats = self._feats()
        feats.loc[0, "factor"] = np.nan  # 第一行 A 因子缺失
        weights, _ = assemble_weights(feats, top_n=1)
        assert (weights.loc[weights.index[0]]["000001.SZ"] == 0.0)


class TestSingleSourceAnchor:
    def test_compute_features_importable_from_155(self):
        assert compute_features_importable() is True


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])


def test_dedup_kline_rows_keeps_last_and_preserves_unique():
    import pandas as pd

    from scripts.backtest.factor_strategy_template import _dedup_kline_rows

    k = pd.DataFrame({
        "date": ["2026-09-10", "2026-09-11", "2026-09-11", "2026-09-12"],
        "s": ["600000.SH", "600000.SH", "600000.SH", "000001.SZ"],
        "close": [10.0, 11.0, 11.5, 9.0],
    })
    out = _dedup_kline_rows(k)
    assert len(out) == 3
    row = out[(out["date"] == "2026-09-11") & (out["s"] == "600000.SH")]
    assert float(row["close"].iloc[0]) == 11.5
    assert list(out["date"]) == ["2026-09-10", "2026-09-11", "2026-09-12"]
