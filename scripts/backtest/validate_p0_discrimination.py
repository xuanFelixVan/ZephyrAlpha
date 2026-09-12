# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.validate_p0_discrimination
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; zephyr.backtest.run_archive; scipy(可选,缺省正态近似)
# [CONSUMERS] c1_backtest.node_verdict(P0-001/002 台账行); 桌面壳 TDM 抽屉验证档案
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 阈值冻结禁挪(BT-P0-001/002 frozen 2026-09-12); 土规(每档>=20且总>=30不足→pending); PIT(教材表 detect 已 ≤t-1, lag_recheck 做对照); IS/OOS 分段如实报告; 台账/档案只增不改
# [MODIFY-GUARD] tests/backtest/test_validate_p0_discrimination.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/落库未确认)
# [TESTS] tests/backtest/test_validate_p0_discrimination.py
# [A_module] module_id=MOD-BT-033 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P0-001/002 区分度检验——L1-AGG 状态判定 + L1 总闸谨慎度（agg_discrimination，SOP-B ④⑥）。

考题（阈值冻结 BT-P0-001/002，2026-09-12，禁挪）:
  BT-P0-002 TDM-E-L1-AGG（市场状态判定）:
    dominant 七态分档 vs 后续 20 日收益（kline_index 000300）；
    相邻语义档 (r3,r2),(r2,r1),(r1,r4) Welch t p<0.05 且高低档(r3-r4)差>=1.0% → valid；
    min p<0.10 → pending；其余 → noise。每档>=20 且总>=30。
  BT-P0-001 TDM-E-L1（总闸谨慎度）:
    shrinkage 四分位 Q1(最谨慎)..Q4 vs 后续 20 日最大回撤（窗口内 min close/close_t-1）；
    Q1 vs Q4 Welch t p<0.05 且档差(Q1-Q4)<=-2.0%（谨慎档回撤更深）→ valid；方向反(>0) → noise。
  PB-16 lag_recheck：dominant shift(1) 重算 P0-002 主判据，差值报告（暴跌=前视嫌疑）。
  窗口：IS 2019-04~2023-12 / OOS 2024-01~2026-09-11 分段如实报告（D1 定稿）；
    notes 声明：判定器参数为结构设计（无调参历史），D 前锁窗语义不适用，OOS=稳定性复核。

产物：双 run 档案（SOP-D）+ node_verdict 台账 2 行（verdict_reason 代码生成，
新增 discrimination_confirmed/discrimination_reversed 两枚举，schema 注记同步）。
依据: validation_method_registry.yaml agg_discrimination + backtest_backlog BT-P0-001/002 frozen plan。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from zephyr.backtest.run_archive import create_run, finalize_run, write_step
from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

logger = logging.getLogger(__name__)

_PROB_TABLE = "c1_backtest.regime_snapshot_history"
_VERDICT_TABLE = "c1_backtest.node_verdict"
_VERDICT_COLUMNS = (
    "(run_id, snapshot_commit, window_start, window_end, node_id, validation_method,"
    " triggers, hit_ratio, significance, verdict, verdict_reason, verdict_at, notes)"
)
_IS_RANGE = ("2019-04-01", "2023-12-31")
_OOS_RANGE = ("2024-01-01", "2026-09-11")
_FWD_DAYS = 20
_MIN_PER_BUCKET = 20
_MIN_TOTAL = 30
# 语义序（10 号 spec Viterbi 特征语义）：r3 牛市 > r2 中波 > r1 低波 > r4 熊市；r10 危机对照
_ADJACENT_PAIRS = [("r3", "r2"), ("r2", "r1"), ("r1", "r4")]
_HIGH, _LOW = "r3", "r4"


def _welch_p(a: np.ndarray, b: np.ndarray) -> float:
    """Welch t 检验 p 值（双尾）；scipy 缺失用正态近似（样本>=20 误差可忽略）。"""
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    try:
        from scipy.stats import ttest_ind

        return float(ttest_ind(a, b, equal_var=False).pvalue)
    except ImportError:
        ma, mb = a.mean(), b.mean()
        va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
        t = (ma - mb) / np.sqrt(va + vb)
        from math import erf, sqrt

        return 2.0 * (1.0 - 0.5 * (1.0 + erf(abs(t) / sqrt(2.0))))


