# [BLUEPRINT] MOD-RPT-036 | 待统筹登记（54号 BM-REC-02-B 绩效归因计算器，§3.2 施工算法落码）
# [MODULE] zephyr.reporting.attribution_calculator
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.contracts.performance_attribution_report(CTR-P1-009)
# [CONSUMERS] zephyr.reporting.attribution_result_store(落库); 归因报告生成链路(54号 BM-REC-02-B)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] BHB守恒（allocation+selection+interaction=R_p−R_b，beginning-of-period权重）; Carino恒等（Σlinked=几何超额收益G，residual浮点精度级<1e-6门禁）; T+1拆分恒等（realized+unrealized=selection总）; 纯函数零IO零DB; 非法输入fail-closed(ValueError)
# [MODIFY-GUARD] 54_reconciliation_attribution.md §3.2/§5.1（公式真源）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(输入非法/residual门禁FAIL strict拒发)
# [TESTS] tests/reporting/test_attribution_calculator.py
# [A_module] module_id=MOD-RPT-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_REPORTING — 绩效归因计算器（54 号 BM-REC-02-B，memo §3.2 施工算法落码）。

施工范围（BM-REC-02-B 残余阻塞之"归因计算实现缺失"）：
  1. calc_single_period_brinson——纯 BHB 三因子单期分解（beginning-of-period
     权重，守恒校验口径与 pf_core MOD-PF-007 生产实现相同）；
  2. carino_link_periods——Carino 对数多期链接（Cariño 1999，GIPS-compliant；
     v1.15.8 公式修正版 k_t=[ln(1+R_p,t)−ln(1+R_b,t)]/(R_p,t−R_b,t)，
     恒等 Σ linked == 几何超额收益 G，residual < 1e-6 质量门禁）；
  3. calc_brinson_with_t1_settlement——A 股 T+1 selection 拆分（realized 可兑现
     vs unrealized 浮盈，t1_warning >50% 浮盈依赖警示）；
  4. get_sector / set_sector_map——申万一级板块映射（降级 "未知板块"，映射表
     由调用方注入，本模块不连数据源）；
  5. build_linked_attribution_report——多期输入 → Carino 链接 → CTR-P1-009
     契约报告（residual 超门禁 strict 默认拒发，fail-closed）。

与既有实现的关系（不收敛、不动既有件）：
  - pf_core PerformanceAttributionEngine（MOD-PF-007，production）：BHB 已实现
    但多期为算术链接；双实现收敛属 54 号 §6 待裁定（Owner 窗口），本模块是
    memo §3.2 施工算法的公式真源落码，不修改 pf_core/reporting 桩任一方。
  - zephyr.reporting.attribution（策略 PnL 核算/求和不变量/Shapley）：正交，
    本模块不复读其实现；两层落库编排见 attribution_result_store。

浮点口径：全部 float（CTR-P1-009 契约为 float）；金额/PnL 精度敏感链路
（trading/pnl_calculator）用 Decimal 不属本模块职责。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Mapping, Sequence

from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)

__all__: Final = [
    "SW_UNKNOWN_SECTOR",
    "CARINO_RESIDUAL_TOLERANCE",
    "LinkedAttribution",
    "build_linked_attribution_report",
    "calc_brinson_with_t1_settlement",
    "calc_single_period_brinson",
    "carino_link_periods",
    "get_sector",
    "set_sector_map",
]

#: Carino residual 质量门禁（54 号 §3.2：|residual| < 1e-6 浮点精度级）
CARINO_RESIDUAL_TOLERANCE: Final[float] = 1e-6

#: 板块映射缺失降级值（54 号 §3.2 get_sector 降级口径）
SW_UNKNOWN_SECTOR: Final = "未知板块"

#: T+1 浮盈依赖警示阈值（54 号 §7 开放问题：>50% selection 来自浮盈时警示，
#: 待实盘回归校准——打板策略可能上调至 70%）
_T1_WARNING_RATIO: Final[float] = 0.5

# 申万一级映射缓存 {symbol: sector}——由调用方（akshare/tushare 预加载批次）
# 经 set_sector_map 注入；本模块不连数据源（54 号 §3.2 v1.13.0 施工算法）。
_SW_LEVEL1_MAP: dict[str, str] = {}


def set_sector_map(mapping: Mapping[str, str] | None) -> None:
    """注入/清空申万一级板块映射（None=清空，测试隔离用）。"""
    _SW_LEVEL1_MAP.clear()
    if mapping:
        _SW_LEVEL1_MAP.update(mapping)


