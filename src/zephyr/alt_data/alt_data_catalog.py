# [BLUEPRINT] MOD-ALT-008 | docs/03_modules/_domain_alt_data/alt_data_catalog/blueprint.md
# [MODULE] zephyr.alt_data.alt_data_catalog
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（目录核心纯内存；lineage_sink/fts_connection/clock 全注入；血缘语义参照 zephyr.data_governance.core.lineage_tracker）
# [CONSUMERS] 运行时装配批（元数据登记入目录 / 真实 LineageTracker 与 SQLite FTS5 连接绑定 / 生命周期审批流）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 数据源类型词表闭合(news|announcement|social|research|policy|other); quality_score恒∈[0,1]有限值; cost_quota恒≥0 int(拒bool); 标签去重升序确定性; 生命周期状态机 REGISTERED→APPROVED→OFFLINE 不可逆越迁Fail-Closed; 血缘强制经lineage_sink回调(未注入Fail-Closed不旁路); FTS5检索注入连接(未注入Fail-Closed)结果按source_id升序确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/alt_data_catalog/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AltDataCatalogError(占位 ZA-ALT-UNREGISTERED-ALT-CATALOG)——重复/未知source_id、非法类型/质量分/配额/标签、非法状态迁移、lineage_sink缺失或回调失败、fts_connection缺失/查询空/语法错时抛
# [TESTS] tests/alt_data/test_alt_data_catalog.py
# [A_module] module_id=MOD-ALT-008 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AltDataCatalog — 另类数据目录（MOD-ALT-008）。

B5-07089（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-024，B5 D-ALT-DATA-09，
canonical 承接 TESTA-011 归并）：数据源/数据集**元数据登记**（source_id/类型/
更新频率/质量分/成本配额/接入状态）+**标签系统**+血缘挂 **lineage_tracker
回调**+**SQLite FTS5 检索**（注入连接）+**注册-审批-下线**生命周期状态机。

查重分工（蓝图 §0）：lineage_tracker=血缘有向图实现（本件仅经注入回调挂边，
不重建图）；alt_data_connector=接入同步协议（本件=目录元数据面，不做抓取）；
alt_data_compliance_reviewer=合规台账（本件生命周期仅接入状态，不做合规审
查）；web_scraper_engine=采集引擎（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: alt_data_catalog.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lineage_sink 参数
#   fields: 参数 lineage_sink（无注解）
#   code: alt_data_catalog.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: fts_connection 参数
#   fields: 参数 fts_connection（无注解）
#   code: alt_data_catalog.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AltDataCatalog
#   name_en: AltDataCatalog
#   intro: 另类数据目录（元数据登记 + 标签 + 血缘回调 + FTS5 检索 + 生命周期）。
#   desc: 另类数据目录（元数据登记 + 标签 + 血缘回调 + FTS5 检索 + 生命周期）。；公共方法（定义序）: register, get, add_tags, remove_tags, tags_of, approve…
#   inputs: clock lineage_sink fts_connection
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: AltDataCatalog
#   downstream: 运行时装配批（元数据登记入目录 / 真实 LineageTracker 与 SQLite FTS5 连接绑定 / 生命周期审批流）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
import sqlite3
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AltDataCatalog",
    "AltDataCatalogError",
    "CatalogEntry",
    "CatalogLifecycle",
    "CatalogRecord",
    "CatalogSourceType",
]

#: FTS5 虚表名（注入连接内建表）
_FTS_TABLE: Final = "alt_data_catalog_fts"


class AltDataCatalogError(Exception):
    """另类数据目录输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-ALT-CATALOG。
    """


class CatalogSourceType(str, Enum):
    """数据源类型（词表闭合）。"""

    NEWS = "news"
    ANNOUNCEMENT = "announcement"
    SOCIAL = "social"
    RESEARCH = "research"
    POLICY = "policy"
    OTHER = "other"


class CatalogLifecycle(str, Enum):
    """生命周期状态机：REGISTERED → APPROVED → OFFLINE（不可逆）。"""

    REGISTERED = "registered"
    APPROVED = "approved"
    OFFLINE = "offline"


@dataclass(frozen=True)
class CatalogEntry:
    """数据源元数据（登记载体，frozen）。"""

    source_id: str
    source_type: CatalogSourceType
    update_frequency: str
    quality_score: float
    cost_quota: int
    description: str = ""
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CatalogRecord:
    """目录记录（元数据 + 生命周期状态，frozen）。"""

    entry: CatalogEntry
    state: CatalogLifecycle
    registered_at: datetime.datetime
    state_updated_at: datetime.datetime


