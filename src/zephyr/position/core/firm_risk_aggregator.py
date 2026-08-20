# [BLUEPRINT] MOD-POS-021 | docs/03_modules/_domain_position/firm_risk_aggregator/blueprint.md
# [MODULE] zephyr.position.core.firm_risk_aggregator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.strategy_book
# [CONSUMERS] MOD-POS-001(position_sizing_engine消费FirmTargetPortfolio)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 自然叠加(S1给3%+S2给5%=8%); 单票硬上限裁剪按比例削(非按策略优先级截断); 不做MVO不做协方差估计; O(N)复杂度; 冲突标的按净额处理
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AggregationError(ZA-POS-0021); ConstraintViolationError(ZA-POS-0023)
# [TESTS] tests/position/test_firm_risk_aggregator.py
# [A_module] module_id=MOD-POS-021 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


FirmRiskAggregator — Firm层风险聚合器 (MOD-POS-021)

A 模型（30_multi_strategy_concurrency §2.2）的组合汇总层。消费所有 StrategyBook 的
TargetPortfolio，**按标的求和（自然叠加）+ 组合级硬上限裁剪 + 冲突净额处理**，
产出 FirmTargetPortfolio 交由 MOD-POS-001 精裁决。

核心哲学（30_multi_strategy_concurrency §2.3）：用加法替代优化器，O(N) 替代 O(N²)。
多策略选到同一只票时仓位自然叠加，等价于永远稳定的等权 risk-budget 优化器。

不做什么：MVO/协方差估计（§3.1 拒绝）/ Kelly（归 MOD-POS-001）/
         选股（归 StrategyBook）/ 跨策略投票（§3.2 拒绝 Model D）

两段接口（32号 §2.1.1 v1.0.19）：
    StrategyBook → pre_kelly_aggregate → MOD-PO-001 Kelly → post_kelly_clip → FirmTargetPortfolio

依据: 30_multi_strategy_concurrency §2.2/§2.3/§3.1 + 32_firm_risk_aggregator §2.1.1
SSoT: depgraph MOD-POS-021
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 各策略目标 StrategyTarget 列表
#   fields: strategy_id + target_portfolio({symbol:weight}) + budget_used
#   code: pre_kelly_aggregate L214 / _sum_by_symbol L370
# - id: I2
#   name: T-1 持仓快照 position_snapshot
#   fields: {symbol: weight} 当前持仓权重（冲突净额截断必需）
#   code: aggregate L174-181
# - id: I3
#   name: 行业映射 + ADV 流动性数据
#   fields: industry_map(symbol→行业) + adv_data(symbol→adv_20d_p25)
#   code: post_kelly_clip L260-264
# - id: I4
#   name: Kelly 精裁决后权重 kelly_adjusted
#   fields: {symbol: weight}（MOD-POS-001 中间产物，f_i^norm）
#   code: post_kelly_clip L256-258
# 层: 算法
# - id: A1
#   name_zh: ① 按标的求和 自然叠加
#   name_en: _sum_by_symbol
#   intro: 各策略权重先归一到总资金口径再按 symbol 相加，同票仓位自然叠加
#   desc: account_weight = tp_weight × budget_used/total_budget（L396-402），CASH 不参与求和；同时记录 contributions {symbol:{strategy_id:贡献}} 归因（正=买负=卖）
#   inputs: I1
#   outputs: raw_summed + contributions
#   invariant: 自然叠加（S1给3%+S2给5%=8%）；O(N) 复杂度
# - id: A2
#   name_zh: ② 冲突标的净额处理
#   name_en: _resolve_conflicts
#   intro: 一策略买一策略卖同一票时按净额处理，净额为负截断防做空
#   desc: has_buy&has_sell 判冲突；net<0 → final=max(0, net+holdings_weight) 截断并记录 truncated_amount（L426-456）；非冲突直接用求和值
#   inputs: A1 I2
#   outputs: summed_weights + conflicts（PreKellyResult）
#   invariant: 冲突标的按净额处理；A股不能做空
# - id: A3
#   name_zh: ③ 单票硬上限裁剪 8%
#   name_en: _clip_single_name
#   intro: 单票超 8% 总资金一律削到 8%，按比例削不按策略优先级截断
#   desc: w>cap → cut_ratio=1-cap/w, w=cap（L473-484）；CASH 豁免裁剪
#   inputs: I4
#   outputs: 裁剪后权重 + cut_ratios
#   invariant: 按比例削保持各策略相对贡献不变
# - id: A4
#   name_zh: ④ 流动性裁剪 ADV 口径
#   name_en: _clip_liquidity
#   intro: 持仓金额占 ADV 超 20% 削到 20%，超 10% 削半，ADV 缺失取同行业中位数
#   desc: adv_pct=w×budget/adv_20d_p25；>0.20→w×0.20/adv_pct；>0.10→w×0.5（L518-553）；ADV≤0 降级取 sector_adv_median（L506-522）
#   inputs: A3 I3
#   outputs: 裁剪后权重
# - id: A5
#   name_zh: ⑤ 行业绝对上限裁剪 30%
#   name_en: _clip_sector
#   intro: 同行业权重加总超 30% 硬顶，行业内各票等比缩放到 30%
#   desc: 按 industry_map 归类求和 sector_weights；>cap → scale=cap/w，行业内每票 w×scale（L569-591）；偏离基准 ±10%/±15% 待 D-FACTOR 未实现
#   inputs: A4 I3
#   outputs: 裁剪后权重
# - id: A6
#   name_zh: ⑥ 总仓位裁剪 + 现金管理
#   name_en: _clip_total_exposure + 现金残差
#   intro: 总暴露超 regime_cap 等比缩放，剩余差额记为 CASH 现金
#   desc: sum>regime_cap → 全部 w×regime_cap/sum（L607-615）；cash_weight=total_budget−total_exposure（负值兜底 0）写入 CASH（L327-333）；再按 5 条件组装 degraded 降级标记（L346-353）
#   inputs: A5
#   outputs: firm_positions + constraint_checks + degraded
#   invariant: 级联每步只减不增单调收敛；总暴露 ≤ regime_cap
# 层: 输出
# - id: O1
#   name_zh: 组合级汇总目标 FirmTargetPortfolio
#   name_en: FirmTargetPortfolio
#   intro: 裁剪后的组合级粗仓位（含贡献归因/裁剪比例/约束检查/degraded），交 Kelly 精裁决下游
#   invariant: total_exposure ≤ regime_cap；cash_ratio = budget − exposure
#   downstream: MOD-POS-001 position_sizing_engine（消费 FirmTargetPortfolio）
# - id: O2
#   name_zh: Kelly 前聚合结果 PreKellyResult
#   name_en: PreKellyResult
#   intro: 求和+净额后的权重与冲突记录，作为 MOD-POS-001 Kelly 合成规则的 w_i^sum 输入
#   downstream: MOD-POS-001（Kelly 精裁决）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> O2
# I4 --> A3
# A3 --> A4
# I3 --> A4
# A4 --> A5
# I3 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

