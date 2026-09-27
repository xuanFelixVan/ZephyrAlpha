# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md | §4 材料资格 M-1..M-4 + §2 双门 + §5 判据
# [MODULE] t0_conditional_e4_v3_exam（scripts 判据脚本；T0-CONDITIONAL-V3 预注册卡 §6 执行件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/cost_trio_exam.py（build_pairs 配对判据唯一真源）；scripts/audit/t0_conditional_e4_exam.py（宏观门 t1_state/load_regime_states/常数 + 五态判定 _verdict_for）；scripts/audit/t0_conditional_e4_v2_exam.py（情绪门三态 emotion_state_for + 分组统计 stats_of，二者口径 V3 未改故复用）；docs/_working/t0_matrix/six_phase_history_v1.csv（六段真源）；data/backtest_artifacts/bt-*.json（材料）
# [CONSUMERS] Owner 复查窗；docs/_working/t0_matrix/t0_conditional_e4_v3_verdict.md；周五 GPU 矩阵做T 条件维验收；红蓝 PIT 断言
# [STARTUP] manual（python scripts/audit/t0_conditional_e4_v3_exam.py --artifacts-dir <主区材料目录>）
# [MATURITY] production（考试执行件，卡先行：t0_conditional_v3_prereg_card.md frozen 先于本脚本取数）
# [INVARIANTS] 判据数值零改动（成本 31.2bp/前置 30bp/前置率 0.30/土规 30 对/双门门规则全部 import 复用既有判据件，禁重写禁改常数）；本件唯一新逻辑=卡 §4 材料资格四判据 M-1 日内粒度、M-2 往返同体（逐 run 单独 build_pairs 禁跨 run 合并）、M-3 trade_log 哈希去重、M-4 涨跌停可行性硬门（阈值=交易所公开规则算术推论）；剔除必按原因计数入 material_audit，禁静默丢料；情绪门 unevaluable_day 走副考禁并入主考；fail-closed 五态枚举禁硬出；禁为过土规新增/延长材料（卡 §8.3 自禁线）；查库只读；产物只写 docs/_working/t0_matrix/（.yaml/.csv 禁 .json）；零状态变更
# [MODIFY-GUARD] 本脚本改动=考试判据变更，须先改卡并作废重开（卡 frozen 纪律）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 材料缺失/六段真源缺失=显式报错非静默空结果；四判据全剔致零入样=显式报错并披露各原因计数（禁把"无料"判成"无信号"）
# [TESTS] tests/audit/test_t0_conditional_e4_v3_exam.py（M-2 跨 run 污染必被剔/M-3 同指纹只计一次/M-4 超限剔除/主考禁收副考料）
# [TTL] task_bound
"""t0_conditional_e4_v3_exam.py — 条件化做T E4 双门考试 V3（往返身份修正版）

与 V2 的唯一差异=材料资格判据（卡 §4 M-1…M-4：配对必带 run 维 + 日志去重 + 涨跌停可行性）。
假设、双门门规则、成本口径、四条土规逐字继承，函数级 import 复用，零重写。
V2 及其产物按卡 §0.2 作废留档，本件不改写它们。

用法：
  python scripts/audit/t0_conditional_e4_v3_exam.py --artifacts-dir D:/ZephyrAlpha/data/backtest_artifacts
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cost_trio_exam as ct  # 配对判据唯一真源
import t0_conditional_e4_exam as v1  # 宏观门 + 五态判定
import t0_conditional_e4_v2_exam as v2  # 情绪门三态 + 分组统计（口径未变，复用）

EXAM_START = v2.EXAM_START  # 卡 §4 考窗起点 2026-06-01（承 V2，真源=第三方 frozen 卡）

# M-4 涨跌停可行性：单日理论极限毛价差 =(1+limit)/(1−limit)−1，全部由交易所公开比例算术推论
_PRICE_LIMIT_RATIO = {
    "gem_star": 0.20,  # 创业板 300/301、科创板 688/689 → ±20%
    "bse": 0.30,  # 北交所 4xx/8xx → ±30%
    "main": 0.10,  # 主板 → ±10%
}


def board_of(symbol: str) -> str:
    s = str(symbol).split(".")[0]
    if s.startswith(("300", "301", "688", "689")):
        return "gem_star"
    # 注：ST 类实为 ±5%，本卡不按 name 判 ST（材料 symbol 无名称字段）⇒ ST 主板股被套以 2222bp
    # 的偏松上限；红蓝⑪实测本材料零命中（max|gross|=491.66bp），无实质影响，如实登记。
    if s.startswith(("4", "8", "920")) and len(s) == 6:
        return "bse"
    return "main"


def max_feasible_gross_bp(symbol: str) -> float:
    lim = _PRICE_LIMIT_RATIO[board_of(symbol)]
    return ((1 + lim) / (1 - lim) - 1) * 1e4  # 主板上限 2222bp / 创业科创 5000bp / 北交 8571bp


def log_fingerprint(trade_log: list) -> str:
    return hashlib.sha256(json.dumps(trade_log, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_material(artifacts_dir: Path) -> tuple[list[dict], dict]:
    """卡 §4 M-1…M-3：逐件装载→指纹去重→日内粒度过滤→按 run 独立配对（M-2 在 pair_within_runs）。"""
    files = sorted(artifacts_dir.glob("bt-*.json"))
    if not files:
        raise SystemExit(f"FAIL: 材料缺失——{artifacts_dir} 下无 bt-*.json")
    audit: Counter[str] = Counter()
    seen_fp: dict[str, str] = {}
    runs: dict[str, list[dict]] = {}
    kept_files: list[str] = []
    for f in files:
        audit["files_total"] += 1
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            audit["parse_fail"] += 1
            sys.stderr.write(f"parse fail {f.name}: {exc}\n")
            continue
        trade_log = data.get("trade_log") or []
        if not trade_log:
            audit["files_empty_log"] += 1
            continue
        fp = log_fingerprint(trade_log)
        if fp in seen_fp:  # M-3 同指纹日志只取首个代表件（否则同流水换 run_id 重复计数至 7 次）
            audit["files_deduped_away"] += 1
            audit["fills_deduped_away"] += len(trade_log)
            continue
        seen_fp[fp] = f.name
        run_id = str(data.get("run_id") or f.stem)
        for t in trade_log:
            audit["fills_total"] += 1
            ts = str(t.get("timestamp", ""))
            if len(ts) <= 10:  # M-1 仅日期粒度=日线 bar，同日买卖属同 bar 聚合，不构成往返
                audit["fills_excluded_m1_daily_bar"] += 1
                continue
            day = ts[:10]
            if day < EXAM_START:
                audit["fills_excluded_m1_pre_exam_window"] += 1
                continue
            audit["fills_in_sample"] += 1
            runs.setdefault(run_id, []).append({**t, "trade_date": day, "run_id": run_id, "_log_fp": fp})
        if runs.get(run_id):
            kept_files.append(f.name)
    if not runs:
        raise SystemExit(f"FAIL: 四判据过滤后零入样——禁把'无料'判成'无信号'。审计={dict(audit)}")
    return kept_files, {"runs": runs, "keep_files": kept_files, **{k: v for k, v in audit.items()}}


def pair_within_runs(runs: dict[str, list[dict]]) -> tuple[list[dict], Counter]:
    """M-2 往返同体：逐 run 单独调用 build_pairs ⇒ 买/卖两腿必属同一组合。M-4 可行性硬门随后施加。"""
    tally: Counter[str] = Counter()
    pairs: list[dict] = []
    for run_id, fills in sorted(runs.items()):
        # M-2 加强（红蓝⑩构造性反例）：同一 run_id 若挂两个不同 trade_log 指纹，
        # 仍会把两套组合的买卖拼成假往返（跨件池化实测恰造 2 个假对）。此处 fail-closed。
        fps = {f.get("_log_fp") for f in fills if f.get("_log_fp")}
        if len(fps) > 1:
            raise SystemExit(
                f"FAIL: run_id={run_id} 挂了 {len(fps)} 个不同 trade_log 指纹"
                "——同 run_id 跨日志配对会重开假往返，禁在此出 verdict"
            )
        own = ct.build_pairs(fills)  # 配对判据=cost_trio 同一函数（零重写）
        tally["runs_with_pairs"] += int(bool(own))
        for p in own:
            tally["pairs_gross"] += 1
            cap = max_feasible_gross_bp(p["symbol"])
            if abs(p["gross_bp"]) > cap:  # M-4 超单日涨跌停理论极限=执行模型/数据异常，非可捕获价差
                tally["pairs_rejected_m4_price_limit"] += 1
                continue
            pairs.append({**p, "run_id": run_id})
    tally["runs_with_pairs"] = len({p["run_id"] for p in pairs})
    return pairs, tally


def _structural_findings(regime: dict) -> dict:
    """把可机算的结构性事实单列（与主诊断分离，保持两个函数各自短小）。"""
    allow = {"ignition", "expansion", "euphoria"}
    return {
        "state_domain_of_macro_source": sorted({str(d) for d, _ in regime.values() if d}),
        "r12_branch_reachable": any(str(d) == "r12" for d, _ in regime.values()),
        "macro_branch_disjointness": {
            "days_vol_gt_h": sum(1 for _, v in regime.values() if v is not None and v > v1.MACRO_VOL_H),
            "days_dominant_in_trend_set": sum(1 for d, _ in regime.values() if str(d) in v1.MACRO_TREND_STATES),
            "days_both_branches": sum(
                1
                for d, v in regime.values()
                if str(d) in v1.MACRO_TREND_STATES and v is not None and v > v1.MACRO_VOL_H
            ),
        },
        "emotion_allow_days_in_state_source": sum(1 for d, _ in regime.values() if str(d) in allow),
        "note": (
            "以上计数全部机算自本次取数的两份真源（regime_state_anchored 与六段物化件），"
            "禁把手写散文数字当结论；结构性解读见交付报告与 GPU 包 meta.caveats.dual_gate_anatomy"
        ),
    }


def gate_diagnostics(primary, secondary, control, regime, phases) -> dict:
    """主集为空的**机制**归因（披露层，不动任何判据）。双门口径下 n_gate=0 有三种可能成因，
    字面文案（沿用 v1 单门语境）分不出来，必须用计数分开：
    宏观门本身零命中 / 宏观命中但情绪判禁做 / 宏观命中但情绪不可评。"""
    from collections import Counter

    allp = [("primary", primary), ("secondary", secondary), ("control", control)]
    macro_allow = sum(1 for _, c in allp for p in c if p["macro_gate"] == "allow")
    six_ct = Counter(p.get("t1_six_phase") or "unrouted" for _, c in allp for p in c if p["macro_gate"] == "allow")
    return {
        "n_pairs_by_set": {"primary": len(primary), "secondary": len(secondary), "control": len(control)},
        "macro_gate_allow_pairs": macro_allow,
        "macro_allow_but_emotion_deny": sum(
            1 for _, c in allp for p in c if p["macro_gate"] == "allow" and p["emotion_gate"] == "deny"
        ),
        "macro_allow_but_emotion_unevaluable": sum(
            1 for _, c in allp for p in c if p["macro_gate"] == "allow" and p["emotion_gate"] == ""
        ),
        "six_phase_among_macro_allow": dict(six_ct.most_common()),
        "pair_days": sorted({p["trade_date"] for _, c in allp for p in c}),
        "t1_dominant_domain_in_material": sorted(
            {
                str(v1.t1_state(regime, date.fromisoformat(p["trade_date"]))[0])
                for _, c in allp
                for p in c
                if v1.t1_state(regime, date.fromisoformat(p["trade_date"]))
            }
        ),
        "reading": (
            "主集为零的真因不是宏观门未触发，而是**两门在考窗内互斥**：宏观门放行靠 "
            "vol_pct>0.700 分支，而高波动日恰落在 r4(=R2SIX accumulation) 与 capitulation/distribution "
            "等情绪禁做段；情绪门放行（expansion）的那几日常态 vol_pct 仅 0.48–0.51 不过宏观门。"
        ),
        "structural_findings_for_gpu_matrix": _structural_findings(regime),
    }


# NO-BARE-SQL 合规：SQL 提为模块级常量（§5.160.2 SQL 集中化），禁函数内字面量
_SQL_DUP_STATE_KEYS = "SELECT count() FROM (SELECT trade_date FROM {t} GROUP BY trade_date HAVING count() > 1)"


def assert_state_versions_unambiguous(regime: dict) -> None:
    """状态源 backtest_regime_state_anchored(逻辑品类) 是 ReplacingMergeTree（实测 system.tables）。
    未合并时同一 trade_date 有多个物理版本，v1.load_regime_states 的 dict 后写覆盖先写
    ⇒ 版本选取随物理序漂移（可能取到旧版）。本断言把"静默漂移"变成显式失败。
    今日实测 dup_keys=0（断言恒真），但它守的是合并进度变化后的那一天。"""
    from zephyr.data.table_registry import get_registry
    from zephyr.infrastructure.database_service import DatabaseService

    table = get_registry().table("backtest_regime_state_anchored")
    conn = DatabaseService().get_clickhouse_conn()
    dups = conn.execute(_SQL_DUP_STATE_KEYS.format(t=table))[0][0]
    if dups:
        raise SystemExit(
            f"FAIL: 状态源存在 {dups} 个多版本 trade_date（ReplacingMergeTree 未合并）——"
            "v1 加载器按物理序取版会静默选中旧版，禁在此状态下出 verdict；"
            "修法=load_regime_states 改 argMax(…, ingest_ts) 后作废重开考试"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="条件化做T E4 双门考试 V3（T0-CONDITIONAL-V3 frozen 判据）")
    ap.add_argument("--artifacts-dir", default="data/backtest_artifacts")
    ap.add_argument("--emotion-truth", default=str(v2.EMOTION_TRUTH))
    ap.add_argument("--out-dir", default="docs/_working/t0_matrix")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    keep_files, mat = load_material(Path(args.artifacts_dir))
    runs = mat.pop("runs")
    pairs, pair_tally = pair_within_runs(runs)
    if not pairs:
        raise SystemExit(
            f"FAIL: 入样材料零配对（全单边或被 M-4 全剔）——判据禁静默空结果。审计={mat} {dict(pair_tally)}"
        )

    phases = v2.load_emotion_phases(Path(args.emotion_truth))
    regime = v1.load_regime_states()
    assert_state_versions_unambiguous(regime)
    primary, secondary, control, tally = v2.split_gates(pairs, regime, phases)
    tally.update(dict(pair_tally))
    tally["pairs_entering_gates"] = len(pairs)

    verdict = v1._verdict_for(primary, True)  # 五态判定复用；主考=双门均可评口径
    diag = gate_diagnostics(primary, secondary, control, regime, phases)
    result = {
        "card": "docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md (frozen)",
        "supersedes": "T0-CONDITIONAL-V2（作废，卡 §0.2；其产物标 VOID 原样保留）",
        "mode": "dual_gate_within_run",
        "verdict_wording_note": (
            "五态判定件 _verdict_for 的 STATE_GATE_NEVER_TRIGGERED 结论文案沿用 v1 单门语境"
            "（'宏观门在材料窗零命中'）。双门口径下主集为空的**真因见 gate_diagnostics**——"
            "本班不改继承件文案（改=动判据件），改以诊断块如实纠偏，禁让读者按字面理解。"
        ),
        "gate_diagnostics": diag,
        "material_qualification": {
            "M1_intraday_granularity": "timestamp 长度>10 且日≥考窗起点",
            "M2_round_trip_within_one_run": "逐 run 单独 build_pairs（治跨组合假往返）",
            "M3_trade_log_dedup": "sha256(trade_log) 指纹，同指纹只取首个代表件",
            "M4_price_limit_feasibility": "abs(gross_bp) ≤ 该板 (1+lim)/(1−lim)−1 推论上限",
        },
        "emotion_gate": {
            "available": True,
            "truth_source": str(args.emotion_truth),
            "allow_set": sorted(v2.EMOTION_ALLOW),
            "pit": "T-1 交易日，asof 容差 7 自然日（与宏观门同构）",
        },
        "material_audit": mat,
        "measured": {
            "n_fills_in_sample": mat.get("fills_in_sample", 0),
            "n_pairs": len(pairs),
            "runs_with_pairs": pair_tally.get("runs_with_pairs", 0),
            "pair_days": sorted({p["trade_date"] for p in pairs}),
            "gate_tally": tally,
            "whole_material": v2.stats_of(pairs),
            "primary": v2.stats_of(primary),
            "secondary_single_macro": v2.stats_of(secondary),
            "control": v2.stats_of(control),
        },
        "verdict": verdict,
        "criteria_provenance": {
            "pairing": "cost_trio_exam.build_pairs（import 复用，逐 run 施加）",
            "macro_gate": "t0_conditional_e4_exam.{MACRO_VOL_H,MACRO_TREND_STATES,ASOF_TOLERANCE_DAYS,t1_state,load_regime_states}",
            "emotion_gate": "six_phase_history_v1.csv ← auto_mount.{R2SIX,phase_overlay,resolve_six_phase}",
            "five_state_verdict": "t0_conditional_e4_exam._verdict_for",
            "cost_basis": "CST-T0-001 rt=31.2bp / 前置 30bp / 前置率 0.30 / 土规 30 对",
        },
    }
    (out_dir / "t0_conditional_e4_v3_result.yaml").write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    fields = [
        "run_id",
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
    with (out_dir / "t0_conditional_e4_v3_pairs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for name, coll in (("primary", primary), ("secondary", secondary), ("control", control)):
            for p in coll:
                w.writerow({**p, "set_name": name})
    print(
        yaml.safe_dump(
            {
                "material_audit": mat,
                "pair_tally": dict(pair_tally),
                "gate_tally": tally,
                "gate_diagnostics": {k: v for k, v in diag.items() if k != "structural_findings_for_gpu_matrix"},
                "whole_material_unconditional": result["measured"]["whole_material"],
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
