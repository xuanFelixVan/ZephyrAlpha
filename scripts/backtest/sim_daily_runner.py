# [BLUEPRINT] MOD-BT-222 | docs/03_modules/_domain_backtest/blueprint.md | §模拟盘判定台账
# [MODULE] scripts.backtest.sim_daily_runner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.data.ch_writer; scripts.backtest.sim_platform_journal（expected_fresh_date 复用）
# [CONSUMERS] c1_backtest.sim_daily_report（判定台账）；c1_backtest.sim_trade_log/sim_pocket_daily
#   （sim_observe 观察平面）；c1_market.judgment_daily_plan/judgment_intraday_market_state（只读消费）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 判定/结算分离（判定列 asof 落行只用 ≤T 数据；结算列 T+1 回填）；丁域只读
#   （judgment_* 表零写入）；方案C 收盘价成交口径（与 sim_paper_ledger 同成本模型，乐观偏差由
#   偏离报告单列监督）； posture 翻译零伪造——计划动作无订单语义时如实记 unexecutable，不编造仓位；
#   judgment_id 确定性派生（重跑=同键覆盖幂等）；synthetic 恒 0
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(落库未确认/全部重放失败); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_sim_daily_runner.py
# [A_module] module_id=MOD-BT-222 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: CLI 接电执行体由管线事件链/排产调用（同 sim 家族
#   sim_paper_ledger/sim_platform_journal 手动 CLI 先例），无常驻循环，非自走时钟
"""模拟盘日链接电执行体（st-sim-launch-20260922 分包2/3）。

三个平面：
- plan-bridge：消费丁线日计划（judgment_daily_plan，只读）+盘中归类（五态），把计划
  姿态翻译为模拟盘姿态并落判定台账行。防御（stand_aside_defense）=唯一可机械执行姿态
  （=空仓）；其余动作无订单语义，如实记 unexecutable(action_not_order_mapped)——
  不伪造信号/仓位（平台铁律），订单映射待 Owner 批后扩。
- e4-replay：E4 观察档（strategy_screen verdict=oos_tested 且有 translated/c4_<hash>_*.py
  翻译件）按 build(start,end) 标准接口重放，尾行目标仓位按方案C 收盘价成交出模拟单
  （mode=sim_observe 观察平面，观察名义本金 100 万 flat；与注册表 sim_daily 平面分离，
  不占分配链额度）。首夜 --limit 控面（自裁 A3），跑通后扩全量。
- report/settle：平台汇总行+累积结算扫描（settle(D) 结算所有 report_date<D 未结算行，
  幂等可重入——错过的日子不丢账，与丁线 maybe_settle_judgment_ledger 同款）。

用法:
  python scripts/backtest/sim_daily_runner.py plan-bridge [--day 2026-09-22]
  python scripts/backtest/sim_daily_runner.py e4-replay [--day 2026-09-22] [--limit 5]
  python scripts/backtest/sim_daily_runner.py report [--day 2026-09-22]
  python scripts/backtest/sim_daily_runner.py settle [--day 2026-09-22]
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import logging
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts" / "backtest"))

import sim_paper_ledger as _ledger  # noqa: E402  常量/写入器同源复用

from schemas.categories.judgment.judgment_daily_plan import (  # noqa: E402
    DATABASE as _DB_JUDGMENT,
)
from schemas.categories.judgment.judgment_daily_plan import (  # noqa: E402
    TABLE_NAME as _T_PLAN,
)
from schemas.categories.judgment.judgment_intraday_market_state import (  # noqa: E402
    TABLE_NAME as _T_STATE,
)

# 表名 SSoT 接线（TABLE-NAME-REGISTRY 治本：schema TABLE_NAME 常量+TableRegistry+复用
# forward_post.fetch_passers，本文件零表名字面量——#ARCH-CH-024）
from schemas.categories.sim_daily_report import TABLE_NAME as _T_REPORT  # noqa: E402
from schemas.categories.sim_pocket_daily import TABLE_NAME as _T_POCKET  # noqa: E402
from schemas.categories.sim_trade_log import TABLE_NAME as _T_TRADELOG  # noqa: E402

_TABLE = _T_REPORT
_COLS = (
    "(report_date, source, subject, judgment_id, asof_ts, input_cutoff_ts, payload,"
    " confidence, inputs_ref, run_id, synthetic, realized_scenario, realized_value,"
    " outcome_ts, eval_method, eval_score, evaluated_at, evaluated_by)"
)
_TRANSLATED_DIR = _ROOT / "scripts" / "backtest" / "translated"
_OBSERVE_NOTIONAL = 1_000_000.0  # 观察档名义本金（flat 口径；不占分配链额度，note 留痕）
_OBSERVE_MODE = "sim_observe"
BUY_COST, SELL_COST = _ledger.BUY_COST, _ledger.SELL_COST  # 同成本模型（方案C）

# ── SQL 集中化（NO-BARE-SQL 治本：语句常量模块级，表名走 schema/registry 常量） ──
SQL_PLAN_FOR_DAY = (
    "SELECT judgment_id, asof_ts, input_cutoff_ts, payload, confidence, subject"
    f" FROM {_DB_JUDGMENT}.{_T_PLAN}"
    " WHERE asof_ts < '{cutoff}' ORDER BY asof_ts DESC LIMIT 20"
)
SQL_STATE_FOR_DAY = (
    f"SELECT judgment_id, asof_ts, payload FROM {_DB_JUDGMENT}.{_T_STATE}"
    " WHERE asof_ts >= '{day} 00:00:00' AND asof_ts < '{day} 16:00:00'"
    " ORDER BY asof_ts DESC LIMIT 1"
)
SQL_OBSERVE_POSITION = (
    "SELECT argMax(cash, ingest_ts), argMax(shares, ingest_ts),"
    " argMax(position_symbol, ingest_ts), argMax(equity, ingest_ts), count()"
    f" FROM {_T_POCKET} FINAL"
    " WHERE strategy_id = '{cid}'"
    f" AND mode = '{_OBSERVE_MODE}'"
)
SQL_POCKETS_FOR_DAY = (
    "SELECT strategy_id, argMax(mode, ingest_ts), argMax(equity, ingest_ts)"
    f" FROM {_T_POCKET} FINAL"
    " WHERE trade_date = '{day}' GROUP BY strategy_id"
)
SQL_EVENTS_FOR_DAY = f"SELECT count() FROM {_T_TRADELOG} FINAL WHERE trade_date = '{{day}}'"
SQL_KLINE_MAX = "SELECT max(trade_date) FROM {kline_index} WHERE symbol = '000300'"
SQL_REPORT_ROW = (
    "SELECT report_date, source, subject, judgment_id, asof_ts, input_cutoff_ts,"
    " payload, confidence, inputs_ref, run_id, synthetic, realized_scenario,"
    " realized_value, outcome_ts, eval_method, eval_score, evaluated_at, evaluated_by"
    f" FROM {_TABLE} FINAL"
    " WHERE report_date = '{day}' AND source = '{source}'"
    " AND subject = '{subject}'"
)
SQL_UNSETTLED = (
    f"SELECT report_date, source, subject, payload FROM {_TABLE} FINAL"
    " WHERE report_date < '{day}' AND evaluated_by = ''"
    " ORDER BY report_date, source, subject"
)
SQL_HEARTBEAT = f"SELECT count() FROM {_T_POCKET} FINAL WHERE trade_date = '{{d}}'"

# 计划动作→模拟盘姿态映射（Owner 2026-09-22 委托裁定，决策卡=
#   docs/_working/sim_launch/01_ruling_plan_mapping_and_orphans.md §表一）：
#   防御=空仓（唯一无歧义姿态）；进攻=trend_follow_no_chase 按 30% 额度建仓 510300 代理、
#   不追高（日涨幅≥1.5%≈1σ 不建仓，顺延观望）；震荡无订单语义维持不执行（原样）。
PLAN_ACTION_POSTURE = {
    "stand_aside_defense": "flat",
    "trend_follow_no_chase": "long_proxy",
}
NO_CHASE_MAX_RET_1D = 0.015  # 不追高阈值：000300 当日涨幅 <1.5% 才建仓（≈1σ，提案参数可修）
PLAN_ENTRY_FRACTION = 0.30  # 进军建仓动用钱包额度比例（提案参数可修）
PLAN_POCKET_ID = "SIM-PLAN-001"  # plan 桥专用钱包（sim_observe 平面，非注册表策略）
PLAN_SYMBOL = "510300"  # 交易代理=300ETF（丁线 plan payload proxy_notes P2a 既定口径）
# 计划树外五态的类推映射（裁决 §表一第 4 行：低迷=空仓、亢奋=减半减险；其余不动）
STATE_EXTRA_POSTURE = {"低迷": "flat", "亢奋": "trim_half"}
# 盘中五态→计划场景键（部分映射：低迷/亢奋不在计划三场景树内，如实记 no_matching_scenario）
STATE_TO_SCENARIO = {"防御": "S2_defense", "进攻": "S1_attack", "震荡": "S3_oscillation"}

SQL_PLAN_INDEX_2D = (
    "SELECT trade_date, argMax(open, ingest_ts), argMax(close, ingest_ts)"
    " FROM {kline_index} WHERE symbol = '000300' AND trade_date IN ('{day}', '{prev}')"
    " GROUP BY trade_date ORDER BY trade_date"
)
SQL_PLAN_ETF_CLOSE = (
    "SELECT argMax(close, ingest_ts) FROM {kline_etf} WHERE symbol LIKE '510300%' AND trade_date = '{day}'"
)
SQL_PLAN_POSITION = (
    "SELECT argMax(cash, ingest_ts), argMax(shares, ingest_ts), argMax(equity, ingest_ts), count()"
    f" FROM {_T_POCKET} FINAL"
    " WHERE strategy_id = '{cid}'"
    f" AND mode = '{_OBSERVE_MODE}'"
)


def _q(sql: str):
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _cutoff_ts(day: str) -> str:
    """判定输入截断（PIT）：T 日 15:00 北京 = 07:00 UTC（收盘数据口径）。"""
    d = date.fromisoformat(day)
    return f"{d.isoformat()} 07:00:00"


def make_judgment_id(day: str, source: str, subject: str) -> str:
    """确定性派生（重跑=同键覆盖幂等；subject 去冒号防 id 歧义）。"""
    return f"SIMP-{day}-{source}-{subject.replace(':', '')}"


def _report_tsv(row: list) -> str:
    from zephyr.data.ch_writer import tsv_escape  # noqa: PLC0415  正典转义（NaN/\x00 全治）

    return "\t".join(tsv_escape(v) for v in row) + "\n"


def write_report_row(row: list) -> None:
    from zephyr.data import ch_writer

    if not ch_writer.write_tsv(_TABLE, _COLS, _report_tsv(row).encode("utf-8")):
        raise RuntimeError("判定台账落库未确认——fail-closed")


def fetch_plan(day: str) -> dict | None:
    """取 T 日计划（next_session_date==day 优先；回退=asof 在 T 日 12:00 前的最新行）。"""
    rows = _q(SQL_PLAN_FOR_DAY.format(cutoff=_cutoff_ts(day)))
    for r in rows:
        try:
            payload = json.loads(r[3])
            if str(payload.get("evidence", {}).get("next_session_date")) == day:
                return _plan_obj(r, payload)
        except Exception:  # noqa: BLE001 — 单行 JSON 损坏不阻断扫描
            continue
    return _plan_obj(rows[0], json.loads(rows[0][3])) if rows else None


def _plan_obj(r, payload: dict) -> dict:
    return {
        "judgment_id": r[0],
        "asof_ts": r[1],
        "cutoff": r[2],
        "payload": payload,
        "confidence": float(r[4]),
        "subject": r[5],
    }


def fetch_realized_state(day: str) -> dict | None:
    """T 日盘中归类（五态 state_label），取当日最新一行。"""
    rows = _q(SQL_STATE_FOR_DAY.format(day=day))
    if not rows:
        return None
    try:
        payload = json.loads(rows[0][2])
    except Exception:  # noqa: BLE001 — 损坏行按无归类处理
        return None
    return {"judgment_id": rows[0][0], "asof_ts": rows[0][1], "state_label": str(payload.get("state_label", ""))}


def posture_for_action(action: str) -> tuple[str, str]:
    """动作→(姿态, 理由)。零伪造：无订单语义的动作如实记 unexecutable。"""
    if action in PLAN_ACTION_POSTURE:
        return PLAN_ACTION_POSTURE[action], f"action={action} 可机械执行"
    return "unexecutable", f"action={action} 无订单语义(action_not_order_mapped)"


def plan_bridge(day: str) -> dict:
    """平面1：日计划→姿态→判定台账行（丁域零写入）。非交易日不落行（台账=一交易日一行）。"""
    from zephyr.data.trading_calendar import is_trading_day

    if not is_trading_day(date.fromisoformat(day)):
        return {"day": day, "written": False, "why": "non_trading_day"}
    plan = fetch_plan(day)
    if plan is None:
        return {"day": day, "written": False, "why": "no_plan_for_day"}
    state = fetch_realized_state(day)
    scenarios = plan["payload"].get("scenarios", [])
    plan_action_by_sid = {s.get("scenario_id"): s.get("action", "") for s in scenarios}
    realized_scenario, realized_action = "", ""

    if state is None:
        posture, reason = "pending_unclassified", "盘中归类未落(五态未出)"
    else:
        realized_scenario = STATE_TO_SCENARIO.get(state["state_label"], "")
        if not realized_scenario:
            # 计划树外五态：类推映射（裁决 §表一第 4 行批准）——低迷=空仓、亢奋=减半减险
            extra = STATE_EXTRA_POSTURE.get(state["state_label"])
            if extra:
                posture, reason = extra, (f"五态 {state['state_label']} 类推映射（决策卡 §表一第 4 行已批）")
                realized_action = f"extrapolated:{extra}"
            else:
                posture, reason = (
                    "pending_owner_mapping",
                    (f"五态 {state['state_label']} 不在计划三场景树(no_matching_scenario)"),
                )
        else:
            realized_action = plan_action_by_sid.get(realized_scenario, "")
            posture, reason = posture_for_action(realized_action)

    subject = plan["subject"]
    payload = {
        "plan_ref": plan["judgment_id"],
        "scenario_count": len(scenarios),
        "realized_state_label": state["state_label"] if state else None,
        "realized_scenario": realized_scenario or None,
        "realized_action": realized_action or None,
        "posture": posture,
        "posture_reason": reason,
    }
    inputs_ref = f"judgment_daily_plan:{plan['judgment_id']}"
    if state:
        inputs_ref += f"; judgment_intraday_market_state:{state['judgment_id']}"
    row = [
        date.fromisoformat(day),
        "plan_bridge",
        subject,
        make_judgment_id(day, "plan_bridge", subject),
        _now_utc().strftime("%Y-%m-%d %H:%M:%S"),
        _cutoff_ts(day),
        json.dumps(payload, ensure_ascii=False),
        plan["confidence"],
        inputs_ref,
        f"simwire-{_now_utc().strftime('%Y%m%d%H%M%S')}",
        0,
        None,
        None,
        None,
        None,
        None,
        None,
        "",
    ]
    write_report_row(row)
    return {"day": day, "written": True, "posture": posture, "realized_scenario": realized_scenario or None}


def e4_candidates() -> list[tuple[str, Path]]:
    """E4 观察档（oos_tested ∧ 有翻译件）：candidate 哈希→translated/c4_<hash>_*.py。"""
    from forward_post import fetch_passers  # noqa: PLC0415  复用既有 oos_tested 查询（表名 SSoT 留在原文件）

    ids = sorted({str(s) for s in fetch_passers(1000)})
    out: list[tuple[str, Path]] = []
    for cid in ids:
        h = cid.split("CAND-", 1)[-1]
        matches = sorted(_TRANSLATED_DIR.glob(f"c4_{h}_*.py"))
        if matches:
            out.append((cid, matches[0]))
    return out


def _observe_position(cid: str) -> tuple[float, float, str, float, bool]:
    """观察钱包当前 (cash, shares, position_symbol, 前一日权益, 是否已有行)。"""
    rows = _q(SQL_OBSERVE_POSITION.format(cid=cid))
    if not rows or int(rows[0][4]) == 0:
        return 0.0, 0.0, "", _OBSERVE_NOTIONAL, False
    return (float(rows[0][0] or 0.0), float(rows[0][1] or 0.0), str(rows[0][2] or ""), float(rows[0][3] or 0.0), True)


@dataclasses.dataclass
class _FillTarget:
    """重放成交上下文（长参数表治本：参数对象化）。"""

    day: str
    cid: str
    target_pos: float
    symbol: str
    px: float
    module_name: str
    run_id: str


def _plan_fill(target: _FillTarget, holding: bool, cash: float, shares: float, pos_sym: str) -> tuple:
    """目标仓位→(signal, events, cash, shares)：方案C 收盘成交决策（纯计算）。"""
    events: list[list] = []
    signal = "cash"
    if target.target_pos > 0 and not holding:
        buy_cost = cash * BUY_COST
        shares = cash / target.px * (1 - BUY_COST) * min(target.target_pos, 1.0)
        cash = 0.0
        signal = "entry"
        events.append(
            [
                target.day,
                target.cid,
                target.symbol,
                "entry",
                shares,
                target.px,
                buy_cost,
                0.0,
                f"E4 重放目标仓位={target.target_pos:.2f}（{target.module_name}）",
                _OBSERVE_MODE,
                target.run_id,
            ]
        )
    elif target.target_pos == 0 and holding:
        proceeds = shares * target.px * (1 - SELL_COST)
        events.append(
            [
                target.day,
                target.cid,
                pos_sym,
                "exit",
                shares,
                target.px,
                shares * target.px * SELL_COST,
                proceeds,
                f"E4 重放目标仓位=0（{target.module_name}）",
                _OBSERVE_MODE,
                target.run_id,
            ]
        )
        cash, shares = proceeds, 0.0
        signal = "exit"
    elif target.target_pos > 0 and holding:
        signal = "holding"
    return signal, events, cash, shares


def replay_one(cid: str, module_path: Path, day: str, run_id: str) -> dict:
    """单候选重放：build() 尾行目标仓位→方案C 收盘成交（entry/exit/hold 标记市场）。"""
    spec = importlib.util.spec_from_file_location(f"simreplay_{cid.replace('-', '_')}", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"翻译件不可加载: {module_path.name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    start = (date.fromisoformat(day) - timedelta(days=420)).isoformat()
    weights, prices = mod.build(start, day)
    if weights is None or len(weights) == 0:
        raise RuntimeError("build() 返回空权重")
    w = weights.iloc[-1]
    targets = {str(c): float(w[c]) for c in w.index if abs(float(w[c])) > 1e-12}
    target_pos = sum(targets.values())
    px_series = prices[sorted(targets)[0]] if targets else prices.iloc[:, -1]
    px = float(px_series.iloc[-1])
    if not math.isfinite(px):
        # NaN/Inf 价格卫兵（2026-09-22 实证：c4 翻译件尾行 NaN 会把 equity 污染成
        # NaN 落库）——此处抛错=本候选记 error 隔离，零写入（写发生在函数尾部）
        raise RuntimeError(f"翻译件尾行价格非有限: px={px}（{module_path.name}）")

    cash, shares, pos_sym, prev_equity, exists = _observe_position(cid)
    # 未开户观察钱包：名义本金起步（无信号日也落开户口径行，权益不得为 0 假死）。
    # 自愈：cash=0∧空仓∧目标空仓 在本成本模型下只有首轮 bug 写入态可产生
    # （exit 后 cash=proceeds>0 恒成立），按名义本金补足（重跑幂等覆盖）。
    if not exists or (shares == 0 and cash <= 0 and target_pos == 0):
        cash, prev_equity = _OBSERVE_NOTIONAL, _OBSERVE_NOTIONAL
    holding = shares > 0
    note = f"E4 观察档翻译件重放（{_OBSERVE_MODE} 平面，名义本金 {_OBSERVE_NOTIONAL:.0f} flat 非注册表）"
    fill = _FillTarget(
        day=day,
        cid=cid,
        target_pos=target_pos,
        symbol=sorted(targets)[0] if targets else "",
        px=px,
        module_name=module_path.name,
        run_id=run_id,
    )
    signal, events, cash, shares = _plan_fill(fill, holding, cash, shares, pos_sym)
    pos_val = shares * px
    equity = cash + pos_val
    pocket = [
        day,
        cid,
        _OBSERVE_NOTIONAL,
        round(cash, 2),
        sorted(targets)[0] if target_pos > 0 else "",
        round(shares, 2),
        round(pos_val, 2),
        round(equity, 2),
        round(equity - prev_equity, 2),
        signal,
        _OBSERVE_MODE,
        run_id,
        note,
    ]
    _write_observe(pocket, events)
    return {
        "cid": cid,
        "target_position": target_pos,
        "signal": signal,
        "module": module_path.name,
        "events": len(events),
        "equity": round(equity, 2),
    }


def _write_observe(pocket: list, events: list[list]) -> None:
    from zephyr.data import ch_writer
    from zephyr.data.ch_writer import tsv_escape  # noqa: PLC0415  正典转义（防克隆，FUNCTION-DUP 清偿）

    p_cols = _ledger._COLS  # 同一表结构，写入器同源（事件溯源平面分离靠 mode 列）
    tsv = "\t".join(tsv_escape(v) for v in pocket) + "\n"
    if not ch_writer.write_tsv(_T_POCKET, p_cols, tsv.encode("utf-8")):
        raise RuntimeError("观察钱包落库未确认——fail-closed")
    if events:
        ev_cols = (
            "(trade_date, strategy_id, symbol, action, shares, price, cost_paid, cash_after,"
            " signal_reason, mode, run_id)"
        )
        ev_tsv = "\n".join("\t".join(tsv_escape(v) for v in r) for r in events) + "\n"
        if not ch_writer.write_tsv(_T_TRADELOG, ev_cols, ev_tsv.encode("utf-8")):
            raise RuntimeError("观察事件落库未确认——fail-closed")


def e4_replay(day: str, limit: int) -> dict:
    """平面2：E4 观察档批量重放（单条失败收集不连坐；全失败才 fail-closed）。"""
    cands = e4_candidates()[: max(limit, 0)]
    out: dict = {"replayed": [], "errors": [], "day": day}
    run_id = f"sim-observe-{_now_utc().strftime('%Y%m%d%H%M%S')}"
    for cid, module_path in cands:
        try:
            res = replay_one(cid, module_path, day, run_id)
            out["replayed"].append(res)
            subject = cid
            row = [
                date.fromisoformat(day),
                "e4_replay",
                subject,
                make_judgment_id(day, "e4_replay", subject),
                _now_utc().strftime("%Y-%m-%d %H:%M:%S"),
                _cutoff_ts(day),
                json.dumps(res, ensure_ascii=False),
                1.0,
                f"translated:{res['module']}; strategy_screen:{cid}",
                run_id,
                0,
                None,
                None,
                None,
                None,
                None,
                None,
                "",
            ]
            write_report_row(row)
        except Exception as exc:  # noqa: BLE001 — 逐候选隔离（自裁 A5：全失败才 fail-closed）
            out["errors"].append({"cid": cid, "error": f"{type(exc).__name__}: {str(exc)[:160]}"})
    if cands and not out["replayed"]:
        raise RuntimeError(f"E4 重放全失败（fail-closed）: {out['errors']}")
    return out


def _plan_decision(posture: str, holding: bool, ret_1d: float | None, has_px: bool) -> str:
    """姿态→订单动作（纯函数）：entry/hold/trim_half/exit/wait/none。

    long_proxy 不追高：当日涨幅缺失或 ≥NO_CHASE_MAX_RET_1D → wait（顺延观望，不追）。
    任何输入不完整（价格缺失）→ none（fail-visible 不下单）。
    """
    if posture in ("flat", "trim_half") and not holding:
        return "none"
    if posture == "flat":
        return "exit"
    if posture == "trim_half":
        return "trim_half"
    if posture == "long_proxy":
        if not has_px:
            return "none"
        if holding:
            return "hold"
        if ret_1d is None or ret_1d >= NO_CHASE_MAX_RET_1D:
            return "wait"
        return "entry"
    return "none"


def _plan_position(cid: str) -> tuple[float, float, float, bool]:
    """plan 钱包 (cash, shares, equity, 是否已有行)。"""
    rows = _q(SQL_PLAN_POSITION.format(cid=cid))
    if not rows or int(rows[0][3]) == 0:
        return 0.0, 0.0, _OBSERVE_NOTIONAL, False
    return (float(rows[0][0] or 0.0), float(rows[0][1] or 0.0), float(rows[0][2] or 0.0), True)


def plan_execute(day: str) -> dict:
    """平面4：日计划姿态→SIM-PLAN-001 钱包模拟单（裁决 §表一执行体）。

    数据：000300（不追高阈值）+510300 收盘价（成交价，kline_etf_daily）。
    方案C 收盘价成交、账本同款成本模型；任何数据缺失→不下单并如实留痕。
    """
    from zephyr.data.table_registry import get_registry  # noqa: PLC0415

    # 当日 plan_bridge 行（无行=先跑 plan-bridge）
    row = _row_by_id(day, "plan_bridge", "index:000300.SH")
    if row is None:
        br = plan_bridge(day)
        if not br.get("written"):
            return {"day": day, "executed": False, "why": br.get("why", "no_plan_row")}
        row = _row_by_id(day, "plan_bridge", "index:000300.SH")
        if row is None:
            return {"day": day, "executed": False, "why": "plan_row_missing"}
    payload = json.loads(row[6])
    posture = str(payload.get("posture", ""))

    cash, shares, prev_equity, exists = _plan_position(PLAN_POCKET_ID)
    if not exists:
        cash, prev_equity = _OBSERVE_NOTIONAL, _OBSERVE_NOTIONAL
    holding = shares > 0

    # 不追高阈值输入：000300 当日/昨收
    prev = (date.fromisoformat(day) - timedelta(days=14)).isoformat()
    k_idx = get_registry().table("market_index_kline")
    k_etf = get_registry().table("market_kline_etf_daily")
    rows2 = _q(SQL_PLAN_INDEX_2D.format(kline_index=k_idx, day=day, prev=prev))
    ret_1d = None
    if len(rows2) == 2:
        prev_close = float(rows2[0][2])
        today_close = float(rows2[1][2])
        if prev_close > 0:
            ret_1d = today_close / prev_close - 1.0
    # 成交价：510300 收盘
    rows3 = _q(SQL_PLAN_ETF_CLOSE.format(kline_etf=k_etf, day=day))
    px = float(rows3[0][0]) if rows3 and rows3[0][0] is not None else None
    has_px = px is not None and math.isfinite(px)

    action = _plan_decision(posture, holding, ret_1d, has_px)
    events: list[list] = []
    run_id = f"plan-exec-{_now_utc().strftime('%Y%m%d%H%M%S')}"
    cash2, shares2 = cash, shares
    if action == "entry":
        spend = cash * PLAN_ENTRY_FRACTION
        buy_cost = spend * BUY_COST
        shares2 = spend / px * (1 - BUY_COST)
        cash2 = cash - spend
        events.append(
            [
                day,
                PLAN_POCKET_ID,
                PLAN_SYMBOL,
                "entry",
                shares2,
                px,
                buy_cost,
                cash2,
                f"plan 进军建仓 30% 额度（不追高 ret={ret_1d:.4f}）",
                _OBSERVE_MODE,
                run_id,
            ]
        )
    elif action == "exit":
        proceeds = shares * px * (1 - SELL_COST)
        events.append(
            [
                day,
                PLAN_POCKET_ID,
                PLAN_SYMBOL,
                "exit",
                shares,
                px,
                shares * px * SELL_COST,
                proceeds,
                "plan 防御/低迷空仓",
                _OBSERVE_MODE,
                run_id,
            ]
        )
        cash2, shares2 = proceeds, 0.0
    elif action == "trim_half":
        half = shares / 2.0
        proceeds = half * px * (1 - SELL_COST)
        events.append(
            [
                day,
                PLAN_POCKET_ID,
                PLAN_SYMBOL,
                "exit",
                half,
                px,
                half * px * SELL_COST,
                proceeds,
                "plan 亢奋减半减险",
                _OBSERVE_MODE,
                run_id,
            ]
        )
        cash2, shares2 = cash + proceeds, shares - half
    signal = {"entry": "entry", "exit": "exit", "trim_half": "exit", "hold": "holding"}.get(action, "cash")
    pos_val = shares2 * px if has_px else 0.0
    equity = cash2 + pos_val
    note = f"plan 桥执行（姿态={posture}，510300 代理方案C 收盘价，名义本金 100 万 flat）"
    pocket = [
        day,
        PLAN_POCKET_ID,
        _OBSERVE_NOTIONAL,
        round(cash2, 2),
        PLAN_SYMBOL if shares2 > 0 else "",
        round(shares2, 2),
        round(pos_val, 2),
        round(equity, 2),
        round(equity - prev_equity, 2),
        signal,
        _OBSERVE_MODE,
        run_id,
        note,
    ]
    _write_observe(pocket, events)
    subject = PLAN_POCKET_ID
    row_out = [
        date.fromisoformat(day),
        "plan_execute",
        subject,
        make_judgment_id(day, "plan_execute", subject),
        _now_utc().strftime("%Y-%m-%d %H:%M:%S"),
        _cutoff_ts(day),
        json.dumps(
            {
                "posture": posture,
                "action": action,
                "ret_1d": ret_1d,
                "px": px,
                "events": len(events),
                "equity": round(equity, 2),
            },
            ensure_ascii=False,
        ),
        1.0,
        f"plan_bridge:{make_judgment_id(day, 'plan_bridge', 'index:000300.SH')}",
        run_id,
        0,
        None,
        None,
        None,
        None,
        None,
        None,
        "",
    ]
    write_report_row(row_out)
    return {
        "day": day,
        "executed": True,
        "posture": posture,
        "action": action,
        "ret_1d": ret_1d,
        "px": px,
        "events": len(events),
        "equity": round(equity, 2),
    }


def report(day: str) -> dict:
    """平面3：平台汇总行（三平面钱包计数+新鲜度+在册外钱包哨兵）。"""
    from zephyr.data.trading_calendar import is_trading_day

    pockets = _q(SQL_POCKETS_FOR_DAY.format(day=day))
    reg_ids = {e["strategy_id"] for e in _ledger.registry_sim_entries()}
    by_mode: dict = {}
    unregistered: list[str] = []
    for sid, mode, equity in pockets:
        by_mode[str(mode)] = by_mode.get(str(mode), 0) + 1
        if str(mode) == "sim_daily" and sid not in reg_ids and sid != _ledger.STRATEGY_ID:
            unregistered.append(str(sid))
    events = _q(SQL_EVENTS_FOR_DAY.format(day=day))
    from zephyr.data.table_registry import get_registry  # noqa: PLC0415

    kline_index = get_registry().table("market_index_kline")
    kline_max = _q(SQL_KLINE_MAX.format(kline_index=kline_index))[0][0]
    import sim_platform_journal as _journal

    fresh_base = _journal.expected_fresh_date(day)
    fresh_ok = 1 if (kline_max and str(kline_max) >= fresh_base) else 0
    payload = {
        "pockets_by_mode": by_mode,
        "event_count": int(events[0][0]),
        "fresh_ok": fresh_ok,
        "fresh_base": fresh_base,
        "kline_max": str(kline_max),
        "unregistered_wallets": unregistered,
        "heartbeat_ok": 1 if pockets else 0,
        "trading_day": 1 if is_trading_day(date.fromisoformat(day)) else 0,
    }
    subject = "platform"
    row = [
        date.fromisoformat(day),
        "platform",
        subject,
        make_judgment_id(day, "platform", subject),
        _now_utc().strftime("%Y-%m-%d %H:%M:%S"),
        _cutoff_ts(day),
        json.dumps(payload, ensure_ascii=False),
        1.0,
        "sim_pocket_daily; sim_trade_log; kline_index(000300)",
        f"simwire-{_now_utc().strftime('%Y%m%d%H%M%S')}",
        0,
        None,
        None,
        None,
        None,
        None,
        None,
        "",
    ]
    write_report_row(row)
    return {"day": day, "written": True, **payload}


def _row_by_id(day: str, source: str, subject: str) -> list | None:
    rows = _q(SQL_REPORT_ROW.format(day=day, source=source, subject=subject))
    return list(rows[0]) if rows else None


def _settle_row(
    old: list, realized_scenario: str | None, realized_value: dict, eval_method: str, eval_score: float | None
) -> list:
    """结算=同键重写（ReplacingMergeTree 覆盖），只填结算列+evaluated_by。"""
    now = _now_utc()
    return [
        old[0],
        old[1],
        old[2],
        old[3],
        old[4],
        old[5],
        old[6],
        old[7],
        old[8],
        f"settle-{now.strftime('%Y%m%d%H%M%S')}",
        old[10],
        realized_scenario,
        json.dumps(realized_value, ensure_ascii=False),
        now.strftime("%Y-%m-%d %H:%M:%S"),
        eval_method,
        eval_score,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        "sim_settler",
    ]


def settle(day: str) -> dict:
    """累积结算扫描：结算所有 report_date < day 且未结算的行（幂等可重入）。"""
    rows = _q(SQL_UNSETTLED.format(day=day))
    settled, unresolvable = 0, 0
    for r in rows:
        d, source, subject = str(r[0]), str(r[1]), str(r[2])
        old = _row_by_id(d, source, subject)
        if old is None:
            continue
        payload = json.loads(old[6]) if old[6] else {}
        if source == "plan_bridge":
            state = fetch_realized_state(d)
            label = state["state_label"] if state else None
            scenario = STATE_TO_SCENARIO.get(label or "", "")
            if not scenario:
                out_row = _settle_row(old, label, {"state_label": label}, "unresolvable", None)
                unresolvable += 1
            else:
                expected_flat = payload.get("posture") == "flat"
                actual_flat = scenario == "S2_defense"
                score = 1.0 if expected_flat == actual_flat else 0.0
                out_row = _settle_row(
                    old, scenario, {"state_label": label, "scenario": scenario}, "posture_check", score
                )
        elif source == "e4_replay":
            target = float(payload.get("target_position", 0.0))
            cash, shares, _sym, _prev, _exists = _observe_position(subject)
            actual_pos = 1.0 if shares > 0 else 0.0
            score = 1.0 if (target > 0) == (actual_pos > 0) else 0.0
            out_row = _settle_row(
                old,
                None,
                {"target_position": target, "actual_position": actual_pos, "cash": round(cash, 2)},
                "replay_consistent",
                score,
            )
        elif source == "plan_execute":
            target = json.loads(old[6]).get("action")
            cash, shares, _prev, _exists = _plan_position(subject)
            actual = {
                "entry": "hold",
                "hold": "hold",
                "trim_half": "holding",
                "exit": "cash",
                "wait": "cash",
                "none": "cash",
            }.get(str(target), "cash")
            consistent = (shares > 0) == (actual in ("hold", "holding"))
            out_row = _settle_row(
                old,
                None,
                {"action": target, "shares_now": round(shares, 2)},
                "replay_consistent",
                1.0 if consistent else 0.0,
            )
        else:  # platform
            pockets = _q(SQL_HEARTBEAT.format(d=d))
            hb = 1 if int(pockets[0][0]) > 0 else 0
            out_row = _settle_row(old, None, {"heartbeat": hb}, "heartbeat_check", float(hb))
        write_report_row(out_row)
        settled += 1
    return {"settled": settled, "unresolvable": unresolvable, "sweep_before": day}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘日链接电执行体（plan桥/E4重放/日报/结算）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan-bridge", "plan-execute", "e4-replay", "report", "settle"):
        p = sub.add_parser(name)
        p.add_argument("--day", default=date.today().strftime("%Y-%m-%d"))
        if name == "e4-replay":
            p.add_argument("--limit", type=int, default=5, help="首夜控面（自裁 A3），跑通后扩全量")
    args = ap.parse_args()
    day = args.day
    if args.cmd == "plan-bridge":
        out = plan_bridge(day)
    elif args.cmd == "e4-replay":
        out = e4_replay(day, args.limit)
    elif args.cmd == "plan-execute":
        out = plan_execute(day)
    elif args.cmd == "report":
        out = report(day)
    else:
        out = settle(day)
    print(json.dumps(out, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
