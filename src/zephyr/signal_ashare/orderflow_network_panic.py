# [BLUEPRINT] MOD-SIG-121 | docs/03_modules/_domain_signal/orderflow_network_panic/blueprint.md
# [MODULE] zephyr.signal_ashare.orderflow_network_panic
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（统计核心纯内存；granger_tester/clock 全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配：邻接矩阵 / Granger 检验器 / 节点收益接入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 回撤事件深度>阈值且窗口不重叠; Moran's I>0.3 判定聚集(零方差降级 0); 传导时滞 ∈ {1,2} 且 p<alpha; 扩散强度=事件深度×decay^hop 按 BFS 最短跳; 邻接矩阵须 n×n 非负且与排序后节点对齐; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/orderflow_network_panic/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OrderflowPanicError(占位 ZA-SIG-UNREGISTERED-ORDERFLOW-PANIC)——空序列/窗口或阈值越界/邻接非方阵/维度不齐/负权重/无边/检验器未注入/时滞越界时抛
# [TESTS] tests/signal_ashare/test_orderflow_network_panic.py
# [A_module] module_id=MOD-SIG-121 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""OrderflowNetworkPanic — 跨资产订单流网络与亏钱扩散（MOD-SIG-121）。

B10-01388（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-041，A1 模块52）：
大幅回撤事件检测（窗口回撤 >30%）+ 板块内 Moran's I 空间聚集统计
（>0.3 聚集判定，注入地理/行业邻接矩阵）+ 恐慌传导时滞（Granger 1-2 日
注入检验器）+ 扩散路径与强度输出。

