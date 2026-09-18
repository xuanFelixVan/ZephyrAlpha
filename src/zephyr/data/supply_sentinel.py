# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.supply_sentinel
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.alerter; zephyr.shared.io.paths; zephyr.shared.utils.time_utils; zephyr.data.calendar(懒加载)
# [CONSUMERS] zephyr.data.scheduler (_run_special_schedule: data_supply_sentinel 槽位); CLI 独立运行;
#   本槽位同时托管 zephyr.data.quality_sentinel 变异巡检（quality_sentinel.run_hosted_sweep，
#   全流通战役 R-021 辨析：不为哨兵族另开第二个排班槽位）
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 阈值配置唯一真源=src/zephyr/data/config/data_supply_sentinel.yaml（fail-visible 缺失即报错）;
#   只检测不修复（补跑由 catchup_guard/backfill 负责）; 查询失败按违规上报（宁报不漏）;
#   告警经 Alerter（失败落 failures/ 留痕）; calendar 表只对 past 窗口判停更（未来行不稀释新鲜度）;
#   新鲜度判据必须以**业务日期列**为主腿——ingest_ts 腿只证明"我们在写"，不证明"数据新"
#   （BRK-038/040 实证：同一张表业务日停更 49/323 天而 ingest 腿 lag=0 全绿）;
#   仅心跳腿覆盖的表=盲点，必出声（blind_spots→WARN），禁静默当已覆盖;
#   配置条目出现未知字段=报错（拼错一个阈值名会让该检查静默空转还谎报"已覆盖"）;
#   降级方向恒定取更严口径（trading_days 日历不可用→按日历日判，禁为过检放宽）;
#   托管的变异巡检自身故障不阻断断供腿（两段各自 try/except，各自出声）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置缺失/畸形/未知字段->SupplySentinelError 上抛（fail-visible）; 单表查询异常->计为违规+继续;
#   托管变异巡检异常->WARN 告警+blind_spot 式留痕，不改写断供腿结论; 全程不抛
# [TESTS] tests/zephyr/data/test_supply_sentinel.py
# [A_module] module_id=MOD-L00-004-SS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据断供哨兵——表级**业务新鲜度**停更检测（SOP §10.2 运维常态）。

诞生背景（altdata_line 09 清单 D1/D2 波1，2026-09-18 夜班 st-datapack-20260918）：
    股东户数表 2026-07 断供两月才被发现（shareholder_incremental 任务在、miniqmt 清退后
    管线死——「任务存在≠管线活着」SOP 反例）。L11 integrity_check 的日频口径对
    业务事件日期列表（解禁日/公告日/决议日）天然误报而被强制跳过（#ARCH-DATA-017
    _BUSINESS_EVENT_DATE_COLS），事件日历族由此成为停更检测盲区。本件补上该层：
    按表配置 max_lag_days，对 max(date_col) 落后天数判停更。

2026-09-18 全流通战役 st-ff-sentinel-20260918 的判据维度扩展（普查 R-026 第 6 型治本）：
    实测（check_tables 前后对比，见 lanes/sentinel_premise_recheck.md）证明本件此前
    度量的是「我们有没有在写」而不是「数据新不新」：
      c1_market.alt_sz_reservoir_level  max(tdate)=2026-07-31 / max(ingest_ts)=2026-09-18
                                        → 业务滞后 49 天，采集滞后 0 天，且本表**无阈值行**
      c1_market.rate_decision_calendar  按 ingest_ts 判 lag=0 全绿，而 max(decision_date)
                                        =2025-10-30（滞后 323 天）完全不可见
      c1_market.futures_warehouse_receipt 表级 lag=0 全绿，SHFE 维度实停 2025-11-17（305 天）
      c1_market.daily_valuation         FINAL 259238 行 close/amount/turnover 非零命中 **0 行**
                                        （行数正常、日期新鲜、值全 0 = 错数进闭环）
    四例共性=**单条判据（表级 max(date_col) 落后日历日）**兜不住任何一型，故扩展为：
      row_filter            维度/源粒度腿（治 SHFE 单维停更、synth_* 冒充 tdx 真值）
      lag_basis             calendar_days | trading_days（治周末/节假日/停牌合法滞后，
                            从而不必为降噪把 max_lag_days 掰宽）
      cadence               incremental | static_backfill（一次性回填/全量刷新表无日更语义，
                            改判行数地板而非日频滞后）
      min_rows_in_window    行数地板（window_days=0 即全表地板）——治"任务活着、零产出"
      column_fill_ratio     关键列非零率/非空率（治 N-1 型：非 Nullable 列把无值写成 0）
      heartbeat_leg + blind_spots  心跳腿显性声明；只有心跳腿的表=盲点，必出声

