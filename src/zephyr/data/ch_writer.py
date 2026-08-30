# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] http.client(标准库); clickhouse-driver(pip); zephyr.data.local_replay; zephyr.data.ch_config; zephyr.shared.observability.metrics
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 二级降级：query/delete_where 走 clickhouse-driver TCP(9000)，write_tsv 走 HTTP API(8123)→本地落盘兜底(local_replay); 幂等性由调用方决定(ReplacingMergeTree直接INSERT/MergeTree写前DELETE); HTTP 传输用 http.client; ClickHouse 不可达时数据写入本地 TSV 文件待回灌（裁定 #ARCH-CH-013）; create_fallback=False 时HTTP失败跳过本地落盘（回灌路径专用，防重复TSV）; health_check() 提供传输路径健康诊断
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] write_result失败->返回False+log; query失败->返回空字符串; delete_where失败->返回False
# [TESTS] tests/zephyr/data/test_ch_writer.py
# [A_module] module_id=MOD-GOV-ch_writer | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""



ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步 + §7.3 幂等性）。

二级传输架构（Hyper-V 迁移，2026-07-16 修订）：
- query/delete_where → clickhouse-driver TCP（9000端口）
- write_tsv → HTTP API（8123端口，POST TSV body）→ 本地落盘兜底
- 端点从 config/.env.clickhouse 读取（CLICKHOUSE_HOST / CLICKHOUSE_HTTP_PORT）
- 移除 WSL subprocess fallback（裁定 #ARCH-CH-010 Phase 3 迁移至 Hyper-V VM）

提供：
- write_result(result): 把 FetchResult.rows 转 TSV 写入 CH
- tsv_escape(v): 转义字段值（None/NaN -> \N，字符串去换行制表符）
- delete_where(table, condition): 写前删除（MergeTree 幂等性）
- query(sql): 查询 CH（用于 DESCRIBE TABLE 获取列清单）
- ensure_database(name): 建库前置容错（#256③ 路线B：存在即过，缺失才 CREATE，权限不足 fail-visible）
- get_table_engine(table) / is_replacing_engine(table): 查询表引擎，辅助幂等性决策（裁定 #ARCH-CH-002）

幂等性策略（§7.3）：
- ReplacingMergeTree -> 直接 INSERT（重复键由 CH 后台合并）
- MergeTree -> 写前 DELETE WHERE date = today()
- 临时表 -> staging + INSERT SELECT DISTINCT（阶段3+ 实现）

