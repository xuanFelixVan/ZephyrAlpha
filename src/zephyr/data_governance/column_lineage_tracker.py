# [BLUEPRINT] MOD-DATA_GOV-012 | docs/03_modules/_domain_data_governance/column_lineage_tracker/blueprint.md
# [MODULE] zephyr.data_governance.column_lineage_tracker
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] 无（纯内存；与 core/lineage_tracker 边语义对齐并扩展列级映射）
# [CONSUMERS] 运行时装配批（SQL 解析列映射登记 / 删列影响面评审 / 重构门禁）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 列引用 table.column 二元闭合; 映射边唯一(source_col,target_col)幂等更新transform; 有向无环(加边成环拒绝); 上下游闭包按 (table,column) 确定性排序去重; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_governance/column_lineage_tracker/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ColumnLineageError(占位 ZA-DATA-UNREGISTERED-COLUMN-LINEAGE)——空表/列名/非法引用格式/自映射/成环时抛
# [TESTS] tests/data_governance/test_column_lineage_tracker.py
# [A_module] module_id=MOD-DATA_GOV-012 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
column_lineage_tracker — 列级血缘追踪器（MOD-DATA_GOV-012）。

B10-02321（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-009，A1 M8-NEW-02）：
列级血缘——血缘边扩展 **column 映射**（source_col -> target_col + transform
表达式字段）+ 登记接口 + 列级上下游查询（给定 表.列 查上游列链/下游影响列）
+ 列级影响分析（**删列影响面**）。

查重分工（蓝图 §0）：core/lineage_tracker=表/因子/信号级血缘图（本件=列级
粒度独立图，不改其存储）；core/column_lineage_analyzer=SQL 静态解析产出列映
射（本件=映射登记与查询门面，解析结果经登记接口注入）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: column_lineage_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① ColumnRef
#   name_en: ColumnRef
#   intro: 列引用（table.column 二元闭合，frozen）。
#   desc: 列引用（table.column 二元闭合，frozen）。；公共方法（定义序）: parse；源码 L89-L106
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ColumnLineageTracker
#   name_en: ColumnLineageTracker
#   intro: 列级血缘追踪器（映射登记 + 上下游查询 + 删列影响面）。
#   desc: 列级血缘追踪器（映射登记 + 上下游查询 + 删列影响面）。；公共方法（定义序）: register, register_mapping, mappings, direct_upstream, direct_downs…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ColumnRef, ColumnLineageTracker
#   downstream: 运行时装配批（SQL 解析列映射登记 / 删列影响面评审 / 重构门禁）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "ColumnLineageError",
    "ColumnLineageTracker",
    "ColumnMapping",
    "ColumnRef",
]


class ColumnLineageError(Exception):
    """列级血缘登记/查询输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-COLUMN-LINEAGE。
    """


@dataclass(frozen=True, order=True)
class ColumnRef:
    """列引用（table.column 二元闭合，frozen）。"""

    table: str
    column: str

    @classmethod
    def parse(cls, ref: str) -> ColumnRef:
        """解析 "table.column"（恰一个点，两侧非空，否则 Fail-Closed）。"""
        if ref.count(".") != 1:
            raise ColumnLineageError(f"非法列引用格式(须 table.column): {ref!r}")
        table, column = ref.split(".")
        if not table or not column:
            raise ColumnLineageError(f"列引用端点为空: {ref!r}")
        return cls(table=table, column=column)

    def __str__(self) -> str:
        return f"{self.table}.{self.column}"


@dataclass(frozen=True)
class ColumnMapping:
    """列级映射边（source_col -> target_col + transform 表达式，frozen）。"""

    source: ColumnRef
    target: ColumnRef
    transform: str = ""


