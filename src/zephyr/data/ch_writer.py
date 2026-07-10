# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] subprocess(标准库); clickhouse-driver(pip); clickhouse-client(via WSL,系统工具)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 混合传输：query/delete_where 走 clickhouse-driver TCP(9000)，write_tsv 走 WSL subprocess TSV(TSV 自动处理类型转换); 幂等性由调用方决定(ReplacingMergeTree直接INSERT/MergeTree写前DELETE)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] write_result失败->返回False+log; query失败->返回空字符串; delete_where失败->返回False
# [TESTS] tests/zephyr/data/test_ch_writer.py
# [A_module] module_id=MOD-L00-004-ch_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步 + §7.3 幂等性）。

混合传输架构（裁定 #ARCH-CH-004，2026-07-10）：
- query/delete_where → clickhouse-driver TCP（9000端口，2.9x 加速，连接复用）
- write_tsv → WSL subprocess TSV（TSV 自动处理类型转换，Provider 返回字符串日期无需转换）

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
- 自封装 _wsl_ch / tsv_escape / _get_insert_columns 逻辑
- query/delete_where 用 clickhouse-driver TCP，write_tsv 用 WSL subprocess（混合传输）
"""
from __future__ import annotations

import logging
import subprocess
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


def _discover_wsl_ip() -> str:
    """发现 WSL2 的 IP 地址（用于 clickhouse-driver TCP 连接）。

    WSL2 的 localhost 转发可能失效（Windows 服务问题），
    需要直接查询 WSL2 IP 建立连接。

    Returns:
        WSL2 IP 地址字符串。失败返回空字符串。
    """
    try:
        r = subprocess.run(
            ["wsl", "-d", "Ubuntu", "-e", "hostname", "-I"],
            capture_output=True, timeout=5,
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
    3. 均失败则返回 None（触发 WSL subprocess fallback）
    """
    global _ch_client
    if _ch_client is not None:
        return _ch_client
    from clickhouse_driver import Client
    # 策略1: localhost（WSL2 localhost 转发）
    for host in ("localhost",):
        try:
            c = Client(host=host, port=9000, connect_timeout=3)
            c.execute("SELECT 1")
            _ch_client = c
            log.info("clickhouse-driver TCP 已连接 (%s:9000)", host)
            return _ch_client
        except Exception as e:
            log.debug("clickhouse-driver localhost 连接失败: %s", e)
    # 策略2: WSL2 IP 直连
    wsl_ip = _discover_wsl_ip()
    if wsl_ip:
        try:
            c = Client(host=wsl_ip, port=9000, connect_timeout=3)
            c.execute("SELECT 1")
            _ch_client = c
            log.info("clickhouse-driver TCP 已连接 (%s:9000)", wsl_ip)
            return _ch_client
        except Exception as e:
            log.warning("clickhouse-driver WSL IP 连接失败 (%s:9000): %s", wsl_ip, e)
    log.warning("clickhouse-driver TCP 不可用，所有查询将走 WSL subprocess fallback")
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


def query(sql: str, timeout: int = _DEFAULT_TIMEOUT) -> str:
    """执行 CH 查询，返回 TSV 格式字符串（向后兼容 WSL clickhouse-client 输出）。

    混合传输（裁定 #ARCH-CH-004）：
    - SELECT → clickhouse-driver TCP，结果格式化为 TSV 返回
    - DDL（TRUNCATE/ALTER/CREATE 等）→ clickhouse-driver TCP，返回空字符串
    - clickhouse-driver 不可用时降级到 WSL subprocess（fallback）

    失败时 log 错误并返回空字符串（不抛异常）。
    """
    # 尝试 clickhouse-driver TCP
    client = _get_client()
    if client is not None:
        try:
            sql_stripped = sql.strip()
            # SELECT 查询：返回 TSV 格式
            if sql_stripped.upper().startswith("SELECT") or sql_stripped.upper().startswith("DESCRIBE"):
                rows = client.execute(sql, settings={"max_execution_time": timeout})
                if not rows:
                    return ""
                lines = []
                for row in rows:
                    lines.append("\t".join(str(v) for v in row))
                return "\n".join(lines) + "\n"
            else:
                # DDL 语句
                client.execute(sql, settings={"max_execution_time": timeout})
                return ""
        except Exception as e:
            log.warning("clickhouse-driver query 失败，降级到 WSL: %s", e)
    # 降级到 WSL subprocess
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
        log.error("CH query 异常(driver+WSL 均失败): %s", e2)
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

    Returns:
        列名集合。查询失败返回空集合。
    """
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

    Returns:
        引擎名字符串。查询失败返回空字符串。
    """
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


def write_tsv(
    table: str,
    columns: str | None,
    tsv_bytes: bytes,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """TSV 批量写入表。

    Args:
        table: 完整表名（如 c1_market.kline_daily）
        columns: "(col1, col2, ...)" 字符串，None 时自动查询列清单
        tsv_bytes: TSV 格式字节数据
        timeout: 超时秒数

    Returns:
        是否成功。
    """
    if not tsv_bytes:
        log.warning("write_tsv(%s): 空数据，跳过", table)
        return False
    cols_clause = columns if columns else _get_insert_columns(table)
    sql = f"INSERT INTO {table} {cols_clause} FORMAT TSV"
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
            return False
        return True
    except subprocess.TimeoutExpired:
        log.error("CH insert 超时(%ds): %s", timeout, table)
        return False
    except Exception as e:
        log.error("CH insert 异常(%s): %s", table, e)
        return False


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
            # 查询失败，用 result.columns 原样
            cols_clause = "(" + ", ".join(result.columns) + ")"
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
    # 尝试 clickhouse-driver TCP
    client = _get_client()
    if client is not None:
        try:
            client.execute(sql, settings={"max_execution_time": timeout})
            return True
        except Exception as e:
            log.warning("clickhouse-driver delete 失败，降级到 WSL: %s", e)
    # 降级到 WSL subprocess
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
