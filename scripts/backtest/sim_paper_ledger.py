# [BLUEPRINT] MOD-BT-084 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_paper_ledger
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_config;
#   schemas.categories.alloc_budget_daily(读钱包额度模板); zephyr.pf_alloc.allocation_inputs(日期校验)
# [CONSUMERS] c1_backtest.sim_pocket_daily（注册表全部 sim 策略钱包）；每日自动化（C2 已接线：
#   pipeline_events kind sim_ledger_daily/sim_wallet_due 经 subprocess/import 调本模块）
# [STARTUP] manual+event（CLI 手工；sim_ledger_daily/sim_wallet_due 事件消费为自动）
# [MATURITY] experimental
# [INVARIANTS] 一策略一钱包（初始 100 万=Owner 批准）；信号=当日收盘判定收盘执行
#   （方案 C 口径，仅内置引擎策略 STR-VREV-025）；成本=冻结土规（买 2.5bp+5bp，卖 2.5bp+10bp+5bp）；
#   幂等（同策略+日替换写；ensure_wallet 同策略+日已有行=零副作用跳过）；
#   模拟盘模式 mode 标记 replay_demo/sim_daily；
#   多策略（S08 C1）：非内置引擎策略的开户行=signal=open（策略引擎未接线不伪造信号/收益，
#   日账待翻译件重放接线），钱包额度=pf_alloc 分配快照 allocated_capital，链当日无行/表未建
#   才回退 flat 初始资金且回退原因入 note（禁静默伪造额度），--from-registry 扫 lifecycle==sim 全部条目；
#   WO-2a 危机闸 L3（2026-09-18）：crisis 日 panic entry→cash（持有/强平不动，存量不强平），
#   判定复用 zephyr.pf_alloc.crisis_gate（现读 CH，零本地内存态），resolver 异常 fail-closed 拦 entry
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(行情缺失/落库未确认)
# [TESTS] tests/backtest/test_c4_batch_smoke.py; tests/pf_alloc/test_sim_ledger_allocation_wiring.py
# [A_module] module_id=MOD-BT-133 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""模拟盘方案 C 账本——多策略虚拟钱包引擎（S08 C1 参数化；内置引擎=恐慌反弹 STR-VREV-025）。

规则（与回测翻译件 c4_e3da6fa71af1 同口径，仅内置引擎策略）：上证昨日收盘跌幅<=-1.5% 且当日
<=-1.4% → 次日按中证1000 收盘价全仓买入；持有满 19 交易日强制平仓。钱包初始 100 万（Owner 批）。
mode=replay_demo 历史演示（验证管线）/sim_daily 正式模拟盘日账。
用法：python scripts/backtest/sim_paper_ledger.py --mode replay_demo（回放验证，仅内置引擎策略）
      python scripts/backtest/sim_paper_ledger.py --mode sim_daily（每日收盘后跑内置引擎策略=既有行为）
      python scripts/backtest/sim_paper_ledger.py --mode sim_daily --strategy-id STR-XXX
        （单策略幂等开钱包：内置引擎策略跑当日口径，其余策略写开户行）
      python scripts/backtest/sim_paper_ledger.py --mode sim_daily --from-registry
        （扫注册表 lifecycle==sim 全部条目逐个幂等开钱包，C1 验收入口）
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logger = logging.getLogger(__name__)

STRATEGY_ID = "STR-VREV-025"
INITIAL_CAPITAL = 1_000_000.0
DROP_PREV, DROP_TODAY, HOLD_N = -0.015, -0.014, 20
SYMBOL = "000852"
BUY_COST, SELL_COST = (2.5 + 5.0) / 10000.0, (2.5 + 10.0 + 5.0) / 10000.0
from schemas.categories.sim_pocket_daily import TABLE_NAME as _TABLE  # noqa: E402
from schemas.categories.sim_trade_log import TABLE_NAME as _T_TRADELOG  # noqa: E402

