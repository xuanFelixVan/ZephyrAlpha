# [BLUEPRINT] MOD-BT-032 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.print_regime_history
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.regime.regime_feature_builder; zephyr.regime.core.regime_detector; zephyr.data.ch_writer; zephyr.backtest.run_archive
# [CONSUMERS] P0-001 L1-AGG 回放; P0-002 总闸回放; 衰减巡检对照
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] PIT 铁律(detect(t) 只用 ≤t-1 特征,builder 内置 shift(1)); 台账/教材表只增不改(重印=新 run_id); 落盘走 run_archive API 禁手 mkdir; 落库失败不归档(fail-closed)
# [MODIFY-GUARD] tests/backtest/test_print_regime_history.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/落库未确认)
# [TESTS] tests/backtest/test_print_regime_history.py
# [A_module] module_id=MOD-BT-032 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P0 印教材——RegimeSnapshot walk-forward 历史逐日落库（SOP-A Step A3 P0 批 / SOP-B ③缺口取数）。

数据链（复用 G03 C1 real 模式骨架，零新算法）:
  ClickHouse(c1_market.kline_index 等) → RegimeFeatureBuilder(6特征+walk-forward 季度重拟合)
  → RegimeDetector.detect 逐日 → 7 维灰度概率 + Shrinkage 三元组
  → c1_backtest.regime_snapshot_history 落库(ch_writer TSV) → run 档案归档(run_archive API)

方法学调研结论（SOP-B ①）：考试大纲现成=11_regime_backtest_validation_plan（B1/B2/B4/C1 四接口，
G03 模块级验收曾全通过）；P0-001 节点级验证=agg_discrimination（validation_method_registry），
本脚本只做其输入重建（印教材），区分度检验在 P0-001 检验脚本。

G07 教训防复发（docs/_working/2026-09-11-g07-sentiment-validation.md §4）：
  RegimeDetector 结构上无链式先验（HMM 后验由 trailing 窗口+当季模型决定，非递归先验）、
  无兜底强制保守分支（仅 fit 失败→均匀分布降级，次季自愈）——但脚本侧仍输出
  state_health QA（各态占比/最长连续同态天数），防"长期锁死单一态"类路径依赖蒙混入库。

Usage:
  python scripts/backtest/print_regime_history.py --dry-run   # 预演（建 run 档案但不落库）
  python scripts/backtest/print_regime_history.py             # 正式：2019-01-01~今
依据: 11_regime_backtest_validation_plan §4/§7 / SOP-D 档案规范 / P-BT-001（evidence-log 讨论稿 §八 R1）
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from zephyr.backtest.run_archive import create_run, finalize_run, write_step
from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.features.regime_data_loader import RegimeDataLoader
from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

logger = logging.getLogger(__name__)

_TABLE = "c1_backtest.regime_snapshot_history"
_INSERT_COLUMNS = (
    "(run_id, snapshot_commit, trade_date, p_r1, p_r2, p_r3, p_r4, p_r10, p_r11, p_r12,"
    " dominant, confidence, confidence_signal, risk_signal, shrinkage, probs_json)"
)
_STATE_KEYS = ("r1", "r2", "r3", "r4", "r10", "r11", "r12")

DEFAULT_START = "2019-01-01"
DEFAULT_LOAD_START = "2014-01-01"  # walk-forward 5 年训练历史


def _tsv_cell(v: Any) -> str:
    """CH TSV 转义：None→\\N，制表符清洗（runner 同款，防列错位）。"""
    if v is None:
        return "\\N"
    return str(v).replace("\t", " ")


