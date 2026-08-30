# [BLUEPRINT] MOD-DATENG-002 | docs/03_modules/_domain_data_eng/cold_data_archive_manager/blueprint.md
# [MODULE] zephyr.data_eng.cold_data_archive_manager
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] 无（编排核心纯内存；archiver/index_conn/purge_executor/clock/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（归档调度挂 auto_archive 周期计划 / 归档索引接 SQLite / 清理接存储执行器）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 归档索引唯一键(table,partition)幂等防重; 计划按(table,partition)确定性排序; 保留期注册表闭合(未注册表禁止清理裁决); 检索只读(不写索引); 归档/清理执行全经注入回调(不直连CH/Parquet); occurred时间全走注入时钟(不读墙钟); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_eng/cold_data_archive_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ColdArchiveError(占位 ZA-DE-UNREGISTERED-COLD-ARCHIVE)——空表名/空分区/非法cutoff/索引连接缺失/重复归档/执行回调缺失/未注册保留策略时抛
# [TESTS] tests/data_eng/test_cold_data_archive_manager.py
# [A_module] module_id=MOD-DATENG-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



ColdDataArchiveManager — 冷数据归档管理器（MOD-DATENG-002）。

B13-04331（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-005，A3数据架构）：
ClickHouse 老分区 → Parquet(zstd) 归档目录**编排层**——归档计划生成
（cutoff 裁老分区）、归档索引登记（SQLite 注入连接：partition/path/
hash/archived_at）、保留期清理裁决（保留期注册表 + 清理执行回调注入）、
归档只读检索、auto_archive_scheduler 周期计划生成。

边界声明（蓝图 §0）：本件不写 Parquet、不直连 ClickHouse（归档执行经注
入 archiver 回调，返回 (path, hash)）；索引表 archive_index 由本件在注
入连接上自建自维护；物理清理由注入 purge_executor 执行，本件只做裁决
与索引维护；tiered_storage（D_GOV_AUDIT）为分层存储语义件，零交集。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: index_conn 参数
#   fields: 参数 index_conn（无注解）
#   code: cold_data_archive_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: cold_data_archive_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: archiver 参数
#   fields: 参数 archiver（无注解）
#   code: cold_data_archive_manager.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: purge_executor 参数
#   fields: 参数 purge_executor（无注解）
#   code: cold_data_archive_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ColdDataArchiveManager
#   name_en: ColdDataArchiveManager
#   intro: 冷数据归档编排件（计划 + 索引 + 清理裁决 + 只读检索 + 周期计划）。
#   desc: 冷数据归档编排件（计划 + 索引 + 清理裁决 + 只读检索 + 周期计划）。；公共方法（定义序）: plan_archive, run_archive, register_retention, plan_purge,…
#   inputs: index_conn clock archiver purge_executor alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: ColdDataArchiveManager
#   downstream: 运行时装配批（归档调度挂 auto_archive 周期计划 / 归档索引接 SQLite / 清理接存储执行器）
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
import sqlite3
from dataclasses import dataclass
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "ArchivePlan",
    "ArchiveRecord",
    "ColdArchiveError",
    "ColdDataArchiveManager",
    "PartitionInfo",
    "PurgeVerdict",
    "ScheduledRun",
]

_INDEX_DDL: Final = (
    "CREATE TABLE IF NOT EXISTS archive_index ("
    "table_name TEXT NOT NULL, "
    "partition TEXT NOT NULL, "
    "path TEXT NOT NULL, "
    "content_hash TEXT NOT NULL, "
    "archived_at TEXT NOT NULL, "
    "PRIMARY KEY (table_name, partition))"
)


class ColdArchiveError(Exception):
    """冷数据归档编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DE-UNREGISTERED-COLD-ARCHIVE。
    """


@dataclass(frozen=True)
class PartitionInfo:
    """CH 分区观测（归档候选输入，frozen）。"""

    table: str
    partition: str
    max_ts: datetime.datetime
    row_count: int = 0


@dataclass(frozen=True)
class ArchivePlan:
    """归档计划（cutoff 裁出的应归档分区清单，确定性排序）。"""

    cutoff: datetime.datetime
    partitions: tuple[PartitionInfo, ...]


@dataclass(frozen=True)
class ArchiveRecord:
    """归档索引记录（partition/path/hash/archived_at）。"""

    table: str
    partition: str
    path: str
    content_hash: str
    archived_at: datetime.datetime


@dataclass(frozen=True)
class PurgeVerdict:
    """保留期清理裁决（索引记录超保留期 → 应清理）。"""

    table: str
    partition: str
    reason: str
    decided_at: datetime.datetime


