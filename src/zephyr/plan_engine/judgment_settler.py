# [BLUEPRINT] MOD-PLAN-027 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §四
# [MODULE] zephyr.plan_engine.judgment_settler
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.brier_calibration(brier 纯函数复用); zephyr.plan_engine.judgment_ledger(表注册); zephyr.infrastructure.database_service(reader); zephyr.data.ch_writer(strict 写通道)
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events(事件挂点 maybe_settle_judgment_ledger); 作战室三任务聚合报告; Phase 5 meta-回测逐层归因（数据源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 结算列组唯一写方（判定模块无写通道——标准 §一.2）; 回填=轻量 mutation 带 WHERE evaluated_at IS NULL 双闸（重复回填防御，第二次扫不到未结算行）; 不可结算=eval_method='unresolvable'+原因落库（禁跳过式静默）; 业务日真源=行情库（kline_index 000300，禁墙钟猜日）; 触发=事件驱动（daily_kline SUCCESS 唤醒，禁 cron/sleep-loop）; MergeTree 只增不改——判定列组永不被 UPDATE（结算回填是唯一豁免且仅限结算列组）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（table_key/参数非法 fail-closed）; CH 异常严格上抛（结算失败必须出声，get_client_strict）; 单行回填失败=该行留未结算（下轮重试），批量报告留痕
# [TESTS] tests/plan_engine/test_judgment_settler.py
# [A_module] module_id=MOD-PLAN-027 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""judgment_settler — 判定台账共享结算器（判定台账标准 v0.1 §四）。

职责链：按 horizon 扫描到期未结算行 → 联结行情出 outcome → 回填结算列组
→ 聚合报告（按 module_id/model_version 分组）——聚合报告=Phase 5 逐层归
因报告的数据源。与判定发射器（judgment_ledger）构成判定/结算分离铁律的
两侧：本件只写结算列组，判定列组只读。

为什么并列新件而不改 brier_calibration.py：多车道在飞低冲突优先；brier
数学纯函数直接复用（import brier_score/brier_score_multiclass，既有签名
零改动）——"扩展"语义由复用+同包落位达成。

结算口径（subject=index:000300.SH，行情源=kline_index symbol='000300'，
与 pipeline_events.resolve_pf_alloc_trade_date 同真源）：
- next_day_forecast：到期=T+1 交易日收盘入库。realized_return=close_t1/close_t-1；
  label=±0.1% 带宽三态；brier=三元分布多分类 Brier；log_loss=-ln(p[实际])；
  calibration_bucket=p_up 十分位。
- intraday_market_state：到期=当日日K入库。realized_close_vs_open=close/open-1；
  state_realized=±0.3% 带宽三态；brier_contrib=多头侧（进攻+亢奋）二值 Brier；
  realized_tail_return 需 14:30 分钟源（Phase 2 接电，不伪造=留 NULL）。
- daily_plan：到期=verification 行（judgment_plan_verification 联结，取最新）；
  scenario_brier=path_prior 按 actual one-hot 多分类 Brier；当日宽限：asof 日
  < 最新业务日仍无 verification → unresolvable('verification_missing')。
- 不可结算：行情断供（asof→target 间隔超 _TARGET_GAP_DAYS_MAX）/subject 未映射/
  payload 坏 JSON → eval_method='unresolvable'+原因落 outcome_value（禁静默）。

统一 eval_score=该表主 Brier（越小越准）；outcome_value JSON 恒含 "hit"
（label 判对/方向判对/最大 prior 场景兑现）——聚合报告 hit_rate 的统一抽取键。

触发：pipeline_events 的 daily_kline SUCCESS 唤醒链挂点（参照
maybe_refresh_regime_snapshot 先例：marker 先落、永不反噬、人工逃生口=
本模块 settle_all CLI）。宪法 §9.3：禁 cron/Timer/sleep-loop。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §四
SSoT: depgraph node 14509130（MOD-PLAN-027）
Version: 0.1.0
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Final, Sequence

from zephyr.plan_engine.brier_calibration import brier_score, brier_score_multiclass
from zephyr.plan_engine.judgment_ledger import JUDGMENT_TABLES  # 表名注册单一真源（发射器侧）

