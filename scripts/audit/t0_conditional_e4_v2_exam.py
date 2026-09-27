# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_matrix/t0_conditional_v2_prereg_card.md | §2 双门+§4 材料+§5 判据
# [MODULE] t0_conditional_e4_v2_exam（scripts 判据脚本；T0-CONDITIONAL-V2 预注册卡 §6 执行件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/cost_trio_exam.py（配对判据 build_pairs 唯一真源，import 复用）；scripts/audit/t0_conditional_e4_exam.py（宏观门 t1_state/load_regime_states + 五态判定 _verdict_for，import 复用）；docs/_working/t0_matrix/six_phase_history_v1.csv（情绪门六段真源）；data/backtest_artifacts/bt-*.json（材料，绝对路径可指主区）
# [CONSUMERS] Owner 复查窗；docs/_working/t0_matrix/t0_conditional_e4_v2_verdict.md（verdict 留档）；红蓝 PIT 断言
# [STARTUP] manual（python scripts/audit/t0_conditional_e4_v2_exam.py --artifacts-dir <主区材料目录>）
# [MATURITY] production（考试执行件，卡先行纪律：t0_conditional_v2_prereg_card.md frozen 先于本脚本取数）
# [INVARIANTS] 判据全部来自 frozen 卡且**全部 import 自既有判据件**（配对/宏观门/五态判定零重写，禁克隆）；本件唯一新逻辑=材料合格性过滤（卡 §4.1 机械判据：str(timestamp)>10 才入样）与情绪门按日三态查表（allow/deny/unevaluable_day）；卡 §2.3 主考=双门均可评且均允许，unevaluable_day 配对单独入副考**禁并入主考**，禁当禁做段入对照；fail-closed：样本不足/门零命中落卡 §5 五态枚举，禁硬出；禁写 summary.json 到 data/strategy_intake（会污染 DSR 分母）；查库只读；产物只写 docs/_working/t0_matrix/（.yaml/.csv，禁 .json）；零状态变更
# [MODIFY-GUARD] 本脚本改动=考试判据变更，须先改卡并作废重开（卡 frozen 纪律）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 材料缺失/情绪真源缺失=显式报错非静默空结果（禁把"读不到"判成"不命中"）；真源含重复 trade_date=显式报错；考窗内零入样=显式报错并披露剔除统计
# [TESTS] tests/audit/test_t0_conditional_e4_v2_exam.py（材料过滤机械性/三态情绪门/副考不污染主考/判据零重写）
# [TTL] task_bound
"""t0_conditional_e4_v2_exam.py — 条件化做T E4 双门考试 V2（T0-CONDITIONAL-V2 卡 §6，frozen 判据）

判据真源：docs/_working/t0_matrix/t0_conditional_v2_prereg_card.md（frozen）。
与 v1 的唯一差异=材料窗（卡 §0 三条实测事实决定必须另立一卡）；假设、宏观门、情绪门词表、
成本口径、四条土规全部逐字继承，且**函数级复用** v1/cost_trio 判据件，零重写。

用法：
  python scripts/audit/t0_conditional_e4_v2_exam.py \
      --artifacts-dir D:/ZephyrAlpha/data/backtest_artifacts
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cost_trio_exam as ct  # 配对判据唯一真源
import t0_conditional_e4_exam as v1  # 宏观门 + 五态判定复用（禁克隆）

EXAM_START = "2026-06-01"  # 卡 §4.2 frozen（第三方 frozen 卡 t0_regime §3 考试段起点，非本卡新定）
EMOTION_ALLOW = {"ignition", "expansion", "euphoria"}  # 卡 §2.2 frozen 允许集
EMOTION_TRUTH = Path("docs/_working/t0_matrix/six_phase_history_v1.csv")


def load_intraday_fills(artifacts_dir: Path) -> tuple[list[dict], dict]:
    """卡 §4.1 材料合格性过滤：只读记录格式（timestamp 是否含时分），不读价格/收益。"""
    files = sorted(artifacts_dir.glob("bt-*.json"))
    if not files:
        raise SystemExit(f"FAIL: 材料缺失——{artifacts_dir} 下无 bt-*.json（判据禁静默空结果）")
    fills: list[dict] = []
    audit: Counter[str] = Counter()
    keep_files: list[str] = []
    for f in files:
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            audit[f"parse_fail:{f.name}"] = 1
            audit["parse_fail_fills"] += 0
            sys.stderr.write(f"parse fail {f.name}: {exc}\n")
            continue
        kept = 0
        for t in data.get("trade_log") or []:
            audit["fills_total"] += 1
            ts = str(t.get("timestamp", ""))
            if len(ts) <= 10:  # 仅日期粒度=日线 bar，同日买卖属同 bar 聚合，不构成 T 往返
                audit["fills_excluded_daily_bar"] += 1
                continue
            day = ts[:10]
            if day < EXAM_START:
                audit["fills_excluded_pre_exam_window"] += 1
                continue
            audit["fills_in_exam_window"] += 1
            fills.append({**t, "trade_date": day, "run_id": data.get("run_id", f.name)})
            kept += 1
        if kept:
            keep_files.append(f.name)
            audit["files_keeping_intraday"] += 1
    audit["files_total"] = len(files)
    if not fills:
        raise SystemExit(f"FAIL: 考窗内零入样（日内粒度材料被全剔）——禁把'无材料'判成'无信号'。 剔除审计={dict(audit)}")
    return fills, {"keep_files": keep_files, **{k: v for k, v in audit.items()}}


def load_emotion_phases(path: Path) -> dict[str, str]:
    """情绪门六段真源装载（卡 §2.2）。缺文件/缺列=显式报错，禁降级为'不命中'。"""
    if not path.exists():
        raise SystemExit(f"FAIL: 情绪门真源缺失 {path}——先跑 scripts/audit/t0_six_phase_materialize.py（卡 §2.2）")
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"FAIL: 情绪门真源为空 {path}")
    out: dict[str, str] = {}
    for r in rows:
        d = r["trade_date"]
        if d in out:
            raise SystemExit(f"FAIL: 情绪门真源含重复 trade_date={d}（双写会致按日计数翻倍）")
        out[d] = r["six_phase"] if r.get("routed") == "1" else ""
    return out


def emotion_state_for(phases: dict[str, str], day: date) -> tuple[str, str, int]:
    """卡 §2.2 PIT=T-1 交易日 + 7 日容差（与宏观门同构，复用 v1.t1_state 的容差常数）。"""
    cands = [d for d in phases if date.fromisoformat(d) < day]
    if not cands:
        return "unevaluable_day", "", 1
    prev = max(cands)
    prev_d = date.fromisoformat(prev)
    if (day - prev_d).days > v1.ASOF_TOLERANCE_DAYS:
        return "unevaluable_day", "", 1
    six = phases[prev]
    if not six:
        return "unevaluable_day", prev, 0
    return ("allow" if six in EMOTION_ALLOW else "deny"), prev, 0


def split_gates(pairs: list[dict], regime: dict, phases: dict[str, str]) -> tuple[list, list, list, dict]:
    """卡 §2.3 三集切分：primary（双门均允许）/secondary（情绪不可评日按单宏观门）/control（宏观禁做）。"""
    primary: list[dict] = []
    secondary: list[dict] = []
    control: list[dict] = []
    tally = Counter()
    for p in pairs:
        day = date.fromisoformat(p["trade_date"])
        st = v1.t1_state(regime, day)
        if st is None:
            tally["dropped_asof_macro"] += 1
            continue
        dominant, vol_pct = st
        macro_ok = (vol_pct is not None and vol_pct > v1.MACRO_VOL_H) or (dominant in v1.MACRO_TREND_STATES)
        emo, emo_t1, emo_dropped = emotion_state_for(phases, day)
        if emo_dropped:
            tally["emotion_dropped_asof"] += 1
        rec = dict(
            p,
            t1_dominant=dominant,
            t1_vol_pct=vol_pct,
            macro_gate="allow" if macro_ok else "deny",
            t1_six_phase=phases.get(emo_t1, "") if emo_t1 else "",
            emotion_gate=emo,
        )
        tally[f"emotion_{emo}"] += 1
        if not macro_ok:
            control.append(rec)  # 宏观禁做=对照集（情绪态无论何值不入主考）
        elif emo == "allow":
            primary.append(rec)
        elif emo == "deny":
            control.append(rec)
            tally["emotion_deny_within_macro_allow"] += 1
        else:
            secondary.append(rec)  # 卡 §2.3 副考，禁并入主考
    tally["primary"] = len(primary)
    tally["secondary"] = len(secondary)
    tally["control"] = len(control)
    return primary, secondary, control, dict(tally)


def stats_of(pairs: list[dict]) -> dict:
    if not pairs:
        return {
            "n_pairs": 0,
            "net_positive": 0,
            "edge_ge_30bp": 0,
            "gross_mean_bp": None,
            "net_mean_bp": None,
            "gross_p50_bp": None,
            "net_p50_bp": None,
            "edge_precondition_hit_rate": None,
        }
    gross = [p["gross_bp"] for p in pairs]
    net = [p["net_bp"] for p in pairs]
    return {
        "n_pairs": len(pairs),
        "net_positive": sum(1 for x in net if x > 0),
        "edge_ge_30bp": sum(1 for x in gross if x >= ct.EDGE_PRECONDITION_BP),
        "gross_mean_bp": round(statistics.fmean(gross), 2),
        "gross_p50_bp": round(statistics.median(gross), 2),
        "net_mean_bp": round(statistics.fmean(net), 2),
        "net_p50_bp": round(statistics.median(net), 2),
        "edge_precondition_hit_rate": round(sum(1 for x in gross if x >= ct.EDGE_PRECONDITION_BP) / len(gross), 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="条件化做T E4 双门考试 V2（T0-CONDITIONAL-V2 frozen 判据）")
    ap.add_argument("--artifacts-dir", default="data/backtest_artifacts")
    ap.add_argument("--emotion-truth", default=str(EMOTION_TRUTH))
    ap.add_argument("--out-dir", default="docs/_working/t0_matrix")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fills, mat_audit = load_intraday_fills(Path(args.artifacts_dir))
    pairs = ct.build_pairs(fills)  # 配对判据=cost_trio 同一函数（零重写）
    if not pairs:
        raise SystemExit("FAIL: 入样材料零配对（全单边？）——判据禁静默空结果")

    phases = load_emotion_phases(Path(args.emotion_truth))
    regime = v1.load_regime_states()
    primary, secondary, control, tally = split_gates(pairs, regime, phases)

    verdict = v1._verdict_for(primary, True)  # 五态判定复用；主考=双门均可评 ⇒ emotion_ok=True 口径
    result = {
        "card": "docs/_working/t0_matrix/t0_conditional_v2_prereg_card.md (frozen)",
        "mode": "dual_gate",
        "emotion_gate": {
            "available": True,
            "truth_source": str(args.emotion_truth),
            "allow_set": sorted(EMOTION_ALLOW),
            "pit": "T-1 交易日，asof 容差 7 自然日（与宏观门同构）",
        },
        "material_audit": mat_audit,
        "measured": {
            "n_fills_in_sample": len(fills),
            "n_pairs_total": len(pairs),
            "pair_days": sorted({p["trade_date"] for p in pairs}),
            "gate_tally": tally,
            "primary": stats_of(primary),
            "secondary_single_macro": stats_of(secondary),
            "control": stats_of(control),
        },
        "verdict": verdict,
        "criteria_provenance": {
            "pairing": "cost_trio_exam.build_pairs（import 复用）",
            "macro_gate": "t0_conditional_e4_exam.{MACRO_VOL_H,MACRO_TREND_STATES,ASOF_TOLERANCE_DAYS,t1_state,load_regime_states}",
            "five_state_verdict": "t0_conditional_e4_exam._verdict_for",
            "emotion_mapping": "auto_mount.{R2SIX,phase_overlay,resolve_six_phase}（经 six_phase_history_v1.csv 物化）",
            "cost_basis": "CST-T0-001 rt=31.2bp / 前置 30bp / 前置率 0.30 / 土规 30 对",
        },
    }
    (out_dir / "t0_conditional_e4_v2_result.yaml").write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    fields = [
        "symbol",
        "trade_date",
        "buy_qty",
        "sell_qty",
        "vwap_buy",
        "vwap_sell",
        "gross_bp",
        "net_bp",
        "realized_comm_bp",
        "fills",
        "runs",
        "t1_dominant",
        "t1_vol_pct",
        "t1_six_phase",
        "macro_gate",
        "emotion_gate",
        "set_name",
    ]
    with (out_dir / "t0_conditional_e4_v2_pairs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for name, coll in (("primary", primary), ("secondary", secondary), ("control", control)):
            for p in coll:
                w.writerow({**p, "set_name": name})
    print(
        yaml.safe_dump(
            {
                "material_audit": mat_audit,
                "gate_tally": tally,
                "primary": result["measured"]["primary"],
                "secondary_single_macro": result["measured"]["secondary_single_macro"],
                "control": result["measured"]["control"],
            },
            allow_unicode=True,
            sort_keys=False,
        )
    )
    print("verdict:", yaml.safe_dump(verdict, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
