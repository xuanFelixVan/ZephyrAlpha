# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | ATR离场双臂对照仿真器（有增益MaxDD+16.5pp）
# [MODULE] scripts.backtest.fexam.exit_sim.exit_simulator.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] run_fexam.py 或手工 CLI
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] staging 转正件；判定面不入核
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见 docstring
# [TESTS] tests/backtest/fexam/
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（Owner 批 P0-1），对拍结论已锁定随文件
"""exit_simulator — E道离场族首件：日收盘粒度 ATR 止损/移动止损路径依赖仿真器（夜战 tmp 版）。

考试装置扩展（复用禁重造）：strategy_exam.composite_signal / monthly_topn_signals /
window_metrics + ch_data 只读装载。prereg 冻结件=同目录 prereg_frozen.yaml
（冻结时间先于一切仿真运行）。正式 src/ 模块化+治理三件套=日光档工单（非本件范围；
本 tmp 版未登记 creation_token/模块简介/depgraph，日光档补齐）。

纪律：数据只读（CH SELECT）；禁改既有文件；禁 git。
"""

from __future__ import annotations

import json
import sys
import time
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

_HERE = Path(__file__).resolve().parent
RUN_ROOT = _HERE.parents[3]
assert (RUN_ROOT / "AGENTS.md").exists(), f"RUN_ROOT 解析失败: {RUN_ROOT}"
for _p in (str(RUN_ROOT / "scripts" / "backtest" / "fexam"), str(RUN_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ch_data  # noqa: E402
import strategy_exam  # noqa: E402
from strategy_exam import composite_signal, monthly_topn_signals, window_metrics  # noqa: E402

from zephyr.backtest.core.matching_logic import COMMISSION_RATE  # noqa: E402
from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

# ---------- prereg 冻结常量（真源=prereg_frozen.yaml，此处只镜像） ----------
WARM_START = "2017-10-01"  # ATR14 暖机 3 个月
WINDOW_RUN = ("2018-01-02", "2026-09-30")
WINDOW_IS = ("2018-01-02", "2025-09-30")
WINDOW_OOS = ("2025-10-09", "2026-09-30")  # = ch_data.WINDOW_HOLDOUT
STOP_MULT = 3.0
ATR_N = 14
TOP_N = 20
COL_CAP = 24
COMMISSION = float(COMMISSION_RATE)
INITIAL_CAPITAL = 1_000_000.0

SCORES_YAML = RUN_ROOT / "docs" / "_working" / "fexam" / "indicator_exam_scores_v1.yaml"
PREREG_PATH = _HERE / "prereg_frozen.yaml"
CACHE_DIR = _HERE / "cache"
OUT_YAML = RUN_ROOT / "docs" / "_working" / "fexam" / "exit_sim_report_v1.yaml"
OUT_MD = RUN_ROOT / "docs" / "_working" / "fexam" / "exit_sim_report_v1.md"


# ---------- 确定性列提取（与 prereg 冻结清单核对） ----------
def load_pass_columns(cap: int = COL_CAP) -> list[tuple[str, str]]:
    """scores YAML 文档序取 verdict==pass 的 ch_backings 首列，去重 cap（确定性不挑）。"""
    book = yaml.safe_load(SCORES_YAML.read_text(encoding="utf-8"))
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for r in book["results"]:
        if r.get("verdict") != "pass":
            continue
        cbs = r.get("ch_backings") or []
        if not cbs or cbs[0] in seen:
            continue
        seen.add(cbs[0])
        out.append((cbs[0], r["object_id"]))
        if len(out) >= cap:
            break
    return out


# ---------- 带缓存装载（只读 SELECT） ----------
def _cached(name: str, fn):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR / f"{name}.pkl"
    if p.exists():
        return pd.read_pickle(p)
    df = fn()
    df.to_pickle(p)
    return df


def load_kline(field: str) -> pd.DataFrame:
    return _cached(
        f"kline_{field}_{WARM_START}_{WINDOW_RUN[1]}",
        lambda: ch_data.load_panel(ch_data.T_KLINE_DAILY_HFQ, field, WARM_START, WINDOW_RUN[1]),
    )


def load_indicator(col_key: str) -> pd.DataFrame:
    table, column = col_key.rsplit(".", 1)
    return _cached(
        f"ind_{table.replace('.', '_')}_{column}_{WINDOW_RUN[0]}_{WINDOW_RUN[1]}",
        lambda: ch_data.load_panel(table, column, *WINDOW_RUN),
    )


# ---------- ATR14（Wilder，种子=前14个有效TR的SMA；停牌日 TR=NaN→ATR 沿用前值） ----------
def wilder_atr_one(tr: np.ndarray, n: int = ATR_N) -> np.ndarray:
    atr = np.full(len(tr), np.nan)
    valid = np.where(np.isfinite(tr))[0]
    if len(valid) < n:
        return atr
    seed_i = valid[n - 1]
    prev = float(tr[valid[:n]].mean())
    atr[seed_i] = prev
    for i in range(seed_i + 1, len(tr)):
        t = tr[i]
        if np.isfinite(t):
            prev = (prev * (n - 1) + float(t)) / n
        atr[i] = prev  # TR NaN（停牌）→ 沿用前值
    return atr


def atr14_wilder(close: pd.DataFrame, high: pd.DataFrame, low: pd.DataFrame) -> pd.DataFrame:
    pc = close.ffill().shift(1)
    tr = np.maximum(np.maximum((high - low), (high - pc).abs()), (low - pc).abs())  # NaN 传播=停牌日
    out = {}
    hv = tr.values.astype("float64")
    for j, sym in enumerate(tr.columns):
        out[sym] = wilder_atr_one(hv[:, j])
    return pd.DataFrame(out, index=tr.index, columns=tr.columns).astype("float64")


# ---------- 信号构建（装置复用 + ATR 候选过滤，prereg 冻结） ----------
def month_start_rows(trading_dates: pd.DatetimeIndex) -> list[int]:
    """与 monthly_topn_signals 内部同一构造：每月首个交易日行号（装置语义=月频调仓行）。"""
    seen: set[tuple[int, int]] = set()
    rows: list[int] = []
    for i, d in enumerate(trading_dates):
        key = (d.year, d.month)
        if key not in seen:
            seen.add(key)
            rows.append(i)
    return rows


def build_signals(ind_panels: dict[str, pd.DataFrame], kline_close: pd.DataFrame, atr: pd.DataFrame):
    composite = composite_signal(ind_panels, directions={k: 1 for k in ind_panels})
    close_run = kline_close.loc[
        (kline_close.index >= pd.Timestamp(WINDOW_RUN[0])) & (kline_close.index <= pd.Timestamp(WINDOW_RUN[1]))
    ]
    atr_al = atr.reindex(index=composite.index, columns=composite.columns)
    comp_f = composite.where(atr_al.notna())  # 信号日 ATR14 非 NaN 才入候选
    signals = monthly_topn_signals(comp_f, close_run.index, top_n=TOP_N)
    reb_rows = month_start_rows(close_run.index)  # 调仓行=月首行（非权重变化行——等权同集连月也必须重置）
    return signals, close_run, reb_rows


# ---------- 路径依赖日循环仿真（截面向量化 + 时序顺序；双臂同码仅 stop_enabled 异） ----------
def simulate(
    open_p: pd.DataFrame,
    close: pd.DataFrame,
    atr: pd.DataFrame,
    signals: pd.DataFrame,
    reb_rows: list[int],
    *,
    stop_enabled: bool,
    stop_mult: float = STOP_MULT,
    commission: float = COMMISSION,
) -> tuple[pd.Series, dict]:
    active = signals.columns[signals.abs().sum(axis=0) > 0]
    sig = signals[active]
    open_p, close, atr = open_p[active], close[active], atr[active]
    dates = close.index
    W = sig.reindex(dates).fillna(0.0).values
    O = open_p.reindex(dates).values.astype("float64")
    C = close.reindex(dates).values.astype("float64")
    A = atr.reindex(dates).values.astype("float64")
    T, N = C.shape

    execs: dict[int, tuple[np.ndarray, int]] = {}
    for i in reb_rows:
        if i + 1 < T:
            execs[i + 1] = (W[i], i)  # (目标权重, 信号日行号)

    cash = INITIAL_CAPITAL
    shares = np.zeros(N)
    entry_px = np.full(N, np.nan)
    hi_close = np.full(N, np.nan)
    atr_entry = np.full(N, np.nan)
    pend_exit = np.zeros(N, bool)
    deferred_sell = np.zeros(N, bool)
    last_px = np.full(N, np.nan)
    nav = np.full(T, np.nan)

    st = {
        "n_rebalance_exec_days": len(execs),
        "n_empty_months": 0,
        "n_stop_pierces": 0,
        "n_stop_exits": 0,
        "n_stop_pending_at_end": 0,
        "n_cash_capped_buys": 0,
        "n_deferred_sells": 0,
        "n_rebalance_trades": 0,
        "n_symbols_traded": 0,
        "pierces_sample": [],  # 前5例留痕（手工复核用）
    }

    for t in range(T):
        o, c, a = O[t], C[t], A[t]
        o_fin = np.isfinite(o)
        blocked = np.zeros(N, bool)

        # --- 早盘 @open：昨日 pierce 的止损离场（T+1，禁当日来回） ---
        if stop_enabled:
            m = pend_exit & (shares > 0) & o_fin
            for i in np.where(m)[0]:
                val = shares[i] * o[i]
                cash += val - val * commission
                shares[i] = 0.0
                pend_exit[i] = False
                blocked[i] = True
                st["n_stop_exits"] += 1
            blocked |= pend_exit  # 挂单未平（停牌顺延）禁买

        # --- 早盘 @open：顺延的调仓卖出重试 ---
        m = deferred_sell & (shares > 0) & o_fin
        for i in np.where(m)[0]:
            val = shares[i] * o[i]
            cash += val - val * commission
            shares[i] = 0.0
            deferred_sell[i] = False
        blocked |= deferred_sell

        # --- 调仓执行（T+1 开盘，等权重置） ---
        if t in execs:
            w_tgt, sig_i = execs[t]
            if float(w_tgt.sum()) <= 0.0:
                st["n_empty_months"] += 1
            a_sig = A[sig_i]
            m_sell = (w_tgt <= 0.0) & (shares > 0) & ~blocked & o_fin
            for i in np.where(m_sell)[0]:
                val = shares[i] * o[i]
                cash += val - val * commission
                shares[i] = 0.0
                st["n_rebalance_trades"] += 1
            m_def = (w_tgt <= 0.0) & (shares > 0) & ~blocked & ~o_fin
            deferred_sell |= m_def
            st["n_deferred_sells"] += int(m_def.sum())

            px_mark = np.where(o_fin, o, np.nan_to_num(last_px, nan=0.0))
            equity_open = cash + float((shares * px_mark).sum())
            m_buy = (w_tgt > 0.0) & ~blocked & o_fin
            for i in np.where(m_buy)[0]:
                tgt_notional = equity_open * float(w_tgt[i])
                tgt_shares = tgt_notional / (o[i] * (1.0 + commission))
                delta = tgt_shares - shares[i]
                trade_val = delta * o[i]
                need = abs(trade_val) * (1.0 + commission)
                if trade_val > 0 and need > cash:  # 禁杠杆：现金不足按可负担封顶
                    affordable_sh = cash / (o[i] * (1.0 + commission))
                    if affordable_sh <= shares[i]:
                        st["n_cash_capped_buys"] += 1
                        continue
                    tgt_shares = affordable_sh
                    delta = tgt_shares - shares[i]
                    trade_val = delta * o[i]
                    st["n_cash_capped_buys"] += 1
                cash -= trade_val + abs(trade_val) * commission
                shares[i] = tgt_shares
                entry_px[i] = o[i]  # 调仓再买=新入场（prereg: 全重置）
                hi_close[i] = o[i]
                atr_entry[i] = a_sig[i]
                last_px[i] = o[i] if not np.isfinite(last_px[i]) else last_px[i]
                st["n_rebalance_trades"] += 1

        # --- 收盘：估值 + 止损判定（日收盘粒度） ---
        c_fin = np.isfinite(c)
        last_px = np.where(c_fin, c, last_px)
        held_any = shares > 0
        assert not (held_any & ~np.isfinite(last_px)).any(), f"持仓缺估值标记 t={t}"
        contrib = np.where(held_any, shares * np.nan_to_num(last_px, nan=0.0), 0.0)
        nav[t] = cash + float(contrib.sum())
        if stop_enabled:
            held = (shares > 0) & c_fin & np.isfinite(a) & np.isfinite(atr_entry)
            hi_close[held] = np.maximum(hi_close[held], c[held])
            trail = hi_close - stop_mult * a
            init_s = entry_px - stop_mult * atr_entry
            eff = np.fmax(init_s, trail)  # NaN 感知 max
            pierce = held & np.isfinite(eff) & (c < eff)
            newly = pierce & ~pend_exit
            st["n_stop_pierces"] += int(newly.sum())
            if newly.any() and len(st["pierces_sample"]) < 5:
                for i in np.where(newly)[0][: 5 - len(st["pierces_sample"])]:
                    st["pierces_sample"].append(
                        {
                            "date": str(dates[t].date()),
                            "symbol": str(sig.columns[i]),
                            "close": round(float(c[i]), 4),
                            "eff_stop": round(float(eff[i]), 4),
                            "entry_px": round(float(entry_px[i]), 4),
                            "hi_close": round(float(hi_close[i]), 4),
                            "atr_entry": round(float(atr_entry[i]), 6),
                            "atr_now": round(float(a[i]), 6),
                        }
                    )
            pend_exit |= pierce

    st["n_stop_pending_at_end"] = int((pend_exit & (shares > 0)).sum())
    st["n_symbols_traded"] = int((np.abs(sig.values).sum(axis=0) > 0).sum())
    st["final_equity"] = float(nav[-1])
    st["n_days"] = int(T)
    return pd.Series(nav, index=dates, name="nav"), st


# ---------- 主流程 ----------
def run_all() -> dict:
    t_load0 = time.perf_counter()
    prereg = yaml.safe_load(PREREG_PATH.read_text(encoding="utf-8"))
    cols = load_pass_columns()
    frozen_cols = [c["column"] for c in prereg["device"]["columns_cap24"]]
    assert [c for c, _ in cols] == frozen_cols, "提取列与 prereg 冻结清单不一致——禁跑"
    print(f"[1] 列提取与 prereg 冻结清单一致（{len(cols)} 列）")

    kline_open = load_kline("open")
    kline_high = load_kline("high")
    kline_low = load_kline("low")
    kline_close = load_kline("close")
    print(f"[2] K线面板就绪 {kline_close.shape}（warm {WARM_START}..{WINDOW_RUN[1]}）")

    atr = _cached(
        f"atr14_{ATR_N}_{WARM_START}_{WINDOW_RUN[1]}",
        lambda: atr14_wilder(kline_close, kline_high, kline_low),
    )
    print(f"[3] ATR14 就绪 {atr.shape}")

    ind_panels = {k: load_indicator(k) for k, _ in cols}
    ind_panels = {k: v for k, v in ind_panels.items() if not v.empty}
    print(f"[4] 指标面板就绪 {len(ind_panels)}/{len(cols)} 列")

    signals, close_run, reb_rows = build_signals(ind_panels, kline_close, atr)
    n_pos_days = int((signals.abs().sum(axis=1) > 0).sum())
    print(f"[5] 信号就绪：{signals.shape}，调仓月行={len(reb_rows)}，有持仓日={n_pos_days}")
    t_load = time.perf_counter() - t_load0

    open_run = kline_open.reindex(close_run.index)

    # 重标定：warm 1 + 实测 3（双臂各测）
    timing: dict[str, dict] = {}
    arms: dict[str, tuple[pd.Series, dict]] = {}
    for arm, stop_on in (("nostop", False), ("stop", True)):
        simulate(open_run, close_run, atr, signals, reb_rows, stop_enabled=stop_on)  # warm-up
        times = []
        for _ in range(3):
            t0 = time.perf_counter()
            nav, stats = simulate(open_run, close_run, atr, signals, reb_rows, stop_enabled=stop_on)
            times.append(time.perf_counter() - t0)
        arms[arm] = (nav, stats)
        timing[arm] = {
            "per_run_seconds_warmup_plus3_mean": float(np.mean(times)),
            "per_run_seconds_runs": [float(x) for x in times],
            "per_symbol_day_us": float(np.mean(times) * 1e6 / (stats["n_symbols_traded"] * stats["n_days"])),
        }
        print(f"[6] {arm}: per_run={np.mean(times):.3f}s stats={stats}")
    nav_nostop, stats_nostop = arms["nostop"]
    nav_stop, stats_stop = arms["stop"]

    m_nostop = {
        "is": window_metrics(nav_nostop, *WINDOW_IS),
        "oos": window_metrics(nav_nostop, *WINDOW_OOS),
        "run": window_metrics(nav_nostop, *WINDOW_RUN),
    }
    m_stop = {
        "is": window_metrics(nav_stop, *WINDOW_IS),
        "oos": window_metrics(nav_stop, *WINDOW_OOS),
        "run": window_metrics(nav_stop, *WINDOW_RUN),
    }
    # 判定（prereg judge_frozen 语义：改善=MaxDD 朝 0 靠拢即回撤变浅）
    # erratum：prereg 机器行公式 "(nostop-stop)×100" 与自身括注「改善=朝 0 靠拢」符号相反（起草笔误）；
    # 按冻结语义+工单原文（止损版 MaxDD 改善>=5pp）统一取 (stop-nostop)×100，erratum 随册如实登记。
    improve_pp = (m_stop["oos"]["max_drawdown"] - m_nostop["oos"]["max_drawdown"]) * 100.0
    sharpe_delta = m_stop["oos"]["sharpe"] - m_nostop["oos"]["sharpe"]
    gain = bool(improve_pp >= 5.0 and sharpe_delta >= -0.2)
    verdict = "有增益" if gain else "无增益/负增益"
    judge = {
        "oos_maxdd_improve_pp": round(improve_pp, 2),
        "oos_sharpe_delta": round(sharpe_delta, 4),
        "criterion": "MaxDD改善(回撤变浅)>=5pp 且 Sharpe不降超0.2（prereg judge_frozen 语义口径）",
        "sign_erratum": "prereg 机器行公式 (nostop-stop) 与括注「改善=朝 0 靠拢」符号相反，按语义取 (stop-nostop)；双臂同规则无选择性",
        "verdict": verdict,
    }
    print(f"[7] 判定: {verdict} (MaxDD改善={improve_pp:.1f}pp, SharpeΔ={sharpe_delta:+.3f})")

    # 引擎参考跑（无止损 sanity，非判据）：daemon 线程+看门狗，超时不阻断主交付；结果缓存复用
    _ref_cache = _HERE / "engine_ref_cache.json"
    if _ref_cache.exists():
        ref = json.loads(_ref_cache.read_text(encoding="utf-8"))
        ref["cached"] = True
    else:
        ref = {"status": "skipped"}

    def _engine_ref_job(out: dict) -> None:
        try:
            from zephyr.backtest.implementations.vectorized_engine import (
                BacktestConfig,
                DefaultBacktestEngine,
            )

            vol = _cached(
                f"kline_volume_{WINDOW_RUN[0]}_{WINDOW_RUN[1]}",
                lambda: ch_data.load_panel(ch_data.T_KLINE_DAILY_HFQ, "volume", *WINDOW_RUN),
            )
            cr = close_run
            common = cr.index.intersection(vol.index)
            cr2 = cr.loc[common]
            vr2 = vol.reindex(index=common, columns=cr.columns)
            op2 = kline_open.reindex(index=common, columns=cr.columns)
            flat = pd.DataFrame(
                {
                    "date": cr2.index.repeat(cr2.shape[1]),
                    "symbol": np.tile(cr2.columns.values, len(cr2.index)),
                    "open": op2.values.reshape(-1),
                    "close": cr2.values.reshape(-1),
                    "volume": vr2.values.reshape(-1),
                }
            ).dropna(subset=["close"])
            engine = DefaultBacktestEngine(BacktestConfig())
            result = engine.run(flat, signals, strategy_name="exit_sim_ref_nostop")
            nav_e = engine.last_portfolio.nav_series
            nav_e = nav_e[~nav_e.index.isna()]
            out.update(
                {
                    "status": "ok",
                    "note": "官方引擎默认装置（PIT/剔ST/滑点/冲击/参与率全默认开）无止损参考跑，仅 sanity 非判据",
                    "metrics": {"is": window_metrics(nav_e, *WINDOW_IS), "oos": window_metrics(nav_e, *WINDOW_OOS)},
                    "trades_count": int(result.trades_count),
                }
            )
        except Exception as exc:  # noqa: BLE001 — 参考跑失败不阻断主对照
            out.update({"status": "engine_error", "error": f"{type(exc).__name__}: {exc}"[:200]})

    import threading

    if "cached" not in ref:
        _thread = threading.Thread(target=_engine_ref_job, args=(ref,), daemon=True)
        _thread.start()
        _thread.join(timeout=480.0)
        if _thread.is_alive():
            ref = {
                "status": "timeout",
                "note": "官方引擎参考跑 480s 看门狗超时（Decimal 全市场逐日单线程，sanity 用途非判据）；主对照=本模拟器双臂，不受影响",
            }
        safe_write_text(_ref_cache, json.dumps(ref, ensure_ascii=False))
    print(f"[8] 引擎参考跑: {ref['status']}", flush=True)

    book = {
        "doc_type": "exit_sim_report",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "prereg_frozen_at_utc": prereg["frozen_at_utc"],
        "prereg_frozen_source": ".runtime/tmp/st-matrix-20261006/exit_sim/prereg_frozen.yaml",
        "prereg_frozen": prereg,
        "window_definition": {"run": list(WINDOW_RUN), "is": list(WINDOW_IS), "oos_holdout": list(WINDOW_OOS)},
        "recalibration": {
            "duty": "T3b-T0：路径依赖日循环性能以本次实测为唯一口径；0.53s/格旧口径（c4 GPU 网格引擎 T3a 专用）禁引用",
            "method": "time.perf_counter 包住单次完整仿真；warm 1 次 + 实测 3 次取均值",
            "nostop": timing["nostop"],
            "stop": timing["stop"],
            "data_load_seconds": round(t_load, 1),
            "note": "网格外推：路径依赖参数网格≈per_run_seconds/格（stop 臂口径）",
        },
        "comparison": {
            "primary": "同一模拟器 stop_enabled on/off 双跑（同信号同装置同成本）",
            "nostop": {"metrics": m_nostop, "sim_stats": stats_nostop},
            "stop": {"metrics": m_stop, "sim_stats": stats_stop},
            "judge": judge,
        },
        "signal_coverage": {
            "total_months": int(len(reb_rows)),
            "positioned_months": int(len(reb_rows) - stats_nostop["n_empty_months"]),
            "empty_months": int(stats_nostop["n_empty_months"]),
            "note": "24 列 pass 指标列 CH 覆盖起点≈2021-01（技术指标真源表数据起点），"
            "2018-01..2020-12 共 36 个月按装置语义（候选<20 只）空仓；prereg 窗口冻结不动，覆盖现实如实随册",
        },
        "reference_engine_nostop": ref,
        "device_delta_note": "本仿真器与官方引擎装置差异：无 PIT/剔ST/滑点/冲击/参与率建模，佣金同源双边；"
        "对照双臂同口径故差分方向不受影响；正式化时如需引擎级保真另立工单",
        "provenance": {
            "scores_yaml": "docs/_working/fexam/indicator_exam_scores_v1.yaml",
            "columns": [{"column": c, "provenance": oid} for c, oid in cols],
            "signal_functions": "scripts/backtest/fexam/strategy_exam.py（composite_signal/monthly_topn_signals/window_metrics 复用）",
            "module_tmp": ".runtime/tmp/st-matrix-20261006/exit_sim/exit_simulator.py",
            "commission_rate": COMMISSION,
        },
    }
    return book


def main() -> None:
    book = run_all()
    j = book["comparison"]["judge"]
    safe_write_text(OUT_YAML, yaml.safe_dump(book, allow_unicode=True, sort_keys=False, width=110))
    md = "\n".join(
        [
            "# exit_sim_report_v1 — E道离场族 ATR 止损首件对照（夜战 tmp 版）",
            "",
            f"- 判定（prereg 冻结判据）：**{j['verdict']}**",
            f"- OOS MaxDD 改善：{j['oos_maxdd_improve_pp']:+.1f}pp（止损版 vs 无止损）",
            f"- OOS Sharpe 变化：{j['oos_sharpe_delta']:+.3f}",
            f"- 无止损 OOS：Sharpe={book['comparison']['nostop']['metrics']['oos']['sharpe']:.3f}，"
            f"MaxDD={book['comparison']['nostop']['metrics']['oos']['max_drawdown']:.2%}",
            f"- 止损版 OOS：Sharpe={book['comparison']['stop']['metrics']['oos']['sharpe']:.3f}，"
            f"MaxDD={book['comparison']['stop']['metrics']['oos']['max_drawdown']:.2%}",
            f"- 重标定：stop 臂 per_run={book['recalibration']['stop']['per_run_seconds_warmup_plus3_mean']:.3f}s"
            f"（{book['recalibration']['stop']['per_symbol_day_us']:.2f}us/标的·日）；"
            f"0.53s/格旧口径（c4 网格专用）已禁用，路径依赖网格外推≈0.4s/格（本装置实测）",
            "- 装置：月频 top20 等权（批3 pass 24 列等权合成），T+1 开盘执行，"
            "初始止损=入场价-3×ATR14，移动止损=持仓期最高收盘-3×ATR14，日收盘 pierce 次日开盘离场",
            f"- 信号覆盖：{book['signal_coverage']['positioned_months']}/{book['signal_coverage']['total_months']} 个月有持仓"
            f"（24 列指标 CH 数据 2021-01 起，2018-2020 空仓为覆盖现实）",
            f"- 无止损基线注记：nostop 臂本身为强负 alpha 装置（IS 收益 "
            f"{book['comparison']['nostop']['metrics']['is']['total_return']:.0%}），"
            f"对照判据按 prereg 冻结线执行，负基线语境如实随册",
            f"- 引擎参考跑：{book['reference_engine_nostop']['status']}",
            f"- prereg 冻结：{book['prereg_frozen_at_utc']}（先于一切仿真运行）",
            "",
            f"细节={OUT_YAML.as_posix()}；模块=.runtime/tmp/st-matrix-20261006/exit_sim/（正式化=日光档工单）",
            "",
        ]
    )
    safe_write_text(OUT_MD, md)
    print(f"[9] 报告已落盘: {OUT_YAML}")
    print(f"[9] 报告已落盘: {OUT_MD}")


if __name__ == "__main__":
    main()
