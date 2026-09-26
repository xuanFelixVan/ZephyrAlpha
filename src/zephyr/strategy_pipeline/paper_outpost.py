# [BLUEPRINT] MOD-BT-225 | docs/03_modules/_domain_backtest/blueprint.md | §模拟盘前哨（FAC-E7）
# [MODULE] zephyr.strategy_pipeline.paper_outpost
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.promotion_advisory(REG-STR 真源路径常量); lifecycle_fsm
#   (sim→shelved 合法边校验); screen_source(_q CH 查询复用); zephyr.data.trading_calendar/
#   table_registry(kline SSoT);
#   zephyr.backtest.run_archive(前哨对账报告落册); scripts.backtest.sim_daily_runner(判定台账写入器)
# [CONSUMERS] c1_backtest.sim_daily_report（判定台账 source=paper_outpost 汇总行，复用既有台账
#   勿建平行账本）; data/backtest_artifacts/runs/SCR-OUTPOST-*/（FAC-E7 store_refs 落点）;
#   F27 StrategyBook（未来消费幸存者名单）; lifecycle FSM sim→shelved（只产建议不流转）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 建议只产不改册（lifecycle 终裁=Owner：只输建议，禁写注册表/禁执行 FSM 流转，
#   同 promotion_advisory 边界）；判不了不许放行（覆盖<MIN_COVERAGE 或零账面=not_evaluable，
#   fail-visible 不造 pass，与 PA-1"缺证据=不通过"同罪同治）；逐日对账=账实核对口径：市场隐含
#   盈亏=(期初股本)×(T 收盘−T-1 收盘)−当日成本（方案C 同源），对账 pocket equity_change，
#   偏差比=|隐含−账面|/前期权益；阈值=提案值（MIN_COVERAGE/DEV_TOL 公开修订留痕可改）；
#   判定台账复用 sim_daily_runner 台账（source=paper_outpost, evaluated_by 非空=settle 不重结算）；
#   单符号持仓简化；registry 名单只读（空池=如实报，sim 池空心是 E6 前置）
# [MODIFY-GUARD] tests/strategy_pipeline/test_paper_outpost.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(判定台账落库未确认经 write_report_row 原样上抛/幸存者名单为空)；
#   其余单策略失败收集不连坐（同 e4_replay 逐候选隔离先例）
# [TESTS] tests/strategy_pipeline/test_paper_outpost.py
# [A_module] module_id=MOD-BT-225 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 CLI 触发先例同 sim 家族（sim_daily_runner/
#   sim_deviation_report），设计触发链=SIM_DAILY 日链后追跑（接线另批），非常驻循环
"""F26 E7 模拟盘前哨考核器（挖矿真源 b2_f26_e7_paper_outpost.md，FAC-E7 缺位件本体）。

环节定义（图上原文）：registry 幸存者以 live 数据跑模拟盘 N 周，逐日对账预测 vs 实际
+滑点/容量实测；不达标退回 E6 标 decayed；对应 lifecycle_status=sim/paper。

本件=前哨考核闭环的最小实件：
  ①名单：读 REG-STR（docs/01.../_registry/catalogs/strategy_registry.yaml，经
    promotion_advisory.REGISTRY 真源常量）取 lifecycle∈(sim,paper) 幸存者；
  ②逐日对账：考核窗（N 周交易日）逐日账实核对——市场隐含盈亏 vs 判定台账账面盈亏
    （sim_pocket_daily mode=sim_daily 平面 + sim_trade_log 成本 + kline 收盘价）；
  ③期末判定：{ok, reason, source} 三件套（promotion_advisory 实据范式）+
    verdict=pass/fail/not_evaluable + 建议（continue_sim/demote_shelved/extend_observation），
    demote 建议经 lifecycle_fsm sim→shelved 合法边校验（只校验边合法，不执行流转）；
  ④落点：run 档案 SCR-OUTPOST-*（04_wide/outpost_report.json）+ 判定台账汇总行
    （c1_backtest.sim_daily_report source=paper_outpost——复用既有台账，勿建平行账本）。

用法:
  python -m zephyr.strategy_pipeline.paper_outpost [--weeks 4] [--end-day 2026-09-25]
      [--strategy-ids STR-A,STR-B] [--dry-run]

与 F72 分工：E7=准入前哨（本件，考核期）；F72=转正汇总（Owner 门）。共用 sim_pocket 账本面。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry_path 参数
#   fields: 待校准
#   code: registry_path
# - id: I2
#   name: statuses 参数
#   fields: 待校准
#   code: statuses
# - id: I3
#   name: end_day 参数
#   fields: 待校准
#   code: end_day
# - id: I4
#   name: weeks 参数
#   fields: 待校准
#   code: weeks
# 层: 特征
# - id: F1
#   name_zh: 待校准特征
#   name_en: feature_tbd
#   intro: 待校准（AI读代码确认）
#   formula: 待校准
#   code: 待校准
#   registry: factor_registry: 待查
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ①名单：读 REG-STR（docs/01.../_registry/catal
#   name_en: tbd
#   intro: ①名单：读 REG-STR（docs/01.../_registry/catalogs/strategy_registr
#   inputs: 待校准
#   outputs: 待校准
# - id: A2
#   name_zh: ②逐日对账：考核窗（N 周交易日）逐日账实核对——市场隐含盈亏 vs 判定台账账
#   name_en: tbd
#   intro: ②逐日对账：考核窗（N 周交易日）逐日账实核对——市场隐含盈亏 vs 判定台账账面盈亏 （sim_pocket_dail
#   inputs: 待校准
#   outputs: 待校准
# - id: A3
#   name_zh: ③期末判定：{ok, reason, source} 三件套（promotion
#   name_en: tbd
#   intro: ③期末判定：{ok, reason, source} 三件套（promotion_advisory 实据范式）+ ver
#   inputs: 待校准
#   outputs: 待校准
# - id: A4
#   name_zh: ④落点：run 档案 SCR-OUTPOST-*（04_wide/outpost
#   name_en: tbd
#   intro: ④落点：run 档案 SCR-OUTPOST-*（04_wide/outpost_report.json）+ 判定台账汇
#   inputs: 待校准
#   outputs: 待校准
# 层: 输出
# - id: O1
#   name_zh: 待校准输出 None
#   name_en: None
#   intro: 待校准
#   downstream: 待校准
# - id: O2
#   name_zh: 待校准输出 bool
#   name_en: bool
#   intro: 待校准
#   downstream: 待校准
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I2 -.->|断点| F1
# I3 -.->|断点| F1
# I4 -.->|断点| F1
# F1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from zephyr.data.table_registry import get_registry
from zephyr.strategy_pipeline.lifecycle_fsm import SHELVED, SIM, build_strategy_fsm
from zephyr.strategy_pipeline.promotion_advisory import REGISTRY
from zephyr.strategy_pipeline.screen_source import _q as ch_q  # noqa: PLC2701  CH 查询单例复用（FUNCTION-DUP 净零）

logger = logging.getLogger(__name__)

#: 幸存者词表（同 promotion_advisory._OBSERVING_LIFECYCLES 口径：sim/paper=前哨观察态）
OBSERVING_LIFECYCLES = ("sim", "paper")
#: 前哨考核窗默认周数（N 参数化；图上"N 周"提案值=4）
DEFAULT_WEEKS = 4
#: 考核窗账面覆盖下限（提案值）：有账面日/窗口交易日 低于此=not_evaluable（判不了不许放行）
MIN_COVERAGE = 0.6
#: 逐日账实偏差比容忍线（提案值，占前期权益 0.1%；四舍五入+两源时点微差余量）
DEV_TOL = 0.001
#: 判定台账 source 列值（复用 c1_backtest.sim_daily_report 台账，勿新建平行账本）
OUTPOST_SOURCE = "paper_outpost"
#: 模拟盘日频平面 mode 值（registry 策略钱包平面，sim_daily_runner.report 同款字面）
MODE_SIM_DAILY = "sim_daily"

# ── SQL 集中化（NO-BARE-SQL：语句常量模块级，表名走 schema/registry 常量） ──
from schemas.categories.sim_pocket_daily import TABLE_NAME as _T_POCKET  # noqa: E402
from schemas.categories.sim_trade_log import TABLE_NAME as _T_TRADELOG  # noqa: E402

_SQL_POCKET_DAY = (
    "SELECT argMax(signal, ingest_ts), argMax(equity, ingest_ts),"
    " argMax(position_symbol, ingest_ts), argMax(shares, ingest_ts),"
    " argMax(equity_change, ingest_ts)"
    f" FROM {_T_POCKET} FINAL"
    " WHERE strategy_id = '{sid}' AND trade_date = '{day}' AND mode = '" + MODE_SIM_DAILY + "'"
)
_SQL_TRADES_DAY = (
    "SELECT action, shares, price, cost_paid"
    f" FROM {_T_TRADELOG} FINAL"
    " WHERE strategy_id = '{sid}' AND trade_date = '{day}'"
)
_SQL_KLINE_PX = (
    "SELECT argMax(close, ingest_ts) FROM {kline_table}"
    " WHERE symbol = '{symbol}' AND trade_date IN ('{day}', '{prev}')"
    " GROUP BY trade_date ORDER BY trade_date"
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def list_survivors(
    registry_path: Path | None = None,
    statuses: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    """REG-STR 幸存者名单（只读）：lifecycle∈statuses 且 strategy_id 非空的条目。

    零伪造：空池返回空表（sim 池空心是 E6 前置病灶，本件如实上报不造数）。
    """
    import yaml

    path = registry_path or REGISTRY
    wanted = statuses or OBSERVING_LIFECYCLES
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = []
    for s in data.get("strategies", []):
        if not s.get("strategy_id"):
            continue
        if str(s.get("lifecycle_status") or "") in wanted:
            out.append(
                {
                    "strategy_id": s["strategy_id"],
                    "name_zh": s.get("name_zh", ""),
                    "code_path": s.get("code_path", ""),
                    "lifecycle_status": s.get("lifecycle_status"),
                }
            )
    return out


def outpost_window(end_day: str, weeks: int = DEFAULT_WEEKS) -> list[str]:
    """考核窗=含 end_day 的往前 N 自然周×真交易日（XSHG 日历，升序）。"""
    from zephyr.data.trading_calendar import trading_days_in_range

    end = date.fromisoformat(end_day)
    start = end - timedelta(weeks=weeks)
    return [d.isoformat() for d in trading_days_in_range(start, end)]


def prev_trading_day(day: str) -> str | None:
    """窗口首日的 T-1 真交易日（账实核对的前收基准）；14 自然日内无交易日=None。"""
    from zephyr.data.trading_calendar import trading_days_in_range

    d = date.fromisoformat(day)
    days = trading_days_in_range(d - timedelta(days=14), d)
    return days[-2].isoformat() if len(days) >= 2 else None


def _kline_close_pair(q: Callable, symbol: str, day: str, prev: str) -> tuple[float, float] | None:
    """(T-1 收盘, T 收盘)（ETF 主表，空则指数表回退）；两行不齐=None（fail-visible 不猜价）。"""
    reg = get_registry()
    for category in ("market_kline_etf_daily", "market_index_kline"):
        rows = q(_SQL_KLINE_PX.format(kline_table=reg.table(category), symbol=symbol, day=day, prev=prev))
        if len(rows) == 2 and rows[0][0] is not None and rows[1][0] is not None:
            return float(rows[0][0]), float(rows[1][0])
    return None


def _parse_pocket_row(q: Callable, sid: str, day: str) -> dict[str, Any] | None:
    """读 pocket 日行→账面要素；无行=None（零账面如实记）。"""
    rows = q(_SQL_POCKET_DAY.format(sid=sid, day=day))
    if not rows or rows[0][1] is None:
        return None
    equity = float(rows[0][1])
    ledger_pnl = float(rows[0][4] or 0.0)
    return {
        "signal": str(rows[0][0] or ""),
        "equity": equity,
        "symbol": str(rows[0][2] or ""),
        "shares_now": float(rows[0][3] or 0.0),
        "ledger_pnl": ledger_pnl,
        "prev_equity": equity - ledger_pnl,
    }


def _parse_day_trades(q: Callable, sid: str, day: str) -> tuple[float, float]:
    """当日成交→(成本合计, 净股本变更)（entry 加/exit 减，方案C 收盘成交同源）。"""
    cost, net_change = 0.0, 0.0
    for action, shares, _price, cost_paid in q(_SQL_TRADES_DAY.format(sid=sid, day=day)):
        cost += float(cost_paid or 0.0)
        if str(action) == "entry":
            net_change += float(shares or 0.0)
        elif str(action) == "exit":
            net_change -= float(shares or 0.0)
    return cost, net_change


def daily_deviation(sid: str, day: str, prev_day: str, q: Callable | None = None) -> dict[str, Any]:
    """单策略单日账实核对行（纯查询+纯计算，可注入 q 测试）。

    口径（INVARIANTS）：隐含盈亏=(期初股本)×(T 收盘−T-1 收盘)−当日成本；
    期初股本=当日终股本−当日净变更（entry 加/exit 减，与方案C 收盘成交同源）；
    偏差比=|隐含−账面 equity_change|/前期权益。无账面行=has_data False（如实记）。
    """
    q = q or ch_q
    pocket = _parse_pocket_row(q, sid, day)
    if pocket is None:
        return {"day": day, "has_data": False}
    cost, net_change = _parse_day_trades(q, sid, day)
    shares_prev_close = pocket["shares_now"] - net_change
    exposed = bool(pocket["symbol"] and pocket["shares_now"])
    px_pair = _kline_close_pair(q, pocket["symbol"], day, prev_day) if exposed else None
    if exposed and px_pair is None:
        return {
            "day": day,
            "has_data": True,
            "signal": pocket["signal"],
            "px_missing": True,
            "ledger_pnl": round(pocket["ledger_pnl"], 2),
            "prev_equity": round(pocket["prev_equity"], 2),
        }
    return _deviation_row(pocket, shares_prev_close, cost, px_pair, day)


def _deviation_row(
    pocket: dict[str, Any],
    shares_prev_close: float,
    cost: float,
    px_pair: tuple[float, float] | None,
    day: str,
) -> dict[str, Any]:
    """账面要素+行情→对账行（纯计算）。"""
    implied = ((shares_prev_close * (px_pair[1] - px_pair[0])) - cost) if px_pair is not None else None
    dev = abs(implied - pocket["ledger_pnl"]) if implied is not None else None
    prev_equity = pocket["prev_equity"]
    return {
        "day": day,
        "has_data": True,
        "signal": pocket["signal"],
        "symbol": pocket["symbol"],
        "shares_now": round(pocket["shares_now"], 2),
        "shares_prev_close": round(shares_prev_close, 2),
        "implied_pnl": round(implied, 2) if implied is not None else None,
        "ledger_pnl": round(pocket["ledger_pnl"], 2),
        "cost_paid": round(cost, 2),
        "prev_equity": round(prev_equity, 2),
        "dev": round(dev, 2) if dev is not None else None,
        "dev_ratio": round(dev / max(abs(prev_equity), 1e-9), 6) if dev is not None else None,
    }


def summarize(rows: list[dict[str, Any]], window_days: int) -> dict[str, Any]:
    """纯函数：逐日偏差行→期末判定 {verdict, ok, reason, recommendation, metrics}。

    not_evaluable（覆盖不足/零账面）判不了不许放行；fail→demote_shelved 建议
    （对应图上"不达标退回 E6 标 decayed"，FSM 合法边=sim→shelved）。
    """
    data_rows = [r for r in rows if r.get("has_data")]
    coverage = len(data_rows) / window_days if window_days else 0.0
    if coverage < MIN_COVERAGE:
        return {
            "verdict": "not_evaluable",
            "ok": False,
            "reason": f"账面覆盖 {len(data_rows)}/{window_days}<{MIN_COVERAGE}（判不了不许放行）",
            "recommendation": "extend_observation",
            "metrics": {"coverage": round(coverage, 4), "eval_days": len(data_rows)},
        }
    breaches = [r["day"] for r in data_rows if r.get("dev_ratio") is not None and r["dev_ratio"] > DEV_TOL]
    px_missing = [r["day"] for r in data_rows if r.get("px_missing")]
    eval_days = [r for r in data_rows if r.get("dev_ratio") is not None]
    ok = not breaches and not px_missing
    reasons = []
    if breaches:
        reasons.append(f"账实偏差超限 {len(breaches)} 日>{DEV_TOL}: {breaches[:5]}")
    if px_missing:
        reasons.append(f"行情价缺失 {len(px_missing)} 日（fail-visible 不算过）: {px_missing[:5]}")
    return {
        "verdict": "pass" if ok else "fail",
        "ok": ok,
        "reason": "逐日账实相符" if ok else "；".join(reasons),
        "recommendation": "continue_sim" if ok else "demote_shelved",
        "metrics": {
            "coverage": round(coverage, 4),
            "eval_days": len(eval_days),
            "max_dev_ratio": max((r["dev_ratio"] for r in eval_days), default=None),
            "total_cost_paid": round(sum(r.get("cost_paid", 0.0) for r in data_rows), 2),
        },
    }


def verify_demote_edge(sid: str) -> bool:
    """复用 lifecycle_fsm 合法边校验：sim→shelved（判定建议的机面合法性证据）。"""
    return build_strategy_fsm(sid).can_transition_from(SIM, SHELVED)


def run_outpost(
    strategy_ids: list[str] | None = None,
    weeks: int = DEFAULT_WEEKS,
    end_day: str | None = None,
    dry_run: bool = False,
    q: Callable | None = None,
) -> dict[str, Any]:
    """前哨考核主入口：名单→逐日对账→期末判定→落册（dry_run 可只算不落）。"""
    end_day = end_day or date.today().isoformat()
    days = outpost_window(end_day, weeks)
    if not days:
        raise RuntimeError(f"考核窗为空: end_day={end_day} weeks={weeks}")
    survivors = list_survivors()
    if strategy_ids:
        wanted = set(strategy_ids)
        survivors = [s for s in survivors if s["strategy_id"] in wanted]
    if not survivors:
        raise RuntimeError("registry 无 sim/paper 幸存者（sim 池空心=E6 前置病灶，如实中止）")

    now = _now_utc()
    run_id = f"SCR-OUTPOST-{now.strftime('%Y%m%d-%H%M%S')}"
    lead_prev = prev_trading_day(days[0]) or days[0]
    reports = []
    for entry in survivors:
        sid = entry["strategy_id"]
        rows = []
        for i, d in enumerate(days):
            prev_day = days[i - 1] if i > 0 else lead_prev
            try:
                rows.append(daily_deviation(sid, d, prev_day, q=q))
            except Exception as exc:  # noqa: BLE001 — 逐日隔离不连坐（同 e4_replay 先例）
                rows.append({"day": d, "has_data": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
        summary = summarize([r for r in rows if "error" not in r], len(days))
        fsm_edge_ok = verify_demote_edge(sid) if summary["recommendation"] == "demote_shelved" else None
        reports.append(
            {
                "strategy_id": sid,
                "name_zh": entry["name_zh"],
                "lifecycle_status": entry["lifecycle_status"],
                "window": {"start": days[0], "end": days[-1], "trading_days": len(days)},
                "evidence": {
                    "ok": summary["ok"],
                    "reason": summary["reason"],
                    "source": f"{_T_POCKET};{_T_TRADELOG};kline_etf_daily/kline_index; run={run_id}",
                },
                "verdict": summary["verdict"],
                "recommendation": summary["recommendation"],
                "fsm_sim_shelved_edge_ok": fsm_edge_ok,
                "metrics": summary["metrics"],
                "daily": rows,
            }
        )
        logger.info("前哨 %s: verdict=%s coverage=%s", sid, summary["verdict"], summary["metrics"]["coverage"])

    out = {"run_id": run_id, "end_day": end_day, "weeks": weeks, "survivors": len(reports), "reports": reports}
    if not dry_run:
        _land(run_id, out, now)
    return out


def _land(run_id: str, out: dict[str, Any], now: datetime) -> None:
    """落册：run 档案（前哨对账报告=FAC-E7 store_refs 落点）+ 判定台账汇总行（复用既有台账）。"""
    from zephyr.backtest.run_archive import create_run, finalize_run, write_step

    create_run(
        run_id=run_id,
        object_id="",
        kind="SCREEN",
        window={"start": out["reports"][0]["window"]["start"], "end": out["reports"][0]["window"]["end"]},
        cost_mode="frozen_l0",
        created_by="ai-session:paper-outpost",
    )
    write_step(
        run_id,
        "03",
        (
            "# 数据清单\n\n- name: E7 模拟盘前哨逐日对账\n"
            f"  source: {_T_POCKET}(mode={MODE_SIM_DAILY}) + {_T_TRADELOG} + kline 收盘价\n"
            f"  window: {out['reports'][0]['window']}\n"
            "  pit_note: '账实核对=当日收盘 vs 前日收盘，判定只用 ≤T 数据'\n  proxy: false\n"
        ),
    )
    write_step(run_id, "04", json.dumps(out, ensure_ascii=False, indent=1, default=str), filename="outpost_report.json")
    n_pass = sum(1 for r in out["reports"] if r["verdict"] == "pass")
    n_fail = sum(1 for r in out["reports"] if r["verdict"] == "fail")
    n_ne = sum(1 for r in out["reports"] if r["verdict"] == "not_evaluable")
    write_step(
        run_id,
        "verdict",
        (
            f"# 判定书：{run_id}\n\n对象：E7 模拟盘前哨考核（FAC-E7，MOD-BT-225）\n"
            f"结论：verdict=done（幸存者 {len(out['reports'])}：pass {n_pass} / fail {n_fail} / "
            f"not_evaluable {n_ne}）｜ verdict_reason=paper_outpost_reconciliation\n"
            f"阈值（提案值可公开修订）：覆盖>={MIN_COVERAGE} 逐日偏差比<={DEV_TOL}\n"
            f"判定回写边界：本件只产建议（continue_sim/demote_shelved），lifecycle 终裁=Owner\n"
        ),
    )
    finalize_run(run_id, verdict_ref={"table": "c1_backtest.sim_daily_report", "run_id": run_id})

    # 判定台账汇总行：复用 sim_daily_runner 判定台账写入器（禁复制写入路径）
    from scripts.backtest.sim_daily_runner import make_judgment_id, write_report_row

    for r in out["reports"]:
        payload = {k: r[k] for k in ("verdict", "recommendation", "evidence", "metrics", "fsm_sim_shelved_edge_ok")}
        score = 1.0 if r["verdict"] == "pass" else 0.0
        ts = now.strftime("%Y-%m-%d %H:%M:%S")
        row = [
            date.fromisoformat(out["end_day"]),
            OUTPOST_SOURCE,
            r["strategy_id"],
            make_judgment_id(out["end_day"], OUTPOST_SOURCE, r["strategy_id"]),
            ts,
            f"{out['end_day']} 07:00:00",
            json.dumps(payload, ensure_ascii=False),
            1.0,
            r["evidence"]["source"],
            run_id,
            0,
            r["verdict"],
            json.dumps(payload, ensure_ascii=False),
            ts,
            "outpost_daily_reconciliation",
            score,
            ts,
            OUTPOST_SOURCE,
        ]
        write_report_row(row)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="E7 模拟盘前哨考核器（registry 幸存者 N 周逐日对账）")
    ap.add_argument("--weeks", type=int, default=DEFAULT_WEEKS, help=f"考核窗周数（默认 {DEFAULT_WEEKS}）")
    ap.add_argument("--end-day", default=None, help="窗口末日 YYYY-MM-DD（默认今天）")
    ap.add_argument("--strategy-ids", default=None, help="逗号分隔策略 id 子集（默认全量幸存者）")
    ap.add_argument("--dry-run", action="store_true", help="只算不落册（run 档案+判定台账零写入）")
    args = ap.parse_args()
    out = run_outpost(
        strategy_ids=args.strategy_ids.split(",") if args.strategy_ids else None,
        weeks=args.weeks,
        end_day=args.end_day,
        dry_run=args.dry_run,
    )
    print(json.dumps(out, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