class ColumnLineageTracker:
    """列级血缘追踪器（映射登记 + 上下游查询 + 删列影响面）。"""

    def __init__(self) -> None:
        self._edges: dict[tuple[ColumnRef, ColumnRef], ColumnMapping] = {}
        self._downstream: dict[ColumnRef, set[ColumnRef]] = {}
        self._upstream: dict[ColumnRef, set[ColumnRef]] = {}

    # ── 登记 ─────────────────────────────────────────────────────────────

    def register(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: str,
        transform: str = "",
    ) -> ColumnMapping:
        """登记列映射：空名/自映射/成环拒绝；同边幂等更新 transform。"""
        if not source_table or not source_column or not target_table or not target_column:
            raise ColumnLineageError(
                f"表/列名存在空值: {source_table!r}.{source_column!r} -> {target_table!r}.{target_column!r}"
            )
        return self.register_mapping(
            ColumnMapping(
                source=ColumnRef(source_table, source_column),
                target=ColumnRef(target_table, target_column),
                transform=transform,
            )
        )

    def register_mapping(self, mapping: ColumnMapping) -> ColumnMapping:
        """登记 ColumnMapping 值对象（语义同 register）。"""
        source, target = mapping.source, mapping.target
        if not source.table or not source.column or not target.table or not target.column:
            raise ColumnLineageError(f"映射端点含空表/列名: {mapping!r}")
        if source == target:
            raise ColumnLineageError(f"自映射非法: {source}")
        key = (source, target)
        if key in self._edges:
            self._edges[key] = mapping  # 幂等更新 transform
            return mapping
        if self._reachable(target, source):
            raise ColumnLineageError(f"加边成环拒绝: {source} -> {target}（{target} 已是 {source} 上游）")
        self._edges[key] = mapping
        self._downstream.setdefault(source, set()).add(target)
        self._upstream.setdefault(target, set()).add(source)
        _log.debug("列映射登记: %s -> %s (%s)", source, target, mapping.transform)
        return mapping

    # ── 查询 ─────────────────────────────────────────────────────────────

    def mappings(self) -> tuple[ColumnMapping, ...]:
        """全部映射（按 (source,target) 确定性排序）。"""
        return tuple(self._edges[k] for k in sorted(self._edges))

    def direct_upstream(self, table: str, column: str) -> tuple[ColumnRef, ...]:
        """直接上游列（排序）。"""
        ref = ColumnRef(table, column)
        return tuple(sorted(self._upstream.get(ref, ())))

    def direct_downstream(self, table: str, column: str) -> tuple[ColumnRef, ...]:
        """直接下游列（排序）。"""
        ref = ColumnRef(table, column)
        return tuple(sorted(self._downstream.get(ref, ())))

    def upstream_columns(self, table: str, column: str) -> tuple[ColumnRef, ...]:
        """上游列链闭包（BFS，未知节点返回空，排序去重）。"""
        return self._closure(ColumnRef(table, column), self._upstream)

    def downstream_columns(self, table: str, column: str) -> tuple[ColumnRef, ...]:
        """下游影响列闭包（BFS，未知节点返回空，排序去重）。"""
        return self._closure(ColumnRef(table, column), self._downstream)

    def drop_column_impact(self, table: str, column: str) -> tuple[ColumnRef, ...]:
        """删列影响面：该列下游全部受影响列（闭包，排序去重）。"""
        return self.downstream_columns(table, column)

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _reachable(self, start: ColumnRef, goal: ColumnRef) -> bool:
        """沿下游索引查 start 是否可达 goal（用于成环预判）。"""
        visited: set[ColumnRef] = set()
        stack: list[ColumnRef] = [start]
        while stack:
            node = stack.pop()
            if node == goal:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(self._downstream.get(node, ()))
        return False

    @staticmethod
    def _closure(seed: ColumnRef, index: dict[ColumnRef, set[ColumnRef]]) -> tuple[ColumnRef, ...]:
        visited: set[ColumnRef] = set()
        stack: list[ColumnRef] = list(index.get(seed, ()))
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            stack.extend(index.get(node, ()))
        return tuple(sorted(visited))
