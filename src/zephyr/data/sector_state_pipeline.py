# [BLUEPRINT] MOD-SIG-026 supplement | docs/_working/sector_line/sector_layer_skeleton_v0.md §6 + 22_sector_rotation_spec.md §3.1
# [MODULE] zephyr.data.sector_state_pipeline
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; zephyr.signal_ashare.sector.sector_state_aggregator(纯函数算法层); schemas.categories.sector_state; schemas.categories.sector_preference
# [CONSUMERS] data scheduler 特殊槽 sector_close_final/sector_pre_open（scheduler.py _run_special_schedule 分支）; strategy_pipeline.daily_gate_snapshot（load_l2_admission，L2 门三原料供料）; plan_engine 编排链（经 gate 快照间接消费——丁线 owner_gate C1 乙档治本）
# [STARTUP] imported（由 data scheduler 两特殊槽定时调用；无独立常驻进程）
# [MATURITY] testing
# [INVARIANTS] 纯编排层（CH 面板读取+落库），算法零重造（全部委托 sector_state_aggregator 纯函数）；
#   stage 契约：close_final=T 日 15:10 行情定格（真源态）；pre_open=T+1 09:15 复制 T 日 close_final
#   +偏好重映射（消费 emotion_index@T close_final——晚于情绪班落库时点，无竞速）；同一时戳禁循环
#   （板块热度禁回灌 emotion_index）；pit 纪律：T 日行只吃 ≤T 数据；幂等=ReplacingMergeTree 同键
#   去重可安全重跑；总闸 data/runtime/sector_state_pipeline.disabled 存在=跳过（服务总闸惯例）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一原料缺席→对应成分 status=missing/insufficient 如实落库不硬凑；CH 不可达
#   /零面板→返回 False+告警（调用方 alerter），不抛反噬调度器
# [TESTS] tests/data/test_sector_state_pipeline.py（面板装配 SQL 形态级+偏好消费契约级）
# [TTL] permanent
"""板块状态管道（批2 落库编排器：close_final 定格 / pre_open 消费）。

数据流（骨架稿 §1/§6）：
  kline_sector_880(70日面板) ─┐
  limit_up_pool×sector_constituent ─┼→ sector_state_aggregator.assemble_sector_states
  money_flow×sector_constituent ─┘         ↓
                            c1_market.sector_state（close_final, T 日 15:10）
                                        ↓ 复制+重映射（T+1 09:15）
              c1_market.sector_state(pre_open) + c1_market.sector_preference(pre_open)

排班：sector_close_final（15:10）/ sector_pre_open（09:15）两特殊槽（dloop_post 同款
编排型调用先例，不入 tasks.yaml 表构建管线——计算时刻非数据源）。
# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/sector_line/sector_state_pipeline.yaml
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path

from zephyr.data.ch_writer import WriteDisposition, write_tsv_outcome
from zephyr.data.table_registry import get_registry
from zephyr.signal_ashare.sector.sector_state_aggregator import (
    AGGREGATOR_VERSION,
    SectorPanelInputs,
    assemble_sector_states,
    map_preference,
)

_TBL_STATE = get_registry().table("market_sector_state")
_TBL_PREF = get_registry().table("market_sector_preference")
_TBL_KLINE880 = get_registry().table("market_sector_kline_880")
_TBL_CONSTITUENT = get_registry().table("market_sector_constituent_880")
_TBL_LIMIT_UP = get_registry().table("market_limit_up_pool")
_TBL_MONEY_FLOW = get_registry().table("market_money_flow")
_TBL_REGIME = get_registry().table("backtest_regime_state_anchored")
_TBL_EMOTION = get_registry().table("market_emotion_index")
_TBL_INDEX_KLINE = get_registry().table("market_index_kline")

log = logging.getLogger(__name__)

#: 面板回看窗（交易日）：RRG 需 62 日 + leader 历史余量
_PANEL_LOOKBACK_DAYS = 75
#: 面板回看日历窗（自然日；≈75 交易日 + 节假日余量）
_PANEL_LOOKBACK_CALENDAR_DAYS = 115
#: leader 历史天数（市场级 lead_streak 判定用）
_LEADER_HISTORY_LEN = 10
_LATEST_TRADE_DATE_SQL = (
    "SELECT max(trade_date) "
    "FROM {kline880} WHERE trade_date <= toDate('{asof}')"
)
_LATEST_TRADE_DATE_UNBOUNDED_SQL = (
    "SELECT max(trade_date) "
    "FROM {kline880}"
)
_PANEL_SQL = (
    "SELECT sector_code, sector_name, trade_date, toFloat64(close), toFloat64(amount) "
    "FROM {kline880} FINAL "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{trade_date}') "
    "ORDER BY sector_code, trade_date"
)
_BENCH_SQL = (
    "SELECT trade_date, toFloat64(close) "
    "FROM {kline880} FINAL "
    "WHERE sector_code = '880001.SH' AND trade_date <= toDate('{trade_date}') "
    "ORDER BY trade_date DESC LIMIT {lookback}"
)
_CONSTITUENT_SQL = (
    "SELECT sector_code, sector_name, stock_code "
    "FROM {constituent} FINAL "
    "WHERE valid_from <= toDate('{trade_date}') AND (valid_to IS NULL OR valid_to > toDate('{trade_date}'))"
)
_LIMIT_UP_SQL = (
    "SELECT symbol_canonical, consec_limit "
    "FROM {limit_up} FINAL"
    " WHERE trade_date = toDate('{trade_date}')"
)
_MONEY_FLOW_SQL = (
    "SELECT symbol, toFloat64(main_net_inflow) "
    "FROM {money_flow} FINAL WHERE trade_date = toDate('{trade_date}')"
)
_REGIME_SQL = (
    "SELECT dominant "
    "FROM {regime} FINAL WHERE trade_date = toDate('{trade_date}') LIMIT 1"
)
_EMOTION_SQL = (
    "SELECT emotion_index, version "
    "FROM {emotion} FINAL "
    "WHERE trade_date = toDate('{trade_date}') AND stage = 'close_final' "
    "ORDER BY ts DESC LIMIT 1"
)
_COPY_PRE_OPEN_SQL = (
    "SELECT sector_code, sector_name, momentum_pct, rrg_quadrant, strength, "
    "net_inflow_pct, capital_score, watch_score, components, version "
    "FROM {state_table} FINAL "
    "WHERE trade_date = toDate('{trade_date}') AND stage = 'close_final'"
)


_TABLE_SLOTS: dict[str, str] = {
    "kline880": _TBL_KLINE880,
    "constituent": _TBL_CONSTITUENT,
    "limit_up": _TBL_LIMIT_UP,
    "money_flow": _TBL_MONEY_FLOW,
    "regime": _TBL_REGIME,
    "emotion": _TBL_EMOTION,
    "state_table": _TBL_STATE,
    "pref_table": _TBL_PREF,
}


def _sql(template: str, **kw) -> str:
    """SQL 常量格式化：表名槽位集中注入（TableRegistry 真源），其余参数显式传。"""
    slots = {**_TABLE_SLOTS, **kw}
    return template.format(**slots)


_SQL_L2_PREF = (
    "SELECT preference_label, tilt, banned_quadrant, watch_score "
    "FROM {pref_table} FINAL "
    "WHERE trade_date = toDate('{trade_date}') AND stage = 'pre_open' LIMIT 1"
)
_SQL_L2_STATE = (
    "SELECT sector_code, rrg_quadrant, momentum_pct, strength "
    "FROM {state_table} FINAL "
    "WHERE trade_date = toDate('{trade_date}') AND stage = 'pre_open'"
)

SECTOR_STATE_TABLE = _TBL_STATE
SECTOR_PREFERENCE_TABLE = _TBL_PREF
SECTOR_STATE_COLUMNS = (
    "(trade_date, stage, ts, sector_code, sector_name, momentum_pct, rrg_quadrant, "
    "strength, net_inflow_pct, capital_score, watch_score, components, version)"
)
SECTOR_PREFERENCE_COLUMNS = (
    "(trade_date, stage, ts, regime_dominant, emotion_index, emotion_version, "
    "preference_label, tilt, banned_quadrant, watch_score, version)"
)


def _flag_disabled() -> bool:
    """服务总闸：data/runtime/sector_state_pipeline.disabled 存在=跳过（即时生效）。"""
    flag = Path(__file__).resolve().parents[3] / "data" / "runtime" / "sector_state_pipeline.disabled"
    return flag.exists()


def _latest_trade_date(ch, asof: datetime.date | None = None) -> datetime.date | None:
    """面板基准日：kline_sector_880 最新交易日（≤asof；空库/CH 故障 None）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(
        _sql(_LATEST_TRADE_DATE_SQL, asof=asof.isoformat()) if asof else _sql(_LATEST_TRADE_DATE_UNBOUNDED_SQL)
    )
    line = (tsv or "").strip().splitlines()
    if not line or not line[0].strip():
        return None
    try:
        return datetime.date.fromisoformat(line[0].strip()[:10])
    except ValueError:
        return None


