# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.wal_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.local_replay; zephyr.data.ch_writer; zephyr.data.provider_base; zephyr.shared.observability.metrics
# [CONSUMERS] zephyr.data.tick_subscriber
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 数据先落本地 WAL 段文件再异步排空到 CH（写入路径延迟稳定）；段落盘复用 local_replay.save_fallback（格式与回灌兼容）；drain 复用 local_replay.replay_batch；列过滤复用 ch_writer._get_table_columns_set；_segment/_cols_clause 加锁保护（add 与 stop/flush 跨线程）；WAL 容量 90% critical 背压阻断写入；P1-5 metrics 埋点覆盖 segments/wal_dir_bytes/backlog_files/drain_replayed/drain_failed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] add失败->返回False（result.error或critical背压）；段落盘失败->返回False+行保留；drain异常->log+指数退避不退出；stop->flush残留段后停止drain
# [TESTS] tests/zephyr/data/test_wal_writer.py
# [A_module] module_id=MOD-GOV-wal_writer | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



主动 WAL 写入器（P0-1 Phase A）。

数据先落本地 WAL 段文件，再由后台 drain 线程异步排空到 ClickHouse。
解决实时 tick 写入路径在 CH 慢/不可达时延迟突增的问题。

与 BufferedWriter 的区别：
    - BufferedWriter：攒批 → 直接写 CH（失败才降级到 local_fallback）
    - WalWriter：攒批 → 主动写 local_fallback 段文件 → drain 线程异步回灌 CH

优势：写入路径延迟稳定（本地落盘快），CH 慢/不可达不阻塞生产者。

复用机制：
    - local_replay.save_fallback()：段落盘（原子写 + manifest 追加）
    - local_replay.replay_batch()：drain 回灌
    - ch_writer._get_table_columns_set()：列过滤
    - ch_writer.tsv_escape()：TSV 序列化

用法：
    writer = WalWriter("c1_market.tick_data", segment_max_rows=3000)
    writer.start()
    try:
        for result in provider.fetch(payload, policy):
            if not writer.add(result):
                break  # critical 背压，生产者应减速/中断
    finally:
        writer.stop()  # flush 残留段 + 停止 drain 线程

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: table 参数
#   fields: 参数 table（无注解）
#   code: wal_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: segment_max_rows 参数
#   fields: 参数 segment_max_rows（无注解）
#   code: wal_writer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: segment_max_seconds 参数
#   fields: 参数 segment_max_seconds（无注解）
#   code: wal_writer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: wal_dir_max_bytes 参数
#   fields: 参数 wal_dir_max_bytes（无注解）
#   code: wal_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① WalWriter
#   name_en: WalWriter
#   intro: 主动 WAL 写入器——数据先落本地段文件，再异步排空到 ClickHouse。
#   desc: 主动 WAL 写入器——数据先落本地段文件，再异步排空到 ClickHouse。；公共方法（定义序）: drain_thread, add, flush, start, stop, total_segmented, t…
#   inputs: table segment_max_rows segment_max_seconds wal_dir_max_bytes
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: WalWriter
#   downstream: zephyr.data.tick_subscriber
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

import logging
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

from zephyr.shared.observability.metrics import get_registry

from . import ch_writer, local_replay

if TYPE_CHECKING:
    from .provider_base import FetchResult

log = logging.getLogger(__name__)

# 段落盘默认阈值（蓝图 P0-1：每段 ≥ 3000 行或 ≥ 5 秒触发）
_DEFAULT_SEGMENT_MAX_ROWS = 3000
_DEFAULT_SEGMENT_MAX_SECONDS = 5.0

# WAL 容量上限（2GB）：70% warning，90% critical 背压
_DEFAULT_WAL_DIR_MAX_BYTES = 2 * 1024**3
_WARNING_RATIO = 0.7
_CRITICAL_RATIO = 0.9

# drain 线程轮询参数
_DRAIN_IDLE_INTERVAL = 2.0  # 无积压轮询间隔
_DRAIN_FAST_INTERVAL = 0.5  # 有积压快速重试
_DRAIN_BACKOFF_MAX = 60.0  # 失败指数退避封顶


def _dir_size_bytes(path: Path) -> int:
    """计算目录总字节数（递归）。"""
    if not path.exists():
        return 0
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def _serialize_tsv(rows: list[tuple]) -> bytes:
    """将行列表序列化为 TSV 字节（复用 ch_writer.tsv_escape）。"""
    lines = ["\t".join(ch_writer.tsv_escape(v) for v in row) for row in rows]
    return "\n".join(lines).encode("utf-8")