# SQL 集中化（NO-BARE-SQL）：语句常量模块级，占位符运行期 format
SQL_REBUILD_EVENTS = (
    f"SELECT trade_date, action, shares, cash_after, run_id FROM {_T_TRADELOG} FINAL "
    "WHERE strategy_id = '{strategy_id}' AND mode = '{mode}' "
    "ORDER BY trade_date, action"
)
SQL_WALLET_EXISTS = (
    f"SELECT count() FROM {_TABLE} FINAL WHERE strategy_id = '{{strategy_id}}' AND trade_date = '{{day}}'"
)

_COLS = (
    "(trade_date, strategy_id, initial_capital, cash, position_symbol, shares, position_value,"
    " equity, daily_pnl, signal, mode, run_id, note)"
)


def _q(sql: str):
    """只读查询（进程内单客户端缓存+退出关闭，禁 socket 泄漏）。"""
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)


def run(
    mode: str, start: str, end: str, run_id: str | None = None, strategy_id: str | None = None, *, crisis_resolver=None
) -> dict:
    """内置引擎策略日账（strategy_id 缺省=STR-VREV-025，既有行为不变）。

    仅内置引擎策略（STRATEGY_ID，参数内联）有真实信号口径；传其他 strategy_id 会套用
    内置恐慌反弹参数——开户/多策略场景请走 ensure_wallet（signal=open 开户行），勿用本函数。

    WO-2a 危机闸（L3 账本级，2026-09-18）：entry 分支前置按日危机拦截——crisis 日
    panic 入场被拦 → signal 保持 'cash'，行 note 记 crisis_gate:entry_blocked；持有/
    强平逻辑不动（裁定 §2 动作矩阵：存量不强平）。crisis_resolver 注入缝（测试用假件，
    缺省=crisis_gate.resolve_crisis_state 现读 CH）；resolver 异常按 fail-closed 处理
    （读不到≠安全，拦 entry 不拦持有）；gate 旁路（crisis_gate.yaml enabled=false）时
    全程零调用。被拦日不出 sim_trade_log 事件（无交易发生），留痕走 crisis_gate_log。
    """
    sid = strategy_id or STRATEGY_ID
    run_id = run_id or f"sim-{mode}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    sh = pd_idx("000001", start, end)
    px = pd_idx(SYMBOL, start, end)
    if sh.empty or px.empty:
        raise RuntimeError("指数行情缺失")
    ret = sh["close"].pct_change()
    panic = (ret.shift(1) <= DROP_PREV) & (ret <= DROP_TODAY)
    dates = list(px.index)
    px_map = px["close"].to_dict()

    # ── WO-2a 危机闸（L3 账本级）：按日 crisis 判定（带缓存，gate 旁路则零调用）──
    try:
        from zephyr.pf_alloc.crisis_gate import load_crisis_gate_config

        crisis_enabled = load_crisis_gate_config().enabled
    except Exception:  # noqa: BLE001 — 配置读不到按启用处理（判定入口失败≠安全）
        crisis_enabled = True
    resolver = crisis_resolver or _default_crisis_resolver
    crisis_cache: dict = {}
    crisis_blocked_days: list[str] = []

    def _crisis_blocked(day_key: str) -> tuple[bool, str]:
        """(是否拦 entry, 留痕说明)。resolver 异常=读不到≠安全 → fail-closed 拦截。"""
        if not crisis_enabled:
            return False, ""
        if day_key not in crisis_cache:
            try:
                crisis_cache[day_key] = resolver(day_key)
            except Exception as exc:  # noqa: BLE001 — fail-closed：拦 entry，note 留原因
                crisis_cache[day_key] = None
                logger.warning("crisis_resolver 异常（fail-closed 拦 entry）: %s", exc)
                return True, f"crisis_gate:resolver_error({type(exc).__name__})"
        cs = crisis_cache[day_key]
        if cs is None:
            return True, ""  # 异常原因已在首次求值时记 warning
        if cs.is_crisis:
            return True, f"crisis_gate:entry_blocked({cs.state},p_r10={cs.p_r10:.3f})"
        return False, ""

    cash, shares, hold_day = INITIAL_CAPITAL, 0.0, 0
    entry_px = 0.0
    out_rows = []
    events = []
    prev_equity = INITIAL_CAPITAL
    for dt in dates:
        px_now = float(px_map[dt])
        signal = "cash"
        note = ""
        if shares > 0:
            hold_day += 1
            signal = "holding"
            if hold_day >= HOLD_N:
                cost = shares * px_now * SELL_COST
                proceeds = shares * px_now * (1 - SELL_COST)
                events.append(
                    [
                        dt.strftime("%Y-%m-%d"),
                        sid,
                        SYMBOL,
                        "exit",
                        shares,
                        px_now,
                        cost,
                        proceeds,
                        f"持有满{HOLD_N - 1}交易日平仓(入场价{entry_px:.2f})",
                        mode,
                        run_id,
                    ]
                )
                cash, shares, hold_day = proceeds, 0.0, 0
                signal = "exit"
        elif bool(panic.loc[dt]):
            day_key = dt.strftime("%Y-%m-%d")
            blocked, block_note = _crisis_blocked(day_key)
            if blocked:
                # WO-2a L3：crisis 日 panic 入场被拦 → signal='cash'（无交易，
                # 不写 sim_trade_log 事件；持有/强平逻辑不动，存量不强平）
                signal = "cash"
                note = block_note
                crisis_blocked_days.append(day_key)
            else:
                buy_cost = cash * BUY_COST
                shares = cash / px_now * (1 - BUY_COST)
                entry_px = px_now
                cash = 0.0
                hold_day = 1
                signal = "entry"
                events.append(
                    [
                        dt.strftime("%Y-%m-%d"),
                        sid,
                        SYMBOL,
                        "entry",
                        shares,
                        px_now,
                        buy_cost,
                        0.0,
                        f"恐慌触发:上证两日跌幅达阈值({DROP_PREV}/{DROP_TODAY})",
                        mode,
                        run_id,
                    ]
                )
        pos_val = shares * px_now
        equity = cash + pos_val
        daily_pnl = equity - prev_equity
        prev_equity = equity
        out_rows.append(
            [
                dt.strftime("%Y-%m-%d"),
                sid,
                INITIAL_CAPITAL,
                round(cash, 2),
                SYMBOL if shares > 0 else "",
                round(shares, 2),
                round(pos_val, 2),
                round(equity, 2),
                round(daily_pnl, 2),
                signal,
                mode,
                run_id,
                note,
            ]
        )
    # 被拦日出声+留痕（裁定 D3/D4：失败不阻断账本主流程，函数内自兜底）
    for day_key in crisis_blocked_days:
        cs = crisis_cache.get(day_key)
        if cs is None:
            continue  # resolver 异常日已记 warning，不伪造 CrisisState 出声
        from zephyr.pf_alloc.crisis_gate import alert_crisis_level, log_crisis_gate_row

        alert_crisis_level(
            "l3", trade_date=day_key, crisis_state=cs, detail="L3 entry→cash（恐慌反弹入场被危机闸拦截）"
        )
        log_crisis_gate_row(
            trade_date=day_key,
            crisis_state=cs,
            action_l1="not_wired",
            action_l2="not_applicable",
            action_l3="entry_to_cash",
        )
    return {
        "rows": out_rows,
        "events": events,
        "final_equity": round(prev_equity, 2),
        "days": len(dates),
        "entry_px_last": entry_px,
        "crisis_blocked_days": crisis_blocked_days,
    }


