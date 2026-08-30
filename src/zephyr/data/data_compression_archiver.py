# [BLUEPRINT] MOD-DATA-064 | docs/03_modules/_domain_data/data_compression_archiver/blueprint.md
# [MODULE] zephyr.data.data_compression_archiver
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（编排核心纯内存；archiver/clock/sqlite_conn/duckdb_conn 全注入；tiered_storage 语义参照不 import）
# [CONSUMERS] 运行时装配批（三层存储装配 / 归档计划任务 / 冷层 DuckDB 查询门面绑定）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分区须先注册方可编排; 归档方向仅 WARM→COLD(HOT 不直归); plan(cutoff) 清单=温层且 month 早于 cutoff 月,按分区名确定性排序; 执行强制注入 archiver 回调(未注入 Fail-Closed); 归档索引双写内存镜像+注入 SQLite(分区主键); 冷层查询强制注入 duckdb 连接且仅放行只读 SELECT; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data/data_compression_archiver/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DataCompressionError(占位 ZA-DATA-UNREGISTERED-COMPRESSION)——空分区名/非法月份/未知分区/非法层级迁移/archiver或连接缺失/非只读SQL时抛
# [TESTS] tests/data/test_data_compression_archiver.py
# [A_module] module_id=MOD-DATA-064 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DataCompressionArchiver — 行情数据压缩与归档编排器（MOD-DATA-064）。

B1-00106（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DAT-018，C2 D-DATA-08）：
行情热(Redis/CH) → 温(CH分区) → 冷(Parquet 按年月分区 + snappy 压缩)
三层归档编排——归档任务 plan(cutoff) → 应归档分区清单；执行经注入
archiver 回调（真 Parquet 写可选）；归档索引登记（SQLite 注入连接）；
DuckDB 直查冷层查询门面（注入 duckdb 连接）。

查重分工（蓝图 §0）：tiered_storage=三层存储读写路径治理（本件=归档编排
与索引，不实现层内读写）；data_lifecycle=保留期与删除裁定（本件只做
温→冷迁移，不做到期清理）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: data_compression_archiver.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: archiver 参数
#   fields: 参数 archiver（无注解）
#   code: data_compression_archiver.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: sqlite_conn 参数
#   fields: 参数 sqlite_conn（无注解）
#   code: data_compression_archiver.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: duckdb_conn 参数
#   fields: 参数 duckdb_conn（无注解）
#   code: data_compression_archiver.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DataCompressionArchiver
#   name_en: DataCompressionArchiver
#   intro: 行情三层归档编排器（plan → execute → index → 冷层查询门面）。
#   desc: 行情三层归档编排器（plan → execute → index → 冷层查询门面）。；公共方法（定义序）: register_partition, tier_of, partitions, plan, execute…
#   inputs: clock archiver sqlite_conn duckdb_conn compression
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: DataCompressionArchiver
#   downstream: 运行时装配批（三层存储装配 / 归档计划任务 / 冷层 DuckDB 查询门面绑定）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import re
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ArchivePlan",
    "ArchiveRecord",
    "DataCompressionArchiver",
    "DataCompressionError",
    "StorageTier",
]

#: 月份分区键格式（YYYY-MM，确定性字典序=时序）
_MONTH_RE: Final = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class DataCompressionError(Exception):
    """归档编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-COMPRESSION。
    """


class StorageTier(str, Enum):
    """存储层级（词表闭合）。"""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


@dataclass(frozen=True)
class ArchivePlan:
    """归档计划（cutoff 月之前的温层分区清单，确定性排序）。"""

    cutoff_month: str
    partitions: tuple[str, ...]


@dataclass(frozen=True)
class ArchiveRecord:
    """归档索引记录（frozen）。"""

    partition: str
    path: str
    rows: int
    archived_at: datetime.datetime


@dataclass
class _Partition:
    """分区内部状态。"""

    month: str
    tier: StorageTier
    rows: int