@dataclass(frozen=True)
class ScheduledRun:
    """auto_archive 周期计划单次运行（run_at + 该次归档计划）。"""

    run_at: datetime.datetime
    plan: ArchivePlan


class ColdDataArchiveManager:
    """冷数据归档编排件（计划 + 索引 + 清理裁决 + 只读检索 + 周期计划）。"""

    def __init__(
        self,
        *,
        index_conn: sqlite3.Connection | None,
        clock: Callable[[], datetime.datetime] | None = None,
        archiver: Callable[[PartitionInfo], tuple[str, str]] | None = None,
        purge_executor: Callable[[ArchiveRecord], None] | None = None,
        alert_sink: Callable[[str], None] | None = None,
    ) -> None:
        if index_conn is None:
            raise ColdArchiveError("index_conn 未注入（归档索引强制 SQLite 注入连接）")
        self._conn = index_conn
        self._clock = clock or datetime.datetime.now
        self._archiver = archiver
        self._purge_executor = purge_executor
        self._alert_sink = alert_sink
        self._retention_days: dict[str, int] = {}
        self._conn.execute(_INDEX_DDL)

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_partition(info: PartitionInfo) -> None:
        if not info.table:
            raise ColdArchiveError("table 为空")
        if not info.partition:
            raise ColdArchiveError(f"partition 为空: table={info.table!r}")
        if info.row_count < 0:
            raise ColdArchiveError(f"row_count 非法: {info.row_count}")

    def _alert(self, message: str) -> None:
        _log.warning("冷归档告警: %s", message)
        if self._alert_sink is not None:
            try:
                self._alert_sink(message)
            except Exception:  # noqa: BLE001 — 告警不阻断
                _log.exception("alert_sink 告警失败")

    def _indexed(self, table: str, partition: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM archive_index WHERE table_name = ? AND partition = ?",
            (table, partition),
        ).fetchone()
        return row is not None

    # ── 归档计划与执行 ────────────────────────────────────────────────────

    def plan_archive(self, partitions: Iterable[PartitionInfo], cutoff: datetime.datetime) -> ArchivePlan:
        """归档计划：max_ts < cutoff 的老分区，按 (table, partition) 排序。"""
        if cutoff is None:
            raise ColdArchiveError("cutoff 为空")
        candidates = list(partitions)
        for info in candidates:
            self._validate_partition(info)
        selected = [p for p in candidates if p.max_ts < cutoff]
        selected.sort(key=lambda p: (p.table, p.partition))
        return ArchivePlan(cutoff=cutoff, partitions=tuple(selected))

    def run_archive(self, partitions: Iterable[PartitionInfo], cutoff: datetime.datetime) -> tuple[ArchiveRecord, ...]:
        """归档执行：plan → 注入 archiver 逐分区归档 → 索引登记（防重 Fail-Closed）。"""
        if self._archiver is None:
            raise ColdArchiveError("archiver 未注入（归档执行强制注入回调，禁止旁路）")
        plan = self.plan_archive(partitions, cutoff)
        records: list[ArchiveRecord] = []
        for info in plan.partitions:
            if self._indexed(info.table, info.partition):
                raise ColdArchiveError(f"重复归档拒绝: {info.table}/{info.partition} 已在归档索引")
            path, content_hash = self._archiver(info)
            if not path or not content_hash:
                raise ColdArchiveError(f"archiver 返回非法: {info.table}/{info.partition} path/hash 为空")
            archived_at = self._clock()
            self._conn.execute(
                "INSERT INTO archive_index (table_name, partition, path, content_hash, archived_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (info.table, info.partition, path, content_hash, archived_at.isoformat()),
            )
            records.append(
                ArchiveRecord(
                    table=info.table,
                    partition=info.partition,
                    path=path,
                    content_hash=content_hash,
                    archived_at=archived_at,
                )
            )
        self._conn.commit()
        _log.info("归档完成: %d 分区（cutoff=%s）", len(records), cutoff.isoformat())
        return tuple(records)

    # ── 保留策略与清理裁决 ────────────────────────────────────────────────

    def register_retention(self, table: str, retention_days: int) -> None:
        """保留期注册：归档超过 retention_days 的记录判定可清理。"""
        if not table:
            raise ColdArchiveError("table 为空")
        if retention_days <= 0:
            raise ColdArchiveError(f"retention_days 非法: {retention_days}")
        self._retention_days[table] = retention_days

    def plan_purge(self) -> tuple[PurgeVerdict, ...]:
        """清理裁决：索引记录 archived_at + 保留期 <= now → 应清理（确定性排序）。"""
        now = self._clock()
        verdicts: list[PurgeVerdict] = []
        for record in self.list_archived():
            retention = self._retention_days.get(record.table)
            if retention is None:
                continue  # 未注册保留策略的表不参与清理裁决（注册表闭合）
            deadline = record.archived_at + datetime.timedelta(days=retention)
            if deadline <= now:
                verdicts.append(
                    PurgeVerdict(
                        table=record.table,
                        partition=record.partition,
                        reason=(f"归档超保留期: archived_at={record.archived_at.isoformat()} + {retention}d <= now"),
                        decided_at=now,
                    )
                )
        verdicts.sort(key=lambda v: (v.table, v.partition))
        return tuple(verdicts)

    def run_purge(self) -> tuple[PurgeVerdict, ...]:
        """清理执行：裁决 → 注入 purge_executor 物理清理 → 索引除名。"""
        if self._purge_executor is None:
            raise ColdArchiveError("purge_executor 未注入（清理执行强制注入回调）")
        verdicts = self.plan_purge()
        for verdict in verdicts:
            record = self.lookup(verdict.table, verdict.partition)
            if record is None:  # pragma: no cover — 裁决与检索同源，防御性兜底
                raise ColdArchiveError(f"索引不一致: {verdict.table}/{verdict.partition} 裁决后检索缺失")
            self._purge_executor(record)
            self._conn.execute(
                "DELETE FROM archive_index WHERE table_name = ? AND partition = ?",
                (verdict.table, verdict.partition),
            )
            self._alert(f"冷归档已清理: {verdict.table}/{verdict.partition}")
        self._conn.commit()
        return verdicts

    # ── 只读检索 ──────────────────────────────────────────────────────────

    def lookup(self, table: str, partition: str) -> ArchiveRecord | None:
        """单分区归档检索（只读；未命中返回 None）。"""
        if not table or not partition:
            raise ColdArchiveError("table/partition 为空")
        row = self._conn.execute(
            "SELECT path, content_hash, archived_at FROM archive_index WHERE table_name = ? AND partition = ?",
            (table, partition),
        ).fetchone()
        if row is None:
            return None
        return ArchiveRecord(
            table=table,
            partition=partition,
            path=row[0],
            content_hash=row[1],
            archived_at=datetime.datetime.fromisoformat(row[2]),
        )

    def list_archived(self, table: str | None = None) -> tuple[ArchiveRecord, ...]:
        """归档清单检索（只读；按 (table, partition) 确定性排序）。"""
        if table is None:
            rows = self._conn.execute(
                "SELECT table_name, partition, path, content_hash, archived_at"
                " FROM archive_index ORDER BY table_name, partition"
            ).fetchall()
        else:
            if not table:
                raise ColdArchiveError("table 为空")
            rows = self._conn.execute(
                "SELECT table_name, partition, path, content_hash, archived_at"
                " FROM archive_index WHERE table_name = ? ORDER BY table_name, partition",
                (table,),
            ).fetchall()
        return tuple(
            ArchiveRecord(
                table=r[0],
                partition=r[1],
                path=r[2],
                content_hash=r[3],
                archived_at=datetime.datetime.fromisoformat(r[4]),
            )
            for r in rows
        )

    # ── auto_archive 周期计划 ─────────────────────────────────────────────

    def auto_archive_schedule(
        self,
        partitions: Iterable[PartitionInfo],
        *,
        cutoff: datetime.datetime,
        period: datetime.timedelta,
        horizon: datetime.timedelta,
    ) -> tuple[ScheduledRun, ...]:
        """auto_archive_scheduler 周期计划：now 起每 period 一次，截止 now+horizon。

        第 k 次运行的 cutoff 按 k*period 同步前移（数据随时间变老，计划确定
        性可预演）；每次运行复用 plan_archive 语义。
        """
        if period <= datetime.timedelta(0):
            raise ColdArchiveError("period 非正")
        if horizon < datetime.timedelta(0):
            raise ColdArchiveError("horizon 非法")
        candidates = list(partitions)
        for info in candidates:
            self._validate_partition(info)
        base = self._clock()
        runs: list[ScheduledRun] = []
        step = 1
        while period * step <= horizon:
            run_at = base + period * step
            run_cutoff = cutoff + period * step
            runs.append(ScheduledRun(run_at=run_at, plan=self.plan_archive(candidates, run_cutoff)))
            step += 1
        return tuple(runs)