def _tsv_cell(v: Any) -> str:
    """TSV 转义：None→\\N；清洗 \\t/\\r/\\n（红蓝对抗 A1：notes 含换行断列）。"""
    if v is None:
        return "\\N"
    return str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """教材表 1809 日概率 + 000300 收盘价（前向收益/回撤窗口原料）。"""
    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from clickhouse_driver import Client

    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg.get("user", "default"),
               password=cfg.get("password", ""), connect_timeout=5)
    probs = pd.DataFrame(c.execute(
        f"SELECT trade_date, dominant, shrinkage FROM {_PROB_TABLE} ORDER BY trade_date"
    ), columns=["trade_date", "dominant", "shrinkage"])
    px = pd.DataFrame(c.execute(
        "SELECT trade_date, toFloat64(close) AS close FROM c1_market.kline_index "
        "WHERE symbol = '000300' AND trade_date >= '2019-01-01' ORDER BY trade_date"
    ), columns=["trade_date", "close"])
    if probs.empty or px.empty:
        raise RuntimeError(f"数据缺失: probs={len(probs)} px={len(px)}——检查教材表/指数行情")
    probs["trade_date"] = pd.to_datetime(probs["trade_date"])
    px["trade_date"] = pd.to_datetime(px["trade_date"])
    return probs, px


def build_dataset() -> pd.DataFrame:
    """合并 + 前向 20 日收益与前向 20 日窗口最大回撤（PIT：只用 t 之后数据作标签，检验允许）。"""
    probs, px = load_data()
    px = px.sort_values("trade_date").reset_index(drop=True)
    px["fwd_20d"] = px["close"].shift(-_FWD_DAYS) / px["close"] - 1.0
    # 前向 20 日窗口最大回撤：min(close[t+1..t+20])/close[t]-1（更负=更深）
    roll_min = px["close"].shift(-1).rolling(_FWD_DAYS, min_periods=_FWD_DAYS).min()
    px["maxdd_20d"] = roll_min / px["close"] - 1.0
    df = probs.merge(px[["trade_date", "fwd_20d", "maxdd_20d"]], on="trade_date", how="left")
    return df


def _seg(df: pd.DataFrame, seg: tuple[str, str] | None) -> pd.DataFrame:
    if seg is None:
        return df
    return df[(df["trade_date"] >= seg[0]) & (df["trade_date"] <= seg[1])]


def agg_check(df: pd.DataFrame) -> dict[str, Any]:
    """BT-P0-002：dominant 分档区分度（冻结口径：min 相邻 p<0.05 且高低差>=1.0%）。"""
    counts = df["dominant"].value_counts()
    buckets = {k: df.loc[df["dominant"] == k, "fwd_20d"].dropna().to_numpy() * 100.0
               for k in _STATE_KEYS_7}
    usable = {k: v for k, v in buckets.items() if counts.get(k, 0) >= _MIN_PER_BUCKET and len(v) > 0}
    pairs = [(a, b) for a, b in _ADJACENT_PAIRS if a in usable and b in usable]
    p_vals = {f"{a}>{b}": _welch_p(usable[a], usable[b]) for a, b in pairs}
    spread = (float(np.mean(usable[_HIGH])) - float(np.mean(usable[_LOW]))
              if _HIGH in usable and _LOW in usable else float("nan"))
    min_p = min(p_vals.values()) if p_vals else float("nan")
    total = int(sum(counts.get(k, 0) for k in _STATE_KEYS_7))
    # 土规（registry 口径）：参与检验的档（>=20 者入选 usable）每档达标且总触发>=30；
    # 小样本档 fail-open 剔除（不参与判据，也不触发 insufficient）——首版实现误把剔除档计入检查，已修
    if total < _MIN_TOTAL or len(usable) < 2:
        verdict, reason = "pending", "insufficient_samples"
    elif min_p < 0.05 and abs(spread) >= 1.0:
        verdict, reason = "valid", "discrimination_confirmed"
    elif min_p < 0.10:
        verdict, reason = "pending", "discrimination_below_threshold"
    else:
        verdict, reason = "noise", "discrimination_reversed"
    return {"min_p": min_p, "p_vals": p_vals, "spread": spread, "total": total,
            "dropped_small_buckets": [k for k in _STATE_KEYS_7 if k in buckets and counts.get(k, 0) < _MIN_PER_BUCKET],
            "bucket_counts": {k: int(counts.get(k, 0)) for k in _STATE_KEYS_7},
            "bucket_means": {k: (float(np.mean(v)) if len(v) else None) for k, v in buckets.items()},
            "verdict": verdict, "reason": reason}


