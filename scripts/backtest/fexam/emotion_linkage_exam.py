# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/mining/emotion_index_prereg_and_first_exam_v1.md | 情绪指数联动首考（裁定#489③ v1 三线）
# [MODULE] scripts.backtest.fexam.emotion_linkage_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; scripts.backtest.fexam.ch_data（冻结窗+CH 只读装载同门）; scripts.backtest.fexam.roster（PREREG_V1 及格线常量，禁抄写漂移）;
#                zephyr.data.ch_reader（严格读通道）; zephyr.data.table_registry（表名真源）; zephyr.shared.utils.time_utils.now_utc
# [CONSUMERS] 手工 CLI（python scripts/backtest/fexam/emotion_linkage_exam.py --out <json>）; prereg 卡 verdict 回填
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] prereg v2 冻结（emPrereg 卡 §2 逐字落地，禁现场改判据/改窗）: 主标签 fwd5_off=close(t+5)/close(t+1)-1
#              （t+1 起 5 日，信号日信息零重叠——v1"同步量无前瞻"缺陷治本）; 方向两可（|IC| 两向判定，
#              冻结节前声明）; 判定窗=HOLDOUT headline; 及格线=裁定#489③ v1 三线 AND（常量经 roster.PREREG_V1）;
#              PIT a-c 实测/d-e 冻结事实援引; CH 只读零 DB 写; 负结果如实入册禁软判
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 失败→ch_reader 严格通道异常上抛（fail-closed 禁伪造空卷）; FINAL 后同键多行→
#                  ExamDataError 上抛; 窗内月桶<6→该窗 n/a 判不达（不静默跳过）
# [TESTS] tests/backtest/fexam/test_emotion_linkage_exam.py
# [MODIFY-GUARD] docs/_working/matrix_campaign/mining/emotion_index_prereg_and_first_exam_v1.md（prereg 冻结块，禁现场改）
# [TTL] permanent
# create-guard-not-dup: 情绪指数单序列联动考（月度桶 Spearman+三线判定），与 ic_exam 截面板/strategy_exam 策略面无功能交集
"""emotion_linkage_exam — 情绪指数→大盘 forward 收益 联动首考（prereg v2 冻结口径）.

考卷真源: docs/_working/matrix_campaign/mining/emotion_index_prereg_and_first_exam_v1.md §2 冻结块。
- 信号: c1_market.emotion_index stage='close_final' e(t)（0-1 灰度分位）
- 代理: c1_market.kline_index 000300 close
- 主标签: fwd5_off(t) = close(t+5)/close(t+1) - 1（t+1 起 5 日，信号日零重叠）
- IC: 月度桶内 Spearman（有效对 <10 → NaN 月）；窗 IC=月度均值；ICIR=mean/std(ddof=0)
- 判定: HOLDOUT headline，|IC|>0.02 AND |ICIR|>0.3 AND retain=|IC_h|/|IC_r|>=0.5（三线 AND，
  及格线常量=roster.PREREG_V1["factor_pass_line"]，裁定#489③ v1）
- 敏感性 report-only: fwd5_old（上考旧口径）/fwd5_leg5（5 完整腿）/同期相关/滚动 20 日 IC
- PIT: a ts 时点/b asof 越界/c 同键异值 实测；d 构造 trailing/e 改写能力=冻结事实援引

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: CH 严格读信号+代理（query_rows，FINAL 注入，同键唯一断言）
# 层: 算法
# - id: A1
#   name_zh: 前向标签（t+1 起 5 日主标签+敏感性族）
# - id: A2
#   name_zh: 月度桶 Spearman IC 序列→窗统计→retain→三线判定
# - id: A3
#   name_zh: PIT a/b/c 实测复检（扩展窗）
# 层: 输出
# - id: O1
#   name: verdict JSON（staging 落盘+stdout 摘要）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
_FEXAM = RUN_ROOT / "scripts" / "backtest" / "fexam"
for _p in (str(_FEXAM), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ch_data  # noqa: E402
from roster import PREREG_V1  # noqa: E402

from zephyr.data import ch_reader  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

#: 表名真源=TableRegistry（#ARCH-CH-024，禁硬编码）
_TBL_EMO_INDEX = get_registry().table("market_emotion_index")
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")

#: NO-BARE-SQL：_SQL_* 常量唯一定义点（只读；FINAL 由 ch_reader 注入）
_SQL_EMO = (
    "SELECT trade_date, stage, ts, emotion_index, components, version, ingest_ts"
    f" FROM {_TBL_EMO_INDEX} WHERE stage='close_final' ORDER BY trade_date, ingest_ts"
)
_SQL_KLINE = f"SELECT trade_date, close FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' ORDER BY trade_date"

#: prereg v2 冻结常量（改此=改考卷，禁）
LABEL_H = 5
MIN_PAIRS_PER_BUCKET = 10
MIN_BUCKETS_PER_WINDOW = 6
EXAM_START, EXAM_END = "2005-01-04", "2026-09-30"  # 代理可得窗冻结（考窗起点=数据可得性）
STAGE = "close_final"
VERSION = "v0.1.0"
TS_SUFFIX = " 15:10:00"  # close_final 状态时戳口径（表设计；a 检判据）

#: 及格线=裁定#489③ v1（roster 常量引用，禁抄写漂移）
PASS_LINE: dict[str, Any] = PREREG_V1["factor_pass_line"]
WINDOW_HOLDOUT = ch_data.WINDOW_HOLDOUT
WINDOW_IS_REF = ch_data.WINDOW_IS_REF

#: 冻结事实援引（prereg 卡 §2.5 d/e；本考不重推，读数只作呈现）
PIT_D_FACT = (
    "builder _pctl=vals.tail(250) trailing+拉窗止于当日+C6 rolling+C5 asof（v1 冻结核验，git log 核验 builder 未变）"
)
PIT_E_FACT = "表级可重写实证在案（pre_open 2026-10-02 双行）；考窗无逐日快照留痕（单批 replay）；快照器 2026-10-08 上线后增量留痕开始"


class ExamDataError(RuntimeError):
    """考卷数据面违规（FINAL 后同键多行等）。fail-closed。"""


# ---------- 纯函数（单测面） ----------


def offset_labels(close: pd.Series, *, h: int = LABEL_H) -> pd.DataFrame:
    """前向标签族（PIT：t 日信号只用 t 及以前信息，标签只用 t 之后价格）。

    fwd5_off = close(t+h)/close(t+1) - 1（主标签，t+1 起 h 日）
    fwd5_old = close(t+h)/close(t) - 1（上考旧口径，敏感性对照）
    fwd5_leg5 = close(t+h+1)/close(t+1) - 1（t+1 起 h 条完整收益腿，敏感性对照）
    ret_t = close(t)/close(t-1) - 1（同期收益，同步性存档读数）
    """
    out = pd.DataFrame(index=close.index)
    out["fwd5_off"] = close.shift(-h) / close.shift(-1) - 1.0
    out["fwd5_old"] = close.shift(-h) / close - 1.0
    out["fwd5_leg5"] = close.shift(-(h + 1)) / close.shift(-1) - 1.0
    out["ret_t"] = close / close.shift(1) - 1.0
    return out


def monthly_ic(
    signal: pd.Series,
    label: pd.Series,
    *,
    min_pairs: int = MIN_PAIRS_PER_BUCKET,
    start: str | None = None,
    end: str | None = None,
) -> pd.Series:
    """月度桶内 Spearman IC 序列（index=月末 Timestamp）。有效对 <min_pairs → 该月 NaN。"""
    df = pd.concat({"e": signal, "lab": label}, axis=1).dropna()
    if start is not None:
        df = df[df.index >= pd.Timestamp(start)]
    if end is not None:
        df = df[df.index <= pd.Timestamp(end)]
    if df.empty:
        return pd.Series(dtype="float64", name="ic")
    months = df.groupby(df.index.to_period("M"))
    vals: dict[pd.Period, float] = {}
    for period, grp in months:
        if len(grp) < min_pairs:
            vals[period] = float("nan")
            continue
        r = grp["e"].corr(grp["lab"], method="spearman")
        vals[period] = float(r) if pd.notna(r) else float("nan")
    ser = pd.Series(vals).sort_index()
    ser.index = ser.index.to_timestamp()
    return ser.rename("ic")


def window_stats(ic: pd.Series, *, min_buckets: int = MIN_BUCKETS_PER_WINDOW) -> dict[str, Any]:
    """窗 IC 读数：均值/ICIR/有效月桶数。月桶 <min_buckets → n/a（判不达不静默）。"""
    valid = ic.dropna()
    n = int(len(valid))
    if n < min_buckets or n < 2:
        return {"ic_mean": None, "icir": None, "n_buckets": n, "na": True}
    mean = float(valid.mean())
    std = float(valid.std(ddof=0))
    icir = mean / std if std > 1e-12 else None
    return {"ic_mean": mean, "icir": icir, "n_buckets": n, "na": False}


def retain_stat(ic_h: float | None, ic_r: float | None) -> float | None:
    """retain = |IC_h| / |IC_r|（canon 口径取 |·|；分母 0/缺 → None=不可判）。"""
    if ic_h is None or ic_r is None or abs(ic_r) < 1e-12:
        return None
    return abs(ic_h) / abs(ic_r)


def judge(
    ic_h: float | None,
    icir_h: float | None,
    retain: float | None,
    pass_line: dict[str, Any] = PASS_LINE,
) -> tuple[bool, str]:
    """裁定#489③ v1 三线 AND（方向两可=|·| 判定，prereg §2.4 冻结）。返回 (过线, 明细)。"""
    ic_min = float(pass_line["abs_ic_min"])
    icir_min = float(pass_line["icir_min"])
    retain_min = float(pass_line["ic_retain_min"])
    if ic_h is None or icir_h is None:
        return False, f"headline 窗 n/a（月桶<{MIN_BUCKETS_PER_WINDOW}）判不达"
    if retain is None:
        return False, "retain 不可判（|IC_r|=0 或 IS_REF n/a）判不达"
    ok = abs(ic_h) > ic_min and abs(icir_h) > icir_min and retain >= retain_min
    detail = (
        f"|ic|={abs(ic_h):.4f}(线{ic_min}) |icir|={abs(icir_h):.2f}(线{icir_min}) "
        f"retain={retain:.2f}(线{retain_min}) → {'三线全过' if ok else '未全过'}"
    )
    return ok, detail


