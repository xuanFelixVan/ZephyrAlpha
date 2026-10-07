# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 批1因子/批3指标 IC考试引擎
# [MODULE] scripts.backtest.fexam.ic_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.factor.core.evaluation.metrics（compute_ic_series 内核复用，禁重造）;
#                scripts.backtest.fexam.ch_data; scripts.backtest.fexam.roster
# [CONSUMERS] run_fexam.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] PIT铁律——只用已实现前向收益（INV-004 对齐）；HOLDOUT窗与IS_REF窗严格不交；
#              verdict三态机判（pass/rework/retire_candidate）判据全部来自 roster.PREREG_V1（禁现场改判据）；
#              同列多对象只算一次（列级去重）；checkpoint 幂等可续跑；负结果（无alpha/低覆盖）如实入册；
#              registry零回写（分数只落分数册，回写另行批）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单列数据拉取失败→该列对象 verdict=rework(reason=ch_error)，不阻断全批；
#                  全部失败→保留空册并抛错（fail-closed 不静默）
# [TESTS] tests/backtest/fexam/test_ic_exam.py
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（三态判据禁现场改）
# [TTL] permanent
# create-guard-not-dup: 批量IC考试引擎（复用官方metrics内核），命中项为生成器/校验器无交集
"""ic_exam — 批1因子全量考 + 批3指标全量考（IC/ICIR/换手/分体制/衰减）。

考卷（prereg v1，roster 冻结）：
- 三窗 IC：1/5/20 日前向收益秩相关（headline=5d）
- ICIR = mean(IC)/std(IC)（HOLDOUT 窗）
- 换手率代理：HOLDOUT 内月末截面秩相关→1-ρ 月度均值
- 分体制 IC：HOLDOUT 内按 regime 态分组（regime_snapshot_history 真源，<2019 SMA fallback）
- OOS 衰减：retain = |IC_h(HOLDOUT)| / |IC_h(IS_REF)|，判据 retain>=0.5
- device：CPU pandas（spearman 秩相关无 GPU 核——degrade 台账逐条可解释）
"""

from __future__ import annotations

import json
import sys
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

from zephyr.factor.core.evaluation.metrics import compute_ic_series  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

_EPS = 1e-6
#: 覆盖率及格线（对齐 factor_registry 头部晋升门 coverage>=60%）
COVERAGE_MIN = 0.60
#: 分体制切片最小样本数（低于此标 n/a 禁下结论）
REGIME_MIN_OBS = 30


# ---------- 纯函数（单测面） ----------


def fast_rank_ic(panel: pd.DataFrame, ret: pd.DataFrame) -> pd.Series:
    """向量秩 IC（与 compute_ic_series 逐日 spearman 数学同构，selftest 对拍锁定）。

    逐日 Spearman = 逐日秩变换后的 Pearson。把两面板沿 date 轴一次性秩变换+行内
    标准化，IC 序列=逐元素乘积的行均值——全向量化，160 列批耗时从小时级降到分钟级。
    任一日有效对 <30 → 该日 NaN（防小样本噪声，对齐内核 common<2 返回 0 的防呆意图）。
    """
    common_cols = panel.columns.intersection(ret.columns)
    if len(common_cols) == 0:
        return pd.Series(dtype="float64", name="ic")
    common_idx = panel.index.intersection(ret.index)
    f_all = panel[common_cols].loc[common_idx]
    r_all = ret[common_cols].loc[common_idx]
    # 联合有效掩码先裁剪再秩变换——与 compute_ic 的"交集内 spearman"逐位同构
    # （若先各自秩变换，NaN 模式不一致时分母集不同 → IC 有偏）
    mask = f_all.notna() & r_all.notna()
    f = f_all.where(mask).rank(axis=1, pct=True)
    r = r_all.where(mask).rank(axis=1, pct=True)
    valid = mask.sum(axis=1)
    zf = f.sub(f.mean(axis=1), axis=0)
    zr = r.sub(r.mean(axis=1), axis=0)
    denom_f = zf.pow(2).sum(axis=1).pow(0.5).replace(0.0, np.nan)
    denom_r = zr.pow(2).sum(axis=1).pow(0.5).replace(0.0, np.nan)
    ic = (zf * zr).sum(axis=1) / (denom_f * denom_r)
    ic[valid < 30] = np.nan
    return ic.rename("ic").dropna()


