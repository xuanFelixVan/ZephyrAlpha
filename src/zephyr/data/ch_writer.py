# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] subprocess(标准库); clickhouse-client(via WSL,系统工具)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 通过 WSL subprocess 调用 clickhouse-client; TSV 格式批量写入; 不依赖 tmp/_ds_common.py(自封装); 幂等性由调用方决定(ReplacingMergeTree直接INSERT/MergeTree写前DELETE)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] write_result失败→返回False+log; _wsl_ch超时→subprocess.TimeoutExpired; 查询失败→返回空字符串
# [TESTS] tests/zephyr/data/test_ch_writer.py
# [A_module] module_id=MOD-L00-004-ch_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步 + §7.3 幂等性）。

封装 WSL clickhouse-client 调用，提供：
- write_result(result): 把 FetchResult.rows 转 TSV 写入 CH
- tsv_escape(v): 转义字段值（None/NaN → \\N，字符串去换行制表符）
- delete_where(table, condition): 写前删除（MergeTree 幂等性）
- query(sql): 查询 CH（用于 DESCRIBE TABLE 获取列清单）

幂等性策略（§7.3）：
- ReplacingMergeTree → 直接 INSERT（重复键由 CH 后台合并）
- MergeTree → 写前 DELETE WHERE date = today()
- 临时表 → staging + INSERT SELECT DISTINCT（阶段3+ 实现）

设计要点：
- 不依赖 tmp/_ds_common.py（TTL=task_bound，src/ 不能长期依赖 tmp/）
- 自封装 _wsl_ch / tsv_escape / _get_insert_columns 逻辑
- subprocess 调用 clickhouse-client，不依赖 Python clickhouse-driver 包
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
    """执行 CH 查询，返回 stdout 字符串。

    失败时 log 错误并返回空字符串（不抛异常）。
    """
    try:
        r = _wsl_ch(["--query", sql], timeout=timeout)
        if r.returncode != 0:
            log.error("CH query 失败: %s", r.stderr.decode("utf-8", errors="replace"))
            return ""
        return r.stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        log.error("CH query 超时(%ds): %s", timeout, sql[:200])
        return ""
    except Exception as e:
        log.error("CH query 异常: %s", e)
        return ""


def tsv_escape(v) -> str:
    """转义字段值用于 TSV。

    - None / NaN → ``\\N``
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

    # 构造 TSV 字节
    tsv_lines = []
    for row in result.rows:
        tsv_lines.append("\t".join(tsv_escape(v) for v in row))
    tsv_bytes = "\n".join(tsv_lines).encode("utf-8")

    # 构造列子句
    if columns:
        cols_clause = columns
    elif result.columns:
        cols_clause = "(" + ", ".join(result.columns) + ")"
    else:
        cols_clause = None  # write_tsv 内部自动查询

    return write_tsv(result.table, cols_clause, tsv_bytes, timeout=timeout)


def delete_where(
    table: str,
    condition: str,
    timeout: int = _DEFAULT_TIMEOUT,
) -> bool:
    """删除满足条件的行（用于 MergeTree 幂等性：写前 DELETE）。

    Args:
        table: 表名
        condition: WHERE 条件（如 "date = '2026-07-05'"）
        timeout: 超时秒数

    Returns:
        是否成功。
    """
    sql = f"ALTER TABLE {table} DELETE WHERE {condition}"
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
    except Exception as e:
        log.error("CH delete 异常(%s): %s", table, e)
        return False
