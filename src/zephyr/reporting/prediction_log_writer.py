# [BLUEPRINT] MOD-RPT-028 | 待统筹登记（92号清单 §7.13 M4-② prediction_log 统一落库）
# [MODULE] zephyr.reporting.prediction_log_writer
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.io.paths(DB_PATH SSoT); zephyr.shared.io.sqlite_factory(get_db_connection); zephyr.shared.io.serialization(dumps canonical)
# [CONSUMERS] 波5 各生产模块（M1 情绪分/M2 边界修正事件/M3 三情景/LLM 盘前分析——44号 §12.1 M4-② 四族）; 92号 §8.7 M4-④ 命中率统计器（规划）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] append-only 仅 INSERT（同键重复=跳过保首条不覆写）; SQL 参数化+常量（NO-BARE-SQL）; db_path 默认 None 走 DB_PATH SSoT（测试注入临时库，trend_analyzer db_path 同款隔离先例）; 输入校验 fail-closed; input_hash 缺省=canonical payload SHA-256（内容寻址，幂等键恒有效）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（输入非法 fail-closed）; sqlite3.Error 透传
# [TESTS] tests/reporting/test_prediction_log_writer.py
# [A_module] module_id=MOD-RPT-028 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
prediction_log_writer — 每日预测类输出统一落库写入器（92号 §7.13 M4-②）

设计真源：44号备忘 §12.1 M4-②（"每天预测了什么"可回查可验证）+
92号清单 §7.13（governance.db 新表 prediction_log，D2 授权 DB 写；
对齐 reconciliation_differences 落治理库先例，见 trading/recon_runner.py）。
机构对标：TradingAgents decision log（持久化决策日志）/ 对冲基金 research journal。

幂等语义（写清）
--------------
唯一键 UNIQUE(trade_date, module, prediction_type, input_hash)：
**同键重复写=跳过（INSERT OR IGNORE），保留首条**，返回已存在行 id——
预测日志是审计载体，"当天预测了什么"以首写为准；重跑同输入（同 input_hash）
不覆写历史，修正性重跑因输入变化自然产生新键新行（与仓 append-only 文化一致）。
input_hash 缺省时自动取 canonical payload 的 SHA-256（内容寻址）——调用方不传
幂等键也恒有效；显式传入（如 44号 §9.14 七族输入 hash）优先。
SQLite UNIQUE 中 NULL 互不冲突，故 input_hash 入库前 None 归一为 ''。

落库
----
生产表已由 92号 §7.13 工单对 governance.db（DB_PATH SSoT）执行建表；
新环境/测试库走 ``ensure_prediction_log_table(db_path)`` 幂等建表
（CREATE TABLE IF NOT EXISTS，DDL 常量即本模块真源，禁止测试侧复刻副本）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: db_path 参数
#   fields: 参数 db_path，类型注解 str | Path | None
#   code: prediction_log_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: trade_date 参数
#   fields: 参数 trade_date，类型注解 str
#   code: prediction_log_writer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: module 参数
#   fields: 参数 module，类型注解 str
#   code: prediction_log_writer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: prediction_type 参数
#   fields: 参数 prediction_type，类型注解 str
#   code: prediction_log_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ensure_prediction_log_table
#   name_en: ensure_prediction_log_table
#   intro: 幂等建表（CREATE TABLE IF NOT EXISTS + 两索引）。
#   desc: 幂等建表（CREATE TABLE IF NOT EXISTS + 两索引）。 Args: db_path: 库路径；None=DB_PATH SSoT（governance.d…；源码 L242-L260
#   inputs: db_path
#   outputs: Path
# - id: A2
#   name_zh: ② log_prediction
#   name_en: log_prediction
#   intro: 写一条预测记录到 prediction_log（幂等：同键重复写=跳过保首条）。
#   desc: 写一条预测记录到 prediction_log（幂等：同键重复写=跳过保首条）。 Args: trade_date: 交易日 "YYYY-MM-DD"（非法即拒）。 module…；源码 L263-L321
#   inputs: trade_date module prediction_type payload asof_ts model_version promp…
#   outputs: int
# - id: A3
#   name_zh: ③ query_predictions
#   name_en: query_predictions
#   intro: 查询预测记录（过滤器可组合，按 trade_date/id 倒序）。
#   desc: 查询预测记录（过滤器可组合，按 trade_date/id 倒序）。 Args: trade_date: 交易日过滤（None=不限；给定则须合法 YYYY-MM-DD）。 mo…；源码 L324-L372
#   inputs: trade_date module prediction_type limit db_path
#   outputs: list[dict]
# 层: 输出
# - id: O1
#   name_zh: Path
#   name_en: Path
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 波5 各生产模块（M1 情绪分/M2 边界修正事件/M3 三情景/LLM 盘前分析——44号 §12.1 M4-② 四族）; 92号 §8.7 M4-④ 命中…
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 波5 各生产模块（M1 情绪分/M2 边界修正事件/M3 三情景/LLM 盘前分析——44号 §12.1 M4-② 四族）; 92号 §8.7 M4-④ 命中…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Final

