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
# [TESTS] tests/backtest/test_sim_daily_runner.py; tests/backtest/test_bridge_execute.py
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
  python scripts/backtest/sim_daily_runner.py bridge-execute [--day 2026-09-28] [--orders-file P] [--dry-run]

- bridge-execute：SimBridgeExecute 执行腿（F56 断腿重建，run_sim_bridge_execute_daily.ps1
  09:35/13:05 调用点）。链路=委托批次文件→解析（坏行跳过计数）→窗口闸→幂等预扫
  （批次指纹回执存在=SKIP 不重复下单）→正门装配（三闸 OrderManager+R-H5E-1 风控闸，
  env=sim 恒定 real 恒不接=裁定#338⑤）→经 QMT 文件桥逐单执行→执行回执落盘（文件面）。
  退出码 0=成功/honest SKIP、4=有单失败、1=环境失败。处方=delivery_report_20260923 §3
  （限价=桥盘口 买=ask1/卖=bid1、quote mtime>900s 或零盘口=fail-visible 不下单）。
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import hashlib
import importlib.util
import io
import json
import logging
import math
import sys
from datetime import date, datetime, timedelta, timezone
from datetime import time as dtime
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts" / "backtest"))
sys.path.insert(0, str(_ROOT / "scripts"))  # start_paper_session 正门装配件（bridge-execute 延迟导入用）

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


def replay_one(cid: str, module_path: Path, day: str, run_id: str, *, state_dir: Path | None = None) -> dict:
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

    # ── 风控闸（[整装回测备战W1] 接线②）：六态机唯一仲裁，risk_blocked 不进重放成交 ──
    risk = _evaluate_sim_risk(day, equity=prev_equity, state_dir=state_dir)
    if not risk["allow_new_position"]:
        liquidation = None
        if risk["kill_switch_active"] or risk["state"] == "KILL":
            liquidation = _apply_sim_kill_switch_liquidation(
                day,
                _SimPos(cid=cid, cash=cash, shares=shares, pos_symbol=pos_sym, px=px),
                reason=f"E4 {risk['state']}",
                state_dir=state_dir,
                prev_equity=prev_equity,
            )
        return {
            "cid": cid,
            "target_position": target_pos,
            "signal": "risk_blocked",
            "module": module_path.name,
            "events": 0,
            "equity": round(cash + shares * px, 2),
            "risk": risk,
            "liquidation": liquidation,
        }

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


def e4_replay(day: str, limit: int, *, state_dir: Path | None = None) -> dict:
    """平面2：E4 观察档批量重放（单条失败收集不连坐；全失败才 fail-closed）。

    风控闸（[整装回测备战W1] 接线②）：逐候选过 _evaluate_sim_risk，拒绝者记
    risk_blocked 不进重放成交；KILL 追加熔断清算台账行。
    """
    cands = e4_candidates()[: max(limit, 0)]
    out: dict = {"replayed": [], "errors": [], "day": day}
    run_id = f"sim-observe-{_now_utc().strftime('%Y%m%d%H%M%S')}"
    for cid, module_path in cands:
        try:
            res = replay_one(cid, module_path, day, run_id, state_dir=state_dir)
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