# ── 常量（参数来源：31_position_sizing §2.4）──
SINGLE_NAME_CAP = 0.08           # 单票硬上限 8%（总资金口径，§2.4）
SECTOR_DEVIATION_CAP = 0.10      # 单行业偏离基准 ±10%（§2.5.1）
SECTOR_DEVIATION_CAP_OVERLAY = 0.15  # 叠加态 ±15%（板块轮动 overlay 激活时）
SECTOR_ABSOLUTE_CAP = 0.30       # 单行业绝对上限 30%（§2.5.1）
CASH_SYMBOL = "CASH"             # 现金虚拟标的（§2.4 CASH 豁免裁剪）

# 流动性裁剪阈值（31号 §2.4.4 ADV 口径）
LIQUIDITY_SEVERE_PCT = 0.20      # 严重档：持仓 > 20% ADV → 削到 20% ADV
LIQUIDITY_MODERATE_PCT = 0.10    # 削半档：持仓 > 10% ADV → 削半

# tail_risk 四轴质量分档阈值（§6 CVaR 接口对齐，CVaR/VaR 比值启发式：
# 正态 95% 下 ES/VaR≈1.13；厚尾分布比值走高）
TAIL_QUALITY_NORMAL_MAX = 1.25   # ratio ≤ 1.25 → normal
TAIL_QUALITY_ELEVATED_MAX = 1.50  # ratio ≤ 1.50 → elevated；> 1.50 → heavy_tail


def build_tail_risk_check(
    var_95: float | None,
    cvar_95: float | None,
    var_source: str = "var_calculator",
) -> dict[str, Any]:
    """CVaR 接口对齐函数（§2.10.1 / §6 待对齐行）：var_calculator 输出 → constraint_checks.tail_risk 四轴结构。

    四轴（§6 裁定字段结构）：var_95 / cvar_95 / cvar_var_ratio / tail_quality。
    调用时机：post_kelly_clip 后由调用方用 var_calculator（MOD-RK-05，production）
    对最终组合做验证性计算，产出经本函数对齐后传入 post_kelly_clip(tail_risk=...)
    ——G13 只记录不重复计算（非裁剪主算法）；与 30号 §2.5 drawdown_controller
    5 级响应的关系：drawdown_controller 消费同源 CVaR 做分级响应，本结构仅留痕。

    Args:
        var_95: 组合 95% VaR（占组合价值比例口径，如 VaRResult.value_pct），None=未计算
        cvar_95: 组合 95% CVaR/ES（同口径），None=未计算
        var_source: 计算来源标记（默认 var_calculator；降级源如实标记）

    Returns:
        tail_risk dict：
          var_95 / cvar_95（比例口径原值透传，None 保留 None）
          cvar_var_ratio（var>0 且两者齐备时 = cvar/var，否则 None）
          tail_quality（normal/elevated/heavy_tail/unavailable 四档）
          var_source（来源留痕）
    """
    if var_95 is None or cvar_95 is None:
        return {
            "var_95": var_95,
            "cvar_95": cvar_95,
            "cvar_var_ratio": None,
            "tail_quality": "unavailable",
            "var_source": var_source,
        }

    ratio = cvar_95 / var_95 if var_95 > 0 else None
    if ratio is None:
        # var=0（零波动/空仓）且 cvar≥0：无尾部信息，记 normal
        quality = "normal"
    elif ratio <= TAIL_QUALITY_NORMAL_MAX:
        quality = "normal"
    elif ratio <= TAIL_QUALITY_ELEVATED_MAX:
        quality = "elevated"
    else:
        quality = "heavy_tail"

    return {
        "var_95": var_95,
        "cvar_95": cvar_95,
        "cvar_var_ratio": ratio,
        "tail_quality": quality,
        "var_source": var_source,
    }