from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.serialization import dumps as _canonical_dumps
from zephyr.shared.io.sqlite_factory import get_db_connection

__all__: Final = [
    "PREDICTION_LOG_DDL",
    "ensure_prediction_log_table",
    "log_prediction",
    "query_predictions",
]

# ── DDL-as-Code（92号 §7.13；本模块为 prediction_log schema 唯一真源）──
PREDICTION_LOG_DDL: Final = """
CREATE TABLE IF NOT EXISTS prediction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,               -- 交易日 YYYY-MM-DD
    module TEXT NOT NULL,                   -- 产出模块（如 signal_ashare.market_sentiment）
    prediction_type TEXT NOT NULL,          -- 预测类型（sentiment_score/boundary_revision/scenario_plan/llm_analysis/...）
    payload_json TEXT NOT NULL,             -- 预测载荷（canonical JSON，sort_keys 稳定序）
    asof_ts TEXT NOT NULL,                  -- 预测生效时点（ISO8601；PIT——该时点可见信息集）
    model_version TEXT,                     -- 模型版本（可空）
    prompt_version TEXT,                    -- prompt 版本（LLM 类预测用，可空）
    input_hash TEXT,                        -- 输入内容 hash（缺省=canonical payload SHA-256；NULL 归一 ''）
    created_at TEXT NOT NULL,               -- 落库时点 UTC ISO8601
    UNIQUE(trade_date, module, prediction_type, input_hash)
)
"""
_DDL_IDX_TRADE_DATE: Final = "CREATE INDEX IF NOT EXISTS idx_prediction_log_trade_date ON prediction_log (trade_date)"
_DDL_IDX_MODULE: Final = "CREATE INDEX IF NOT EXISTS idx_prediction_log_module ON prediction_log (module)"

# ── SQL 常量（NO-BARE-SQL 门禁；append-only 仅 INSERT，参数化防注入）──
_SQL_INSERT: Final = (
    "INSERT OR IGNORE INTO prediction_log "
    "(trade_date, module, prediction_type, payload_json, asof_ts, "
    "model_version, prompt_version, input_hash, created_at) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SQL_SELECT_ID_BY_KEY: Final = (
    "SELECT id FROM prediction_log WHERE trade_date=? AND module=? AND prediction_type=? AND input_hash=?"
)
_SQL_QUERY_BASE: Final = (
    "SELECT id, trade_date, module, prediction_type, payload_json, asof_ts, "
    "model_version, prompt_version, input_hash, created_at FROM prediction_log"
)
_SQL_WHERE_TRADE_DATE: Final = "trade_date = ?"
_SQL_WHERE_MODULE: Final = "module = ?"
_SQL_WHERE_PREDICTION_TYPE: Final = "prediction_type = ?"
_SQL_QUERY_TAIL: Final = "ORDER BY trade_date DESC, id DESC LIMIT ?"

_TRADE_DATE_RE: Final = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DEFAULT_QUERY_LIMIT: Final = 1000


def _strict_json_default(o: object) -> object:
    """严格 JSON 序列化校验的 default 钩子（fail-closed 用）。

    与 serialization canonical 规则同族放行 Decimal/datetime/date/Enum；
    其余未知类型抛 TypeError（拒收，防 str() 静默降级入审计载体）。
    """
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Enum):
        return o.value
    raise TypeError(f"非 JSON 可序列化类型: {type(o).__name__}")


def _serialize_payload(payload: object) -> str:
    """payload → canonical JSON（sort_keys 稳定序）；非可序列化 fail-closed 拒收。

    Raises:
        ValueError: payload 含非 JSON 可序列化字段。
    """
    try:
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=_strict_json_default)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"payload 非 JSON 可序列化（fail-closed 拒收）: {exc}") from exc
    return _canonical_dumps(payload, ensure_ascii=False, sort_keys=True)


def _validate_trade_date(trade_date: object) -> str:
    """交易日校验：必须 YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(trade_date, str) or not _TRADE_DATE_RE.match(trade_date):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
    try:
        date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    return trade_date


def _validate_non_empty_str(value: object, field: str) -> str:
    """非空字符串字段校验（module/prediction_type，fail-closed）。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} 非法（须非空字符串）: {value!r}")
    return value.strip()


def _validate_optional_str(value: object, field: str) -> str | None:
    """可空字符串字段校验（model_version/prompt_version/input_hash）。"""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} 非法（须 str 或 None）: {value!r}")
    return value


def _validate_asof_ts(asof_ts: object) -> str:
    """asof_ts 校验：None=补当前 UTC；给定则须可解析 ISO8601（fail-closed）。"""
    if asof_ts is None:
        return datetime.now(UTC).isoformat()
    if not isinstance(asof_ts, str) or not asof_ts.strip():
        raise ValueError(f"asof_ts 非法（须 ISO8601 字符串或 None）: {asof_ts!r}")
    try:
        datetime.fromisoformat(asof_ts)
    except ValueError as exc:
        raise ValueError(f"asof_ts 非 ISO8601: {asof_ts!r}") from exc
    return asof_ts


