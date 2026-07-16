# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] http.client(标准库); clickhouse-driver(pip); zephyr.data.local_replay
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 二级降级：query/delete_where 走 clickhouse-driver TCP(9000)，write_tsv 走 HTTP API(8123)→本地落盘兜底(local_replay); 幂等性由调用方决定(ReplacingMergeTree直接INSERT/MergeTree写前DELETE); HTTP 传输用 http.client; ClickHouse 不可达时数据写入本地 TSV 文件待回灌（裁定 #ARCH-CH-013）; health_check() 提供传输路径健康诊断
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] write_result失败->返回False+log; query失败->返回空字符串; delete_where失败->返回False
# [TESTS] tests/zephyr/data/test_ch_writer.py
# [A_module] module_id=MOD-L00-004-ch_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步 + §7.3 幂等性）。

二级传输架构（Hyper-V 迁移，2026-07-16 修订）：
- query/delete_where → clickhouse-driver TCP（9000端口）
- write_tsv → HTTP API（8123端口，POST TSV body）→ 本地落盘兜底
- 端点从 config/.env.clickhouse 读取（CLICKHOUSE_HOST / CLICKHOUSE_HTTP_PORT）
- 移除 WSL subprocess fallback（裁定 #ARCH-CH-010 Phase 3 迁移至 Hyper-V VM）

提供：
- write_result(result): 把 FetchResult.rows 转 TSV 写入 CH
- tsv_escape(v): 转义字段值（None/NaN -> \\N，字符串去换行制表符）
- delete_where(table, condition): 写前删除（MergeTree 幂等性）
- query(sql): 查询 CH（用于 DESCRIBE TABLE 获取列清单）
- get_table_engine(table) / is_replacing_engine(table): 查询表引擎，辅助幂等性决策（裁定 #ARCH-CH-002）

幂等性策略（§7.3）：
- ReplacingMergeTree -> 直接 INSERT（重复键由 CH 后台合并）
- MergeTree -> 写前 DELETE WHERE date = today()
- 临时表 -> staging + INSERT SELECT DISTINCT（阶段3+ 实现）

