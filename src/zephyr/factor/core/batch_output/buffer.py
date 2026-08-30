# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-BO
# [MODULE] zephyr.factor.core.batch_output.buffer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.contracts.factor_signal
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 缓冲达 batch_size 或距上次 flush 超 flush_interval_s 触发刷新；空缓冲 flush 返回 None；TSV 列顺序与 _SIGNAL_COLUMNS 一致
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] writer 失败由调用方处理（FlushOutcome.outcome 携带 WriteOutcome）；空 payload 跳过写入
# [TESTS] tests/factor/test_batch_output.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""
D_FACTOR core batch_output.buffer——FactorSignal 批量缓冲写入器。

将 FactorSignal 列表缓冲，按定量（batch_size）或定时（flush_interval_s）触发刷新，
转换为 TSV 字节流后调用 ch_writer.write_tsv_outcome 写入 ClickHouse。

设计要点：
- 不重造 TSV 写入——复用 ch_writer.write_tsv_outcome / tsv_escape
- target_table 参数化（默认 c1_market.factor_signal，调用方可覆盖）
- writer 参数可注入（测试用，生产用默认 ch_writer.write_tsv_outcome）
- 线程安全：threading.Lock 保护内部 list 和 _last_flush_ts

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: s 参数
#   fields: 参数 s，类型注解 FactorSignal
#   code: buffer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: signals 参数
#   fields: 参数 signals，类型注解 list[FactorSignal]
#   code: buffer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① signal_to_tsv_row
#   name_en: signal_to_tsv_row
#   intro: 单条 FactorSignal → TSV 行。
#   desc: 单条 FactorSignal → TSV 行。 字段顺序与 _SIGNAL_COLUMNS 一致。NULL 值（None/NaN）由 ch_writer.tsv_escape…；源码 L163-L189
#   inputs: s
#   outputs: str
# - id: A2
#   name_zh: ② signals_to_tsv
#   name_en: signals_to_tsv
#   intro: 批量转 TSV 字节流。
#   desc: 批量转 TSV 字节流。 Args: signals: FactorSignal 列表 Returns: UTF-8 编码的 TSV 字节流（每行一个信号，以 \n 分隔，末尾含…；源码 L192-L204
#   inputs: signals
#   outputs: bytes
# - id: A3
#   name_zh: ③ FactorSignalBuffer
#   name_en: FactorSignalBuffer
#   intro: FactorSignal 批量缓冲写入器。
#   desc: FactorSignal 批量缓冲写入器。 Usage:: buf = FactorSignalBuffer(BatchOutputConfig(batch_size=100))…；公共方法（定义序）: add, ad…
#   inputs: config table writer
#   outputs: 返回值
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: bytes
#   name_en: bytes
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from zephyr.data import ch_writer
from zephyr.factor.core.config_manager.loader import get_section
from zephyr.shared.contracts.factor_signal import FactorSignal

log = logging.getLogger(__name__)

# TSV 列顺序（与 FactorSignal 标量字段对齐，排除 trace_context/extra 等非标量）
# 写入时显式指定列子句，避免 ch_writer._get_insert_columns 查询 DESCRIBE TABLE 开销
_SIGNAL_COLUMNS: list[str] = [
    "as_of_date",
    "factor_id",
    "idempotency_key",
    "raw_value",
    "symbol",
    "confidence",
    "normalized_value",
    "rank_pct",
    "is_valid",
    "factor_version",
    "schema_version",
]

# 列子句："(col1, col2, ...)" 字符串，传给 ch_writer.write_tsv_outcome 的 columns 参数
_COLUMNS_CLAUSE: str = "(" + ", ".join(_SIGNAL_COLUMNS) + ")"


@dataclass(frozen=True)
class BatchOutputConfig:
    """批量输出配置。

    Attributes:
        batch_size: 定量刷新阈值（条）。缓冲达此数自动 flush。
        flush_interval_s: 定时刷新间隔（秒）。距上次 flush 超过此值时 maybe_flush_by_time 触发。
        target_table: 默认写入表（调用方可通过 FactorSignalBuffer(table=...) 覆盖）。
    """

    batch_size: int = 500
    flush_interval_s: float = 5.0
    target_table: str = "c1_market.factor_signal"


def _default_config() -> BatchOutputConfig:
    """从 core/_config.yaml 的 batch_output 节构建默认配置（真源=YAML，缺省回退常量）。"""
    s = get_section("batch_output")
    return BatchOutputConfig(
        batch_size=int(s.get("batch_size", 500)),
        flush_interval_s=float(s.get("flush_interval_s", 5.0)),
        target_table=str(s.get("target_table", "c1_market.factor_signal")),
    )


@dataclass
class FlushOutcome:
    """单次 flush 的结果。

    Attributes:
        flushed: 实际刷新的信号条数
        outcome: ch_writer.WriteOutcome（含 disposition 和 detail）
        table: 写入的目标表名
    """

    flushed: int
    outcome: object  # ch_writer.WriteOutcome，用 object 避免循环 import
    table: str