__all__: Final = [
    "SettleReport",
    "SettleRowResult",
    "aggregate_report",
    "diebold_mariano",
    "settle_all",
    "settle_table",
]

# ── 口径常量 ──

_DB: Final = "c1_market"
_SUBJECT_SYMBOL: Final[dict[str, str]] = {"index:000300.SH": "000300"}  # Phase 1 首批映射
_INDEX_SOURCE_TABLE: Final = "kline_index"  # 业务日/行情真源（与 pf_alloc 同源）
_FLAT_BAND_NEXT_DAY: Final = 0.001  # 次日三态带宽 ±0.1%
_FLAT_BAND_INTRADAY: Final = 0.003  # 盘中状态三态带宽 ±0.3%
_TARGET_GAP_DAYS_MAX: Final = 10  # asof→target 自然日间隔上限（超限=行情断供）
_LABELS: Final[tuple[str, ...]] = ("up", "flat", "down")
_LOG_LOSS_CLIP: Final = 1e-12
_UNRESOLVABLE: Final = "unresolvable"

_SETTLE_COLUMNS: Final[dict[str, tuple[str, ...]]] = {
    "intraday_market_state": (
        "realized_close_vs_open",
        "state_realized",
        "brier_contrib",
        "outcome_ts",
        "outcome_value",
        "eval_method",
        "eval_score",
        "evaluated_at",
    ),
    "next_day_forecast": (
        "realized_return",
        "realized_label",
        "brier_score",
        "log_loss",
        "calibration_bucket",
        "outcome_ts",
        "outcome_value",
        "eval_method",
        "eval_score",
        "evaluated_at",
    ),
    "daily_plan": (
        "actual_scenario_id",
        "scenario_brier",
        "outcome_ts",
        "outcome_value",
        "eval_method",
        "eval_score",
        "evaluated_at",
    ),
}

_SETTLE_TABLES: Final[dict[str, str]] = JUDGMENT_TABLES  # 表名注册单一真源=发射器库件（禁另拼第二份）

_SCAN_COLUMNS: Final = ("judgment_id", "module_id", "model_version", "asof_ts", "subject", "payload", "confidence")


# ── 读写通道（模块级函数=测试注入点；生产走 DatabaseService reader / ch_writer strict）──


def _reader_execute(sql: str) -> list[tuple]:
    """只读查询（DatabaseService reader 角色——§9.1 禁裸连接散落）。"""
    from zephyr.infrastructure.database_service import get_db_service

    return list(get_db_service().get_clickhouse_conn(role="reader").execute(sql) or [])


def _writer_execute(sql: str) -> None:
    """结算回填 mutation（strict 通道：失败必须出声，结算不可假成功）。"""
    from zephyr.data.ch_writer import get_client_strict

    get_client_strict().execute(sql, settings={"mutations_sync": 1})


# ── 行情日历（联结真源）──

_KLINE_CLOSE_SQL: Final = (
    "SELECT trade_date, close FROM {db}.{src} "  # noqa: bare-sql  行情联结查询集中为模块常量
    "WHERE symbol = '{symbol}' AND quality_flag = 1 ORDER BY trade_date"
)
_KLINE_OHLC_SQL: Final = (
    "SELECT trade_date, open, close FROM {db}.{src} "  # noqa: bare-sql  行情联结查询集中为模块常量
    "WHERE symbol = '{symbol}' AND quality_flag = 1 ORDER BY trade_date"
)


def _load_kline_calendar(symbol: str) -> dict[str, float]:
    """symbol 的 trade_date→close 映射（联结真源一次拉全量——台账行数量级小）。"""
    rows = _reader_execute(_KLINE_CLOSE_SQL.format(db=_DB, src=_INDEX_SOURCE_TABLE, symbol=symbol))
    return {str(r[0]): float(r[1]) for r in rows}


def _load_kline_ohlc(symbol: str) -> dict[str, tuple[float, float]]:
    """symbol 的 trade_date→(open, close) 映射（盘中状态结算用）。"""
    rows = _reader_execute(_KLINE_OHLC_SQL.format(db=_DB, src=_INDEX_SOURCE_TABLE, symbol=symbol))
    return {str(r[0]): (float(r[1]), float(r[2])) for r in rows}