def _state_health(dominants: pd.Series) -> str:
    """G07 教训 QA：七态分布健康度（占比/最长连续同态），markdown 表格。"""
    counts = dominants.value_counts()
    total = max(len(dominants), 1)
    longest, cur, prev = 0, 0, None
    for d in dominants.tolist():
        cur = cur + 1 if d == prev else 1
        prev = d
        longest = max(longest, cur)
    lines = [
        "| 态 | 天数 | 占比 |",
        "|---|---|---|",
    ]
    for k in _STATE_KEYS:
        n = int(counts.get(k, 0))
        lines.append(f"| {k} | {n} | {100.0 * n / total:.1f}% |")
    lines.append("")
    lines.append(f"- 交易日总数: {len(dominants)}")
    lines.append(f"- 最长连续同态: {longest} 天（>250 天=疑似锁死，需人工复核后再用于 P0 检验）")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    """主流程：开档 → walk-forward 收集 → QA → 落库 → 归档。"""
    start = args.start
    end = args.end
    load_start = args.load_start
    now = datetime.now()
    run_id = f"VAL-P0-{now.strftime('%Y%m%d-%H%M%S')}"

    # ① 开档（SOP-D：禁手 mkdir，走 API；dry-run 也开档——过程留痕原则）
    run_dir = create_run(
        run_id=run_id,
        object_id="BT-P0-001",
        kind="VAL",
        window={"start": start, "end": end},
        holdout={"mode": "anchor", "cutoff": "2026-09-09"},
        cost_mode="rough",
        created_by="ai-session:p0-print-regime",
    )
    logger.info("run 档案已开: %s", run_dir)

    # ② walk-forward 收集（prob_sink 钩子收 7 维概率；build_shrinkage_schedule 内置 PIT shift(1)）
    collected: list[dict[str, Any]] = []

    def _sink(dt: datetime, probs: Any) -> None:
        collected.append({"dt": dt, "probs": probs})

    data_loader = RegimeDataLoader(data_load_start=load_start, backtest_end=end)
    builder = RegimeFeatureBuilder(
        backtest_start=start,
        backtest_end=end,
        data_load_start=load_start,
        enable_full_risk=(args.risk_mode == "full"),
        enable_overlay=(args.overlay == "on"),
        enable_phase2c=True,
        data_loader=data_loader,
    )
    detector = RegimeDetector(shrinkage_enabled=True)
    schedule = builder.build_shrinkage_schedule(
        detector,
        train_years=args.train_years,
        detect_window=args.detect_window,
        prob_sink=_sink,
    )
    logger.info("walk-forward 完成: %d 日 schedule, %d 日概率", len(schedule), len(collected))
    if not collected:
        raise RuntimeError("概率收集为空（prob_sink 未触发）——检查 detect 窗口与数据区间")

    # ③ QA（G07 教训：健康度检查）
    rows = []
    for item in collected:
        p: Any = item["probs"]
        dt = item["dt"]
        # build_shrinkage_schedule 的 schedule 值=float(shrinkage.value)；分量（confidence_signal/
        # risk_signal）不经该接口暴露，置 None（教材核心=7 维概率；P0-002 需分量时再扩展 builder）
        sh_val = schedule.get(dt)
        probs_json = json.dumps(
            {
                "probabilities": {k: round(float(p.probabilities.get(k, 0.0)), 6) for k in _STATE_KEYS},
                "hmm": {k: round(float(v), 6) for k, v in (p.hmm_probabilities or {}).items()},
                "overlay": {k: round(float(v), 6) for k, v in (p.overlay_probabilities or {}).items()},
                "schema_version": p.schema_version,
            },
            allow_nan=False,
        )
        rows.append(
            {
                "trade_date": dt.strftime("%Y-%m-%d"),
                "p_r1": float(p.probabilities.get("r1", 0.0)),
                "p_r2": float(p.probabilities.get("r2", 0.0)),
                "p_r3": float(p.probabilities.get("r3", 0.0)),
                "p_r4": float(p.probabilities.get("r4", 0.0)),
                "p_r10": float(p.probabilities.get("r10", 0.0)),
                "p_r11": float(p.probabilities.get("r11", 0.0)),
                "p_r12": float(p.probabilities.get("r12", 0.0)),
                "dominant": p.dominant_regime,
                "confidence": float(p.confidence),
                "confidence_signal": None,
                "risk_signal": None,
                "shrinkage": float(sh_val) if sh_val is not None else None,
                "probs_json": probs_json,
            }
        )
    df = pd.DataFrame(rows)
    health_md = _state_health(df["dominant"])

    # ④ 产物归档（先产物后落库：落库失败=run 留在未归档态，巡检器曝光，不造已归档假象）
    write_step(run_id, "01", (
        "# 候选方法学调研结论\n\n"
        "- 考试大纲现成：11_regime_backtest_validation_plan（B1 校准/B2 CRPS/B4 转换触发/C1 Shrinkage 开关四接口），"
        "G03 模块级验收四项曾全通过——无需新增全网调研。\n"
        "- P0-001 节点级判据=agg_discrimination（validation_method_registry.yaml），本 run 仅做其输入重建（印教材）。\n"
        "- 结构自查（G07 教训）：RegimeDetector 无链式先验/无兜底强制保守分支；state_health QA 见 06_narrow/qa_report.md。\n"
    ))
    write_step(run_id, "02", (
        "# DATA-GAP 清单\n\n"
        "- [已备] 4 指数日线：c1_market.kline_index（000300/000905/399006/399106，覆盖至回测前一日）\n"
        "- [已备] 判定器：src/zephyr/regime/core/regime_detector.py（production）\n"
        "- [已备] 特征管道：src/zephyr/regime/regime_feature_builder.py（C1 real 已验证）\n"
        "- [无缺口] 前向收益窗口数据（区分度检验侧需求，检验脚本开工时另行核查 kline_index 收盘价可得性）\n"
    ))
    write_step(run_id, "03", (
        "# 数据清单\n\n"
        "- name: 指数日线\n"
        "  source: c1_market.kline_index（ClickHouse）\n"
        "  symbols: ['000300','000905','399006','399106']\n"
        f"  window: {{start: {load_start}, end: {end}}}\n"
        "  pit_note: '特征 shift(1)，detect(t) 只用 ≤t-1；builder 内置（C1 一票否决前提）'\n"
        "  proxy: false\n"
    ))
    write_step(run_id, "05", (
        "# 剪枝记录\n\n不适用：印教材为全量逐日落库（剪枝语义属于信号/因子筛选，教材保留全部交易日）。\n"
    ))
    qa_path = write_step(run_id, "06", (
        f"# 印教材 QA 报告\n\n窗口: {start} ~ {end}\n行数: {len(df)}\n\n## 七态分布健康度\n\n{health_md}\n\n"
        f"## 数值健康\n\n- NaN 概率格数: {int(df[['p_r1','p_r2','p_r3','p_r4','p_r10','p_r11','p_r12']].isna().sum().sum())}\n"
        f"- 概率行和!=1 的行数: {int((df[['p_r1','p_r2','p_r3','p_r4','p_r10','p_r11','p_r12']].sum(axis=1) - 1.0).abs().gt(1e-6).sum())}\n"
        f"- Shrinkage 均值: {df['shrinkage'].mean():.4f} / <1.0 占比: {100.0 * (df['shrinkage'] < 1.0).mean():.1f}%\n"
    ), filename="qa_report.md")

    # ⑤ 落库（ch_writer TSV，CH_COMMITTED 才算成功——fail-closed）
    if args.dry_run:
        logger.info("dry-run: %d 行不落库（run_id=%s，档案保留）", len(df), run_id)
        return {"run_id": run_id, "rows": len(df), "dry_run": True, "qa_path": str(qa_path)}

    from zephyr.backtest.core.engine_base import current_map_snapshot
    from zephyr.data import ch_writer

    snapshot_commit = current_map_snapshot()
    tsv_lines = []
    for r in rows:
        cells = [
            run_id, snapshot_commit, r["trade_date"],
            r["p_r1"], r["p_r2"], r["p_r3"], r["p_r4"], r["p_r10"], r["p_r11"], r["p_r12"],
            r["dominant"], r["confidence"], r["confidence_signal"], r["risk_signal"], r["shrinkage"],
            r["probs_json"],
        ]
        tsv_lines.append("\t".join(_tsv_cell(c) for c in cells))
    tsv = ("\n".join(tsv_lines) + "\n").encode("utf-8")
    written = ch_writer.write_tsv(_TABLE, _INSERT_COLUMNS, tsv)
    if not written:
        raise RuntimeError(
            f"教材表落库未确认 CH_COMMITTED（run_id={run_id}）——fail-closed：查 ch_writer 落盘兜底，不归档"
        )
    logger.info("教材表落库确认: %d 行 → %s", len(df), _TABLE)

    # ⑥ 归档（verdict 判定书先落，finalize 校验 kind×必选矩阵）
    write_step(run_id, "verdict", (
        f"# 判定书：{run_id}\n\n"
        f"对象/节点：BT-P0-001（TDM-E-L1-AGG 输入重建——印教材）｜ kind=VAL ｜ 窗口={start}~{end} ｜ 成本口径=rough（不适用）\n"
        "结论：verdict=done（教材印制完成，非研究结论）｜ significance=ok ｜ "
        "verdict_reason=method_not_applicable（本 run 为数据准备，区分度检验在 P0-001 检验批）\n"
        "判定链：SOP-B ③缺口取数完成即归档；本 run 不下策略/判定结论。\n\n"
        f"关键数字：\n- 落库 {len(df)} 行 → {_TABLE}（CH_COMMITTED 确认）\n"
        f"- 七态分布：{', '.join(f'{k} {100.0 * n / len(df):.1f}%' for k, n in df['dominant'].value_counts().items())}\n"
        f"- Shrinkage 均值 {df['shrinkage'].mean():.4f}（EMA α=0.15）\n"
        "遗留问题：confidence_signal/risk_signal 分量列暂 NULL（P0-002 需要时扩展 builder）\n\n"
        f"台账回执：verdict_ref={_TABLE} run_id={run_id}\n"
    ))
    meta = finalize_run(
        run_id,
        verdict_ref={"table": _TABLE, "run_id": run_id},
        linked_artifacts=[],
    )
    return {
        "run_id": run_id,
        "rows": len(df),
        "window": {"start": start, "end": end},
        "table": _TABLE,
        "dominant_dist": df["dominant"].value_counts().to_dict(),
        "finalized_at": meta.get("finalized_at"),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="P0 印教材：RegimeSnapshot walk-forward 历史逐日落库")
    parser.add_argument("--start", default=DEFAULT_START, help="回测窗口起点（默认 2019-01-01，IS 起点）")
    parser.add_argument("--end", default=datetime.now().strftime("%Y-%m-%d"), help="回测窗口终点（默认今）")
    parser.add_argument("--load-start", default=DEFAULT_LOAD_START, help="数据加载起点（默认 2014-01-01=起点前 5 年训练窗）")
    parser.add_argument("--train-years", type=int, default=5, help="walk-forward 训练窗口年数（默认 5）")
    parser.add_argument("--detect-window", type=int, default=60, help="detect trailing 窗口（默认 60 日）")
    parser.add_argument("--risk-mode", choices=["simple", "full"], default="full", help="risk 参数模式（生产默认 full）")
    parser.add_argument("--overlay", choices=["off", "on"], default="on", help="overlay 信号开关（生产默认 on；构造器缺失自动降级）")
    parser.add_argument("--dry-run", action="store_true", help="预演：建 run 档案但不落库")
    args = parser.parse_args()
    result = run(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