def _resolve_db_path(db_path: str | Path | None) -> Path:
    """db_path 解析：None=DB_PATH SSoT（测试注入临时库走显式参数）。"""
    return Path(db_path) if db_path is not None else DB_PATH


def ensure_prediction_log_table(db_path: str | Path | None = None) -> Path:
    """幂等建表（CREATE TABLE IF NOT EXISTS + 两索引）。

    Args:
        db_path: 库路径；None=DB_PATH SSoT（governance.db）。

    Returns:
        实际建表库路径。
    """
    resolved = _resolve_db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(resolved)
    try:
        conn.execute(PREDICTION_LOG_DDL)
        conn.execute(_DDL_IDX_TRADE_DATE)
        conn.execute(_DDL_IDX_MODULE)
    finally:
        conn.close()
    return resolved


def log_prediction(
    trade_date: str,
    module: str,
    prediction_type: str,
    payload: object,
    asof_ts: str | None = None,
    model_version: str | None = None,
    prompt_version: str | None = None,
    input_hash: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    """写一条预测记录到 prediction_log（幂等：同键重复写=跳过保首条）。

    Args:
        trade_date: 交易日 "YYYY-MM-DD"（非法即拒）。
        module: 产出模块标识（非空字符串）。
        prediction_type: 预测类型（非空字符串；如 sentiment_score/boundary_revision/
            scenario_plan/llm_analysis）。
        payload: 预测载荷（须 JSON 可序列化；Decimal/datetime/Enum 按 canonical
            规则放行，其余未知类型 fail-closed 拒收）。
        asof_ts: 预测生效时点 ISO8601；None=落库当前 UTC。
        model_version: 模型版本（可空）。
        prompt_version: prompt 版本（LLM 类预测用，可空）。
        input_hash: 输入内容 hash；None=自动取 canonical payload SHA-256
            （内容寻址，幂等键恒有效）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。

    Returns:
        行 id——新插入=新 id；同键重复=已存在行 id（首条保留不覆写）。

    Raises:
        ValueError: 任一输入非法（fail-closed）。
        sqlite3.Error: 库级异常透传（表缺失先调 ensure_prediction_log_table）。
    """
    v_date = _validate_trade_date(trade_date)
    v_module = _validate_non_empty_str(module, "module")
    v_type = _validate_non_empty_str(prediction_type, "prediction_type")
    payload_json = _serialize_payload(payload)
    v_asof = _validate_asof_ts(asof_ts)
    v_model = _validate_optional_str(model_version, "model_version")
    v_prompt = _validate_optional_str(prompt_version, "prompt_version")
    v_hash = _validate_optional_str(input_hash, "input_hash")
    if v_hash is None:
        v_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    created_at = datetime.now(UTC).isoformat()
    conn = get_db_connection(_resolve_db_path(db_path))
    try:
        cur = conn.execute(
            _SQL_INSERT,
            (v_date, v_module, v_type, payload_json, v_asof, v_model, v_prompt, v_hash, created_at),
        )
        if cur.rowcount == 1:
            return int(cur.lastrowid)
        # 同键重复：跳过保首条，返回已存在行 id（幂等语义见模块 docstring）
        row = conn.execute(_SQL_SELECT_ID_BY_KEY, (v_date, v_module, v_type, v_hash)).fetchone()
        return int(row["id"]) if row is not None else -1
    finally:
        conn.close()


def query_predictions(
    trade_date: str | None = None,
    module: str | None = None,
    prediction_type: str | None = None,
    limit: int = _DEFAULT_QUERY_LIMIT,
    db_path: str | Path | None = None,
) -> list[dict]:
    """查询预测记录（过滤器可组合，按 trade_date/id 倒序）。

    Args:
        trade_date: 交易日过滤（None=不限；给定则须合法 YYYY-MM-DD）。
        module: 模块过滤（None=不限；给定则须非空）。
        prediction_type: 类型过滤（None=不限；给定则须非空）。
        limit: 返回上限（须正整数）。
        db_path: 库路径；None=DB_PATH SSoT。

    Returns:
        行 dict 列表（payload_json 保持字符串，调用方自行 json.loads——
        落库契约保原文不回解析，防浮点/精度二次失真）。

    Raises:
        ValueError: 过滤器非法（fail-closed）。
    """
    where: list[str] = []
    params: list[object] = []
    if trade_date is not None:
        where.append(_SQL_WHERE_TRADE_DATE)
        params.append(_validate_trade_date(trade_date))
    if module is not None:
        where.append(_SQL_WHERE_MODULE)
        params.append(_validate_non_empty_str(module, "module"))
    if prediction_type is not None:
        where.append(_SQL_WHERE_PREDICTION_TYPE)
        params.append(_validate_non_empty_str(prediction_type, "prediction_type"))
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError(f"limit 非法（须正整数）: {limit!r}")

    sql = _SQL_QUERY_BASE
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " " + _SQL_QUERY_TAIL
    params.append(limit)

    conn = get_db_connection(_resolve_db_path(db_path))
    try:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