设计要点：
- 不依赖 tmp/_ds_common.py（TTL=task_bound，src/ 不能长期依赖 tmp/）
- 自封装 _http_insert / tsv_escape / _get_insert_columns 逻辑
- 端点配置从 config/.env.clickhouse 读取，不硬编码 IP/端口
"""
from __future__ import annotations

import http.client
import logging
import os
import threading
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.data.provider_base import FetchResult

log = logging.getLogger(__name__)

# ClickHouse 连接配置（从 config/.env.clickhouse 读取）
# 环境变量由启动脚本（scheduler/worker）通过 dotenv 加载
_CH_HOST = os.environ.get("CLICKHOUSE_HOST", "172.24.30.100")
_CH_TCP_PORT = int(os.environ.get("CLICKHOUSE_PORT", "9000"))
_CH_HTTP_PORT = int(os.environ.get("CLICKHOUSE_HTTP_PORT", "8123"))

# 默认超时（秒）
_DEFAULT_TIMEOUT = 600

# SQL 常量集中化（NO-BARE-SQL gate 豁免 SQL_* 前缀）
SQL_ENGINE_BY_DB = "SELECT engine FROM system.tables WHERE database = '{}' AND name = '{}'"
SQL_ENGINE_BY_NAME = "SELECT engine FROM system.tables WHERE name = '{}'"
SQL_INSERT_TSV = "INSERT INTO {table} {cols_clause} SETTINGS max_partitions_per_insert_block=0 FORMAT TSV"

# clickhouse-driver TCP 客户端单例
_ch_client = None
# TCP 失败冷却时间戳（避免每次 query 都重试 TCP 连接）
_tcp_fail_ts: float = 0
_TCP_COOLDOWN_SEC = 15  # TCP 连接失败后 15 秒内不再重试

# 线程安全锁（run_schedule 并行化后多任务共用 ch_writer 全局状态）
# clickhouse-driver Client 非线程安全（TCP 长连接并发 execute 会导致协议错乱）
_ch_lock = threading.Lock()
# 连接创建锁（保护 _ch_client/_ch_http_host 单例创建，秒级临界区）
# 锁顺序：_cache_lock → _connect_lock → _ch_lock（单向，无死锁）
_connect_lock = threading.Lock()
# 表列/引擎缓存读写保护（防 TOCTOU 竞态，避免多线程重复查询）
_cache_lock = threading.Lock()


class WriteDisposition(str, Enum):
    """一次写入尝试的真实持久化位置。"""

    CH_COMMITTED = "ch_committed"
    LOCAL_DURABLE = "local_durable"
    NOT_DURABLE = "not_durable"


@dataclass(frozen=True)
class WriteOutcome:
    """写入结果；禁止把本地持久化伪装成 ClickHouse 已提交。"""

    disposition: WriteDisposition
    detail: str = ""

    @property
    def is_ch_committed(self) -> bool:
        return self.disposition is WriteDisposition.CH_COMMITTED


def _get_client():
    """获取 clickhouse-driver TCP 客户端单例（懒初始化）。

    clickhouse-driver 使用 ClickHouse 原生 TCP 协议（9000 端口）。

    连接策略（Hyper-V 迁移，2026-07-16）：
    - 直连配置的 CLICKHOUSE_HOST（默认 172.24.30.100，Hyper-V VM）
    - 失败则返回 None（触发 HTTP API fallback）
    - TCP 失败后冷却期内不再重试

    线程安全：
    - 用 _connect_lock 保护单例创建
    - 与 _ch_lock（execute 串行化）分离
    - 冷却期检查在锁外快速路径
    """
    global _ch_client, _tcp_fail_ts
    # 快速路径1（无锁读，CPython GIL 保证引用读原子）
    if _ch_client is not None:
        return _ch_client
    # 快速路径2：冷却期内跳过 TCP 连接尝试（无锁读）
    import time as _time
    if _tcp_fail_ts and (_time.time() - _tcp_fail_ts) < _TCP_COOLDOWN_SEC:
        return None
    with _connect_lock:
        # double-check（防止竞态期间其他线程已创建）
        if _ch_client is not None:
            return _ch_client
        # 锁内二次检查冷却期
        if _tcp_fail_ts and (_time.time() - _tcp_fail_ts) < _TCP_COOLDOWN_SEC:
            return None
        from clickhouse_driver import Client
        try:
            c = Client(host=_CH_HOST, port=_CH_TCP_PORT, connect_timeout=3,
                       tcp_keepalive=True, sync_request_timeout=10)
            c.execute("SELECT 1")
            _ch_client = c
            log.info("clickhouse-driver TCP 已连接 (%s:%s)", _CH_HOST, _CH_TCP_PORT)
            return _ch_client
        except Exception as e:
            log.warning("clickhouse-driver TCP 连接失败 (%s:%s): %s", _CH_HOST, _CH_TCP_PORT, e)
        _tcp_fail_ts = _time.time()
        return None


# HTTP 主机缓存 + 冷却期
_ch_http_host: str | None = None
_http_fail_ts: float = 0
_HTTP_COOLDOWN_SEC = 15  # HTTP 失败后 15 秒内不再重试（缩短冷却期减少偶发降级时间）


def _get_http_host() -> str:
    """获取可用的 ClickHouse HTTP 主机。

    策略（Hyper-V 迁移，2026-07-16）：
    - 直连配置的 CLICKHOUSE_HOST（默认 172.24.30.100）
    - 结果缓存到全局 _ch_http_host
    - HTTP 失败后冷却期内返回空字符串（调用方应降级到本地落盘）

    线程安全：
    - 用 _connect_lock double-check locking 保护单例创建
    - 冷却期检查在锁外快速路径
    """
    global _ch_http_host, _http_fail_ts
    # 快速路径1（无锁读）
    if _ch_http_host is not None:
        return _ch_http_host
    # 快速路径2：冷却期内跳过（无锁读）
    import time as _time
    if _http_fail_ts and (_time.time() - _http_fail_ts) < _HTTP_COOLDOWN_SEC:
        return ""
    with _connect_lock:
        # double-check
        if _ch_http_host is not None:
            return _ch_http_host
        if _http_fail_ts and (_time.time() - _http_fail_ts) < _HTTP_COOLDOWN_SEC:
            return ""
        # 直连配置的 ClickHouse host
        try:
            conn = http.client.HTTPConnection(_CH_HOST, _CH_HTTP_PORT, timeout=3)
            conn.request("GET", "/ping")
            resp = conn.getresponse()
            if resp.status == 200:
                _ch_http_host = _CH_HOST
                conn.close()
                log.info("ClickHouse HTTP 已连接 (%s:%s)", _CH_HOST, _CH_HTTP_PORT)
                return _ch_http_host
            conn.close()
        except Exception as e:
            log.warning("ClickHouse HTTP 连接失败 (%s:%s): %s", _CH_HOST, _CH_HTTP_PORT, e)
        # 兜底：HTTP 不可用，设置冷却时间戳
        _http_fail_ts = _time.time()
        log.warning("ClickHouse HTTP 不可用，%ds 内跳过", _HTTP_COOLDOWN_SEC)
        return ""


def _invalidate_tcp_client(reason: str = "") -> None:
    """清理已断开的 TCP 连接单例 + 设置冷却期（CH 重启自愈，裁定 #ARCH-CH-014）。

    当 client.execute 失败时调用，确保下次 _get_client() 会重新创建连接。
    不清理的话 _get_client 快速路径1返回旧 Client，冷却期机制完全失效。
    """
    global _ch_client, _tcp_fail_ts
    import time as _time
    with _connect_lock:
        if _ch_client is not None:
            try:
                _ch_client.disconnect()
            except Exception:
                pass
            _ch_client = None
            _tcp_fail_ts = _time.time()
            log.info("TCP 连接已失效（%s），%ds 冷却后重试", reason, _TCP_COOLDOWN_SEC)


def _invalidate_http_host(reason: str = "") -> None:
    """清理已断开的 HTTP host 单例 + 设置冷却期（CH 重启自愈，裁定 #ARCH-CH-014）。"""
    global _ch_http_host, _http_fail_ts
    import time as _time
    with _connect_lock:
        if _ch_http_host is not None:
            _ch_http_host = None
            _http_fail_ts = _time.time()
            log.info("HTTP 连接已失效（%s），%ds 冷却后重试", reason, _HTTP_COOLDOWN_SEC)


