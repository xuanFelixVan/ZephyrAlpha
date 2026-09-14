# [BLUEPRINT] MOD-BT-158 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_lane_c2_agentic_miner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas
# [CONSUMERS] MOD-BT-158 lane_c2_agentic_miner 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM：合成面板验证 DSL 校验/求值/AST 相似度/prompt/出生证
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-158 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1C 二轨纯函数核单测——DSL 校验/求值/AST 原创性/prompt/出生证，合成面板零网络。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.lane_c2_agentic_miner import (
    ORIGINALITY_MAX_SIM,
    attach_birth_certificate,
    ast_similarity,
    build_eval_ops,
    build_generation_prompt,
    evaluate_expr,
    load_existing_ids,
    make_candidate_id,
    originality_max,
    parse_candidates,
    validate_expr,
)

FEATURES = ["ret_1d", "ret_5d", "vol_20d", "turnover"]
N = 2  # 每日 2 标的


@pytest.fixture()
def ops():
    return build_eval_ops(N)


def _panel(rows: int = 8):
    rng = np.random.default_rng(5)
    return rng.normal(size=(rows * N, len(FEATURES)))


class TestValidateExpr:
    def test_valid_call_form(self):
        ok, why = validate_expr("add(ret_1d, div(vol_20d, turnover))", FEATURES,
                                {"add", "div"})
        assert ok, why

    def test_unknown_op_rejected(self):
        ok, why = validate_expr("sin(ret_1d)", FEATURES, {"add"})
        assert not ok and "sin" in why

    def test_unknown_feature_rejected(self):
        ok, why = validate_expr("add(close_ma20, ret_1d)", ["ret_1d"], {"add"})
        assert not ok and "close_ma20" in why

    def test_binop_style_rejected(self):
        ok, why = validate_expr("ret_1d + ret_5d", FEATURES, {"add"})
        assert not ok  # 只准函数调用形式（prompt 已约束）

    def test_constant_allowed(self):
        ok, _ = validate_expr("mul(ret_1d, 2)", FEATURES, {"mul"})
        assert ok

    def test_ts_ops_accepted(self):
        ok, why = validate_expr("ts_zscore_20(ts_delta_5(ret_1d))", FEATURES,
                                {"ts_zscore_20", "ts_delta_5"})
        assert ok, why


class TestEvaluateExpr:
    def _ops(self, dates: int):
        from scripts.backtest.lane_c_formula_miner import make_panel_operators
        dc = np.repeat(np.arange(dates), N)
        sc = np.tile([0, 1], dates)
        return build_eval_ops(dc, sc), dc, sc

    def test_add_semantics(self):
        x = _panel(4)
        ops, _, _ = self._ops(4)
        out = evaluate_expr("add(ret_1d, ret_5d)", FEATURES, ops, x)
        assert np.allclose(out, x[:, 0] + x[:, 1])

    def test_protected_div_no_inf(self):
        x = _panel(4)
        x[:, 3] = 0.0  # turnover=0 → div 分母保护
        ops, _, _ = self._ops(4)
        out = evaluate_expr("div(ret_1d, turnover)", FEATURES, ops, x)
        assert np.isfinite(out).all()

    def test_ts_delta_5_groupwise(self):
        x = _panel(6)  # 6 交易日 × 2 标的
        ops, dc, _ = self._ops(6)
        out = evaluate_expr("ts_delta_5(ret_1d)", FEATURES, ops, x).reshape(-1, N)
        assert np.allclose(out[:5], 0.0)
        assert out[5, 0] == pytest.approx(x[10, 0] - x[0, 0])  # 跨标的零污染

    def test_rank_cs_groupwise(self):
        x = _panel(4)
        ops, _, _ = self._ops(4)
        out = evaluate_expr("rank_cs(ret_1d)", FEATURES, ops, x).reshape(-1, N)
        assert np.allclose(out.sum(axis=1), 1.5)  # 两标的截面 pct 秩之和恒为 1.5