def plan_execute(day: str, *, state_dir: Path | None = None) -> dict:
    """平面4：日计划姿态→SIM-PLAN-001 钱包模拟单（裁决 §表一执行体）。

    数据：000300（不追高阈值）+510300 收盘价（成交价，kline_etf_daily）。
    方案C 收盘价成交、账本同款成本模型；任何数据缺失→不下单并如实留痕。
    风控闸（[整装回测备战W1]）：_evaluate_sim_risk 六态机唯一仲裁+kill switch
    禁旁路；拒绝当日禁开仓，KILL 追加熔断清算台账行。
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

    # ── 风控闸（[整装回测备战W1] 接线①）：六态机唯一仲裁，禁旁路 ──
    risk = _evaluate_sim_risk(day, equity=prev_equity, state_dir=state_dir)
    if not risk["allow_new_position"]:
        return _sim_risk_blocked(
            day,
            _SimPos(
                cid=PLAN_POCKET_ID,
                cash=cash,
                shares=shares,
                pos_symbol=PLAN_SYMBOL if shares > 0 else "",
                px=px,
            ),
            source="plan_execute",
            subject=PLAN_POCKET_ID,
            risk=risk,
            state_dir=state_dir,
        )

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


# ══ bridge-execute（F56 断腿重建：SimBridgeExecute 执行腿，处方=delivery_report_20260923 §3）══
# 语义：读委托批次文件→正门装配（三闸 OrderManager+R-H5E-1 风控闸）→env=sim 文件桥逐单执行→
# 写执行回执（文件面）。退出码 0=成功/honest SKIP、4=有单失败、1=环境失败（装配/连接失败）。
_BRIDGE_DATA_DIR = _ROOT / "data" / "runtime" / "qmt_bridge"
_BRIDGE_ORDERS_DIR = _BRIDGE_DATA_DIR / "orders"
_BRIDGE_RECEIPTS_DIR = _BRIDGE_DATA_DIR / "receipts"
_BRIDGE_ENV = "sim"  # env=sim ONLY——real 账户=Owner 门（裁定 #338⑤），装配 enable_real 恒 False
_BRIDGE_BROKER_ID = "qmt_sim"
_BRIDGE_STRATEGY_ID = "bridge-execute"
_BRIDGE_SIGNAL_BATCH_PREFIX = "plan-bridge"  # 幂等键批次号（处方 §3：signal_batch=plan-bridge-<day>）
_BRIDGE_TRADE_WINDOWS = ((dtime(9, 30), dtime(11, 25)), (dtime(13, 0), dtime(14, 55)))  # 处方 §3 窗口闸
_BRIDGE_QUOTE_STALE_SECONDS = 900.0  # 处方：quote mtime>900s=fail-visible 不下单（禁旧价）
_BRIDGE_RISK_STATE_DIR = _ROOT / "data" / "runtime" / "state"  # 与 start_paper_session 同源（kill switch SSoT）


class BridgeEnvError(RuntimeError):
    """桥环境失败（装配/连接失败=非订单语义，退出码 1；订单语义失败=回执 failed 行，退出码 4）。"""


def _now_cn() -> datetime:
    from zoneinfo import ZoneInfo  # noqa: PLC0415  stdlib 延迟导入（本文件延迟面同风格）

    return datetime.now(ZoneInfo("Asia/Shanghai"))


def in_bridge_trade_window(now: datetime) -> bool:
    """纯函数：北京时 now 是否落在桥执行窗口（09:30-11:25 / 13:00-14:55，处方 §3）。"""
    t = now.time()
    return any(lo <= t <= hi for lo, hi in _BRIDGE_TRADE_WINDOWS)


def parse_orders_csv(text: str) -> tuple[list[dict], list[str]]:
    """委托批次文件解析（纯函数）：返回 (合法单列表, 坏行原因列表)。

    行格式 ``symbol,action,shares[,limit_px]``（action∈buy/sell，symbol 用桥格式如
    510300.SH；首条非空行以 symbol 开头=表头跳过）。坏行（列数/非数字/未知动作/
    非正值）跳过计数不阻断——如实回执，不伪造成功（平台铁律）。
    """
    rows: list[dict] = []
    bad: list[str] = []
    seen_data_line = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if not seen_data_line and parts and parts[0].lower() == "symbol":
            seen_data_line = True  # 表头行
            continue
        seen_data_line = True
        if len(parts) not in (3, 4):
            bad.append(f"line{lineno}:columns={len(parts)}")
            continue
        symbol, action = parts[0], parts[1].lower()
        if action not in ("buy", "sell"):
            bad.append(f"line{lineno}:action={parts[1]}")
            continue
        try:
            shares = int(parts[2])
            limit_px = float(parts[3]) if len(parts) == 4 and parts[3] else None
        except ValueError:
            bad.append(f"line{lineno}:non_numeric")
            continue
        if not symbol or shares <= 0 or (limit_px is not None and limit_px <= 0):
            bad.append(f"line{lineno}:non_positive_value")
            continue
        rows.append({"symbol": symbol, "action": action, "shares": shares, "limit_px": limit_px})
    return rows, bad


def _bridge_batch_id(day: str, text: str) -> str:
    """批次指纹（规范化非空行 sha256 前 12 位）——同批文件重跑=同 id，回执存在即幂等 SKIP。"""
    normalized = "\n".join(ln.strip() for ln in text.splitlines() if ln.strip())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"bridge-{day}-{digest[:12]}"


def _new_paper_order_manager():
    """正门 OrderManager（F62/M7-06 禁裸构造：C-004 三闸注入，assemble_session 同源装配件）。"""
    from start_paper_session import _assemble_paper_order_manager  # noqa: PLC0415  延迟导入防重 import 面

    return _assemble_paper_order_manager()


def _build_bridge_assembly(order_manager, state_dir: Path | None = None):
    """env=sim 桥装配（R-H5E-1 风控闸注入=裁定#338⑤；enable_real 恒 False=实盘腿零接）。"""
    from zephyr.ex_core.adapters.qmt_file_bridge_integration import QmtFileBridgeAssembly  # noqa: PLC0415
    from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge  # noqa: PLC0415
    from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator  # noqa: PLC0415
    from zephyr.shared.state_store import JsonStateStore  # noqa: PLC0415

    validator = DefaultRiskValidator(state_store=JsonStateStore(state_dir or _BRIDGE_RISK_STATE_DIR))
    return QmtFileBridgeAssembly(
        order_manager,
        enable_real=False,
        enable_sim=True,
        sync_interval=3.0,
        risk_validator=RiskValidationBridge(validator),
    )