@dataclass(frozen=True)
class FirmTarget:
    """单标的汇总后目标（含各策略贡献明细）。"""

    target_weight: float                 # 裁剪后最终权重
    contributions: dict[str, float]      # {strategy_id: 贡献权重}（归因用）
    cut_ratio: float                     # 被裁剪比例（0=未裁剪，0.2=削了20%）


@dataclass(frozen=True)
class ConflictRecord:
    """冲突标的净额处理记录（一策略买一策略卖）。"""

    symbol: str
    buy_strategies: dict[str, float]     # {strategy_id: 买方权重}
    sell_strategies: dict[str, float]    # {strategy_id: 卖方权重}
    net_weight: float                    # 净额


@dataclass(frozen=True)
class FirmTargetPortfolio:
    """组合级汇总目标（CTR-POS-021）。

    所有策略汇总 + 裁剪后的组合级粗仓位，仍未经 Kelly，交由 MOD-POS-001 精裁决。
    """

    firm_positions: dict[str, FirmTarget]
    total_exposure: float                # 所有标的 target_weight 之和
    total_budget: float                  # 所有策略 budget 之和
    cash_ratio: float                    # = total_budget − total_exposure
    constraint_checks: dict[str, Any]    # 单票/行业/总仓位检查结果（含是否触发裁剪）
    conflicts_resolved: list[ConflictRecord] = field(default_factory=list)
    degraded: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    idempotency_key: str = ""
    schema_version: str = "1.0"


@dataclass(frozen=True)
class PreKellyResult:
    """pre_kelly_aggregate 输出：求和+冲突净额后的权重 + 冲突记录 + 策略贡献归因。

    交 MOD-POS-001 做 Kelly 精裁决（31号 §2.3.4 合成规则消费 summed_weights[symbol] 作为 w_i^sum）。
    """

    summed_weights: dict[str, float]          # symbol → 归一后权重（budget 口径，含净额截断）
    conflicts: list[dict[str, Any]]           # ConflictRecord 列表（§2.3 冲突标的净额处理记录）
    total_exposure_pre_kelly: float           # 求和后总暴露（sum of summed_weights，供 Kelly 层 pro-rata 参考）
    contributions: dict[str, dict[str, float]]  # symbol → {strategy_id: 贡献权重}（§2.2 归因用，须透传给 post_kelly_clip）