class TestPanelOperators:
    """分组语义验证：8 交易日 × 2 标的（日期主序交替行，groupby 分组码）。"""

    def _ops(self):
        from scripts.backtest.lane_c_formula_miner import make_panel_operators
        return {f.name: f for f in make_panel_operators(
            np.repeat(np.arange(8), 2), np.tile([0, 1], 8),
            ["rank_cs", "ts_delta_5", "ts_zscore_20", "ts_corr_20"])}

    def _panel(self):
        a = np.arange(1.0, 9.0)          # 标的 A 逐日 1..8
        b = np.arange(2.0, 17.0, 2.0)    # 标的 B 逐日 2..16
        return np.stack([a, b], axis=1).ravel()

    def test_rank_cs_per_date(self):
        out = self._ops()["rank_cs"](self._panel())
        assert len(out) == 16
        assert np.allclose(out[0::2], 0.5)  # A 每日都小 → 秩 0.5
        assert np.allclose(out[1::2], 1.0)  # B 每日都大 → 秩 1.0

    def test_ragged_group_supported(self):
        # 参差面板（停牌日整组缺失）：groupby 语义天然支持
        from scripts.backtest.lane_c_formula_miner import make_panel_operators
        x = self._panel()
        ragged = np.delete(x, [0, 1])  # 删第 0 日整组
        f = {f.name: f for f in make_panel_operators(
            np.repeat(np.arange(8), 2)[2:], np.tile([0, 1], 7),
            ["rank_cs"])}["rank_cs"]
        out = f(ragged)
        assert len(out) == 14 and np.isfinite(out).all()

    def test_ts_delta_5_symbolwise(self):
        out = self._ops()["ts_delta_5"](self._panel()).reshape(-1, 2)
        assert np.allclose(out[:5], 0.0)  # 段首无历史=0
        assert out[5, 0] == 5.0 and out[5, 1] == 10.0  # A:6-1=5; B:12-2=10（跨标的零污染）

    def test_ts_zscore_20_finite_and_head_zero(self):
        out = self._ops()["ts_zscore_20"](self._panel()).reshape(-1, 2)
        assert np.isfinite(out).all()
        assert np.allclose(out[:4], 0.0)  # min_periods=5 → 前 4 日无历史=0
        assert out[4, 0] > 0  # 第 5 日起可算（上斜序列 z 为正）

    def test_ts_corr_self_finite(self):
        x = self._panel()
        out = self._ops()["ts_corr_20"](x, x).reshape(-1, 2)
        assert np.isfinite(out).all()
        assert np.allclose(out[:7], 0.0)  # min_periods=8 → 前 7 日=0
        assert np.allclose(out[7], 1.0)  # 第 8 日起自相关=1


class TestAstSimilarity:
    def test_identical_is_one(self):
        assert ast_similarity("add(ret_1d, ret_5d)", "add(ret_1d, ret_5d)",
                              FEATURES) == 1.0

    def test_feature_rename_normalized(self):
        # 特征名差异被 V 归一：结构相同=相似度 1（结构去重不看变量名）
        assert ast_similarity("add(ret_1d, ret_5d)", "add(vol_20d, turnover)",
                              FEATURES) == 1.0

    def test_different_structure_low(self):
        s = ast_similarity("add(ret_1d, ret_5d)", "log(abs(ret_1d))", FEATURES)
        assert s < 0.5

    def test_originality_max_over_pool(self):
        pool = ["add(ret_1d, ret_5d)", "log(abs(ret_1d))"]
        assert originality_max("mul(ret_1d, turnover)", pool, FEATURES) < \
            ORIGINALITY_MAX_SIM
        assert originality_max("add(vol_20d, turnover)", pool, FEATURES) == 1.0


class TestGenerationPrompt:
    def test_deterministic_and_complete(self):
        p1 = build_generation_prompt("动量假说", FEATURES, ["add", "log"], ["a+ b"], 3)
        p2 = build_generation_prompt("动量假说", FEATURES, ["add", "log"], ["a+ b"], 3)
        assert p1 == p2
        assert "动量假说" in p1 and "add" in p1 and "ret_1d" in p1
        for token in ("谁在卖给你", "为什么愿意亏", "成本或", "原创", "14"):
            assert token in p1  # 三正则事前约束+交易对手三问（v2 逼问升级）

    def test_mechanism_empty_talk_forbidden(self):
        p = build_generation_prompt("h", FEATURES, ["add"], [], 1)
        assert "利用风险溢价" in p and "机制不清晰" in p  # 套话点名为反面教材

    def test_existing_examples_capped(self):
        p = build_generation_prompt("h", FEATURES, ["add"], [f"f{i}" for i in range(9)], 1)
        assert "f4" in p and "f5" not in p  # 只列前 5 条既有公式


class TestParseCandidates:
    def test_clean_array(self):
        raw = '[{"expression": "add(a, b)", "description": "d", "mechanism": "m"}]'
        assert len(parse_candidates(raw)) == 1

    def test_items_without_expression_dropped(self):
        raw = '[{"description": "x"}, {"expression": "log(a)"}]'
        assert len(parse_candidates(raw)) == 1

    def test_garbage_empty(self):
        assert parse_candidates("我想不出") == []


class TestLedgerAndBirth:
    def test_candidate_id_content_addressed(self):
        assert make_candidate_id("add(a)") == make_candidate_id("add(a)")
        assert make_candidate_id("add(a)") != make_candidate_id("sub(a)")

    def test_birth_certificate_machine_written(self, tmp_path):
        df = pd.DataFrame([{"candidate_id": "CAND-x", "incr_ic": 0.1}])
        out = attach_birth_certificate(df.to_dict("records"), "E1C2-x", "qwen3:8b",
                                       "wlsha", 3)
        assert out[0]["birth_channel"] == "C2"
        assert "agentic-llm:qwen3:8b" in out[0]["birth_source"]
        assert "E2passed:3" in out[0]["birth_source"]

    def test_load_existing_ids_missing_file(self, tmp_path):
        assert load_existing_ids(tmp_path / "nope.csv") == set()


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