def _connect_bridge_world(order_manager, state_dir: Path | None = None):
    """装配+连接 env=sim 桥与反向行情桥。返回 (assembly, quote_provider|None)。

    broker 连接失败=BridgeEnvError（退出码 1）；quote 面失败=返回 None
    （显式限价单仍可执行，盘口推导单逐单 fail-visible——处方 §3 拒单语义）。
    """
    assembly = _build_bridge_assembly(order_manager, state_dir=state_dir)
    results = assembly.connect_all()
    if not results.get(_BRIDGE_BROKER_ID):
        assembly.disconnect_all()
        raise BridgeEnvError("qmt_sim broker connect 失败（终端未就绪/桥目录不可达）")
    quote_provider = None
    try:
        from zephyr.ex_core.adapters.qmt_file_bridge_quote import QmtFileBridgeQuoteProvider  # noqa: PLC0415

        quote_provider = QmtFileBridgeQuoteProvider(env=_BRIDGE_ENV, stale_seconds=_BRIDGE_QUOTE_STALE_SECONDS)
        quote_provider.connect()
    except Exception:  # noqa: BLE001  quote 面 fail-visible：坏天气不阻断显式价单
        quote_provider = None
    return assembly, quote_provider


def _resolve_bridge_limit_px(row: dict, quote_provider) -> tuple[Decimal | None, str]:
    """委托行→(限价, 价格来源)。显式价直用；否则买=ask1/卖=bid1（处方 §3 禁旧价）；
    quote 缺失/超龄/零盘口/异常=（None, 原因）——fail-visible 该单不下。"""
    if row["limit_px"] is not None:
        return Decimal(str(row["limit_px"])), "explicit"
    if quote_provider is None:
        return None, "quote_unavailable"
    try:
        if not quote_provider.is_fresh():
            return None, "quote_stale"
        snap = quote_provider.get_quote(row["symbol"])
        if snap is None:
            return None, "quote_missing"
        px = snap.ask1 if row["action"] == "buy" else snap.bid1
    except Exception:  # noqa: BLE001  行情面任何异常都按无价处理（不下单不猜价）
        return None, "quote_error"
    if px is None or px <= 0:
        return None, "quote_zero_spread"
    return px, "bridge_quote"


def _submit_bridge_batch(order_manager, rows: list[dict], quote_provider) -> list[dict]:
    """逐单 create+submit（幂等键由 OrderManager 批次上下文派生=R-L3；单失败隔离不连坐）。

    返回回执行列表：status∈submitted/skipped_no_price/failed。
    """
    from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType  # noqa: PLC0415

    receipts: list[dict] = []
    for row in rows:
        px, px_source = _resolve_bridge_limit_px(row, quote_provider)
        rec = {
            "symbol": row["symbol"],
            "action": row["action"],
            "shares": row["shares"],
            "limit_px": str(px) if px is not None else "",
            "px_source": px_source,
            "order_id": "",
            "status": "",
            "error": "",
        }
        if px is None:
            rec.update(status="skipped_no_price", error=px_source)
            receipts.append(rec)
            continue
        try:
            order = order_manager.create_order(
                symbol=row["symbol"],
                strategy_id=_BRIDGE_STRATEGY_ID,
                side=OrderSide.BUY if row["action"] == "buy" else OrderSide.SELL,
                order_type=OrderType.LIMIT,
                quantity=Decimal(str(row["shares"])),
                limit_price=px,
                broker_id=_BRIDGE_BROKER_ID,
            )
            rec["order_id"] = str(order_manager.submit_order(order.order_id, _BRIDGE_BROKER_ID))
            rec["status"] = "submitted"
        except Exception as exc:  # noqa: BLE001  单失败隔离计数（处方 §3 fail-visible）
            rec["status"] = "failed"
            rec["error"] = f"{type(exc).__name__}: {str(exc)[:120]}"
        receipts.append(rec)
    return receipts