def _label_of(ret: float, band: float) -> str:
    """收益→三态标签（±band 带宽，机械映射）。"""
    if ret > band:
        return "up"
    if ret < -band:
        return "down"
    return "flat"


def _next_kline_date(calendar: dict[str, float], asof_day: str) -> str | None:
    """asof 日之后的第一个行情日（不存在=未到期）。"""
    later = [d for d in calendar if d > asof_day]
    return min(later) if later else None


# ── 单行结算（纯逻辑，行情数据以映射注入——可单测）──


@dataclass(frozen=True)
class SettleRowResult:
    """单行结算结果。"""

    judgment_id: str
    action: str  # settled / unresolvable / not_matured
    reason: str = ""
    score: float | None = None


@dataclass(frozen=True)
class SettleReport:
    """单表结算报告（JSON 可序列化）。"""

    table: str
    scanned: int
    settled: int
    unresolvable: int
    not_matured: int
    failed: int = 0  # 回填异常（行留未结算，下轮重试）
    rows: tuple[SettleRowResult, ...] = field(default_factory=tuple)

    def brief(self) -> str:
        return (
            f"{self.table}: scan={self.scanned} settled={self.settled} "
            f"unresolvable={self.unresolvable} pending={self.not_matured} failed={self.failed}"
        )


def _parse_payload(judgment_id: str, payload_raw: str) -> tuple[dict[str, Any] | None, str]:
    """payload 解析（坏 JSON=返回原因——禁跳过式静默）。"""
    try:
        obj = json.loads(payload_raw)
        if not isinstance(obj, dict):
            return None, "payload_not_dict"
        return obj, ""
    except (json.JSONDecodeError, TypeError) as exc:
        return None, f"payload_bad_json:{type(exc).__name__}"


def _settle_next_day(
    row: dict[str, Any],
    calendar: dict[str, float],
) -> tuple[dict[str, Any] | None, SettleRowResult, bool]:
    """次日概率行结算。返回 (回填列 dict|None, 结果, 是否永久不可结算)。"""
    jid = row["judgment_id"]
    payload, err = _parse_payload(jid, row["payload"])
    if payload is None:
        return None, SettleRowResult(jid, "unresolvable", err), True
    symbol = _SUBJECT_SYMBOL.get(str(row["subject"]))
    if symbol is None:
        return None, SettleRowResult(jid, "unresolvable", "subject_unmapped"), True
    asof_day = str(row["asof_ts"])[:10]
    asof_close = calendar.get(asof_day)
    if asof_close is None:
        return None, SettleRowResult(jid, "unresolvable", "asof_date_no_kline"), True
    target_day = _next_kline_date(calendar, asof_day)
    if target_day is None:
        return None, SettleRowResult(jid, "not_matured"), False  # T+1 未收盘，下轮再扫
    gap = (date.fromisoformat(target_day) - date.fromisoformat(asof_day)).days
    if gap > _TARGET_GAP_DAYS_MAX:
        return None, SettleRowResult(jid, "unresolvable", f"target_gap_{gap}d_no_kline"), True
    try:
        p_up = float(payload["p_up"])
        p_flat = float(payload["p_flat"])
        p_down = float(payload["p_down"])
    except (KeyError, TypeError, ValueError):
        return None, SettleRowResult(jid, "unresolvable", "payload_missing_probs"), True
    realized_return = calendar[target_day] / asof_close - 1.0
    label = _label_of(realized_return, _FLAT_BAND_NEXT_DAY)
    label_idx = _LABELS.index(label)
    brier = brier_score_multiclass([([p_up, p_flat, p_down], label_idx)])
    p_label = max(_LOG_LOSS_CLIP, min(1.0, (p_up, p_flat, p_down)[label_idx]))
    log_loss = -math.log(p_label)
    bucket_idx = min(int(p_up * 10), 9)
    bucket = f"{bucket_idx / 10:.1f}-{(bucket_idx + 1) / 10:.1f}"
    hit = label == _LABELS[[p_up, p_flat, p_down].index(max(p_up, p_flat, p_down))]
    backfill = {
        "realized_return": realized_return,
        "realized_label": label,
        "brier_score": brier,
        "log_loss": log_loss,
        "calibration_bucket": bucket,
        "outcome_value": json.dumps(
            {"ret": round(realized_return, 8), "label": label, "target_date": target_day, "hit": hit},
            ensure_ascii=False,
        ),
        "eval_method": "brier_multiclass",
        "eval_score": brier,
    }
    return (
        backfill,
        SettleRowResult(jid, "settled", score=brier),
        False,
    )


