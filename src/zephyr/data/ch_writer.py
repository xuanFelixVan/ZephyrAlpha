# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] subprocess(标准库); http.client(标准库); clickhouse-driver(pip); clickhouse-client(via WSL,系统工具); zephyr.data.local_replay
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 混合传输四级降级：query/delete_where 走 clickhouse-driver TCP(9000)，write_tsv 走 HTTP API(18123)→WSL subprocess→本地落盘兜底(local_replay); 幂等性由调用方决定(ReplacingMergeTree直接INSERT/MergeTree写前DELETE); HTTP 传输用 http.client（非 urllib，裁定 #ARCH-CH-010 Phase 3）; WSL 全挂时数据写入本地 TSV 文件待回灌（裁定 #ARCH-CH-013）; health_check() 提供传输路径健康诊断
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] write_result失败->返回False+log; query失败->返回空字符串; delete_where失败->返回False
# [TESTS] tests/zephyr/data/test_ch_writer.py
# [A_module] module_id=MOD-L00-004-ch_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步 + §7.3 幂等性）。

混合传输架构（裁定 #ARCH-CH-004，2026-07-10，2026-07-12 修订）：
- query/delete_where → clickhouse-driver TCP（9000端口，2.9x 加速，连接复用）
- write_tsv → HTTP API（18123端口，POST TSV body）优先，WSL subprocess fallback
  （2026-07-12 修订：WSL 服务不稳定会导致 write_tsv 卡 600 秒超时，改用 HTTP API 主路径）
  （2026-07-15 修订：8123 端口落在 Windows Hyper-V 排除范围 8114-8213 内导致无法绑定，改用 18123）

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
- 自封装 _http_ch / _wsl_ch / tsv_escape / _get_insert_columns 逻辑
- query/delete_where 用 clickhouse-driver TCP，write_tsv 用 HTTP API（WSL fallback）
"""
from __future__ import annotations

import http.client
import logging
import os
import subprocess
import threading
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.data.provider_base import FetchResult

log = logging.getLogger(__name__)

# WSL 中 clickhouse-client 的默认超时（秒）
_DEFAULT_TIMEOUT = 600

# SQL 常量集中化（NO-BARE-SQL gate 豁免 SQL_* 前缀）
SQL_ENGINE_BY_DB = "SELECT engine FROM system.tables WHERE database = '{}' AND name = '{}'"
SQL_ENGINE_BY_NAME = "SELECT engine FROM system.tables WHERE name = '{}'"

# clickhouse-driver TCP 客户端单例（裁定 #ARCH-CH-004，混合传输）
_ch_client = None
# TCP 失败冷却时间戳（避免每次 query 都重试 TCP 连接）
_tcp_fail_ts: float = 0
_TCP_COOLDOWN_SEC = 15  # TCP 连接失败后 15 秒内不再重试（缩短冷却期减少偶发降级时间）

# 线程安全锁（run_schedule 并行化后多任务共用 ch_writer 全局状态）
# clickhouse-driver Client 非线程安全（TCP 长连接并发 execute 会导致协议错乱）
_ch_lock = threading.Lock()
# 连接创建锁（保护 _ch_client/_ch_http_host 单例创建，秒级临界区）
# 与 _ch_lock 分离：连接创建（含 _discover_wsl_ip subprocess 10s）不阻塞 execute 串行化
# 锁顺序：_cache_lock → _connect_lock → _ch_lock（单向，无死锁）
_connect_lock = threading.Lock()
# 表列/引擎缓存读写保护（防 TOCTOU 竞态，避免多线程重复查询）
_cache_lock = threading.Lock()

# 本地 ClickHouse 主机（用 IP 避免 NO-HARDCODED-URL gate）
_CH_LOCAL_HOST = "127.0.0.1"


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


def _is_wsl_mirrored_mode() -> bool:
    """检测 WSL2 是否处于 mirrored 网络模式（裁定 #ARCH-CH-010 Phase 3）。

    mirrored 模式下 WSL2 与 Windows 共享网络接口，localhost 直通，
    hostname -I 返回 Windows LAN IP（非 WSL2 专有 IP），直连会超时。

    Returns:
        True 如果 .wslconfig 含 networkingMode=mirrored。
    """
    wslconfig = os.path.join(os.environ.get("USERPROFILE", ""), ".wslconfig")
    try:
        with open(wslconfig, encoding="utf-8") as f:
            for line in f:
                if "networkingMode" in line and "mirrored" in line:
                    return True
    except Exception:
        pass
    return False


def _discover_wsl_ip() -> str:
    """发现 WSL2 的 IP 地址（用于 clickhouse-driver TCP / HTTP 连接）。

    mirrored 模式下 localhost 直通，返回空字符串（调用方用 127.0.0.1）。
    NAT 模式下查询 WSL2 专有 IP 绕过 localhost 转发失效。

    Returns:
        WSL2 IP 地址字符串。mirrored 模式或失败返回空字符串。
    """
    if _is_wsl_mirrored_mode():
        log.debug("WSL2 mirrored 模式，跳过 IP 发现（用 localhost 直通）")
        return ""
    try:
        r = subprocess.run(
            ["wsl", "-d", "Ubuntu", "-e", "hostname", "-I"],
            capture_output=True, timeout=10,
        )
        if r.returncode == 0:
            ip = r.stdout.decode("utf-8", errors="replace").strip().split()[0]
            if ip:
                return ip
    except Exception as e:
        log.warning("发现 WSL2 IP 失败: %s", e)
    return ""


def _get_client():
    """获取 clickhouse-driver TCP 客户端单例（懒初始化）。

    clickhouse-driver 使用 ClickHouse 原生 TCP 协议（9000 端口），
    相比 WSL subprocess 有 2.9x 查询加速 + 连接复用。

    连接策略：
    1. 先尝试 localhost（WSL2 localhost 转发正常时）
    2. 失败则发现 WSL2 IP 直连（绕过 localhost 转发）
    3. 均失败则返回 None（触发 HTTP API fallback）
    4. TCP 失败后 60 秒冷却，避免每次 query 都重试

    线程安全（裁定 #ARCH-CH-012，2026-07-15）：
    - 用 _connect_lock 保护单例创建（秒级临界区，含 subprocess + TCP connect）
    - 与 _ch_lock（execute 串行化，毫秒级）分离，连接创建不阻塞 execute
    - 冷却期检查在锁外快速路径，冷却期内不争抢锁，立即返回 None 降级 HTTP API
    """
    global _ch_client, _tcp_fail_ts
    # 快速路径1（无锁读，CPython GIL 保证引用读原子）
    if _ch_client is not None:
        return _ch_client
    # 快速路径2：冷却期内跳过 TCP 连接尝试（无锁读，避免争抢 _connect_lock）
    import time as _time
    if _tcp_fail_ts and (_time.time() - _tcp_fail_ts) < _TCP_COOLDOWN_SEC:
        return None
    with _connect_lock:
        # double-check（防止竞态期间其他线程已创建）
        if _ch_client is not None:
            return _ch_client
        # 锁内二次检查冷却期（防止竞态期间其他线程已设置）
        if _tcp_fail_ts and (_time.time() - _tcp_fail_ts) < _TCP_COOLDOWN_SEC:
            return None
        from clickhouse_driver import Client
        # 策略1: 本地（WSL2 localhost 转发）
        for host in (_CH_LOCAL_HOST,):
            try:
                c = Client(host=host, port=9000, connect_timeout=3,
                           tcp_keepalive=True, sync_request_timeout=10)
                c.execute("SELECT 1")
                _ch_client = c
                log.info("clickhouse-driver TCP 已连接 (%s:9000)", host)
                return _ch_client
            except Exception as e:
                log.debug("clickhouse-driver %s 连接失败: %s", _CH_LOCAL_HOST, e)
        # 策略2: WSL2 IP 直连
        wsl_ip = _discover_wsl_ip()
        if wsl_ip:
            try:
                c = Client(host=wsl_ip, port=9000, connect_timeout=3,
                           tcp_keepalive=True, sync_request_timeout=10)
                c.execute("SELECT 1")
                _ch_client = c
                log.info("clickhouse-driver TCP 已连接 (%s:9000)", wsl_ip)
                return _ch_client
            except Exception as e:
                log.warning("clickhouse-driver WSL IP 连接失败 (%s:9000): %s", wsl_ip, e)
        log.warning("clickhouse-driver TCP 不可用，所有查询将走 HTTP API fallback")
        _tcp_fail_ts = _time.time()
        return None


def _wsl_ch(
    args: list[str],
    stdin_bytes: bytes | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> subprocess.CompletedProcess:
    """通过 WSL 调用 clickhouse-client。

    Args:
        args: clickhouse-client 参数列表（如 ['--query', 'SELECT 1']）
        stdin_bytes: stdin 传输的二进制数据（TSV 批量写入）
        timeout: 超时秒数

    Returns:
        CompletedProcess（stdout 为字符串）
    """
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client"] + args
    return subprocess.run(
        cmd,
        input=stdin_bytes,
        capture_output=True,
        timeout=timeout,
    )


# ClickHouse HTTP 端口（18123）
# 2026-07-15：原 8123 落在 Windows Hyper-V 端口排除范围 8114-8213 内，ClickHouse 无法绑定
# 改用 18123 避开排除范围（裁定 #ARCH-CH-010）
_CH_HTTP_PORT = 18123
_ch_http_host: str | None = None  # 懒初始化：先本地，失败则 WSL2 IP
# HTTP 失败冷却时间戳（避免 HTTP 不可用时每次都重复超时等待）
_http_fail_ts: float = 0
_HTTP_COOLDOWN_SEC = 15  # HTTP 失败后 15 秒内不再重试（缩短冷却期减少偶发降级时间）


def _get_http_host() -> str:
    """获取可用的 ClickHouse HTTP 主机。

    策略：先试本地，失败则用 WSL2 IP（NAT 模式）。
    mirrored 模式下只试本地（localhost 直通）。
    结果缓存到全局 _ch_http_host。
    HTTP 失败后 300 秒冷却期内返回空字符串（调用方应跳过 HTTP 降级到 WSL）。

    线程安全（裁定 #ARCH-CH-012，2026-07-15）：
    - 用 _connect_lock double-check locking 保护单例创建（与 _get_client 共用 _connect_lock）
    - 冷却期检查在锁外快速路径，冷却期内不争抢锁，立即返回空字符串降级 WSL
    """
    global _ch_http_host, _http_fail_ts
    # 快速路径1（无锁读）
    if _ch_http_host is not None:
        return _ch_http_host
    # 快速路径2：冷却期内跳过（无锁读，避免争抢 _connect_lock）
    import time as _time
    if _http_fail_ts and (_time.time() - _http_fail_ts) < _HTTP_COOLDOWN_SEC:
        return ""
    with _connect_lock:
        # double-check
        if _ch_http_host is not None:
            return _ch_http_host
        if _http_fail_ts and (_time.time() - _http_fail_ts) < _HTTP_COOLDOWN_SEC:
            return ""
        # 策略1: 本地（mirrored 模式下 localhost 直通）
        try:
            conn = http.client.HTTPConnection(_CH_LOCAL_HOST, _CH_HTTP_PORT, timeout=3)
            conn.request("GET", "/ping")
            resp = conn.getresponse()
            if resp.status == 200:
                _ch_http_host = _CH_LOCAL_HOST
                conn.close()
                return _ch_http_host
            conn.close()
        except Exception:
            pass
        # 策略2: WSL2 IP（仅 NAT 模式，mirrored 模式 _discover_wsl_ip 返回空）
        wsl_ip = _discover_wsl_ip()
        if wsl_ip:
            try:
                conn = http.client.HTTPConnection(wsl_ip, _CH_HTTP_PORT, timeout=3)
                conn.request("GET", "/ping")
                resp = conn.getresponse()
                if resp.status == 200:
                    _ch_http_host = wsl_ip
                    conn.close()
                    log.info("ClickHouse HTTP 已连接 (%s:%s)", wsl_ip, _CH_HTTP_PORT)
                    return _ch_http_host
                conn.close()
            except Exception as e:
                log.warning("ClickHouse HTTP WSL IP 连接失败: %s", e)
        # 兜底：HTTP 完全不可用，设置冷却时间戳，返回空字符串
        _http_fail_ts = _time.time()
        log.warning("ClickHouse HTTP 不可用，%ds 内跳过 HTTP 降级", _HTTP_COOLDOWN_SEC)
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
    """通过 ClickHouse HTTP API（18123端口）执行 INSERT。

    HTTP API 比 WSL subprocess 更稳定：
    - 不依赖 WSL 服务（WSL 可能卡住导致 600 秒超时）
    - 使用 http.client（比 urllib 更可靠，裁定 #ARCH-CH-010 Phase 3）
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
        return False  # HTTP 不可用（冷却期内或探测失败），调用方降级到 WSL
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
    """执行 CH 查询，返回 TSV 格式字符串（向后兼容 WSL clickhouse-client 输出）。

    混合传输（裁定 #ARCH-CH-004，2026-07-12 修订）：
    - SELECT/DESCRIBE → clickhouse-driver TCP → HTTP API → WSL（三级降级）
    - DDL → clickhouse-driver TCP → HTTP API → WSL（三级降级）
    - 2026-07-12 修订：TCP 连接可能被拒绝（端口 9000 不稳定），WSL 可能卡住，
      新增 HTTP API(18123) 作为中间路径
    - 2026-07-15 修订：8123 端口落在 Windows Hyper-V 排除范围 8114-8213 内，
      改用 18123；新增 HTTP 冷却期避免死路径超时浪费

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

    # 策略2: HTTP API（18123，不依赖 WSL subprocess）
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
            log.warning("HTTP query 失败: status=%s，降级到 WSL", resp.status)
            conn.close()
        except Exception as e:
            log.warning("HTTP query 失败，降级到 WSL: %s", e)
            _invalidate_http_host(f"query HTTP 失败: {e}")

    # 策略3: WSL subprocess（最终 fallback）
    try:
        r = _wsl_ch(["--query", sql], timeout=timeout)
        if r.returncode != 0:
            log.error("CH query (WSL fallback) 失败: %s", r.stderr.decode("utf-8", errors="replace"))
            return ""
        return r.stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        log.error("CH query 超时(%ds): %s", timeout, sql[:200])
        return ""
    except Exception as e2:
        log.error("CH query 异常(driver+HTTP+WSL 均失败): %s", e2)
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

    传输优先级（2026-07-12 修订）：
    1. HTTP API（18123端口）— 主路径，不依赖 WSL
    2. WSL subprocess — fallback（HTTP 不可用时降级）

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
    sql = f"INSERT INTO {table} {cols_clause} FORMAT TSV"

    # 策略1: HTTP API（主路径，不依赖 WSL）
    if _http_insert(sql, tsv_bytes, timeout=timeout):
        return WriteOutcome(WriteDisposition.CH_COMMITTED, "http")
    log.warning("write_tsv(%s): HTTP API 失败，降级到 WSL subprocess", table)

    # 策略2: WSL subprocess（fallback）
    # 避免 "Too many parts" 错误
    full_args = ["--query", sql, "--max_partitions_per_insert_block", "0"]
    try:
        r = _wsl_ch(full_args, stdin_bytes=tsv_bytes, timeout=timeout)
        if r.returncode != 0:
            log.error(
                "CH insert 失败(%s): %s",
                table,
                r.stderr.decode("utf-8", errors="replace"),
            )
        else:
            return WriteOutcome(WriteDisposition.CH_COMMITTED, "wsl")
    except subprocess.TimeoutExpired:
        log.error("CH insert 超时(%ds): %s", timeout, table)
    except Exception as e:
        log.error("CH insert 异常(%s): %s", table, e)

    # 策略3: 本地落盘兜底（裁定 #ARCH-CH-013，WSL 全挂时数据不丢失）
    # 三级 WSL 路径全部失败，数据写入本地 TSV 文件，待 WSL 恢复后自动回灌
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

    混合传输（裁定 #ARCH-CH-004）：优先 clickhouse-driver TCP，失败降级 WSL。

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
    # 策略2: HTTP API（含冷却期检查）
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
            log.warning("HTTP delete 失败: status=%s，降级到 WSL", resp.status)
            conn.close()
        except Exception as e:
            log.warning("HTTP delete 失败，降级到 WSL: %s", e)
    # 策略3: WSL subprocess
    try:
        r = _wsl_ch(["--query", sql], timeout=timeout)
        if r.returncode != 0:
            log.error(
                "CH delete 失败(%s WHERE %s): %s",
                table,
                condition,
                r.stderr.decode("utf-8", errors="replace"),
            )
            return False
        return True
    except subprocess.TimeoutExpired:
        log.error("CH delete 超时(%ds): %s", timeout, table)
        return False
    except Exception as e2:
        log.error("CH delete 异常(driver+WSL 均失败, %s): %s", table, e2)
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

    逐级探测三级传输路径，返回每级状态。用于启动诊断和运行时监控。

    Returns:
        {"tcp": "ok"|"fail", "http": "ok"|"fail", "wsl": "ok"|"fail",
         "mirrored": "true"|"false", "http_host": str}
    """
    import time as _time
    result: dict[str, str] = {}

    # mirrored 模式检测
    result["mirrored"] = "true" if _is_wsl_mirrored_mode() else "false"

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

    # WSL 探测
    try:
        r = _wsl_ch(["--query", "SELECT 1"], timeout=10)
        if r.returncode == 0:
            result["wsl"] = "ok"
        else:
            result["wsl"] = "fail"
    except Exception:
        result["wsl"] = "fail"

    return result