查重分工（蓝图 §0）：market_breadth_collector=市场广度采集（本件=回撤
事件与网络扩散统计，不采集行情）；cross_market_conduction_sensor=跨市场
传导传感（本件=A 股板块/个股网络空间聚集与恐慌扩散，零交集）；
supply_chain_gnn=产业链 GNN 建模（本件注入邻接矩阵做统计判定，不建图
神经网络）。
"""

from __future__ import annotations

import datetime
import logging
import math
from collections import deque
from dataclasses import dataclass
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ConductionLink",
    "DiffusionPath",
    "DrawdownEvent",
    "OrderflowNetworkPanic",
    "OrderflowPanicError",
    "PanicAssessment",
]

#: 大幅回撤默认阈值（窗口回撤 >30%）
_DEFAULT_DRAWDOWN_THRESHOLD: Final = 0.30
#: Moran's I 聚集判定阈值（>0.3）
_DEFAULT_MORANS_THRESHOLD: Final = 0.3
#: Granger 传导最大时滞（1-2 日）
_DEFAULT_MAX_LAG: Final = 2
#: 传导显著性默认 alpha
_DEFAULT_ALPHA: Final = 0.05
#: 扩散强度逐跳衰减系数
_DEFAULT_DECAY: Final = 0.5
#: Granger 检验最短样本数
_MIN_CONDUCTION_SAMPLES: Final = 5


class OrderflowPanicError(Exception):
    """跨资产订单流网络与亏钱扩散输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-ORDERFLOW-PANIC。
    """


@dataclass(frozen=True)
class DrawdownEvent:
    """大幅回撤事件（窗口内峰值→谷值深度 > 阈值）。"""

    node: str
    peak_idx: int
    trough_idx: int
    depth: float  # (peak - trough) / peak ∈ (0,1)


@dataclass(frozen=True)
class ConductionLink:
    """恐慌传导边：source 收益 Granger 领先 target 收益 lag 日。"""

    source: str
    target: str
    lag: int  # ∈ {1,2}


@dataclass(frozen=True)
class DiffusionPath:
    """扩散路径：事件节点经邻接边 BFS 传播，强度逐跳衰减。"""

    source: str
    target: str
    hops: int  # BFS 最短跳数（>= 1）
    strength: float  # 事件深度 × decay^hops


@dataclass(frozen=True)
class PanicAssessment:
    """亏钱扩散综合评估输出（frozen）。"""

    events: tuple[DrawdownEvent, ...]
    morans_i: float
    is_clustered: bool
    conduction_links: tuple[ConductionLink, ...]
    diffusion_paths: tuple[DiffusionPath, ...]
    is_panic: bool  # 有回撤事件 且 空间聚集
    assessed_at: datetime.datetime


def _as_finite_series(name: str, values: Sequence[float], *, min_len: int = 1) -> tuple[float, ...]:
    """序列校验：长度下限 + 全部有限值，非法 Fail-Closed。"""
    try:
        seq = tuple(float(v) for v in values)
    except (TypeError, ValueError) as exc:
        raise OrderflowPanicError(f"{name} 含非数值元素: {exc}") from exc
    if len(seq) < min_len:
        raise OrderflowPanicError(f"{name} 长度 {len(seq)} < 下限 {min_len}")
    for v in seq:
        if not math.isfinite(v):
            raise OrderflowPanicError(f"{name} 含非有限值: {v!r}")
    return seq


def _max_drawdown(series: Sequence[float]) -> tuple[int, int, float]:
    """全序列最大回撤 (peak_idx, trough_idx, depth)；单调不降退化为 0。"""
    peak = series[0]
    peak_idx = 0
    best = (0, 0, 0.0)
    for j in range(1, len(series)):
        if series[j] > peak:
            peak = series[j]
            peak_idx = j
        if peak > 0.0:
            dd = (peak - series[j]) / peak
            if dd > best[2]:
                best = (peak_idx, j, dd)
    return best


class OrderflowNetworkPanic:
    """亏钱扩散统计件（纯内存；邻接矩阵 / Granger 检验器 / 时钟注入）。

    Args:
        granger_tester: Granger 检验回调
            ``tester(source_returns, target_returns, lag) -> p_value``，
            语义为「source 在 lag 日处 Granger 领先 target」；未注入则
            传导时滞判定 Fail-Closed。
        clock: 时钟注入（测试可控）；缺省系统时钟。
    """

    def __init__(
        self,
        *,
        granger_tester: Callable[[Sequence[float], Sequence[float], int], float] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._granger_tester = granger_tester
        self._clock = clock or datetime.datetime.now

    # ── 大幅回撤事件检测 ──────────────────────────────────────────────────

    def detect_drawdown_events(
        self,
        node: str,
        prices: Sequence[float],
        *,
        window: int,
        threshold: float = _DEFAULT_DRAWDOWN_THRESHOLD,
    ) -> tuple[DrawdownEvent, ...]:
        """窗口回撤 > 阈值的事件检测（事件区间不重叠，确定性）。"""
        if not node:
            raise OrderflowPanicError("node 为空")
        if window < 2:
            raise OrderflowPanicError(f"window 非法: {window!r}（须 >= 2）")
        if not 0.0 < threshold < 1.0:
            raise OrderflowPanicError(f"threshold 非法: {threshold!r}（须 ∈ (0,1)）")
        series = _as_finite_series("prices", prices, min_len=window)
        for p in series:
            if p <= 0.0:
                raise OrderflowPanicError(f"价格非正: {p!r}")

        events: list[DrawdownEvent] = []
        i = 0
        n = len(series)
        while i + window <= n:
            seg = series[i:i + window]
            peak_off, trough_off, depth = _max_drawdown(seg)
            if depth > threshold:
                events.append(DrawdownEvent(
                    node=node,
                    peak_idx=i + peak_off,
                    trough_idx=i + trough_off,
                    depth=depth,
                ))
                i += trough_off + 1  # 跳过事件覆盖区间，防重叠重复
            else:
                i += 1
        return tuple(events)

    # ── Moran's I 空间聚集 ────────────────────────────────────────────────

    def morans_i(
        self,
        values: Sequence[float],
        adjacency: Sequence[Sequence[float]],
    ) -> float:
        """Moran's I = (n/S0)·ΣΣ w_ij·dx_i·dx_j / Σ dx_i²；零方差降级 0.0。"""
        xs = _as_finite_series("values", values, min_len=2)
        n = len(xs)
        w = self._check_adjacency(adjacency, n)
        if all(x == xs[0] for x in xs):
            return 0.0  # 全部相等无空间结构可言（降级不触发）
        mean = sum(xs) / n
        dev = [x - mean for x in xs]
        denom = sum(d * d for d in dev)
        if denom == 0.0:
            return 0.0
        s0 = sum(sum(row) for row in w)
        if s0 == 0.0:
            raise OrderflowPanicError("邻接矩阵无边（S0=0，Moran's I 无定义）")
        num = sum(
            w[i][j] * dev[i] * dev[j]
            for i in range(n)
            for j in range(n)
            if w[i][j] != 0.0
        )
        return (n / s0) * (num / denom)

    def _check_adjacency(
        self,
        adjacency: Sequence[Sequence[float]],
        n: int,
    ) -> tuple[tuple[float, ...], ...]:
        """邻接矩阵校验：n×n 方阵、非负、有限。"""
        try:
            rows = tuple(tuple(float(v) for v in row) for row in adjacency)
        except (TypeError, ValueError) as exc:
            raise OrderflowPanicError(f"邻接矩阵含非数值元素: {exc}") from exc
        if len(rows) != n:
            raise OrderflowPanicError(
                f"邻接矩阵维度不齐: {len(rows)} 行 vs 节点数 {n}"
            )
        for row in rows:
            if len(row) != n:
                raise OrderflowPanicError(
                    f"邻接矩阵非方阵: 行长 {len(row)} != {n}"
                )
            for v in row:
                if not math.isfinite(v):
                    raise OrderflowPanicError(f"邻接矩阵含非有限值: {v!r}")
                if v < 0.0:
                    raise OrderflowPanicError(f"邻接矩阵含负权重: {v!r}")
        return rows

    # ── 恐慌传导时滞（Granger 注入检验器）─────────────────────────────────

    def panic_conduction_lag(
        self,
        source_returns: Sequence[float],
        target_returns: Sequence[float],
        *,
        max_lag: int = _DEFAULT_MAX_LAG,
        alpha: float = _DEFAULT_ALPHA,
    ) -> int | None:
        """最小显著传导时滞（1..max_lag 首个 p<alpha）；不显著返回 None。"""
        if self._granger_tester is None:
            raise OrderflowPanicError(
                "granger_tester 未注入（恐慌传导时滞判定强制注入检验器）"
            )
        if max_lag not in (1, 2):
            raise OrderflowPanicError(f"max_lag 非法: {max_lag!r}（须 ∈ {{1,2}}）")
        if not 0.0 < alpha < 1.0:
            raise OrderflowPanicError(f"alpha 非法: {alpha!r}（须 ∈ (0,1)）")
        src = _as_finite_series(
            "source_returns", source_returns, min_len=_MIN_CONDUCTION_SAMPLES
        )
        tgt = _as_finite_series(
            "target_returns", target_returns, min_len=_MIN_CONDUCTION_SAMPLES
        )
        if len(src) != len(tgt):
            raise OrderflowPanicError(
                f"传导序列长度不齐: {len(src)} vs {len(tgt)}"
            )
        for lag in range(1, max_lag + 1):
            try:
                p_value = float(self._granger_tester(src, tgt, lag))
            except Exception as exc:  # noqa: BLE001 — 检验器异常 Fail-Closed
                raise OrderflowPanicError(f"granger_tester 异常(lag={lag}): {exc}") from exc
            if not math.isfinite(p_value):
                raise OrderflowPanicError(f"granger_tester 返回非有限 p 值: {p_value!r}")
            if p_value < alpha:
                return lag
        return None

    # ── 扩散路径（BFS）────────────────────────────────────────────────────

    def diffusion_paths(
        self,
        nodes: Sequence[str],
        sources: Mapping[str, float],
        adjacency: Sequence[Sequence[float]],
        *,
        decay: float = _DEFAULT_DECAY,
    ) -> tuple[DiffusionPath, ...]:
        """自事件节点 BFS 扩散，强度 = 事件深度 × decay^hops。

        Args:
            nodes: 全网络节点名（排序后与邻接矩阵行列对齐）。
            sources: {事件节点: 事件深度}，须为 nodes 子集且深度 > 0。
            adjacency: n×n 非负邻接矩阵（n = len(nodes)）。
            decay: 逐跳衰减系数 ∈ (0,1)。
        """
        node_tuple = tuple(sorted(nodes))
        if not node_tuple:
            raise OrderflowPanicError("nodes 为空")
        if len(set(node_tuple)) != len(node_tuple):
            raise OrderflowPanicError("nodes 含重复节点")
        if not sources:
            raise OrderflowPanicError("sources 为空（无扩散源）")
        if not 0.0 < decay < 1.0:
            raise OrderflowPanicError(f"decay 非法: {decay!r}（须 ∈ (0,1)）")
        unknown = sorted(set(sources) - set(node_tuple))
        if unknown:
            raise OrderflowPanicError(f"扩散源不在节点全集: {unknown!r}")
        n = len(node_tuple)
        w = self._check_adjacency(adjacency, n)
        index = {name: i for i, name in enumerate(node_tuple)}
        paths: list[DiffusionPath] = []
        for src in sorted(sources):
            depth = float(sources[src])
            if not math.isfinite(depth) or depth <= 0.0:
                raise OrderflowPanicError(f"事件深度非法: {src}={depth!r}")
            # BFS（邻居按索引升序，确定性）
            hops_of: dict[str, int] = {src: 0}
            queue: deque[str] = deque([src])
            while queue:
                cur = queue.popleft()
                ci = index[cur]
                for j in range(n):
                    if w[ci][j] <= 0.0:
                        continue
                    nxt = node_tuple[j]
                    if nxt in hops_of:
                        continue
                    hops_of[nxt] = hops_of[cur] + 1
                    queue.append(nxt)
            for target, hops in hops_of.items():
                if hops == 0:
                    continue
                paths.append(DiffusionPath(
                    source=src,
                    target=target,
                    hops=hops,
                    strength=depth * (decay ** hops),
                ))
        paths.sort(key=lambda p: (p.hops, p.source, p.target))
        return tuple(paths)

    # ── 综合评估 ──────────────────────────────────────────────────────────

    def assess(
        self,
        *,
        node_returns: Mapping[str, Sequence[float]],
        adjacency: Sequence[Sequence[float]],
        window: int,
        drawdown_threshold: float = _DEFAULT_DRAWDOWN_THRESHOLD,
        morans_threshold: float = _DEFAULT_MORANS_THRESHOLD,
        max_lag: int = _DEFAULT_MAX_LAG,
        alpha: float = _DEFAULT_ALPHA,
        decay: float = _DEFAULT_DECAY,
    ) -> PanicAssessment:
        """亏钱扩散综合评估（确定性聚合；时钟注入留痕）。

        Args:
            node_returns: {节点: 日收益序列}（等长；邻接矩阵与排序后节点对齐）。
            adjacency: n×n 非负邻接矩阵（行业/地理邻接，注入）。
            window: 回撤检测窗口（交易日）。
            drawdown_threshold: 大幅回撤阈值（>30% 语义，严格大于）。
            morans_threshold: Moran's I 聚集判定阈值（>0.3 语义，严格大于）。
            max_lag: Granger 传导最大时滞（1-2 日）。
            alpha: 传导显著性水平。
            decay: 扩散强度逐跳衰减。
        """
        if not node_returns:
            raise OrderflowPanicError("node_returns 为空")
        if not 0.0 < morans_threshold:
            raise OrderflowPanicError(
                f"morans_threshold 非法: {morans_threshold!r}（须 > 0）"
            )
        nodes = tuple(sorted(node_returns))
        series: dict[str, tuple[float, ...]] = {}
        length: int | None = None
        for name in nodes:
            seq = _as_finite_series(f"node_returns[{name!r}]", node_returns[name])
            if length is None:
                length = len(seq)
            elif len(seq) != length:
                raise OrderflowPanicError("node_returns 各节点序列长度不齐")
            series[name] = seq
        self._check_adjacency(adjacency, len(nodes))

        # ① 回撤事件（收益→净值曲线后窗口检测）
        events: list[DrawdownEvent] = []
        depths: dict[str, float] = {}
        for name in nodes:
            equity: list[float] = [1.0]
            for r in series[name]:
                equity.append(equity[-1] * (1.0 + r))
            _, _, full_depth = _max_drawdown(equity)
            depths[name] = full_depth
            events.extend(self.detect_drawdown_events(
                name, equity, window=window + 1, threshold=drawdown_threshold,
            ))
        events.sort(key=lambda e: (e.node, e.trough_idx))

        # ② Moran's I 空间聚集（截面值=各节点全序列最大回撤深度）
        morans = self.morans_i([depths[name] for name in nodes], adjacency)
        is_clustered = morans > morans_threshold

        # ③ 恐慌传导时滞（事件节点两两有序对，Granger 注入检验）
        event_nodes = tuple(sorted({e.node for e in events}))
        links: list[ConductionLink] = []
        for src in event_nodes:
            for tgt in event_nodes:
                if src == tgt:
                    continue
                lag = self.panic_conduction_lag(
                    series[src], series[tgt], max_lag=max_lag, alpha=alpha,
                )
                if lag is not None:
                    links.append(ConductionLink(source=src, target=tgt, lag=lag))

        # ④ 扩散路径与强度（无事件源 → 空路径）
        paths: tuple[DiffusionPath, ...] = ()
        if event_nodes:
            src_depths = {
                name: max(e.depth for e in events if e.node == name)
                for name in event_nodes
            }
            paths = self.diffusion_paths(nodes, src_depths, adjacency, decay=decay)

        is_panic = bool(events) and is_clustered
        _log.info(
            "亏钱扩散评估: events=%d morans=%.4f clustered=%s links=%d paths=%d panic=%s",
            len(events), morans, is_clustered, len(links), len(paths), is_panic,
        )
        return PanicAssessment(
            events=tuple(events),
            morans_i=morans,
            is_clustered=is_clustered,
            conduction_links=tuple(links),
            diffusion_paths=paths,
            is_panic=is_panic,
            assessed_at=self._clock(),
        )
