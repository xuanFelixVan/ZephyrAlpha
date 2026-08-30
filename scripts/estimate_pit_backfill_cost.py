# [BLUEPRINT] MOD-PLAN-007 | docs/03_modules/_domain_plan_engine/llm_premarket_analysis/blueprint.md
# [MODULE] scripts.estimate_pit_backfill_cost
# [DOMAIN] D_PLAN
# [DEPENDENCIES] stdlib；zephyr.plan_engine.llm_premarket_analysis（DDL 字段与模型版本常量真源）
# [CONSUMERS] 44号 M3-⑨ PIT 回填成本预估（Owner 决策用，dry-run 不触发任何真实 API 调用）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯估算：不读真实 token 计数、不调 LLM API、不写 DB；token 量按 llm_premarket_analysis 七族输入规模区间 + 输出契约规模给保守中位估计；单价以 llm_runtime_gateway._PRICING_PER_MILLION 2026-08-22 校准版为锚（DeepSeek 峰谷分时 / Qwen 平价）
# [MODIFY-GUARD] 44_premarket_intraday_decision_upgrade §9.14；2026-08-22-llm-registry-reconciliation.md §四
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无外部副作用；非法参数 -> exit 2
# [TESTS] 无（一次性估算脚本）
# [A_module] module_id=MOD-SCRIPT-estimate_pit_backfill_cost | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""estimate_pit_backfill_cost.py — llm_premarket_analysis PIT 回填成本 dry-run 估算（44号 §9.14）

真源
----
- 44号 §9.14：回测 PIT 回填四铁律 + 七族输入 ~8-15K token / 输出 JSON 契约。
- llm_premarket_analysis.py：llm_daily_analysis DDL（tokens_in/tokens_out/cost_yuan 字段）
  与 v1/v2 调用编排（v1=1 次调用；v2 debate=3 次调用）。
- llm_runtime_gateway.py 2026-08-22 校准价表（元/百万 token，缓存未命中口径）：
  DeepSeek v4-flash 高峰 3.0/9.0、空闲 1.5/4.5；qwen-flash 0.15/1.5 无峰谷。

口径
----
- 730 交易日 ≈ 3 年 A 股交易日（244/年 × 3 ≈ 732，取整 730）。
- 输入 token 估计：七族数据包 canonical JSON + system prompt + 输出 schema 指令，
  中位 ~12K token（44号 §9.14 原文 "~8-15K token"）；min=8K，max=15K。
- 输出 token 估计：v1 单调用三情景 JSON ~600 token；v2 debate 三调用合计
  ~1800 token（bull 400 字 + bear 400 字 + arbiter JSON 600 token 量级）。
- DeepSeek 时段：盘前回填跑批设定在 08:00 前（谷时窗口 18:00-次日 9:00），
  故按 valley 价；若白天补跑则按 peak 价——脚本双通道并列输出。
- 不写真实 API 调用，不落库，纯 stdout 估算表。

用法
----
    python scripts/estimate_pit_backfill_cost.py                # 默认 730 日 v1+v2 双模式双通道
    python scripts/estimate_pit_backfill_cost.py --days 244     # 单年口径
    python scripts/estimate_pit_backfill_cost.py --mode v2      # 只看 v2 debate
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Final

# ── 估算常量（44号 §9.14 + 2026-08-22 校准价表）──

TRADING_DAYS_PER_YEAR: Final = 244  # A 股年交易日经验值
DEFAULT_DAYS: Final = 730  # ≈3 年（244×3=732 取整）

# 输入 token：七族数据包 + system prompt + schema 指令（44号 §9.14 "~8-15K token"）
INPUT_TOKENS_MIN: Final = 8_000
INPUT_TOKENS_MID: Final = 12_000
INPUT_TOKENS_MAX: Final = 15_000

# 输出 token：v1 单调用三情景 JSON 契约规模
OUTPUT_TOKENS_V1_MIN: Final = 400
OUTPUT_TOKENS_V1_MID: Final = 600
OUTPUT_TOKENS_V1_MAX: Final = 1_000

# v2 debate：bull(≤400字) + bear(≤400字) + arbiter(JSON) 三调用合计
OUTPUT_TOKENS_V2_MIN: Final = 1_200
OUTPUT_TOKENS_V2_MID: Final = 1_800
OUTPUT_TOKENS_V2_MAX: Final = 3_000

# 价表锚（元/百万 token，2026-08-22 校准，llm_runtime_gateway._PRICING_PER_MILLION 同口径）
PRICING: Final[dict[str, dict[str, float]]] = {
    "deepseek-v4-flash": {"peak_in": 3.0, "peak_out": 9.0, "valley_in": 1.5, "valley_out": 4.5},
    "qwen-flash": {"peak_in": 0.15, "peak_out": 1.5, "valley_in": 0.15, "valley_out": 1.5},
}


