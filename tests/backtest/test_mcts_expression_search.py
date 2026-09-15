# [BLUEPRINT] MOD-BT-202 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_mcts_expression_search
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; scripts.backtest.mcts_expression_search
# [CONSUMERS] MOD-BT-202 mcts_expression_search 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络；合成 eval_fn 验证 UCB 选择/树生长/reward 回传/vs 随机基线
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-202 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MCTS 表达式搜索纯函数单测——UCB 数学/树生长/reward 回传/基线对比，零网络。"""
from __future__ import annotations

import math

import numpy as np
import pytest

from scripts.backtest.mcts_expression_search import MCTSNode, mcts_search


class TestMCTSNode:
    def test_ucb_unvisited_is_inf(self):
        root = MCTSNode(())
        child = MCTSNode(("op_a",), parent=root)
        assert child.ucb() == float("inf")

    def test_ucb_matches_manual_formula(self):
        root = MCTSNode(())
        child = MCTSNode(("op_a",), parent=root)
        root.visits, child.visits, child.value = 10, 4, 2.0
        expected = 2.0 / 4 + 1.4 * math.sqrt(2 * math.log(10) / 4)
        assert abs(child.ucb(1.4) - expected) < 1e-12

    def test_ucb_zero_visit_parent_is_inf(self):
        root = MCTSNode(())
        child = MCTSNode(("op_a",), parent=root)
        child.visits, child.value = 4, 2.0
        assert child.ucb() == float("inf")

    def test_is_leaf_property(self):
        root = MCTSNode(())
        assert root.is_leaf
        root.children.append(MCTSNode(("op_a",), parent=root))
        assert not root.is_leaf


class TestMctsSearch:
    @staticmethod
    def _binary_eval(tokens) -> float:
        return 1.0 if "sig" in tokens else 0.0

    def test_one_eval_per_iteration(self):
        calls: list = []

        def eval_fn(tokens):
            calls.append(1)
            return 0.0

        mcts_search(["op_a", "op_b"], ["sig", "noise"], eval_fn,
                    iterations=25, seed=3)
        assert len(calls) == 25

    def test_backprop_final_leaf_invariants(self):
        # 终叶（从未被扩展）恰好被回传一次：visits=2、value=2×reward，
        # 故 avg_value 恒等于其出生 reward（二值奖励下 ∈{0,1}）
        res = mcts_search(["op_a", "op_b"], ["sig", "noise"],
                          self._binary_eval, iterations=20, seed=5)
        assert res
        assert all(r["visits"] == 2 for r in res)
        assert all(r["avg_value"] in (0.0, 1.0) for r in res)
        # 树中存在 sig 分支时，其终叶 avg==1（reward 沿链回传到叶自身与祖先）
        assert any(r["avg_value"] == 1.0 for r in res)

    def test_tree_depth_bounded(self):
        res = mcts_search(["op_a", "op_b"], ["sig", "noise"],
                          lambda t: 0.5, iterations=30, max_depth=3, seed=11)
        assert all(len(r["expression"].split()) <= 4 for r in res)

    def test_results_sorted_by_value_desc(self):
        res = mcts_search(["op_a", "op_b"], ["sig", "noise"],
                          self._binary_eval, iterations=40, seed=7)
        vals = [r["avg_value"] for r in res]
        assert vals == sorted(vals, reverse=True)

    def test_expression_is_token_join(self):
        res = mcts_search(["op_a"], ["sig"], lambda t: 0.0, iterations=5, seed=1)
        assert res and all(isinstance(r["expression"], str) and r["visits"] >= 2
                           for r in res)

    def test_deterministic_same_seed(self):
        kw = dict(ops=["op_a", "op_b"], features=["sig", "noise"],
                  eval_fn=self._binary_eval, iterations=30, seed=42)
        assert mcts_search(**kw) == mcts_search(**kw)

    def test_finds_positive_reward_beats_random_baseline(self):
        ops, feats = ["op_a", "op_b"], ["sig", "noise"]
        res = mcts_search(ops, feats, self._binary_eval,
                          iterations=60, max_depth=4, seed=7)
        top_avg = res[0]["avg_value"]
        rng = np.random.default_rng(7)
        pool = ops + feats
        rnd = [self._binary_eval(tuple(pool[rng.integers(0, len(pool))]
                                       for _ in range(int(rng.integers(2, 5)))))
               for _ in range(60)]
        assert top_avg == pytest.approx(1.0)
        assert top_avg > float(np.mean(rnd))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