def _default_crisis_resolver(day: str):
    """缺省危机判定入口（lazy import：裸脚本场景不拖 pf_alloc 全链）。"""
    from zephyr.pf_alloc.crisis_gate import resolve_crisis_state

    return resolve_crisis_state(day)


def pd_idx(sym: str, start: str, end: str):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "translated"))
    from _c4_engine import load_index

    df = load_index(sym, start, end, fields=("close",))
    return df


def rebuild(strategy_id: str, mode: str, start: str, end: str) -> list[list]:
    """从 sim_trade_log 事件流重建钱包日账（后备方案：账本损毁可全量重建）。"""
    ev = _q(SQL_REBUILD_EVENTS.format(strategy_id=strategy_id, mode=mode))
    ev_by_date = {str(r[0]): r for r in ev}
    px = pd_idx(SYMBOL, start, end)
    px_map = px["close"].to_dict()
    cash, shares = INITIAL_CAPITAL, 0.0
    rows = []
    prev_equity = INITIAL_CAPITAL
    for dt in px.index:
        ds = dt.strftime("%Y-%m-%d")
        signal = "holding" if shares > 0 else "cash"
        run_id = "rebuild"
        if ds in ev_by_date:
            _, action, sh, cash_after, run_id = ev_by_date[ds]
            if action == "entry":
                shares, cash = float(sh), float(cash_after)
            else:
                shares, cash = 0.0, float(cash_after)
            signal = action
        pos_val = shares * float(px_map[dt]) if shares > 0 else 0.0
        equity = cash + pos_val
        daily_pnl = equity - prev_equity
        prev_equity = equity
        rows.append(
            [
                ds,
                strategy_id,
                INITIAL_CAPITAL,
                round(cash, 2),
                SYMBOL if shares > 0 else "",
                round(shares, 2),
                round(pos_val, 2),
                round(equity, 2),
                round(daily_pnl, 2),
                signal,
                mode,
                f"rebuild-{run_id}",
                "",
            ]
        )
    return rows


