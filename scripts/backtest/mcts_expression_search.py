# [BLUEPRINT] MOD-BT-202 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.mcts_expression_search
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; scripts.backtest.lane_c_formula_miner
# [CONSUMERS] 策略生产全景图 FAC-E1C 车道C 第三轨（MCTS 公式搜索）；lane_c2_candidates.csv
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 树节点=DSL 子表达式（算子栈前缀），action=白名单算子/特征追加；
#   UCB1 选择（c=1.4）；reward=增量 IC（跨 194 考尺同源）；纯函数核心零 IO
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(参数非法)
# [TESTS] tests/backtest/test_mcts_expression_search.py
# [A_module] module_id=MOD-BT-202 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 非常驻服务：事件调用无常驻循环
"""FAC-E1C 第三轨——MCTS 表达式搜索 MVP（AlphaMuse 思路：LLM 生成+树搜索组织探索）。

MCTS 四步循环：UCB 选择→随机扩展→增量 IC 评估（复用 155 residualize+rank_ic）→
reward 回传。叶子=完整 DSL 表达式。搜索空间受控（白名单算子+已知特征）。
产出生成考卷件候选→E2 预审（同 158 产线）。

用法:
  python scripts/backtest/mcts_expression_search.py search --iterations 50 --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "lane_c3_candidates.csv"


class MCTSNode:
    """树节点：state=DSL 前缀（token 列表），children=子节点列表。"""

    def __init__(self, tokens: tuple[str, ...], parent=None):
        self.tokens = tokens
        self.parent = parent
        self.children: list[MCTSNode] = []
        self.visits = 0
        self.value = 0.0

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def ucb(self, c: float = 1.4) -> float:
        if self.visits == 0:
            return float("inf")
        p = self.parent
        return self.value / self.visits + c * math.sqrt(2 * math.log(p.visits) / self.visits) \
            if p and p.visits > 0 else float("inf")


def mcts_search(ops: list[str], features: list[str],
                eval_fn, iterations: int = 50, max_depth: int = 4,
                c: float = 1.4, seed: int = 42) -> list[dict]:
    """MCTS 搜索循环（纯函数：eval_fn 注入求值逻辑）。

    eval_fn(tokens: tuple[str,...]) -> float  # 增量 IC 或 reward
    返回 top-N 候选节点（按 visits×value 排序）。
    """
    rng = np.random.default_rng(seed)
    root = MCTSNode(())
    all_tokens = list(ops) + list(features)
    candidates: list[dict] = []

    for _ in range(iterations):
        node = root
        depth = 0
        # Selection: walk down tree via UCB
        while not node.is_leaf and depth < max_depth:
            best = max(node.children, key=lambda ch: ch.ucb(c))
            node = best
            depth += 1
        # Expansion: create child with random token
        token = all_tokens[rng.integers(0, len(all_tokens))]
        child_tokens = node.tokens + (token,)
        child = MCTSNode(child_tokens, parent=node)
        node.children.append(child)
        # Simulation: evaluate expression value
        reward = eval_fn(child_tokens)
        child.visits = 1
        child.value = reward
        # Backprop
        p = child
        while p:
            p.visits += 1
            p.value += reward
            p = p.parent

    # Collect leaves with best value
    leaves = []
    def _collect(n: MCTSNode, d: int):
        if n.is_leaf:
            leaves.append(n)
        for ch in n.children:
            _collect(ch, d + 1)
    _collect(root, 0)
    leaves.sort(key=lambda n: -n.value / max(n.visits, 1))
    results = []
    for n in leaves[:20]:
        expr = " ".join(n.tokens)
        results.append({"expression": expr, "avg_value": round(n.value / max(n.visits, 1), 6),
                        "visits": n.visits})
    return results


def run_search(iterations: int, max_depth: int, top_n: int, dry_run: bool = False) -> dict:
    """主流程：白名单→面板→MCTS→产候选→卸 CSV。"""
    from scripts.backtest.lane_c_formula_miner import (
        compute_features, fetch_panel, load_whitelist, build_eval_ops,
        evaluate_expr, residualize, rank_ic,
    )
    whitelist = load_whitelist()
    op_names = [op for grp in whitelist["approved"].values() for op in grp]
    op_names = [op["op"] if isinstance(op, dict) else op for op in op_names]
    panel = fetch_panel(40, 250)
    feats = panel["features"]
    ops = build_eval_ops(panel["date_codes"], panel["symbol_codes"])
    baseline = panel["baseline"]

    def eval_fn(tokens):
        expr = " ".join(tokens)
        try:
            vals = evaluate_expr(expr, feats, ops, panel["X"])
            res = residualize(vals, baseline)
            return rank_ic(res, panel["y"])
        except Exception:
            return -1.0

    # Simplified MCTS (random expansion + eval, no UCB tree for MVP)
    rng = np.random.default_rng(42)
    candidates = []
    for i in range(iterations):
        n_ops = int(rng.integers(2, max_depth + 1))
        tokens = [op_names[rng.integers(0, len(op_names))] for _ in range(n_ops)]
        for j in range(n_ops // 2):
            tokens.insert(rng.integers(0, len(tokens) + 1), feats[rng.integers(0, len(feats))])
        expr = " ".join(tokens)
        try:
            vals = evaluate_expr(expr, feats, ops, panel["X"])
            ic = rank_ic(residualize(vals, baseline), panel["y"])
        except Exception:
            ic = -1.0
        if ic > 0:
            candidates.append({"expression": expr, "incr_ic": round(float(ic), 6)})
    candidates.sort(key=lambda c: -c["incr_ic"])
    top = candidates[:top_n]
    for c in top:
        cid = hashlib.md5(f"E1C3:{c['expression']}".encode()).hexdigest()[:12]
        c["candidate_id"] = f"CAND-{cid}"
    if not dry_run and top:
        _INTAKE_CSV.parent.mkdir(parents=True, exist_ok=True)
        header = not _INTAKE_CSV.exists()
        pd.DataFrame(top).to_csv(_INTAKE_CSV, mode="a", header=header, index=False, encoding="utf-8-sig")
    return {"iterations": iterations, "mined": len(top), "candidates": top}


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1C MCTS 表达式搜索 MVP")
    ap.add_argument("--iterations", type=int, default=50)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rep = run_search(args.iterations, args.max_depth, args.top_n, args.dry_run)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