def get_sector(symbol: str) -> str:
    """申万一级板块映射（symbol → 板块名；映射缺失降级 "未知板块"）。"""
    return _SW_LEVEL1_MAP.get(symbol, SW_UNKNOWN_SECTOR)


def _validate_weights(weights: Mapping[str, float], field: str) -> None:
    """权重 fail-closed 校验：负权重拒绝（beginning-of-period 权重语义）。"""
    for sector, w in weights.items():
        if w < 0:
            raise ValueError(f"{field} 含负权重（sector={sector!r}, w={w}）")


def calc_single_period_brinson(
    portfolio_weights: Mapping[str, float],
    benchmark_weights: Mapping[str, float],
    portfolio_returns: Mapping[str, float],
    benchmark_returns: Mapping[str, float],
    benchmark_total_return: float = 0.0,
) -> dict[str, float]:
    """单期 Brinson BHB 三因子分解（54 号 §3.2 v1.15.0 守恒修正口径）。

    纯 BHB（beginning-of-period 权重，T-1 收盘）：
        allocation_i  = (w_p,i - w_b,i) × r_b,i
        selection_i   = w_b,i × (r_p,i - r_b,i)
        interaction_i = (w_p,i - w_b,i) × (r_p,i - r_b,i)
    守恒：三式求和 = R_p − R_b（不满足即实现 bug）。
    （benchmark_total_return 保留用于报告展示与 BF 备选口径切换，BHB 不用。）

    Raises:
        ValueError: 板块并集为空或存在负权重（fail-closed）。
    """
    _validate_weights(portfolio_weights, "portfolio_weights")
    _validate_weights(benchmark_weights, "benchmark_weights")
    sectors = set(portfolio_weights) | set(benchmark_weights)
    if not sectors:
        raise ValueError("板块并集为空（两侧权重不可同时为空）")

    alloc = selec = interact = 0.0
    for s in sectors:
        wp = portfolio_weights.get(s, 0.0)
        wb = benchmark_weights.get(s, 0.0)
        rp = portfolio_returns.get(s, 0.0)
        rb = benchmark_returns.get(s, 0.0)
        alloc += (wp - wb) * rb
        selec += wb * (rp - rb)
        interact += (wp - wb) * (rp - rb)
    return {
        "allocation_effect": alloc,
        "selection_effect": selec,
        "interaction_effect": interact,
        "single_period_active_return": alloc + selec + interact,
    }


def carino_link_periods(
    period_effects: Sequence[Mapping[str, float]],
    portfolio_period_returns: Sequence[float],
    benchmark_period_returns: Sequence[float],
) -> dict[str, float | str]:
    """Carino 对数链接——多期单期 Brinson 效应链接为多期归因（54 号 §3.2）。

    v1.15.8 公式修正版（原版 k_t=ln(1+R_p,t)/R_p,t 零基准极限过不了门禁）：
      k_t = [ln(1+R_p,t) − ln(1+R_b,t)] / (R_p,t − R_b,t)   期修正因子
      A   = G / ln(1+G)，G = (1+R_p)/(1+R_b) − 1            总几何超额收益
      linked_i = A × Σ_t e_{i,t} × k_t
    恒等性质：Σ_i linked_i = G（residual 应处浮点精度级，非零即数据/单期 bug）。

    Returns:
        linked_allocation/selection/interaction_effect + geometric_active_return
        + carino_residual + residual_quality（PASS/FAIL，门禁 1e-6）。

    Raises:
        ValueError: 三期序列长度不齐或为空（fail-closed）。
    """
    if not period_effects:
        raise ValueError("period_effects 不能为空")
    if not (
        len(period_effects) == len(portfolio_period_returns) == len(benchmark_period_returns)
    ):
        raise ValueError(
            "三期序列长度不一致: "
            f"effects={len(period_effects)} portfolio={len(portfolio_period_returns)} "
            f"benchmark={len(benchmark_period_returns)}"
        )

    # 1. 累计几何收益 + 总几何超额收益 G
    cum_portfolio = 1.0
    cum_benchmark = 1.0
    for r_p, r_b in zip(portfolio_period_returns, benchmark_period_returns, strict=True):
        cum_portfolio *= 1.0 + r_p
        cum_benchmark *= 1.0 + r_b
    geometric_active_return = (cum_portfolio / cum_benchmark) - 1.0

    # 2. 全局缩放因子 A = G / ln(1+G)（G→0 退化时洛必达极限 A→1）
    log_active = math.log(1.0 + geometric_active_return) if (1.0 + geometric_active_return) > 0 else 0.0
    global_scale = (geometric_active_return / log_active) if abs(log_active) > 1e-12 else 1.0

    # 3. 各期 Carino 修正因子 k_t（R_p,t→R_b,t 退化时 k_t→1/(1+R_p,t)，洛必达极限）
    k_factors: list[float] = []
    for r_p, r_b in zip(portfolio_period_returns, benchmark_period_returns, strict=True):
        active_t = r_p - r_b
        if abs(active_t) < 1e-12:
            k_factors.append(1.0 / (1.0 + r_p))
        else:
            k_factors.append((math.log(1.0 + r_p) - math.log(1.0 + r_b)) / active_t)

    # 4. 链接各效应
    linked_alloc = linked_selec = linked_interact = 0.0
    for eff, k_t in zip(period_effects, k_factors, strict=True):
        linked_alloc += eff["allocation_effect"] * k_t * global_scale
        linked_selec += eff["selection_effect"] * k_t * global_scale
        linked_interact += eff["interaction_effect"] * k_t * global_scale

    # 5. residual 质量校验（恒等性质下应处浮点精度级；非零即数据/单期计算 bug）
    linked_sum = linked_alloc + linked_selec + linked_interact
    residual = geometric_active_return - linked_sum

    return {
        "linked_allocation_effect": linked_alloc,
        "linked_selection_effect": linked_selec,
        "linked_interaction_effect": linked_interact,
        "geometric_active_return": geometric_active_return,
        "carino_residual": residual,
        "residual_quality": "PASS" if abs(residual) < CARINO_RESIDUAL_TOLERANCE else "FAIL",
    }


