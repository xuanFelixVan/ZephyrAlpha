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
    def test_add_semantics(self):
        x = _panel(4)
        ops = build_eval_ops(N)
        out = evaluate_expr("add(ret_1d, ret_5d)", FEATURES, ops, x)
        assert np.allclose(out, x[:, 0] + x[:, 1])

    def test_protected_div_no_inf(self):
        x = _panel(4)
        x[:, 3] = 0.0  # turnover=0 → div 分母保护
        ops = build_eval_ops(N)
        out = evaluate_expr("div(ret_1d, turnover)", FEATURES, ops, x)
        assert np.isfinite(out).all()

    def test_ts_delta_5_groupwise(self):
        x = _panel(6)  # 6 交易日 × 2 标的
        ops = build_eval_ops(N)
        out = evaluate_expr("ts_delta_5(ret_1d)", FEATURES, ops, x).reshape(-1, N)
        assert np.allclose(out[:5], 0.0)
        assert out[5, 0] == pytest.approx(x[10, 0] - x[0, 0])  # 跨标的零污染


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
        for token in ("赚谁的钱", "原创", "14"):
            assert token in p1  # 三正则事前约束：对齐/原创/简洁

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