def _settle_intraday(
    row: dict[str, Any],
    ohlc: dict[str, tuple[float, float]],
) -> tuple[dict[str, Any] | None, SettleRowResult, bool]:
    """盘中状态行结算（realized_tail_return 留 NULL——分钟源 Phase 2 接电，不伪造）。"""
    jid = row["judgment_id"]
    payload, err = _parse_payload(jid, row["payload"])
    if payload is None:
        return None, SettleRowResult(jid, "unresolvable", err), True
    symbol = _SUBJECT_SYMBOL.get(str(row["subject"]))
    if symbol is None:
        return None, SettleRowResult(jid, "unresolvable", "subject_unmapped"), True
    asof_day = str(row["asof_ts"])[:10]
    bar = ohlc.get(asof_day)
    if bar is None:
        latest = max(ohlc) if ohlc else ""
        if latest and asof_day < latest:
            return None, SettleRowResult(jid, "unresolvable", "asof_date_no_kline"), True
        return None, SettleRowResult(jid, "not_matured"), False  # 当日未收盘
    probs = payload.get("state_probs")
    if not isinstance(probs, dict):
        return None, SettleRowResult(jid, "unresolvable", "payload_missing_state_probs"), True
    p_bull = 0.0
    for k in ("进攻", "亢奋"):
        v = probs.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            p_bull += float(v)
    open_, close = bar
    realized = close / open_ - 1.0
    state = _label_of(realized, _FLAT_BAND_INTRADAY)
    outcome_hit = 1.0 if state == "up" else 0.0
    contrib = brier_score([(p_bull, outcome_hit)])
    hit = (p_bull >= 0.5) == (state == "up")
    backfill = {
        "realized_close_vs_open": realized,
        "state_realized": state,
        "brier_contrib": contrib,
        "outcome_value": json.dumps(
            {"ret": round(realized, 8), "state": state, "p_bull": round(p_bull, 6), "hit": hit,
             "tail_return": "pending_minute_source"},
            ensure_ascii=False,
        ),
        "eval_method": "brier_binary",
        "eval_score": contrib,
    }
    return backfill, SettleRowResult(jid, "settled", score=contrib), False


def _settle_daily_plan(
    row: dict[str, Any],
    verifications: dict[str, dict[str, Any]],
    latest_day: str,
) -> tuple[dict[str, Any] | None, SettleRowResult, bool]:
    """晨间预案行结算（verification 链联结；当日宽限，隔日无验证=unresolvable）。"""
    jid = row["judgment_id"]
    asof_day = str(row["asof_ts"])[:10]
    ver = verifications.get(jid)
    if ver is None:
        if asof_day >= latest_day:
            return None, SettleRowResult(jid, "not_matured"), False  # 当日盘中宽限
        return None, SettleRowResult(jid, "unresolvable", "verification_missing"), True
    payload, err = _parse_payload(jid, row["payload"])
    if payload is None:
        return None, SettleRowResult(jid, "unresolvable", err), True
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return None, SettleRowResult(jid, "unresolvable", "payload_missing_scenarios"), True
    priors: list[float] = []
    ids: list[str] = []
    for sc in scenarios:
        if not isinstance(sc, dict):
            return None, SettleRowResult(jid, "unresolvable", "payload_bad_scenario"), True
        ids.append(str(sc.get("scenario_id")))
        priors.append(float(sc.get("path_prior", 0.0)))
    actual = str(ver.get("actual_scenario_id") or "")
    if actual not in ids:
        return None, SettleRowResult(jid, "unresolvable", "actual_scenario_unknown"), True
    brier = brier_score_multiclass([(priors, ids.index(actual))])
    top_prior = ids[priors.index(max(priors))]
    hit = actual == top_prior
    backfill = {
        "actual_scenario_id": actual,
        "scenario_brier": brier,
        "outcome_value": json.dumps(
            {"actual": actual, "top_prior": top_prior, "hit": hit,
             "plan_followed": bool(ver.get("plan_followed")),
             "n_hits": len(json.loads(ver.get("scenario_hits") or "[]"))},
            ensure_ascii=False,
        ),
        "eval_method": "brier_multiclass",
        "eval_score": brier,
    }
    return backfill, SettleRowResult(jid, "settled", score=brier), False