def calc_brinson_with_t1_settlement(
    portfolio_weights: Mapping[str, float],
    benchmark_weights: Mapping[str, float],
    portfolio_returns: Mapping[str, float],
    benchmark_returns: Mapping[str, float],
    benchmark_total_return: float = 0.0,
    new_positions_today: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, float | bool]:
    """Brinson 三因子 + A 股 T+1 已实现/浮盈分离（54 号 §3.2 v1.15.0 口径）。

    将 selection effect 拆为：
      - realized_selection：T-1 前已建仓位（T 日可卖）的选股贡献，可兑现；
      - unrealized_selection：T 日新建仓位（T+1 才可卖）的选股贡献，仅为浮盈。
    拆分原理（收益贡献拆分口径）：板块组合收益 r_p,i = (1−λ_i)·r_old + λ_i·r_new，
    λ_i = 新建仓位占板块组合市值比例；unrealized_i = w_b,i × λ_i × (r_new − r_b,i)。

    Args:
        new_positions_today: T 日新建仓位 {symbol: {'weight': w, 'day_return': r}}；
            None 等价空（无新仓退化，unrealized=0）。day_return =
            (当日收盘 − 买入加权均价)/买入加权均价（来自当日 buy fills）。

    Returns:
        allocation/interaction（T+1 不影响）+ realized/unrealized/selection 总
        + t1_locked_weight + t1_warning（>50% selection 来自浮盈时 True）。
    """
    new_positions = new_positions_today or {}

    # 1. 标准 Brinson 三因子（纯 BHB）
    base = calc_single_period_brinson(
        portfolio_weights, benchmark_weights, portfolio_returns, benchmark_returns,
        benchmark_total_return,
    )

    # 2. 按板块聚合新建仓位的收益贡献（λ_i 与 r_p,i^new）
    sector_new_weight: dict[str, float] = {}
    sector_new_ret_num: dict[str, float] = {}
    for symbol, info in new_positions.items():
        sector = get_sector(symbol)
        w_new = info["weight"]
        r_new = info.get("day_return", 0.0)
        sector_new_weight[sector] = sector_new_weight.get(sector, 0.0) + w_new
        sector_new_ret_num[sector] = sector_new_ret_num.get(sector, 0.0) + w_new * r_new

    # 3. 拆分 selection：新建仓位浮盈贡献 vs 已有仓位已实现贡献
    unrealized_selection = 0.0
    for sector, new_w in sector_new_weight.items():
        sector_total_wp = portfolio_weights.get(sector, 0.0)
        wb = benchmark_weights.get(sector, 0.0)
        rb = benchmark_returns.get(sector, 0.0)
        if sector_total_wp > 1e-12 and new_w > 1e-12:
            lambda_i = new_w / sector_total_wp
            r_new_avg = sector_new_ret_num[sector] / new_w
            unrealized_selection += wb * lambda_i * (r_new_avg - rb)

    realized_selection = base["selection_effect"] - unrealized_selection
    total_selection = base["selection_effect"]

    return {
        "allocation_effect": base["allocation_effect"],
        "realized_selection_effect": realized_selection,
        "unrealized_selection_effect": unrealized_selection,
        "selection_effect_total": total_selection,
        "interaction_effect": base["interaction_effect"],
        "t1_locked_weight": sum(info["weight"] for info in new_positions.values()),
        "t1_warning": (
            unrealized_selection / total_selection > _T1_WARNING_RATIO
            if abs(total_selection) > 1e-12
            else False
        ),
    }