def _write_bridge_receipt(path: Path, day: str, batch_id: str, receipts: list[dict]) -> None:
    """执行回执落盘（文件面，safe_write CAS 原子写）。回执存在=同批已处理（幂等标记）。"""
    from zephyr.shared.io.file_utils import safe_write_text  # noqa: PLC0415  热文件写入纪律同源

    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=(
            "day",
            "batch_id",
            "submitted_at",
            "symbol",
            "action",
            "shares",
            "limit_px",
            "px_source",
            "order_id",
            "status",
            "error",
        ),
        lineterminator="\n",  # LF 落盘（safe_write 回读=universal newlines，CRLF 会哈希错位）
    )
    submitted_at = _now_utc().strftime("%Y-%m-%d %H:%M:%S")
    writer.writeheader()
    for rec in receipts:
        writer.writerow({"day": day, "batch_id": batch_id, "submitted_at": submitted_at, **rec})
    path.parent.mkdir(parents=True, exist_ok=True)
    result = safe_write_text(path, buf.getvalue())
    if not result.written:
        # 路径不进错误消息文本（MSG-EXPOSURE 5.99.20：safe_write 审计已留痕路径）
        raise RuntimeError("执行回执落盘未确认——fail-closed（safe_write 拒写/回读不符，路径见 safe_write 审计）")


def bridge_execute(
    day: str,
    orders_file: str | None = None,
    dry_run: bool = False,
    *,
    receipts_dir: Path | None = None,
    state_dir: Path | None = None,
) -> dict:
    """bridge-execute 主流程（SimBridgeExecute 执行腿本体，ps1 09:35/13:05 调用点）。

    链路：委托批次文件（默认 data/runtime/qmt_bridge/orders/orders_<day>.csv）→
    解析（坏行跳过计数）→窗口闸→幂等预扫（批次指纹回执存在=SKIP）→
    正门装配（三闸 OrderManager+R-H5E-1 env=sim 桥）→逐单执行→执行回执落盘。
    dry-run 只解析+打印计划，不装配、不下单、不落任何文件。

    退出码（ps1 契约）：0=成功/honest SKIP、4=有单失败、1=环境失败。
    """
    path = Path(orders_file) if orders_file else _BRIDGE_ORDERS_DIR / f"orders_{day}.csv"
    out: dict = {"day": day, "orders_file": str(path), "env": _BRIDGE_ENV, "dry_run": dry_run}
    if not path.exists():
        return {**out, "executed": False, "why": "orders_file_missing", "exit_code": 0}
    text = path.read_text(encoding="utf-8")
    rows, bad = parse_orders_csv(text)
    out["bad_rows"] = bad
    if not rows:
        return {**out, "executed": False, "why": "no_valid_orders", "exit_code": 0}
    if not in_bridge_trade_window(_now_cn()):
        return {**out, "executed": False, "why": "outside_trade_window", "exit_code": 0}
    batch_id = _bridge_batch_id(day, text)
    receipt_path = (receipts_dir or _BRIDGE_RECEIPTS_DIR) / f"{batch_id}.csv"
    out["batch_id"] = batch_id
    out["receipt"] = str(receipt_path)
    if receipt_path.exists():
        # 幂等（处方 §3：同批重跑不二次下单）——回执存在即 SKIP，绝不重复执行
        return {**out, "executed": False, "why": "already_executed_idempotent_skip", "exit_code": 0}
    if dry_run:
        return {**out, "executed": False, "why": "dry_run_no_action", "would_submit": len(rows), "exit_code": 0}
    # ── 两级风险闸（[整装回测备战W1] 接线③）：级1 kill switch 整批拒；
    # 级2 六态机 defensive_only 拒新开仓（buy）、减险单（sell）放行 ──
    gate = _bridge_risk_gate(rows, state_dir=state_dir)
    out["risk_gate"] = {
        "kill_switch_active": gate["kill_switch_active"],
        "drawdown_state": gate["drawdown_state"],
        "blocked_rows": len(gate["blocked_rows"]),
    }
    if gate["kill_switch_active"]:
        return {**out, "executed": False, "why": "risk_blocked_kill_switch", "exit_code": 0}
    rows = gate["allowed_rows"]
    if not rows:
        return {**out, "executed": False, "why": "risk_blocked_drawdown_halt", "exit_code": 0}
    order_manager = _new_paper_order_manager()  # 正门装配：禁裸 OrderManager()（F62/M7-06）
    order_manager.begin_signal_batch(f"{_BRIDGE_SIGNAL_BATCH_PREFIX}-{day}", day)  # R-L3 幂等键批次上下文
    try:
        assembly, quote_provider = _connect_bridge_world(order_manager, state_dir=state_dir)
    except BridgeEnvError as exc:
        return {**out, "executed": False, "why": "bridge_env_failure", "error": str(exc)[:200], "exit_code": 1}
    try:
        receipts = _submit_bridge_batch(order_manager, rows, quote_provider)
    finally:
        assembly.disconnect_all()
    failed = sum(1 for r in receipts if r["status"] != "submitted")
    _write_bridge_receipt(receipt_path, day, batch_id, receipts)
    out["submitted"] = len(receipts) - failed
    out["failed"] = failed
    out["receipts"] = receipts
    out["executed"] = True
    out["exit_code"] = 4 if failed else 0  # 0=全成；4=有单失败（任务契约）
    return out