设计要点：
- 不依赖 tmp/_ds_common.py（TTL=task_bound，src/ 不能长期依赖 tmp/）
- 自封装 http_insert / tsv_escape / get_insert_columns 逻辑
- 端点配置从 config/.env.clickhouse 读取，不硬编码 IP/端口

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: sql 参数
#   fields: 参数 sql，类型注解 str
#   code: ch_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: tsv_bytes 参数
#   fields: 参数 tsv_bytes，类型注解 bytes
#   code: ch_writer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: timeout 参数
#   fields: 参数 timeout，类型注解 int
#   code: ch_writer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: name 参数
#   fields: 参数 name，类型注解 str
#   code: ch_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① WriteOutcome
#   name_en: WriteOutcome
#   intro: 写入结果；禁止把本地持久化伪装成 ClickHouse 已提交。
#   desc: 写入结果；禁止把本地持久化伪装成 ClickHouse 已提交。；公共方法（定义序）: is_ch_committed；源码 L240-L248
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_client
#   name_en: get_client
#   intro: 获取 clickhouse-driver TCP 客户端单例（懒初始化）。
#   desc: 获取 clickhouse-driver TCP 客户端单例（懒初始化）。 clickhouse-driver 使用 ClickHouse 原生 TCP 协议（9000 端口）。…；源码 L266-L320
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ get_http_host
#   name_en: get_http_host
#   intro: 获取可用的 ClickHouse HTTP 主机。
#   desc: 获取可用的 ClickHouse HTTP 主机。 策略（Hyper-V 迁移，2026-07-16）： - 直连配置的 CLICKHOUSE_HOST（默认 172.24.30…；源码 L335-L380
#   inputs: 无参数
#   outputs: str
# - id: A4
#   name_zh: ④ http_insert
#   name_en: http_insert
#   intro: 通过 ClickHouse HTTP API（8123端口）执行 INSERT。
#   desc: 通过 ClickHouse HTTP API（8123端口）执行 INSERT。 HTTP API 作为 TCP 失败时的降级通道： - 端点从 config/.env.clic…；源码 L434-L471
#   inputs: sql tsv_bytes timeout
#   outputs: bool
# - id: A5
#   name_zh: ⑤ query
#   name_en: query
#   intro: 执行 CH 查询，返回 TSV 格式字符串。
#   desc: 执行 CH 查询，返回 TSV 格式字符串。 二级传输（Hyper-V 迁移，2026-07-16）： - clickhouse-driver TCP → HTTP API（二级…；源码 L483-L540
#   inputs: sql timeout
#   outputs: str
# - id: A6
#   name_zh: ⑥ ensure_database
#   name_en: ensure_database
#   intro: 确保数据库存在（#256③ 路线B：writer 无 CREATE DATABASE 权限的容错通道）。
#   desc: 确保数据库存在（#256③ 路线B：writer 无 CREATE DATABASE 权限的容错通道）。 语义： - 库已存在（system.databases 可查，write…；源码 L543-L572
#   inputs: name timeout
#   outputs: bool
# - id: A7
#   name_zh: ⑦ tsv_escape
#   name_en: tsv_escape
#   intro: 转义字段值用于 TSV。
#   desc: 转义字段值用于 TSV。 - None / NaN -> ``\N`` - 字符串去掉换行制表符（替换为空格） - 反斜杠转义 Returns: TSV 安全的字符串。；源码 L575-L595
#   inputs: v
#   outputs: str
# - id: A8
#   name_zh: ⑧ get_insert_columns
#   name_en: get_insert_columns
#   intro: 查询表的可插入列清单（用于 INSERT 时显式指定列）。
#   desc: 查询表的可插入列清单（用于 INSERT 时显式指定列）。 DESCRIBE TABLE 输出字段: name, type, default_type, default_expr…；源码 L612-L650
#   inputs: table
#   outputs: str
# - id: A9
#   name_zh: ⑨ get_table_columns_set
#   name_en: get_table_columns_set
#   intro: 查询表的全部列名集合（含 DEFAULT/MATERIALIZED/ALIAS 列）。
#   desc: 查询表的全部列名集合（含 DEFAULT/MATERIALIZED/ALIAS 列）。 用于 write_result 列过滤：只插入表中存在的列。 线程安全：double-ch…；源码 L663-L691
#   inputs: table
#   outputs: set[str]
# - id: A10
#   name_zh: ⑩ get_insertable_columns_set
#   name_en: get_insertable_columns_set
#   intro: 查询表的可插入列名集合（排除 MATERIALIZED/ALIAS，保留 DEFAULT 和普通列）。
#   desc: 查询表的可插入列名集合（排除 MATERIALIZED/ALIAS，保留 DEFAULT 和普通列）。 用于 write_result / buffered_writer / w…；源码 L703-L746
#   inputs: table
#   outputs: set[str]
#   （注：A10 之后另有 9 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

import http.client
import logging
import os
import threading
import time
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.data.provider_base import FetchResult

log = logging.getLogger(__name__)

# ClickHouse 连接配置（裁定 #ARCH-CH-017：真源为 config/.env.clickhouse）
# 由 ch_config.ensure_ch_env_loaded() 主动加载到 os.environ，禁止硬编码 IP 默认值。
# 配置缺失时 _CH_HOST 为空字符串，连接时 fail-closed（Client(host="") 会失败）。
from zephyr.data.ch_config import ensure_ch_env_loaded as _ensure_ch_env_loaded

_ensure_ch_env_loaded()

# P1-5 metrics 埋点（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase E 补齐）
from zephyr.shared.observability.metrics import get_registry as _get_metrics_registry
from zephyr.shared.security.secrets import get_secret_or_default

_CH_HOST = get_secret_or_default("CLICKHOUSE_HOST", "")
_CH_TCP_PORT = int(get_secret_or_default("CLICKHOUSE_PORT", "9000"))
_CH_HTTP_PORT = int(get_secret_or_default("CLICKHOUSE_HTTP_PORT", "8123"))

# audit 9.4 RBAC（#ARCH-CH-027，2026-07-23 治本）：
# 写入路径使用 zephyr_writer 账号（DB 级 INSERT/ALTER/CREATE/DROP/OPTIMIZE 权限）
# 未配置 CLICKHOUSE_WRITER_USER 时回退到 CLICKHOUSE_USER（向后兼容）
_CH_USER = get_secret_or_default("CLICKHOUSE_WRITER_USER") or get_secret_or_default("CLICKHOUSE_USER", "default")
_CH_PASSWORD = get_secret_or_default("CLICKHOUSE_WRITER_PASSWORD") or get_secret_or_default("CLICKHOUSE_PASSWORD", "")

# 默认超时（秒）
_DEFAULT_TIMEOUT = 600

