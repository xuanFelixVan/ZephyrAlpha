# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 批2 策略全量考
# [MODULE] scripts.backtest.fexam.strategy_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine（MOD-BT-001 复用，禁重造引擎）;
#                zephyr.backtest.core.n_trial_ledger（DSR 记账复用）;
#                scripts.backtest.fexam.ch_data; scripts.backtest.fexam.roster
# [CONSUMERS] run_fexam.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 标准化装置口径（prereg 冻结）：alpha_sources 等权合成→月频 top20 等权→引擎
#              （PIT/剔ST/T+1/参与率/冲击成本全默认开）；一次连续跑 nav 分段 IS/OOS；
#              checkpoint 幂等可续跑；sanity guard 触发=该策略 verdict=rework(engine_error) 不绕过；
#              DSR：全批一次 record_run 幂等入 N 账本；分数册不回写地图（D124 另批）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单策略引擎异常→rework(engine_error) 继续；数据拉取失败→fail-closed 上抛
# [TESTS] tests/backtest/fexam/test_strategy_exam.py
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（harness口径禁改）
# [TTL] permanent
# create-guard-not-dup: 策略全量考标准化装置（引擎复用非重造），无既有等价物
"""strategy_exam — 批2：161 策略整装全量考（IS/OOS 双窗 Sharpe + DSR + 最大回撤 + 体制切片）。

诚实边界（prereg 冻结）：
- 考的是「策略的 alpha_sources 在标准装置上的表现」，非其全部定制逻辑
  （entry_logic/exit_logic/position_sizing 多为设计态文本，逐策略定制回测=L 级另行登记）。
- non_quantified（alpha_sources 空或全部不可解析）→ rework 如实登记，禁造凑数。
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
for _p in (str(RUN_ROOT / "scripts" / "backtest" / "fexam"), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ch_data  # noqa: E402
from roster import PREREG_V1  # noqa: E402

from zephyr.backtest.core.n_trial_ledger import TrialLedger  # noqa: E402
from zephyr.backtest.implementations.vectorized_engine import (  # noqa: E402
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

#: 连续跑窗：起点受引擎逐日循环性能约束（2018 起覆盖 2018 牛熊+2022-2024 震荡两轮体制，
#: 且 regime 真源自 2019-04 全覆盖 OOS）；终点=数据真源末班 2026-09-30。
WINDOW_RUN = ("2018-01-02", "2026-09-30")
WINDOW_IS = ("2018-01-02", "2025-09-30")
#: OOS = HOLDOUT（与批1/批3 同一干净窗，严格分离）
TRADING_DAYS_PER_YEAR = 244
BATCH_ID = "fexam-strategies-20261006"
_EPS = 1e-9


# ---------- 纯函数（单测面） ----------


def composite_signal(columns: dict[str, pd.DataFrame], directions: dict[str, int]) -> pd.DataFrame:
    """多列等权合成信号：逐列截面秩 pct（short 方向取 1-pct），逐日均值。"""
    ranked = []
    for key, panel in columns.items():
        r = panel.rank(axis=1, pct=True)
        if directions.get(key, 1) < 0:
            r = 1.0 - r
        ranked.append(r)
    stacked = pd.concat(ranked)
    return stacked.groupby(level=0).mean()


def monthly_topn_signals(composite: pd.DataFrame, trading_dates: pd.DatetimeIndex, top_n: int = 20) -> pd.DataFrame:
    """月频调仓信号：月首交易日截面取 top_n 等权 1/top_n，其余日持仓前向填充（步进函数）。"""
    dates = [d for d in trading_dates if d in composite.index]
    if not dates:
        return pd.DataFrame()
    month_starts: list[pd.Timestamp] = []
    seen_month: set[tuple[int, int]] = set()
    for d in dates:
        key = (d.year, d.month)
        if key not in seen_month:
            seen_month.add(key)
            month_starts.append(d)
    reb = pd.DataFrame(0.0, index=pd.DatetimeIndex(month_starts), columns=composite.columns)
    for d in month_starts:
        row = composite.loc[d].dropna()
        if len(row) < top_n:
            continue
        top = row.nlargest(top_n).index
        reb.loc[d, top] = 1.0 / top_n
    # 步进函数：只在调仓日有权重行，reindex 到全部交易日前填（清零语义由 0 值行携带，禁 replace-nan-ffill）
    weights = reb.reindex(trading_dates).ffill().fillna(0.0)
    return weights


def window_metrics(nav: pd.Series, start: str, end: str) -> dict[str, float]:
    """nav 分段指标：sharpe（年化 244）+ 最大回撤 + 累计收益。"""
    seg = nav.loc[(nav.index >= pd.Timestamp(start)) & (nav.index <= pd.Timestamp(end))]
    if len(seg) < 20:
        return {
            "sharpe": float("nan"),
            "max_drawdown": float("nan"),
            "total_return": float("nan"),
            "n_days": int(len(seg)),
        }
    ret = seg.pct_change().dropna()
    std = float(ret.std(ddof=0))
    sharpe = float(float(ret.mean()) / std * np.sqrt(TRADING_DAYS_PER_YEAR)) if std > _EPS else 0.0
    peak = seg.cummax()
    maxdd = float(((seg - peak) / peak).min())
    total = float(seg.iloc[-1] / seg.iloc[0] - 1.0)
    return {"sharpe": sharpe, "max_drawdown": maxdd, "total_return": total, "n_days": int(len(seg))}


def regime_sharpe(nav: pd.Series, regimes: pd.Series) -> dict[str, dict[str, float]]:
    """分段 nav 收益按 regime 分组 sharpe（样本<30 日标 n/a）。"""
    ret = nav.pct_change().dropna()
    joined = pd.concat([ret.rename("r"), regimes.rename("regime")], axis=1, join="inner").dropna()
    out: dict[str, dict[str, float]] = {}
    for label, grp in joined.groupby("regime"):
        std = float(grp["r"].std(ddof=0))
        n = int(len(grp))
        if n < 30:
            out[str(label)] = {"sharpe": float("nan"), "n_days": n}
        else:
            out[str(label)] = {
                "sharpe": float(float(grp["r"].mean()) / std * np.sqrt(TRADING_DAYS_PER_YEAR)) if std > _EPS else 0.0,
                "n_days": n,
            }
    return out


def judge_strategy(
    *, is_sharpe: float, oos_sharpe: float, oos_maxdd: float, pass_line: dict[str, Any]
) -> tuple[str, str]:
    """三态机判（prereg）。is/oos 任一 NaN → rework(engine_metric_missing)。"""
    if any(map(lambda v: v != v, (is_sharpe, oos_sharpe, oos_maxdd))):
        return "rework", "engine_metric_missing（窗内交易日不足）"
    if is_sharpe < 0 and oos_sharpe < 0:
        return "retire_candidate", f"双窗负Sharpe（is={is_sharpe:.2f}, oos={oos_sharpe:.2f}）"
    if (
        oos_sharpe >= float(pass_line["oos_sharpe_min"])
        and is_sharpe >= float(pass_line["is_sharpe_min"])
        and oos_maxdd >= -float(pass_line["oos_maxdd_max"])
    ):
        return "pass", "prereg线全过"
    return "rework", (f"is_sharpe={is_sharpe:.2f} oos_sharpe={oos_sharpe:.2f} oos_mdd={oos_maxdd:.2%}")


# ---------- 批执行 ----------


def _load_run_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """引擎输入（一次拉取全批共用）：flat data（date/symbol/open/close/volume）+ close 面板 + volume 面板。"""
    close = ch_data.load_close(*WINDOW_RUN)
    open_p = ch_data.load_panel(ch_data.T_KLINE_DAILY_HFQ, "open", *WINDOW_RUN)
    vol = ch_data.load_panel(ch_data.T_KLINE_DAILY_HFQ, "volume", *WINDOW_RUN)
    common_idx = close.index.intersection(open_p.index).intersection(vol.index)
    close, open_p, vol = close.loc[common_idx], open_p.loc[common_idx], vol.loc[common_idx]
    flat = pd.DataFrame(
        {
            "date": close.index.repeat(close.shape[1]),
            "symbol": np.tile(close.columns.values, len(close.index)),
            "open": open_p.values.reshape(-1),
            "close": close.values.reshape(-1),
            "volume": vol.values.reshape(-1),
        }
    )
    flat = flat.dropna(subset=["close"])
    return flat, close, vol


def run_exam(
    roster: dict[str, Any],
    out_path: Path,
    ckpt_path: Path,
    *,
    session_id: str = "st-matrix-20261006",
) -> dict[str, Any]:
    """批2主入口。幂等：ckpt 已完成策略跳过；DSR 全批一次幂等记账。"""
    pass_line = PREREG_V1["strategy_pass_line"]
    device = PREREG_V1["strategy_device"]
    strategies = roster["strategy"]
    factor_map = {f["object_id"]: f for f in roster["factor"]}

    done: dict[str, dict[str, Any]] = {}
    if ckpt_path.exists():
        for line in ckpt_path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                done[rec["object_id"]] = rec
            except (json.JSONDecodeError, KeyError):
                continue

    flat, close, _vol = _load_run_data()
    # 裁定#489②：默认 SMA200 帘子（regime_source="sma200_default"）；HMM 未过考禁回用
    regimes, regime_source = ch_data.regime_series(*WINDOW_RUN)
    engine = DefaultBacktestEngine(BacktestConfig())

    col_panels: dict[tuple[str, str], pd.DataFrame] = {}
    results: list[dict[str, Any]] = []
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)

    with ckpt_path.open("a", encoding="utf-8") as ck:
        for stg in strategies:
            sid = stg["object_id"]
            if sid in done:
                results.append(done[sid])
                continue
            if stg["bucket"] != "harness_examinable":
                rec = {
                    "object_id": sid,
                    "kind": "strategy",
                    "bucket": stg["bucket"],
                    "verdict": "rework",
                    "reason": "alpha_sources 空或全部不可解析（未量化/缺CH列）——如实登记禁造凑数",
                    "missing_recipe_flags": stg.get("missing_recipe_flags") or [],
                    "metrics": {},
                }
            else:
                directions: dict[str, int] = {}
                cols: dict[str, pd.DataFrame] = {}
                try:
                    for fid in stg["backed_alpha_sources"]:
                        fmeta = factor_map[fid]
                        table, column = fmeta["ch_backings"][0].rsplit(".", 1)  # db.table.column 三段式
                        key = f"{table}.{column}"
                        if key not in col_panels:
                            col_panels[key] = ch_data.load_panel(table, column, *WINDOW_RUN)
                        panel = col_panels[key]
                        if panel.empty:
                            continue
                        cols[fid] = panel
                        directions[fid] = -1 if str(fmeta.get("direction") or "").lower() == "short" else 1
                    if not cols:
                        rec = {
                            "object_id": sid,
                            "kind": "strategy",
                            "bucket": stg["bucket"],
                            "verdict": "rework",
                            "reason": "backed列窗内全空数据",
                            "metrics": {},
                        }
                    else:
                        composite = composite_signal(cols, directions)
                        signals = monthly_topn_signals(composite, close.index, top_n=int(device["top_n"]))
                        result = engine.run(flat, signals, strategy_name=sid)
                        nav = engine.last_portfolio.nav_series
                        nav = nav[~nav.index.isna()]
                        is_m = window_metrics(nav, *WINDOW_IS)
                        oos_m = window_metrics(nav, *ch_data.WINDOW_HOLDOUT)
                        verdict, reason = judge_strategy(
                            is_sharpe=is_m["sharpe"],
                            oos_sharpe=oos_m["sharpe"],
                            oos_maxdd=oos_m["max_drawdown"],
                            pass_line=pass_line,
                        )
                        rec = {
                            "object_id": sid,
                            "kind": "strategy",
                            "bucket": stg["bucket"],
                            "verdict": verdict,
                            "reason": reason,
                            "alpha_used": sorted(cols),
                            "engine_run_id": result.idempotency_key,
                            "engine": {
                                "trades_count": result.trades_count,
                                "win_rate": result.win_rate,
                                "overfitting_flag": result.overfitting_flag,
                            },
                            "metrics": {
                                "is": is_m,
                                "oos": oos_m,
                                "regime_sharpe": regime_sharpe(nav, regimes),
                            },
                            "activation_suggestion": (
                                {"lifecycle": "paper", "weight_band": pass_line["activation_weight_band"]}
                                if verdict == "pass"
                                else None
                            ),
                        }
                except Exception as exc:  # noqa: BLE001 — 单策略异常=该策略 rework，批不中断（ERROR_CONTRACT）
                    rec = {
                        "object_id": sid,
                        "kind": "strategy",
                        "bucket": stg["bucket"],
                        "verdict": "rework",
                        "reason": f"engine_error: {type(exc).__name__}: {exc}"[:220],
                        "metrics": {},
                    }
            results.append(rec)
            ck.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            ck.flush()

    n_runs = sum(1 for r in results if r.get("engine_run_id"))
    ledger_note = f"fexam batch2 evidence={out_path.as_posix()}; windows={WINDOW_RUN}+{ch_data.WINDOW_HOLDOUT}"
    try:
        dsr = TrialLedger().record_run(
            kind="fexam_strategy_batch",
            batch_id=BATCH_ID,
            n_trials=n_runs,
            note=ledger_note,
            recorded_by=session_id,
        )
    except Exception as exc:  # noqa: BLE001 — 账本不可用不伪造记账，如实留痕
        dsr = {"status": "ledger_error", "error": str(exc)[:160]}

    counts: dict[str, int] = {"total": len(results)}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    book = {
        "doc_type": "fexam_strategy_scores",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "prereg_v1": PREREG_V1,
        "window_definition": {
            "run": list(WINDOW_RUN),
            "is": list(WINDOW_IS),
            "oos_holdout": list(ch_data.WINDOW_HOLDOUT),
            "separation_note": "单次连续跑 nav 按 IS/OOS 时间分段；OOS=近12月干净窗与批1/批3同窗",
        },
        "device_ledger": [
            {
                "object": "strategy_exam",
                "device": "cpu",
                "reason": "vectorized_engine(MOD-BT-001)为CPU逐日引擎，无cupy核；"
                "0.53s/格口径属c4网格引擎（T3a专用），批2为逐策略单跑不适用；"
                "成本大头=数据一次拉取（全批摊薄）",
            },
        ],
        "harness_note": "策略考=alpha_sources等权合成在标准装置(top20/月频/等权/PIT/剔ST/T+1)上的表现；"
        "非策略全部定制逻辑（定制回测=L级另行登记）",
        "regime_source": regime_source,
        "dsr_ledger": {
            "batch_id": BATCH_ID,
            "n_trials": n_runs,
            "record": dsr,
            "note": "DSR折减只记账不计入本批判定（判定用OOS干净窗，试次折减随册呈报）",
        },
        "counts": counts,
        "results": results,
    }
    from zephyr.shared.io.file_utils import safe_write_text

    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out_path, yaml.safe_dump(book, allow_unicode=True, sort_keys=False, width=120))
    return book