def _bridge_risk_gate(rows: list[dict], *, state_dir: Path | None = None) -> dict:
    """bridge-execute 下单前两级风险闸（[整装回测备战W1] 三路径接线③）。

    级1：kill switch 闩（DefaultRiskValidator.kill_switch_active，禁旁路）→ 整批拒；
    级2：回撤六态机（DrawdownStateMachine）defensive_only（CRISIS/KILL）→ 拒新开仓
    （buy），减险单（sell）放行——风险只减不增。

    Returns:
        {"kill_switch_active": bool, "drawdown_state": str,
         "allowed_rows": list, "blocked_rows": list}
    """
    validator, machine = _assemble_sim_risk_layer(state_dir)
    if validator.kill_switch_active:
        return {
            "kill_switch_active": True,
            "drawdown_state": machine.current.value,
            "allowed_rows": [],
            "blocked_rows": list(rows),
        }
    if machine.defensive_only:
        return {
            "kill_switch_active": False,
            "drawdown_state": machine.current.value,
            "allowed_rows": [r for r in rows if r["action"] == "sell"],
            "blocked_rows": [r for r in rows if r["action"] != "sell"],
        }
    return {
        "kill_switch_active": False,
        "drawdown_state": machine.current.value,
        "allowed_rows": list(rows),
        "blocked_rows": [],
    }


# ══ 风控接线（[整装回测备战W1]：三路径风控闸，装配同构 start_paper_session:442）══
_SIM_PEAK_EQUITY_NS = "sim_peak_equity"  # 峰值权益 running max（回撤输入）


def _assemble_sim_risk_layer(state_dir: Path | None = None):
    """风控层装配（同构 scripts/start_paper_session.py assemble_risk_layer 两个不变量）。

    DefaultRiskValidator=kill_switch_owner（熔断唯一仲裁，禁旁路）；DrawdownStateMachine=
    回撤六态机唯一仲裁（load_or_none 启动恢复，None=冷启动 NORMAL）。两者共用同一
    JsonStateStore——与订单级校验共享同一熔断闩，"风控桥放行/编排层熔断"双头禁绝。
    """
    from zephyr.risk.core.drawdown_state_machine import DrawdownStateMachine  # noqa: PLC0415
    from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator  # noqa: PLC0415
    from zephyr.shared.state_store import JsonStateStore  # noqa: PLC0415

    store = JsonStateStore(state_dir or _BRIDGE_RISK_STATE_DIR)
    validator = DefaultRiskValidator(state_store=store)
    machine = DrawdownStateMachine(store)
    machine.load_or_none()
    return validator, machine


def _sim_drawdown_pct(store, equity: float) -> float:
    """回撤输入（峰值权益 running max，JsonStateStore 持久化；peak<=0 恒 0）。"""
    rec = store.load(_SIM_PEAK_EQUITY_NS) or {}
    try:
        peak = max(float(rec.get("peak", 0.0)), float(equity))
    except (TypeError, ValueError):
        peak = float(equity)
    rec["peak"] = peak
    store.save(_SIM_PEAK_EQUITY_NS, rec)
    if peak <= 0:
        return 0.0
    return max(0.0, 1.0 - float(equity) / peak)