def check_ts_semantics(df: pd.DataFrame, start: str, end: str) -> dict[str, Any]:
    """PIT-a：考窗 close_final ts 时点=15:10:00 且 ts 日期=trade_date。

    ts 列经 ch_reader 为 tz-aware datetime（Asia/Shanghai）——先归一为 wall-time 字符串
    （strftime 只取日期+时分秒，剥时区尾缀），再比冻结口径后缀，防表示层假阳性。
    """
    sub = df[(df["td"] >= start) & (df["td"] <= end)]
    ts_fmt = pd.to_datetime(sub["ts"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    bad_suffix = int((~ts_fmt.str.endswith(TS_SUFFIX)).sum())
    bad_date = int((ts_fmt.str[:10] != sub["td"]).sum())
    return {"n": int(len(sub)), "ts_suffix_violations": bad_suffix, "ts_date_mismatch": bad_date}


def check_asof(df: pd.DataFrame, start: str, end: str) -> dict[str, Any]:
    """PIT-b：考窗 components 逐成分 asof ≤ trade_date（越界=前视）。"""
    sub = df[(df["td"] >= start) & (df["td"] <= end)]
    bad = 0
    per_comp: dict[str, int] = {}
    for row in sub.itertuples(index=False):
        comps = json.loads(row.components)
        for comp in comps:
            asof = str(comp.get("asof", "") or "")
            if asof and asof > row.td:
                bad += 1
                name = str(comp.get("name", "?"))
                per_comp[name] = per_comp.get(name, 0) + 1
    return {"n_rows": int(len(sub)), "asof_future_violations": bad, "per_component": per_comp}


def check_key_uniqueness(df: pd.DataFrame) -> dict[str, Any]:
    """PIT-c：FINAL 后同 (trade_date, stage) 键必须唯一行。"""
    dup = df[df.duplicated(subset=["td", "stage"], keep=False)]
    multi_val = 0
    if not dup.empty:
        multi_val = int(dup.groupby(["td", "stage"])["emotion_index"].nunique().gt(1).sum())
    return {"duplicate_keys": int(dup.groupby(["td", "stage"]).ngroups), "multi_value_keys": multi_val}


# ---------- IO（薄层） ----------


def load_signal() -> pd.DataFrame:
    """close_final 信号帧（td/ts/emotion_index/components/version），FINAL 唯一性断言。"""
    rows = ch_reader.query_rows(_SQL_EMO)
    df = pd.DataFrame(rows, columns=["td", "stage", "ts", "emotion_index", "components", "version", "ingest_ts"])
    df["td"] = df["td"].astype(str).str[:10]
    df["version"] = df["version"].astype(str)
    sub = df[df["version"] == VERSION].copy()
    chk = check_key_uniqueness(sub)
    if chk["duplicate_keys"] > 0 or chk["multi_value_keys"] > 0:
        raise ExamDataError(f"FINAL 后同键多行（PIT-c 违例）: {chk}")
    return sub


def load_proxy() -> pd.Series:
    """000300 收盘序列（index=DatetimeIndex）。"""
    rows = ch_reader.query_rows(_SQL_KLINE)
    df = pd.DataFrame(rows, columns=["td", "close"])
    ser = pd.Series(df["close"].astype(float).values, index=pd.to_datetime(df["td"]), name="close")
    return ser[~ser.index.duplicated(keep="last")].sort_index()


# ---------- 考试主流程 ----------


def run_exam(*, h: int = LABEL_H) -> dict[str, Any]:
    """按 prereg v2 冻结口径跑全考，返回 verdict 结构（纯读，无副作用）。"""
    sig = load_signal()
    proxy = load_proxy()
    e = pd.Series(sig["emotion_index"].astype(float).values, index=pd.to_datetime(sig["td"]), name="e")
    e = e[~e.index.duplicated(keep="last")].sort_index()

    union_start = max(e.index.min(), proxy.index.min())
    union_end = min(e.index.max(), proxy.index.max())
    e_w = e[(e.index >= union_start) & (e.index <= union_end)]
    labels = offset_labels(proxy, h=h)

    report: dict[str, Any] = {
        "prereg": "emotion_index_prereg_and_first_exam_v1.md §2（2026-10-08 冻结）",
        "pass_line": {
            "abs_ic_min": PASS_LINE["abs_ic_min"],
            "icir_min": PASS_LINE["icir_min"],
            "ic_retain_min": PASS_LINE["ic_retain_min"],
        },
        "data": {
            "signal_rows_close_final": int(len(sig)),
            "signal_range": [str(e.index.min().date()), str(e.index.max().date())],
            "proxy_rows": int(len(proxy)),
            "proxy_range": [str(proxy.index.min().date()), str(proxy.index.max().date())],
            "exam_window": [str(union_start.date()), str(union_end.date())],
            "aligned_signal_days_in_window": int(len(e_w)),
        },
    }

    # 主考：月度桶 IC → 三窗读数
    lab = labels["fwd5_off"].reindex(e_w.index)
    windows = {
        "holdout": WINDOW_HOLDOUT,
        "is_ref": WINDOW_IS_REF,
        "full_window": (str(union_start.date()), str(union_end.date())),
    }
    ics: dict[str, pd.Series] = {}
    stats: dict[str, dict[str, Any]] = {}
    for name, (w0, w1) in windows.items():
        ic = monthly_ic(e_w, lab, start=w0, end=w1)
        ics[name] = ic
        stats[name] = window_stats(ic)
    report["monthly_ic"] = {
        name: {
            "n_buckets": int(st["n_buckets"]),
            "ic_mean": st["ic_mean"],
            "icir": st["icir"],
            "na": st["na"],
            "ic_by_month": {str(k.date()): (None if pd.isna(v) else round(float(v), 6)) for k, v in ics[name].items()},
        }
        for name, st in stats.items()
    }

    ic_h = stats["holdout"]["ic_mean"]
    icir_h = stats["holdout"]["icir"]
    retain = retain_stat(ic_h, stats["is_ref"]["ic_mean"])
    sign_flip = ic_h is not None and stats["is_ref"]["ic_mean"] is not None and ic_h * stats["is_ref"]["ic_mean"] < 0
    passed, detail = judge(ic_h, icir_h, retain)
    report["headline"] = {
        "window": "holdout",
        "ic_mean": ic_h,
        "icir": icir_h,
        "retain": retain,
        "is_ref_ic_mean": stats["is_ref"]["ic_mean"],
        "sign_flip_vs_is_ref": bool(sign_flip),
        "judge_detail": detail,
        "lines_pass": passed,
    }

    # 敏感性（report-only，不进判定）
    sens: dict[str, Any] = {}
    for col in ("fwd5_old", "fwd5_leg5"):
        lab_x = labels[col].reindex(e_w.index)
        st_h = window_stats(monthly_ic(e_w, lab_x, start=WINDOW_HOLDOUT[0], end=WINDOW_HOLDOUT[1]))
        st_r = window_stats(monthly_ic(e_w, lab_x, start=WINDOW_IS_REF[0], end=WINDOW_IS_REF[1]))
        sens[col] = {"holdout": st_h, "is_ref": st_r}
    sens["concurrent_ret_t"] = {
        "holdout": window_stats(
            monthly_ic(e_w, labels["ret_t"].reindex(e_w.index), start=WINDOW_HOLDOUT[0], end=WINDOW_HOLDOUT[1])
        ),
    }
    roll = e_w.rank().rolling(20, min_periods=20).corr(lab.rank()).dropna()
    sens["rolling20d_spearman"] = {
        "n": int(len(roll)),
        "mean": float(roll.mean()) if len(roll) else None,
        "min": float(roll.min()) if len(roll) else None,
        "max": float(roll.max()) if len(roll) else None,
    }
    report["sensitivity_report_only"] = sens

    # PIT a/b/c 实测（考窗），d/e 冻结事实援引
    pit_a = check_ts_semantics(sig, EXAM_START, EXAM_END)
    pit_b = check_asof(sig, EXAM_START, EXAM_END)
    pit_c = check_key_uniqueness(sig)
    a_b_c_clean = (
        pit_a["ts_suffix_violations"] == 0
        and pit_a["ts_date_mismatch"] == 0
        and pit_b["asof_future_violations"] == 0
        and pit_c["multi_value_keys"] == 0
    )
    report["pit"] = {
        "a_ts_semantics": pit_a,
        "b_asof": pit_b,
        "c_key_uniqueness": pit_c,
        "d_construction": PIT_D_FACT,
        "e_revision_capability": PIT_E_FACT,
    }
    report["pit_verdict"] = "conditional_clean" if a_b_c_clean else "dirty"

    # 总判（prereg §2.6）
    if not a_b_c_clean:
        final = "不合格（PIT dirty）"
    elif passed and report["pit_verdict"] == "clean":
        final = "合格"
    elif passed:
        final = "有条件合格（三线全过+PIT conditional_clean；投产前置=逐日快照留痕持续+只追加读径）"
    else:
        final = "不合格（联动三线未全过）"
    report["verdict"] = final
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI：跑考→verdict JSON 落 staging→stdout 摘要。"""
    ap = argparse.ArgumentParser(prog="emotion_linkage_exam", description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=".runtime/sessions/st-mx07-L8/staging/emotion_linkage_exam_v1_results.json")
    args = ap.parse_args(argv)
    report = run_exam()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    hd = report["headline"]
    print(
        "HEADLINE(holdout): ic={} icir={} retain={} sign_flip={}\n{}\nPIT={}\nVERDICT: {}\n-> {}".format(
            hd["ic_mean"],
            hd["icir"],
            hd["retain"],
            hd["sign_flip_vs_is_ref"],
            hd["judge_detail"],
            report["pit_verdict"],
            report["verdict"],
            out,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