# ── 回填（结算器专属 mutation，双闸防重复回填）──


def _sql_literal(v: Any) -> str:
    """回填值→SQL 字面量（内部白名单列+受控类型，字符串统一转义单引号）。"""
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return repr(float(v)) if isinstance(v, float) else str(v)
    raise ValueError(f"回填值类型非法: {type(v).__name__}")


def _backfill_row(table: str, table_key: str, judgment_id: str, backfill: dict[str, Any],
                  settled_at: str) -> None:
    """单行回填：SET 结算列组 WHERE judgment_id AND evaluated_at IS NULL（双闸）。

    双闸语义：扫描侧只取 evaluated_at IS NULL；mutation 侧 WHERE 再判一次——
    并发结算器同时回填时，后到者 mutation 命中 0 行（CH mutation 按部分
    重 evaluating WHERE），结构性防重复回填覆写。
    """
    cols = _SETTLE_COLUMNS[table_key]
    assignments = ", ".join(f"{c} = {_sql_literal(backfill[c])}" for c in cols if c in backfill)
    assignments += f", outcome_ts = '{settled_at}', evaluated_at = '{settled_at}'"
    # noqa: bare-sql  结算回填 mutation 列值逐行动态拼接（白名单 _SETTLE_COLUMNS+双闸 WHERE），不可常量化
    sql = (
        f"ALTER TABLE {table} UPDATE {assignments} "
        f"WHERE judgment_id = '{judgment_id}' AND evaluated_at IS NULL "
        f"SETTINGS mutations_sync = 1"
    )
    _writer_execute(sql)


def _backfill_unresolvable(table: str, judgment_id: str, reason: str, settled_at: str) -> None:
    """不可结算留痕（eval_method='unresolvable'+原因——禁跳过式静默）。"""
    payload_json = json.dumps({"reason": reason}, ensure_ascii=False)
    # noqa: bare-sql  unresolvable 留痕 mutation 按行动态拼接（原因串受控转义），不可常量化
    _writer_execute(
        f"ALTER TABLE {table} UPDATE eval_method = '{_UNRESOLVABLE}', "
        f"outcome_value = {_sql_literal(payload_json)}, evaluated_at = '{settled_at}' "
        f"WHERE judgment_id = '{judgment_id}' AND evaluated_at IS NULL "
        f"SETTINGS mutations_sync = 1"
    )


# ── 组合入口 ──

_SCAN_UNSETTLED_SQL: Final = "SELECT {cols} FROM {table} WHERE evaluated_at IS NULL"  # noqa: bare-sql  未结算扫描查询集中为模块常量
_VERIFICATION_LATEST_SQL: Final = (
    "SELECT plan_judgment_id, actual_scenario_id, plan_followed, scenario_hits, verified_at "
    "FROM {db}.judgment_plan_verification "
    "ORDER BY plan_judgment_id, verified_at, verification_id"
)


def _scan_unsettled(table: str) -> list[dict[str, Any]]:
    cols = ", ".join(_SCAN_COLUMNS)
    rows = _reader_execute(_SCAN_UNSETTLED_SQL.format(cols=cols, table=table))
    return [dict(zip(_SCAN_COLUMNS, r)) for r in rows]


def _load_verifications() -> dict[str, dict[str, Any]]:
    """plan_judgment_id → 最新 verification 行。"""
    rows = _reader_execute(_VERIFICATION_LATEST_SQL.format(db=_DB))
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        out[str(r[0])] = {
            "actual_scenario_id": r[1],
            "plan_followed": r[2],
            "scenario_hits": r[3],
            "verified_at": str(r[4]),
        }
    return out