def _evaluate_sim_risk(
    day: str,
    *,
    drawdown_pct: float | None = None,
    equity: float | None = None,
    state_dir: Path | None = None,
) -> dict:
    """组合级风控评估（plan-execute/e4-replay 共用，[整装回测备战W1] 接线①②）。

    六态机唯一仲裁：drawdown_pct 提供时过日度评估（同日幂等）；equity 提供时以
    峰值权益换算回撤。六态机 KILL → kill_switch_owner.trigger_kill_switch 合流
    单一仲裁点（禁旁路）。 Returns{"kill_switch_active","state","position_cap",
    "allow_new_position","drawdown_pct"}。
    """
    from zephyr.risk.core.drawdown_state_machine import DrawdownState  # noqa: PLC0415
    from zephyr.shared.state_store import JsonStateStore  # noqa: PLC0415

    validator, machine = _assemble_sim_risk_layer(state_dir)
    if drawdown_pct is None and equity is not None:
        drawdown_pct = _sim_drawdown_pct(JsonStateStore(state_dir or _BRIDGE_RISK_STATE_DIR), equity)
    if drawdown_pct is not None:
        machine.evaluate(trade_date=date.fromisoformat(day), drawdown_pct=drawdown_pct)
    if machine.current is DrawdownState.KILL and not validator.kill_switch_active:
        validator.trigger_kill_switch(reason=f"drawdown_state_machine=KILL day={day}")
    kill_active = bool(validator.kill_switch_active)
    allow_new = not (kill_active or machine.defensive_only)
    return {
        "kill_switch_active": kill_active,
        "state": machine.current.value,
        "position_cap": machine.position_cap,
        "allow_new_position": allow_new,
        "drawdown_pct": drawdown_pct,
    }


class _SimLedgerBroker:
    """模拟盘清算台账 broker（execute_kill_switch_liquidation 下单面）。

    模拟盘无实时券商：无 available_qty/get_holdings 探针能力=清算按台账快照
    全量平（stop_loss 既有 legacy 路径）；place_order 只记成交回执，由
    _apply_sim_kill_switch_liquidation 翻译为 _write_observe 台账行。
    """

    def __init__(self) -> None:
        self.fills: list[dict] = []

    def cancel_order(self, order_id: str) -> None:
        pass

    def place_order(self, symbol: str, direction: str, qty: float, order_type: str) -> None:
        self.fills.append({"symbol": symbol, "direction": direction, "qty": float(qty), "order_type": order_type})


@dataclasses.dataclass
class _SimPos:
    """模拟盘持仓快照（§5.150 长参数列表治本：风控清算族共用参数对象）。"""

    cid: str
    cash: float
    shares: float
    pos_symbol: str
    px: float | None