def _parse_date_cell(cell: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(cell.strip()[:10])
    except ValueError:
        return None


def _load_close_panel(ch_reader, trade_date: datetime.date) -> tuple[dict, dict, dict] | None:
    """收盘/成交额/名称三面板（日历窗 + (code,date) 去重后写胜）。"""
    closes: dict[str, list[float]] = {}
    amounts: dict[str, list[float]] = {}
    names: dict[str, str] = {}
    dates: list[datetime.date] = []
    start = trade_date - datetime.timedelta(days=_PANEL_LOOKBACK_CALENDAR_DAYS)
    tsv = ch_reader.query(_sql(_PANEL_SQL, start=start.isoformat(), trade_date=trade_date.isoformat()))
    if not tsv:
        return None
    # FINAL 语义兜底：Python 侧 (code, date) 去重后写胜（防配额降级 FINAL 失效时重复行）
    seen: dict[tuple[str, datetime.date], int] = {}
    rows_raw: list[tuple[str, str, datetime.date, float, float]] = []
    for line in tsv.splitlines():
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        dt = _parse_date_cell(parts[2])
        if dt is None:
            continue
        try:
            rows_raw.append((parts[0], parts[1], dt, float(parts[3]), float(parts[4])))
        except ValueError:
            continue
        seen[(parts[0], dt)] = len(rows_raw) - 1
        if dt not in dates:
            dates.append(dt)
    dates.sort()
    # 去重后按 (code, date) 升序回填序列
    per_code: dict[str, list[tuple[datetime.date, float, float]]] = {}
    for idx in seen.values():
        code, name, dt, close, amt = rows_raw[idx]
        per_code.setdefault(code, []).append((dt, close, amt))
        if name and name != code and not names.get(code):
            names[code] = name
    for code, items in per_code.items():
        items.sort(key=lambda x: x[0])
        closes[code] = [c for _d, c, _a in items]
        amounts[code] = [a for _d, _c, a in items]
    return closes, amounts, names


def _load_benchmark(ch_reader, trade_date: datetime.date) -> list[float]:
    """基准（880001.SH）收盘升序序列。"""
    bench_tsv = ch_reader.query(_sql(_BENCH_SQL, trade_date=trade_date.isoformat(), lookback=_PANEL_LOOKBACK_DAYS))
    bench_rows: list[tuple[datetime.date, float]] = []
    for line in (bench_tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        dt = _parse_date_cell(parts[0])
        if dt is not None:
            try:
                bench_rows.append((dt, float(parts[1])))
            except ValueError:
                continue
    bench_rows.sort()  # DESC 输入翻转升序
    return [v for _d, v in bench_rows]


def _load_constituent_map(ch_reader, trade_date: datetime.date, names: dict[str, str]) -> tuple[dict, dict]:
    """成分 PIT 反查映射 + 各板块成分数（码后缀归一供涨停/资金流 join）。"""
    stock_to_sector: dict[str, list[str]] = {}
    constituent_count: dict[str, int] = {}
    tsv = ch_reader.query(_sql(_CONSTITUENT_SQL, trade_date=trade_date.isoformat()))
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        code, name, stock = parts[0], parts[1], parts[2]
        bare = stock.split(".")[0]
        stock_to_sector.setdefault(bare, []).append(code)
        constituent_count[code] = constituent_count.get(code, 0) + 1
        if name and name != code and not names.get(code):
            names[code] = name
    return stock_to_sector, constituent_count


def _load_limit_up_maps(ch_reader, trade_date: datetime.date, stock_to_sector: dict) -> tuple[dict, dict]:
    """涨停数 + 连板梯队（成分反查，绕行业名错配）。"""
    limit_up_by_sector: dict[str, int] = {}
    tier_by_sector: dict[str, tuple[int, int]] = {}
    tsv = ch_reader.query(_sql(_LIMIT_UP_SQL, trade_date=trade_date.isoformat()))
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        sym = parts[0].split(".")[0]
        try:
            consec = int(parts[1])
        except ValueError:
            consec = 1
        for code in stock_to_sector.get(sym, ()):  # 一股多板块归属全计
            limit_up_by_sector[code] = limit_up_by_sector.get(code, 0) + 1
            t2, t3 = tier_by_sector.get(code, (0, 0))
            tier_by_sector[code] = (t2 + (1 if consec >= 2 else 0), t3 + (1 if consec >= 3 else 0))
    return limit_up_by_sector, tier_by_sector


def _load_sector_inflow(ch_reader, trade_date: datetime.date, stock_to_sector: dict) -> dict[str, float]:
    """money_flow 板块聚合（spec §3.1⑥ 唯一路径）。"""
    sector_inflow: dict[str, float] = {}
    tsv = ch_reader.query(_sql(_MONEY_FLOW_SQL, trade_date=trade_date.isoformat()))
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        sym = parts[0].split(".")[0]
        try:
            val = float(parts[1])
        except ValueError:
            continue
        for code in stock_to_sector.get(sym, ()):
            sector_inflow[code] = sector_inflow.get(code, 0.0) + val
    return sector_inflow


def _load_panels(trade_date: datetime.date) -> dict | None:
    """一次性拉齐聚合所需面板（CH 只读；缺原料返回 dict 内 None 由成分 status 如实标注）。"""
    from zephyr.data import ch_reader

    loaded = _load_close_panel(ch_reader, trade_date)
    if loaded is None:
        return None
    closes, amounts, names = loaded
    bench_closes = _load_benchmark(ch_reader, trade_date)
    stock_to_sector, constituent_count = _load_constituent_map(ch_reader, trade_date, names)
    limit_up_by_sector, tier_by_sector = _load_limit_up_maps(ch_reader, trade_date, stock_to_sector)
    sector_inflow = _load_sector_inflow(ch_reader, trade_date, stock_to_sector)
    return {
        "closes": closes,
        "amounts": amounts,
        "benchmark": bench_closes,
        "names": names,
        "constituent_count": constituent_count,
        "limit_up": limit_up_by_sector,
        "tiers": tier_by_sector,
        "inflow": sector_inflow,
    }


def _load_leader_history(closes: dict[str, list[float]], n: int = _LEADER_HISTORY_LEN) -> list[str]:
    """近 n 日领涨板块序列（旧→今）：逐日截面涨幅 Top1。"""
    lengths = {c: len(s) for c, s in closes.items()}
    if not lengths:
        return []
    total = min(lengths.values())
    history: list[str] = []
    for off in range(max(1, total - n), total):
        best_code, best_pct = "", None
        for code, seq in closes.items():
            if len(seq) < off + 1 or seq[off - 1] <= 0:
                continue
            pct = seq[off] / seq[off - 1] - 1.0
            if best_pct is None or pct > best_pct:
                best_code, best_pct = code, pct
        if best_code:
            history.append(best_code)
    return history


def run_close_final(trade_date: datetime.date | None = None, *, alerter=None) -> bool:
    """T 日盘后定格：组装五成分截面并落 sector_state（stage=close_final, ts=15:10）。"""
    if _flag_disabled():
        log.info("sector_state_pipeline 跳过：总闸 sector_state_pipeline.disabled 存在")
        return False
    from zephyr.data import ch_reader

    t = trade_date or _latest_trade_date(ch_reader)
    if t is None:
        log.error("sector_state close_final 无基准交易日（面板空/CH 不可达）")
        return False
    panels = _load_panels(t)
    if not panels or not panels["closes"]:
        log.error("sector_state close_final 面板为空（trade_date=%s）", t)
        return False
    rows, market = assemble_sector_states(
        panels["closes"],
        trade_date=t,
        benchmark_closes=panels["benchmark"] or [],
        panels=SectorPanelInputs(
            amount_panel=panels["amounts"],
            limit_up_by_sector=panels["limit_up"],
            tier_by_sector=panels["tiers"],
            constituents_by_sector=panels["constituent_count"],
            sector_main_inflow=panels["inflow"],
            sector_names=panels["names"],
            leader_history=_load_leader_history(panels["closes"]),
        ),
        version=AGGREGATOR_VERSION,
    )
    ts = f"{t.isoformat()} 15:10:00"
    lines = []
    for r in rows:
        lines.append(
            "\t".join(
                [
                    t.isoformat(),
                    "close_final",
                    ts,
                    r.sector_code,
                    r.sector_name or "",
                    _num(r.momentum_pct),
                    r.rrg_quadrant or "\\N",
                    _num(r.strength),
                    _num(r.net_inflow_pct),
                    _num(r.capital_score),
                    _num(r.watch_score),
                    json.dumps(r.components, ensure_ascii=False),
                    AGGREGATOR_VERSION,
                ]
            )
        )
    outcome = write_tsv_outcome(SECTOR_STATE_TABLE, SECTOR_STATE_COLUMNS, ("\n".join(lines) + "\n").encode("utf-8"))
    ok = outcome.disposition in (WriteDisposition.CH_COMMITTED, WriteDisposition.LOCAL_DURABLE)
    log.info(
        "sector_state close_final(%s): %d 行, market=%s(watch=%.2f), 写库=%s",
        t,
        len(rows),
        market.rotation_state,
        market.watch_score,
        outcome.detail,
    )
    if not ok and alerter is not None:
        alerter.notify(
            "sector_close_final",
            f"sector_state 落库异常: {outcome.detail}",
            level="ERROR",
            source="sector_state_pipeline",
        )
    return ok


def _copy_close_to_pre_open(ch_reader, base: datetime.date, target: datetime.date) -> tuple[list[str], float | None]:
    """① 复制 T=base 的 close_final → target 日 pre_open（骨架稿 §6：盘前=昨日定格态）。"""
    tsv = ch_reader.query(_sql(_COPY_PRE_OPEN_SQL, trade_date=base.isoformat()))
    lines = []
    watch = None
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 10:
            continue
        lines.append(
            "\t".join(
                [
                    target.isoformat(),
                    "pre_open",
                    f"{target.isoformat()} 09:15:00",
                    parts[0],  # sector_code
                    _null_cell(parts[1]),  # sector_name
                    _null_cell(parts[2]),  # momentum_pct
                    _null_cell(parts[3]),  # rrg_quadrant
                    _null_cell(parts[4]),  # strength
                    _null_cell(parts[5]),  # net_inflow_pct
                    _null_cell(parts[6]),  # capital_score
                    _null_cell(parts[7]),  # watch_score
                    parts[8],  # components
                    parts[9],  # version
                ]
            )
        )
        if watch is None and len(parts) >= 8:
            watch = _maybe_float(parts[7])
    return lines, watch


def _read_regime_and_emotion(ch_reader, base: datetime.date) -> tuple[str | None, float | None, str]:
    """dominant@T + emotion@T close_final（真值优先，缺窗返回 None 由映射层 mock 标注）。"""
    regime_tsv = ch_reader.query(_sql(_REGIME_SQL, trade_date=base.isoformat()))
    dominant = (regime_tsv or "").strip().splitlines()[0].strip() if (regime_tsv or "").strip() else None
    emo_tsv = ch_reader.query(_sql(_EMOTION_SQL, trade_date=base.isoformat()))
    emotion_value, emotion_version = None, ""
    if (emo_tsv or "").strip():
        emo_parts = (emo_tsv or "").strip().splitlines()[0].split("\t")
        if len(emo_parts) >= 2:
            try:
                emotion_value = float(emo_parts[0])
                emotion_version = emo_parts[1]
            except ValueError:
                pass
    return dominant, emotion_value, emotion_version


def run_pre_open(trade_date: datetime.date | None = None, *, alerter=None) -> bool:
    """T+1 盘前：复制 T 日 close_final 态为 pre_open 行 + 偏好重映射落 preference 表。

    Args:
        trade_date: 待生成的交易日（缺省=面板基准日次一自然日；行情日历由消费方终判）。
        alerter: 告警通道（调度器注入）。
    """
    if _flag_disabled():
        log.info("sector_state_pipeline 跳过：总闸 sector_state_pipeline.disabled 存在")
        return False
    from zephyr.data import ch_reader

    base = _latest_trade_date(ch_reader)
    if base is None:
        log.error("sector_state pre_open 无基准交易日")
        return False
    target = trade_date or (base + datetime.timedelta(days=1))

    # ① 复制定格态
    lines, watch = _copy_close_to_pre_open(ch_reader, base, target)
    ok_state = True
    if lines:
        outcome = write_tsv_outcome(SECTOR_STATE_TABLE, SECTOR_STATE_COLUMNS, ("\n".join(lines) + "\n").encode("utf-8"))
        ok_state = outcome.disposition in (WriteDisposition.CH_COMMITTED, WriteDisposition.LOCAL_DURABLE)
        log.info("sector_state pre_open(%s): %d 行, 写库=%s", target, len(lines), outcome.detail)
    else:
        log.warning("sector_state pre_open(%s): T=%s close_final 无行可复制", target, base)

    # ② 偏好重映射（市场级 watch_score 透传取 T 日 close_final 首行冗余列）
    dominant, emotion_value, emotion_version = _read_regime_and_emotion(ch_reader, base)
    pref = map_preference(dominant, emotion_value)
    pref_line = "\t".join(
        [
            target.isoformat(),
            "pre_open",
            f"{target.isoformat()} 09:15:00",
            dominant or "\\N",
            _num(emotion_value),
            emotion_version or "\\N",
            pref.preference_label,
            f"{pref.tilt:.4f}",
            pref.banned_quadrant or "",
            _num(watch),
            AGGREGATOR_VERSION,
        ]
    )
    outcome = write_tsv_outcome(SECTOR_PREFERENCE_TABLE, SECTOR_PREFERENCE_COLUMNS, (pref_line + "\n").encode("utf-8"))
    ok_pref = outcome.disposition in (WriteDisposition.CH_COMMITTED, WriteDisposition.LOCAL_DURABLE)
    log.info(
        "sector_preference pre_open(%s): dominant=%s emotion=%s(%s) -> %s tilt=%.2f axis=%s, 写库=%s",
        target,
        dominant,
        emotion_value,
        emotion_version or "mock",
        pref.preference_label,
        pref.tilt,
        pref.axis_status,
        outcome.detail,
    )
    if not (ok_state and ok_pref) and alerter is not None:
        alerter.notify(
            "sector_pre_open", "sector_state/pre_open 落库异常", level="ERROR", source="sector_state_pipeline"
        )
    return ok_state and ok_pref


def _rank_l2_entries(state_tsv: str, banned: str) -> dict:
    """板块行 TSV → top/retained/score 三原料（纯解析，供 load_l2_admission 复用）。"""
    entries: list[dict] = []
    for line in state_tsv.strip().splitlines():
        p = line.split("\t")
        if len(p) < 4:
            continue
        entries.append(
            {
                "sector_code": p[0],
                "rrg_quadrant": p[1],
                "momentum_pct": _maybe_float(p[2]),
                "strength": _maybe_float(p[3]),
            }
        )
    ranked = sorted(
        [e for e in entries if e["momentum_pct"] is not None],
        key=lambda e: e["momentum_pct"],
        reverse=True,
    )
    top = [e["sector_code"] for e in ranked[:5]]
    retained = [
        e["sector_code"]
        for e in entries
        if e["rrg_quadrant"] in ("leading", "improving") and (not banned or e["rrg_quadrant"] != banned)
    ]
    score = ranked[0]["strength"] if ranked and ranked[0]["strength"] is not None else None
    return {"top": top, "retained_sectors": retained, "score": score}


def load_l2_admission(trade_date: datetime.date | None = None) -> dict:
    """L2 门三原料读取（daily_gate_snapshot 消费；fail-open，异常恒 absent 不炸门）。

    Returns:
        {status: ok|absent, top: [...], retained_sectors: [...], score: float|None,
         preference_label, banned_quadrant, tilt, asof}
    """
    from zephyr.data import ch_reader

    try:
        t = trade_date or _latest_trade_date(ch_reader)
        if t is None:
            return {"status": "absent", "error": "no_trade_date"}
        pref_tsv = ch_reader.query(_sql(_SQL_L2_PREF, trade_date=t.isoformat()))
        banned, label, tilt = "", "", None
        if (pref_tsv or "").strip():
            pp = pref_tsv.strip().splitlines()[0].split("\t")
            if len(pp) >= 3:
                label, tilt_s, banned = pp[0], pp[1], pp[2]
                tilt = _maybe_float(tilt_s)
        state_tsv = ch_reader.query(_sql(_SQL_L2_STATE, trade_date=t.isoformat()))
        if not (state_tsv or "").strip():
            return {"status": "absent", "error": "no_sector_state_rows"}
        ranked = _rank_l2_entries(state_tsv, banned)
        return {
            "status": "ok",
            **ranked,
            "preference_label": label,
            "banned_quadrant": banned,
            "tilt": tilt,
            "asof": t.isoformat(),
        }
    except Exception as exc:  # noqa: BLE001 — 供料 fail-open：缺原料=门未评，不炸拍板
        return {"status": "absent", "error": type(exc).__name__}


def _num(v: float | None) -> str:
    """float → TSV 数值串（None=\\N；统一 6 位小数）。"""
    return "\\N" if v is None else f"{v:.6f}"


_NULL_TOKENS = frozenset({"\\N", "None", "nan", ""})


def _null_cell(v: str) -> str:
    """ch_reader TSV 单元格 NULL 归一（TCP 通道把 NULL 渲染成 'None'，HTTP 路径是 \\N）。"""
    return "\\N" if v in _NULL_TOKENS else v


def _maybe_float(v: str) -> float | None:
    """TSV 单元格 → float（NULL 形态全容忍；非数值/NaN → None）。"""
    if v in _NULL_TOKENS:
        return None
    try:
        f = float(v)
    except ValueError:
        return None
    return None if f != f else f