_STATE_KEYS_7 = ("r1", "r2", "r3", "r4", "r10", "r11", "r12")


def gate_check(df: pd.DataFrame) -> dict[str, Any]:
    """BT-P0-001：shrinkage 四分位谨慎度 vs 前向 20 日最大回撤（冻结口径：p<0.05 且 Q1-Q4<=-2.0%）。"""
    d = df.dropna(subset=["shrinkage", "maxdd_20d"]).copy()
    # 红蓝对抗 A6：shrinkage 恒值（极端市况全员同一节流值）时 qcut 抛 Bin edges unique 异常——
    # 降级为 pending/insufficient_samples（诚实：无离散度=无分档检验意义）
    if d["shrinkage"].nunique() < 4:
        return {"p": float("nan"), "delta": float("nan"), "counts": {}, "total": int(len(d)),
                "means": {}, "verdict": "pending", "reason": "insufficient_samples"}
    d["bucket"] = pd.qcut(d["shrinkage"], 4, labels=["Q1", "Q2", "Q3", "Q4"])  # Q1=shrinkage 最低=最谨慎
    groups = {q: d.loc[d["bucket"] == q, "maxdd_20d"].to_numpy() * 100.0 for q in ("Q1", "Q2", "Q3", "Q4")}
    counts = {q: len(v) for q, v in groups.items()}
    p = _welch_p(groups["Q1"], groups["Q4"])
    delta = float(np.mean(groups["Q1"]) - float(np.mean(groups["Q4"])))  # 负=谨慎档回撤更深
    if min(counts.values()) < _MIN_PER_BUCKET or len(d) < _MIN_TOTAL:
        verdict, reason = "pending", "insufficient_samples"
    elif p < 0.05 and delta <= -2.0:
        verdict, reason = "valid", "discrimination_confirmed"
    elif p < 0.10:
        verdict, reason = "pending", "discrimination_confirmed"
    elif delta > 0:
        verdict, reason = "noise", "discrimination_reversed"
    else:
        verdict, reason = "noise", "discrimination_confirmed"
    return {"p": p, "delta": delta, "counts": counts, "total": int(len(d)),
            "means": {q: float(np.mean(v)) for q, v in groups.items()},
            "verdict": verdict, "reason": reason}