def _apply_sim_kill_switch_liquidation(
    day: str,
    pos: _SimPos,
    *,
    reason: str,
    state_dir: Path | None = None,
    prev_equity: float | None = None,
) -> dict:
    """KILL 熔断清算腿（[整装回测备战W1] 接线①②共用）。

    execute_kill_switch_liquidation 平台账仓（复用 T+1 分桶+清算锁+幂等）→
    台账行落 _write_observe（钱包行 signal=kill_switch_liquidation + exit 事件
    行 reason 留痕）。px 缺失/非有限=fail-visible 不清算（不猜价），仍落零事件
    钱包行如实留痕。
    """
    cid, cash, shares = pos.cid, pos.cash, pos.shares
    pos_symbol, px = pos.pos_symbol, pos.px
    from zephyr.risk.stop_loss import execute_kill_switch_liquidation  # noqa: PLC0415
    from zephyr.shared.state_store import JsonStateStore  # noqa: PLC0415

    run_id = f"kill-liq-{_now_utc().strftime('%Y%m%d%H%M%S')}"
    tradable = px is not None and math.isfinite(px) and px > 0
    events: list[list] = []
    cash2, shares2 = cash, shares
    report: dict = {}
    if tradable and shares > 0:
        broker = _SimLedgerBroker()
        report = execute_kill_switch_liquidation(
            broker,
            {pos_symbol: shares} if pos_symbol else {},
            open_orders={},
            scope="position",
            max_orders_per_second=15,
            state_store=JsonStateStore(state_dir or _BRIDGE_RISK_STATE_DIR),
        )
        for fill in broker.fills:
            proceeds = fill["qty"] * px * (1 - SELL_COST)
            events.append(
                [
                    day,
                    cid,
                    fill["symbol"],
                    "exit",
                    fill["qty"],
                    px,
                    fill["qty"] * px * SELL_COST,
                    proceeds,
                    f"kill_switch_liquidation {reason}",
                    _OBSERVE_MODE,
                    run_id,
                ]
            )
            cash2 += proceeds
            shares2 -= fill["qty"]
    pos_val = shares2 * px if (tradable and shares2 > 0) else 0.0
    equity = cash2 + pos_val
    delta = round(equity - prev_equity, 2) if prev_equity is not None else 0.0
    pocket = [
        day,
        cid,
        _OBSERVE_NOTIONAL,
        round(cash2, 2),
        pos_symbol if shares2 > 0 else "",
        round(shares2, 2),
        round(pos_val, 2),
        round(equity, 2),
        delta,
        "kill_switch_liquidation" if events else "risk_blocked",
        _OBSERVE_MODE,
        run_id,
        f"kill switch 熔断清算（{reason}）",
    ]
    _write_observe(pocket, events)
    return {
        "liquidated": bool(events),
        "events": len(events),
        "cash": round(cash2, 2),
        "shares": round(shares2, 2),
        "report_status": str(report.get("status", "")),
        "t_plus_1_rejected": [list(t) for t in report.get("t_plus_1_rejected", [])],
    }


def _sim_risk_blocked(
    day: str,
    pos: _SimPos,
    *,
    source: str,
    subject: str,
    risk: dict,
    state_dir: Path | None = None,
) -> dict:
    """风控拒绝分支（plan-execute 用）：KILL → 熔断清算；判定行 action=risk_blocked。"""
    cid, cash, shares = pos.cid, pos.cash, pos.shares
    pos_symbol, px = pos.pos_symbol, pos.px
    liquidation = None
    if risk.get("kill_switch_active") or risk.get("state") == "KILL":
        liquidation = _apply_sim_kill_switch_liquidation(
            day,
            pos,
            reason=f"state={risk.get('state')} kill_switch_active={risk.get('kill_switch_active')}",
            state_dir=state_dir,
            prev_equity=(cash + shares * px) if px is not None and math.isfinite(px) else None,
        )
    payload = {
        "risk_blocked": True,
        "posture": "risk_blocked",
        "action": "risk_blocked",
        "risk": risk,
        "liquidation": liquidation,
    }
    row_out = [
        date.fromisoformat(day),
        source,
        subject,
        make_judgment_id(day, source, subject),
        _now_utc().strftime("%Y-%m-%d %H:%M:%S"),
        _cutoff_ts(day),
        json.dumps(payload, ensure_ascii=False),
        1.0,
        "risk_layer:drawdown_state_machine; kill_switch:default_risk_validator",
        f"riskblock-{_now_utc().strftime('%Y%m%d%H%M%S')}",
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
    return {"day": day, "executed": False, "why": "risk_blocked", "risk": risk, "liquidation": liquidation}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘日链接电执行体（plan桥/E4重放/日报/结算/桥执行）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan-bridge", "plan-execute", "e4-replay", "report", "settle", "bridge-execute"):
        p = sub.add_parser(name)
        p.add_argument("--day", default=date.today().strftime("%Y-%m-%d"))
        if name == "e4-replay":
            p.add_argument("--limit", type=int, default=5, help="首夜控面（自裁 A3），跑通后扩全量")
        if name == "bridge-execute":
            p.add_argument(
                "--orders-file",
                default=None,
                help="委托批次文件（默认 data/runtime/qmt_bridge/orders/orders_<day>.csv，行=symbol,action,shares[,limit_px]）",
            )
            p.add_argument("--dry-run", action="store_true", help="只解析+打印计划，不装配不下单不落回执")
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
    elif args.cmd == "bridge-execute":
        out = bridge_execute(day, orders_file=args.orders_file, dry_run=args.dry_run)
    else:
        out = settle(day)
    print(json.dumps(out, ensure_ascii=False, default=str))
    if args.cmd == "bridge-execute":
        sys.exit(int(out.get("exit_code", 0)))  # 0=成功/SKIP 4=有单失败 1=环境失败（ps1 契约）


if __name__ == "__main__":
    main()