# ---------- S08 C1 多策略开户（幂等开钱包） ----------
def registry_sim_entries() -> list[dict]:
    """扫注册表 lifecycle_status=="sim" 全部条目（真源=strategy_registry.yaml）。

    复用 intake 既有 loader（zephyr.strategy_pipeline.intake._load_registry，RULE-REGISTRY/
    RULE-SSOT：不另建读取路径）；测试隔离经 monkeypatch intake.REGISTRY 指 tmp_path。
    """
    from zephyr.strategy_pipeline import intake as _intake

    reg = _intake._load_registry()
    return [
        {"strategy_id": s["strategy_id"], "code_path": s.get("code_path") or ""}
        for s in reg.get("strategies", [])
        if s.get("lifecycle_status") == "sim"
    ]


def allocation_wallet_capital(strategy_id: str, day: str) -> tuple[float | None, str]:
    """读 pf_alloc 分配快照取本策略当日钱包额度 → (额度 | None, 溯源/回退说明)。

    额度真值 = alloc_budget_daily.allocated_capital，与 `run_daily_allocation()` 返回对象的
    ``wallet_capital[strategy_id]`` 同源（orchestrator 以同一值装配行与返回值，重跑=新 run_id
    追加，故读"当日该策略最近一次 run"即最新口径）。SQL 取 schemas 读模板真源（禁裸 SQL/
    禁复制列名），只读通道复用本模块 `_q`。

    回退（fail-open **只在回退路径**）：表未建 / 当日无行 / 本策略无行 / 额度非法 / 查询异常
    → (None, 原因)。账本据此按旧 flat 口径开行并把原因写进行 note——绝不静默伪造额度，
    也绝不因"分配链当日缺席"阻断开户（钱包行是分配链自身的绩效输入，先有鸡）。
    """
    try:
        # 先挂 pf_alloc：它把仓根（schemas DDL-as-Code 真源所在）插进 sys.path——
        # 账本以 `python scripts/backtest/sim_paper_ledger.py` 裸脚本跑时仓根不在 sys.path
        from zephyr.pf_alloc.allocation_inputs import validate_date_literal

        day = validate_date_literal(day)
    except Exception as exc:  # noqa: BLE001 — 日期不合分配口径=不查库，直接回退
        return None, f"业务日期不可用于分配查询（{type(exc).__name__}: {str(exc)[:120]}）"
    try:
        from schemas.categories.alloc_budget_daily import SQL_DAY_SLICE, TABLE_NAME
    except Exception as exc:  # noqa: BLE001 — 读模板不可用=回退（分配链尚未落地该表）
        return None, f"alloc_budget_daily 读模板不可用（{type(exc).__name__}: {str(exc)[:120]}）"
    try:
        rows = list(_q(SQL_DAY_SLICE.format(table=TABLE_NAME, date=day)))
    except Exception as exc:  # noqa: BLE001 — 未建表/CH 不可达，原因原样入 note
        return None, f"{TABLE_NAME} 不可读（{type(exc).__name__}: {str(exc)[:120]}）"
    row = next((r for r in rows if str(r[0]) == strategy_id), None)
    if row is None:
        return None, (
            f"分配链当日无本策略行（{day} 共 {len(rows)} 行）"
            if rows
            else f"分配链当日无快照行（{day}，链未跑或已回退 flat）"
        )
    try:
        capital = round(float(row[5]), 2)
    except (TypeError, ValueError) as exc:  # noqa: BLE001 — 非数值额度=不可信，回退
        return None, f"allocated_capital 非数值（{row[5]!r}，{type(exc).__name__}）"
    if capital != capital or capital < 0:  # NaN / 负额度（口径不可能值）
        return None, f"allocated_capital={capital} 非法（须为非负有限值）"
    return capital, f"pf_alloc 分配快照 run={row[1]}（{TABLE_NAME} {day}）"