# SQL 常量集中化（NO-BARE-SQL gate 豁免 SQL_* 前缀）
SQL_ENGINE_BY_DB = "SELECT engine FROM system.tables WHERE database = '{}' AND name = '{}'"
SQL_ENGINE_BY_NAME = "SELECT engine FROM system.tables WHERE name = '{}'"
SQL_INSERT_TSV = (
    "INSERT INTO {table} {cols_clause} SETTINGS async_insert=0, max_partitions_per_insert_block=0 FORMAT TSV"
)

# clickhouse-driver TCP 客户端单例
ch_client = None
_ch_client = ch_client  # 向后兼容别名（R5 公共化）
# TCP 失败冷却时间戳（避免每次 query 都重试 TCP 连接）
_tcp_fail_ts: float = 0
_TCP_COOLDOWN_SEC = 15  # TCP 连接失败后 15 秒内不再重试

# 线程安全锁（run_schedule 并行化后多任务共用 ch_writer 全局状态）
# clickhouse-driver Client 非线程安全（TCP 长连接并发 execute 会导致协议错乱）
_ch_lock = threading.Lock()
# 连接创建锁（保护 ch_client/ch_http_host 单例创建，秒级临界区）
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


# P1-5 metrics 埋点映射（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase E 补齐）
_OUTCOME_LABELS: dict[WriteDisposition, str] = {
    WriteDisposition.CH_COMMITTED: "committed",
    WriteDisposition.LOCAL_DURABLE: "local",
    WriteDisposition.NOT_DURABLE: "not_durable",
}


def _record_write_outcome(disposition: WriteDisposition, elapsed: float) -> None:
    """记录 CH 写入 metrics：Counter(outcome label) + Histogram(latency)。"""
    reg = _get_metrics_registry()
    reg.inc("zephyr_ch_write_total", {"outcome": _OUTCOME_LABELS.get(disposition, "unknown")})
    reg.observe("zephyr_ch_write_latency_seconds", elapsed)


def get_client():
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
    global ch_client, _tcp_fail_ts
    # 快速路径1（无锁读，CPython GIL 保证引用读原子）
    if ch_client is not None:
        return ch_client
    # 快速路径2：冷却期内跳过 TCP 连接尝试（无锁读）
    import time as _time

    if _tcp_fail_ts and (_time.time() - _tcp_fail_ts) < _TCP_COOLDOWN_SEC:
        return None
    with _connect_lock:
        # double-check（防止竞态期间其他线程已创建）
        if ch_client is not None:
            return ch_client
        # 锁内二次检查冷却期
        if _tcp_fail_ts and (_time.time() - _tcp_fail_ts) < _TCP_COOLDOWN_SEC:
            return None
        # 治本修复#ARCH-CH-FALLBACK-001（2026-07-24）：import 移入 try 块，
        # 缺 clickhouse_driver 时降级到 HTTP 而非抛 ImportError（原 bug：import 在 try 外）
        try:
            from clickhouse_driver import Client

            c = Client(
                host=_CH_HOST,
                port=_CH_TCP_PORT,
                user=_CH_USER,
                password=_CH_PASSWORD,
                connect_timeout=3,
                tcp_keepalive=True,
                sync_request_timeout=10,
            )
            c.execute("SELECT 1")
            ch_client = c
            _get_metrics_registry().set_gauge("zephyr_ch_tcp_cooldown_active", 0)
            log.info("clickhouse-driver TCP 已连接 (%s:%s)", _CH_HOST, _CH_TCP_PORT)
            return ch_client
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("clickhouse-driver TCP 连接失败 (%s:%s): %s", _CH_HOST, _CH_TCP_PORT, e)
        _tcp_fail_ts = _time.time()
        _get_metrics_registry().set_gauge("zephyr_ch_tcp_cooldown_active", 1)
        return None


def _get_client():
    """向后兼容 thin wrapper（R5 公共化）。"""
    return get_client()


# HTTP 主机缓存 + 冷却期
ch_http_host: str | None = None
_ch_http_host = ch_http_host  # 向后兼容别名（R5 公共化）
_http_fail_ts: float = 0
_HTTP_COOLDOWN_SEC = 15  # HTTP 失败后 15 秒内不再重试（缩短冷却期减少偶发降级时间）