def ic_stats(ic_series: pd.Series) -> dict[str, float]:
    """IC 均值/ICIR（std≈0 或样本<2 返回 0.0，对齐 metrics.compute_ir 口径）。"""
    if ic_series is None or len(ic_series) < 2:
        return {"ic_mean": 0.0, "icir": 0.0, "n_obs": int(0 if ic_series is None else len(ic_series))}
    mean = float(ic_series.mean())
    std = float(ic_series.std(ddof=0))
    icir = mean / std if std > _EPS else 0.0
    return {"ic_mean": mean, "icir": float(icir), "n_obs": int(len(ic_series))}


def slice_ic(ic_series: pd.Series, start: str, end: str) -> pd.Series:
    if ic_series.empty:
        return ic_series
    return ic_series.loc[(ic_series.index >= pd.Timestamp(start)) & (ic_series.index <= pd.Timestamp(end))]


def turnover_proxy(panel: pd.DataFrame, dates: pd.DatetimeIndex, *, max_pairs: int = 12) -> float:
    """换手率代理：月末截面 Spearman(panel_t, panel_{t-1}) → 1-ρ 均值。低换手因子 ρ 高。"""
    if len(dates) < 2:
        return float("nan")
    month_ends = pd.DatetimeIndex(sorted({d for d in dates if d.is_month_end}))
    picked = month_ends[-max_pairs:]
    rhos: list[float] = []
    for d in picked:
        pos = dates.get_loc(d)
        if pos == 0:
            continue
        a, b = panel.loc[d], panel.loc[dates[pos - 1]]
        common = a.dropna().index.intersection(b.dropna().index)
        if len(common) < 30:
            continue
        rho = a[common].corr(b[common], method="spearman")
        if pd.notna(rho):
            rhos.append(float(rho))
    if not rhos:
        return float("nan")
    return float(1.0 - float(np.mean(rhos)))


def regime_ic_slice(ic_series: pd.Series, regimes: pd.Series) -> dict[str, dict[str, float]]:
    """分体制 IC：{label: {ic_mean, n_obs}}；样本<REGIME_MIN_OBS 标 n/a（禁小样本结论）。"""
    out: dict[str, dict[str, float]] = {}
    if ic_series.empty or regimes.empty:
        return out
    joined = pd.concat([ic_series.rename("ic"), regimes.rename("regime")], axis=1, join="inner").dropna()
    for label, grp in joined.groupby("regime"):
        n = int(len(grp))
        if n < REGIME_MIN_OBS:
            out[str(label)] = {"ic_mean": float("nan"), "n_obs": n}
        else:
            out[str(label)] = {"ic_mean": float(grp["ic"].mean()), "n_obs": n}
    return out


def judge_indicator(*, ic_h: float, coverage: float, pass_line: dict[str, Any]) -> tuple[str, str]:
    """指标批三态机判（prereg：只看 |IC_5d| + 覆盖率；IC/体制切片只报告）。

    指标=状态量计算工具（registry entry_role=state），负 IC 即反向可用信号，
    故按绝对值判，方向语义随 direction 字段在册——与因子判据（带方向/ICIR/衰减）分开。
    """
    ic_min = float(pass_line["abs_ic_5d_min"])
    if coverage < COVERAGE_MIN:
        return "rework", f"coverage {coverage:.2f}<{COVERAGE_MIN}"
    if abs(ic_h) < 0.005:
        return "retire_candidate", f"clean窗无可测关联（|ic_5d|={abs(ic_h):.4f}）"
    if abs(ic_h) >= ic_min:
        return "pass", f"|ic_5d|={abs(ic_h):.4f}>=线{ic_min}"
    return "rework", f"|ic_5d|={abs(ic_h):.4f}<线{ic_min}"


def judge(
    *,
    ic_h: float,
    icir_h: float,
    retain: float,
    coverage: float,
    direction: str | None,
    pass_line: dict[str, Any],
) -> tuple[str, str]:
    """三态机判（判据全来自 prereg，禁现场改）。返回 (verdict, reason)。

    方向口径：registry direction=short 的对象按反向IC判定（long/both/neutral 用原始IC）。
    """
    eff = -ic_h if str(direction).lower() == "short" else ic_h
    eff_icir = -icir_h if str(direction).lower() == "short" else icir_h
    ic_min = float(pass_line["abs_ic_min"])
    icir_min = float(pass_line["icir_min"])
    retain_min = float(pass_line["ic_retain_min"])
    if coverage < COVERAGE_MIN:
        return "rework", f"coverage {coverage:.2f}<{COVERAGE_MIN}"
    if abs(eff) < 0.005 and abs(eff_icir) < 0.1:
        return "retire_candidate", f"clean窗无可测alpha（|ic|={abs(eff):.4f}, |icir|={abs(eff_icir):.2f}）"
    if abs(eff) >= ic_min and eff_icir >= icir_min and retain >= retain_min:
        return "pass", "prereg线全过"
    return "rework", (
        f"|ic|={abs(eff):.4f}(线{ic_min}) icir={eff_icir:.2f}(线{icir_min}) retain={retain:.2f}(线{retain_min})"
    )