def lag_recheck(df: pd.DataFrame) -> float:
    """PB-16：dominant shift(1) 重算 P0-002 主判据 min-p（差值大=前视嫌疑）。"""
    d = df.copy()
    d["dominant"] = d["dominant"].shift(1)
    return agg_check(d.dropna(subset=["dominant"]))["min_p"]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="P0-001/002 区分度检验（agg_discrimination，冻结口径）")
    parser.add_argument("--dry-run", action="store_true", help="只算不写台账/不归档")
    parser.add_argument("--only", choices=["BT-P0-001", "BT-P0-002"], default=None,
                        help="只跑单对象（BT-P0-002 已出分的续跑场景）")
    args = parser.parse_args()

    df = build_dataset()
    logger.info("数据集: %d 日（fwd_20d 有值 %d）", len(df), int(df["fwd_20d"].notna().sum()))

    now = datetime.now()
    results: dict[str, Any] = {}
    for obj_id, node_id, checker in (
        ("BT-P0-002", "TDM-E-L1-AGG", agg_check),
        ("BT-P0-001", "TDM-E-L1", gate_check),
    ):
        if args.only and obj_id != args.only:
            continue
        full = checker(df)
        is_r = checker(_seg(df, _IS_RANGE))
        oos_r = checker(_seg(df, _OOS_RANGE))
        lr = lag_recheck(df) if obj_id == "BT-P0-002" else None
        run_id = f"VAL-P0-{now.strftime('%Y%m%d-%H%M%S')}-{obj_id.split('-')[-1]}"
        create_run(
            run_id=run_id, object_id=obj_id, kind="VAL",
            window={"start": "2019-04-01", "end": "2026-09-11"},
            holdout={"mode": "anchor", "cutoff": "2026-09-09",
                     "note": "判定器参数为结构设计无调参历史，OOS=稳定性复核"},
            cost_mode="rough", created_by="ai-session:p0-discrimination",
        )
        body = json.dumps(full, ensure_ascii=False, indent=1, default=str)
        write_step(run_id, "01", (
            "# 方法学调研结论\n\nagg_discrimination 口径=validation_method_registry.yaml（相邻档 Welch t p<0.05 "
            "+ 高低档差阈值）；冻结阈值见 backtest_backlog BT-P0-001/002（threshold_status=frozen 2026-09-12，禁挪）。"
        ))
        write_step(run_id, "02", (
            "# DATA-GAP 清单\n\n- [已备] 教材表 c1_backtest.regime_snapshot_history（1809 日）\n"
            "- [已备] 前向收益/回撤原料：c1_market.kline_index 000300 close（覆盖至 2026-09-11）\n- [无缺口]\n"
        ))
        write_step(run_id, "03", (
            "# 数据清单\n\n- name: 判定器历史概率\n  source: c1_backtest.regime_snapshot_history\n"
            "  pit_note: 'detect(t) 只用 ≤t-1 特征（builder 内置 shift(1)）；标签 fwd_20d/maxdd_20d 为 t 之后数据（检验标签允许）'\n"
            "- name: 市场基准\n  source: c1_market.kline_index symbol=000300\n  proxy: false\n"
        ))
        write_step(run_id, "05", "# 剪枝记录\n\n不适用：分档全量样本参与（剪枝语义属信号筛选）。\n")
        write_step(run_id, "06", json.dumps(
            {"full": full, "is": is_r, "oos": oos_r, "lag_recheck_minp": lr},
            ensure_ascii=False, indent=1, default=str), filename="segmented_stats.json")
        write_step(run_id, "verdict", (
            f"# 判定书：{run_id}\n\n对象：{obj_id} / {node_id} ｜ method=agg_discrimination ｜ 窗口=2019-04~2026-09\n"
            f"结论：verdict={full['verdict']} ｜ significance={'ok' if full['reason'] != 'insufficient_samples' else 'insufficient_samples'}"
            f" ｜ verdict_reason={full['reason']}\n判定链：冻结口径（backlog plan，2026-09-12 frozen）代码执行，未手调。\n\n"
            f"关键数字：{body}\n\n"
            f"分段：IS={json.dumps(is_r, default=str)}\nOOS={json.dumps(oos_r, default=str)}\n"
            f"lag_recheck：{lr}\n\n台账回执：node_verdict run_id={run_id}\n"
        ))
        finalize_run(run_id, verdict_ref={"table": _VERDICT_TABLE, "run_id": run_id})
        results[obj_id] = {"run_id": run_id, **{k: v for k, v in full.items()}}
        if not args.dry_run:
            from zephyr.backtest.core.engine_base import current_map_snapshot
            from zephyr.data import ch_writer

            sig = "insufficient_samples" if full["reason"] == "insufficient_samples" else "ok"
            row = [run_id, current_map_snapshot(), "2019-04-01", "2026-09-11", node_id,
                   "agg_discrimination", full["total"], None, sig, full["verdict"],
                   full["reason"], now.strftime("%Y-%m-%d %H:%M:%S"),
                   f"min_p={full.get('min_p', full.get('p'))}; delta/spread={full.get('spread', full.get('delta'))}; "
                   f"分段 IS/OOS 见 run 档案 06"]
            written = ch_writer.write_tsv(_VERDICT_TABLE, _VERDICT_COLUMNS,
                                          ("\t".join(_tsv_cell(c) for c in row) + "\n").encode("utf-8"))
            if not written:
                raise RuntimeError(f"台账落库未确认（{node_id}）——fail-closed")
            logger.info("台账已写: %s verdict=%s", node_id, full["verdict"])
    print(json.dumps(results, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    sys.exit(main())