class DataCompressionArchiver:
    """行情三层归档编排器（plan → execute → index → 冷层查询门面）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        archiver: Callable[[str], str] | None = None,
        sqlite_conn: sqlite3.Connection | None = None,
        duckdb_conn: Any | None = None,
        compression: str = "snappy",
    ) -> None:
        if compression != "snappy":
            raise DataCompressionError(f"非法压缩编码: {compression!r}（冷层锁定 snappy）")
        self._clock = clock or datetime.datetime.now
        self._archiver = archiver
        self._sqlite = sqlite_conn
        self._duckdb = duckdb_conn
        self._compression = compression
        self._partitions: dict[str, _Partition] = {}
        self._index: dict[str, ArchiveRecord] = {}
        if self._sqlite is not None:
            self._sqlite.execute(
                "CREATE TABLE IF NOT EXISTS archive_index ("
                "partition TEXT PRIMARY KEY, path TEXT NOT NULL, "
                "rows INTEGER NOT NULL, archived_at TEXT NOT NULL)"
            )

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _partition_of(self, partition: str) -> _Partition:
        entry = self._partitions.get(partition)
        if entry is None:
            raise DataCompressionError(f"未知分区: {partition!r}（须先 register_partition）")
        return entry

    # ── 分区注册 ──────────────────────────────────────────────────────────

    def register_partition(
        self,
        partition: str,
        *,
        month: str,
        tier: StorageTier,
        rows: int = 0,
    ) -> None:
        """注册分区（重复注册拒绝；month 锁 YYYY-MM 格式）。"""
        if not partition:
            raise DataCompressionError("partition 为空")
        if not _MONTH_RE.match(month):
            raise DataCompressionError(f"month 非法: {month!r}（须 YYYY-MM）")
        if not isinstance(tier, StorageTier):
            raise DataCompressionError(f"非法存储层级: {tier!r}")
        if rows < 0:
            raise DataCompressionError(f"rows 非法: {rows!r}（须 ≥ 0）")
        if partition in self._partitions:
            raise DataCompressionError(f"分区重复注册: {partition!r}")
        self._partitions[partition] = _Partition(month=month, tier=tier, rows=rows)

    def tier_of(self, partition: str) -> StorageTier:
        """分区当前层级查询（未知分区 Fail-Closed）。"""
        return self._partition_of(partition).tier

    def partitions(self) -> tuple[str, ...]:
        """已注册分区清单（确定性排序）。"""
        return tuple(sorted(self._partitions))

    # ── 归档编排 ──────────────────────────────────────────────────────────

    def plan(self, cutoff: datetime.date) -> ArchivePlan:
        """归档计划：温层且 month 早于 cutoff 月的分区清单（字典序=时序）。"""
        if not isinstance(cutoff, datetime.date):
            raise DataCompressionError(f"cutoff 非法: {cutoff!r}（须 datetime.date）")
        cutoff_month = f"{cutoff.year:04d}-{cutoff.month:02d}"
        due = sorted(
            name
            for name, entry in self._partitions.items()
            if entry.tier is StorageTier.WARM and entry.month < cutoff_month
        )
        return ArchivePlan(cutoff_month=cutoff_month, partitions=tuple(due))

    def execute(self, plan: ArchivePlan) -> tuple[ArchiveRecord, ...]:
        """执行归档：逐分区经注入 archiver 回调写出，登记索引并置冷层。"""
        if not isinstance(plan, ArchivePlan):
            raise DataCompressionError(f"plan 非法: {plan!r}（须 ArchivePlan）")
        if self._archiver is None and plan.partitions:
            raise DataCompressionError("archiver 回调未注入（归档执行强制注入，禁止旁路）")
        records: list[ArchiveRecord] = []
        for name in plan.partitions:
            entry = self._partition_of(name)
            if entry.tier is not StorageTier.WARM:
                raise DataCompressionError(f"非法层级迁移: {name!r} 当前 {entry.tier.value}（仅 WARM→COLD）")
            path = self._archiver(name)  # type: ignore[misc]  # 上方已守卫
            if not isinstance(path, str) or not path:
                raise DataCompressionError(f"archiver 返回非法路径: {path!r}（分区 {name!r}）")
            record = ArchiveRecord(
                partition=name,
                path=path,
                rows=entry.rows,
                archived_at=self._clock(),
            )
            entry.tier = StorageTier.COLD
            self._index[name] = record
            if self._sqlite is not None:
                self._sqlite.execute(
                    "INSERT INTO archive_index (partition, path, rows, archived_at) VALUES (?, ?, ?, ?)",
                    (name, path, entry.rows, record.archived_at.isoformat()),
                )
                self._sqlite.commit()
            records.append(record)
            _log.info("分区归档: %s → %s（%d 行, %s）", name, path, entry.rows, self._compression)
        return tuple(records)

    # ── 索引与冷层查询 ────────────────────────────────────────────────────

    def index(self) -> tuple[ArchiveRecord, ...]:
        """归档索引（SQLite 注入时以库为准；按分区名确定性排序）。"""
        if self._sqlite is not None:
            rows = self._sqlite.execute(
                "SELECT partition, path, rows, archived_at FROM archive_index ORDER BY partition"
            ).fetchall()
            return tuple(
                ArchiveRecord(
                    partition=p,
                    path=path,
                    rows=r,
                    archived_at=datetime.datetime.fromisoformat(ts),
                )
                for p, path, r, ts in rows
            )
        return tuple(self._index[p] for p in sorted(self._index))

    def cold_query(self, sql: str) -> list[tuple]:
        """DuckDB 冷层查询门面（只读 SELECT；连接未注入 Fail-Closed）。"""
        if self._duckdb is None:
            raise DataCompressionError("duckdb 连接未注入（冷层查询强制注入）")
        if not isinstance(sql, str) or not sql.strip():
            raise DataCompressionError("sql 为空")
        if not sql.lstrip().upper().startswith("SELECT"):
            raise DataCompressionError("冷层门面仅放行只读 SELECT")
        return list(self._duckdb.execute(sql).fetchall())