def _write_rows(rows: list[list], events: list[list]) -> None:
    from zephyr.data import ch_writer

    def cell(v):
        if v is None:
            return chr(92) + "N"
        return str(v).replace(chr(9), " ").replace(chr(10), " ")

    tsv = "\n".join("\t".join(cell(v) for v in r) for r in rows) + "\n"
    if not ch_writer.write_tsv(_TABLE, _COLS, tsv.encode("utf-8")):
        raise RuntimeError("落库未确认——fail-closed")
    if events:
        ev_cols = (
            "(trade_date, strategy_id, symbol, action, shares, price, cost_paid, cash_after,"
            " signal_reason, mode, run_id)"
        )
        ev_tsv = "\n".join("\t".join(cell(v) for v in r) for r in events) + "\n"
        if not ch_writer.write_tsv("c1_backtest.sim_trade_log", ev_cols, ev_tsv.encode("utf-8")):
            raise RuntimeError("事件流水落库未确认——fail-closed")


def ensure_wallet(
    strategy_id: str,
    day: str | None = None,
    mode: str = "sim_daily",
    code_path: str = "",
    allow_unregistered: bool = False,
) -> dict:
    """幂等开钱包（C1 核心）：同策略+日已有钱包行则跳过（重复调用零副作用）。

    - 注册表 SSOT 卫兵（R5 治本 2026-09-22 st-sim-launch）：mode=sim_daily 平面的
      钱包准入真源=strategy_registry lifecycle==sim（+内置引擎策略）。非在册条目
      拒绝开户返回 why=not_in_registry_sim（不写任何行）——止血注册表外幽灵钱包
      每日自我续开户（STR-AUTO-001/STR-MULTIFACTOR-001 实证）。显式逃生=
      allow_unregistered=True（手工运维通道，留痕调用方自担）。
    - 内置引擎策略（STRATEGY_ID）→ run() 当日全口径（与既有 sim_daily 行为等值，不迁移不破坏）；
    - 其余注册表 sim 条目 → 开户行（signal=open，note 记额度来源——
      策略日账/信号待翻译件 build() 重放接线，禁伪造信号与收益）；
      钱包额度=pf_alloc 分配快照 allocated_capital（= run_daily_allocation().wallet_capital，
      见 `allocation_wallet_capital`）；分配链当日无行/表未建/查询异常 → 回退旧 flat
      INITIAL_CAPITAL 口径并把回退原因写进 note（回退是显式事实，不是静默伪造数字）；
    - sim_trade_log 同步落 open 事件（事件溯源：rebuild() 对非 entry 动作按现金到账处理，兼容）。
    返回 {"strategy_id", "day", "created": bool, "capital", "capital_source", ...}；
    code_path 仅作 payload 透传留痕。
    """
    day = day or date.today().strftime("%Y-%m-%d")
    existing = _q(SQL_WALLET_EXISTS.format(strategy_id=strategy_id, day=day))
    if existing and int(existing[0][0]) > 0:
        return {"strategy_id": strategy_id, "day": day, "created": False, "why": "row_exists"}
    if (
        mode == "sim_daily"
        and strategy_id != STRATEGY_ID
        and not allow_unregistered
        and strategy_id not in {e["strategy_id"] for e in registry_sim_entries()}
    ):
        return {"strategy_id": strategy_id, "day": day, "created": False, "why": "not_in_registry_sim"}
    run_id = f"sim-open-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    if strategy_id == STRATEGY_ID:
        res = run(mode, day, day, run_id=run_id, strategy_id=strategy_id)
        rows, events = res["rows"], res["events"]
        capital, source = INITIAL_CAPITAL, "内置引擎策略日账（额度不经分配链）"
    else:
        alloc_cap, source = allocation_wallet_capital(strategy_id, day)
        if alloc_cap is None:
            # 回退路径（fail-open）：额度=旧 flat 口径，**原因入 note 留痕**，不静默伪造
            capital = INITIAL_CAPITAL
            note = f"C1 自动开户（策略引擎未接线，日账待翻译件重放）｜钱包额度回退 flat 旧口径：{source}"
        else:
            capital = alloc_cap
            note = f"C1 自动开户（钱包额度={source}）｜信号待翻译件重放，不伪造信号/收益"
        rows = [
            [
                day,
                strategy_id,
                capital,
                round(capital, 2),
                "",
                0.0,
                0.0,
                round(capital, 2),
                0.0,
                "open",
                mode,
                run_id,
                note,
            ]
        ]
        events = [[day, strategy_id, "", "open", 0.0, 0.0, 0.0, capital, f"C1 自动开户｜{source}", mode, run_id]]
    _write_rows(rows, events)
    return {
        "strategy_id": strategy_id,
        "day": day,
        "created": True,
        "rows": len(rows),
        "events": len(events),
        "capital": capital,
        "capital_source": source,
    }


