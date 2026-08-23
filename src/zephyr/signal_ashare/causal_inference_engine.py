# [BLUEPRINT] MOD-SIG-042 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5
# [MODULE] zephyr.signal_ashare.causal_inference_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] zephyr.signal_ashare.causal_factor_validator; zephyr.signal_ashare.event_driven_screener（传导链风险数值消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 传导图边权 ∈ (0,1]；影响传播随深度单调衰减；lead-lag 判定只读历史序列无未来函数；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 样本不足 min_samples → ValueError；常数序列（std=0）IC 按 0.0 处理不抛错
# [TESTS] tests/signal_ashare/test_causal_inference_engine.py
# [A_module] module_id=MOD-SIG-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 事件节点+关联边（公司/行业/概念，边权+传导时滞）；因子/收益/市场控制序列
# A1: conduction_paths——BFS 传导路径推演（深度×边权衰减，cutoff 剪枝）
# A2: propagate_impact——事件冲击沿图衰减扩散 → 各节点传导风险分
# A3: assess_causality——lead-lag 双 IC + 控制市场后的偏 IC（残差法）→ 因果/相关/伪相关裁定
# O1: ConductionPath / ImpactMap / CausalAssessment(forward_ic/backward_ic/partial_ic/verdict)
# [/ALGO_FLOW]
"""知识图谱与因果推演引擎（BM-SEL-11，MOD-SIG-042）。

两件套：
  ① 事件传导路径推演——事件、公司、行业的关联织成有向带权图（边权=传导强度、
     lag=传导时滞交易日），事件一来 BFS 推演传导路径，冲击按 深度×边权 衰减扩散，
     输出各节点传导风险分（供 BM-SEL-19 事件筛选的 conduction_risk 消费）。
  ② 关联因子 vs 因果因子区分——lead-lag 双 IC 检验（因子领先收益 vs 收益领先因子）
     + 控制市场收益后的偏 IC（残差法，轻量后门调整）：因子 IC 高但偏 IC≈0 者为
     市场驱动的伪相关；因子显著领先且控制后仍显著者为因果候选。

轻量实现纪律：numpy 单一依赖，不引入 DoWhy/DML 重模型栈（25 号 memo BM-SEL-02-M
裁定——DoWhy/DML 登记远期 Phase 4，本模块为统计社区标准 lead-lag/偏相关做法的
轻量落地；因果图未就绪时下游降级为仅统计评估）。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterable

import numpy as np

__all__: Final = [
    "CausalAssessment",
    "CausalVerdict",
    "ConductionEdge",
    "ConductionGraph",
    "ConductionPath",
    "assess_causality",
]

#: 影响传播默认深度衰减系数（每深一层 ×0.5，初拟）
_DEFAULT_DEPTH_DECAY: Final = 0.5
#: 传导路径最低累计权重（低于剪枝，防噪声路径爆炸）
_MIN_PATH_WEIGHT: Final = 0.01


class CausalVerdict(str, Enum):
    """因子因果性裁定。"""

    CAUSAL_CANDIDATE = "CAUSAL_CANDIDATE"  # 因果候选（领先且控制后仍显著）
    CORRELATED = "CORRELATED"  # 相关（显著但领先性不足或控制后衰减）
    SPURIOUS = "SPURIOUS"  # 伪相关（裸 IC 高但控制市场后≈0）
    INSIGNIFICANT = "INSIGNIFICANT"  # 不显著（裸 IC 低于下限）


@dataclass(frozen=True)
class ConductionEdge:
    """传导边：src → dst，weight=传导强度 (0,1]，lag_days=传导时滞（交易日）。"""

    src: str
    dst: str
    weight: float = 1.0
    lag_days: int = 1
    relation: str = ""  # 关系标签（行业同属/供应链/概念共振等）


@dataclass(frozen=True)
class ConductionPath:
    """一条传导路径（BFS 推演结果）。"""

    nodes: tuple[str, ...]  # 路径节点序列（含起点）
    cumulative_weight: float  # 累计权重（边权连乘）
    total_lag_days: int  # 累计传导时滞


@dataclass(frozen=True)
class CausalAssessment:
    """因子因果性评估输出。"""

    forward_ic: float  # 因子_t × 收益_{t+1} 相关（因子领先）
    backward_ic: float  # 收益_t × 因子_{t+1} 相关（收益领先因子=反向因果迹象）
    partial_ic: float  # 控制市场后的偏 IC（残差法）
    verdict: CausalVerdict
    n_samples: int


class ConductionGraph:
    """事件传导有向带权图（知识图谱轻量版：邻接表 + BFS 推演）。"""

    def __init__(self) -> None:
        self._adj: dict[str, list[ConductionEdge]] = {}

    def add_edge(self, edge: ConductionEdge) -> None:
        """加边。weight∉(0,1] 或 lag_days<0 → ValueError。"""
        if not 0.0 < edge.weight <= 1.0:
            raise ValueError(f"边权必须 ∈ (0,1]: {edge.weight}")
        if edge.lag_days < 0:
            raise ValueError(f"传导时滞必须 ≥0: {edge.lag_days}")
        self._adj.setdefault(edge.src, []).append(edge)
        self._adj.setdefault(edge.dst, self._adj.get(edge.dst, []))

    @property
    def node_count(self) -> int:
        return len(self._adj)

    def neighbors(self, node: str) -> tuple[ConductionEdge, ...]:
        return tuple(self._adj.get(node, ()))

    def conduction_paths(
        self,
        source: str,
        *,
        max_depth: int = 3,
        min_weight: float = _MIN_PATH_WEIGHT,
    ) -> tuple[ConductionPath, ...]:
        """BFS 推演 source 的全部传导路径（深度≤max_depth，累计权重≥min_weight）。

        累计权重=路径边权连乘（单调衰减）；带环保护（路径内节点不重复）。
        """
        paths: list[ConductionPath] = []
        queue: deque[tuple[tuple[str, ...], float, int]] = deque([((source,), 1.0, 0)])
        while queue:
            nodes, weight, lag = queue.popleft()
            if len(nodes) - 1 >= max_depth:
                continue
            for edge in self._adj.get(nodes[-1], ()):
                if edge.dst in nodes:  # 环保护
                    continue
                new_weight = weight * edge.weight
                if new_weight < min_weight:
                    continue
                new_nodes = nodes + (edge.dst,)
                new_lag = lag + edge.lag_days
                paths.append(ConductionPath(nodes=new_nodes, cumulative_weight=new_weight, total_lag_days=new_lag))
                queue.append((new_nodes, new_weight, new_lag))
        return tuple(paths)

    def propagate_impact(
        self,
        sources: dict[str, float],
        *,
        depth_decay: float = _DEFAULT_DEPTH_DECAY,
        max_depth: int = 3,
    ) -> dict[str, float]:
        """事件冲击扩散：sources={事件节点: 初始强度} → {节点: 传导风险分}。

        节点风险分 = Σ 各 source 经最短深度到达该节点的 强度 × depth_decay^深度 × 路径边权连乘，
        多路径到达取最大（风险上界口径，保守）；source 自身不计入输出。
        """
        impact: dict[str, float] = {}
        for src, strength in sources.items():
            queue: deque[tuple[str, int, float]] = deque([(src, 0, strength)])
            best_depth: dict[str, int] = {src: 0}
            while queue:
                node, depth, acc = queue.popleft()
                if depth >= max_depth:
                    continue
                for edge in self._adj.get(node, ()):
                    new_acc = acc * depth_decay * edge.weight
                    new_depth = depth + 1
                    if new_acc <= 0.0:
                        continue
                    if new_acc > impact.get(edge.dst, 0.0):
                        impact[edge.dst] = new_acc
                    # 只在"更优深度"上继续扩散，避免环上无限循环
                    if new_depth < best_depth.get(edge.dst, max_depth + 1):
                        best_depth[edge.dst] = new_depth
                        queue.append((edge.dst, new_depth, new_acc))
        return impact


# ------------------------------------------------------------------
# 关联因子 vs 因果因子区分（lead-lag 双 IC + 残差法偏 IC）
# ------------------------------------------------------------------


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson 相关；常数序列（std≈0）返回 0.0（不抛错）。"""
    sx = float(x.std())
    sy = float(y.std())
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _residualize(y: np.ndarray, control: np.ndarray) -> np.ndarray:
    """y 对 control 一元 OLS 残差（轻量后门调整）。control 常数时返回去均值 y。"""
    if float(control.std()) < 1e-12:
        return y - y.mean()
    beta = float(np.cov(y, control, ddof=0)[0, 1] / control.var())
    return y - beta * control