def _validate_tags(tags: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """标签校验 + 归一（去重升序，确定性）。"""
    if not isinstance(tags, (tuple, list)):
        raise AltDataCatalogError(f"tags 类型非法: {type(tags)!r}（须 tuple/list[str]）")
    for tag in tags:
        if not isinstance(tag, str) or not tag:
            raise AltDataCatalogError(f"tag 非法: {tag!r}（须非空 str）")
    return tuple(sorted(set(tags)))


class AltDataCatalog:
    """另类数据目录（元数据登记 + 标签 + 血缘回调 + FTS5 检索 + 生命周期）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        lineage_sink: Callable[[str, str, str], None] | None = None,
        fts_connection: sqlite3.Connection | None = None,
    ) -> None:
        if clock is not None and not callable(clock):
            raise AltDataCatalogError("clock 非 callable")
        if lineage_sink is not None and not callable(lineage_sink):
            raise AltDataCatalogError("lineage_sink 非 callable")
        self._clock = clock or datetime.datetime.now
        self._lineage_sink = lineage_sink
        self._fts = fts_connection
        self._records: dict[str, CatalogRecord] = {}
        if self._fts is not None:
            self._fts.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS {_FTS_TABLE} USING fts5(source_id UNINDEXED, description, tags)"
            )
            self._fts.commit()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _record_of(self, source_id: str) -> CatalogRecord:
        record = self._records.get(source_id)
        if record is None:
            raise AltDataCatalogError(f"未知数据源: {source_id!r}（未登记）")
        return record

    def _fts_upsert(self, entry: CatalogEntry) -> None:
        if self._fts is None:
            return
        self._fts.execute(f"DELETE FROM {_FTS_TABLE} WHERE source_id = ?", (entry.source_id,))
        self._fts.execute(
            f"INSERT INTO {_FTS_TABLE}(source_id, description, tags) VALUES (?, ?, ?)",
            (entry.source_id, entry.description, " ".join(entry.tags)),
        )
        self._fts.commit()

    def _replace_entry(self, source_id: str, entry: CatalogEntry) -> None:
        record = self._records[source_id]
        self._records[source_id] = replace(record, entry=entry)
        self._fts_upsert(entry)

    # ── 元数据登记 ────────────────────────────────────────────────────────

    def register(self, entry: CatalogEntry) -> None:
        """登记数据源元数据：初始 REGISTERED；quality∈[0,1]、cost_quota≥0。"""
        if not isinstance(entry, CatalogEntry):
            raise AltDataCatalogError(f"entry 类型非法: {type(entry)!r}")
        if not isinstance(entry.source_id, str) or not entry.source_id:
            raise AltDataCatalogError("source_id 为空")
        if not isinstance(entry.source_type, CatalogSourceType):
            raise AltDataCatalogError(f"非法数据源类型: {entry.source_type!r}（词表闭合）")
        if not isinstance(entry.update_frequency, str) or not entry.update_frequency:
            raise AltDataCatalogError("update_frequency 为空")
        if isinstance(entry.quality_score, bool) or not isinstance(entry.quality_score, (int, float)):
            raise AltDataCatalogError(f"quality_score 类型非法: {entry.quality_score!r}")
        score = float(entry.quality_score)
        if not math.isfinite(score) or score < 0.0 or score > 1.0:
            raise AltDataCatalogError(f"quality_score 须 ∈ [0,1] 有限值: {entry.quality_score!r}")
        if isinstance(entry.cost_quota, bool) or not isinstance(entry.cost_quota, int) or entry.cost_quota < 0:
            raise AltDataCatalogError(f"cost_quota 须 ≥0 int: {entry.cost_quota!r}")
        if entry.source_id in self._records:
            raise AltDataCatalogError(f"source_id 重复: {entry.source_id!r}")
        normalized = replace(entry, quality_score=score, tags=_validate_tags(entry.tags))
        now = self._clock()
        self._records[entry.source_id] = CatalogRecord(
            entry=normalized,
            state=CatalogLifecycle.REGISTERED,
            registered_at=now,
            state_updated_at=now,
        )
        self._fts_upsert(normalized)
        _log.info("目录登记: %s (%s)", entry.source_id, entry.source_type.value)

    def get(self, source_id: str) -> CatalogRecord:
        """单源查询（未知 → Fail-Closed）。"""
        return self._record_of(source_id)

    # ── 标签系统 ──────────────────────────────────────────────────────────

    def add_tags(self, source_id: str, tags: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        """加标签（合并去重升序）；返回更新后标签视图。"""
        record = self._record_of(source_id)
        merged = tuple(sorted(set(record.entry.tags) | set(_validate_tags(tags))))
        self._replace_entry(source_id, replace(record.entry, tags=merged))
        return merged

    def remove_tags(self, source_id: str, tags: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        """移除标签（不存在者静默略过）；返回更新后标签视图。"""
        record = self._record_of(source_id)
        doomed = set(_validate_tags(tags))
        remaining = tuple(t for t in record.entry.tags if t not in doomed)
        self._replace_entry(source_id, replace(record.entry, tags=remaining))
        return remaining

    def tags_of(self, source_id: str) -> tuple[str, ...]:
        """标签视图（升序，确定性）。"""
        return self._record_of(source_id).entry.tags

    # ── 生命周期状态机 ────────────────────────────────────────────────────

    def approve(self, source_id: str) -> CatalogLifecycle:
        """审批上线：REGISTERED → APPROVED（其余迁移非法）。"""
        return self._transition(source_id, CatalogLifecycle.REGISTERED, CatalogLifecycle.APPROVED)

    def offline(self, source_id: str) -> CatalogLifecycle:
        """下线：APPROVED → OFFLINE（其余迁移非法）。"""
        return self._transition(source_id, CatalogLifecycle.APPROVED, CatalogLifecycle.OFFLINE)

    def _transition(
        self,
        source_id: str,
        expect: CatalogLifecycle,
        target: CatalogLifecycle,
    ) -> CatalogLifecycle:
        record = self._record_of(source_id)
        if record.state is not expect:
            raise AltDataCatalogError(
                f"非法状态迁移: {source_id!r} 当前 {record.state.value}，仅 {expect.value} → {target.value}"
            )
        self._records[source_id] = replace(record, state=target, state_updated_at=self._clock())
        _log.info("生命周期迁移: %s %s -> %s", source_id, expect.value, target.value)
        return target

    def list_by_state(self, state: CatalogLifecycle) -> tuple[CatalogRecord, ...]:
        """按生命周期过滤（source_id 升序，确定性）。"""
        if not isinstance(state, CatalogLifecycle):
            raise AltDataCatalogError(f"非法生命周期状态: {state!r}")
        out = [r for r in self._records.values() if r.state is state]
        out.sort(key=lambda r: r.entry.source_id)
        return tuple(out)

    # ── 血缘回调 ──────────────────────────────────────────────────────────

    def attach_lineage(self, source_id: str, upstream: str, transformation: str = "catalog_register") -> None:
        """挂血缘：upstream → source_id 经注入 lineage_sink 回调（未注入 Fail-Closed）。"""
        self._record_of(source_id)
        if not isinstance(upstream, str) or not upstream:
            raise AltDataCatalogError("upstream 为空")
        if self._lineage_sink is None:
            raise AltDataCatalogError("lineage_sink 未注入（血缘强制回调登记，禁止旁路）")
        try:
            self._lineage_sink(upstream, source_id, transformation)
        except Exception as exc:
            raise AltDataCatalogError(f"lineage_sink 回调失败: {upstream!r} -> {source_id!r}: {exc}") from exc

    # ── FTS5 检索 ─────────────────────────────────────────────────────────

    def search(self, query: str) -> tuple[str, ...]:
        """FTS5 检索（注入连接；source_id 升序确定性）。"""
        if self._fts is None:
            raise AltDataCatalogError("fts_connection 未注入（FTS5 检索不可用，Fail-Closed）")
        if not isinstance(query, str) or not query:
            raise AltDataCatalogError("query 为空")
        try:
            cursor = self._fts.execute(
                f"SELECT source_id FROM {_FTS_TABLE} WHERE {_FTS_TABLE} MATCH ? ORDER BY source_id",
                (query,),
            )
            return tuple(row[0] for row in cursor.fetchall())
        except sqlite3.Error as exc:
            raise AltDataCatalogError(f"FTS5 检索失败: {query!r}: {exc}") from exc