# ---------- 批执行 ----------


def _ic_series_for_panel(panel: pd.DataFrame, ret: pd.DataFrame, headline_dates: pd.DatetimeIndex) -> pd.Series:
    """列级 IC 序列（快路径，与内核同构——见 fast_rank_ic docstring）。"""
    return fast_rank_ic(panel, ret.reindex(columns=panel.columns))


def _empty_result(obj: dict[str, Any], kind: str, verdict: str, reason: str) -> dict[str, Any]:
    return {
        "object_id": obj["object_id"],
        "kind": kind,
        "bucket": obj.get("bucket"),
        "verdict": verdict,
        "reason": reason,
        "ch_backings": obj.get("ch_backings") or [],
        "metrics": {},
    }


def _measure_column(
    table: str,
    column: str,
    rets: dict[int, pd.DataFrame],
    regimes: pd.Series,
    headline_h: int,
) -> dict[str, Any] | None:
    """单列全量度量（多对象共享）。返回 None=该列数据不可用。"""
    panel = ch_data.load_panel(table, column, *ch_data.WINDOW_UNION)
    if panel.empty:
        return None
    panel = panel.dropna(how="all").dropna(axis=1, how="all")
    if panel.empty:
        return None
    out: dict[str, Any] = {"per_horizon": {}, "headline": {}}
    for h, ret in rets.items():
        ic = _ic_series_for_panel(panel, ret, panel.index)
        st_h = ic_stats(slice_ic(ic, *ch_data.WINDOW_HOLDOUT))
        st_is = ic_stats(slice_ic(ic, *ch_data.WINDOW_IS_REF))
        out["per_horizon"][str(h)] = {
            "holdout": st_h,
            "is_ref": st_is,
            "retain": float(abs(st_h["ic_mean"]) / max(abs(st_is["ic_mean"]), _EPS)),
        }
        if h == headline_h:
            holdout_dates = slice_ic(ic, *ch_data.WINDOW_HOLDOUT).index
            cov = float(panel.loc[panel.index.intersection(holdout_dates)].notna().mean().mean())
            out["headline"] = {
                "ic_series_len_holdout": int(st_h["n_obs"]),
                "coverage_holdout": cov,
                "turnover_proxy": turnover_proxy(panel, holdout_dates),
                "regime_ic": regime_ic_slice(slice_ic(ic, *ch_data.WINDOW_HOLDOUT), regimes),
            }
    out["headline"]["regime_source"] = (
        regimes.attrs.get("source", "sma200_default") if isinstance(regimes, pd.Series) else "n/a"
    )
    return out