def assess_causality(
    factor_values: Iterable[float],
    forward_returns: Iterable[float],
    *,
    control_values: Iterable[float] | None = None,
    min_samples: int = 30,
    ic_floor: float = 0.02,
    lead_margin: float = 1.5,
    partial_floor_ratio: float = 0.5,
) -> CausalAssessment:
    """因子因果性评估（统计社区标准做法轻量版，无重模型依赖）。

    三路证据：
      forward_ic  = corr(factor_t, ret_{t+1})——因子领先收益（因果必要条件）
      backward_ic = corr(ret_t, factor_{t+1})——收益领先因子（反向因果/被动暴露迹象）
      partial_ic  = 控制序列（通常为市场收益）残差化后的 corr——剔除共同驱动

    裁定：
      |forward|<ic_floor → INSIGNIFICANT；
      裸 forward 显著但 |partial| < |forward|×partial_floor_ratio → SPURIOUS（市场驱动）；
      |forward| ≥ |backward|×lead_margin 且 partial 保持 → CAUSAL_CANDIDATE；
      其余 → CORRELATED。

    Args:
        factor_values: 因子值序列（与收益同期对齐，长度 n+1：末尾多 1 期用于对齐）
        forward_returns: 收益序列（同期口径，长度 n+1）
        control_values: 控制序列（如市场收益，长度 n+1）；None → 不做偏 IC（=forward_ic）
        min_samples: 最小样本数（不足 → ValueError）
        ic_floor: IC 显著性下限（0.02 与因子库有效线一致）
        lead_margin: 领先性倍数门槛（forward 须 ≥ backward×1.5 才算领先）
        partial_floor_ratio: 偏 IC 保持率下限（partial ≥ forward×0.5 才非伪相关）

    Raises:
        ValueError: 样本不足 min_samples 或序列长度不一致。
    """
    f = np.asarray(list(factor_values), dtype=float)
    r = np.asarray(list(forward_returns), dtype=float)
    if f.shape != r.shape:
        raise ValueError(f"因子与收益序列长度不一致: {len(f)} vs {len(r)}")
    n = len(f) - 1
    if n < min_samples:
        raise ValueError(f"样本不足: {n} < min_samples={min_samples}")
    forward_ic = _corr(f[:-1], r[1:])  # factor_t × ret_{t+1}
    backward_ic = _corr(r[:-1], f[1:])  # ret_t × factor_{t+1}
    if control_values is not None:
        c = np.asarray(list(control_values), dtype=float)
        if c.shape != f.shape:
            raise ValueError(f"控制序列长度不一致: {len(c)} vs {len(f)}")
        f_res = _residualize(f[:-1], c[:-1])
        r_res = _residualize(r[1:], c[1:])
        partial_ic = _corr(f_res, r_res)
    else:
        partial_ic = forward_ic

    abs_fwd = abs(forward_ic)
    if abs_fwd < ic_floor:
        verdict = CausalVerdict.INSIGNIFICANT
    elif abs(partial_ic) < abs_fwd * partial_floor_ratio:
        verdict = CausalVerdict.SPURIOUS
    elif abs_fwd >= abs(backward_ic) * lead_margin:
        verdict = CausalVerdict.CAUSAL_CANDIDATE
    else:
        verdict = CausalVerdict.CORRELATED
    return CausalAssessment(
        forward_ic=forward_ic,
        backward_ic=backward_ic,
        partial_ic=partial_ic,
        verdict=verdict,
        n_samples=n,
    )
