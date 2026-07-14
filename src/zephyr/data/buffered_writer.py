# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.buffered_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer
# [CONSUMERS] zephyr.data.scheduler; tmp._backfill
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 攒批写入（每批 ≥ max_rows 或 ≥ max_seconds 触发 flush）；per-task 实例（无需线程安全）；列过滤复用 ch_writer._get_table_columns_set；禁止绕过 BufferedWriter 在 for 循环内直接调用 ch_writer.write_result（裁定 #ARCH-CH-003）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] add失败->返回False; flush失败->返回False+log(ch_writer.write_tsv内部处理); 空缓冲区flush->返回True
# [TESTS] tests/zephyr/data/test_buffered_writer.py
# [A_module] module_id=MOD-L00-004-buffered_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""批量聚合写入器（MOD-L00-004 §18.3 裁定 #ARCH-CH-003）。

在 Provider 和 ch_writer 之间插入缓冲层，攒批后一次性写入 ClickHouse。

背景（裁定 #ARCH-CH-001）：
    ch_writer.write_result 每个 FetchResult（1 只股票 ~3 行）= 1 次 WSL 进程启动
    + 1 次 INSERT + 1 个 data part。5204 只股票 = 5204 个 data parts，
    CH 后台 merge 跟不上 → CPU 饱和 → 写入失败。

解决方案（裁定 #ARCH-CH-003）：
    BufferedWriter 聚合多个 FetchResult 的 rows，达到阈值后一次性 write_tsv。
    预期效果：5204 次 INSERT → 1-3 次 INSERT，data parts 从 5204 → 1-3。

用法：
    writer = BufferedWriter("c1_market.kline_daily")
    for result in provider.fetch(payload, policy):
        if not writer.add(result):
            break  # 写入失败
    writer.flush()  # 最后 flush 残留

    # 搭配 ReplacingMergeTree（裁定 #ARCH-CH-002）：
    # 直接 INSERT，CH 后台去重，无需先删后插。
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from . import ch_writer

if TYPE_CHECKING:
    from .provider_base import FetchResult

log = logging.getLogger(__name__)

# 默认阈值（蓝图 §18.3：每批 ≥ 50000 行或 ≥ 30 秒触发）
_DEFAULT_MAX_ROWS = 50000
_DEFAULT_MAX_SECONDS = 30


class BufferedWriter:
    """批量聚合写入器——攒批后一次性写入 ClickHouse。

    per-task 实例（每个下载任务一个 BufferedWriter），无需线程安全。
    scheduler 的 max_instances=1 保证同任务不并发。
    """

    def __init__(
        self,
        table: str,
        max_rows: int = _DEFAULT_MAX_ROWS,
        max_seconds: float = _DEFAULT_MAX_SECONDS,
    ):
        """初始化缓冲区。

        Args:
            table: 目标表名（如 c1_market.kline_daily）
            max_rows: 最大缓冲行数，达到后触发 flush
            max_seconds: 最大缓冲时间（秒），达到后触发 flush
        """
        self._table = table
        self._max_rows = max_rows
        self._max_seconds = max_seconds
        self._buffer: list[tuple] = []
        self._cols_clause: str | None = None
        self._keep_indices: list[int] | None = None
        self._first_buffer_ts: float | None = None
        self._total_flushed: int = 0
        self._total_added: int = 0
        self._flush_count: int = 0

    def add(self, result: "FetchResult") -> bool:
        """添加 FetchResult 到缓冲区。达阈值时自动 flush。

        Args:
            result: Provider 返回的 FetchResult

        Returns:
            True 表示成功（已入缓冲区或已 flush 成功）；
            False 表示写入失败（result.error 或 flush 失败），调用方应中断。
        """
        if result.error:
            log.warning("BufferedWriter.add(%s): result.error=%s", self._table, result.error)
            return False
        if not result.rows:
            return True

        # 首次 add：确定列子句和列过滤索引
        if self._cols_clause is None:
            self._init_columns(result)

        # 按列过滤索引添加行
        if self._keep_indices and len(self._keep_indices) < len(result.columns):
            for row in result.rows:
                self._buffer.append(tuple(row[i] for i in self._keep_indices))
        else:
            self._buffer.extend(result.rows)

        self._total_added += len(result.rows)
        if self._first_buffer_ts is None:
            self._first_buffer_ts = time.time()

        # 达阈值触发 flush
        if len(self._buffer) >= self._max_rows or \
           (time.time() - self._first_buffer_ts) >= self._max_seconds:
            return self.flush()
        return True

    def _init_columns(self, result: "FetchResult") -> None:
        """从首个 FetchResult 确定列子句（含列过滤）。

        复用 ch_writer._get_table_columns_set 做列过滤：
        只插入表中存在的列，忽略多余列。
        """
        table_cols = ch_writer._get_table_columns_set(result.table)
        if table_cols and result.columns:
            common_cols = [c for c in result.columns if c in table_cols]
            if common_cols:
                self._cols_clause = "(" + ", ".join(common_cols) + ")"
                self._keep_indices = [i for i, c in enumerate(result.columns) if c in table_cols]
                if len(common_cols) < len(result.columns):
                    log.info(
                        "BufferedWriter(%s): 列过滤 %d->%d",
                        self._table, len(result.columns), len(common_cols),
                    )
                return
            log.error("BufferedWriter(%s): result.columns 与表列无交集", self._table)
        # fallback：用 result.columns 原样
        if result.columns:
            self._cols_clause = "(" + ", ".join(result.columns) + ")"
            self._keep_indices = list(range(len(result.columns)))
        else:
            self._cols_clause = None  # write_tsv 内部自动查询
            self._keep_indices = None

    def flush(self) -> bool:
        """强制写入缓冲区全部数据。

        Returns:
            True 表示成功（含空缓冲区）；False 表示写入失败。
        """
        if not self._buffer:
            return True

        tsv_lines = []
        for row in self._buffer:
            tsv_lines.append("\t".join(ch_writer.tsv_escape(v) for v in row))
        tsv_bytes = "\n".join(tsv_lines).encode("utf-8")

        ok = ch_writer.write_tsv(self._table, self._cols_clause, tsv_bytes)
        if ok:
            self._total_flushed += len(self._buffer)
            self._flush_count += 1
            log.info(
                "BufferedWriter.flush(%s): 第%d次 flush，%d 行（累计 flush %d/%d 行）",
                self._table, self._flush_count, len(self._buffer),
                self._total_flushed, self._total_added,
            )
            self._buffer.clear()
            self._first_buffer_ts = None
        else:
            log.error(
                "BufferedWriter.flush(%s): 写入失败，%d 行保留在缓冲区待重试",
                self._table, len(self._buffer),
            )
        return ok

    @property
    def total_flushed(self) -> int:
        """已成功 flush 的总行数。"""
        return self._total_flushed

    @property
    def total_added(self) -> int:
        """已添加到缓冲区的总行数（含未 flush 的）。"""
        return self._total_added

    @property
    def flush_count(self) -> int:
        """已执行 flush 的次数。"""
        return self._flush_count

    @property
    def pending_rows(self) -> int:
        """当前缓冲区中待 flush 的行数。"""
        return len(self._buffer)