def get_http_host() -> str:
    """获取可用的 ClickHouse HTTP 主机。

    策略（Hyper-V 迁移，2026-07-16）：
    - 直连配置的 CLICKHOUSE_HOST（默认 172.24.30.100）
    - 结果缓存到全局 ch_http_host
    - HTTP 失败后冷却期内返回空字符串（调用方应降级到本地落盘）

    线程安全：
    - 用 _connect_lock double-check locking 保护单例创建
    - 冷却期检查在锁外快速路径
    """
    global ch_http_host, _http_fail_ts
    # 快速路径1（无锁读）
    if ch_http_host is not None:
        return ch_http_host
    # 快速路径2：冷却期内跳过（无锁读）
    import time as _time

    if _http_fail_ts and (_time.time() - _http_fail_ts) < _HTTP_COOLDOWN_SEC:
        return ""
    with _connect_lock:
        # double-check
        if ch_http_host is not None:
            return ch_http_host
        if _http_fail_ts and (_time.time() - _http_fail_ts) < _HTTP_COOLDOWN_SEC:
            return ""
        # 直连配置的 ClickHouse host
        try:
            conn = http.client.HTTPConnection(_CH_HOST, _CH_HTTP_PORT, timeout=3)
            conn.request("GET", "/ping")
            resp = conn.getresponse()
            if resp.status == 200:
                ch_http_host = _CH_HOST
                conn.close()
                _get_metrics_registry().set_gauge("zephyr_ch_http_cooldown_active", 0)
                log.info("ClickHouse HTTP 已连接 (%s:%s)", _CH_HOST, _CH_HTTP_PORT)
                return ch_http_host
            conn.close()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("ClickHouse HTTP 连接失败 (%s:%s): %s", _CH_HOST, _CH_HTTP_PORT, e)
        # 兜底：HTTP 不可用，设置冷却时间戳
        _http_fail_ts = _time.time()
        _get_metrics_registry().set_gauge("zephyr_ch_http_cooldown_active", 1)
        log.warning("ClickHouse HTTP 不可用，%ds 内跳过", _HTTP_COOLDOWN_SEC)
        return ""


def _get_http_host() -> str:
    """向后兼容 thin wrapper（R5 公共化）。"""
    return get_http_host()


def _invalidate_tcp_client(reason: str = "") -> None:
    """清理已断开的 TCP 连接单例 + 设置冷却期（CH 重启自愈，裁定 #ARCH-CH-014）。

    当 client.execute 失败时调用，确保下次 get_client() 会重新创建连接。
    不清理的话 get_client 快速路径1返回旧 Client，冷却期机制完全失效。
    """
    global ch_client, _tcp_fail_ts
    import time as _time

    with _connect_lock:
        if ch_client is not None:
            try:
                ch_client.disconnect()
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                pass
            ch_client = None
            _tcp_fail_ts = _time.time()
            _get_metrics_registry().set_gauge("zephyr_ch_tcp_cooldown_active", 1)
            log.info("TCP 连接已失效（%s），%ds 冷却后重试", reason, _TCP_COOLDOWN_SEC)


def _invalidate_http_host(reason: str = "") -> None:
    """清理已断开的 HTTP host 单例 + 设置冷却期（CH 重启自愈，裁定 #ARCH-CH-014）。"""
    global ch_http_host, _http_fail_ts
    import time as _time

    with _connect_lock:
        if ch_http_host is not None:
            ch_http_host = None
            _http_fail_ts = _time.time()
            _get_metrics_registry().set_gauge("zephyr_ch_http_cooldown_active", 1)
            log.info("HTTP 连接已失效（%s），%ds 冷却后重试", reason, _HTTP_COOLDOWN_SEC)


def _ch_http_headers() -> dict[str, str]:
    """返回 CH HTTP API 认证头（audit 9.4 RBAC #ARCH-CH-027）。

    使用 X-ClickHouse-User/X-ClickHouse-Key 头传递 zephyr_writer 凭据，
    避免 URL query string 暴露密码到日志。
    """
    return {
        "X-ClickHouse-User": _CH_USER,
        "X-ClickHouse-Key": _CH_PASSWORD,
    }


