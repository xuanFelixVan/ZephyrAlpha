# [BLUEPRINT] MOD-BT-243 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.fexam.calibration_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; scripts/backtest/fexam/ch_data; scripts/backtest/fexam/ic_exam;
#   zephyr/backtest/core/n_trial_ledger; yaml
# [CONSUMERS] W4 校准战役出分（20 张预注册卡的执行器）；W5 writeback_exam_confidence（分数册消费方上游）;
#   人工 CLI（--card 逐卡开考）
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 只考 preregistered 卡（empty=未冻结禁考；examined=已出分，重考须 --force 且新分数行
#   only-add 追加禁改旧行）；判据门柱=卡内 pillars_numeric（裁定#501 冻结面，执行器零裁量）；
#   verdict=门柱全过才 pass（一票否决）；分数行落 exam_scores_v1.yaml only-add；试次入 n_trial_ledger；
#   信号/目标可注入（测试零 CH），缺省经 ch_data 按 signal_spec/target_spec 取数。
# [MODIFY-GUARD] tests/backtest/test_calibration_exam.py
# [STABILITY] experimental
# [ERROR_CONTRACT] RuntimeError: 卡状态非法/缺 pillars_numeric/信号目标缺失/分数册 CAS 冲突
# [TESTS] tests/backtest/test_calibration_exam.py
# [A_module] module_id=MOD-BT-243 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [not-trading: 回测研究面工具（考试卡骨架/校准执行/置信度回写），不在实盘交易决策路径上；TDM 挂载随分数册集成批另办]
"""环节校准卡考试执行器（W4）——预注册卡 → 响应曲线/IC/时滞/行情段四件套 → 分数行。

两形信号：
  panel  逐符号面板：复用 ic_exam.fast_rank_ic/ic_stats/regime_ic_slice（机判同构不自研）。
  series 日度序列（广度/结果面）：分桶日→桶中位次日目标→桶秩-中位 Spearman 单调 +
         时序 Spearman 作 IC；牛/熊窗分段同号判稳。

分数行 schema 与 W5 writeback_exam_confidence 对齐（card_id/node_id/run_id/kind/verdict/
pillars_all_pass/oos_ok/regimes/date）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date as _date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

from fexam.ic_exam import fast_rank_ic, ic_stats, regime_ic_slice  # noqa: E402

SCORES_PATH = REPO_ROOT / "docs" / "03_modules" / "_domain_backtest" / "exam_scores_v1.yaml"


class _ToolError(RuntimeError):
    def __init__(self, msg: str, details: dict | None = None):
        super().__init__(msg)
        self.details = details or {}


_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _span_dates(span: str) -> tuple[str, str]:
    """行情段跨度解析：取串内前两个日期（容许尾注，如 '2019-01-04..2021-06-30（流动性牛）'）。"""
    hits = _DATE_RE.findall(str(span))
    if len(hits) < 2:
        return span, span
    return hits[0], hits[1]


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    s = pd.Series(a).rank()
    t = pd.Series(b).rank()
    if s.std() == 0 or t.std() == 0:
        return float("nan")
    return float(np.corrcoef(s, t)[0, 1])


def _round_trip_cost_bp(config_path=None) -> float:
    """G1 净费参数（exam_scale_cost_gate.yaml net_fee 节，禁硬编码；读败=nan 不伪造）。"""
    cp = Path(config_path) if config_path else REPO_ROOT / "config" / "exam_scale_cost_gate.yaml"
    try:
        data = yaml.safe_load(cp.read_text(encoding="utf-8"))
        return float(data["net_fee"]["round_trip_cost_bp"])
    except Exception:  # noqa: BLE001  读败=nan 不伪造（费率参数面缺 net_fee 节属合法态）
        return float("nan")


def _signal_turnover(signal: pd.Series) -> float | None:
    """G2 换手计量：相邻交易日信号值变化占比（档位翻转率，只计量不判罚）。"""
    v = signal.dropna()
    if len(v) < 2:
        return None
    changes = (v.diff().fillna(0) != 0).iloc[1:]
    return round(float(changes.mean()), 4)


def _bucket_response(signal: pd.Series, target: pd.Series, n_buckets: int = 10) -> dict:
    """日度序列分桶响应：按信号分位分桶 → 桶内目标中位 → 桶序-中位 Spearman。

    序数信号（唯一值 <= n_buckets，如三态档位卡）按信号值直接分桶（尊重冻结桶型）。"""
    df = pd.concat({"sig": signal, "tgt": target}, axis=1).dropna()
    if len(df) < n_buckets * 10:
        return {"n": len(df), "bucket_medians": [], "mono_spearman": float("nan")}
    if df["sig"].nunique() <= n_buckets:
        df["b"] = df["sig"].rank(method="dense")
    else:
        df["b"] = pd.qcut(df["sig"].rank(method="first"), n_buckets, labels=False)
    med = df.groupby("b")["tgt"].median()
    rho = _spearman(med.index.to_numpy(float), med.to_numpy(float))
    return {"n": int(len(df)), "bucket_medians": [float(x) for x in med], "mono_spearman": rho}


def _series_metrics(signal: pd.Series, target: pd.Series, card: dict) -> dict:
    sig = signal.sort_index()
    tgt = target.sort_index().shift(-1)  # 次日目标（PIT：t 信号对 t+1 目标）
    aligned = pd.concat({"s": sig, "t": tgt}, axis=1).dropna()
    ic_ts = _spearman(aligned["s"].to_numpy(), aligned["t"].to_numpy())
    resp = _bucket_response(sig, tgt)
    regimes = card.get("window", {}).get("regimes", {})
    seg: dict[str, float] = {}
    for name, span in regimes.items():
        a, b = _span_dates(span)
        m = aligned[(aligned.index >= pd.Timestamp(a)) & (aligned.index <= pd.Timestamp(b))]
        seg[name] = _spearman(m["s"].to_numpy(), m["t"].to_numpy()) if len(m) >= 60 else float("nan")
    oos = card.get("oos_window_ref") or []
    oos_ic = float("nan")
    if len(oos) == 2:
        m = aligned[(aligned.index >= pd.Timestamp(oos[0])) & (aligned.index <= pd.Timestamp(oos[1]))]
        oos_ic = _spearman(m["s"].to_numpy(), m["t"].to_numpy()) if len(m) >= 60 else float("nan")
    # G1 净费读数（增补令 2026-10-10）：桶中位收益减往返成本（费率参数面 net_fee 节，禁硬编码）
    net_med = None
    if resp.get("bucket_medians"):
        rt = _round_trip_cost_bp()
        net_med = [round(x - rt / 10000.0, 6) for x in resp["bucket_medians"]]
    # G2 换手读数（只计量不判罚）：相邻交易日信号档位翻转率
    turn = _signal_turnover(signal)
    return {
        "ic_mean": ic_ts,
        "mono_spearman": resp.get("mono_spearman"),
        "n": resp.get("n"),
        "regime_ic": seg,
        "oos_ic": oos_ic,
        "ic_ir": None,
        "bucket_medians": resp.get("bucket_medians"),
        "net_bucket_medians": net_med,
        "round_trip_cost_bp": _round_trip_cost_bp(),
        "signal_turnover_daily": turn,
    }


def _panel_metrics(signal: pd.DataFrame, target: pd.DataFrame, card: dict) -> dict:
    ret = target.shift(-1)
    ic = fast_rank_ic(signal, ret).dropna()
    st = ic_stats(ic)
    regimes = card.get("window", {}).get("regimes", {})
    seg = {}
    for name, span in regimes.items():
        a, b = _span_dates(span)
        part = ic[(ic.index >= pd.Timestamp(a)) & (ic.index <= pd.Timestamp(b))]
        seg[name] = float(part.mean()) if len(part) >= 30 else float("nan")
    oos = card.get("oos_window_ref") or []
    oos_ic = float("nan")
    if len(oos) == 2:
        part = ic[(ic.index >= pd.Timestamp(oos[0])) & (ic.index <= pd.Timestamp(oos[1]))]
        oos_ic = float(part.mean()) if len(part) >= 30 else float("nan")
    return {
        "ic_mean": float(st.get("ic_mean", float("nan"))),
        "ic_ir": float(st.get("ic_ir", float("nan"))),
        "mono_spearman": None,
        "regime_ic": seg,
        "oos_ic": oos_ic,
        "n": int(ic.notna().sum()),
        "bucket_medians": None,
    }


def _arm_nav_metrics(exposure: pd.Series, target: pd.Series, cost_bp: float | None = None) -> dict:
    """对照/消融单臂日频回放（PIT：t 收盘敞口 → t+1 目标收益；同轴同撮合同成本）。

    maxdd=正深度（0..1）；sharpe 年化（sqrt252）已扣换手成本；turnover_annual_x=年化敞口
    翻转倍数（|Δ敞口|均值×252，无量纲 x——对齐 exam_scale_cost_gate turnover_gate.cap_annual_x 口径）。
    成本默认读 net_fee.round_trip_cost_bp（读败=0 成本并在返回面标 cost_bp=nan，禁伪造）。
    """
    if cost_bp is None:
        cost_bp = _round_trip_cost_bp()
    df = pd.concat({"e": exposure.sort_index(), "r": target.sort_index()}, axis=1).dropna()
    if len(df) < 30:
        return {
            "n": len(df),
            "maxdd": float("nan"),
            "sharpe": float("nan"),
            "turnover_annual_x": float("nan"),
            "ann_ret": float("nan"),
            "cost_bp": cost_bp,
        }
    ret = df["e"].shift(0) * df["r"].shift(-1)  # t 敞口吃 t+1 收益
    turn = df["e"].diff().abs().iloc[1:]
    cbp = cost_bp if cost_bp == cost_bp else 0.0
    ret_net = ret - turn.reindex(ret.index).fillna(0.0) * cbp / 10000.0
    nav = (1.0 + ret_net.fillna(0.0)).cumprod()
    dd = nav / nav.cummax() - 1.0
    mu, sd = ret_net.mean(), ret_net.std()
    sharpe = float(mu / sd * np.sqrt(252)) if sd and sd == sd and sd > 0 else float("nan")
    return {
        "n": int(len(df)),
        "maxdd": float(-dd.min()) if len(dd) else float("nan"),
        "sharpe": sharpe,
        "turnover_annual_x": float(turn.mean() * 252) if len(turn) else float("nan"),
        "ann_ret": float(ret_net.mean() * 252),
        "cost_bp": cost_bp,
    }


_COMPARISON_KNOWN_KEYS = frozenset(
    {
        "misfire_reduction_min",
        "maxdd_improvement_min",
        "maxdd_deterioration_max_pp",
        "sharpe_delta_min",
        "turnover_delta_annual_max",
        "cost_tier_bp_required",
        "oos_same_sign",
    }
)


def _comparison_metrics(sig_open: pd.Series, sig_base: pd.Series, target: pd.Series, card: dict) -> dict:
    """对照/消融配对面：双臂各自 IC 面（复用 _series_metrics）+ NAV 回放面 + 配对差。

    开臂/基臂共用同一目标与窗（paired_arm_protocol：仅信号处理异，零行循环差异）。"""
    mo_open = _series_metrics(sig_open, target, card)
    mo_base = _series_metrics(sig_base, target, card)
    nav_open = _arm_nav_metrics(sig_open, target)
    nav_base = _arm_nav_metrics(sig_base, target)
    rt = _round_trip_cost_bp()
    tier = card.get("pillars_numeric", {}).get("cost_tier_bp_required")
    nav_open_tier = _arm_nav_metrics(sig_open, target, cost_bp=float(tier)) if tier else None
    icd = mo_open.get("ic_mean") - mo_base.get("ic_mean")
    icd = icd if icd == icd else float("nan")
    icd_oos = mo_open.get("oos_ic") - mo_base.get("oos_ic")
    icd_oos = icd_oos if icd_oos == icd_oos else float("nan")
    return {
        "arm_open": {k: v for k, v in mo_open.items() if k != "bucket_medians"} | {"nav": nav_open},
        "arm_base": {k: v for k, v in mo_base.items() if k != "bucket_medians"} | {"nav": nav_base},
        "maxdd_improvement_pp": (nav_base["maxdd"] - nav_open["maxdd"]) * 100.0,
        "sharpe_delta": nav_open["sharpe"] - nav_base["sharpe"],
        "turnover_delta_annual_x": nav_open["turnover_annual_x"] - nav_base["turnover_annual_x"],
        "open_sharpe_at_tier_bp": nav_open_tier["sharpe"] if nav_open_tier else float("nan"),
        "ic_delta_is": icd,
        "ic_delta_oos": icd_oos,
        "round_trip_cost_bp": rt,
    }


def _judge_comparison(card: dict, m: dict) -> tuple[str, list[str]]:
    """对照/消融判（pillars_numeric 冻结键，执行器零裁量；未知键=诚实 fail-closed）。"""
    p = card.get("pillars_numeric")
    if not p:
        raise _ToolError("卡缺 pillars_numeric（冻结判据机判面）", {"card_id": card.get("card_id")})
    unknown = set(p) - _COMPARISON_KNOWN_KEYS
    fails: list[str] = []
    if unknown:
        fails.append(f"未支持判据键（机判面待扩）: {sorted(unknown)}")
    if "misfire_reduction_min" in p:
        # 误清率面需"卖出后再创新高"笔级价格面（W4 绑定层），本核 NAV/IC 面不可判——如实记败不冒判
        fails.append(f"misfire_reduction_min 无机判面（缺笔级价格面，W4 绑定层后重考）: {p['misfire_reduction_min']}")
    imp = m.get("maxdd_improvement_pp")
    if imp == imp:
        if imp < float(p.get("maxdd_improvement_min", float("-inf"))):
            fails.append(f"maxdd_improvement {imp:.2f}pp < {p.get('maxdd_improvement_min')}")
        det = -imp
        if det > float(p.get("maxdd_deterioration_max_pp", float("inf"))):
            fails.append(f"maxdd_deterioration {det:.2f}pp > {p.get('maxdd_deterioration_max_pp')}pp")
    elif "maxdd_improvement_min" in p:
        fails.append("maxdd_improvement nan（NAV 面样本不足）")
    sd = m.get("sharpe_delta")
    if sd == sd:
        if sd < float(p.get("sharpe_delta_min", float("-inf"))):
            fails.append(f"sharpe_delta {sd:.3f} < {p.get('sharpe_delta_min')}")
    elif "sharpe_delta_min" in p:
        fails.append("sharpe_delta nan（NAV 面样本不足）")
    td = m.get("turnover_delta_annual_x")
    if td == td:
        if td > float(p.get("turnover_delta_annual_max", float("inf"))):
            fails.append(f"turnover_delta {td:.2f}x > {p.get('turnover_delta_annual_max')}x")
    tier_s = m.get("open_sharpe_at_tier_bp")
    if tier_s == tier_s and p.get("cost_tier_bp_required"):
        if tier_s < 0.0:
            fails.append(f"open_sharpe@{p['cost_tier_bp_required']}bp {tier_s:.3f} < 0.0")
    if p.get("oos_same_sign"):
        d_is, d_oos = m.get("ic_delta_is"), m.get("ic_delta_oos")
        if d_is == d_is and d_oos == d_oos and d_is != 0:
            if (d_oos > 0) != (d_is > 0):
                fails.append(f"oos_sign_flip ic_delta oos={d_oos:.4f} is={d_is:.4f}")
        else:
            fails.append("oos_sign_flip ic_delta nan（配对 IC 面样本不足）")
    return ("pass", []) if not fails else ("fail", fails)


def judge(card: dict, m: dict) -> tuple[str, list[str]]:
    """pillars_numeric 机械判（执行器零裁量，一票否决）。"""
    p = card.get("pillars_numeric")
    if not p:
        raise _ToolError("卡缺 pillars_numeric（冻结判据机判面）", {"card_id": card.get("card_id")})
    fails: list[str] = []
    if m.get("mono_spearman") is not None and m["mono_spearman"] == m["mono_spearman"]:
        if m["mono_spearman"] < p["mono_spearman_min"]:
            fails.append(f"mono_spearman {m['mono_spearman']:.3f} < {p['mono_spearman_min']}")
    ic = m.get("ic_mean")
    if ic == ic:
        if ic < p["ic_mean_min"]:
            fails.append(f"ic_mean {ic:.4f} < {p['ic_mean_min']}")
    ir = m.get("ic_ir")
    if ir is not None and ir == ir and ir < p["ic_ir_min"]:
        fails.append(f"ic_ir {ir:.3f} < {p['ic_ir_min']}")
    seg = m.get("regime_ic") or {}
    vals = [v for v in seg.values() if v == v]
    if len(vals) >= 2 and p.get("regime_same_sign"):
        if len({v > 0 for v in vals}) > 1:
            fails.append(f"regime_sign_flip {seg}")
    oos = m.get("oos_ic")
    if oos == oos and p.get("oos_same_sign"):
        base_ic = ic if (ic == ic) else 0.0
        if base_ic != 0 and (oos > 0) != (base_ic > 0):
            fails.append(f"oos_sign_flip oos={oos:.4f} is={base_ic:.4f}")
    if oos != oos:
        fails.append("oos_ic nan（OOS 窗样本不足）")
    ic_ok = ic == ic
    mono = m.get("mono_spearman")
    mono_ok = mono is not None and mono == mono
    if not ic_ok and not mono_ok:
        fails.append("无有效主指标（ic/mono 均 nan——样本不足或信号恒定）")
    return ("pass", []) if not fails else ("fail", fails)


def run_card(
    card_path: str | Path,
    *,
    signal=None,
    signal_b=None,
    target=None,
    force: bool = False,
    run_id: str | None = None,
    recorded_by: str = "calibration_exam",
    scores_path: Path = SCORES_PATH,
) -> dict:
    card = yaml.safe_load(Path(card_path).read_text(encoding="utf-8"))
    status = card.get("status")
    if status != "preregistered" and not force:
        raise _ToolError("卡状态非 preregistered：只考 preregistered 卡（重考带 --force）", {"status": status})
    kind = card.get("signal_kind")
    if kind not in ("panel", "series"):
        raise _ToolError("卡缺 signal_kind", {"card_id": card.get("card_id")})
    if signal is None or target is None:
        raise RuntimeError(
            "缺省 CH 取数面未接（signal_spec/target_spec 绑定属 W4 运行期配置）——"
            "请注入 signal/target 或先行落绑定册（防误绑数据面）"
        )
    family = card.get("family")
    # 判官按判据键分派（W-A 臂协议配方面 2026-10-10）：family=comparison/ablation 但
    # pillars_numeric 全韦校准键（mono/ic/ic_ir/regime/oos，如 C-L1 冻结映射面）→ 映射面后
    # 走校准判官；含任一 NAV/笔级键（maxdd/sharpe_delta/misfire 等）→ 双臂判官。判据面零裁量。
    _CALIBRATION_KEYS = {"mono_spearman_min", "ic_mean_min", "ic_ir_min", "regime_same_sign", "oos_same_sign"}
    _pn_keys = set(card.get("pillars_numeric") or {})
    _cal_shaped = bool(_pn_keys) and _pn_keys <= _CALIBRATION_KEYS
    if family in ("comparison", "ablation") and not _cal_shaped:
        # 对照/消融分支（夜矿续战三连裁② 2026-10-10 并入本执行核）：双臂配对面
        if signal_b is None:
            raise _ToolError(
                "对照/消融卡需双臂信号：signal=开臂（或全量臂），signal_b=基臂（或消融臂）",
                {"card_id": card.get("card_id"), "family": family},
            )
        m = _comparison_metrics(signal, signal_b, target, card)
        verdict, fails = _judge_comparison(card, m)
    else:
        m = _series_metrics(signal, target, card) if kind == "series" else _panel_metrics(signal, target, card)
        verdict, fails = judge(card, m)
    pillars_all_pass = verdict == "pass"
    used_nav = family in ("comparison", "ablation") and not _cal_shaped
    if used_nav:
        oos_ok = (m.get("ic_delta_oos") == m.get("ic_delta_oos")) and not any("oos" in f for f in fails)
        seg = m.get("arm_open", {}).get("regime_ic") or {}
    else:
        oos_ok = (m.get("oos_ic") == m.get("oos_ic")) and not any("oos" in f for f in fails)
        seg = m.get("regime_ic") or {}
    regimes = [k for k, v in seg.items() if v == v]
    row = {
        "card_id": card["card_id"],
        "node_id": card["node_id"],
        "run_id": run_id or f"examcard-{_date.today().isoformat()}",
        "kind": "exam",
        "verdict": verdict,
        "pillars_all_pass": pillars_all_pass,
        "oos_ok": bool(oos_ok),
        "regimes": regimes,
        "date": _date.today().isoformat(),
        "metrics": {k: v for k, v in m.items() if k != "bucket_medians"},
        "fails": fails,
    }
    # 分数册 only-add 追加
    sp = Path(scores_path)
    if sp.exists():
        reg = yaml.safe_load(sp.read_text(encoding="utf-8")) or {}
        rows = reg.get("rows") or []
    else:
        reg = {"schema_version": "1.0", "title": "考试卡分数册（成绩汇总面，方案 §6 D4）", "rows": []}
        rows = reg["rows"]
    rows.append(row)
    reg["rows"] = rows
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(yaml.safe_dump(reg, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8", newline="\n")
    # 卡面更新：status=examined + lineage 指针
    card["status"] = "examined"
    card.setdefault("lineage", {})
    card["lineage"]["run_id"] = row["run_id"]
    card["lineage"]["score_row"] = f"exam_scores_v1.yaml#rows[{len(rows) - 1}]"
    Path(card_path).write_text(
        yaml.safe_dump(card, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n"
    )
    # 试次记账（DSR 分母强制面）
    try:
        from zephyr.backtest.core.n_trial_ledger import TrialLedger

        TrialLedger().record_run(
            kind="exam_card",
            batch_id=f"examcard:{card['card_id']}:{row['date']}",
            n_trials=1,
            note=f"verdict={verdict}",
            recorded_by=recorded_by,
        )
    except Exception as e:  # noqa: BLE001 — 台账失败不吞考试结果，但必须留痕
        row["ledger_warning"] = str(e)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--card", required=True)
    ap.add_argument("--signal-csv", help="信号 csv（index=date；series 用 value 列，panel 用宽表）")
    ap.add_argument("--signal-b-csv", help="对照/消融基臂（或消融臂）信号 csv（comparison/ablation 卡必带）")
    ap.add_argument("--target-csv", help="目标 csv（index=date，value 列）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    sig = tgt = sig_b = None
    if args.signal_csv:
        s = pd.read_csv(args.signal_csv, index_col=0, parse_dates=True)
        sig = s.iloc[:, 0] if isinstance(s, pd.Series) is False and s.shape[1] == 1 else s
    if args.signal_b_csv:
        sb = pd.read_csv(args.signal_b_csv, index_col=0, parse_dates=True)
        sig_b = sb.iloc[:, 0] if sb.shape[1] == 1 else sb
    if args.target_csv:
        t = pd.read_csv(args.target_csv, index_col=0, parse_dates=True)
        tgt = t.iloc[:, 0]
    row = run_card(args.card, signal=sig, signal_b=sig_b, target=tgt, force=args.force)
    print(json.dumps(row, ensure_ascii=False, indent=2, default=str))
    return 0 if row["verdict"] == "pass" else 1


# 人工CLI设计如此（同域MOD-BT-197先例）：按TDM变更/分数册更新/逐卡开考人工触发，非永久自动系统面
if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工CLI（同域MOD-BT-197先例），非永久自动系统
    sys.exit(main())