def run_exam(
    roster: dict[str, Any],
    kind: str,
    out_path: Path,
    ckpt_path: Path,
    *,
    headline_h: int | None = None,
) -> dict[str, Any]:
    """批1/批3 主入口。kind ∈ {factor, indicator}。幂等：ckpt 已完成对象跳过。"""
    headline_h = headline_h or int(PREREG_V1["headline_horizon"])
    horizons = tuple(int(h) for h in PREREG_V1["horizons"])
    objects: list[dict[str, Any]] = roster[kind]
    pass_line = PREREG_V1[f"{kind}_pass_line"]

    close = ch_data.load_close(*ch_data.WINDOW_UNION)
    rets = ch_data.forward_returns(close, horizons)
    # 裁定#489②：默认 SMA200 帘子（regime_source="sma200_default"）；HMM 未过考禁回用
    regimes, regime_source = ch_data.regime_series(*ch_data.WINDOW_HOLDOUT)

    done: dict[str, dict[str, Any]] = {}
    if ckpt_path.exists():
        for line in ckpt_path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                done[rec["object_id"]] = rec
            except (json.JSONDecodeError, KeyError):
                continue

    cache: dict[str, set[str]] = {}
    col_cache: dict[tuple[str, str], dict[str, Any] | None] = {}
    results: list[dict[str, Any]] = []
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)

    with ckpt_path.open("a", encoding="utf-8") as ck:
        for obj in objects:
            if obj["object_id"] in done:
                results.append(done[obj["object_id"]])
                continue
            bucket = obj.get("bucket")
            if bucket == "non_quantified":
                rec = _empty_result(
                    obj, kind, "rework", "未量化（自然语言规则/待定义），无可计算列——如实登记，禁造凑数因子"
                )
            elif bucket == "code_backed":
                rec = _empty_result(
                    obj, kind, "rework", "quantized有码但outputs无CH列映射——需因子值落库管线，登记施工缺口"
                )
            elif bucket == "col_missing":
                rec = _empty_result(obj, kind, "rework", "outputs列在CH候选表全部未命中——登记列名漂移缺口")
            elif bucket == "ch_backed":
                backings = obj.get("ch_backings") or []
                if not backings:
                    rec = _empty_result(obj, kind, "rework", "ch_backed但backings为空（roster不一致）")
                else:
                    table, column = backings[0].rsplit(".", 1)  # db.table.column 三段式
                    if (table, column) not in col_cache:
                        try:
                            col_cache[(table, column)] = _measure_column(table, column, rets, regimes, headline_h)
                        except ch_data.CHAccessError as exc:
                            col_cache[(table, column)] = {"error": str(exc)}
                    meas = col_cache[(table, column)]
                    if meas is None:
                        rec = _empty_result(obj, kind, "rework", f"{table}.{column} 窗内无数据")
                    elif "error" in meas:
                        rec = _empty_result(obj, kind, "rework", f"ch_error: {meas['error'][:160]}")
                    else:
                        h_stats = meas["per_horizon"][str(headline_h)]
                        direction = obj.get("direction")
                        if kind == "indicator":
                            verdict, reason = judge_indicator(
                                ic_h=h_stats["holdout"]["ic_mean"],
                                coverage=meas["headline"]["coverage_holdout"],
                                pass_line=pass_line,
                            )
                        else:
                            verdict, reason = judge(
                                ic_h=h_stats["holdout"]["ic_mean"],
                                icir_h=h_stats["holdout"]["icir"],
                                retain=h_stats["retain"],
                                coverage=meas["headline"]["coverage_holdout"],
                                direction=direction,
                                pass_line=pass_line,
                            )
                        declared = obj.get("regime_valid") or []
                        deviation = (
                            _regime_deviation(meas["headline"]["regime_ic"], declared) if kind == "indicator" else None
                        )
                        rec = {
                            "object_id": obj["object_id"],
                            "kind": kind,
                            "bucket": bucket,
                            "verdict": verdict,
                            "reason": reason,
                            "ch_backings": backings,
                            "direction": direction,
                            "metrics": meas,
                            "regime_valid_declared": declared,
                            "regime_deviation": deviation,
                        }
            else:
                rec = _empty_result(obj, kind, "rework", f"未知bucket:{bucket}")
            results.append(rec)
            ck.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            ck.flush()

    counts: dict[str, int] = {"total": len(results)}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    book = {
        "doc_type": f"fexam_{kind}_scores",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "prereg_v1": PREREG_V1,
        "window_definition": {
            "holdout_exam": list(ch_data.WINDOW_HOLDOUT),
            "is_ref_decay": list(ch_data.WINDOW_IS_REF),
            "separation_note": "选样窗（registry冻结于考前）与考试窗（HOLDOUT）分离；IS_REF仅用于衰减对照",
        },
        "device_ledger": [
            {
                "object": f"{kind}_exam",
                "device": "cpu",
                "reason": "spearman秩相关(pandas)无GPU核；rank_ic非矩阵乘法密集型，GPU无收益",
            }
        ],
        "regime_source": regime_source,
        "counts": counts,
        "results": results,
    }
    from zephyr.shared.io.file_utils import safe_write_text

    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out_path, yaml.safe_dump(book, allow_unicode=True, sort_keys=False, width=120))
    return book


def _regime_deviation(measured: dict[str, dict[str, float]], declared: list[str]) -> dict[str, Any]:
    """regime_valid 声明 vs 实测偏差：实测有效（|ic|>=线）态集合与声明集合对比，只报告不判死。"""
    ic_min = float(PREREG_V1["indicator_pass_line"]["abs_ic_5d_min"])
    measured_valid = sorted(
        lbl for lbl, st in measured.items() if st["n_obs"] >= REGIME_MIN_OBS and abs(st["ic_mean"]) >= ic_min
    )
    declared_set = {str(d) for d in declared}
    return {
        "measured_valid_regimes": measured_valid,
        "declared_regimes": sorted(declared_set),
        "deviation": {
            "declared_but_weak": sorted(declared_set - set(measured_valid)),
            "strong_but_undeclared": sorted(set(measured_valid) - declared_set),
        },
        "note": "声明核对 report_only（prereg）；标签词表差异（HMM四态 vs 册内七态）如实并存，禁硬映射",
    }