def open_wallets_from_registry(day: str | None = None) -> dict:
    """逐个幂等开钱包（--from-registry 本体）：单条失败收集后统一 fail-closed。"""
    out: dict = {"opened": [], "skipped": [], "errors": []}
    for e in registry_sim_entries():
        try:
            r = ensure_wallet(e["strategy_id"], day=day, code_path=e.get("code_path") or "")
            (out["opened"] if r.get("created") else out["skipped"]).append(e["strategy_id"])
        except Exception as exc:  # noqa: BLE001 —— 收集全部失败，循环不断（逐策略隔离）
            out["errors"].append({"strategy_id": e["strategy_id"], "error": str(exc)[:160]})
    if out["errors"]:
        raise RuntimeError(f"开户存在失败（fail-closed）: {out['errors']}")
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘方案C钱包（多策略；内置引擎=恐慌反弹）")
    ap.add_argument("--mode", choices=["replay_demo", "sim_daily"], required=True)
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    ap.add_argument("--rebuild", action="store_true", help="从事件流重建钱包日账（后备方案，不产生新事件）")
    ap.add_argument("--strategy-id", default=None, help="单策略幂等开钱包（ensure_wallet）；缺省=内置引擎策略既有行为")
    ap.add_argument(
        "--from-registry",
        action="store_true",
        help="扫注册表 lifecycle==sim 全部条目逐个幂等开钱包（仅 sim_daily；C1 验收入口）",
    )
    ap.add_argument(
        "--allow-unregistered",
        action="store_true",
        help="逃生口：--strategy-id 手工运维通道绕过注册表 SSOT 卫兵（留痕自担；默认拒绝在册外开户）",
    )
    args = ap.parse_args()
    if args.from_registry and args.mode != "sim_daily":
        raise SystemExit("--from-registry 仅支持 --mode sim_daily（开户是模拟盘动作）")
    if args.strategy_id and args.strategy_id != STRATEGY_ID and (args.mode == "replay_demo" or args.rebuild):
        raise SystemExit(
            f"replay_demo/rebuild 仅内置引擎策略 {STRATEGY_ID} 支持"
            f"（{args.strategy_id} 无内联引擎；多策略请用 --from-registry 开户）"
        )
    if args.from_registry:
        day = args.start or date.today().strftime("%Y-%m-%d")
        out = open_wallets_from_registry(day=day)
        print(json.dumps({"mode": "sim_daily", "from_registry": True, "day": day, **out}, ensure_ascii=False))
        return
    if args.strategy_id and args.mode == "sim_daily" and not args.rebuild:
        out = ensure_wallet(
            args.strategy_id,
            day=args.start or date.today().strftime("%Y-%m-%d"),
            allow_unregistered=args.allow_unregistered,
        )
        print(json.dumps({"mode": "sim_daily", "strategy_id": args.strategy_id, **out}, ensure_ascii=False))
        return
    if args.mode == "replay_demo":
        start, end = args.start or "2026-07-01", args.end or date.today().strftime("%Y-%m-%d")
    else:
        start = end = args.start or date.today().strftime("%Y-%m-%d")
    if args.mode == "sim_daily" and not args.rebuild:
        # 红蓝对抗加固 2026-09-14：19:30 档撞 CH 维护窗口（VHDX/备份类优雅停机
        # 10-25 分钟）时读数阶段直接失败，当日钱包快照丢失（9/14 实证）。
        # 有界重试覆盖 ~20 分钟窗口；replay_demo（交互式）不重试。
        import threading

        max_attempts, gap = 10, 120
        for attempt in range(1, max_attempts + 1):
            try:
                res = run(
                    args.mode,
                    start,
                    end,
                    run_id=f"sim-{args.mode}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                )
                break
            except Exception as e:  # noqa: BLE001 — CH 不可达/断连类失败均重试
                if attempt == max_attempts:
                    raise
                print(
                    f"[sim_daily] CH 不可达（{type(e).__name__}: {str(e)[:80]}），"
                    f"{gap}s 后第 {attempt}/{max_attempts} 次重试",
                    flush=True,
                )
                threading.Event().wait(gap)  # 有界退避（非定时触发）
        else:
            return
    elif args.rebuild:
        rows = rebuild(STRATEGY_ID, args.mode, start, end)
        from zephyr.data import ch_writer

        def cell2(v):
            if v is None:
                return chr(92) + "N"
            return str(v).replace(chr(9), " ").replace(chr(10), " ")

        tsv = "\n".join("\t".join(cell2(v) for v in r) for r in rows) + "\n"
        if not ch_writer.write_tsv(_TABLE, _COLS, tsv.encode("utf-8")):
            raise RuntimeError("重建落库未确认——fail-closed")
        print(json.dumps({"rebuild": True, "rows": len(rows)}, ensure_ascii=False))
        return
    if args.mode != "sim_daily" or args.rebuild:
        res = run(
            args.mode, start, end, run_id=f"sim-{args.mode}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        )
    from zephyr.data import ch_writer

    def cell(v):
        if v is None:
            return chr(92) + "N"
        return str(v).replace(chr(9), " ").replace(chr(10), " ")

    tsv = "\n".join("\t".join(cell(v) for v in r) for r in res["rows"]) + "\n"
    if not ch_writer.write_tsv(_TABLE, _COLS, tsv.encode("utf-8")):
        raise RuntimeError("落库未确认——fail-closed")
    ev_cols = (
        "(trade_date, strategy_id, symbol, action, shares, price, cost_paid, cash_after, signal_reason, mode, run_id)"
    )
    if res["events"]:
        ev_tsv = "\n".join("\t".join(cell(v) for v in r) for r in res["events"]) + "\n"
        if not ch_writer.write_tsv("c1_backtest.sim_trade_log", ev_cols, ev_tsv.encode("utf-8")):
            raise RuntimeError("事件流水落库未确认——fail-closed")
    print(
        json.dumps(
            {
                "mode": args.mode,
                "days": res["days"],
                "final_equity": res["final_equity"],
                "rows": len(res["rows"]),
                "events": len(res["events"]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
