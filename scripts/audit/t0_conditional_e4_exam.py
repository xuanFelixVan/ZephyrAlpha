# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_revival/t0_conditional_prereg_card.md | §2 状态门+§5 判据
# [MODULE] t0_conditional_e4_exam（scripts 判据脚本；T0-CONDITIONAL 预注册卡 §6 执行件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/cost_trio_exam.py（配对判据复用）；c1_backtest.regime_state_anchored（宏观门，只读）；c1_market.sentiment_panel（情绪门数据可得性核查，只读）；data/backtest_artifacts/bt-*.json（材料）
# [CONSUMERS] Owner 复查窗；t0_conditional_e4_verdict.md（verdict 留档）
# [STARTUP] manual（python scripts/audit/t0_conditional_e4_exam.py）
# [MATURITY] production（考试执行件，卡先行纪律：t0_conditional_prereg_card.md frozen 先于本脚本取数）
# [INVARIANTS] 判据全部来自 frozen 卡（禁脚本内改判据=禁裸跑）；fail-closed：样本不足/门不可评/状态门零命中落卡 §5 五态枚举，禁硬出；情绪门历史不可评=单宏观门+emotion_gate=unevaluable 显式标记（禁用他轴指标顶替六段词表——前视偏差与词表越轴禁令）；查库只读（DatabaseService reader）；产物只写 docs/_working/t0_revival/（.yaml，目录契约禁 .json）；零状态变更
# [MODIFY-GUARD] 本脚本改动=考试判据变更，须先改卡并作废重开（卡 frozen 纪律）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达/材料缺失=显式报错非静默空结果；状态 asof 容差外=弃日计数披露不硬凑
# [TESTS] verdict 枚举与卡 §5 一致；配对数与 cost_trio 基线（24）对账
# [TTL] task_bound
"""t0_conditional_e4_exam.py — 条件化做T E4 考试执行件（T0-CONDITIONAL 卡 §6，frozen 判据）

判据真源：docs/_working/t0_revival/t0_conditional_prereg_card.md（frozen）。本脚本只是卡的机械执行：
- 材料：bt-*.json trade_log，D=2026-09-09 后成交；配对=cost_trio 同规则。
- 宏观门（PIT=T-1 交易日，asof ≤7 自然日容差）：vol_pct>0.700 或 dominant∈{r3,r12}。
- 情绪门：丁线六段历史标签不存在（sentiment_panel 仅 fear_greed_index，异轴禁顶替）→ 单宏观门模式，
  emotion_gate=unevaluable 显式入 verdict。
- 土规：n_gate_pairs≥30 出结论；≥0 命中才评；前置命中率≥0.30；net_mean>0。
"""

from __future__ import annotations

import argparse
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cost_trio_exam as ct  # 配对判据复用（禁克隆）

MACRO_VOL_H = 0.700  # 卡 §2.1 frozen（H 桶下界）
MACRO_TREND_STATES = {"r3", "r12"}  # 卡 §2.1 frozen（牛市趋势/突破）
ASOF_TOLERANCE_DAYS = 7  # 卡 §2.1 frozen
PRECONDITION_HIT_RATE_MIN = 0.30  # 卡 §5 frozen
PAIR_GATE = 30  # 卡 §5 frozen


def load_regime_states() -> dict[date, tuple[str | None, float | None]]:
    from zephyr.data.table_registry import get_registry
    from zephyr.infrastructure.database_service import DatabaseService

    table = get_registry().table("backtest_regime_state_anchored")
    conn = DatabaseService().get_clickhouse_conn()
    rows = conn.execute(f"SELECT trade_date, dominant, vol_pct FROM {table} ORDER BY trade_date")  # noqa: bare-sql  文档区判据脚本一次性只读探针，不可机械集中化
    return {r[0]: (r[1], float(r[2]) if r[2] is not None else None) for r in rows}


def t1_state(states: dict[date, tuple], day: date) -> tuple[str | None, float | None] | None:
    """PIT=T-1 交易日读数，asof 向后容差；容差外= None（弃日，披露）。"""
    cands = [d for d in states if d < day]
    if not cands:
        return None
    d = max(cands)
    if (day - d).days > ASOF_TOLERANCE_DAYS:
        return None
    return states[d]


def emotion_gate_availability() -> tuple[bool, str]:
    """核查丁线六段历史标签是否存在（禁顶替）。存在返回 (True, 来源)；否则 (False, 原因)。"""
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    from zephyr.data.table_registry import get_registry

    sentiment_table = get_registry().table("market_sentiment_panel")
    metrics = [r[0] for r in conn.execute(f"SELECT DISTINCT metric FROM {sentiment_table}")]  # noqa: bare-sql  情绪门可得性一次性只读探针，不可机械集中化
    # 六段词表官方拼写（capitulation/accumulation/ignition/expansion/euphoria/distribution）
    # 及其带前缀的变体（emotion.*）——sentiment_panel 现存 metric 仅 fear_greed_index 等，均非六段。
    six_vocab = {"capitulation", "accumulation", "ignition", "expansion", "euphoria", "distribution"}
    hit = [m for m in metrics if str(m).lower() in six_vocab or str(m).lower().endswith(tuple(six_vocab))]
    if hit:
        return True, ",".join(hit)
    return False, (
        f"sentiment_panel metrics={metrics} 无丁线情绪六段历史标签（fear_greed_index 为异轴指标，"
        "卡 §2.2 禁顶替）；六段持久化为前瞻接线义务"
    )