与相邻检测面的分工（查重声明）：
    - integrity_checker（L11）= 当日行数达标检测（高频日频表），事件日历表被跳过；
    - backfill_checker（L10/L10.5）= 缺口发现+补下载；
    - catchup_guard（L10.7）= 任务档期对账补跑（调度侧视角）；
    - 本件（data_supply_sentinel，L13）= 表侧业务新鲜度/维度/填充率停更检测，
      覆盖慢频/事件日历族，并托管 quality_sentinel 的三类变异检测（同一排班正门）。

用法：
    scheduler.run_schedule("data_supply_sentinel")   # 调度槽位（schedule.yaml 06:50 日批，
                                                     # APScheduler 常驻调度=自动触发正门）
    python -c "from zephyr.data.supply_sentinel import run_supply_sentinel; run_supply_sentinel()"
                                                     # 运维一次性巡检（无 argparse 入口：
                                                     # MANUAL-ONLY-PERMANENT 门禁禁 permanent 模块
                                                     # 带 manual 触发模式）
"""

from __future__ import annotations

import logging
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Final
from zoneinfo import ZoneInfo

import yaml

from zephyr.data import ch_reader
from zephyr.data.alerter import LEVEL_ERROR, LEVEL_WARN, Alerter
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "SupplySentinelError",
    "run_supply_sentinel",
    "check_tables",
    "HEARTBEAT_DATE_COLS",
]

#: 阈值配置唯一真源（规则数据=YAML，trae_062 SSoT）
_SENTINEL_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "data_supply_sentinel.yaml"

#: 业务时区（CH 业务日期列为 Asia/Shanghai 口径，判"今天"须同日界，RULE-SCHEMA-TZ）
_BUSINESS_TZ: Final = ZoneInfo("Asia/Shanghai")

#: 采集/写入心跳列——只证明"我们在写"，不证明"数据新"（BRK-038/040 教训的机检形态）
HEARTBEAT_DATE_COLS: Final = frozenset(
    {"ingest_ts", "ingest_time", "ingested_at", "captured_at", "created_at", "updated_at"}
)

#: 条目允许的键（未知键=报错，防拼错的阈值名让检查静默空转）
_ALLOWED_KEYS: Final = frozenset(
    {
        "table", "date_col", "max_lag_days", "past_only", "allow_empty",
        "rationale_zh", "reviewed_at", "reviewed_by", "gap_id",
        "row_filter", "lag_basis", "cadence", "heartbeat_leg", "leg_name",
        "min_rows_in_window", "column_fill_ratio",
    }
)
_LAG_BASES: Final = frozenset({"calendar_days", "trading_days"})
_CADENCES: Final = frozenset({"incremental", "static_backfill"})

#: 列名白名单（拼进 countIf 表达式前拦死投毒片段，同 quality_sentinel._validate_spec 口径）
_IDENT_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀常量约定；禁加 Final 注解 R-029）
_SQL_MAX_DATE = "SELECT max({date_col}) FROM {table}{where_clause}"
_SQL_ROW_COUNT = "SELECT count() FROM {table}"
_SQL_WINDOW_COUNT = "SELECT count() FROM {table}{where_clause}"
_SQL_FILL_RATIO = "SELECT count(){count_expr} FROM {table}{where_clause}"
_EMPTY_MAX_TOKENS: Final = ("", "\\N", "NULL")


class SupplySentinelError(Exception):
    """哨兵配置非法（缺失/畸形/未知字段）——fail-visible，禁码内第二真源兜底。"""


def _config_error(msg: str, **details) -> SupplySentinelError:
    """配置级错误工厂：路径/条目序号等敏感定位信息走 details 结构化字段（MSG-EXPOSURE 5.99.20）。"""
    exc = SupplySentinelError(msg)
    exc.details = details  # type: ignore[attr-defined]
    return exc


# ============== 配置加载与 fail-closed 校验 ==============


def _load_config(config_path: Path | None = None) -> list[dict[str, Any]]:
    """加载哨兵表清单（fail-visible：文件缺失/畸形/空清单/未知字段即抛）。"""
    path = config_path or _SENTINEL_CONFIG_PATH
    if not path.exists():
        raise _config_error("断供哨兵配置缺失", path=str(path))
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as ex:
        raise _config_error("断供哨兵配置 YAML 畸形", path=str(path), yaml_error=str(ex)[:200]) from ex
    tables = data.get("tables")
    if not isinstance(tables, list) or not tables:
        raise _config_error("断供哨兵配置 tables 清单为空", path=str(path))
    for i, entry in enumerate(tables):
        if not isinstance(entry, dict):
            raise _config_error("断供哨兵配置条目非映射", path=str(path), entry_index=i)
        for field in ("table", "date_col", "max_lag_days"):
            if field not in entry:
                raise _config_error(
                    "断供哨兵配置条目缺必备字段", path=str(path), entry_index=i, missing_field=field
                )
        _validate_entry(entry, path=path, index=i)
    return tables


def _validate_entry(entry: dict[str, Any], *, path: Path, index: int) -> None:
    """条目级校验：未知字段/取值域/谓词字符集/新机制字段结构一次判完（拼错即红，不静默）。"""
    loc = {"path": str(path), "entry_index": index, "table": entry.get("table")}
    unknown = set(entry) - _ALLOWED_KEYS
    if unknown:
        raise _config_error(f"断供哨兵配置含未知字段（拼错=该检查静默空转）: {sorted(unknown)}", **loc)
    date_col = str(entry["date_col"])
    if date_col in HEARTBEAT_DATE_COLS and not entry.get("heartbeat_leg"):
        raise _config_error(
            f"心跳列 {date_col} 作 date_col 须显式声明 heartbeat_leg: true"
            "（心跳只证明进程活着，不证明数据新——BRK-038/040）",
            **loc,
        )
    if entry.get("lag_basis", "calendar_days") not in _LAG_BASES:
        raise _config_error("lag_basis 取值非法（calendar_days|trading_days）", **loc)
    if entry.get("cadence", "incremental") not in _CADENCES:
        raise _config_error("cadence 取值非法（incremental|static_backfill）", **loc)
    _validate_row_filter(entry.get("row_filter"), loc=loc)
    _validate_min_rows(entry.get("min_rows_in_window"), loc=loc)
    _validate_fill_ratio(entry.get("column_fill_ratio"), loc=loc)


def _validate_row_filter(row_filter: Any, *, loc: dict) -> None:
    """维度谓词字符集护栏：只拦语句级逃逸（分号/注释/UNION），比较表达式放行。"""
    if row_filter is None:
        return
    if not isinstance(row_filter, str) or not row_filter.strip():
        raise _config_error("row_filter 须为非空字符串", **loc)
    lowered = row_filter.lower()
    for banned in (";", "--", "/*", "*/", "union", "insert", "delete", "drop", "alter"):
        if banned in lowered:
            raise _config_error(f"row_filter 含禁用片段 {banned!r}", **loc)


def _validate_min_rows(spec: Any, *, loc: dict) -> None:
    """min_rows_in_window 结构校验（window_days=0 即全表行数地板）。"""
    if spec is None:
        return
    if not isinstance(spec, dict):
        raise _config_error("min_rows_in_window 须为映射", **loc)
    unknown = set(spec) - {"window_days", "min_rows"}
    if unknown:
        raise _config_error(f"min_rows_in_window 含未知字段: {sorted(unknown)}", **loc)
    window_days, min_rows = _as_pos_int(spec.get("window_days", 0)), _as_pos_int(spec.get("min_rows", 1))
    if window_days is None or min_rows is None or min_rows < 1:
        raise _config_error("min_rows_in_window 的 window_days/min_rows 须为非负/正整数", **loc)


def _validate_fill_ratio(spec: Any, *, loc: dict) -> None:
    """column_fill_ratio 结构校验（cols 非空 + min_ratio∈(0,1] + 列名白名单）。"""
    if spec is None:
        return
    if not isinstance(spec, dict):
        raise _config_error("column_fill_ratio 须为映射", **loc)
    unknown = set(spec) - {"cols", "min_ratio", "window_days", "treat_zero_as_missing"}
    if unknown:
        raise _config_error(f"column_fill_ratio 含未知字段: {sorted(unknown)}", **loc)
    cols = spec.get("cols")
    if not isinstance(cols, list) or not cols:
        raise _config_error("column_fill_ratio.cols 须为非空列表", **loc)
    for col in cols:
        if not _IDENT_RE.match(str(col)):
            raise _config_error(f"column_fill_ratio.cols 含非法列名: {col!r}", **loc)
    try:
        ratio = float(spec.get("min_ratio", 0.95))
    except (TypeError, ValueError) as ex:
        raise _config_error("column_fill_ratio.min_ratio 须为数值", **loc) from ex
    if not 0 < ratio <= 1:
        raise _config_error("column_fill_ratio.min_ratio 须在 (0,1]", **loc)
    if _as_pos_int(spec.get("window_days", 0)) is None:
        raise _config_error("column_fill_ratio.window_days 须为非负整数", **loc)


def _as_pos_int(value: Any) -> int | None:
    """非负整数解析（bool 拒收——YAML `true` 投毒成 1 是静默失效的老坑）。"""
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


# ============== SQL 组装与执行 ==============

QueryRunner = Callable[[str], str]


def _business_today() -> date:
    """今日（业务时区口径）——now_utc() 唯一入口（RULE-SCHEMA-TZ），禁 date.today() 散落。"""
    return now_utc().astimezone(_BUSINESS_TZ).date()


def _predicates(
    entry: dict[str, Any], today: date, *, window_days: int | None = None, upper_bound: bool = True
) -> list[str]:
    """条目 -> SQL 谓词列表：past_only 上界 + row_filter 维度切片 + 可选回看窗下界。"""
    date_col = str(entry["date_col"])
    preds: list[str] = []
    if upper_bound and entry.get("past_only"):
        preds.append(f"{date_col} <= toDate('{today.isoformat()}')")
    if entry.get("row_filter"):
        preds.append(f"({entry['row_filter']})")
    if window_days:
        preds.append(f"{date_col} >= toDate('{(today - timedelta(days=window_days)).isoformat()}')")
    return preds


def _where(preds: list[str]) -> str:
    return f" WHERE {' AND '.join(preds)}" if preds else ""


def _scalar(runner: QueryRunner, sql: str) -> str:
    """取单标量首行首列；空返回=查询失败（ch_reader 失败返回 ""，宁报不漏按违规处理）。"""
    raw = runner(sql)
    if raw is None:
        raise ValueError("查询无返回（CH 不可达）")
    first = str(raw).strip().split("\n")[0].strip()
    if not first:
        raise ValueError("查询返回空值（CH 失败或列不存在）")
    return first


def _is_empty_max(raw: str) -> bool:
    """max(date) 空值判定：NULL/\\N/1970-01-01（空表 max() 在 CH 返纪元而非 NULL，D5 实测）。"""
    return raw in _EMPTY_MAX_TOKENS or raw.startswith("1970-01-01")


def _default_calendar():
    from zephyr.data.calendar import get_market_calendar

    return get_market_calendar("ashare")


# ============== 三类判据腿 ==============


def _check_date_leg(
    entry: dict[str, Any], today: date, runner: QueryRunner, calendar_cache: dict
) -> dict[str, Any]:
    """业务新鲜度腿：max(date_col) 落后天数 vs max_lag_days（含维度切片/交易日口径/回填档位）。"""
    table = str(entry["table"])
    date_col = str(entry["date_col"])
    max_lag = int(entry["max_lag_days"])
    result: dict[str, Any] = {
        "table": table, "date_col": date_col, "leg": entry.get("leg_name"),
        "max_date": None, "lag_days": None, "max_lag_days": max_lag,
        "breached": False, "detail": "ok",
    }
    if entry.get("cadence") == "static_backfill":
        result["detail"] = "cadence=static_backfill（无日更语义，新鲜度腿让位于行数地板）"
        return result
    sql = _SQL_MAX_DATE.format(
        date_col=date_col, table=table, where_clause=_where(_predicates(entry, today))
    )
    raw = _scalar(runner, sql)
    if _is_empty_max(raw):
        if entry.get("allow_empty"):
            result["detail"] = "empty(allowed)"
            return result
        result["breached"] = True
        result["detail"] = "empty table or dimension slice"
        return result
    max_date = date.fromisoformat(raw.split(" ")[0])
    lag_days = _lag_days(entry, max_date, today, calendar_cache)
    result["max_date"] = max_date.isoformat()
    result["lag_days"] = lag_days
    if lag_days > max_lag:
        result["breached"] = True
        basis = entry.get("lag_basis", "calendar_days")
        result["detail"] = f"lag={lag_days}d({basis}) > {max_lag}d"
    return result


def _lag_days(entry: dict[str, Any], max_date: date, today: date, calendar_cache: dict) -> int:
    """落后天数：日历日 or 交易日口径。交易日兜不住时降级为日历日（更严方向，永不放宽）。"""
    calendar_days = (today - max_date).days
    if entry.get("lag_basis") != "trading_days":
        return calendar_days
    try:
        if "cal" not in calendar_cache:
            calendar_cache["cal"] = _default_calendar()
        window = calendar_cache["cal"].trading_days_in_range(max_date + timedelta(days=1), today)
        return len(list(window))
    except Exception as exc:  # noqa: BLE001 — 降级取更严口径（日历日），并在 detail 留痕
        log.warning("断供哨兵 trading_days 降级为日历日: %s", exc)
        return calendar_days


def _check_row_floor_leg(entry: dict[str, Any], today: date, runner: QueryRunner) -> dict | None:
    """行数地板腿：窗口内（含 row_filter 切片）行数 < min_rows 即违规。

    治"调度成功、日志无错、数据不更新"型半死管线（BRK-040），以及
    `source_min_rows` 需求（row_filter 切到真值源，synth_* 冒充不再算数）。
    window_days=0 → 全表计数（static_backfill 表的正确判据）。
    """
    spec = entry.get("min_rows_in_window")
    if not spec:
        return None
    window_days = int(spec.get("window_days", 0))
    min_rows = int(spec.get("min_rows", 1))
    preds = _predicates(entry, today, window_days=window_days)
    sql = _SQL_WINDOW_COUNT.format(table=entry["table"], where_clause=_where(preds))
    rows = int(_scalar(runner, sql))
    outcome = {
        "kind": "row_floor", "window_days": window_days, "min_rows": min_rows, "rows": rows,
        "breached": rows < min_rows,
        "detail": f"rows={rows} < floor {min_rows}" if rows < min_rows else f"rows={rows}",
    }
    return outcome


def _check_fill_ratio_leg(entry: dict[str, Any], today: date, runner: QueryRunner) -> dict | None:
    """关键列填充率腿：cols 各列"有值行占比"低于 min_ratio 即违规（N-1 型：值写成 0 也算无值）。

    行数正常、日期新鲜但关键列全 0 = 错数进闭环，前两腿都兜不住，故独立成判据。
    """
    spec = entry.get("column_fill_ratio")
    if not spec:
        return None
    cols = [str(c) for c in spec["cols"]]
    min_ratio = float(spec.get("min_ratio", 0.95))
    window_days = int(spec.get("window_days", 0))
    treat_zero_missing = bool(spec.get("treat_zero_as_missing", True))
    exprs = "".join(f", countIf({_fill_expr(c, treat_zero_missing)})" for c in cols)
    sql = _SQL_FILL_RATIO.format(
        count_expr=exprs, table=entry["table"],
        where_clause=_where(_predicates(entry, today, window_days=window_days)),
    )
    values = _scalar(runner, sql).split("\t")
    if len(values) != len(cols) + 1:
        # 返回列数与请求不符（列不存在/CH 静默降级）= 该腿未生效，禁当"干净"放行
        raise ValueError(f"fill_ratio 返回列数 {len(values)} != 请求列数+1 {len(cols) + 1}")
    total = int(values[0])
    if total == 0:
        # 窗口内 0 行属"空表/断供"语义，由新鲜度腿与行数地板腿负责，此处不重复鸣（避免一因双告）
        return {"kind": "fill_ratio", "cols": cols, "rows": 0, "breached": False,
                "detail": "fill_ratio skipped: window has 0 rows（空窗由新鲜度/地板腿判定）"}
    ratios = {c: int(v.strip() or 0) / total for c, v in zip(cols, values[1:])}
    low = {c: round(r, 4) for c, r in ratios.items() if r < min_ratio}
    return {
        "kind": "fill_ratio", "cols": cols, "rows": total, "ratios": ratios, "min_ratio": min_ratio,
        "breached": bool(low),
        "detail": f"低填充列 {low}" if low else f"{len(cols)} 列填充率均 >= {min_ratio}",
    }


def _fill_expr(col: str, treat_zero_missing: bool) -> str:
    """命中表达式：非零口径用 ifNull(col,0)!=0（NULL 视同无值），非空口径用 isNotNull。"""
    if treat_zero_missing:
        return f"ifNull({col}, 0) != 0"
    return f"isNotNull({col})"


def _check_one_entry(entry: dict[str, Any], today: date, runner: QueryRunner, calendar_cache: dict) -> dict:
    """单条目全腿判定（任一条腿抛异常=该条目违规，宁报不漏，不阻断其余表）。"""
    try:
        result = _check_date_leg(entry, today, runner, calendar_cache)
        extras = [o for o in (_check_row_floor_leg(entry, today, runner),
                              _check_fill_ratio_leg(entry, today, runner)) if o]
    except Exception as exc:  # noqa: BLE001 — 单表查询异常按违规计，不阻断其余表
        return {
            "table": entry["table"], "date_col": entry.get("date_col"), "leg": entry.get("leg_name"),
            "max_date": None, "lag_days": None, "max_lag_days": entry.get("max_lag_days"),
            "breached": True, "detail": f"query error: {str(exc)[:120]}", "checks": [],
        }
    result["checks"] = extras
    failing = [o for o in extras if o["breached"]]
    if failing:
        result["breached"] = True
        joined = "; ".join(o["detail"] for o in failing)
        result["detail"] = joined if result["detail"] == "ok" else f"{result['detail']}; {joined}"
    elif extras and not result["breached"]:
        result["detail"] = f"{result['detail']}; 附加腿 {len(extras)} 项均达标"
    return result


def find_heartbeat_only_blind_spots(entries: list[dict[str, Any]]) -> list[str]:
    """只有心跳腿（ingest_ts 类）覆盖的表 = 业务新鲜度盲点（BRK-038 型致盲的机检形态）。"""
    covered: dict[str, set[str]] = {}
    for entry in entries:
        legs = covered.setdefault(str(entry["table"]), set())
        key = "heartbeat" if entry.get("heartbeat_leg") else "business"
        legs.add(key)
    return sorted(t for t, legs in covered.items() if legs == {"heartbeat"})


# ============== 汇总与告警 ==============


def check_tables(
    config_path: Path | None = None, *, today: date | None = None, runner: QueryRunner | None = None
) -> dict[str, Any]:
    """逐条目检测业务新鲜度/行数地板/关键列填充率，返回汇总。

    Returns:
        {ok, checked, breached, results, blind_spots, heartbeat_blind}
        注：blind_spots 是"配置覆盖形态"判定（不查库），单独计数不并入 breached。
    """
    today = today or _business_today()
    runner = runner or (lambda sql: ch_reader.query(sql))
    entries = _load_config(config_path)
    calendar_cache: dict = {}
    results = [_check_one_entry(entry, today, runner, calendar_cache) for entry in entries]
    breached = [r for r in results if r["breached"]]
    blind = find_heartbeat_only_blind_spots(entries)
    return {
        "ok": not breached and not blind,
        "checked": len(results),
        "breached": len(breached),
        "results": results,
        "blind_spots": blind,
        "heartbeat_blind": len(blind),
    }


def _alert_breaches(alerter: Alerter, summary: dict[str, Any]) -> None:
    """违规腿逐条告警 + 盲点 WARN 出声（盲点不告警=普查那种"以为覆盖了"的复现）。"""
    for r in summary["results"]:
        if not r["breached"]:
            log.info("断供哨兵 ok: %s.%s max=%s lag=%sd", r["table"], r.get("date_col"), r["max_date"], r["lag_days"])
            continue
        leg = f"[{r['leg']}] " if r.get("leg") else ""
        try:
            alerter.notify(
                "data_supply_sentinel",
                f"断供嫌疑: {leg}{r['table']} max({r.get('date_col')})={r.get('max_date')} "
                f"停更 [{r['detail']}]",
                level=LEVEL_ERROR,
                source="supply_sentinel",
            )
        except Exception:  # noqa: BLE001 — 告警通道故障不阻断巡检
            log.exception("断供哨兵告警写入失败: %s", r["table"])
    for table in summary.get("blind_spots") or []:
        try:
            alerter.notify(
                "data_supply_sentinel",
                f"哨兵盲点: {table} 仅有 ingest 心跳腿覆盖，业务日期新鲜度无人盯（BRK-038/040 型）",
                level=LEVEL_WARN,
                source="supply_sentinel",
                extra={"blind_spot": "heartbeat_only", "table": table},
            )
        except Exception:  # noqa: BLE001 — 告警通道故障不阻断巡检
            log.exception("断供哨兵盲点告警写入失败: %s", table)


def run_supply_sentinel(alerter: Alerter | None = None) -> dict[str, Any]:
    """哨兵入口（调度槽位/运维共用）：断供检测 + 托管变异巡检 + 告警留痕。全程不抛。"""
    alerter = alerter or Alerter()
    try:
        summary = check_tables()
    except SupplySentinelError as e:
        log.error("断供哨兵配置错误: %s", e)
        alerter.notify("data_supply_sentinel", f"哨兵配置错误（检测未执行）: {e}", level=LEVEL_ERROR,
                       source="supply_sentinel")
        return {"ok": False, "config_error": str(e)}
    _alert_breaches(alerter, summary)
    log.info(
        "断供哨兵巡检完成: checked=%d breached=%d blind_spots=%d ok=%s",
        summary["checked"], summary["breached"], summary["heartbeat_blind"], summary["ok"],
    )
    # 托管变异巡检（quality_sentinel 三类检测）：本槽位是 L13 哨兵唯一排班正门，
    # 不为第二个哨兵另开空档期（空档期=静默假通道，R-021）。自身故障只出声不改写断供结论。
    summary["quality_sweep"] = _run_hosted_quality_sweep(alerter)
    return summary


def _run_hosted_quality_sweep(alerter: Alerter) -> dict[str, Any]:
    """在同一条 L13 排班腿里跑 quality_sentinel 变异巡检（只读；报告落盘由其自身负责）。"""
    try:
        from zephyr.data.quality_sentinel import run_hosted_sweep

        return run_hosted_sweep(alerter=alerter)
    except Exception as exc:  # noqa: BLE001 — 托管巡检故障出声不阻断断供结论
        log.exception("托管质量巡检失败")
        try:
            alerter.notify(
                "data_supply_sentinel",
                f"质量变异巡检未执行（托管腿故障）: {str(exc)[:200]}",
                level=LEVEL_WARN,
                source="supply_sentinel",
            )
        except Exception:  # noqa: BLE001 — 告警通道自身故障不再上抛
            pass
        return {"ok": False, "error": str(exc)[:200]}