def _append_rows(segment: list[tuple], result: FetchResult, keep_indices: list[int] | None) -> None:
    """按列过滤索引追加行到段缓冲。"""
    if keep_indices and len(keep_indices) < len(result.columns):
        for row in result.rows:
            segment.append(tuple(row[i] for i in keep_indices))
    else:
        segment.extend(result.rows)


class WalWriter:
    """主动 WAL 写入器——数据先落本地段文件，再异步排空到 ClickHouse。"""

    def __init__(
        self,
        table: str,
        segment_max_rows: int = _DEFAULT_SEGMENT_MAX_ROWS,
        segment_max_seconds: float = _DEFAULT_SEGMENT_MAX_SECONDS,
        wal_dir_max_bytes: int = _DEFAULT_WAL_DIR_MAX_BYTES,
    ):
        """初始化 WAL 写入器。

        Args:
            table: 目标表名（如 c1_market.tick_data）
            segment_max_rows: 段落盘行数阈值
            segment_max_seconds: 段落盘时间阈值（秒）
            wal_dir_max_bytes: WAL 目录容量上限（字节）
        """
        self._table = table
        self._segment_max_rows = max(segment_max_rows, 1)
        self._segment_max_seconds = max(segment_max_seconds, 0.1)
        self._wal_dir_max_bytes = wal_dir_max_bytes
        self._segment: list[tuple] = []
        self._cols_clause: str | None = None
        self._keep_indices: list[int] | None = None
        self._segment_first_ts: float | None = None
        self._lock = threading.Lock()
        self._drain_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._total_segmented = 0
        self._total_added = 0
        self._segment_count = 0

    @property
    def drain_thread(self) -> threading.Thread | None:
        """只读：drain_thread（Stage 4 公共化）。"""
        return self._drain_thread

    @drain_thread.setter
    def drain_thread(self, value):
        """写入：drain_thread（Stage 4 公共化）。"""
        self._drain_thread = value

    def add(self, result: FetchResult) -> bool:
        """添加 FetchResult 到当前段。达阈值时触发段落盘。

        Returns:
            True 表示成功（已入段或已落盘）；False 表示 result.error 或
            critical 背压（WAL 容量 ≥ 90%），调用方应减速/中断。
        """
        if result.error:
            log.warning("WalWriter.add(%s): result.error=%s", self._table, result.error)
            return False
        if not result.rows:
            return True
        # 容量背压检查（遍历目录，不持锁避免长阻塞）
        if not self._apply_backpressure(self._check_wal_capacity()):
            return False
        with self._lock:
            if self._cols_clause is None:
                self._init_columns(result)
            _append_rows(self._segment, result, self._keep_indices)
            self._total_added += len(result.rows)
            if self._segment_first_ts is None:
                self._segment_first_ts = time.time()
            if (
                len(self._segment) >= self._segment_max_rows
                or (time.time() - self._segment_first_ts) >= self._segment_max_seconds  # noqa: m46-time — 分段时长比较与时区无关
            ):
                return self._flush_segment_locked()
        return True

    def _init_columns(self, result: FetchResult) -> None:
        """从首个 FetchResult 确定列子句（含列过滤，参照 BufferedWriter）。"""
        # #ARCH-CH-MATERIALIZED-INSERT：用可插入列集合（排除 MATERIALIZED/ALIAS）
        table_cols = ch_writer.get_insertable_columns_set(result.table)
        if table_cols and result.columns:
            common_cols = [c for c in result.columns if c in table_cols]
            if common_cols:
                self._cols_clause = "(" + ", ".join(common_cols) + ")"
                self._keep_indices = [i for i, c in enumerate(result.columns) if c in table_cols]
                if len(common_cols) < len(result.columns):
                    log.info("WalWriter(%s): 列过滤 %d->%d", self._table, len(result.columns), len(common_cols))
                return
            log.error("WalWriter(%s): result.columns 与表列无交集", self._table)
        # CH 不可用 fallback：不固化不可信的列，落盘 None 让回灌时重新查询
        self._cols_clause = None
        self._keep_indices = list(range(len(result.columns))) if result.columns else None

    def _flush_segment_locked(self) -> bool:
        """将当前段写入本地 WAL 文件（调用方已持锁，复用 local_replay.save_fallback）。"""
        if not self._segment:
            return True
        tsv_bytes = _serialize_tsv(self._segment)
        ok = local_replay.save_fallback(self._table, self._cols_clause, tsv_bytes)
        if ok:
            self._total_segmented += len(self._segment)
            self._segment_count += 1
            get_registry().inc("zephyr_wal_segments_total")
            log.info("WalWriter(%s): 第%d段落盘 %d 行", self._table, self._segment_count, len(self._segment))
            self._segment.clear()
            self._segment_first_ts = None
        else:
            log.error("WalWriter(%s): 段落盘失败，%d 行保留待重试", self._table, len(self._segment))
        return ok

    def flush(self) -> bool:
        """强制当前段落盘。"""
        with self._lock:
            return self._flush_segment_locked()

    def _check_wal_capacity(self) -> str:
        """检查 WAL 目录容量，返回 'ok'/'warning'/'critical'。"""
        # 复用 local_replay 的存储目录（WAL 段与 fallback 文件共用同一目录与 manifest）
        used = _dir_size_bytes(local_replay._FALLBACK_DIR)
        get_registry().set_gauge("zephyr_wal_dir_bytes", used)
        ratio = used / self._wal_dir_max_bytes if self._wal_dir_max_bytes > 0 else 0
        if ratio >= _CRITICAL_RATIO:
            return "critical"
        if ratio >= _WARNING_RATIO:
            return "warning"
        return "ok"

    def _apply_backpressure(self, level: str) -> bool:
        """根据容量级别施加背压。critical 返回 False 阻断写入。"""
        if level == "critical":
            log.error(
                "WalWriter(%s): WAL 容量 critical(≥%d%%)，阻断写入触发背压", self._table, int(_CRITICAL_RATIO * 100)
            )
            return False
        if level == "warning":
            log.warning(
                "WalWriter(%s): WAL 容量 warning(≥%d%%)，建议检查 drain 线程", self._table, int(_WARNING_RATIO * 100)
            )
        return True

    def _drain_loop(self) -> None:
        """drain 线程主循环：轮询积压，回灌 CH（复用 local_replay.replay_batch）。

        P2-5 Stage 5：replay_batch 回灌 CH 耗时度量（zephyr_tick_stage_wal_flush_seconds）。
        """
        fail_backoff = _DRAIN_IDLE_INTERVAL
        reg = get_registry()
        while not self._stop_event.is_set():
            wait_sec = _DRAIN_IDLE_INTERVAL
            try:
                if local_replay.has_backlog():
                    # P2-5: Stage 5——replay_batch 回灌 ClickHouse 耗时
                    t_flush = time.perf_counter()
                    result = local_replay.replay_batch()
                    reg.observe(
                        "zephyr_tick_stage_wal_flush_seconds",
                        time.perf_counter() - t_flush,
                    )
                    remaining = result.get("remaining", 0)
                    replayed = result.get("replayed", 0)
                    fail_backoff = _DRAIN_IDLE_INTERVAL  # 成功，重置退避
                    reg.set_gauge("zephyr_wal_backlog_files", remaining)
                    if replayed > 0:
                        reg.inc("zephyr_drain_replayed_total", n=replayed)
                        log.info("WalWriter(%s) drain: 回灌 %d 段，剩余 %d", self._table, replayed, remaining)
                    if remaining > 0:
                        wait_sec = _DRAIN_FAST_INTERVAL
                else:
                    reg.set_gauge("zephyr_wal_backlog_files", 0)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                reg.inc("zephyr_drain_failed_total")
                log.error("WalWriter(%s) drain 异常: %s，退避 %.1fs", self._table, e, fail_backoff)
                wait_sec = fail_backoff
                fail_backoff = min(fail_backoff * 2, _DRAIN_BACKOFF_MAX)
            self._stop_event.wait(wait_sec)

    def start(self) -> None:
        """启动 drain 线程。"""
        if self._drain_thread is not None:
            return
        self._stop_event.clear()
        self._drain_thread = threading.Thread(
            target=self._drain_loop,
            name=f"WalWriter-drain-{self._table}",
            daemon=True,
        )
        self._drain_thread.start()
        log.info("WalWriter(%s): drain 线程已启动", self._table)

    def stop(self) -> None:
        """停止 drain 线程 + flush 残留段。"""
        self.flush()
        self._stop_event.set()
        if self._drain_thread is not None:
            self._drain_thread.join(timeout=10)
            self._drain_thread = None
        log.info(
            "WalWriter(%s): 已停止（累计落盘 %d 行 / %d 段）", self._table, self._total_segmented, self._segment_count
        )

    @property
    def total_segmented(self) -> int:
        """已成功落盘的总行数。"""
        return self._total_segmented

    @property
    def total_added(self) -> int:
        """已添加到段的总行数（含未落盘的）。"""
        return self._total_added

    @property
    def segment_count(self) -> int:
        """已落盘的段数。"""
        return self._segment_count

    @property
    def pending_rows(self) -> int:
        """当前段中待落盘的行数。"""
        with self._lock:
            return len(self._segment)