def _load_market_context(table_key: str) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """按表加载行情上下文（收盘联结映射 / OHLC / verification 链）。"""
    if table_key == "daily_plan":
        return {}, _load_verifications()
    if table_key == "intraday_market_state":
        return _load_kline_ohlc("000300"), {}
    return _load_kline_calendar("000300"), {}


def _settle_one_row(
    table_key: str,
    row: dict[str, Any],
    market: dict[str, Any],
    verifications: dict[str, dict[str, Any]],
    asof_day: str,
) -> tuple[dict[str, Any] | None, SettleRowResult, bool]:
    """单行结算分派（表专属结算器已收口在 _settle_* 纯函数）。"""
    if table_key == "next_day_forecast":
        return _settle_next_day(row, market)  # type: ignore[arg-type]
    if table_key == "intraday_market_state":
        return _settle_intraday(row, market)  # type: ignore[arg-type]
    return _settle_daily_plan(row, verifications, asof_day)


def _persist_settlement(
    table: str,
    table_key: str,
    backfill: dict[str, Any] | None,
    res: SettleRowResult,
    permanent: bool,
    settled_at: str,
) -> SettleRowResult:
    """回填落库（dry_run/not_matured 不写；单行失败留未结算下轮重试）。"""
    try:
        if res.action == "settled" and backfill is not None:
            _backfill_row(table, table_key, res.judgment_id, backfill, settled_at)
        elif res.action == "unresolvable" and permanent:
            _backfill_unresolvable(table, res.judgment_id, res.reason, settled_at)
    except Exception as exc:  # noqa: BLE001 — 单行失败留未结算（下轮重试），报告留痕出声
        return SettleRowResult(res.judgment_id, "failed", f"backfill_error:{type(exc).__name__}")
    return res


def settle_table(
    table_key: str,
    *,
    asof_day: str | None = None,
    dry_run: bool = False,
) -> SettleReport:
    """单表结算：扫描到期未结算行 → 联结行情 → 回填。

    Args:
        table_key: SETTLE_TABLES 键之一。
        asof_day: 业务日真源（None=行情最新入库日 resolve，禁墙钟猜日；
            测试注入保确定性）。
        dry_run: True=只扫不写（回填 dict 丢弃，返回计划）。

    Returns:
        SettleReport（brief 一行摘要供告警面）。

    Raises:
        ValueError: table_key 非法。
        RuntimeError: 业务日不可解析（调用方决定是否出声——事件挂点永不反噬）。
        Exception: CH 异常严格上抛（结算失败必须出声）。
    """
    if table_key not in _SETTLE_TABLES:
        raise ValueError(f"table_key 非法（值域 {tuple(_SETTLE_TABLES)}）: {table_key!r}")
    table = _SETTLE_TABLES[table_key]
    if asof_day is None:
        from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

        asof_day = resolve_pf_alloc_trade_date()
    rows = _scan_unsettled(table)
    if not rows:
        return SettleReport(table, 0, 0, 0, 0, ())

    settled_at = format_now3()
    market, verifications = _load_market_context(table_key)
    results: list[SettleRowResult] = []
    for row in rows:
        backfill, res, permanent = _settle_one_row(table_key, row, market, verifications, asof_day)
        results.append(res)
        if not dry_run and res.action != "not_matured":
            results[-1] = _persist_settlement(table, table_key, backfill, res, permanent, settled_at)
    return SettleReport(
        table=table,
        scanned=len(rows),
        settled=sum(1 for r in results if r.action == "settled"),
        unresolvable=sum(1 for r in results if r.action == "unresolvable"),
        not_matured=sum(1 for r in results if r.action == "not_matured"),
        failed=sum(1 for r in results if r.action == "failed"),
        rows=tuple(results),
    )


def settle_all(*, asof_day: str | None = None, dry_run: bool = False) -> dict[str, SettleReport]:
    """三表全量结算（事件挂点/人工逃生口共用入口）。"""
    return {k: settle_table(k, asof_day=asof_day, dry_run=dry_run) for k in _SETTLE_TABLES}


def format_now3() -> str:
    """当前 UTC 时刻 → DateTime64(3) 字面量（结算时刻统一口径，单次取钟）。"""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"


# ── 聚合报告（Phase 5 逐层归因的数据源）──