def _verdict_for(gate_pairs: list[dict], emotion_ok: bool) -> dict:
    """卡 §5 五态枚举的机械判定（frozen 判据，拆分以控复杂度）。"""
    n_gate = len(gate_pairs)
    if n_gate == 0:
        return {
            "status": "STATE_GATE_NEVER_TRIGGERED",
            "conclusion": "宏观门在材料窗零命中（门规则与窗不相容），如实披露",
        }
    if n_gate < PAIR_GATE:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "conclusion": f"门内配对数 {n_gate} < {PAIR_GATE}（卡 §5 土规），禁硬出方向性结论",
        }
    gross = [p["gross_bp"] for p in gate_pairs]
    net = [p["net_bp"] for p in gate_pairs]
    hit_rate = sum(1 for g in gross if g >= ct.EDGE_PRECONDITION_BP) / n_gate
    if hit_rate < PRECONDITION_HIT_RATE_MIN:
        return {"status": "FAIL", "conclusion": f"开仓前置命中率 {hit_rate:.2%} < 0.30，门内毛边际不存在"}
    if statistics.fmean(net) > 0:
        status = "PASS-待考" if emotion_ok else "PASS-单门"
        suffix = "；情绪门不可评，须双门复考后方可进一步推进" if not emotion_ok else ""
        return {"status": status, "conclusion": "前置命中率与净期望双过（卡 §5）" + suffix}
    return {"status": "FAIL", "conclusion": f"净期望 {statistics.fmean(net):.2f}bp ≤ 0（fail-closed）"}


def _split_by_macro_gate(pairs: list[dict], regime: dict) -> tuple[list[dict], list[dict], int]:
    """按宏观门（PIT=T-1）分桶：返回 (命中, 对照, asof 弃日数)。卡 §2.1 frozen 规则。"""
    gate_pairs: list[dict] = []
    control_pairs: list[dict] = []
    dropped_asof = 0
    for p in pairs:
        day = date.fromisoformat(p["trade_date"])
        st = t1_state(regime, day)
        if st is None:
            dropped_asof += 1
            continue
        dominant, vol_pct = st
        macro_ok = (vol_pct is not None and vol_pct > MACRO_VOL_H) or (dominant in MACRO_TREND_STATES)
        p2 = dict(p, t1_dominant=dominant, t1_vol_pct=vol_pct, macro_gate="allow" if macro_ok else "deny")
        (gate_pairs if macro_ok else control_pairs).append(p2)
    return gate_pairs, control_pairs, dropped_asof


def main() -> int:
    ap = argparse.ArgumentParser(description="条件化做T E4 考试（T0-CONDITIONAL frozen 判据执行）")
    ap.add_argument("--artifacts-dir", default="data/backtest_artifacts")
    ap.add_argument("--out-dir", default="docs/_working/t0_revival")
    ap.add_argument("--no-db", action="store_true", help="仅离线配对（不起 CH），verdict 强制 INSUFFICIENT")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fills, skips = ct.load_d_after_fills(Path(args.artifacts_dir))
    pairs = ct.build_pairs(fills)
    if not pairs:
        raise SystemExit("FAIL: 配对为零（材料缺失或全单边）——判据禁静默空结果")

    emotion_ok, emotion_detail = (False, "no-db 模式") if args.no_db else emotion_gate_availability()
    mode = "single_macro_gate" if not emotion_ok else "dual_gate"
    if emotion_ok:
        raise SystemExit("FAIL: 情绪门历史已可用，但本脚本尚未实现双门取数——按卡纪律作废重开，禁单门硬出")

    regime = load_regime_states() if not args.no_db else {}
    gate_pairs, control_pairs, dropped_asof = _split_by_macro_gate(pairs, regime)

    verdict = _verdict_for(gate_pairs, emotion_ok)

    result = {
        "card": "docs/_working/t0_revival/t0_conditional_prereg_card.md (frozen)",
        "mode": mode,
        "emotion_gate": {"available": emotion_ok, "detail": emotion_detail},
        "measured": {
            "n_pairs_total": len(pairs),
            "n_gate_pairs": len(gate_pairs),
            "n_control_pairs": len(control_pairs),
            "dropped_asof_days": dropped_asof,
            "gate_pairs_days": sorted({p["trade_date"] for p in gate_pairs}),
            "gate_edge_ge_30bp": sum(1 for p in gate_pairs if p["gross_bp"] >= ct.EDGE_PRECONDITION_BP),
            "gate_net_positive": sum(1 for p in gate_pairs if p["net_bp"] > 0),
            "gate_gross_mean_bp": round(statistics.fmean(p["gross_bp"] for p in gate_pairs), 2) if gate_pairs else None,
            "gate_net_mean_bp": round(statistics.fmean(p["net_bp"] for p in gate_pairs), 2) if gate_pairs else None,
            "control_gross_mean_bp": round(statistics.fmean(p["gross_bp"] for p in control_pairs), 2)
            if control_pairs
            else None,
            "control_net_mean_bp": round(statistics.fmean(p["net_bp"] for p in control_pairs), 2)
            if control_pairs
            else None,
            "material_parse_skips": len(skips),
        },
        "verdict": verdict,
    }
    (out_dir / "t0_conditional_e4_result.yaml").write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(yaml.safe_dump(result["measured"], allow_unicode=True, sort_keys=False))
    print("verdict:", yaml.safe_dump(verdict, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