# 默认 writer：调用 ch_writer.write_tsv_outcome
def _default_writer(table: str, columns: str, tsv_bytes: bytes) -> object:
    """默认 writer——调用 ch_writer.write_tsv_outcome。"""
    return ch_writer.write_tsv_outcome(table, columns, tsv_bytes)


def signal_to_tsv_row(s: FactorSignal) -> str:
    """单条 FactorSignal → TSV 行。

    字段顺序与 _SIGNAL_COLUMNS 一致。NULL 值（None/NaN）由 ch_writer.tsv_escape 转 \\N。

    Args:
        s: FactorSignal 实例

    Returns:
        TSV 行字符串（不含末尾换行）
    """
    # 直接传原始值给 tsv_escape：None/NaN → \\N，float → str(float)，str → 转义后字符串
    # as_of_date 传 datetime 对象，tsv_escape 内 str(datetime) 得 "2026-07-27 15:00:00"
    fields: list[object] = [
        s.as_of_date,
        s.factor_id,
        s.idempotency_key,
        s.raw_value,
        s.symbol,
        s.confidence,
        s.normalized_value,
        s.rank_pct,
        1 if s.is_valid else 0,
        s.factor_version,
        s.schema_version,
    ]
    return "\t".join(ch_writer.tsv_escape(f) for f in fields)


def signals_to_tsv(signals: list[FactorSignal]) -> bytes:
    """批量转 TSV 字节流。

    Args:
        signals: FactorSignal 列表

    Returns:
        UTF-8 编码的 TSV 字节流（每行一个信号，以 \\n 分隔，末尾含 \\n）
    """
    if not signals:
        return b""
    lines = [signal_to_tsv_row(s) for s in signals]
    return ("\n".join(lines) + "\n").encode("utf-8")


class FactorSignalBuffer:
    """FactorSignal 批量缓冲写入器。

    Usage::

        buf = FactorSignalBuffer(BatchOutputConfig(batch_size=100))
        for signal in signals:
            buf.add(signal)  # 达 100 条自动 flush
        buf.flush()  # 收尾强制刷新

    线程安全：所有公共方法持 self._lock。
    """

    def __init__(
        self,
        config: BatchOutputConfig | None = None,
        table: str | None = None,
        writer: Callable[[str, str, bytes], object] | None = None,
    ) -> None:
        self._config = config or _default_config()
        self._table = table or self._config.target_table
        self._writer: Callable[[str, str, bytes], object] = writer or _default_writer
        self._buffer: list[FactorSignal] = []
        self._lock = threading.Lock()
        self._last_flush_ts: float = time.monotonic()

    def add(self, signal: FactorSignal) -> FlushOutcome | None:
        """追加 1 条信号。

        达 batch_size 自动触发 flush，返回 FlushOutcome；否则返回 None。
        """
        with self._lock:
            self._buffer.append(signal)
            if len(self._buffer) < self._config.batch_size:
                return None
            return self._flush_locked()

    def add_many(self, signals: list[FactorSignal]) -> FlushOutcome | None:
        """批量追加信号。

        达 batch_size 自动触发 flush（仅触发一次，超量部分留在缓冲区）。
        """
        if not signals:
            return None
        with self._lock:
            self._buffer.extend(signals)
            if len(self._buffer) < self._config.batch_size:
                return None
            return self._flush_locked()

    def flush(self) -> FlushOutcome | None:
        """强制刷新缓冲区。空缓冲返回 None。"""
        with self._lock:
            return self._flush_locked()

    def maybe_flush_by_time(self) -> FlushOutcome | None:
        """距上次 flush 超过 flush_interval_s 则刷新；否则返回 None。"""
        with self._lock:
            if not self._buffer:
                return None
            elapsed = time.monotonic() - self._last_flush_ts
            if elapsed < self._config.flush_interval_s:
                return None
            return self._flush_locked()

    def __len__(self) -> int:
        """返回当前缓冲区长度（线程安全）。"""
        with self._lock:
            return len(self._buffer)

    def _flush_locked(self) -> FlushOutcome | None:
        """实际刷新逻辑（调用方持 self._lock）。

        - 空缓冲返回 None
        - 转换为 TSV 字节流
        - 调用 writer 写入
        - 重置缓冲区和 _last_flush_ts
        - 返回 FlushOutcome（含 writer 的 WriteOutcome）
        """
        if not self._buffer:
            return None
        to_flush = list(self._buffer)
        self._buffer.clear()
        self._last_flush_ts = time.monotonic()

        tsv_bytes = signals_to_tsv(to_flush)
        if not tsv_bytes:
            return None

        try:
            outcome = self._writer(self._table, _COLUMNS_CLAUSE, tsv_bytes)
        except Exception as e:  # noqa: BLE001 — writer 失败由调用方经 FlushOutcome.outcome 处理（错误契约：不抛出）
            log.error("batch_output flush 失败 (table=%s): %s", self._table, e)
            outcome = None

        return FlushOutcome(
            flushed=len(to_flush),
            outcome=outcome,
            table=self._table,
        )