@dataclass(frozen=True)
class PitBackfillPitBackfillCostEstimate:
    """单通道单模式成本估算结果。"""

    channel: str
    mode: str  # v1 / v2
    days: int
    input_tokens_mid: int
    output_tokens_mid: int
    price_in: float  # 元/百万
    price_out: float  # 元/百万
    cost_per_day_mid: float  # 元
    cost_total_mid: float  # 元
    cost_total_min: float
    cost_total_max: float


def _estimate(channel: str, mode: str, days: int, *, use_peak: bool) -> PitBackfillCostEstimate:
    """按中位 token 量估算单通道单模式成本；min/max 供敏感性区间。"""
    price = PRICING[channel]
    suffix = "peak" if use_peak else "valley"
    price_in = price[f"{suffix}_in"]
    price_out = price[f"{suffix}_out"]

    if mode == "v1":
        in_mid, out_mid = INPUT_TOKENS_MID, OUTPUT_TOKENS_V1_MID
        in_min, out_min = INPUT_TOKENS_MIN, OUTPUT_TOKENS_V1_MIN
        in_max, out_max = INPUT_TOKENS_MAX, OUTPUT_TOKENS_V1_MAX
    else:  # v2 debate
        in_mid, out_mid = INPUT_TOKENS_MID, OUTPUT_TOKENS_V2_MID
        in_min, out_min = INPUT_TOKENS_MIN, OUTPUT_TOKENS_V2_MIN
        in_max, out_max = INPUT_TOKENS_MAX, OUTPUT_TOKENS_V2_MAX

    def _cost(in_tok: int, out_tok: int) -> float:
        return (in_tok / 1_000_000) * price_in + (out_tok / 1_000_000) * price_out

    per_day_mid = _cost(in_mid, out_mid)
    return PitBackfillCostEstimate(
        channel=channel,
        mode=mode,
        days=days,
        input_tokens_mid=in_mid,
        output_tokens_mid=out_mid,
        price_in=price_in,
        price_out=price_out,
        cost_per_day_mid=per_day_mid,
        cost_total_mid=per_day_mid * days,
        cost_total_min=_cost(in_min, out_min) * days,
        cost_total_max=_cost(in_max, out_max) * days,
    )


def _print_row(est: PitBackfillPitBackfillCostEstimate) -> None:
    print(
        f"| {est.channel} | {est.mode} | {est.days} | "
        f"{est.input_tokens_mid:,} / {est.output_tokens_mid:,} | "
        f"{est.price_in:.2f}/{est.price_out:.2f} | "
        f"{est.cost_per_day_mid:.4f} | "
        f"{est.cost_total_mid:.2f} | "
        f"{est.cost_total_min:.2f} ~ {est.cost_total_max:.2f} |"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="llm_premarket_analysis PIT 回填成本 dry-run 估算")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help=f"回填交易日数（默认 {DEFAULT_DAYS}≈3 年）")
    parser.add_argument("--mode", choices=("v1", "v2", "both"), default="both", help="调用模式（默认 both）")
    parser.add_argument(
        "--peak",
        action="store_true",
        help="DeepSeek 按高峰价估算（默认谷时价——回填跑批设定在 08:00 前谷时窗口）",
    )
    args = parser.parse_args(argv)
    if args.days <= 0:
        print("[ERROR] --days 须为正整数", file=sys.stderr)
        return 2

    modes = ("v1", "v2") if args.mode == "both" else (args.mode,)
    print("=" * 100)
    print("llm_premarket_analysis PIT 回填成本估算（dry-run，无真实 API 调用）")
    print(f"回填规模: {args.days} 交易日 | DeepSeek 时段: {'高峰' if args.peak else '谷时（默认 08:00 前）'}")
    print("价表锚: 2026-08-22 校准（DeepSeek 官网 2026-08-17 峰谷分时 / 百炼 qwen-flash 2026-07-31）")
    print("=" * 100)
    print()
    print("| 通道 | 模式 | 交易日 | 输入/输出 token（中位） | 单价 in/out（元/百万） | 单日成本（元） | 总成本（元） | 区间 min~max（元） |")
    print("|---|---|---|---|---|---|---|---|")
    for mode in modes:
        for channel in ("deepseek-v4-flash", "qwen-flash"):
            _print_row(_estimate(channel, mode, args.days, use_peak=args.peak))
    print()
    print("注：")
    print("- 输入 token 中位 12K（44号 §9.14 七族输入 ~8-15K 区间）；min=8K，max=15K。")
    print("- v1 输出中位 600 token（三情景 JSON 契约）；v2 debate 三调用合计中位 1,800 token。")
    print("- DeepSeek 谷时=北京 18:00-次日 9:00（回填跑批设定在 08:00 前，故默认谷时价）。")
    print("- Qwen 无峰谷，峰谷同价。")
    print("- 真实 token 以 llm_runtime_gateway infer 时 API usage 字段回填为准（当前为 len/4 估算）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
