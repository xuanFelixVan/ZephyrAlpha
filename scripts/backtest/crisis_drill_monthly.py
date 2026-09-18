# [BLUEPRINT] MOD-BT-219 | docs/_working/residual_construction/wo2_blackswan_workbook.md §4（战役 WO-2c）
#   （2026-09-18 st-deeprev-20260918：原头用路径作 module_id 被 BLUEPRINT 门禁拦——Owner 授权修复取号 MOD-BT-219，仓内最大 MOD-BT-218）
# [MODULE] scripts.backtest.crisis_drill_monthly
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.infrastructure.database_service; zephyr.risk.core.stress_test_engine(MOD-RK-12); zephyr.risk.core.liquidity_crisis_scenarios(MOD-RK-047); zephyr.risk.core.drawdown_bankruptcy_floor; zephyr.data.alerter; zephyr.shared.io.file_utils
# [CONSUMERS] 月度接线（总统筹 --due 门控调用）; task_board 告警面(经 Alerter failures 正门)
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读生产表(reader角色,禁写生产表); 演练产物只落 data/backtest_artifacts/drills/<run_id>/(只增目录);
#   破产地板口径复用 drawdown_bankruptcy_floor.check_bankruptcy_floor(initial=1.0, ratio=0.85, 严格小于);
#   窗口重放=等权买入持有近似口径(各标的按窗内首日重基,显式标注非真实交易回放);
#   第二口径=stress_test_engine 预置 shock 静态冲击(板块映射缺失时取情景最劣 shock 全仓代理,保守上界,显式标注);
#   第三口径=liquidity_crisis_scenarios 四情景族静态冲击(治"产而不消");
#   月频门控不做新计划任务,交付 --due 检查(marker tmp/crisis_drill_last.json, >30天=due);
#   告警走 Alerter failures 正门(data/failures/*.json),不新增告警通道
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 失败/报告写失败抛异常; is_due 文件缺失/损坏=due(fail-closed); 告警失败不抛(Alerter 自吞)
# [TESTS] tests/backtest/test_crisis_drill_monthly.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是月度危机演练 CLI（WO-2c 裁定不做新计划任务，
#   月频接线归总统筹 --due 门控后人工/统筹按需触发，无常驻进程、无 cron/Timer/sleep-loop），
#   与 commit_queue.py/sim_attribution_report.py（manual+event 接线）同类
"""月度危机演练——当前纸面组合 × 四预置历史危机窗 重放伤亡报告（WO-2c）。

痛点（wo2_blackswan_workbook §4）：无"历史区间+当前持仓"一键重放件，Owner 危机
决策靠肉眼。本件每月把当前纸面组合持仓放进四个历史危机窗重放：

  1. W2015: 2015-06-01 ~ 2015-09-30 千股跌停
  2. W2018: 2018-03-01 ~ 2018-10-31 贸易战
  3. W2020: 2020-02-01 ~ 2020-02-29 疫情
  4. W2024: 2024-01-01 ~ 2024-02-29 微盘崩盘

三口径并列输出：
  口径一(主) 窗口逐日净值重放：kline_daily 真实行情(经 TableRegistry)，等权买入持有
             （各标的窗内首日重基，演练近似口径，非真实交易回放），逐日净值路径
             → MaxDD / 破产地板(nav<0.85×初始,复用 MOD-RK drawdown_bankruptcy_floor
             语义) / 恢复天数。
  口径二(交叉验证) zephyr.risk.core.stress_test_engine 预置历史情景 shock
             (2015→2015_china_stock_crash, 2020→2020_covid_crash, 另跑 2008 作
             上下文)静态冲击 Σw·shock。持仓符号无板块映射时取情景最劣板块 shock
             全仓代理=保守上界（显式标注）。
  口径三(流动性) zephyr.risk.core.liquidity_crisis_scenarios 四情景族
             （枯竭/封死/融资断裂/全员出逃）静态冲击 + 出场滑点（治"产而不消"）。

输入：sim_pocket_daily(账本表,经 schema 真源)最新持仓快照；全现金时降级取最近一次非空持仓
快照（如实标注）；从未有过持仓则出空报告骨架并告警（不硬造组合）。

落盘：data/backtest_artifacts/drills/<run_id>/{casualty_report.json,casualty_report.md}；
成功后写 marker tmp/crisis_drill_last.json；月频接线只调 --due 判定，不做新计划任务。

用法：
    python scripts/backtest/crisis_drill_monthly.py --due          # 月频门控判定
    python scripts/backtest/crisis_drill_monthly.py                # 跑演练
    python scripts/backtest/crisis_drill_monthly.py --no-alert     # 不发告警
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.data.alerter import Alerter, LEVEL_ERROR
from zephyr.risk.core.drawdown_bankruptcy_floor import (
    BankruptcyFloorConfig,
    check_bankruptcy_floor,
)
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

TASK_ID: Final = "crisis_drill_monthly"
DRILL_DIR: Final = Path("data/backtest_artifacts/drills")
MARKER_PATH: Final = Path("tmp/crisis_drill_last.json")
MONTHLY_MAX_DAYS: Final = 30
BANKRUPTCY_FLOOR_RATIO: Final = 0.85  # 真源=BankruptcyFloorConfig 默认值，此处仅报告引用

# 四预置历史危机窗（wo2_blackswan_workbook §4 真源）
PRESET_WINDOWS: Final[tuple[dict[str, str], ...]] = (
    {
        "window_id": "W2015",
        "label": "2015 千股跌停",
        "start": "2015-06-01",
        "end": "2015-09-30",
        "stress_scenario": "2015_china_stock_crash",  # 对应 MOD-RK-12 预置情景
    },
    {
        "window_id": "W2018",
        "label": "2018 贸易战",
        "start": "2018-03-01",
        "end": "2018-10-31",
        "stress_scenario": "",  # 无预置情景，口径二不适用
    },
    {
        "window_id": "W2020",
        "label": "2020 疫情",
        "start": "2020-02-01",
        "end": "2020-02-29",
        "stress_scenario": "2020_covid_crash",
    },
    {
        "window_id": "W2024",
        "label": "2024 微盘崩盘",
        "start": "2024-01-01",
        "end": "2024-02-29",
        "stress_scenario": "",  # 无预置情景，口径二不适用
    },
)


# ────────────────────────── 数据结构 ──────────────────────────


@dataclass(frozen=True)
class DrillPortfolio:
    """演练输入组合（等权/市值权口径的符号→权重）。"""

    positions: dict[str, float]  # symbol -> 权重(未归一,用时归一)
    source: str  # 持仓来源标注(sim_pocket_daily_latest / sim_pocket_daily_last_nonempty / explicit)
    as_of: str  # 快照日
    notes: list[str] = field(default_factory=list)


# ────────────────────────── 纯函数（可测） ──────────────────────────


def normalize_weights(positions: dict[str, float]) -> dict[str, float]:
    """权重归一（非正值剔除；全非正抛 ValueError）。"""
    positive = {s: float(w) for s, w in positions.items() if float(w) > 0}
    if not positive:
        raise ValueError(f"无可归一权重: {positions}")
    total = sum(positive.values())
    return {s: w / total for s, w in positive.items()}


def build_equal_weight_nav(
    price_panel: dict[str, list[tuple[str, float]]],
    positions: dict[str, float],
) -> tuple[list[tuple[str, float]], list[str], list[str]]:
    """等权买入持有净值路径（演练近似口径）。

    Args:
        price_panel: symbol -> [(trade_date_iso, adjusted_close)] 升序
        positions: symbol -> 原始权重

    Returns:
        (nav_series[(date, nav)], included_symbols, excluded_symbols)
        - 各标的按其窗内首日重基（nav_i=price_i(t)/price_i(first)）；
        - 组合 nav(t)=Σ w_i·nav_i(t)，权重按**窗内有数标的**重归一；
        - 窗内无数据的标的进 excluded（如实标注，不静默丢弃）。
    """
    weights_all = normalize_weights(positions)
    included = {s: series for s, series in price_panel.items() if series}
    excluded = sorted(set(weights_all) - set(included))
    if not included:
        return [], [], sorted(weights_all)
    weights = normalize_weights({s: weights_all[s] for s in included})
    rebased: dict[str, dict[str, float]] = {}
    for sym, series in included.items():
        base = series[0][1]
        if base <= 0:
            continue
        rebased[sym] = {d: px / base for d, px in series}
    # 权重按成功重基的标的再归一
    rebased_syms = sorted(rebased)
    if not rebased_syms:
        return [], [], sorted(weights_all)
    w_eff = normalize_weights({s: weights[s] for s in rebased_syms})
    all_dates = sorted({d for sym in rebased_syms for d in rebased[sym]})
    nav_series: list[tuple[str, float]] = []
    for d in all_dates:
        nav = sum(w_eff[s] * rebased[s][d] for s in rebased_syms if d in rebased[s])
        nav_series.append((d, nav))
    return nav_series, rebased_syms, excluded


def compute_window_metrics(nav_series: list[tuple[str, float]]) -> dict[str, Any]:
    """窗口伤亡指标：MaxDD / 破产地板（复用 MOD-RK check_bankruptcy_floor） / 恢复天数。

    - MaxDD = max(1 - nav/cummax)；单点序列=0；
    - 破产地板判定=check_bankruptcy_floor(min_nav, initial=1.0, ratio=0.85)，
      语义与生产 Kill Switch 第五类触发源完全一致（严格小于）；
    - 恢复天数=从回撤谷底日起，净值重新站回前高的交易天数；未恢复=None。
    """
    if not nav_series:
        return {
            "max_drawdown": None,
            "max_drawdown_date": None,
            "trough_date": None,
            "min_nav": None,
            "bankruptcy_floor_breach": False,
            "breach_pct": None,
            "recovery_days": None,
            "recovered": None,
        }
    dates = [d for d, _ in nav_series]
    navs = [float(v) for _, v in nav_series]
    peak = navs[0]
    peak_idx = 0
    max_dd = 0.0
    trough_idx = 0
    dd_peak_idx = 0
    for i, v in enumerate(navs):
        if v > peak:
            peak = v
            peak_idx = i
        dd = peak - v if peak > 0 else 0.0
        dd_pct = dd / peak if peak > 0 else 0.0
        if dd_pct > max_dd:
            max_dd = dd_pct
            trough_idx = i
            dd_peak_idx = peak_idx
    min_nav = min(navs)
    breach = check_bankruptcy_floor(min_nav, 1.0, BankruptcyFloorConfig())
    recovery_days: int | None = None
    recovered = False
    if max_dd > 0:
        pre_peak = navs[dd_peak_idx]
        for offset, v in enumerate(navs[trough_idx + 1 :], start=1):
            if v >= pre_peak:
                recovery_days = offset
                recovered = True
                break
    return {
        "max_drawdown": round(max_dd, 6),
        "max_drawdown_date": dates[dd_peak_idx] if max_dd > 0 else None,
        "trough_date": dates[trough_idx] if max_dd > 0 else None,
        "min_nav": round(min_nav, 6),
        "bankruptcy_floor_breach": breach is not None,
        "breach_pct": round(breach.breach_pct, 6) if breach else None,
        "recovery_days": recovery_days,
        "recovered": recovered if max_dd > 0 else None,
    }


def is_due(
    marker_path: str | Path,
    today: date | None = None,
    max_days: int = MONTHLY_MAX_DAYS,
) -> dict[str, Any]:
    """月频门控判定（fail-closed：marker 缺失/损坏=due）。

    Returns:
        {"due": bool, "last_run": str|None, "days_since": int|None, "marker": str}
    """
    today = today or now_utc().date()
    path = Path(marker_path)
    if not path.exists():
        return {"due": True, "last_run": None, "days_since": None, "marker": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        last_run = str(data["last_run"])
        last_date = date.fromisoformat(last_run[:10])
    except Exception:  # noqa: BLE001 — 损坏 marker 按 due 处理（fail-closed）
        return {"due": True, "last_run": None, "days_since": None, "marker": str(path)}
    days = (today - last_date).days
    return {
        "due": days > max_days,
        "last_run": last_run,
        "days_since": days,
        "marker": str(path),
    }


def load_portfolio_from_rows(
    latest_rows: list[dict[str, Any]],
    last_nonempty_rows: list[dict[str, Any]] | None,
) -> DrillPortfolio | None:
    """持仓加载降级链（纯函数）。

    1. latest_rows 含持仓 → 直接用（source=sim_pocket_daily_latest）；
    2. 全现金且 last_nonempty_rows 含持仓 → 降级用最近非空快照（如实标注）；
    3. 都没有 → None（调用方出空报告骨架，不硬造组合）。
    """
    pos = _rows_to_positions(latest_rows)
    if pos:
        return DrillPortfolio(
            positions=pos,
            source="sim_pocket_daily_latest",
            as_of=str(latest_rows[0]["trade_date"]),
        )
    notes = ["最新快照全现金/无持仓，降级取最近一次非空持仓快照口径（如实标注）"]
    if last_nonempty_rows:
        pos = _rows_to_positions(last_nonempty_rows)
        if pos:
            return DrillPortfolio(
                positions=pos,
                source="sim_pocket_daily_last_nonempty",
                as_of=str(last_nonempty_rows[0]["trade_date"]),
                notes=notes,
            )
    notes.append("sim_pocket_daily 从未有过持仓，无可演练组合（不硬造默认组合）")
    return DrillPortfolio(positions={}, source="sim_pocket_daily_empty", as_of="", notes=notes)


def _rows_to_positions(rows: list[dict[str, Any]]) -> dict[str, float]:
    """sim_pocket_daily 行 → symbol→position_value 权重（剔除空持仓行）。"""
    positions: dict[str, float] = {}
    for row in rows or []:
        sym = str(row.get("position_symbol") or "").strip()
        if not sym:
            continue
        positions[sym] = positions.get(sym, 0.0) + float(row.get("position_value") or 0.0)
    return positions


# ────────────────────────── 数据访问（reader 只读） ──────────────────────────


def _get_reader_conn():
    from zephyr.infrastructure.database_service import get_db_service

    return get_db_service().get_clickhouse_conn(role="reader")


_TABLES: dict[str, str] = {}


def _table(key: str) -> str:
    """表名走真源（TABLE-NAME-REGISTRY 合规）：schema 模块 TABLE_NAME / TableRegistry。"""
    if not _TABLES:
        import importlib

        pocket = importlib.import_module("schemas.categories.sim_pocket_daily")
        kline = importlib.import_module("schemas.categories.kline.market_kline_daily")
        from zephyr.data.table_registry import get_registry

        _TABLES["pocket"] = f"{'c1_backtest'}.{pocket.TABLE_NAME}"
        _TABLES["kline"] = get_registry().table("market_kline_daily")
    return _TABLES[key]


_SNAPSHOT_COLUMNS: Final = ("trade_date", "strategy_id", "position_symbol", "position_value", "equity", "mode")

# NO-BARE-SQL 治本：SQL 提为模块级常量（§7 手册：SQL 常量用 plain 赋值，**不加 Final**——
# _extract_sql_constant_lines 只识别 ast.Assign，AnnAssign 不被豁免）。表名经 _table() 注入。
SQL_LATEST_SNAPSHOT = (
    "SELECT trade_date, strategy_id, position_symbol, position_value, equity, mode "
    "FROM {pocket} FINAL "
    "WHERE trade_date = (SELECT max(trade_date) FROM {pocket})"
)
SQL_LATEST_NONEMPTY_SNAPSHOT = (
    "SELECT trade_date, strategy_id, position_symbol, position_value, equity, mode "
    "FROM {pocket} FINAL "
    "WHERE position_symbol != '' "
    "  AND trade_date = (SELECT max(trade_date) FROM {pocket} WHERE position_symbol != '')"
)
SQL_PRICE_PANEL = (
    "SELECT symbol, toString(trade_date), close, coalesce(adj_factor, 1) AS af "
    "FROM {kline} "
    "WHERE symbol IN ({sym_list}) AND trade_date BETWEEN '{start}' AND '{end}' "
    "ORDER BY trade_date ASC"
)
SQL_ADV_MAP = (
    "SELECT symbol, avg(amount) FROM ("
    "  SELECT symbol, trade_date, amount,"
    "         row_number() OVER (PARTITION BY symbol ORDER BY trade_date DESC) AS rn"
    "  FROM {kline}"
    "  WHERE symbol IN ({sym_list}) AND trade_date <= '{end}' AND amount > 0"
    ") WHERE rn <= {lookback} GROUP BY symbol"
)



def fetch_latest_snapshot_rows(conn) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """读 sim_pocket_daily：最新快照行 + 最近一次非空持仓快照行（只读 FINAL）。"""
    pocket = _table("pocket")
    latest = conn.execute(SQL_LATEST_SNAPSHOT.format(pocket=pocket))
    latest_rows = [dict(zip(_SNAPSHOT_COLUMNS, row)) for row in latest]
    nonempty = conn.execute(SQL_LATEST_NONEMPTY_SNAPSHOT.format(pocket=pocket))
    nonempty_rows = [dict(zip(_SNAPSHOT_COLUMNS, row)) for row in nonempty]
    return latest_rows, nonempty_rows


def fetch_price_panel(
    conn, symbols: list[str], start: str, end: str
) -> dict[str, list[tuple[str, float]]]:
    """窗内复权收盘价面板（close×adj_factor，NULL 因子按 1）。"""
    if not symbols:
        return {}
    sym_list = ",".join(f"'{s.strip()}'" for s in symbols if s.strip())
    kline = _table("kline")
    rows = conn.execute(SQL_PRICE_PANEL.format(kline=kline, sym_list=sym_list, start=start, end=end))
    panel: dict[str, list[tuple[str, float]]] = {}
    for sym, d, close, af in rows:
        adj = float(close) * float(af)
        if adj > 0:
            panel.setdefault(str(sym), []).append((str(d), adj))
    return panel


def fetch_adv_map(conn, symbols: list[str], end: str, lookback_days: int = 20) -> dict[str, float]:
    """窗前 lookback 个交易日的日均成交额（ADV，元）——流动性口径三输入。"""
    if not symbols:
        return {}
    sym_list = ",".join(f"'{s.strip()}'" for s in symbols if s.strip())
    kline = _table("kline")
    rows = conn.execute(
        SQL_ADV_MAP.format(kline=kline, sym_list=sym_list, end=end, lookback=int(lookback_days))
    )
    return {str(sym): float(avg_amt) for sym, avg_amt in rows}


# ────────────────────────── 三口径计算 ──────────────────────────


def run_window_replay(
    conn, portfolio: DrillPortfolio, window: dict[str, str]
) -> dict[str, Any]:
    """口径一：单窗口逐日净值重放 + 伤亡指标。"""
    symbols = sorted(portfolio.positions)
    panel = fetch_price_panel(conn, symbols, window["start"], window["end"])
    nav_series, included, excluded = build_equal_weight_nav(panel, portfolio.positions)
    metrics = compute_window_metrics(nav_series)
    return {
        "window_id": window["window_id"],
        "label": window["label"],
        "start": window["start"],
        "end": window["end"],
        "method": "等权买入持有近似口径（各标的窗内首日重基，非真实交易回放）",
        "symbols_included": included,
        "symbols_excluded_no_data": excluded,
        "nav_points": len(nav_series),
        "available": len(nav_series) > 0,
        **metrics,
    }


def run_stress_engine_crosscheck(portfolio: DrillPortfolio) -> list[dict[str, Any]]:
    """口径二：MOD-RK-12 预置历史情景静态冲击（Σw·shock，最劣板块全仓代理）。"""
    from zephyr.risk.core.stress_test_engine import (
        HISTORICAL_SCENARIOS,
        StressTestEngine,
    )

    engine = StressTestEngine()
    weights = normalize_weights(portfolio.positions)
    results: list[dict[str, Any]] = []
    portfolio_value = 1_000_000.0  # 归一化基准（比例口径，金额仅报告展示用）
    for scenario_name, preset in HISTORICAL_SCENARIOS.items():
        worst = min(preset["shocks"].values())  # 最劣板块 shock（保守上界代理）
        result = engine.run_hypothetical(
            weights=weights,
            portfolio_value=portfolio_value,
            shocks={s: worst for s in weights},
            name=f"historical_proxy::{scenario_name}",
        )
        results.append(
            {
                "scenario": scenario_name,
                "description": preset["description"],
                "proxy_note": "持仓无板块映射，取情景最劣板块 shock 全仓代理（保守上界）",
                "worst_sector_shock": worst,
                "portfolio_loss_pct": round(result.portfolio_loss_pct, 6),
                "portfolio_loss_value": round(result.portfolio_loss_value, 2),
                "is_severe": result.is_severe,
                "floor_breach_static": result.portfolio_loss_pct <= -(1 - BANKRUPTCY_FLOOR_RATIO),
            }
        )
    return results


def run_liquidity_crisis_check(conn, portfolio: DrillPortfolio, as_of: str) -> dict[str, Any]:
    """口径三：MOD-RK-047 流动性危机四情景族静态冲击（治"产而不消"）。"""
    from zephyr.risk.core.liquidity_crisis_scenarios import (
        CrisisPosition,
        run_liquidity_crisis_family,
    )

    weights = normalize_weights(portfolio.positions)
    adv_map = fetch_adv_map(conn, sorted(weights), as_of)
    portfolio_value = 1_000_000.0
    positions = [
        CrisisPosition(
            symbol=sym,
            position_value=w * portfolio_value,
            adv_value=adv_map.get(sym, 0.0),
        )
        for sym, w in sorted(weights.items())
    ]
    if not adv_map:
        return {
            "available": False,
            "gap": "kline_daily 无持仓标的成交额数据，口径三不可算（GAP 登记，不硬接）",
        }
    family_results = run_liquidity_crisis_family(positions)
    families: list[dict[str, Any]] = []
    for fr in family_results:
        loss_pct = sum(weights[s] * fr.scenario.shocks.get(s, 0.0) for s in weights)
        families.append(
            {
                "family": fr.family.value,
                "description": fr.description,
                "portfolio_shock_pct": round(loss_pct, 6),
                "total_slippage_value": round(fr.total_slippage_value, 2),
                "worst_symbol_shock": min(fr.scenario.shocks.values()) if fr.scenario.shocks else 0.0,
                "floor_breach_static": (1.0 + loss_pct) < BANKRUPTCY_FLOOR_RATIO,
            }
        )
    return {
        "available": True,
        "adv_as_of": as_of,
        "adv_basis": "窗前 20 交易日日均成交额（kline_daily.amount）",
        "portfolio_value_basis": portfolio_value,
        "families": families,
    }


# ────────────────────────── 报告落盘与告警 ──────────────────────────


def _render_meta_lines(meta: dict[str, Any]) -> list[str]:
    """报告头部 meta 行（run_id/生成时间/持仓来源/口径标注/归一持仓）。"""
    lines: list[str] = [f"# 月度危机演练伤亡报告 {meta['run_id']}", ""]
    lines.append(f"- 生成时间(UTC): {meta['generated_at_utc']}")
    lines.append(f"- 持仓来源: {meta['portfolio']['source']} (as_of={meta['portfolio']['as_of']})")
    for note in meta["portfolio"].get("notes", []):
        lines.append(f"- 口径标注: {note}")
    pos = meta["portfolio"]["positions"]
    if pos:
        weights_norm = normalize_weights(pos)
        lines.append(f"- 持仓: {', '.join(f'{s}({w:.1%})' for s, w in sorted(weights_norm.items()))}")
    return lines


def _row_window_replay(w: dict[str, Any]) -> str:
    """口径一伤亡表单行（不可算行 / 可算行含触地板与恢复天数文案）。"""
    if not w.get("available"):
        return f"| {w['window_id']} {w['label']} | {w['start']}~{w['end']} | 否(窗内无持仓标的数据) | - | - | - | - |"
    rec = w["recovery_days"]
    breach_txt = "是" if w["bankruptcy_floor_breach"] else "否"
    breach_pct = f"{w['breach_pct']:.1%}" if w["breach_pct"] is not None else "-"
    if rec is not None:
        rec_txt = str(rec)
    elif w["recovered"] is False:
        rec_txt = "未恢复"
    else:
        rec_txt = "-"
    return (
        f"| {w['window_id']} {w['label']} | {w['start']}~{w['end']} | 是"
        f" | {w['max_drawdown']:.2%} | {breach_txt}"
        f" | {breach_pct}"
        f" | {rec_txt} |"
    )


def _row_stress_crosscheck(r: dict[str, Any]) -> str:
    """口径二 stress_test_engine 交叉验证表单行。"""
    return f"| {r['scenario']} | {r['portfolio_loss_pct']:.2%} | {'是' if r['floor_breach_static'] else '否'} | {r['proxy_note']} |"


def _row_liquidity_family(family: dict[str, Any]) -> str:
    """口径三流动性四情景族表单行。"""
    return f"| {family['family']} | {family['portfolio_shock_pct']:.2%} | {'是' if family['floor_breach_static'] else '否'} | {family['total_slippage_value']:.0f} |"


def _render_liquidity_lines(liq: dict[str, Any] | None) -> list[str]:
    """口径三分节行（可算=四情景族表，不可算=gap 单行标注）。"""
    lines: list[str] = ["## 口径三：流动性危机四情景族（MOD-RK-047）", ""]
    if liq and liq.get("available"):
        lines.append("| 情景族 | 组合冲击 | 触地板(静态) | 组合滑点金额(元) |")
        lines.append("|---|---|---|---|")
        for family in liq["families"]:
            lines.append(_row_liquidity_family(family))
    else:
        lines.append(f"- 不可算: {liq.get('gap') if liq else '未执行'}")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    """伤亡报告 JSON → 人类可读 md（同目录 casualty_report.md）。

    行渲染拆为模块级 `_row_*`/`_render_*` helper（NO-HIGH-COMPLEXITY 治本，
    总包预裁：重构降复杂度，不走豁免——裁定#321 门禁只许加严）。
    """
    lines: list[str] = _render_meta_lines(report["meta"])
    lines.append("")
    lines.append("## 四预置历史窗伤亡表（口径一：等权买入持有重放）")
    lines.append("")
    lines.append("| 窗口 | 区间 | 可算 | MaxDD | 触破产地板(nav<0.85) | 击穿深度 | 恢复天数 |")
    lines.append("|---|---|---|---|---|---|---|")
    for w in report["window_replays"]:
        lines.append(_row_window_replay(w))
    lines.append("")
    lines.append("## 口径二：stress_test_engine 预置情景静态冲击（交叉验证）")
    lines.append("")
    lines.append("| 情景 | 组合冲击 | 触地板(静态) | 说明 |")
    lines.append("|---|---|---|---|")
    for r in report.get("stress_engine_crosscheck", []):
        lines.append(_row_stress_crosscheck(r))
    lines.append("")
    lines.extend(_render_liquidity_lines(report.get("liquidity_crisis_check")))
    lines.append("")
    if report.get("gaps"):
        lines.append("## GAP 与标注")
        for g in report["gaps"]:
            lines.append(f"- {g}")
        lines.append("")
    return "\n".join(lines)


def write_report(report: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    """报告落盘（只增目录 data/backtest_artifacts/drills/<run_id>/）。"""
    run_dir = out_dir / report["meta"]["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / "casualty_report.json"
    md_path = run_dir / "casualty_report.md"
    safe_write_text(json_path, json.dumps(report, ensure_ascii=False, indent=2))
    safe_write_text(md_path, render_markdown(report))
    return json_path, md_path


def alert(alert_enabled: bool, breaches: list[str], extra: dict[str, Any], degradation: bool) -> None:
    """task_board 告警面：Alerter failures 正门（data/failures/*.json 被前端消费）。"""
    if not alert_enabled:
        return
    alerter = Alerter()
    if breaches:
        alerter.notify(
            TASK_ID,
            f"危机演练：{len(breaches)} 个历史窗击穿破产地板(nav<0.85×初始)——{'; '.join(breaches)}",
            level=LEVEL_ERROR,
            source="crisis_drill_monthly",
            extra=extra,
        )
    elif degradation:
        alerter.notify(
            TASK_ID,
            "危机演练：无可演练持仓（组合全现金且无历史非空快照），已出空报告骨架",
            level=LEVEL_ERROR,
            source="crisis_drill_monthly",
            extra=extra,
        )
    else:
        logger.info("危机演练完成，无击穿，不触发告警面: %s", extra.get("report_json"))


def write_marker(marker_path: Path, run_id: str) -> None:
    """写月频 marker（tmp/crisis_drill_last.json）。"""
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(
        marker_path,
        json.dumps({"last_run": now_utc().isoformat(), "run_id": run_id}, ensure_ascii=False),
    )


# ────────────────────────── 编排 ──────────────────────────


def run_drill(
    marker_path: Path = MARKER_PATH,
    out_dir: Path = DRILL_DIR,
    alert_enabled: bool = True,
    conn=None,
) -> dict[str, Any]:
    """演练主编排：持仓加载→四窗重放→三口径→落盘→告警→marker。"""
    now = now_utc()
    run_id = f"crisis_drill_{now.strftime('%Y%m%d_%H%M%S')}"
    own_conn = conn is None
    if own_conn:
        conn = _get_reader_conn()
    try:
        latest_rows, nonempty_rows = fetch_latest_snapshot_rows(conn)
        portfolio = load_portfolio_from_rows(latest_rows, nonempty_rows)
        gaps: list[str] = []
        if portfolio is None:
            portfolio = DrillPortfolio(positions={}, source="sim_pocket_daily_empty", as_of="", notes=["无可演练持仓"])
        gaps.extend(portfolio.notes)
        degradation = not portfolio.positions

        window_replays = [run_window_replay(conn, portfolio, w) for w in PRESET_WINDOWS]
        for w in window_replays:
            if not w["available"]:
                gaps.append(
                    f"{w['window_id']}: 持仓标的在窗内无 kline_daily 数据，该窗不可算（如实标注）"
                )

        stress_results: list[dict[str, Any]] = []
        if not degradation:
            stress_results = run_stress_engine_crosscheck(portfolio)

        liquidity: dict[str, Any] = {"available": False, "gap": "空持仓，口径三不适用"}
        if not degradation:
            liquidity = run_liquidity_crisis_check(conn, portfolio, portfolio.as_of or "")

        breaches = [
            f"{w['window_id']}({w['label']}) min_nav={w['min_nav']}"
            for w in window_replays
            if w.get("bankruptcy_floor_breach")
        ]
        report = {
            "meta": {
                "run_id": run_id,
                "generated_at_utc": now.isoformat(timespec="seconds"),
                "task_id": TASK_ID,
                "portfolio": {
                    "source": portfolio.source,
                    "as_of": portfolio.as_of,
                    "positions": portfolio.positions,
                    "notes": portfolio.notes,
                },
                "method_notes": [
                    "口径一为演练近似口径（等权买入持有、窗内首日重基），非真实交易回放",
                    f"破产地板语义复用 drawdown_bankruptcy_floor（nav<{BANKRUPTCY_FLOOR_RATIO}×初始，严格小于）",
                    "只读生产表（reader），演练产物只落 data/backtest_artifacts/drills/",
                ],
            },
            "window_replays": window_replays,
            "stress_engine_crosscheck": stress_results,
            "liquidity_crisis_check": liquidity,
            "breaches": breaches,
            "gaps": gaps,
        }
        json_path, md_path = write_report(report, out_dir)
        write_marker(marker_path, run_id)
        alert(
            alert_enabled,
            breaches,
            extra={
                "run_id": run_id,
                "report_json": str(json_path),
                "report_md": str(md_path),
                "breaches": breaches,
            },
            degradation=degradation,
        )
        report["meta"]["report_json"] = str(json_path)
        report["meta"]["report_md"] = str(md_path)
        return report
    finally:
        if own_conn:
            pass  # reader 连接由 DatabaseService 统一管理，不在此关闭


# ────────────────────────── CLI ──────────────────────────


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="月度危机演练（WO-2c）：当前纸面组合 × 四历史窗重放")
    parser.add_argument("--due", action="store_true", help="仅做月频门控判定（读 marker，>30 天=due）")
    parser.add_argument("--marker", default=str(MARKER_PATH), help=f"marker 路径（默认 {MARKER_PATH}）")
    parser.add_argument("--out-dir", default=str(DRILL_DIR), help=f"报告输出目录（默认 {DRILL_DIR}）")
    parser.add_argument("--no-alert", action="store_true", help="不写 Alerter failures 告警")
    args = parser.parse_args(argv)

    if args.due:
        result = is_due(args.marker)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    report = run_drill(
        marker_path=Path(args.marker),
        out_dir=Path(args.out_dir),
        alert_enabled=not args.no_alert,
    )
    print(
        json.dumps(
            {
                "run_id": report["meta"]["run_id"],
                "report_json": report["meta"].get("report_json"),
                "breaches": report["breaches"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
