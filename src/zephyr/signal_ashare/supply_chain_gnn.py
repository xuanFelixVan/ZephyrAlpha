# [BLUEPRINT] MOD-SIG-055 | docs/03_modules/MOD-SIG-055/
# [MODULE] zephyr.signal_ashare.supply_chain_gnn
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] （远期：供应链传导风险信号消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未 fit 时 propagate_risk 一律 fail-closed（ValueError）；边权 ∈ (0,1]；风险分裁剪至 [0,1]；不引 torch_geometric 等 GNN 依赖——真训练属 B-007 人工闸门
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空节点集/重复节点/悬空边/边权越界/未知种子节点/未训练传播 → ValueError
# [TESTS] tests/signal_ashare/test_supply_chain_gnn.py
# [A_module] module_id=MOD-SIG-055 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""供应链 GNN（MOD-SIG-055）——接口契约 + 轻量占位实现。

产业链/供应链图神经网络属远期增强候选。本模块只立接口契约：fit_baseline 图校验
（节点唯一/边不悬空/边权 ∈ (0,1]）+ propagate_risk 传播接口 + 未训练 fail-closed。
**不引 torch/torch_geometric 依赖**——真 GNN 训练属 B-007 人工闸门。

占位传播路径：种子风险分沿有向边按 边权×decay 逐跳衰减扩散（BFS，访问集防环），
输出每节点 [0,1] 裁剪后的传导风险分——与 causal_inference_engine 传导语义一致
的轻量基线，禁止冒充 GNN 真推理结果消费。
"""

from __future__ import annotations

from collections import deque
from typing import Final

__all__: Final = ["SupplyChainGnn"]


class SupplyChainGnn:
    """供应链 GNN 骨架（BFS 衰减传播占位）。"""

    def __init__(self, *, decay: float = 1.0) -> None:
        if not 0.0 < decay <= 1.0:
            raise ValueError(f"decay 必须 ∈ (0,1]: {decay}")
        self._decay = decay
        self._nodes: list[str] = []
        self._adj: dict[str, list[tuple[str, float]]] = {}

    @property
    def is_fitted(self) -> bool:
        return bool(self._nodes)

    def fit_baseline(self, nodes: list[str], edges: list[tuple[str, str, float]]) -> None:
        """登记供应链图（节点 + 有向带权边）。图非法 → ValueError。"""
        if not nodes:
            raise ValueError("节点集为空")
        if len(set(nodes)) != len(nodes):
            raise ValueError("节点存在重复")
        node_set = set(nodes)
        adj: dict[str, list[tuple[str, float]]] = {n: [] for n in nodes}
        for src, dst, weight in edges:
            if src not in node_set or dst not in node_set:
                raise ValueError(f"边悬空（节点未登记）: {src!r} -> {dst!r}")
            w = float(weight)
            if not 0.0 < w <= 1.0:
                raise ValueError(f"边权必须 ∈ (0,1]: {src!r} -> {dst!r} = {weight}")
            adj[src].append((dst, w))
        self._nodes = list(nodes)
        self._adj = adj

    def propagate_risk(self, seed_scores: dict[str, float]) -> dict[str, float]:
        """种子风险分沿边衰减传播。未训练/未知种子节点 fail-closed。"""
        if not self.is_fitted:
            raise ValueError("模型未训练（图未登记）——propagate_risk fail-closed")
        unknown = set(seed_scores) - set(self._nodes)
        if unknown:
            raise ValueError(f"种子节点未登记: {sorted(unknown)}")

        scores: dict[str, float] = dict.fromkeys(self._nodes, 0.0)
        queue: deque[str] = deque()
        for node, score in seed_scores.items():
            scores[node] = max(scores[node], float(score))
            queue.append(node)

        visited: set[str] = set()
        while queue:
            src = queue.popleft()
            if src in visited:
                continue
            visited.add(src)
            base = scores[src]
            if base <= 0.0:
                continue
            for dst, weight in self._adj.get(src, []):
                propagated = base * weight * self._decay
                if propagated > scores[dst]:
                    scores[dst] = propagated
                    queue.append(dst)

        return {n: min(1.0, max(0.0, s)) for n, s in scores.items()}
