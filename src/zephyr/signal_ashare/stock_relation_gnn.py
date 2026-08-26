# [BLUEPRINT] MOD-SIG-126 | docs/03_modules/_domain_signal/stock_relation_gnn/blueprint.md
# [MODULE] zephyr.signal_ashare.stock_relation_gnn
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（标准库纯内存列表实现；禁PyG/DGL；predictor回调全注入）
# [CONSUMERS] 运行时装配批（邻居聚合特征接密度预测装配 / 关系图信号消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 关系词表闭合(supply_chain|same_industry|concept_cooccur); 聚合模式闭合(gat|gcn); 边按无向闭合(src/dst互为邻居); 特征维数全图一致且全有限; 边权 ∈ (0,1]; 禁自环/重复边; 图规模护栏(max_nodes/max_edges超限拒绝); 邻接按stock_id排序遍历; GCN=度归一化加权均值/GAT=缩放点击注意力softmax; 聚合特征=x_i⊕三路关系聚合(按枚举序拼接); predictor未注入Fail-Closed; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/stock_relation_gnn/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StockRelationGnnError(占位 ZA-SIG-UNREGISTERED-STOCK-RELATION-GNN)——空id/空特征/非有限特征/维数不一致/重复节点/非法关系/未知端点/自环/边权越界/重复边/规模超限/非法聚合模式/未知节点/predictor缺失或异常时抛
# [TESTS] tests/signal_ashare/test_stock_relation_gnn.py
# [A_module] module_id=MOD-SIG-126 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""StockRelationGNN — 股票关系 GNN 基类（MOD-SIG-126）。

B10-01830（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-049，A1 §29.6；
canonical 承接 TESTB-034/046 归并）：**3 种邻接图**（供应链/同行业/概念共现，
词表闭合）+ **GAT/GCN 两路聚合**（注意力系数/度归一化加权均值，标准库纯内存
列表实现，**不引 PyG/DGL**）+ 邻居聚合特征接密度预测（**注入 predictor 回调**）
+ **图规模护栏**（节点/边上限拒绝）。

确定性约定（蓝图 §1）：关系边按无向闭合（src/dst 互为邻居）；邻接遍历按
stock_id 字典序；三路关系聚合结果按 RelationKind 枚举序与自身特征拼接；
浮点累加经 math.fsum，同输入必同输出。真 GNN 训练属人工闸门，本件仅为
确定性前向聚合基类，禁止冒充训练后推理结果消费。
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AggregateMode",
    "DensityForecast",
    "RelationEdge",
    "RelationKind",
    "StockRelationGNN",
    "StockRelationGnnError",
]


class StockRelationGnnError(Exception):
    """股票关系 GNN 输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-STOCK-RELATION-GNN。
    """


class RelationKind(str, Enum):
    """关系图类型（词表闭合；聚合拼接顺序即枚举定义序）。"""

    SUPPLY_CHAIN = "supply_chain"  # 供应链
    SAME_INDUSTRY = "same_industry"  # 同行业
    CONCEPT_COOCCUR = "concept_cooccur"  # 概念共现


class AggregateMode(str, Enum):
    """聚合模式（词表闭合）。"""

    GAT = "gat"  # 注意力系数聚合（缩放点击 softmax）
    GCN = "gcn"  # 度归一化加权均值聚合


@dataclass(frozen=True)
class RelationEdge:
    """关系边（无向闭合；weight ∈ (0,1]，frozen）。"""

    kind: RelationKind
    src: str
    dst: str
    weight: float = 1.0


@dataclass(frozen=True)
class DensityForecast:
    """密度预测结果（聚合特征 + predictor 打分，frozen）。"""

    stock_id: str
    mode: AggregateMode
    features: tuple[float, ...]
    score: float