@dataclass(frozen=True)
class LinkedAttribution:
    """多期链接归因产物：CTR-P1-009 报告 + Carino 质量门禁元数据。"""

    report: PerformanceAttributionReport
    geometric_active_return: float
    carino_residual: float
    residual_quality: str  # PASS / FAIL（54 号 §3.2 质量门禁）


def build_linked_attribution_report(
    portfolio_id: str,
    period_start: str,
    period_end: str,
    idempotency_key: str,
    period_inputs: Sequence[Mapping[str, Mapping[str, float]]],
    transaction_cost_drag: float = 0.0,
    residual_tolerance: float = CARINO_RESIDUAL_TOLERANCE,
    strict: bool = True,
) -> LinkedAttribution:
    """多期归因全链计算：逐期单期 Brinson → Carino 链接 → CTR-P1-009 报告。

    total_return = 几何超额收益 − transaction_cost_drag（守恒口径对齐 pf_core
    attribute_full：total_return = excess_return − cost_drag）。
    factor_contributions 恒 {}（因子维度暂缓，54 号 §3.4/§4.2）。

    Args:
        period_inputs: 各子期输入序列，每项含 portfolio_weights / benchmark_weights /
            portfolio_returns / benchmark_returns 四键（beginning-of-period 权重）。
        residual_tolerance: Carino residual 门禁（默认 1e-6，54 号 §3.2）。
        strict: True=residual 超门禁抛 ValueError 拒发（54 号 §3.2"超阈值拒绝发布
            报告"硬门禁）；False=仅标记 residual_quality=FAIL（诊断/测试用）。

    Raises:
        ValueError: period_inputs 为空 / transaction_cost_drag < 0 / strict 且
            residual 超门禁（fail-closed）。
    """
    if not period_inputs:
        raise ValueError("period_inputs 不能为空")
    if transaction_cost_drag < 0:
        raise ValueError(f"transaction_cost_drag 必须 ≥ 0: {transaction_cost_drag}")

    # 1. 逐期单期 Brinson + 各期组合/基准总收益（R=Σw×r 权重收益同口径）
    period_effects: list[dict[str, float]] = []
    p_rets: list[float] = []
    b_rets: list[float] = []
    for period in period_inputs:
        pw = period["portfolio_weights"]
        bw = period["benchmark_weights"]
        pr = period["portfolio_returns"]
        br = period["benchmark_returns"]
        period_effects.append(calc_single_period_brinson(pw, bw, pr, br))
        sectors = set(pw) | set(bw)
        p_rets.append(sum(pw.get(s, 0.0) * pr.get(s, 0.0) for s in sectors))
        b_rets.append(sum(bw.get(s, 0.0) * br.get(s, 0.0) for s in sectors))

    # 2. Carino 多期链接 + residual 质量门禁
    linked = carino_link_periods(period_effects, p_rets, b_rets)
    residual = float(linked["carino_residual"])
    quality = "PASS" if abs(residual) < residual_tolerance else "FAIL"
    if strict and quality != "PASS":
        raise ValueError(
            f"Carino residual 超门禁拒发: residual={residual} tolerance={residual_tolerance}"
        )

    # 3. 产出 CTR-P1-009 契约报告
    geometric_active = float(linked["geometric_active_return"])
    report = PerformanceAttributionReport(
        portfolio_id=portfolio_id,
        period_start=period_start,
        period_end=period_end,
        total_return=geometric_active - transaction_cost_drag,
        allocation_effect=float(linked["linked_allocation_effect"]),
        selection_effect=float(linked["linked_selection_effect"]),
        interaction_effect=float(linked["linked_interaction_effect"]),
        transaction_cost_drag=transaction_cost_drag,
        factor_contributions={},
        idempotency_key=idempotency_key,
    )
    return LinkedAttribution(
        report=report,
        geometric_active_return=geometric_active,
        carino_residual=residual,
        residual_quality=quality,
    )