def _http_insert(
    sql: str,
    tsv_bytes: bytes,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """通过 ClickHouse HTTP API（8123端口）执行 INSERT。

    HTTP API 作为 TCP 失败时的降级通道：
    - 端点从 config/.env.clickhouse 读取（Hyper-V VM，裁定 #ARCH-CH-010 Phase 3）
    - 使用 http.client（比 urllib 更可靠）
    - POST body 传输 TSV 数据

    Args:
        sql: INSERT SQL 语句（如 "INSERT INTO table (cols) FORMAT TSV"）
        tsv_bytes: TSV 格式字节数据
        timeout: 超时秒数

    Returns:
        是否成功。
    """
    http_host = _get_http_host()
    if not http_host:
        return False  # HTTP 不可用（冷却期内或探测失败），调用方降级到本地落盘
    path = f"/?query={urllib.parse.quote(sql)}"
    try:
        conn = http.client.HTTPConnection(http_host, _CH_HTTP_PORT, timeout=timeout)
        conn.request("POST", path, body=tsv_bytes)
        resp = conn.getresponse()
        body = resp.read()
        conn.close()
        if resp.status == 200:
            return True
        log.error("HTTP insert 失败: status=%s, body=%s", resp.status, body[:200])
        return False
    except Exception as e:
        log.error("HTTP insert 异常: %s", e)
        _invalidate_http_host(f"insert HTTP 失败: {e}")
        return False


def query(sql: str, timeout: int = _DEFAULT_TIMEOUT) -> str:
    """执行 CH 查询，返回 TSV 格式字符串。

    二级传输（Hyper-V 迁移，2026-07-16）：
    - clickhouse-driver TCP → HTTP API（二级降级）
    - 移除 WSL subprocess fallback

    失败时 log 错误并返回空字符串（不抛异常）。
    """
    # 策略1: clickhouse-driver TCP
    client = _get_client()
    if client is not None:
        try:
            sql_stripped = sql.strip()
            # SELECT 查询：返回 TSV 格式
            if sql_stripped.upper().startswith("SELECT") or sql_stripped.upper().startswith("DESCRIBE"):
                with _ch_lock:  # 串行化 execute（clickhouse-driver Client 非线程安全）
                    rows = client.execute(sql, settings={"max_execution_time": timeout})
                if not rows:
                    return ""
                lines = []
                for row in rows:
                    lines.append("\t".join(str(v) for v in row))
                return "\n".join(lines) + "\n"
            else:
                # DDL 语句
                with _ch_lock:  # 串行化 execute
                    client.execute(sql, settings={"max_execution_time": timeout})
                return ""
        except Exception as e:
            log.warning("clickhouse-driver query 失败，降级到 HTTP: %s", e)
            _invalidate_tcp_client(f"query execute 失败: {e}")

    # 策略2: HTTP API
    http_host = _get_http_host()
    if http_host:
        path = f"/?query={urllib.parse.quote(sql)}"
        try:
            conn = http.client.HTTPConnection(http_host, _CH_HTTP_PORT, timeout=timeout)
            conn.request("GET", path)
            resp = conn.getresponse()
            if resp.status == 200:
                data = resp.read().decode("utf-8", errors="replace")
                conn.close()
                return data
            log.warning("HTTP query 失败: status=%s", resp.status)
            conn.close()
        except Exception as e:
            log.warning("HTTP query 失败: %s", e)
            _invalidate_http_host(f"query HTTP 失败: {e}")

    log.error("CH query 失败(TCP+HTTP 均失败): %s", sql[:200])
    return ""


def tsv_escape(v) -> str:
    """转义字段值用于 TSV。

    - None / NaN -> ``\\N``
    - 字符串去掉换行制表符（替换为空格）
    - 反斜杠转义

    Returns:
        TSV 安全的字符串。
    """
    if v is None:
        return "\\N"
    if isinstance(v, float) and v != v:  # NaN
        return "\\N"
    s = str(v)
    # TSV 中不能有 \n \t \r
    s = s.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ").replace("\r", " ")
    return s


def _get_insert_columns(table: str) -> str:
    """查询表的非 DEFAULT 列清单（用于 INSERT 时显式指定列）。

    DESCRIBE TABLE 输出字段: name, type, default_type, default_expression, ...
    排除 default_type 为 DEFAULT/MATERIALIZED/ALIAS 的列（CH 会自动填充）。

    Returns:
        "(col1, col2, ...)" 字符串。查询失败返回 "*"（由 CH 推断全部列）。
    """
    out = query(f"DESCRIBE TABLE {table}")
    if not out.strip():
        return "*"
    cols = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name = parts[0]
        default_type = parts[2] if len(parts) > 2 else ""
        if default_type in ("DEFAULT", "MATERIALIZED", "ALIAS"):
            continue
        cols.append(name)
    if not cols:
        return "*"
    return "(" + ", ".join(cols) + ")"


# 表列缓存（避免每次 write_result 都查 DESCRIBE TABLE）
_table_cols_cache: dict[str, set[str]] = {}


def _get_table_columns_set(table: str) -> set[str]:
    """查询表的全部列名集合（含 DEFAULT/MATERIALIZED/ALIAS 列）。

    用于 write_result 列过滤：只插入表中存在的列。

    线程安全：double-check locking（防 TOCTOU 竞态，避免多线程重复查询）。

    Returns:
        列名集合。查询失败返回空集合。
    """
    # 快速路径（无锁读）
    if table in _table_cols_cache:
        return _table_cols_cache[table]
    with _cache_lock:
        # double-check
        if table in _table_cols_cache:
            return _table_cols_cache[table]
        out = query(f"DESCRIBE TABLE {table}")
        if not out.strip():
            return set()
        cols = set()
        for line in out.split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 1:
                cols.add(parts[0])
        _table_cols_cache[table] = cols
        return cols


# 表引擎缓存（避免每次都查 system.tables）
_table_engine_cache: dict[str, str] = {}


def get_table_engine(table: str) -> str:
    """查询表的引擎类型（如 'MergeTree' / 'ReplacingMergeTree'）。

    用于幂等性决策（裁定 #ARCH-CH-002）：
    - ReplacingMergeTree -> 直接 INSERT（后台去重，无需写前 DELETE）
    - MergeTree -> 写前 DELETE WHERE（避免重复行）

    线程安全：double-check locking（防 TOCTOU 竞态）。

    Returns:
        引擎名字符串。查询失败返回空字符串。
    """
    # 快速路径（无锁读）
    if table in _table_engine_cache:
        return _table_engine_cache[table]
    with _cache_lock:
        # double-check
        if table in _table_engine_cache:
            return _table_engine_cache[table]
        # table 形如 "c1_market.kline_daily"，拆成 database + name
        parts = table.split(".", 1)
        if len(parts) == 2:
            db, name = parts
            sql = SQL_ENGINE_BY_DB.format(db, name)
        else:
            sql = SQL_ENGINE_BY_NAME.format(table)
        out = query(sql)
        engine = out.strip()
        _table_engine_cache[table] = engine
        return engine


def is_replacing_engine(table: str) -> bool:
    """判断表是否使用 ReplacingMergeTree 引擎族（含 Replicated 变体）。

    Returns:
        True 表示可直接 INSERT（后台去重），False 表示需写前 DELETE。
    """
    engine = get_table_engine(table)
    return "Replacing" in engine


def write_tsv_outcome(
    table: str,
    columns: str | None,
    tsv_bytes: bytes,
    timeout: int = _DEFAULT_TIMEOUT,
) -> WriteOutcome:
    """TSV 批量写入表。

    传输优先级（Hyper-V 迁移，2026-07-16）：
    1. HTTP API（8123端口）— 主路径
    2. 本地落盘兜底 — ClickHouse 不可达时数据不丢失

    Args:
        table: 完整表名（如 c1_market.kline_daily）
        columns: "(col1, col2, ...)" 字符串，None 时自动查询列清单
        tsv_bytes: TSV 格式字节数据
        timeout: 超时秒数

    Returns:
        真实投递结果。LOCAL_DURABLE 表示数据已安全落盘、待回灌，
        但尚未提交到 ClickHouse。
    """
    if not tsv_bytes:
        log.warning("write_tsv(%s): 空数据，跳过", table)
        return WriteOutcome(WriteDisposition.NOT_DURABLE, "empty payload")
    cols_clause = columns if columns else _get_insert_columns(table)
    sql = SQL_INSERT_TSV.format(table=table, cols_clause=cols_clause)

    # 策略1: HTTP API（主路径）
    if _http_insert(sql, tsv_bytes, timeout=timeout):
        return WriteOutcome(WriteDisposition.CH_COMMITTED, "http")
    log.warning("write_tsv(%s): HTTP API 失败，降级到本地落盘", table)

    # 策略2: 本地落盘兜底（裁定 #ARCH-CH-013，CH 不可达时数据不丢失）
    # 数据写入本地 TSV 文件，待 CH 恢复后自动回灌
    from zephyr.data.local_replay import save_fallback
    # cols_clause=="*" 意味着 _get_insert_columns 在 CH 不可用时返回的未校验值，
    # 回灌时 "INSERT INTO t * FORMAT TSV" 非法；存 None 让回灌时重新查询表列
    # （裁定 #ARCH-CH-013 Phase 1 根因修复）
    fallback_cols = None if cols_clause == "*" else cols_clause
    if save_fallback(table, fallback_cols, tsv_bytes):
        return WriteOutcome(WriteDisposition.LOCAL_DURABLE, "local_fallback")
    return WriteOutcome(WriteDisposition.NOT_DURABLE, "local_fallback_failed")


def write_tsv(
    table: str,
    columns: str | None,
    tsv_bytes: bytes,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """兼容旧调用方：仅 ClickHouse 已提交才返回 ``True``。

    新调用方必须使用 :func:`write_tsv_outcome`，以区别本地持久化和入库成功。
    """
    return write_tsv_outcome(table, columns, tsv_bytes, timeout).is_ch_committed


def write_result(
    result: "FetchResult",
    columns: str | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """把 FetchResult 写入 ClickHouse。

    Args:
        result: FetchResult（含 table/columns/rows）
        columns: 显式列名 "(col1, col2, ...)"，None 时用 result.columns 构造或自动查询
        timeout: 超时秒数

    Returns:
        是否成功。result.error 非 None 时跳过写入返回 False。
    """
    if result.error:
        log.warning("write_result(%s): FetchResult.error=%s，跳过", result.table, result.error)
        return False
    if not result.rows:
        log.info("write_result(%s): 无数据行，跳过", result.table)
        return True

    # 确定列子句和行数据
    if columns:
        # 显式指定的列，直接用
        cols_clause = columns
        rows = result.rows
    elif result.columns:
        # 自动列过滤：只插入表中存在的列
        table_cols = _get_table_columns_set(result.table)
        if table_cols:
            common_cols = [c for c in result.columns if c in table_cols]
            if not common_cols:
                log.error("write_result(%s): result.columns 与表列无交集", result.table)
                return False
            if len(common_cols) < len(result.columns):
                # 有列被过滤，调整 rows
                keep_indices = [i for i, c in enumerate(result.columns) if c in table_cols]
                rows = [tuple(row[i] for i in keep_indices) for row in result.rows]
                log.info(
                    "write_result(%s): 列过滤 %d->%d（忽略 %d 个不匹配列）",
                    result.table, len(result.columns), len(common_cols),
                    len(result.columns) - len(common_cols),
                )
            else:
                rows = result.rows
            cols_clause = "(" + ", ".join(common_cols) + ")"
        else:
            # CH 不可用：无法校验列，落盘 None 让回灌时（CH 已恢复）重新查询表列
            # 原样用 result.columns 会固化不可信列名（如 Provider 占位符 col1），
            # 回灌时 INSERT 失败永久卡死（裁定 #ARCH-CH-013 Phase 1 根因修复）
            cols_clause = None
            rows = result.rows
    else:
        cols_clause = None  # write_tsv 内部自动查询
        rows = result.rows

    # 构造 TSV 字节
    tsv_lines = []
    for row in rows:
        tsv_lines.append("\t".join(tsv_escape(v) for v in row))
    tsv_bytes = "\n".join(tsv_lines).encode("utf-8")

    return write_tsv(result.table, cols_clause, tsv_bytes, timeout=timeout)


def delete_where(
    table: str,
    condition: str,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """删除满足条件的行（用于 MergeTree 幂等性：写前 DELETE）。

    二级传输（Hyper-V 迁移，2026-07-16）：优先 clickhouse-driver TCP，失败降级 HTTP。
    两者均失败返回 False（调用方应依据返回值决定是否跳过本批次写入）。

    Args:
        table: 表名
        condition: WHERE 条件（如 "date = '2026-07-05'"）
        timeout: 超时秒数

    Returns:
        是否成功。
    """
    sql = f"ALTER TABLE {table} DELETE WHERE {condition}"
    # 策略1: clickhouse-driver TCP
    client = _get_client()
    if client is not None:
        try:
            with _ch_lock:  # 串行化 execute（clickhouse-driver Client 非线程安全）
                client.execute(sql, settings={"max_execution_time": timeout})
            return True
        except Exception as e:
            log.warning("clickhouse-driver delete 失败，降级到 HTTP: %s", e)
            _invalidate_tcp_client(f"delete execute 失败: {e}")
    # 策略2: HTTP API
    http_host = _get_http_host()
    if http_host:
        path = f"/?query={urllib.parse.quote(sql)}"
        try:
            conn = http.client.HTTPConnection(http_host, _CH_HTTP_PORT, timeout=timeout)
            conn.request("POST", path)
            resp = conn.getresponse()
            if resp.status == 200:
                conn.close()
                return True
            log.warning("HTTP delete 失败: status=%s", resp.status)
            conn.close()
        except Exception as e:
            log.warning("HTTP delete 失败: %s", e)
            _invalidate_http_host(f"delete HTTP 失败: {e}")
    log.error("CH delete 失败(TCP+HTTP 均失败): %s WHERE %s", table, condition)
    return False


def delete_by_date_range(
    table: str,
    date_col: str,
    dates: list[str],
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """按日期范围删除行（MergeTree 幂等性便捷方法）。

    封装 delete_where，自动构造 ``toDate(date_col) IN (...)`` 条件。
    date_col 应从 tasks.yaml 读取（SSoT），禁止硬编码列名。

    Args:
        table: 表名（如 c3_fundamental.share_unlock）
        date_col: 日期列名（如 unlock_date），从 tasks.yaml date_col 字段读取
        dates: 日期字符串列表（如 ["2026-07-13", "2026-07-14"]）
        timeout: 超时秒数

    Returns:
        是否成功。
    """
    if not dates:
        return True
    date_list = ", ".join(f"toDate('{d}')" for d in dates)
    return delete_where(table, f"toDate({date_col}) IN ({date_list})", timeout=timeout)


def health_check() -> dict[str, str]:
    """ClickHouse 连接健康检查（裁定 #ARCH-CH-010 Phase 2.2）。

    逐级探测二级传输路径（TCP + HTTP），返回每级状态。
    用于启动诊断和运行时监控。WSL subprocess 通道已随 Hyper-V 迁移移除。

    Returns:
        {"tcp": "ok"|"fail", "http": "ok"|"fail", "http_host": str,
         "endpoint": str}
    """
    result: dict[str, str] = {}
    result["endpoint"] = f"{_CH_HOST}:{_CH_TCP_PORT}/{_CH_HTTP_PORT}"

    # TCP 探测（重置冷却期强制测试）
    global _tcp_fail_ts, _ch_client, _ch_http_host, _http_fail_ts
    old_tcp_ts = _tcp_fail_ts
    old_client = _ch_client
    _tcp_fail_ts = 0
    _ch_client = None
    try:
        c = _get_client()
        if c is not None:
            c.execute("SELECT 1")
            result["tcp"] = "ok"
        else:
            result["tcp"] = "fail"
    except Exception:
        result["tcp"] = "fail"
    finally:
        # 恢复原状态（不污染全局单例）
        _tcp_fail_ts = old_tcp_ts
        _ch_client = old_client

    # HTTP 探测（重置冷却期强制测试）
    old_http_ts = _http_fail_ts
    old_http_host = _ch_http_host
    _http_fail_ts = 0
    _ch_http_host = None
    host = _get_http_host()
    result["http_host"] = host or ""
    if host:
        try:
            conn = http.client.HTTPConnection(host, _CH_HTTP_PORT, timeout=5)
            conn.request("GET", "/ping")
            resp = conn.getresponse()
            result["http"] = "ok" if resp.status == 200 else f"status:{resp.status}"
            conn.close()
        except Exception as e:
            result["http"] = f"fail:{type(e).__name__}"
    else:
        result["http"] = "fail"
    # 恢复原状态
    _http_fail_ts = old_http_ts
    _ch_http_host = old_http_host

    return result
