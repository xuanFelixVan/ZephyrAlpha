# [BLUEPRINT] MOD-GOV-053 | docs/03_modules/_domain_gov_audit/audit_trace_graph_builder/blueprint.md
# [MODULE] zephyr.gov_audit.audit_trace_graph_builder
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] 无（追踪图纯内存；节点/边登记全经入参，无副作用无外部调用）
# [CONSUMERS] 运行时装配批（合规证据包装配：四段边登记 + 缺口报告统一注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 段词表闭合(decision|code|test|deploy); 合法边仅相邻段向下(decision→code→test→deploy); 节点/边登记幂等去重; 全链反查/缺口清单/补齐建议全确定性排序; deploy 无出边/非 decision 须有入边为链完整必要条件; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_gov_audit/audit_trace_graph_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AuditTraceError(占位 ZA-GOVA-UNREGISTERED-AUDIT-TRACE)——空node_id/非法段/重复节点/未知节点/自环/越段或逆向边时抛
# [TESTS] tests/gov_audit/test_audit_trace_graph_builder.py
# [A_module] module_id=MOD-GOV-053 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AuditTraceGraphBuilder — 审计追踪依赖构建器（MOD-GOV-053）。

B14-04667（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-GOVAUDIT-004，A9
M48-S01）：审计追踪依赖图——决策→代码→测试→部署四段全链边登记
（段词表闭合）+ 全链反查 + 缺口自动检测（缺段/断链清单）+ 补齐建议
输出 + 图数据供合规证据包复用。SLSA provenance 思想。

查重分工（蓝图 §0）：merkle_audit=审计哈希链（本件=四段依赖图结构，
不做哈希）；provenance_tracker=产物来源追踪（本件=决策到部署全链完
整性缺口，零交集）；evidence_pack=证据包组装（本件图数据供其复用，
不组装证据包）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AuditTraceError",
    "AuditTraceGraphBuilder",
    "GapKind",
    "GapReport",
    "TraceEdge",
    "TraceGap",
    "TraceNode",
    "TraceSegment",
]

#: 段序号（合法边仅 rank 大 = rank 小 + 1 相邻向下）
_SEGMENT_RANK: Final[dict["TraceSegment", int]] = {}


class AuditTraceError(Exception):
    """审计追踪图输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOVA-UNREGISTERED-AUDIT-TRACE。
    """


class TraceSegment(str, Enum):
    """追踪段词表（闭合）：决策→代码→测试→部署。"""

    DECISION = "decision"
    CODE = "code"
    TEST = "test"
    DEPLOY = "deploy"


_SEGMENT_RANK.update({
    TraceSegment.DECISION: 0,
    TraceSegment.CODE: 1,
    TraceSegment.TEST: 2,
    TraceSegment.DEPLOY: 3,
})

#: 段序 → 段名（缺口建议文案用；词表闭合派生）
_SEGMENT_ORDER: Final[dict[int, str]] = {
    rank: seg.value for seg, rank in _SEGMENT_RANK.items()
}


class GapKind(str, Enum):
    """缺口类型（闭合）：缺段 / 断链。"""

    MISSING_SEGMENT = "missing_segment"
    BROKEN_LINK = "broken_link"


@dataclass(frozen=True)
class TraceNode:
    """追踪图节点（frozen；node_id 全局唯一）。"""

    node_id: str
    segment: TraceSegment
    label: str


@dataclass(frozen=True)
class TraceEdge:
    """追踪图边（src → dst，仅相邻段向下，frozen）。"""

    src_id: str
    dst_id: str


@dataclass(frozen=True)
class TraceGap:
    """缺口条目（缺段/断链，frozen）。"""

    kind: GapKind
    node_id: str
    segment: TraceSegment
    detail: str


@dataclass(frozen=True)
class GapReport:
    """缺口检测报告（确定性排序，frozen）。

    gaps: 缺段/断链清单。
    suggestions: 补齐建议（与 gaps 一一对应排序后输出）。
    """

    gaps: tuple[TraceGap, ...]
    suggestions: tuple[str, ...]