class StockRelationGNN:
    """股票关系 GNN 基类（3 邻接图 + GAT/GCN 聚合 + 密度预测注入 + 规模护栏）。"""

    def __init__(
        self,
        *,
        max_nodes: int = 500,
        max_edges: int = 5000,
        predictor: Callable[[str, tuple[float, ...]], float] | None = None,
    ) -> None:
        if not isinstance(max_nodes, int) or max_nodes < 1:
            raise StockRelationGnnError(f"max_nodes 须为 ≥1 整数: {max_nodes!r}")
        if not isinstance(max_edges, int) or max_edges < 1:
            raise StockRelationGnnError(f"max_edges 须为 ≥1 整数: {max_edges!r}")
        self._max_nodes = max_nodes
        self._max_edges = max_edges
        self._predictor = predictor
        self._features: dict[str, tuple[float, ...]] = {}
        self._dim: int | None = None
        #: 邻接：kind -> stock -> {neighbor: weight}（无向闭合，遍历时排序）
        self._adj: dict[RelationKind, dict[str, dict[str, float]]] = {
            kind: {} for kind in RelationKind
        }
        self._edge_count = 0

    # ── 属性 ─────────────────────────────────────────────────────────────

    @property
    def node_count(self) -> int:
        """已登记节点数。"""
        return len(self._features)

    @property
    def edge_count(self) -> int:
        """已登记关系边数（无向边按 1 计）。"""
        return self._edge_count

    @property
    def feature_dim(self) -> int | None:
        """特征维数（无节点时为 None）。"""
        return self._dim

    # ── 图构建（规模护栏 Fail-Closed） ─────────────────────────────────────

    def add_node(self, stock_id: str, features: Sequence[float]) -> None:
        """登记节点：空id/空特征/非有限/维数不一致/重复/超节点上限 → Fail-Closed。"""
        if not stock_id:
            raise StockRelationGnnError("stock_id 为空")
        if not features:
            raise StockRelationGnnError(f"特征为空: {stock_id!r}")
        vec = tuple(float(v) for v in features)
        if any(not math.isfinite(v) for v in vec):
            raise StockRelationGnnError(f"特征含非有限值: {stock_id!r}")
        if stock_id in self._features:
            raise StockRelationGnnError(f"节点重复: {stock_id!r}")
        if self._dim is None:
            self._dim = len(vec)
        elif len(vec) != self._dim:
            raise StockRelationGnnError(
                f"特征维数不一致: {stock_id!r} 维数 {len(vec)} ≠ 全图 {self._dim}"
            )
        if len(self._features) >= self._max_nodes:
            raise StockRelationGnnError(
                f"节点数超护栏上限: {self._max_nodes}（图规模护栏拒绝）"
            )
        self._features[stock_id] = vec

    def add_edge(self, edge: RelationEdge) -> None:
        """登记关系边：非法关系/未知端点/自环/边权越界/重复/超边上限 → Fail-Closed。"""
        if not isinstance(edge.kind, RelationKind):
            raise StockRelationGnnError(f"非法关系类型: {edge.kind!r}")
        if edge.src == edge.dst:
            raise StockRelationGnnError(f"自环非法: {edge.src!r}")
        for endpoint in (edge.src, edge.dst):
            if endpoint not in self._features:
                raise StockRelationGnnError(f"未知节点: {endpoint!r}（未登记）")
        weight = float(edge.weight)
        if not 0.0 < weight <= 1.0:
            raise StockRelationGnnError(
                f"边权必须 ∈ (0,1]: {edge.src!r} -- {edge.dst!r} = {edge.weight}"
            )
        adj = self._adj[edge.kind]
        if edge.dst in adj.get(edge.src, {}):
            raise StockRelationGnnError(
                f"边重复: {edge.src!r} -- {edge.dst!r} ({edge.kind.value})"
            )
        if self._edge_count >= self._max_edges:
            raise StockRelationGnnError(
                f"边数超护栏上限: {self._max_edges}（图规模护栏拒绝）"
            )
        adj.setdefault(edge.src, {})[edge.dst] = weight
        adj.setdefault(edge.dst, {})[edge.src] = weight  # 无向闭合
        self._edge_count += 1

    # ── 查询 ─────────────────────────────────────────────────────────────

    def adjacency(self, kind: RelationKind) -> dict[str, tuple[tuple[str, float], ...]]:
        """单关系图邻接视图（键与邻居均按 stock_id 确定性排序）。"""
        if not isinstance(kind, RelationKind):
            raise StockRelationGnnError(f"非法关系类型: {kind!r}")
        adj = self._adj[kind]
        return {
            stock: tuple(sorted(adj.get(stock, {}).items()))
            for stock in sorted(self._features)
        }

    def node_features(self, stock_id: str) -> tuple[float, ...]:
        """单节点原始特征（未知 → Fail-Closed）。"""
        vec = self._features.get(stock_id)
        if vec is None:
            raise StockRelationGnnError(f"未知节点: {stock_id!r}（未登记）")
        return vec

    # ── 聚合（GAT/GCN 两路，确定性） ───────────────────────────────────────

    def _require_mode(self, mode: AggregateMode) -> None:
        if not isinstance(mode, AggregateMode):
            raise StockRelationGnnError(f"非法聚合模式: {mode!r}")

    def _aggregate_kind(
        self, kind: RelationKind, mode: AggregateMode
    ) -> dict[str, tuple[float, ...]]:
        """单关系图聚合：GCN=度归一化加权均值；GAT=缩放点击注意力softmax。"""
        assert self._dim is not None
        adj = self._adj[kind]
        out: dict[str, tuple[float, ...]] = {}
        for stock in sorted(self._features):  # 固定遍历序
            neighbors = sorted(adj.get(stock, {}).items())  # (neighbor, weight) 按id排序
            if not neighbors:
                out[stock] = (0.0,) * self._dim
                continue
            x_i = self._features[stock]
            if mode is AggregateMode.GCN:
                degree = math.fsum(w for _, w in neighbors)
                coeffs = [(nbr, w / degree) for nbr, w in neighbors]
            else:  # GAT：缩放点击打分 softmax（温度=sqrt(dim)）
                scale = math.sqrt(self._dim)
                scores = [
                    math.fsum(a * b for a, b in zip(x_i, self._features[nbr])) / scale
                    for nbr, _ in neighbors
                ]
                peak = max(scores)
                exps = [math.exp(s - peak) for s in scores]
                denom = math.fsum(exps)
                coeffs = [
                    (nbr, e / denom) for (nbr, _), e in zip(neighbors, exps)
                ]
            out[stock] = tuple(
                math.fsum(coef * self._features[nbr][d] for nbr, coef in coeffs)
                for d in range(self._dim)
            )
        return out

    def aggregate_features(self, mode: AggregateMode) -> dict[str, tuple[float, ...]]:
        """全图聚合特征：x_i ⊕ 三路关系聚合（RelationKind 枚举序拼接，确定性）。"""
        self._require_mode(mode)
        if not self._features:
            raise StockRelationGnnError("图为空（无节点，禁止聚合）")
        per_kind = {
            kind: self._aggregate_kind(kind, mode) for kind in RelationKind
        }
        out: dict[str, tuple[float, ...]] = {}
        for stock in sorted(self._features):
            parts = [self._features[stock]]
            parts.extend(per_kind[kind][stock] for kind in RelationKind)
            out[stock] = tuple(v for part in parts for v in part)
        return out

    # ── 密度预测（注入 predictor 回调） ────────────────────────────────────

    def predict_density(self, stock_id: str, mode: AggregateMode) -> DensityForecast:
        """聚合特征接密度预测：未知节点/非法模式/predictor未注入或异常 → Fail-Closed。"""
        self._require_mode(mode)
        if stock_id not in self._features:
            raise StockRelationGnnError(f"未知节点: {stock_id!r}（未登记）")
        if self._predictor is None:
            raise StockRelationGnnError(
                "predictor 未注入（密度预测强制注入回调，禁止旁路）"
            )
        features = self.aggregate_features(mode)[stock_id]
        try:
            score = float(self._predictor(stock_id, features))
        except Exception as exc:  # noqa: BLE001 — 外部回调异常 Fail-Closed 包装
            _log.exception("predictor 预测异常: %s", stock_id)
            raise StockRelationGnnError(
                f"predictor 预测异常: {stock_id!r}（Fail-Closed）"
            ) from exc
        if not math.isfinite(score):
            raise StockRelationGnnError(
                f"predictor 返回非有限分: {stock_id!r} = {score}（Fail-Closed）"
            )
        return DensityForecast(
            stock_id=stock_id, mode=mode, features=features, score=score
        )