_AGG_SQL: Final = """
SELECT module_id, model_version,
       count() AS n_total,
       countIf(evaluated_at IS NOT NULL) AS n_settled,
       countIf(eval_method = '{unresolvable}') AS n_unresolvable,
       avgIf(eval_score, eval_score IS NOT NULL) AS avg_score,
       avg(confidence) AS avg_confidence,
       avgIf(JSONExtractBool(outcome_value, 'hit'),
             evaluated_at IS NOT NULL AND eval_method != '{unresolvable}') AS hit_rate
FROM {table}
WHERE asof_ts >= '{window_start}'{synth_clause}
GROUP BY module_id, model_version
ORDER BY module_id, model_version
"""


def aggregate_report(
    table_key: str | None = None,
    *,
    window_days: int = 20,
    asof_day: str | None = None,
    synthetic: bool | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """按 module_id/model_version 聚合结算报告（标准 §四输出契约）。

    Args:
        table_key: 单表（None=三表全量）。
        window_days: asof_ts 回看窗口（自然日）。
        asof_day: 窗口基准日（None=今天 UTC——聚合是分析口径，允许墙钟）。
        synthetic: None=全部 / True=仅合成行（冒烟）/ False=仅生产行。

    Returns:
        {table_key: [group_dict, ...]}；group 含 n_total/n_settled/n_unresolvable/
        avg_score/avg_confidence/hit_rate。
    """
    keys = (table_key,) if table_key else tuple(_SETTLE_TABLES)
    for k in keys:
        if k not in _SETTLE_TABLES:
            raise ValueError(f"table_key 非法（值域 {tuple(_SETTLE_TABLES)}）: {k!r}")
    end = date.fromisoformat(asof_day) if asof_day else datetime.now(timezone.utc).date()
    start = (end - timedelta(days=max(int(window_days) - 1, 0))).isoformat()
    synth_clause = "" if synthetic is None else f" AND synthetic = {1 if synthetic else 0}"
    out: dict[str, list[dict[str, Any]]] = {}
    for k in keys:
        sql = (
            _AGG_SQL.replace("{unresolvable}", _UNRESOLVABLE)
            .replace("{table}", _SETTLE_TABLES[k])
            .replace("{window_start}", start)
            .replace("{synth_clause}", synth_clause)
        )
        rows = _reader_execute(sql)
        cols = ("module_id", "model_version", "n_total", "n_settled", "n_unresolvable",
                "avg_score", "avg_confidence", "hit_rate")
        out[k] = [dict(zip(cols, r)) for r in rows]
    return out


# ── Diebold-Mariano（预测者对比，标准 §四结算方法之四）──


def diebold_mariano(
    losses_a: Sequence[float],
    losses_b: Sequence[float],
    h: int = 1,
) -> float:
    """DM 统计量（纯函数）：H0=两预测者期望损失相等。

    d_t = loss_a - loss_b 的均值是否显著异于 0；h=预测步长，
    方差用 lag<h 的自协方差修正（long-run variance）。惯例：dm < -1.96
    ≈ 5% 显著 → 第一预测者（A）损失显著更小（更优）；dm > 1.96 → B 更优。

    Raises:
        ValueError: 序列空/不等长/h 非法（fail-closed）。
    """
    if h < 1 or isinstance(h, bool) or not isinstance(h, int):
        raise ValueError(f"h 非法（须正整数）: {h!r}")
    if len(losses_a) != len(losses_b) or not losses_a:
        raise ValueError("losses 非法（须同长非空序列）")
    n = len(losses_a)
    d = [float(a) - float(b) for a, b in zip(losses_a, losses_b)]
    mean_d = sum(d) / n
    gamma0 = sum((x - mean_d) ** 2 for x in d) / n
    long_run = gamma0
    for lag in range(1, h):
        cov = sum((d[i] - mean_d) * (d[i + lag] - mean_d) for i in range(n - lag)) / n
        long_run += 2.0 * cov
    if long_run <= 0:
        # 零方差：差分恒定——均值非零=差异确定性存在（统计量无穷大），恒零=无差异
        return 0.0 if mean_d == 0 else math.copysign(math.inf, mean_d)
    return mean_d / math.sqrt(long_run / n)
