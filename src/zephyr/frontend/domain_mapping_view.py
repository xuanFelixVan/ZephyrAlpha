# [BLUEPRINT] MOD-FE-006 | docs/03_modules/_domain_frontend/domain_mapping_view/blueprint.md
# [MODULE] zephyr.frontend.domain_mapping_view
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（纯内存；architecture_model 实体快照/clock 全注入，装配批自 depgraph_reader 适配）
# [CONSUMERS] 运行时装配批（业务域×DB域映射矩阵/桑基图/孤儿清单面板数据供给）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 实体须在注入快照内; 域名单元非空; 同实体重复登记仅同三元组幂等(冲突拒绝); 矩阵单元格计数=桑基边权重(同一聚合); 孤儿=快照内未映射实体; 输出确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/domain_mapping_view/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DomainMappingError(占位 ZA-FE-UNREGISTERED-DOMAIN-MAPPING)——空快照/空实体/未知实体/空域名/冲突重复登记时抛
# [TESTS] tests/frontend/test_domain_mapping_view.py
# [A_module] module_id=MOD-FE-006 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""DomainMappingView — 业务域×DB域映射矩阵视图器（MOD-FE-006）。

B10-02409（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-007，A1 M6-S07）：
业务域×DB域映射矩阵/桑基图**数据底座**（只做后端数据不做页面接线）——
映射关系登记（注入 architecture_model 快照语义：实体集由快照给定）+
矩阵单元格计数聚合 + 桑基流量边（源→目标权重，与矩阵同一聚合口径）+
未映射孤儿清单。

查重分工（蓝图 §0）：depgraph_reader=依赖图 PG 查询接口（本件不查库，
实体快照经 DI 注入）；graph_view_renderer=通用 DAG 布局（无域矩阵/桑基
聚合语义）；value_stream_view=五段泳道（段词表闭合，零交集）。时钟 DI
注入（登记时间戳），其余纯内存确定性。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "DomainMapping",
    "DomainMappingError",
    "DomainMappingView",
    "MappingMatrix",
    "MatrixCell",
    "SankeyFlow",
]


class DomainMappingError(Exception):
    """域映射视图输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-DOMAIN-MAPPING。
    """


@dataclass(frozen=True)
class DomainMapping:
    """单实体映射登记（业务域 × DB 域，frozen）。"""

    entity_id: str
    business_domain: str
    db_domain: str
    registered_at: datetime.datetime


@dataclass(frozen=True)
class MatrixCell:
    """矩阵单元格计数（business_domain × db_domain → 实体数）。"""

    business_domain: str
    db_domain: str
    count: int


@dataclass(frozen=True)
class MappingMatrix:
    """映射矩阵 payload（行=业务域/列=DB域，均确定性排序，frozen）。"""

    rows: tuple[str, ...]
    cols: tuple[str, ...]
    cells: tuple[MatrixCell, ...]


@dataclass(frozen=True)
class SankeyFlow:
    """桑基流量边（源业务域 → 目标DB域，权重=实体数）。"""

    source: str
    target: str
    weight: int


class DomainMappingView:
    """域映射矩阵数据件（登记 + 矩阵聚合 + 桑基边 + 孤儿清单）。"""

    def __init__(
        self,
        *,
        known_entities: Iterable[str],
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        snapshot = set(known_entities)
        if not snapshot:
            raise DomainMappingError("architecture_model 快照为空（无实体可映射）")
        for entity_id in snapshot:
            if not entity_id:
                raise DomainMappingError("快照含空 entity_id")
        self._snapshot: frozenset[str] = frozenset(snapshot)
        self._clock = clock or datetime.datetime.now
        self._mappings: dict[str, DomainMapping] = {}

    # ── 登记 ─────────────────────────────────────────────────────────────

    def register_mapping(self, entity_id: str, business_domain: str, db_domain: str) -> None:
        """登记映射：实体须在快照内；同三元组幂等，冲突重复登记拒绝。"""
        if entity_id not in self._snapshot:
            raise DomainMappingError(f"未知实体: {entity_id!r}（不在 architecture_model 快照内）")
        if not business_domain:
            raise DomainMappingError("business_domain 为空")
        if not db_domain:
            raise DomainMappingError("db_domain 为空")
        existing = self._mappings.get(entity_id)
        if existing is not None:
            if (existing.business_domain, existing.db_domain) == (business_domain, db_domain):
                return  # 同三元组幂等
            raise DomainMappingError(
                f"实体 {entity_id!r} 已映射 {existing.business_domain!r}×{existing.db_domain!r}，"
                f"冲突重复登记 {business_domain!r}×{db_domain!r} 拒绝"
            )
        self._mappings[entity_id] = DomainMapping(
            entity_id=entity_id,
            business_domain=business_domain,
            db_domain=db_domain,
            registered_at=self._clock(),
        )
        _log.debug("映射登记: %s -> %s×%s", entity_id, business_domain, db_domain)

    # ── 聚合查询 ──────────────────────────────────────────────────────────

    def _cell_counts(self) -> dict[tuple[str, str], int]:
        counts: dict[tuple[str, str], int] = {}
        for mapping in self._mappings.values():
            key = (mapping.business_domain, mapping.db_domain)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def matrix(self) -> MappingMatrix:
        """矩阵单元格计数聚合（行/列/单元格均确定性排序）。"""
        counts = self._cell_counts()
        rows = tuple(sorted({biz for biz, _ in counts}))
        cols = tuple(sorted({db for _, db in counts}))
        cells = tuple(
            MatrixCell(business_domain=biz, db_domain=db, count=counts[(biz, db)])
            for biz, db in sorted(counts)
        )
        return MappingMatrix(rows=rows, cols=cols, cells=cells)

    def sankey_edges(self) -> tuple[SankeyFlow, ...]:
        """桑基流量边（源→目标权重=矩阵单元格计数，同一聚合口径）。"""
        counts = self._cell_counts()
        return tuple(
            SankeyFlow(source=biz, target=db, weight=counts[(biz, db)])
            for biz, db in sorted(counts)
        )

    def orphans(self) -> tuple[str, ...]:
        """未映射孤儿清单（快照内无映射登记的实体，排序确定性）。"""
        return tuple(sorted(self._snapshot - self._mappings.keys()))

    def mapping_of(self, entity_id: str) -> DomainMapping:
        """单实体映射查询（未登记/未知 → Fail-Closed）。"""
        mapping = self._mappings.get(entity_id)
        if mapping is None:
            raise DomainMappingError(f"实体未登记映射: {entity_id!r}")
        return mapping