class AuditTraceGraphBuilder:
    """审计追踪依赖图（四段边登记 + 全链反查 + 缺口检测 + 补齐建议）。"""

    def __init__(self) -> None:
        self._nodes: dict[str, TraceNode] = {}
        self._edges: set[TraceEdge] = set()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _node(self, node_id: str) -> TraceNode:
        node = self._nodes.get(node_id)
        if node is None:
            raise AuditTraceError(f"未知节点: {node_id!r}")
        return node

    def _upstream(self, node_id: str) -> set[str]:
        """沿入边递归收集全部祖先（含自身）。"""
        seen: set[str] = set()
        stack = [node_id]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(e.src_id for e in self._edges if e.dst_id == cur)
        return seen

    def _downstream(self, node_id: str) -> set[str]:
        """沿出边递归收集全部后代（含自身）。"""
        seen: set[str] = set()
        stack = [node_id]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(e.dst_id for e in self._edges if e.src_id == cur)
        return seen

    # ── 登记 ─────────────────────────────────────────────────────────────

    def register_node(
        self, node_id: str, segment: TraceSegment, label: str = ""
    ) -> None:
        """登记节点：段词表闭合；node_id 重复 Fail-Closed。"""
        if not node_id:
            raise AuditTraceError("node_id 为空")
        if not isinstance(segment, TraceSegment):
            raise AuditTraceError(f"非法追踪段: {segment!r}")
        if node_id in self._nodes:
            raise AuditTraceError(f"节点重复: {node_id!r}")
        self._nodes[node_id] = TraceNode(node_id=node_id, segment=segment, label=label)
        _log.info("追踪节点登记: %s (%s)", node_id, segment.value)

    def register_edge(self, src_id: str, dst_id: str) -> None:
        """登记边：两端须已登记；仅相邻段向下；自环拒绝；幂等去重。"""
        src = self._node(src_id)
        dst = self._node(dst_id)
        if src_id == dst_id:
            raise AuditTraceError(f"自环非法: {src_id!r}")
        if _SEGMENT_RANK[dst.segment] != _SEGMENT_RANK[src.segment] + 1:
            raise AuditTraceError(
                f"越段/逆向边拒绝: {src_id}({src.segment.value}) -> "
                f"{dst_id}({dst.segment.value})，合法仅相邻段向下"
            )
        self._edges.add(TraceEdge(src_id=src_id, dst_id=dst_id))  # set 幂等

    # ── 查询 ─────────────────────────────────────────────────────────────

    def nodes(self) -> tuple[TraceNode, ...]:
        """全部节点（按 (段序, node_id) 确定性排序）。"""
        return tuple(
            sorted(
                self._nodes.values(),
                key=lambda n: (_SEGMENT_RANK[n.segment], n.node_id),
            )
        )

    def edges(self) -> tuple[TraceEdge, ...]:
        """全部边（按 (src_id, dst_id) 确定性排序）。"""
        return tuple(sorted(self._edges, key=lambda e: (e.src_id, e.dst_id)))

    def chain_of(self, node_id: str) -> tuple[TraceNode, ...]:
        """全链反查：含该节点的完整链视图（祖先 ∪ 后代，段序确定性排序）。"""
        self._node(node_id)
        chain_ids = self._upstream(node_id) | self._downstream(node_id)
        return tuple(
            sorted(
                (self._nodes[i] for i in chain_ids),
                key=lambda n: (_SEGMENT_RANK[n.segment], n.node_id),
            )
        )

    def reachable_segments(self, node_id: str) -> tuple[TraceSegment, ...]:
        """自该节点沿出边可达的段集合（段序排序，确定性）。"""
        self._node(node_id)
        segs = {
            self._nodes[i].segment for i in self._downstream(node_id) if i != node_id
        }
        return tuple(sorted(segs, key=lambda s: _SEGMENT_RANK[s]))

    # ── 缺口检测 ──────────────────────────────────────────────────────────

    def gap_report(self) -> GapReport:
        """缺口自动检测：缺段（决策链不达四段）+ 断链（缺入/出边）+ 补齐建议。"""
        gaps: list[TraceGap] = []
        suggestions: list[str] = []
        ordered = sorted(
            self._nodes.values(), key=lambda n: (_SEGMENT_RANK[n.segment], n.node_id)
        )
        incoming: dict[str, list[TraceEdge]] = {n.node_id: [] for n in ordered}
        outgoing: dict[str, list[TraceEdge]] = {n.node_id: [] for n in ordered}
        for edge in self._edges:
            incoming[edge.dst_id].append(edge)
            outgoing[edge.src_id].append(edge)

        for node in ordered:
            rank = _SEGMENT_RANK[node.segment]
            if node.segment is TraceSegment.DECISION:
                # 缺段：决策链须可达 code/test/deploy 三段
                reached = set(self.reachable_segments(node.node_id))
                for seg in (TraceSegment.CODE, TraceSegment.TEST, TraceSegment.DEPLOY):
                    if seg not in reached:
                        gaps.append(TraceGap(
                            kind=GapKind.MISSING_SEGMENT,
                            node_id=node.node_id,
                            segment=seg,
                            detail=(
                                f"缺段: 决策 {node.node_id} 全链不可达 "
                                f"{seg.value} 段"
                            ),
                        ))
                        suggestions.append(
                            f"为决策 {node.node_id} 补齐 {seg.value} 段节点并登记 "
                            f"{_SEGMENT_ORDER[_SEGMENT_RANK[seg] - 1]}→{seg.value} 相邻边"
                        )
            if rank > 0 and not incoming[node.node_id]:
                prev = _SEGMENT_ORDER[rank - 1]
                gaps.append(TraceGap(
                    kind=GapKind.BROKEN_LINK,
                    node_id=node.node_id,
                    segment=node.segment,
                    detail=(
                        f"断链: 节点 {node.node_id}({node.segment.value}) "
                        f"无 {prev} 段入边"
                    ),
                ))
                suggestions.append(
                    f"为节点 {node.node_id}({node.segment.value}) 登记来自 "
                    f"{prev} 段的上游边"
                )
            if rank < 3 and not outgoing[node.node_id]:
                nxt = _SEGMENT_ORDER[rank + 1]
                gaps.append(TraceGap(
                    kind=GapKind.BROKEN_LINK,
                    node_id=node.node_id,
                    segment=node.segment,
                    detail=(
                        f"断链: 节点 {node.node_id}({node.segment.value}) "
                        f"无 {nxt} 段出边"
                    ),
                ))
                suggestions.append(
                    f"为节点 {node.node_id}({node.segment.value}) 登记指向 "
                    f"{nxt} 段的下游边"
                )
        if gaps:
            _log.warning("审计追踪缺口: %d 条", len(gaps))
        return GapReport(gaps=tuple(gaps), suggestions=tuple(suggestions))