class FirmRiskAggregator:
    """Firm 层风险聚合器（MOD-POS-021）。

    两段接口（32号 §2.1.1 v1.0.19）：
        1. pre_kelly_aggregate(): 求和(§2.2) + 冲突净额(§2.3) → PreKellyResult
        2. [MOD-POS-001 Kelly 精裁决在中间调用]
        3. post_kelly_clip(): 单票裁剪(§2.4) + 流动性裁剪(§2.4.4) + 行业裁剪(§2.5.1) + 总仓位裁剪(§2.5.2) + 现金管理 → FirmTargetPortfolio

    使用方式（两段分别调用，Kelly 在中间由 MOD-POS-001 执行）：
        aggregator = FirmRiskAggregator()
        pre = aggregator.pre_kelly_aggregate(targets, holdings, total_budget, industry_map)
        kelly_adjusted = kelly_fn(pre.summed_weights)  # MOD-POS-001 Kelly
        firm_target = aggregator.post_kelly_clip(kelly_adjusted, total_budget, industry_map, regime_cap,
                                                   contributions=pre.contributions, conflicts=pre.conflicts)

    便捷入口（aggregate）内部做 identity Kelly passthrough，适合测试/无 Kelly 场景：
        firm_target = aggregator.aggregate(targets, total_budget=1.0, industry_map={...})
    """

    def __init__(self, risk_limits: dict[str, Any] | None = None) -> None:
        """初始化。

        Args:
            risk_limits: 硬上限配置（single_name_cap / sector_cap / total_exposure_cap）。
        """
        self.risk_limits = risk_limits or {
            "single_name_cap": SINGLE_NAME_CAP,
            "sector_cap": SECTOR_ABSOLUTE_CAP,
            "total_exposure_cap": 0.95,
        }

    # ══ 公共接口 ══════════════════════════════════════════════════════

    def aggregate(
        self,
        target_portfolios: list[Any],
        position_snapshot: dict[str, Any] | None = None,
        total_budget: float = 1.0,
        industry_map: dict[str, str] | None = None,
        regime_cap: float = 0.95,
        kelly_fn: Callable[[dict[str, float]], dict[str, float]] | None = None,
        adv_data: dict[str, dict[str, float]] | None = None,
        kelly_param_source: str = "density_pdf",
        sector_benchmark_weights: dict[str, float] | None = None,
        sector_overlay_active: bool = False,
    ) -> FirmTargetPortfolio:
        """便捷入口：pre_kelly_aggregate → Kelly → post_kelly_clip → FirmTargetPortfolio。

        步骤（30_multi_strategy_concurrency §2.2 + blueprint §3）：
            1. pre_kelly_aggregate: 按标的求和（自然叠加）+ 冲突净额处理
            2. Kelly 精裁决（若 kelly_fn 为 None，identity passthrough）
            3. post_kelly_clip: 单票/流动性/行业/总仓位硬裁剪 + 现金管理

        Args:
            target_portfolios: 各 StrategyBook 产出的 StrategyTarget 列表
                （每个含 strategy_id / target_portfolio / budget_used）
            position_snapshot: T-1 持仓快照 {symbol: weight}，净额截断必需
                （口径：T+1 可卖权重，昨仓−今日已卖——见 t1_sellable 模块）
            total_budget: 所有策略 budget 之和
            industry_map: symbol → 申万/中信行业映射
            regime_cap: G15 RegimeMetaAllocator 总仓位上限
            kelly_fn: Kelly 精裁决函数（None=identity passthrough，测试/无 Kelly 场景）
            adv_data: symbol → {adv_20d_p25: float}，流动性裁剪用
            kelly_param_source: Kelly 参数来源（density_pdf 正常 / historical_fallback 降级）
            sector_benchmark_weights: 行业基准权重（§2.5.1 偏离裁剪，None=退化只做绝对 30%）
            sector_overlay_active: 板块轮动叠加态开关（偏离档 ±15% vs ±10%）

        Returns:
            FirmTargetPortfolio
        """
        current_holdings: dict[str, float] = {}
        if position_snapshot:
            # position_snapshot 可能是 {symbol: weight} 或 {symbol: {weight: float, ...}}
            for sym, val in position_snapshot.items():
                if isinstance(val, dict):
                    current_holdings[sym] = val.get("weight", 0.0)
                else:
                    current_holdings[sym] = float(val)

        industry_map = industry_map or {}

        # Step 1: pre_kelly_aggregate
        pre = self.pre_kelly_aggregate(
            targets=target_portfolios,
            current_holdings=current_holdings,
            total_budget=total_budget,
            industry_map=industry_map,
        )

        # Step 2: Kelly 精裁决（MOD-POS-001 职责，此处 passthrough 或外部传入）
        if kelly_fn is not None:
            kelly_adjusted = kelly_fn(pre.summed_weights)
        else:
            kelly_adjusted = dict(pre.summed_weights)  # identity passthrough

        # Step 3: post_kelly_clip
        result_dict = self.post_kelly_clip(
            kelly_adjusted=kelly_adjusted,
            total_budget=total_budget,
            industry_map=industry_map,
            regime_cap=regime_cap,
            sector_overlay_active=sector_overlay_active,
            contributions=pre.contributions,
            adv_data=adv_data,
            conflicts=pre.conflicts,
            kelly_param_source=kelly_param_source,
            sector_benchmark_weights=sector_benchmark_weights,
        )

        # 转换 dict → FirmTargetPortfolio dataclass
        return self._dict_to_firm_target_portfolio(result_dict)

    def pre_kelly_aggregate(
        self,
        targets: list[Any],
        current_holdings: dict[str, float],
        total_budget: float,
        industry_map: dict[str, str],
    ) -> PreKellyResult:
        """第一段：按标的求和（自然叠加，§2.2）+ 冲突标的净额处理（§2.3）。

        职责：
          - §2.2 各策略 target_portfolio 按 budget 口径归一后按 symbol 求和
          - §2.3 冲突标的（一买一卖）按净额处理，净额<0 截断为 max(0, net+holdings)

        不做：Kelly / 单票裁剪 / 行业裁剪 / 总仓位裁剪 / 现金管理

        Args:
            targets: 各 StrategyBook 产出的 StrategyTarget 列表
                （每个含 strategy_id / target_portfolio / budget_used）
            current_holdings: symbol → 当前持仓权重（T-1 收盘快照，净额截断必需）
            total_budget: 所有策略 budget_used 之和
            industry_map: symbol → 申万/中信行业映射（pre_kelly 只传递，不消费）

        Returns:
            PreKellyResult（summed_weights + conflicts + total_exposure_pre_kelly + contributions）
        """
        # ── Step 1: budget 口径归一化求和（§2.2 自然叠加）──
        raw_summed, contributions = self._sum_by_symbol(targets, total_budget)

        # ── Step 2: 冲突标的净额处理（§2.3）──
        summed_weights, conflicts = self._resolve_conflicts(
            raw_summed, contributions, current_holdings
        )

        total_exposure_pre_kelly = sum(summed_weights.values())

        return PreKellyResult(
            summed_weights=summed_weights,
            conflicts=conflicts,
            total_exposure_pre_kelly=total_exposure_pre_kelly,
            contributions=contributions,
        )

    def post_kelly_clip(
        self,
        kelly_adjusted: dict[str, float],
        total_budget: float,
        industry_map: dict[str, str],
        regime_cap: float,
        sector_overlay_active: bool = False,
        contributions: dict[str, dict[str, float]] | None = None,
        adv_data: dict[str, dict[str, float]] | None = None,
        conflicts: list[dict[str, Any]] | None = None,
        kelly_param_source: str = "density_pdf",
        sector_benchmark_weights: dict[str, float] | None = None,
        tail_risk: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """第二段：硬上限裁剪（§2.4 单票 → §2.4.4 流动性 → §2.5.1 行业 → §2.5.2 总仓位）+ 现金管理。

        职责：
          - §2.4 单票裁剪（>8% 按比例削，CASH 豁免）
          - §2.4.4 流动性裁剪（ADV 口径，20% 严重档/10% 削半档）
          - §2.5.1 行业裁剪（偏离基准 ±10%/±15% + 绝对 30% 兜底）
          - §2.5.2 总仓位裁剪（>regime_cap 等比缩放）
          - 现金管理（CASH = total_budget - sum(裁剪后股票权重)）

        级联关系（§2.5.2）：每步输入=上步输出，每步只减不增，单调收敛。

        Args:
            kelly_adjusted: MOD-POS-001 Kelly 精裁决后输出（f_i^norm）
            total_budget: 所有策略 budget 之和
            industry_map: symbol → 申万/中信行业映射
            regime_cap: G15 RegimeMetaAllocator 输出的总仓位上限
            sector_overlay_active: 板块轮动叠加态开关（§2.5.1：True → 偏离档放宽 ±15%，False → ±10%）
            contributions: 各 symbol 的策略贡献（归因用），从 PreKellyResult 传入
            adv_data: symbol → {adv_20d_p25: float}，流动性裁剪用
            conflicts: pre_kelly_aggregate 产出的冲突记录（degraded 条件1 判定必需）
            kelly_param_source: Kelly 参数来源（degraded 条件5 判定）
            sector_benchmark_weights: 行业基准权重 {sector: weight}（§2.5.1 偏离裁剪注入式参数）。
                None=基准未就绪（D-FACTOR 行业分类模块待确认，§6）→ 退化路径：
                跳过偏离裁剪只做绝对 30%，constraint_checks 记录 benchmark_missing
            tail_risk: CVaR 尾部风险记录（§2.10.1/§6 接口对齐，build_tail_risk_check 产出）。
                非 None → 写入 constraint_checks["tail_risk"]（G13 只记录不重复计算，
                调用时机=post_kelly_clip 后由调用方用 var_calculator 验证产出，非裁剪主算法）

        Returns:
            dict[str, Any]——FirmTargetPortfolio 字典表示（含 firm_positions /
            constraint_checks / degraded / conflicts_resolved）
        """
        # ── 初始化 ──
        clipped: dict[str, float] = {}
        cut_ratios: dict[str, float] = {}
        constraint_checks: dict[str, Any] = {
            "single_name": {"triggered": False, "cuts": []},
            "sector": {"triggered": False, "cuts": []},
            "total_exposure": {"triggered": False, "scale": 1.0},
            "liquidity_cap": {"triggered": False, "cuts": []},
        }

        for symbol, weight in kelly_adjusted.items():
            if symbol == CASH_SYMBOL:
                continue  # CASH 豁免裁剪（§2.4），权重在 Step 4 残差计算
            clipped[symbol] = weight
            cut_ratios[symbol] = 0.0

        # ══ Step 1: 单票硬上限裁剪（§2.4 按比例削）══
        self._clip_single_name(clipped, cut_ratios, constraint_checks)

        # ══ Step 1b: 流动性硬上限裁剪（§2.4.4 ADV 口径）══
        self._clip_liquidity(
            clipped, cut_ratios, constraint_checks, adv_data, industry_map, total_budget
        )

        # ══ Step 2: 行业硬约束裁剪（§2.5.1 偏离 + 绝对上限）══
        self._clip_sector(
            clipped, cut_ratios, constraint_checks, industry_map,
            sector_benchmark_weights=sector_benchmark_weights,
            sector_overlay_active=sector_overlay_active,
        )

        # ══ Step 3: 总仓位硬约束裁剪（§2.5.2 等比缩放）══
        total_exposure = self._clip_total_exposure(
            clipped, cut_ratios, constraint_checks, regime_cap
        )

        # ══ Step 4: 现金管理（CASH 残差计算，§2.5）══
        cash_weight = total_budget - total_exposure
        if cash_weight < 0:
            # 理论上 Step 3 总仓位裁剪后 total_exposure ≤ regime_cap ≤ total_budget
            # 但浮点精度或 lot 对齐偏差可能导致微小负值，兜底为 0
            cash_weight = 0.0

        clipped[CASH_SYMBOL] = cash_weight

        # ══ Step 5: CVaR 尾部风险记录（§2.10.1/§6 接口对齐，只记录不重复计算）══
        if tail_risk is not None:
            constraint_checks["tail_risk"] = tail_risk

        # ══ 组装 FirmTargetPortfolio（§2.7 数据结构）══
        firm_positions: dict[str, dict[str, Any]] = {}
        for symbol, weight in clipped.items():
            firm_positions[symbol] = {
                "target_weight": weight,
                "contributions": contributions.get(symbol, {}) if contributions else {},
                "cut_ratio": cut_ratios.get(symbol, 0.0),
            }

        # ── degraded 降级标记（§2.1 触发条件 5 条）──
        conflicts_resolved = conflicts or []
        degraded = (
            any(c.get("truncated", False) for c in conflicts_resolved)      # 条件1: 冲突净额截断
            or constraint_checks["single_name"]["triggered"]                # 条件2: 单票裁剪触发
            or constraint_checks["sector"]["triggered"]                     # 条件3: 行业裁剪触发
            or constraint_checks["total_exposure"]["triggered"]            # 条件4: 总仓位裁剪触发
            or constraint_checks["liquidity_cap"]["triggered"]             # 条件4b: 流动性裁剪触发
            or kelly_param_source == "historical_fallback"                 # 条件5: Kelly 参数降级传导
        )

        return {
            "firm_positions": firm_positions,
            "total_exposure": total_exposure,
            "total_budget": total_budget,
            "cash_ratio": cash_weight,
            "constraint_checks": constraint_checks,
            "conflicts_resolved": conflicts_resolved,
            "degraded": degraded,
            "created_at": datetime.now(),
            "idempotency_key": f"firm_agg_{int(datetime.now().timestamp())}",
            "schema_version": "1.0",
        }

    # ══ 内部辅助方法 ═══════════════════════════════════════════════════

    def _sum_by_symbol(
        self, targets: list[Any], total_budget: float
    ) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
        """按标的求和（自然叠加，§2.2），返回 (raw_summed, contributions)。

        各策略 target_portfolio 权重是相对各自 strategy_budget 的占比。
        求和前先归一到账户总资金口径：account_weight = tp_weight × budget_used / total_budget

        Returns:
            raw_summed: symbol → 求和后权重（未处理冲突）
            contributions: symbol → {strategy_id: 贡献权重}（归因用，正=买，负=卖）
        """
        raw_summed: dict[str, float] = {}
        contributions: dict[str, dict[str, float]] = {}

        for tp in targets:
            # 兼容三种格式：TargetPortfolio 对象 / dict(positions/budget) / dict(target_portfolio/budget_used)
            if isinstance(tp, dict):
                strategy_id = tp.get("strategy_id", "unknown")
                # 支持两种 dict 键名：positions/budget（TargetPortfolio 风格）或 target_portfolio/budget_used（旧风格）
                if "positions" in tp:
                    budget_used = tp.get("budget", 0.0)
                    tp_portfolio_raw = tp.get("positions", {})
                    # positions 值可能是 TargetWeight 对象或裸 float
                    tp_portfolio = {}
                    for sym, val in tp_portfolio_raw.items():
                        if hasattr(val, "target_weight"):
                            tp_portfolio[sym] = val.target_weight
                        elif isinstance(val, (int, float)):
                            tp_portfolio[sym] = float(val)
                        else:
                            tp_portfolio[sym] = 0.0
                else:
                    budget_used = tp.get("budget_used", 0.0)
                    tp_portfolio = tp.get("target_portfolio", {})
            else:
                strategy_id = getattr(tp, "strategy_id", "unknown")
                # TargetPortfolio 对象：positions/budget 字段
                if hasattr(tp, "positions"):
                    budget_used = getattr(tp, "budget", 0.0)
                    tp_portfolio_raw = getattr(tp, "positions", {})
                    # positions 值是 TargetWeight 对象，取 .target_weight
                    tp_portfolio = {}
                    for sym, val in tp_portfolio_raw.items():
                        if hasattr(val, "target_weight"):
                            tp_portfolio[sym] = val.target_weight
                        elif isinstance(val, (int, float)):
                            tp_portfolio[sym] = float(val)
                        else:
                            tp_portfolio[sym] = 0.0
                else:
                    budget_used = getattr(tp, "budget_used", 0.0)
                    tp_portfolio = getattr(tp, "target_portfolio", {})

            scale = budget_used / total_budget if total_budget > 0 else 0.0

            for symbol, tp_weight in tp_portfolio.items():
                if symbol == CASH_SYMBOL:
                    continue  # CASH 不参与求和（§2.4 CASH 豁免）
                account_weight = tp_weight * scale
                raw_summed[symbol] = raw_summed.get(symbol, 0.0) + account_weight
                if symbol not in contributions:
                    contributions[symbol] = {}
                # 记录策略贡献方向（正=买，负=卖）
                contributions[symbol][strategy_id] = (
                    contributions[symbol].get(strategy_id, 0.0) + account_weight
                )

        return raw_summed, contributions

    def _resolve_conflicts(
        self,
        raw_summed: dict[str, float],
        contributions: dict[str, dict[str, float]],
        current_holdings: dict[str, float],
    ) -> tuple[dict[str, float], list[dict[str, Any]]]:
        """冲突标的净额处理（§2.3），返回 (summed_weights, conflicts)。

        冲突 = 一策略买（正权重）另一策略卖（负权重）同一标的。
        净额 < 0 时 A 股不能做空 → 截断为 max(0, net + holdings_weight)。
        """
        conflicts: list[dict[str, Any]] = []
        summed_weights: dict[str, float] = {}

        for symbol, net_weight in raw_summed.items():
            strategy_contribs = contributions[symbol]
            has_buy = any(w > 0 for w in strategy_contribs.values())
            has_sell = any(w < 0 for w in strategy_contribs.values())

            if has_buy and has_sell:
                # 冲突标的（§2.3）：一买一卖
                conflict_record: dict[str, Any] = {
                    "symbol": symbol,
                    "buy_strategies": {k: v for k, v in strategy_contribs.items() if v > 0},
                    "sell_strategies": {k: v for k, v in strategy_contribs.items() if v < 0},
                    "net_weight": net_weight,
                }

                if net_weight < 0:
                    # 净额<0：A 股不能做空，截断为 max(0, net + holdings)（§2.3 净额截断）
                    holdings_weight = current_holdings.get(symbol, 0.0)
                    final_weight = max(0.0, net_weight + holdings_weight)
                    conflict_record["truncated"] = True
                    conflict_record["final_weight"] = final_weight
                    conflict_record["truncated_amount"] = (
                        net_weight + holdings_weight - final_weight
                    )
                    conflicts.append(conflict_record)
                    summed_weights[symbol] = final_weight
                else:
                    # 净额≥0：无截断需求
                    conflict_record["truncated"] = False
                    conflict_record["final_weight"] = net_weight
                    conflicts.append(conflict_record)
                    summed_weights[symbol] = net_weight
            else:
                # 非冲突（同向叠加或单策略），直接使用求和值
                summed_weights[symbol] = net_weight

        return summed_weights, conflicts

    def _clip_single_name(
        self,
        clipped: dict[str, float],
        cut_ratios: dict[str, float],
        constraint_checks: dict[str, Any],
    ) -> None:
        """单票硬上限裁剪（§2.4 按比例削，>8% 削到 8%）。

        INVARIANTS：非按策略优先级截断，按比例削保持各策略相对贡献不变。
        """
        cap = self.risk_limits.get("single_name_cap", SINGLE_NAME_CAP)
        for symbol in list(clipped.keys()):
            if clipped[symbol] > cap:
                cut_ratio = 1.0 - cap / clipped[symbol]
                clipped[symbol] = cap
                cut_ratios[symbol] = cut_ratio
                constraint_checks["single_name"]["triggered"] = True
                constraint_checks["single_name"]["cuts"].append({
                    "symbol": symbol,
                    "cut_ratio": cut_ratio,
                    "capped_at": cap,
                })

    def _clip_liquidity(
        self,
        clipped: dict[str, float],
        cut_ratios: dict[str, float],
        constraint_checks: dict[str, Any],
        adv_data: dict[str, dict[str, float]] | None,
        industry_map: dict[str, str],
        total_budget: float,
    ) -> None:
        """流动性硬上限裁剪（§2.4.4 ADV 口径）。

        阈值（31号 §2.4.4）：
          - 严重档：持仓 > 20% ADV → 削到 20% ADV
          - 削半档：持仓 > 10% ADV → 削半
        ADV 缺失/停牌 → 降级取同行业中位数。
        """
        if not adv_data:
            return  # 无 ADV 数据时跳过流动性裁剪（降级为不触发）

        # 预计算行业 ADV 中位数（降级路径用）
        sector_advs: dict[str, list[float]] = {}
        for sym, adv_info in adv_data.items():
            sec = industry_map.get(sym, "UNKNOWN")
            adv_val = adv_info.get("adv_20d_p25", 0)
            if adv_val > 0:
                sector_advs.setdefault(sec, []).append(adv_val)
        sector_adv_median = {
            sec: sorted(vals)[len(vals) // 2]
            for sec, vals in sector_advs.items()
            if vals
        }

        for symbol in list(clipped.keys()):
            adv_i = adv_data.get(symbol, {}).get("adv_20d_p25", 0)
            if adv_i <= 0:
                # ADV 缺失/停牌 → 降级取同行业中位数（31号 §2.4.4 降级路径）
                adv_i = sector_adv_median.get(industry_map.get(symbol, "UNKNOWN"), 0)
            if adv_i <= 0:
                continue  # 仍无 ADV 数据，跳过

            position_value = clipped[symbol] * total_budget
            adv_pct = position_value / adv_i

            if adv_pct > LIQUIDITY_SEVERE_PCT:
                # 严重档：削到 20% ADV
                old = clipped[symbol]
                clipped[symbol] = old * (LIQUIDITY_SEVERE_PCT / adv_pct)
                cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios.get(symbol, 0)) * (
                    LIQUIDITY_SEVERE_PCT / adv_pct
                )
                constraint_checks["liquidity_cap"]["triggered"] = True
                constraint_checks["liquidity_cap"]["cuts"].append({
                    "symbol": symbol,
                    "tier": "severe",
                    "adv_pct": adv_pct,
                    "capped_at_adv": LIQUIDITY_SEVERE_PCT,
                })
            elif adv_pct > LIQUIDITY_MODERATE_PCT:
                # 削半档
                clipped[symbol] *= 0.5
                cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios.get(symbol, 0)) * 0.5
                constraint_checks["liquidity_cap"]["triggered"] = True
                constraint_checks["liquidity_cap"]["cuts"].append({
                    "symbol": symbol,
                    "tier": "moderate",
                    "adv_pct": adv_pct,
                    "halved": True,
                })

    def _clip_sector(
        self,
        clipped: dict[str, float],
        cut_ratios: dict[str, float],
        constraint_checks: dict[str, Any],
        industry_map: dict[str, str],
        sector_benchmark_weights: dict[str, float] | None = None,
        sector_overlay_active: bool = False,
    ) -> None:
        """行业硬约束裁剪（§2.5.1：偏离基准 ±10%/±15% + 绝对上限 30% 兜底）。

        偏离裁剪（注入式参数 + 退化路径）：
          - sector_benchmark_weights 提供行业基准权重（D-FACTOR 行业分类模块产出，§6）时启用：
            sector_weight > benchmark + dev_cap → 行业内等比削到 benchmark + dev_cap；
            dev_cap = ±10%（常态）/ ±15%（sector_overlay_active=True 板块轮动叠加态）。
            只削超配上限（long-only 组合低配偏离不强制买入）。
            基准中缺失的行业（含 UNKNOWN）跳过偏离裁剪（无法评估，非阻断）。
          - 基准 None（D-FACTOR 未就绪）→ 退化路径：跳过偏离裁剪只做绝对 30%，
            constraint_checks["sector"]["deviation"] 记录 benchmark_missing。
        绝对上限 30% 始终生效（不可突破硬顶，偏离裁剪后再校验兜底）。
        """
        cap = self.risk_limits.get("sector_cap", SECTOR_ABSOLUTE_CAP)

        # 2a. 行业归类求和
        sector_weights: dict[str, float] = {}
        sector_symbols: dict[str, list[str]] = {}
        for symbol, weight in clipped.items():
            sector = industry_map.get(symbol, "UNKNOWN")
            sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
            sector_symbols.setdefault(sector, []).append(symbol)

        # 2b. 偏离基准 ±10%/±15% 裁剪（基准注入时启用，§2.5.1）
        dev_cap = SECTOR_DEVIATION_CAP_OVERLAY if sector_overlay_active else SECTOR_DEVIATION_CAP
        constraint_checks["sector"]["deviation"] = {
            "enabled": sector_benchmark_weights is not None,
            "overlay_active": sector_overlay_active,
            "dev_cap": dev_cap,
        }
        if sector_benchmark_weights is not None:
            for sector, weight in sector_weights.items():
                benchmark = sector_benchmark_weights.get(sector)
                if benchmark is None:
                    continue  # 该行业无基准（含 UNKNOWN）→ 跳过偏离裁剪（退化不阻断）
                limit = benchmark + dev_cap
                if weight > limit and weight > 0:
                    scale = limit / weight
                    for symbol in sector_symbols[sector]:
                        clipped[symbol] = clipped[symbol] * scale
                        cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios.get(symbol, 0)) * scale
                    sector_weights[sector] = limit
                    constraint_checks["sector"]["triggered"] = True
                    constraint_checks["sector"]["cuts"].append({
                        "sector": sector,
                        "type": "deviation_cap",
                        "scale": scale,
                        "benchmark": benchmark,
                        "dev_cap": dev_cap,
                        "capped_at": limit,
                    })
        else:
            # 退化路径：D-FACTOR 行业基准权重未就绪（§6），只做绝对 30%
            constraint_checks["sector"]["deviation"]["benchmark_missing"] = True

        # 2c. 绝对上限 30% 裁剪（不可突破硬顶，偏离裁剪后兜底）
        for sector, weight in sector_weights.items():
            if weight > cap:
                scale = cap / weight
                for symbol in sector_symbols[sector]:
                    clipped[symbol] = clipped[symbol] * scale
                    cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios.get(symbol, 0)) * scale
                sector_weights[sector] = cap
                constraint_checks["sector"]["triggered"] = True
                constraint_checks["sector"]["cuts"].append({
                    "sector": sector,
                    "type": "absolute_cap",
                    "scale": scale,
                    "capped_at": cap,
                })

    def _clip_total_exposure(
        self,
        clipped: dict[str, float],
        cut_ratios: dict[str, float],
        constraint_checks: dict[str, Any],
        regime_cap: float,
    ) -> float:
        """总仓位硬约束裁剪（§2.5.2 等比缩放）。

        若 Kelly 层 §2.3.5 已做 pro-rata 归一化（sum ≤ regime_cap），此步自动不触发。

        Returns:
            total_exposure: 裁剪后总暴露
        """
        total_exposure = sum(clipped.values())
        if total_exposure > regime_cap:
            scale = regime_cap / total_exposure
            for symbol in clipped:
                clipped[symbol] *= scale
                cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios.get(symbol, 0)) * scale
            constraint_checks["total_exposure"]["triggered"] = True
            constraint_checks["total_exposure"]["scale"] = scale
            total_exposure = regime_cap
        return total_exposure

    def _dict_to_firm_target_portfolio(
        self, result_dict: dict[str, Any]
    ) -> FirmTargetPortfolio:
        """将 post_kelly_clip 的 dict 输出转换为 FirmTargetPortfolio dataclass。"""
        firm_positions: dict[str, FirmTarget] = {}
        for symbol, pos_data in result_dict["firm_positions"].items():
            firm_positions[symbol] = FirmTarget(
                target_weight=pos_data["target_weight"],
                contributions=dict(pos_data.get("contributions", {})),
                cut_ratio=pos_data.get("cut_ratio", 0.0),
            )

        # conflicts_resolved 中 dict → ConflictRecord
        conflicts_resolved: list[ConflictRecord] = []
        for c in result_dict.get("conflicts_resolved", []):
            conflicts_resolved.append(ConflictRecord(
                symbol=c["symbol"],
                buy_strategies=dict(c.get("buy_strategies", {})),
                sell_strategies=dict(c.get("sell_strategies", {})),
                net_weight=c.get("net_weight", 0.0),
            ))

        return FirmTargetPortfolio(
            firm_positions=firm_positions,
            total_exposure=result_dict["total_exposure"],
            total_budget=result_dict["total_budget"],
            cash_ratio=result_dict["cash_ratio"],
            constraint_checks=result_dict["constraint_checks"],
            conflicts_resolved=conflicts_resolved,
            degraded=result_dict["degraded"],
            created_at=result_dict.get("created_at", datetime.now()),
            idempotency_key=result_dict.get("idempotency_key", ""),
            schema_version=result_dict.get("schema_version", "1.0"),
        )
