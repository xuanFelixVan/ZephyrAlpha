# [BLUEPRINT] MOD-BT-187 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.bh_fdr
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.factor.analysis.bhy_fdr（canonical 决策核，对账 28a7403e86 §二单源裁定）; stdlib（math）
# [CONSUMERS] zephyr.strategy_pipeline.intake（sim 流转预授权门）; C6 管线及格判定扩展
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 决策核单源委托 canonical bhy_fdr（本模块只保留 dict 接口+步进报告，零自有统计实现）；BH 语义保持（arbitrary_dependence=False=预注册口径不变，升 BHY True=收紧裁定待策略域拍板）；零假设族=同一批次内全部待检策略（含已过 §8 门者——选择偏差必须全员入族）；空族/q 越界前置校验；同输入必同输出
# [MODIFY-GUARD] tests/strategy_pipeline/test_bh_fdr.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(空族/q 越界/NaN p)
# [TESTS] tests/strategy_pipeline/test_bh_fdr.py
# [A_module] module_id=MOD-BT-187 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] bh-fdr-mod-bt-187-20260915
"""BH-FDR 门——全自动入库管线的假发现率控制（对账 28a7403e86 §二：决策核已单源收敛）。

决策核委托 canonical `zephyr.factor.analysis.bhy_fdr`（MOD-L02-BHY）——本模块
只保留 intake 契约（dict 接口+步进报告）与预注册语义（arbitrary_dependence=False
=BH 口径，与收敛前逐位一致；升 BHY 只需调用方传 True，属策略域收紧裁定）。

为什么需要：全自动管线没有"这结果看着不对"的人工直觉兜底；§8 双窗土规是逐条判定，
不校正当批多重检验的选择偏差。BH 程序把"批内挑最"的假发现率压到 q 上界以内
（Harvey & Liu 2020 / Benjamini-Hochberg 1995；SSRN 4686376 等 2024-2026 文献一致口径）。

用法（默认 q=0.10，预授权写死在 intake guard）:
    from zephyr.strategy_pipeline.bh_fdr import bh_filter
    keep, report = bh_filter(p_values={"CAND-a": 0.01, ...}, q=0.10)
    # keep: {"CAND-a"}；report: 逐条 {p, bh_rank, bh_threshold, passed, reason}
"""

from __future__ import annotations

import math
from typing import Any

from zephyr.factor.analysis.bhy_fdr import bhy_fdr


def bh_filter(
    p_values: dict[str, float], q: float = 0.10, *, arbitrary_dependence: bool = False
) -> tuple[set[str], dict[str, dict[str, Any]]]:
    """Benjamini-Hochberg FDR 过滤：返回（通过集，逐条报告）。

    决策核委托 canonical bhy_fdr（对账裁定单源）；步进单调通过集语义不变：
    通过集=最大通过 rank 之前的全部条目（防挑尾）。
    """
    if not p_values:
        raise ValueError("空假设族：BH 必须以同批全部待检策略入族（含已过 §8 者防选择偏差）")
    if not 0 < q <= 1:
        raise ValueError(f"q 越界: {q}（合法 (0, 1]）")
    if any(
        isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p)
        for p in p_values.values()
    ):
        raise ValueError("p 值含非有限值")
    ranked = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(ranked)
    if q >= 1:
        # 退化态：q=1=无过滤力（intake 预注册契约 q∈(0,1] 合法），全部步进通过
        # （canonical bhy_fdr 定义域为开区间 (0,1)，退化态在本层短路）
        report = {
            sid: {"p": p, "bh_rank": k, "bh_threshold": round(k / m * 1.0, 6),
                  "passed": True, "reason": "q>=1_degenerate_no_filter"}
            for k, (sid, p) in enumerate(ranked, start=1)
        }
        return {sid for sid, r in report.items() if r["passed"]}, report

    result = bhy_fdr([p for _, p in ranked], q=q, arbitrary_dependence=arbitrary_dependence)
    last_pass = max(
        (rank for rank, rej in enumerate(result.rejected, start=1) if rej), default=0
    )
    report: dict[str, dict[str, Any]] = {}
    for k, (sid, p) in enumerate(ranked, start=1):
        threshold = k / m * q
        passed = last_pass >= k  # 步进：只有最靠前的连续通过段才算（防挑尾）
        report[sid] = {
            "p": p,
            "bh_rank": k,
            "bh_threshold": round(threshold, 6),
            "passed": passed,
            "reason": "stepwise_pass" if passed else (
                f"p>{threshold:.4g}（rank {k}/{m}，q={q}）" if k > last_pass else "beyond_last_pass_step"),
        }
    keep = {sid for sid, r in report.items() if r["passed"]}
    assert all(math.isfinite(r["p"]) for r in report.values()), "p 含非有限值"
    return keep, report