def http_insert(
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
    http_host = get_http_host()
    if not http_host:
        return False  # HTTP 不可用（冷却期内或探测失败），调用方降级到本地落盘
    path = f"/?query={urllib.parse.quote(sql)}"
    try:
        conn = http.client.HTTPConnection(http_host, _CH_HTTP_PORT, timeout=timeout)
        conn.request("POST", path, body=tsv_bytes, headers=_ch_http_headers())
        resp = conn.getresponse()
        body = resp.read()
        conn.close()
        if resp.status == 200:
            return True
        log.error("HTTP insert 失败: status=%s, body=%s", resp.status, body[:200])
        return False
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.error("HTTP insert 异常: %s", e)
        _invalidate_http_host(f"insert HTTP 失败: {e}")
        return False


def _http_insert(
    sql: str,
    tsv_bytes: bytes,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """向后兼容 thin wrapper（R5 公共化）。"""
    return http_insert(sql, tsv_bytes, timeout=timeout)


def query(sql: str, timeout: int = _DEFAULT_TIMEOUT) -> str:
    """执行 CH 查询，返回 TSV 格式字符串。

    二级传输（Hyper-V 迁移，2026-07-16）：
    - clickhouse-driver TCP → HTTP API（二级降级）
    - 移除 WSL subprocess fallback

    失败时 log 错误并返回空字符串（不抛异常）。
    """
    # 策略1: clickhouse-driver TCP
    client = get_client()
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
                    # 手工拼 TSV 须中和值内嵌 \t/\r/\n（2026-08-26 实证：2015 年新闻
                    # content 含真实制表符→伪 TSV 单行爆成 97 字段、采集崩溃）；
                    # 与 tsv_escape 写侧同策（替换为空格），不动 None 语义
                    lines.append(
                        "\t".join(str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ") for v in row)
                    )
                return "\n".join(lines) + "\n"
            else:
                # DDL 语句
                with _ch_lock:  # 串行化 execute
                    client.execute(sql, settings={"max_execution_time": timeout})
                return ""
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("clickhouse-driver query 失败，降级到 HTTP: %s", e)
            _invalidate_tcp_client(f"query execute 失败: {e}")

    # 策略2: HTTP API
    http_host = get_http_host()
    if http_host:
        path = f"/?query={urllib.parse.quote(sql)}"
        try:
            conn = http.client.HTTPConnection(http_host, _CH_HTTP_PORT, timeout=timeout)
            conn.request("GET", path, headers=_ch_http_headers())
            resp = conn.getresponse()
            if resp.status == 200:
                data = resp.read().decode("utf-8", errors="replace")
                conn.close()
                return data
            log.warning("HTTP query 失败: status=%s", resp.status)
            conn.close()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("HTTP query 失败: %s", e)
            _invalidate_http_host(f"query HTTP 失败: {e}")

    log.error("CH query 失败(TCP+HTTP 均失败): %s", sql[:200])
    return ""


def ensure_database(name: str, timeout: int = _DEFAULT_TIMEOUT) -> bool:
    """确保数据库存在（#256③ 路线B：writer 无 CREATE DATABASE 权限的容错通道）。

    语义：
    - 库已存在（system.databases 可查，writer 有 SELECT ON system.*）→ 直接返回 True，
      不发 CREATE DATABASE（避免权限错误走 query() 降级链：TCP 失效 churn + HTTP 伪报）；
    - 库不存在 → 尝试 CREATE DATABASE（仅 admin 凭据场景会成功）；权限不足/失败 →
      log.error fail-visible 并返回 False（调用方应中止，防后续建表连环伪报）。

    治本路径：生产库由管理员预建（scripts/ch/apply_rbac.py apply() 预建步骤），
    writer 凭据永不需要 CREATE DATABASE（2026-08-22 实证 Code 497）。
    """
    probe = query(f"SELECT name FROM system.databases WHERE name = '{name}'", timeout=timeout)
    if probe.strip():
        return True
    client = get_client()
    if client is None:
        log.error("ensure_database(%s): 库不存在且 TCP 不可用——需管理员预建（apply_rbac.py）", name)
        return False
    try:
        with _ch_lock:  # 串行化 execute（clickhouse-driver Client 非线程安全）
            client.execute(f"CREATE DATABASE IF NOT EXISTS {name}", settings={"max_execution_time": timeout})
        return True
    except Exception as e:  # noqa: BLE001 — 权限不足属预期分支，fail-visible 返回 False
        log.error(
            "ensure_database(%s): CREATE DATABASE 失败（writer 无权限时需管理员预建，apply_rbac.py）: %s",
            name,
            e,
        )
        return False


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
    # TSV 中不能有 \x00（CH TSV 解析器遇 \x00 状态错乱，#ARCH-CH-023）
    # 也不能有 \n \t \r 及其他控制字符（0x01-0x08, 0x0B, 0x0C, 0x0E-0x1F）
    s = s.replace("\x00", "")  # NULL 字节直接删除（mootdx C 扩展泄漏的终止符）
    s = s.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ").replace("\r", " ")
    s = "".join(c if ord(c) >= 0x20 else " " for c in s)  # 控制字符→空格
    return s


def _parse_cols_clause(columns: str) -> list[str] | None:
    """解析 "(col1, col2, ...)" 形式的列子句为列名列表。

    供质量门禁按列名定位 OHLC 索引。解析失败或输入为 "*" 返回 None。
    """
    if not columns or columns.strip() == "*":
        return None
    inner = columns.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    parts = [p.strip().strip("`").strip('"') for p in inner.split(",")]
    return [p for p in parts if p] or None


def get_insert_columns(table: str) -> str:
    """查询表的可插入列清单（用于 INSERT 时显式指定列）。

    DESCRIBE TABLE 输出字段: name, type, default_type, default_expression, ...
    排除 default_type 为 MATERIALIZED/ALIAS 的列（CH 禁止 INSERT）。
    保留 DEFAULT 列（可显式提供值覆盖默认值），与 get_insertable_columns_set 一致。

    修复(2026-08-05): 原实现排除 DEFAULT 列，导致 write_tsv 降级路径
    （_cols_clause=None 时）返回的列数与 TSV 数据列数不匹配（provider
    提供 DEFAULT 列值时 INSERT 报 Code 27 Cannot parse input）。

    修复(2026-08-09): DESCRIBE 失败时原返回 "*"，生成非法 SQL
    "INSERT INTO t * SETTINGS ..."（CH 不支持 INSERT INTO t * 语法），
    导致 err.log 疯涨。改为返回 "" 生成合法 SQL "INSERT INTO t SETTINGS ...
    FORMAT TSV"（无列子句 = 插入全部列）。调用方（BufferedWriter/write_result）
    应在 DESCRIBE 失败时用 result.columns 构造显式列子句，避免列数不匹配。

    Returns:
        "(col1, col2, ...)" 字符串。查询失败返回 ""（空串 = 无列子句，
        CH 按 TSV 字段顺序插入全部列，调用方应确保 TSV 列数 = 表列数）。
    """
    out = query(f"DESCRIBE TABLE {table}")
    if not out.strip():
        return ""
    cols = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name = parts[0]
        default_type = parts[2] if len(parts) > 2 else ""
        if default_type in ("MATERIALIZED", "ALIAS"):
            continue
        cols.append(name)
    if not cols:
        return ""
    return "(" + ", ".join(cols) + ")"


def _get_insert_columns(table: str) -> str:
    """向后兼容 thin wrapper（R5 公共化）。"""
    return get_insert_columns(table)


# 表列缓存（避免每次 write_result 都查 DESCRIBE TABLE）
table_cols_cache: dict[str, set[str]] = {}
_table_cols_cache = table_cols_cache  # 向后兼容别名（R5 公共化）


def get_table_columns_set(table: str) -> set[str]:
    """查询表的全部列名集合（含 DEFAULT/MATERIALIZED/ALIAS 列）。

    用于 write_result 列过滤：只插入表中存在的列。

    线程安全：double-check locking（防 TOCTOU 竞态，避免多线程重复查询）。

    Returns:
        列名集合。查询失败返回空集合。
    """
    # 快速路径（无锁读）
    if table in table_cols_cache:
        return table_cols_cache[table]
    with _cache_lock:
        # double-check
        if table in table_cols_cache:
            return table_cols_cache[table]
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
        table_cols_cache[table] = cols
        return cols


def _get_table_columns_set(table: str) -> set[str]:
    """向后兼容 thin wrapper（R5 公共化）。"""
    return get_table_columns_set(table)


# 可插入列缓存（排除 MATERIALIZED/ALIAS，#ARCH-CH-MATERIALIZED-INSERT）
table_insertable_cols_cache: dict[str, set[str]] = {}


def get_insertable_columns_set(table: str) -> set[str]:
    """查询表的可插入列名集合（排除 MATERIALIZED/ALIAS，保留 DEFAULT 和普通列）。

    用于 write_result / buffered_writer / wal_writer 的列过滤（替代 get_table_columns_set）：
    - MATERIALIZED/ALIAS 列由 CH 自动计算或不存储，CH 禁止 INSERT，必须排除
    - DEFAULT 列可 INSERT（显式提供值覆盖默认值），保留以支持 provider 提供值
    - 修复 #ARCH-CH-MATERIALIZED-INSERT（2026-08-03）：原 write_result 用
      get_table_columns_set（含 MATERIALIZED 列）做交集，导致 provider 返回的
      MATERIALIZED 列（如 stock_list.exchange / industry_class.exchange）被保留在
      cols_clause，INSERT 时 CH 报 Code 44 "Cannot insert column X, because it is
      MATERIALIZED column"，数据落 fallback 后回灌永久失败（8/1 起积压 6 个坏文件）。

    与 get_table_columns_set 的区别：后者返回全部列（含 MATERIALIZED/ALIAS），仅用于
    "列是否存在"判断；本函数返回可 INSERT 的列，用于构造 cols_clause。

    线程安全：double-check locking（防 TOCTOU 竞态）。

    Returns:
        可插入列名集合。查询失败返回空集合（调用方将降级到 None cols_clause）。
    """
    # 快速路径（无锁读）
    if table in table_insertable_cols_cache:
        return table_insertable_cols_cache[table]
    with _cache_lock:
        # double-check
        if table in table_insertable_cols_cache:
            return table_insertable_cols_cache[table]
        out = query(f"DESCRIBE TABLE {table}")
        if not out.strip():
            return set()
        cols = set()
        for line in out.split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if not parts:
                continue
            name = parts[0]
            default_type = parts[2] if len(parts) > 2 else ""
            if default_type in ("MATERIALIZED", "ALIAS"):
                continue  # CH 禁止 INSERT MATERIALIZED/ALIAS 列
            cols.add(name)
        table_insertable_cols_cache[table] = cols
        return cols


def _get_insertable_columns_set(table: str) -> set[str]:
    """向后兼容 thin wrapper。"""
    return get_insertable_columns_set(table)


# 表引擎缓存（避免每次都查 system.tables）
table_engine_cache: dict[str, str] = {}
_table_engine_cache = table_engine_cache  # 向后兼容别名（R5 公共化）


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
    if table in table_engine_cache:
        return table_engine_cache[table]
    with _cache_lock:
        # double-check
        if table in table_engine_cache:
            return table_engine_cache[table]
        # table 形如 "c1_market.kline_daily"，拆成 database + name
        parts = table.split(".", 1)
        if len(parts) == 2:
            db, name = parts
            sql = SQL_ENGINE_BY_DB.format(db, name)
        else:
            sql = SQL_ENGINE_BY_NAME.format(table)
        out = query(sql)
        engine = out.strip()
        table_engine_cache[table] = engine
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
    create_fallback: bool = True,
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
    _t0 = time.time()
    if not tsv_bytes:
        log.warning("write_tsv(%s): 空数据，跳过", table)
        _record_write_outcome(WriteDisposition.NOT_DURABLE, time.time() - _t0)
        return WriteOutcome(WriteDisposition.NOT_DURABLE, "empty payload")
    cols_clause = columns if columns else get_insert_columns(table)
    sql = SQL_INSERT_TSV.format(table=table, cols_clause=cols_clause)

    # 策略1: HTTP API（主路径）
    if http_insert(sql, tsv_bytes, timeout=timeout):
        _record_write_outcome(WriteDisposition.CH_COMMITTED, time.time() - _t0)
        return WriteOutcome(WriteDisposition.CH_COMMITTED, "http")
    if not create_fallback:
        log.warning("write_tsv(%s): HTTP API 失败，跳过本地落盘（replay 模式）", table)
        _record_write_outcome(WriteDisposition.NOT_DURABLE, time.time() - _t0)
        return WriteOutcome(WriteDisposition.NOT_DURABLE, "http_failed_no_fallback")
    log.warning("write_tsv(%s): HTTP API 失败，降级到本地落盘", table)

    # 策略2: 本地落盘兜底（裁定 #ARCH-CH-013，CH 不可达时数据不丢失）
    # 数据写入本地 TSV 文件，待 CH 恢复后自动回灌
    from zephyr.data.local_replay import save_fallback

    # cols_clause 为 "*" 或 "" 意味着 get_insert_columns 在 CH 不可用时返回的
    # 未校验值。"*" 生成非法 SQL（已废弃），"" 生成无列子句 SQL（CH 按全列插入）。
    # 两者都意味着 TSV 列数可能与表列数不匹配；存 None 让回灌时重新查询表列。
    # 注意：调用方（BufferedWriter/write_result）应在 DESCRIBE 失败时用
    # result.columns 构造显式列子句，避免走到此 None 分支（裁定 #ARCH-CH-013）。
    fallback_cols = None if cols_clause in ("*", "") else cols_clause
    if save_fallback(table, fallback_cols, tsv_bytes):
        _record_write_outcome(WriteDisposition.LOCAL_DURABLE, time.time() - _t0)
        return WriteOutcome(WriteDisposition.LOCAL_DURABLE, "local_fallback")
    _record_write_outcome(WriteDisposition.NOT_DURABLE, time.time() - _t0)
    return WriteOutcome(WriteDisposition.NOT_DURABLE, "local_fallback_failed")


def write_tsv(
    table: str,
    columns: str | None,
    tsv_bytes: bytes,
    timeout: int = _DEFAULT_TIMEOUT,
    create_fallback: bool = True,
) -> bool:
    """兼容旧调用方：仅 ClickHouse 已提交才返回 ``True``。

    新调用方必须使用 :func:`write_tsv_outcome`，以区别本地持久化和入库成功。
    """
    return write_tsv_outcome(table, columns, tsv_bytes, timeout, create_fallback).is_ch_committed


def write_result(
    result: FetchResult,
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
    eff_cols = None  # 与 rows 列序对齐的列名列表（无则 None）
    if columns:
        # 显式指定的列，直接用
        cols_clause = columns
        rows = result.rows
        # 列名优先取 result.columns（与 rows 同序），否则解析 columns 串
        if result.columns and result.rows and len(result.columns) == len(result.rows[0]):
            eff_cols = list(result.columns)
        else:
            eff_cols = _parse_cols_clause(columns)
    elif result.columns:
        # 自动列过滤：只插入表中可插入的列（排除 MATERIALIZED/ALIAS）
        # #ARCH-CH-MATERIALIZED-INSERT：原用 get_table_columns_set 含 MATERIALIZED 列，
        # 导致 exchange/symbol_canonical 等被保留进 cols_clause，INSERT 报 Code 44
        table_cols = get_insertable_columns_set(result.table)
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
                    result.table,
                    len(result.columns),
                    len(common_cols),
                    len(result.columns) - len(common_cols),
                )
            else:
                rows = result.rows
            cols_clause = "(" + ", ".join(common_cols) + ")"
            eff_cols = common_cols
        else:
            # CH 不可用（DESCRIBE 失败）：用 result.columns 构造显式列子句，
            # 确保 TSV 字段数 = cols_clause 列数（2026-08-09 修复）。
            # 原设计存 None 让回灌重新查询表列，但 get_insert_columns 返回全部
            # 可插入列（含 DEFAULT），TSV 字段数 < 表列数 → Code 27 列数不匹配。
            # 所有 provider 已使用真实列名，用 result.columns 保证列数匹配；
            # 列名有误时 INSERT fail-fast（Code 47），优于静默列数不匹配。
            if result.columns and result.rows and len(result.columns) == len(result.rows[0]):
                cols_clause = "(" + ", ".join(result.columns) + ")"
            else:
                cols_clause = None  # 无列信息，落盘 None 让回灌时重新查询
            rows = result.rows
            eff_cols = list(result.columns) if result.columns else None
    else:
        cols_clause = None  # write_tsv 内部自动查询
        rows = result.rows

    # #ARCH-CH-021 P0-4: 写入前质量门禁（四门禁，异常行置 quality_flag=0）
    if eff_cols and rows:
        try:
            from zephyr.data.quality_gate import apply_quality_gate

            rows, qstats = apply_quality_gate(result.table, eff_cols, rows)
            if qstats["flagged"]:
                log.warning(
                    "write_result(%s): quality_gate flagged %d/%d rows (ohlc=%d change=%d swing=%d adj=%d)",
                    result.table,
                    qstats["flagged"],
                    qstats["checked"],
                    qstats["by_gate"]["ohlc"],
                    qstats["by_gate"]["change"],
                    qstats["by_gate"]["swing"],
                    qstats["by_gate"]["adj"],
                )
        except Exception as e:  # noqa: BLE001 — 质量门禁失败不得阻断写入
            log.warning("write_result(%s): quality_gate 跳过（%s）", result.table, e)

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
    client = get_client()
    if client is not None:
        try:
            with _ch_lock:  # 串行化 execute（clickhouse-driver Client 非线程安全）
                client.execute(sql, settings={"max_execution_time": timeout})
            return True
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("clickhouse-driver delete 失败，降级到 HTTP: %s", e)
            _invalidate_tcp_client(f"delete execute 失败: {e}")
    # 策略2: HTTP API
    http_host = get_http_host()
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    global _tcp_fail_ts, ch_client, ch_http_host, _http_fail_ts
    old_tcp_ts = _tcp_fail_ts
    old_client = ch_client
    _tcp_fail_ts = 0
    ch_client = None
    try:
        c = get_client()
        if c is not None:
            c.execute("SELECT 1")
            result["tcp"] = "ok"
        else:
            result["tcp"] = "fail"
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        result["tcp"] = "fail"
    finally:
        # 恢复原状态（不污染全局单例）
        _tcp_fail_ts = old_tcp_ts
        ch_client = old_client

    # HTTP 探测（重置冷却期强制测试）
    old_http_ts = _http_fail_ts
    old_http_host = ch_http_host
    _http_fail_ts = 0
    ch_http_host = None
    host = get_http_host()
    result["http_host"] = host or ""
    if host:
        try:
            conn = http.client.HTTPConnection(host, _CH_HTTP_PORT, timeout=5)
            conn.request("GET", "/ping")
            resp = conn.getresponse()
            result["http"] = "ok" if resp.status == 200 else f"status:{resp.status}"
            conn.close()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            result["http"] = f"fail:{type(e).__name__}"
    else:
        result["http"] = "fail"
    # 恢复原状态
    _http_fail_ts = old_http_ts
    ch_http_host = old_http_host

    return result
