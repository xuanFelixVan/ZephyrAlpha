---
ttl: permanent
doc_type: architecture_view
title: FirmRiskAggregator 逻辑（组合层风险聚合）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.21"
date: 2026-08-12
topic: firm_risk_aggregator
scope: 07_trading_decision_architecture
---

# FirmRiskAggregator 逻辑（组合层风险聚合）

> 本备忘把 [30_multi_strategy_concurrency §2.2/§2.3](30_multi_strategy_concurrency.md) 已定稿的"FirmRiskAggregator"框架落地为可施工的执行逻辑与接口契约。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 边界：本备忘只定 FirmRiskAggregator 的**求和/裁剪/冲突处理执行逻辑**（G13）；仓位**算法与参数**（Kelly/inverse-vol/单票 8%/行业/总仓位阈值）在 [31_position_sizing](31_position_sizing.md)（G12）已定，本备忘只消费；BudgetChangeHandler 三级升级（G14）在 [33_budget_change_handler](33_budget_change_handler.md)；RegimeMetaAllocator 参数（G15）在 34 号。

## 1. 背景

### 1.1 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G13 FirmRiskAggregator 逻辑 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | G12（仓位算法，[31_position_sizing](31_position_sizing.md) v1.23.0 已定稿） |
| 对标 | Citadel pod 模型 firm 层风险聚合 / Morwane risk-parity-throttle |
| 正交性 | ✅ 与 regime 正交（regime 只缩 budget，不调聚合逻辑） |
| 优先级 | P2 |
| 状态 | ✅ 已定稿 v1.0.21（§2.1 pre_kelly/post_kelly 两段伪代码缺陷修复 A-G 闭环；§2.10.7 Fassino Cauchy 不动点 + §2.10.8 Kakinaga MFCCA + §2.10.9 Hsieh Certified Wasserstein DRO LP 三项远期候选登记（协方差/风险泛函演进三级路径 Fassino→Kakinaga→Hsieh）；§2.10.5 E 补 Absorption Ratio 经典基线背书 + Hammond 2026 实证 + VRC Fragility Score 理论参照；v1.0.20 文档-代码一致性修复（§1.2 L39+§2.1 L76"骨架/待拆分"→"已施工 production"）；**v1.0.21（2026-08-12）灾后修复**：33 号骨架化交叉引用修正 4 处 + §4.2 演进路径三阶段状态更新 + §6 拆分行关闭/字段名三方漂移 P0/T+1 可卖口径/测试丢失/registry 未登记/depgraph 滞后六行 + §7.2 表补状态列 + §7.6 新增已施工设施盘点 + §9 补 v1.0.20 漏记条目。历史细节见 §9 修订记录） |

### 1.2 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1，不能做空）
- 多策略并发架构已定稿为 Model A（独立账本 + firm 风险聚合），见 [30_multi_strategy_concurrency §2](30_multi_strategy_concurrency.md)
- 3-5 个 StrategyBook 各自产出 `StrategyTarget`（粗仓位），需在 firm 层聚合为统一的 `FirmTargetPortfolio`
- [MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) 代码**已施工完成 production**（v1.0.0，2026-08-10，v1.0.20 文档-代码一致性修复）：两段接口 `pre_kelly_aggregate()`+`post_kelly_clip()` 已实现，`aggregate()` 便捷入口内部串联两段+Kelly passthrough，54 单元测试全绿（0.09s），MATURITY=production。§2.1.1 施工伪代码 A-G 修复全部在位（constraint_checks liquidity_cap 键 / degraded 条件 5 条 / adv_data 参数化 / total_budget 口径 / contributions 透传 / sector_overlay_active 预留）

### 1.3 核心问题
30_multi_strategy_concurrency §2.2 已锁定 FirmRiskAggregator 的**职能框架**（求和+硬上限裁剪+冲突处理，不做 MVO），但未定义：
- 求和的确切语义（权重直接相加？budget 口径如何统一？）
- 单票硬上限裁剪的执行算法（按比例削 vs 按策略优先级截断）
- 行业/总仓位硬约束的执行顺序与口径
- 冲突标的（一策略买一策略卖同标的）如何处理
- 输出 `FirmTargetPortfolio` 的数据结构契约
- O(N) 复杂度如何保证（不退化为准 O(N²) 的优化器）

本备忘的工作就是把这些框架变成可施工的执行逻辑。

### 1.4 约束条件
- **30_multi_strategy_concurrency §2.3**：自然叠加——用加法替代优化器，O(N) 替代 O(N²)
- **30_multi_strategy_concurrency §3.1**：不做 MVO，不做协方差估计
- **31_position_sizing §2.4**：硬上限参数已定（单票 8% 总资金口径 / 行业 ±10% 叠加态 ±15% 绝对 30% / 总仓位 9 态 + 3 特殊态 + 2 overlay / **§2.4.4 流动性 ADV 口径 20%/10% 两档**）
- **31_position_sizing §2.1**：分层裁定顺序——求和 → Kelly 精裁决 → 硬上限裁剪（Kelly 在前，裁剪在后，先精算后兜底）
- **31_position_sizing §2.6**：`FirmTargetPortfolio` 数据结构契约已定（holdings 权重和=1.0 含 CASH）
- A 股 T+1 / 不能做空 → 冲突标的不能"做空对冲"，只能净额处理
- INVARIANTS（MOD-POS-021 代码头）：自然叠加 / 按比例削非优先级截断 / 不做 MVO / O(N) / 冲突按净额

## 2. 决策：自然叠加 + 三级硬裁剪 + 冲突净额

### 2.1 聚合流程总览

FirmRiskAggregator 的聚合分两段参与分层裁定（与 [31_position_sizing §2.1](31_position_sizing.md) 数据流一致）：

```
[各 StrategyBook]           [FirmRiskAggregator]            [MOD-POS-001]             [FirmRiskAggregator]
StrategyTarget   →   ① 按标的求和(自然叠加)  →  ③ Kelly精裁决  →  ④ 单票/行业/总仓位硬裁剪  →  FirmTargetPortfolio
                     ② 冲突标的净额处理              (半Kelly+分布感知)       ⑤ 现金管理(CASH=1-sum)
                        O(N) 加法                    只减不增为主              兜底不可突破
```

**两段参与理由**：Kelly 是"精算"（只减不增为主），裁剪是"兜底"（不可突破）。Kelly 需看到求和后的真实总暴露才精算准确（31_position_sizing §2.1："先精算后兜底"）。FirmRiskAggregator 第一段做求和（步骤①②），交 MOD-POS-001 做 Kelly（步骤③），第二段做硬裁剪（步骤④⑤）。

> **✅ 代码现状与设计意图对齐（2026-08-10，v1.0.20 文档-代码一致性修复）**：[MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) 已按设计意图拆分为两段——`pre_kelly_aggregate()`（求和+冲突净额）+ `post_kelly_clip()`（单票/行业/总仓位/现金），由 MOD-POS-001 在中间调用 Kelly。`aggregate()` 便捷入口内部串联 `pre_kelly_aggregate → kelly_fn(passthrough) → post_kelly_clip`，实现"先 Kelly 后裁剪"数据流（31_position_sizing §2.1 "先精算后兜底"）。54 单元测试全绿（0.09s），MATURITY=production。原 §6 待定问题"拆分"项已解决。

> **pre_kelly_aggregate / post_kelly_clip 接口契约（2026-08-10 施工流程补充）**：拆分后的两段接口签名与职责边界如下：
>
> ```python
> # 第一段：求和 + 冲突净额（Kelly 前）
> def pre_kelly_aggregate(
>     targets: list[StrategyTarget],        # 各 StrategyBook 产出
>     current_holdings: dict[str, float],    # symbol → 当前持仓权重（T-1 收盘快照，净额截断必需）
>     total_budget: float,                   # 所有策略 budget 之和（G15 RegimeMetaAllocator 输出）
>     industry_map: dict[str, str],          # symbol → 申万/中信行业映射
> ) -> PreKellyResult:
>     """职责：§2.2 按标的求和（自然叠加，budget 口径归一）+ §2.3 冲突标的净额处理
>     不做：Kelly / 单票裁剪 / 行业裁剪 / 总仓位裁剪 / 现金管理
>     输出：summed_weights: dict[str, float]（归一后权重）+ conflicts: list[ConflictRecord]
>     """
>
> # 第二段：硬上限裁剪 + 现金管理（Kelly 后）
> def post_kelly_clip(
>     kelly_adjusted: dict[str, float],  # MOD-POS-001 Kelly 精裁决后输出（f_i^final）
>     total_budget: float,
>     industry_map: dict[str, str],
>     regime_cap: float,                 # G15 RegimeMetaAllocator 输出的总仓位上限
> ) -> FirmTargetPortfolio:
>     """职责：§2.4 单票裁剪 → §2.5 行业裁剪 → §2.5.2 总仓位裁剪 → §2.5 现金管理
>     不做：Kelly / 求和 / 冲突处理（Kelly 前已完成）
>     输出：FirmTargetPortfolio（§2.7 数据结构，含 constraint_checks/degraded/conflicts_resolved）
>     """
> ```
>
> **两段接口的数据流**：`StrategyBook → pre_kelly_aggregate → MOD-POS-001 Kelly → post_kelly_clip → FirmTargetPortfolio`。MOD-POS-001 消费 `PreKellyResult.summed_weights[symbol]` 作为 `w_i^sum`（31号 §2.3.4 合成规则的粗仓位求和值），产出 `kelly_adjusted[symbol]` 交 `post_kelly_clip` 做最终裁剪。

> **degraded 降级标记触发条件（2026-08-10 施工流程补充）**：`FirmTargetPortfolio.degraded: bool` 标记聚合过程是否发生降级。降级不阻断输出（仍产出合规 FirmTargetPortfolio），但供 G14 BudgetChangeHandler 判断是否需三级升级。触发条件（任一满足即 `degraded=True`）：
> 1. **冲突标的净额截断**：冲突标的净额 < 0 但因 A 股不能做空截断为清仓（§2.3），`conflicts_resolved` 中有 `net_weight < 0` 记录 → 降级（策略意愿未完全表达）
> 2. **单票裁剪触发**：任一标的 `cut_ratio > 0`（§2.4 求和后超 8% 被削）→ 降级（组合集中度超限）
> 3. **行业裁剪触发**：任一行业超绝对 30% 或偏离 ±10%/±15% 被裁（§2.5.1）→ 降级（行业集中度超限）
> 4. **总仓位裁剪触发**：总仓位超 regime Shrinkage 上限被等比缩放（§2.5.2）→ 降级（总暴露超限）
> 5. **Kelly 参数降级传导**：MOD-POS-001 Kelly 降级到历史回测源（31号 §2.3.2 `param_source="historical_fallback"`）→ 降级（密度 PDF 估错，Kelly 精算基于滞后数据）
>
> **degraded=False** 的含义：所有策略意愿完全表达、无裁剪触发、Kelly 主源（密度 PDF）正常。degraded 不等于错误——降级是防御性安全网正常工作的表现，但需 G14 审计是否需三级升级收敛

### 2.1.1 施工算法实现（pre_kelly_aggregate + post_kelly_clip 完整伪代码）

> **2026-08-10 七次审查补全**：§2.1 定义了两段接口契约（签名+职责边界），§2.2-§2.5 定义了各步骤算法（片段伪代码），但缺乏统一编排入口的完整施工伪代码。以下将 §2.2 求和 + §2.3 冲突净额整合为 `pre_kelly_aggregate()`，将 §2.4 单票裁剪 + §2.5 行业/总仓位裁剪 + 现金管理整合为 `post_kelly_clip()`，供 [firm_risk_aggregator.py](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) MOD-POS-021 施工参考。风格对齐 [33号 §3.4](33_budget_change_handler.md) `handle_budget_change` 完整伪代码。

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ── 常量（参数来源：31_position_sizing §2.4）──
SINGLE_NAME_CAP = 0.08           # 单票硬上限 8%（总资金口径，§2.4）
SECTOR_DEVIATION_CAP = 0.10      # 单行业偏离基准 ±10%（§2.5.1）
SECTOR_DEVIATION_CAP_OVERLAY = 0.15  # 叠加态 ±15%（板块轮动 overlay 激活时）
SECTOR_ABSOLUTE_CAP = 0.30       # 单行业绝对上限 30%（§2.5.1）
CASH_SYMBOL = "CASH"             # 现金虚拟标的（§2.4 CASH 豁免裁剪）


@dataclass(frozen=True)
class PreKellyResult:
    """pre_kelly_aggregate 输出：求和+冲突净额后的权重 + 冲突记录 + 策略贡献归因。

    交 MOD-POS-001 做 Kelly 精裁决（31号 §2.3.4 合成规则消费 summed_weights[symbol] 作为 w_i^sum）。
    """
    summed_weights: dict[str, float]          # symbol → 归一后权重（budget 口径，含净额截断）
    conflicts: list[dict[str, Any]]           # ConflictRecord 列表（§2.3 冲突标的净额处理记录）
    total_exposure_pre_kelly: float           # 求和后总暴露（sum of summed_weights，供 Kelly 层 pro-rata 参考）
    contributions: dict[str, dict[str, float]]  # v1.0.19 补：symbol → {strategy_id: 贡献权重}（§2.2 归因用，须透传给 post_kelly_clip 写入 firm_positions[symbol]["contributions"]，否则归因数据丢失）


def pre_kelly_aggregate(
    targets: list[dict[str, Any]],       # 各 StrategyBook 产出的 StrategyTarget（含 strategy_id/target_portfolio/budget_used）
    current_holdings: dict[str, float],   # symbol → 当前持仓权重（T-1 收盘快照，净额截断必需，§2.3）
    total_budget: float,                  # 所有策略 budget_used 之和（G15 RegimeMetaAllocator 输出）
    industry_map: dict[str, str],         # symbol → 申万/中信行业映射（post_kelly_clip 用，pre_kelly 只传递）
) -> PreKellyResult:
    """第一段：按标的求和（自然叠加，§2.2）+ 冲突标的净额处理（§2.3）。
    
    职责：
      - §2.2 各策略 target_portfolio 按 budget 口径归一后按 symbol 求和
      - §2.3 冲突标的（一买一卖）按净额处理，净额<0 截断为 max(0, net+holdings)
    
    不做：Kelly / 单票裁剪 / 行业裁剪 / 总仓位裁剪 / 现金管理
    
    Returns: PreKellyResult（summed_weights + conflicts + total_exposure_pre_kelly）
    """
    # ── Step 1: budget 口径归一化求和（§2.2 自然叠加）──
    # 各策略 target_portfolio 权重是相对各自 strategy_budget 的占比
    # 求和前须先归一到账户总资金口径：account_weight = tp_weight × budget_used / total_budget
    raw_summed: dict[str, float] = {}
    # 同时记录每个 symbol 的各策略贡献（归因用，§2.2 contributions）
    contributions: dict[str, dict[str, float]] = {}  # symbol → {strategy_id: 贡献权重}
    
    for tp in targets:
        strategy_id = tp["strategy_id"]
        budget_used = tp["budget_used"]
        scale = budget_used / total_budget if total_budget > 0 else 0.0
        
        for symbol, tp_weight in tp["target_portfolio"].items():
            if symbol == CASH_SYMBOL:
                continue  # CASH 不参与求和（§2.4 CASH 豁免，现金由 firm 层统一管理）
            account_weight = tp_weight * scale
            raw_summed[symbol] = raw_summed.get(symbol, 0.0) + account_weight
            if symbol not in contributions:
                contributions[symbol] = {}
            # 记录策略贡献方向（正=买，负=卖）
            contributions[symbol][strategy_id] = contributions[symbol].get(strategy_id, 0.0) + account_weight
    
    # ── Step 2: 冲突标的净额处理（§2.3）──
    # 冲突 = 一策略买（正权重）另一策略卖（负权重）同一标的
    # 净额 = sum(contributions)，净额<0 时 A 股不能做空 → 截断为 max(0, net + current_holdings_weight)
    conflicts: list[dict[str, Any]] = []
    summed_weights: dict[str, float] = {}
    
    for symbol, net_weight in raw_summed.items():
        strategy_contribs = contributions[symbol]
        has_buy = any(w > 0 for w in strategy_contribs.values())
        has_sell = any(w < 0 for w in strategy_contribs.values())
        
        if has_buy and has_sell:
            # 冲突标的（§2.3）：一买一卖
            conflict_record = {
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
                conflict_record["truncated_amount"] = net_weight + holdings_weight - final_weight  # 被截断的意愿量
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
    
    total_exposure_pre_kelly = sum(summed_weights.values())
    
    return PreKellyResult(
        summed_weights=summed_weights,
        conflicts=conflicts,
        total_exposure_pre_kelly=total_exposure_pre_kelly,
        contributions=contributions,  # v1.0.19 补：透传给 post_kelly_clip 写入 firm_positions[symbol]["contributions"]（§2.2 归因），修复原数据流断裂（contributions 在内部构建却未传出导致归因丢失）
    )


# ── MOD-POS-001 Kelly 精裁决在中间调用（31号 §2.3）──
# 输入：PreKellyResult.summed_weights[symbol] 作为 w_i^sum
# 输出：kelly_adjusted: dict[str, float]（= f_i^norm，经合成+归一化后的最终仓位建议）
# Kelly 层含 §2.3.5 pro-rata 归一化（若 Kelly 后 sum > regime_cap 则按比例缩放）


def post_kelly_clip(
    kelly_adjusted: dict[str, float],   # MOD-POS-001 Kelly 精裁决后输出（f_i^norm，31号 §2.3.7）
    total_budget: float,                 # 所有策略 budget 之和
    industry_map: dict[str, str],        # symbol → 申万/中信行业映射
    regime_cap: float,                   # G15 RegimeMetaAllocator 输出的总仓位上限（§2.5.2）
    sector_overlay_active: bool = False,  # ⚠️ 预留参数（v1.0.19 澄清）：§2.5.1 行业偏离裁剪 overlay 档（±15% vs ±10%）的开关。当前因行业偏离裁剪整体待 D-FACTOR 行业分类模块确认（见 Step 2 注释 + §6 待定）而未消费——非死代码，是 §2.5.1 接口契约的前向兼容预留，D-FACTOR 落地后连同偏离裁剪一起消费
    contributions: dict[str, dict[str, float]] | None = None,  # v1.0.19 补：各 symbol 的策略贡献（归因用），应从 PreKellyResult.contributions 传入（pre_kelly_aggregate 产出）。None 时 firm_positions[symbol]["contributions"] 写空 dict（归因降级）
    adv_data: dict[str, dict[str, float]] | None = None,  # v1.0.19 补：symbol → {adv_20d_p25: float}，Step 1b 流动性裁剪必需
    conflicts: list[dict[str, Any]] | None = None,  # pre_kelly_aggregate 产出的冲突记录（degraded 条件1 判定必需）
    kelly_param_source: str = "density_pdf",  # Kelly 参数来源（degraded 条件5 判定：density_pdf 正常 / historical_fallback 降级）
) -> dict[str, Any]:
    """第二段：硬上限裁剪（§2.4 单票 → §2.5.1 行业 → §2.5.2 总仓位）+ 现金管理。
    
    职责：
      - §2.4 单票裁剪（>8% 按比例削，CASH 豁免）
      - §2.5.1 行业裁剪（偏离 ±10%/±15% + 绝对 30%，按比例削）
      - §2.5.2 总仓位裁剪（>regime_cap 等比缩放）
      - 现金管理（CASH = total_budget - sum(裁剪后股票权重)，§2.5 残差计算）
    
    级联关系（§2.5.2 级联裁剪说明）：每步输入=上步输出，每步只减不增，单调收敛。
    
    不做：Kelly / 求和 / 冲突处理（Kelly 前已完成）
    
    Returns: FirmTargetPortfolio（§2.7 数据结构，含 firm_positions/constraint_checks/degraded/conflicts_resolved）
    """
    # ── 初始化：从 kelly_adjusted 复制为可变 dict（裁剪过程修改）──
    # 同时初始化 cut_ratio 记录
    clipped: dict[str, float] = {}      # symbol → 裁剪中权重
    cut_ratios: dict[str, float] = {}   # symbol → 累积裁剪比例
    constraint_checks: dict[str, Any] = {
        "single_name": {"triggered": False, "cuts": []},
        "sector": {"triggered": False, "cuts": []},
        "total_exposure": {"triggered": False, "scale": 1.0},
        "liquidity_cap": {"triggered": False, "cuts": []},  # v1.0.19 补：Step 1b 流动性裁剪
    }
    
    for symbol, weight in kelly_adjusted.items():
        if symbol == CASH_SYMBOL:
            continue  # CASH 豁免裁剪（§2.4），权重在 Step 4 残差计算
        clipped[symbol] = weight
        cut_ratios[symbol] = 0.0
    
    # ══ Step 1: 单票硬上限裁剪（§2.4 按比例削）══
    for symbol in list(clipped.keys()):
        if clipped[symbol] > SINGLE_NAME_CAP:
            cut_ratio = 1.0 - SINGLE_NAME_CAP / clipped[symbol]
            clipped[symbol] = SINGLE_NAME_CAP
            cut_ratios[symbol] = cut_ratio
            constraint_checks["single_name"]["triggered"] = True
            constraint_checks["single_name"]["cuts"].append({
                "symbol": symbol, "cut_ratio": cut_ratio, "capped_at": SINGLE_NAME_CAP,
            })

    # ══ Step 1b: 流动性硬上限裁剪（§2.4.4 ADV 口径，2026-08-10 十九次审查补）══
    # 阈值与口径见 [31号 §2.4.4](31_position_sizing.md)；本步执行裁剪
    # v1.0.19 修复：adv_data 作为参数传入（非未定义变量），sector_adv_median 从 adv_data 派生，total_capital→total_budget
    if adv_data is None:
        adv_data = {}  # 无 ADV 数据时跳过流动性裁剪（降级为不触发）
    # 预计算行业 ADV 中位数（降级路径用）
    sector_advs: dict[str, list[float]] = {}
    for sym, adv_info in adv_data.items():
        sec = industry_map.get(sym, "UNKNOWN")
        adv_val = adv_info.get("adv_20d_p25", 0)
        if adv_val > 0:
            sector_advs.setdefault(sec, []).append(adv_val)
    sector_adv_median = {sec: sorted(vals)[len(vals)//2] for sec, vals in sector_advs.items() if vals}
    
    for symbol in list(clipped.keys()):
        adv_i = adv_data.get(symbol, {}).get("adv_20d_p25", 0)  # 20 日 ADV 下四分位（最坏情况）
        if adv_i <= 0:  # ADV 缺失/停牌 → 降级取同行业中位数（31号 §2.4.4 降级路径）
            adv_i = sector_adv_median.get(industry_map.get(symbol, "UNKNOWN"), 0)
        if adv_i > 0:
            position_value = clipped[symbol] * total_budget  # v1.0.19 修复：total_capital→total_budget
            adv_pct = position_value / adv_i
            if adv_pct > 0.20:  # 严重档：削到 20% ADV
                old = clipped[symbol]
                clipped[symbol] = old * (0.20 / adv_pct)
                cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios.get(symbol, 0)) * (0.20 / adv_pct)
                constraint_checks["liquidity_cap"]["triggered"] = True
                constraint_checks["liquidity_cap"]["cuts"].append(
                    {"symbol": symbol, "tier": "severe", "adv_pct": adv_pct, "capped_at_adv": 0.20})
            elif adv_pct > 0.10:  # 削半档
                clipped[symbol] *= 0.5
                constraint_checks["liquidity_cap"]["triggered"] = True
                constraint_checks["liquidity_cap"]["cuts"].append(
                    {"symbol": symbol, "tier": "moderate", "adv_pct": adv_pct, "halved": True})

    # ══ Step 2: 行业硬约束裁剪（§2.5.1）══
    # 2a. 行业归类求和
    sector_weights: dict[str, float] = {}
    sector_symbols: dict[str, list[str]] = {}
    for symbol, weight in clipped.items():
        sector = industry_map.get(symbol, "UNKNOWN")
        sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
        sector_symbols.setdefault(sector, []).append(symbol)
    
    # 2b. 绝对上限 30% 裁剪（不可突破硬顶）
    for sector, weight in sector_weights.items():
        if weight > SECTOR_ABSOLUTE_CAP:
            scale = SECTOR_ABSOLUTE_CAP / weight
            for symbol in sector_symbols[sector]:
                old = clipped[symbol]
                clipped[symbol] = old * scale
                cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios[symbol]) * scale  # 累积裁剪比例
            sector_weights[sector] = SECTOR_ABSOLUTE_CAP
            constraint_checks["sector"]["triggered"] = True
            constraint_checks["sector"]["cuts"].append({
                "sector": sector, "type": "absolute_cap", "scale": scale,
                "capped_at": SECTOR_ABSOLUTE_CAP,
            })
    
    # 注：行业偏离基准 ±10%/±15% 裁剪需行业基准权重数据（申万/中信行业基准），
    # 待 D-FACTOR 行业分类模块确认后补充（§6 待定问题）。MVP 先做绝对上限 30%。
    
    # ══ Step 3: 总仓位硬约束裁剪（§2.5.2 等比缩放）══
    # 注意：若 Kelly 层 §2.3.5 已做 pro-rata 归一化（sum ≤ regime_cap），此步自动不触发
    total_exposure = sum(clipped.values())
    if total_exposure > regime_cap:
        scale = regime_cap / total_exposure
        for symbol in clipped:
            clipped[symbol] *= scale
            cut_ratios[symbol] = 1.0 - (1.0 - cut_ratios[symbol]) * scale
        constraint_checks["total_exposure"]["triggered"] = True
        constraint_checks["total_exposure"]["scale"] = scale
        total_exposure = regime_cap
    
    # ══ Step 4: 现金管理（CASH 残差计算，§2.5）══
    # CASH = total_budget - sum(裁剪后股票权重)
    # CASH 不参与裁剪（§2.4 豁免），权重作为残差计算
    # 叠加 31号 §2.5 现金硬约束（最低储备金/机会储备/节假日等）由上层传入
    cash_weight = total_budget - total_exposure
    if cash_weight < 0:
        # 理论上 Step 3 总仓位裁剪后 total_exposure ≤ regime_cap ≤ total_budget
        # 但浮点精度或 lot 对齐偏差可能导致微小负值，兜底为 0
        cash_weight = 0.0
    
    clipped[CASH_SYMBOL] = cash_weight
    
    # ══ 组装 FirmTargetPortfolio（§2.7 数据结构）══
    firm_positions: dict[str, dict[str, Any]] = {}
    for symbol, weight in clipped.items():
        firm_positions[symbol] = {
            "target_weight": weight,
            "contributions": contributions.get(symbol, {}) if contributions else {},
            "cut_ratio": cut_ratios.get(symbol, 0.0),
        }
    
    # ── degraded 降级标记（§2.1 触发条件，2026-08-10 修复条件1空列表 bug）──
    conflicts_resolved = conflicts or []
    degraded = (
        any(c.get("truncated", False) for c in conflicts_resolved)  # 条件1: 冲突净额截断（net_weight<0 截断为清仓）
        or constraint_checks["single_name"]["triggered"]    # 条件2: 单票裁剪触发
        or constraint_checks["sector"]["triggered"]         # 条件3: 行业裁剪触发
        or constraint_checks["total_exposure"]["triggered"]  # 条件4: 总仓位裁剪触发
        or constraint_checks["liquidity_cap"]["triggered"]   # 条件4b: 流动性裁剪触发（v1.0.19 补，G14 BudgetChangeHandler 感知流动性降级）
        or kelly_param_source == "historical_fallback"      # 条件5: Kelly 参数降级传导（31号 §2.3.2 param_source 标记）
    )

    return {
        "firm_positions": firm_positions,
        "total_exposure": total_exposure,
        "total_budget": total_budget,
        "cash_ratio": cash_weight,
        "constraint_checks": constraint_checks,
        "conflicts_resolved": conflicts_resolved,   # §2.7 FirmTargetPortfolio 契约字段（冲突净额记录）
        "degraded": degraded,
        "created_at": datetime.now(),
        "idempotency_key": f"firm_agg_{int(datetime.now().timestamp())}",
        "schema_version": "1.0",
    }
```

> **施工要点**：
> 1. **两段调用顺序**：`StrategyBook → pre_kelly_aggregate → MOD-POS-001 Kelly → post_kelly_clip → FirmTargetPortfolio`。MOD-POS-001 消费 `PreKellyResult.summed_weights[symbol]` 作为 `w_i^sum`（31号 §2.3.4），产出 `kelly_adjusted[symbol]` 交 `post_kelly_clip`。**数据传递**：`pre_kelly_aggregate` 产出的 `conflicts` 列表 + `contributions` 归因字典 + MOD-POS-001 产出的 `kelly_param_source` 标记须传入 `post_kelly_clip` 的 `conflicts` / `contributions` / `kelly_param_source` 参数——`conflicts` 供 degraded 条件 1 判定（2026-08-10 修复：原传空列表 `[]` 永不触发 bug），`contributions` 供 `firm_positions[symbol]["contributions"]` 归因写入（v1.0.19 修复：原 PreKellyResult 未带 contributions 字段导致归因数据丢失，现 PreKellyResult 增 contributions 字段并透传），`kelly_param_source` 供 degraded 条件 5 判定。
> 2. **CASH 豁免贯穿全流程**：pre_kelly 求和跳过 CASH（§2.2），post_kelly 裁剪跳过 CASH（§2.4），CASH 权重在 Step 4 作为残差计算（`CASH = total_budget - sum(股票权重)`）。
> 3. **级联裁剪单调收敛**：Step 1→2→3 每步输入=上步输出，每步只减不增（`clipped_n ≤ clipped_{n-1}`）。若 Kelly 层 §2.3.5 已 pro-rata 归一化使 sum ≤ regime_cap，Step 3 自动跳过（`triggered=False`），不会双重缩放（§6 待定问题防重复缩放）。
> 4. **cut_ratio 累积**：多级裁剪的 `cut_ratio` 是累积值（非独立），用 `1 - (1-r1)*(1-r2)` 公式合并，保证归因可追溯——`constraint_checks` 中每级裁剪独立记录 `triggered` + `cut_amount`。
> 5. **degraded 降级标记**：任一裁剪触发（单票/行业/总仓位）或冲突净额截断 → `degraded=True`，供 G14 BudgetChangeHandler 判断是否需三级升级（§2.1 触发条件 5 条）。
> 6. **行业偏离基准 ±10%/±15% 待 D-FACTOR**：MVP 先做绝对上限 30% 裁剪（只需 industry_map），偏离基准裁剪需行业基准权重数据（申万/中信行业基准），待 D-FACTOR 行业分类模块确认后补充（§6 待定）。
> 7. **幂等性**：`idempotency_key` 防重复聚合。两段拆分后幂等语义：pre_kelly 结果可缓存，Kelly 重试用同 PreKellyResult（§6 待定问题 pre_kelly/post_kelly 幂等性）。

### 2.2 按标的求和（自然叠加）—— 讨论要点 ①

**算法**：各 StrategyBook 的 `target_portfolio` 按 symbol 直接相加。

```python
# S1 给 600519 = 3%, S2 给 600519 = 5% → 求和后 600519 = 8%
summed_weight[symbol] = sum(tp.target_portfolio[symbol] for tp in target_portfolios if symbol in tp.target_portfolio)
```

**为什么用加法不用优化器**（30_multi_strategy_concurrency §2.3）：
- **等价于永远稳定的等权 risk-budget 优化器**：多策略选到同一只票时仓位自然叠加，无需调投票权重，无需估协方差
- **O(N) 替代 O(N²)**：N 个策略 M 个标的，求和是 O(N×M)；MVO 优化器是 O(M²) 甚至 O(M³)（协方差矩阵求逆）
- **归因清晰**：求和后每只票的权重 = 各策略贡献之和，可追溯到 `contributions: dict[str, float]`（`FirmTarget` 字段），亏钱时能区分哪个策略贡献了多少
- **行业实践印证**：[finlab multi-strategy portfolio](https://finlab.finance/docs/en/workflows/multi_strategy_portfolio/)（2026）明确"if Strategy A holds 2330 at 5% and Strategy B holds 2330 at 3%, the final portfolio holds 8%"——与本项目自然叠加算法完全一致；[quant-portfolio multi-sleeve](https://github.com/isaacnicas/quant-portfolio)（2026-06）实践 per-order attribution 分离各 sleeve 贡献，与 `contributions` 归因字段同理；[rustybt Order Aggregation](https://jerryinyang.github.io/rustybt/api/portfolio-management/order-aggregation/)（2025-10）多策略订单净额聚合——`broker_net(symbol) = Σ subbook[strategy_id].position(symbol)`，与本项目 §2.2 求和 + §2.3 冲突净额同构；[APEX ADR-0012](https://github.com/clement-bbier/APEX/pull/220/files)（2026）多策略 netting + sub-books 架构——"The broker knows only the platform's aggregate net on each symbol; the sub-books collectively re-project that net back into per-strategy components"，与本项目 `contributions` 归因 + `FirmTargetPortfolio` 契约同构；[youcanbuildthings Multi Strategy Allocator](https://youcanbuildthings.com/articles/multi-strategy-trading-bot-python)（2026-05-06）明确"Netting is not a decision; it is arithmetic. The allocator does not ask should I net — it nets"——印证本项目净额处理 O(M) 加法非优先级仲裁的设计

**budget 口径统一**：各 StrategyBook 的 `target_portfolio` 权重是相对各自 `strategy_budget` 的占比。求和前须先归一到账户总资金口径：

```python
# 归一化：策略权重 × 策略 budget / 账户总资金
account_weight[symbol] = sum(
    tp.target_portfolio[symbol] * tp.budget_used / total_budget
    for tp in target_portfolios if symbol in tp.target_portfolio
)
```

> `total_budget` = 所有策略 `budget_used` 之和。各策略 budget 由 RegimeMetaAllocator（G15）分配，FirmRiskAggregator 只消费，不分配。

### 2.3 冲突标的净额处理 —— 讨论要点 ④

**问题**：一策略买标的 X（正权重），另一策略卖标的 X（负权重）。A 股不能做空，但策略可表达"减仓/清仓"意愿（卖出现有持仓）。

**算法**：按净额处理，不按优先级截断。

```python
net_weight = sum(contributions[strategy_id] for strategy_id in all_strategies)
# net_weight > 0 → 买入/持有净额
# net_weight < 0 → 卖出净额（仅可减现有持仓，不可做空）
# net_weight = 0 → 两策略完全对冲，不持有
```

**为什么净额不用优先级**（INVARIANTS + 30 §3.2 拒绝 Model D）：
- **优先级是 meta-参数**：需回测/调参/衰减监控，是技术债（30_multi_strategy_concurrency §3.2 拒绝投票权重的同理）
- **净额是 O(1)**：每个冲突标的一次加法；优先级仲裁是 O(N) 乃至 O(N²)（30_multi_strategy_concurrency §3.2）
- **A 股不能做空约束**：净额 < 0 时截断为 max(0, net_weight - current_holdings_weight)，即最多清仓不做空

> **净额截断需 current_holdings 输入（2026-08-10 施工流程补充）**：净额 < 0 截断规则 `max(0, net_weight - current_holdings_weight)` 需要知道**当前持仓权重** `current_holdings_weight`。FirmRiskAggregator 的 `pre_kelly_aggregate()` 接口除 `targets: list[StrategyTarget]` 外，**须额外接收 `current_holdings: dict[str, float]`**（symbol → 当前持仓权重，来自持仓对账模块 MOD-POS-008 / position_limit_enforcer）。
>
> - `current_holdings_weight = current_holdings.get(symbol, 0.0)`（无持仓时为 0，净额<0 直接截 0）
> - 净额 < 0 时：`final_weight = max(0, net_weight + current_holdings_weight)`（净卖出不超过现有持仓，剩余意愿记入 `ConflictRecord` 供归因审计："策略想卖 X% 但只有 Y% 持仓，仅卖 Y%）
> - 净额 ≥ 0 时：`final_weight = net_weight`（无截断需求，current_holdings 不参与）
> - **数据流**：`current_holdings` 来自持仓对账（T-1 收盘持仓快照），非 StrategyTarget 产出。`pre_kelly_aggregate(targets, current_holdings, total_budget, industry_map)` 四入参，其中 `current_holdings` 是净额截断的必要输入

**冲突记录**：`ConflictRecord`（代码已定义）记录买方/卖方策略及权重，供归因审计：

```python
@dataclass(frozen=True)
class ConflictRecord:
    symbol: str
    buy_strategies: dict[str, float]     # {strategy_id: 买方权重}
    sell_strategies: dict[str, float]    # {strategy_id: 卖方权重}
    net_weight: float                    # 净额
```

**边界**：净额处理仅适用于"一买一卖"冲突。多策略同向（都买或都卖）不是冲突，是自然叠加（§2.2）。

### 2.4 单票硬上限裁剪（按比例削）—— 讨论要点 ②

**参数来源**：[31_position_sizing §2.4.1](31_position_sizing.md)——单票 8%（总资金口径），跨策略求和后 > 8% 按各策略贡献比例削。

**算法**：按比例削（pro-rata clipping），非按策略优先级截断。

```python
single_name_cap = 0.08  # G12 §2.4.1 定义
for symbol, firm_target in firm_positions.items():
    if firm_target.target_weight > single_name_cap:
        cut_ratio = 1.0 - single_name_cap / firm_target.target_weight
        # 按各策略贡献比例削，保持相对贡献不变
        for strategy_id in firm_target.contributions:
            firm_target.contributions[strategy_id] *= (1.0 - cut_ratio)
        firm_target.target_weight = single_name_cap
        firm_target.cut_ratio = cut_ratio
```

**为什么按比例削不用优先级截断**（INVARIANTS："单票硬上限裁剪按比例削(非按策略优先级截断)"）：
- **归因公平**：按比例削保持各策略相对贡献不变，亏赚归因不被裁剪扭曲；优先级截断会让低优先级策略"被抹零"，归因失真
- **无 meta 参数**：按比例削是确定性算法（O(1) per symbol），优先级需定义排序规则（按 Sharpe？按 PnL？按 budget？），引入 meta 参数
- **与自然叠加一致**：自然叠加（§2.2）是"各策略平等贡献"，按比例削是"各策略平等承担裁剪"，哲学一致

> **8% vs 5% 口径**：31_position_sizing §2.4.1 已澄清三层口径（MOD-POS-001 默认 5% / MOD-POS-021 聚合 8% / MOD-POS-010 硬限 5%）。FirmRiskAggregator 用 8% 做聚合后裁剪，MOD-POS-010 的 5% 是最终兜底。三层口径待统一（31_position_sizing §5）。
>
> **CASH 豁免裁剪（2026-08-10 施工流程补充）**：CASH 虚拟标的（31号 §2.5 现金管理）**不参与单票/行业/总仓位裁剪**——CASH 无行业归属（`industry_map` 中无 "CASH" 键）、无策略 contributions（现金由 firm 层统一管理非策略产出）、Kelly 豁免（31号 §2.3.6 CASH σ≈0）。裁剪循环须显式跳过 CASH：`for symbol in firm_positions: if symbol == "CASH": continue`。CASH 权重在现金管理步骤（§2.5.2 Step 4）作为残差计算：`CASH = total_budget - sum(裁剪后股票权重)`，确保 `holdings` 权重和 + `cash_ratio` = `total_budget`

### 2.5 行业/总仓位硬约束 —— 讨论要点 ③

**参数来源**：[31_position_sizing §2.4.2/§2.4.3](31_position_sizing.md)。

#### 2.5.1 行业硬约束

| 约束 | 阈值 | 执行 |
|---|---|---|
| 单行业偏离基准 | ±10%（叠加态 ±15%） | 按行业归类求和后超限，行业内各标的按比例削 |
| 单行业绝对上限 | 30% | 不可突破硬顶，按比例削 |

**算法**：
```python
# 行业归类求和（只需持仓权重 + 行业映射，不估协方差）
sector_weights = {}
for symbol, firm_target in firm_positions.items():
    sector = industry_map[symbol]
    sector_weights[sector] = sector_weights.get(sector, 0) + firm_target.target_weight

# 裁剪：超绝对上限 30% 的行业，行业内按比例削
for sector, weight in sector_weights.items():
    if weight > sector_absolute_cap:  # 0.30
        scale = sector_absolute_cap / weight
        for symbol in symbols_in_sector[sector]:
            firm_positions[symbol] = clip(firm_positions[symbol], scale)
```

**口径**：按持仓权重按行业归类求和，**不估协方差**（与 30_multi_strategy_concurrency §3.1 一致）。

> **相关性聚类（correlation clustering）作为行业约束的补充——待裁定（2026-08-10 审查补充）**：行业归类按"申万/中信行业映射"是**静态分类**，但 A 股存在"跨行业高相关"现象（如 2026-07 量化私募集体回撤中，动量/残差波动率/流动性/短期反转因子罕见同向下跌，跨行业标的同步踩踏）。[tierzero](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading) 2026-01 实践：pairwise correlation >0.6 的策略/标的归同一 cluster，cluster 有独立 notional limit（比各成员 limit 之和更紧）。这是"不做完整协方差但做二元相关性判定"的中间方案——只需 pairwise ρ>0.6 判定（O(N²) 但 N 小），不需完整协方差矩阵求逆。
>
> **当前 MVP 不做**：行业约束（按申万/中信归类）已覆盖主要集中度风险，相关性聚类是补充层。待 ① 各策略有 6+ 月实盘 PnL 数据可算 pairwise ρ ② 行业约束实测不足以控制跨行业相关性风险时，评估引入相关性聚类（记入 §5 待裁定）。与 [31号 §3.7](31_position_sizing.md) HRP（完整聚类+递归二分）的区别：相关性聚类是 tierzero 简化版（二元判定 + cluster cap），比 HRP 轻得多
>
> **tierzero 相关性聚类施工参数（2026-08-10 施工流程补充）**：tierzero 2026-01 工程实现的具体参数可供施工参考——① **PnL 向量窗口**：30 日滚动小时 PnL 向量（A 股无小时线可用 30 日日频 PnL 向量降维）；② **聚类阈值**：pairwise ρ > 0.6 归同 cluster（marcelgautsche 2026-06 给出更细分级：<0.4 好 / >0.7 冗余 / 0.4-0.7 灰区，0.6 是灰区中点偏严）；③ **cluster cap**：簇内策略总 notional 上限 = 各成员 limit 之和 × shrinkage_factor（例：3 策略各 30% notional，同簇 shrinkage_factor=0.55 → 簇 cap 50% 而非 90%）；④ **stale snapshot 检测**：position snapshot 而非 delta-from-last（漏消息导致 stale 而非静默累积误差），2 秒 stale 暂停该策略新订单。**与 §2.10.5 演进方向 B 的区别**：tierzero 聚类是"静态归类+簇 cap"（PnL 层），演进方向 B 是"动态 ρ 突变检测+shrinkage"（stress-aware）。两者可叠加：tierzero 聚类做常态分类，突变检测做压力期降级

> **90 天相关性持续高位规则——退化策略淘汰备选（2026-08-10 施工流程补充，youcanbuildthings 2026-05-06 实证）**：[youcanbuildthings Multi Strategy Allocator](https://youcanbuildthings.com/articles/multi-strategy-trading-bot-python)（2026-05-06）给出与 tierzero 聚类（ρ>0.6 同簇）**互补**的退化规则——**"When two strategies have a 90-day rolling correlation above 0.70 for 30 consecutive days. The diversification benefit between them is gone. Running both is just extra brokerage fees and operational drag."** 即：两策略 90 日滚动 ρ 持续 >0.70 达 30 天 → 分散化收益消失 → 应淘汰其一（保留 track record 更优者）。**与 tierzero 聚类的区别**：tierzero 是"检测到高相关→设更紧簇 cap"（降权但仍运行），youcanbuildthings 是"高相关持续 30 天→淘汰其一"（停运）。两者递进——先用 tierzero 簇 cap 降权，若持续高位再淘汰。**施工参数**：① **窗口**：90 日滚动（比 tierzero 30 日更长，捕捉中长期结构性收敛而非短期波动）；② **阈值**：ρ > 0.70（比 tierzero 0.6 更严，0.70 是 marcelgautsche "冗余"线）；③ **持续期**：30 连续日（防短期 ρ 脉冲误判，要求结构性而非瞬时）；④ **淘汰动作**：标记 `degraded=True` + 通知 G14 BudgetChangeHandler 评估是否触发策略退场流程（归 G14 而非 G13 自行停运——G13 只检测+标记，停运决策归 G14 三级升级或策略管理层）。**为何列为备选非 MVP**：① 需 6+ 月实盘 PnL 才有 90 日滚动窗口数据；② 淘汰策略是重大决策，需人工/AI 审查确认非 regime 临时导致；③ 与 §2.10.5 演进方向 C（crowding 信号层检测）互补——crowding 管信号同质化（早期预警），90 天 ρ 管 PnL 兑现后的结构性收敛（晚期确认）

#### 2.5.2 总仓位硬约束

**参数来源**：[31_position_sizing §2.4.3](31_position_sizing.md)——regime Shrinkage 节流后的 12 态上限（80%~5%）+ 2 overlay。

**算法**：总仓位 = sum(所有标的 target_weight)。超上限时等比缩放（pro-rata），保持相对排序：
```python
if total_exposure > total_exposure_cap:
    scale = total_exposure_cap / total_exposure
    for symbol in firm_positions:
        firm_positions[symbol].target_weight *= scale
```

**执行顺序**：单票裁剪 → 行业裁剪 → 总仓位裁剪。从局部到全局，每步只减不增。

> **级联裁剪"每步基于上一步结果"说明（2026-08-10 施工流程补充）**：三级裁剪是**级联（cascading）**关系，非独立并行——每步的输入是上一步的输出，每步只减不增保证单调收敛：
>
> ```
> Step 1: 单票裁剪      输入=kelly_adjusted[symbol]    输出=clipped_1[symbol]（单票≤8%）
> Step 2: 行业裁剪      输入=clipped_1[symbol]         输出=clipped_2[symbol]（行业内按比例削至≤30%/±10%）
> Step 3: 总仓位裁剪    输入=clipped_2[symbol]         输出=clipped_3[symbol]（等比缩放至≤regime_cap）
> Step 4: 现金管理      输入=clipped_3[symbol]         输出=firm_target_portfolio（CASH=1-sum）
> ```
>
> **为什么级联而非独立**：若三级裁剪独立并行（各自从 kelly_adjusted 出发裁剪后取最小），行业裁剪可能削掉某标的 20%，单票裁剪可能削掉同一标的 10%，但两者独立计算后合并会导致归因纠缠——无法区分"被行业裁剪削了多少 vs 被单票裁剪削了多少"。级联设计保证 `cut_ratio` 可追溯：Step 1 的 `cut_ratio` 记录单票裁剪比例，Step 2 在 Step 1 结果上再记行业裁剪比例，Step 3 在 Step 2 结果上再记总仓位裁剪比例。`constraint_checks` 中每级裁剪独立记录 `triggered: bool` + `cut_amount: float`，归因清晰。
>
> **单调收敛保证**：每步只减不增（`clipped_n[symbol] ≤ clipped_{n-1}[symbol]`），最终 `firm_target_portfolio` 的总暴露 ≤ Kelly 后总暴露 ≤ 求和后总暴露。不会出现"裁剪后反而变大"的异常。若任一步裁剪后总暴露已 ≤ regime_cap，后续步骤自动跳过（`triggered=False`）

> **总仓位上限来源**：FirmRiskAggregator 不读 regime 状态，只收到 RegimeMetaAllocator（G15）Shrinkage 后的 budget 数值上限（30_multi_strategy_concurrency §2.2"策略本身不知道市场态，只收到 budget 数字"）。

### 2.6 不做 MVO / 不估协方差 —— 讨论要点 ⑤

**决策**：FirmRiskAggregator 只做求和+裁剪+冲突净额，**不做 MVO，不估协方差矩阵**。

**依据**（30_multi_strategy_concurrency §3.1 已拒绝，本备忘确认执行）：
- 协方差估计在 A 股情绪周期切换时全错（冰点期相关性飙升到 0.8+）
- 优化器放大输入噪声：小幅协方差扰动 → 权重大幅跳动
- 归因纠缠：亏钱时无法区分"策略 alpha 错"还是"优化器权重错"还是"协方差估错"
- AI 能写对优化器代码，但写不出"准确的协方差矩阵"——那是数据+研究问题

**代码印证**：[MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) 依赖仅 `zephyr.position.core.strategy_book`，无 scipy/numpy 优化器依赖，无协方差计算。

### 2.7 输出 firm_target_portfolio 契约 —— 讨论要点 ⑥

**数据结构**（代码已定义 `FirmTargetPortfolio`，[MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) L63-L79）：

```python
@dataclass(frozen=True)
class FirmTarget:
    target_weight: float                 # 裁剪后最终权重
    contributions: dict[str, float]      # {strategy_id: 贡献权重}（归因用）
    cut_ratio: float                     # 被裁剪比例（0=未裁剪，0.2=削了20%）

@dataclass(frozen=True)
class FirmTargetPortfolio:
    firm_positions: dict[str, FirmTarget]    # symbol → FirmTarget（含 CASH）
    total_exposure: float                    # 所有标的 target_weight 之和
    total_budget: float                      # 所有策略 budget 之和
    cash_ratio: float                        # = total_budget − total_exposure
    constraint_checks: dict[str, Any]        # 单票/行业/总仓位检查结果（含是否触发裁剪）
    conflicts_resolved: list[ConflictRecord] # 冲突标的净额处理记录
    degraded: bool                           # 降级标记
    created_at: datetime
    idempotency_key: str
    schema_version: str = "1.0"
```

**契约纪律**：
- `firm_positions` 权重和 + `cash_ratio` = `total_budget`（现金也是一种仓位，31_position_sizing §2.5）
- 显式包含 `CASH` 虚拟标的（`cash_ratio = total_budget − total_exposure`）
- `contributions` 记录每个标的的各策略贡献，供归因审计（自然叠加的可追溯性）
- `cut_ratio` 记录裁剪比例，供复盘（哪个标的被削了多少）
- `constraint_checks` 记录每级裁剪是否触发，供 G14 BudgetChangeHandler 判断是否需三级升级
- 幂等：`idempotency_key` 防重复聚合

**与 MOD-POS-001 的衔接**：两段接口中，`PreKellyResult`（含 `summed_weights`）交 MOD-POS-001 做 Kelly 精裁决（§2.1 步骤②）。MOD-POS-001 消费 `summed_weights[symbol]` 作为 `w_i^sum`（粗仓位求和值），产出 `kelly_adjusted` 后交回 `post_kelly_clip` 做 §2.4 硬上限裁剪，最终产出 `FirmTargetPortfolio`（§2.1 步骤③）。`FirmTargetPortfolio` 是 firm 层最终输出（非 Kelly 输入），交下游下单执行层。

### 2.8 O(N) 复杂度保证 —— 讨论要点 ⑦

**复杂度分析**：

| 步骤 | 复杂度 | 说明 |
|---|---|---|
| ① 按标的求和 | O(N×M) | N 策略 × M 标的，一次遍历 |
| ② 冲突净额 | O(M) | 每标的一次加法 |
| ④ 单票裁剪 | O(M) | 每标的一次比较+缩放 |
| ⑤ 行业裁剪 | O(M) | 行业归类 O(M) + 超限行业缩放 O(M) |
| ⑤ 总仓位裁剪 | O(M) | 求和 O(M) + 等比缩放 O(M) |
| **总计** | **O(N×M)** | N=3-5 策略，M≤50 标的，总计 <250 次操作 |

**为什么 O(N) 不是 O(N²)**：
- **不用优化器**：MVO 需协方差矩阵求逆 O(M³)，自然叠加用加法 O(N×M)（30_multi_strategy_concurrency §2.3）
- **不用投票仲裁**：Model D 投票冲突仲裁是 O(N²) 乃至 O(2^N)（30_multi_strategy_concurrency §3.2），净额处理是 O(M)
- **不用协方差**：行业归类只需权重+行业映射 O(M)，不需协方差矩阵 O(M²)

**N=3-5 策略的规模**：个人系统 3-5 策略，每策略 10-20 标的，M≤50。O(N×M) < 250 次操作，微秒级完成。O(N²) 优化器在此规模下也无性能优势，但引入协方差估计风险。

### 2.9 边界声明（确认不做什么）

| 边界 | 内容 | 依据 |
|---|---|---|
| **不做 MVO / 不估协方差** | 只求和+裁剪+净额，不做 MVO，不估协方差矩阵 | 30_multi_strategy_concurrency §3.1 |
| **不做 Kelly** | Kelly 精裁决归 MOD-POS-001（G12），FirmRiskAggregator 只消费 Kelly 结果做最终裁剪 | 31_position_sizing §2.1 分层裁定 |
| **不做选股** | 选股归 StrategyBook，FirmRiskAggregator 只接收 `StrategyTarget` | 30_multi_strategy_concurrency §2.2 |
| **不做跨策略投票** | 自然叠加替代投票（Model D 已拒绝） | 30_multi_strategy_concurrency §3.2 |
| **不做 budget 分配** | budget 分配归 RegimeMetaAllocator（G15），FirmRiskAggregator 只消费 budget 数字 | 30_multi_strategy_concurrency §2.2 |
| **不做三级升级** | budget 变动的三级升级归 BudgetChangeHandler（G14），FirmRiskAggregator 只记录 `constraint_checks` 供 G14 判断 | 33_budget_change_handler |
| **仓位算法不内置 regime 切换** | 聚合逻辑不随 regime 变；regime 只通过 Shrinkage 缩 budget 间接影响总仓位上限 | 30_multi_strategy_concurrency §2.2 |

### 2.10 选项之外的更好算法（远期演进方向）

> 当前 §2 决策（自然叠加 + 三级硬裁剪 + 冲突净额）是 MVP 施工目标，O(N×M) 简单确定。本节记录 2026 最新研究中**选项之外**的更好算法，作为远期演进方向——非 MVP，重评条件见 §5。本节只写 why（为何是演进方向 / 为何暂缓），how 归施工层（非本备忘职责，[01_design_memo_management_spec §4.3](01_design_memo_management_spec.md)）。

#### 2.10.1 CVaR 作为统一尾部风险度量（替代/增强方差与权重归类）

**当前方案**: §2.5 行业/总仓位裁剪用"持仓权重 + 行业映射"做集中度控制，不估协方差（§2.6 拒绝 MVO）。这是 O(M) 简单方案，但**只管集中度不管尾部形状**——两个相同行业权重的组合，左尾厚度可能差 2 倍（[Man Numeric 2025-07](https://www.man.com/documents/download/81842-e96ab-9099d-e1c10/Numeric_Insights_Covering_Your_Tail%3A_The_Case_for_Expected_Shortfall_in_Tail_Risk_Management_English_%28United_States%29_23-07-2025.pdf) 实证：相同 variance 的两组合 CVaR 差 −1.32% vs −1.78%，"Portfolio Two is much crashier"）。

**CVaR 演进方向**（裁剪后用 CVaR 做组合尾部风险**验证**，非裁剪主算法）:
- **CVaR 是一致性风险度量**（次可加性 / 正齐次 / 单调 / 传递不变），分散化逻辑自洽——VaR 不满足次可加性，两资产组合 VaR 可能 > 各自 VaR 之和（[alcapitaladvisory 2026-07](https://alcapitaladvisory.com/research/frameworks/cvar.html)，Basel III/IV 已用 ES=CVaR 替代 VaR 作为银行内部模型标准）
- **CVaR 显式度量不利结果**: 方差把上行下行对称处理（涨停板=风险），CVaR 只看左尾（Man Numeric 2025-07）——与 A 股打板策略"涨停板是好事"直觉一致（[34号 §3.2.2](34_regime_meta_allocator.md) Sortino 选型同理）
- **CVaR/VaR 比率作为尾部严重度连续指标**: [pooyagolchian 2026-04](https://pooyagolchian.com/blog/portfolio-risk-var-cvar-kelly-criterion-2026/) 实证 ~1.48x（95%），集中组合可 >2.0x——"when bad days happen, they are on average 48% worse than the VaR boundary"。该比率是"尾部比 VaR 阈值严重多少"的连续指标，比本备忘 §2.4-§2.5 二元"是否触发裁剪"信息更丰富，可填入 `constraint_checks` 供 G14 三级升级判断严重度

**与上下游对齐（不重复造轮子）**:
- [31号 §2.3.4](31_position_sizing.md) Kelly 合成规则已含 `cvar_cap_i`（CVaR_95 上限约束，Binding constraint 显式化）——Kelly 层已用 CVaR 做**单标的**上限
- [30号 §2.5](30_multi_strategy_concurrency.md) `drawdown_controller.py`（MOD-POS-008，production）已实现 5 级系统性风险响应 GREEN/YELLOW/ORANGE/RED/BLACK（VaR<2% / 2-4% / 4-6% / >6% / CVaR>10% 驱动 BLACK）——**组合级 CVaR 计算已存在**于 `var_calculator.py`
- **本备忘 G13 的角色**: 消费 `var_calculator.py` 产出的组合 CVaR 作为 `constraint_checks` 的一部分，供 G14 三级升级判断——**不重算 CVaR，只消费**（与 §2.9 边界声明"不做 Kelly/不估 regime，只消费"同构）

**arXiv:2607.00883 四轴诊断**（[Noguer i Alonso & Al-Fallouji 2026-07](https://arxiv.org/pdf/2607.00883v1)）: CVaR 框架把尾部风险视为"跨损失机制的配置问题"（abrupt crash states / volatility repricing / persistent drawdowns 需不同保护），四轴诊断可借鉴为裁剪后验证维度——条件凸性 / 尾部事件可靠性 / 非压力 carry / 回撤持续性。**对本项目**: 当前 §2.5 行业/总仓位裁剪对应"集中度"维度，四轴诊断是更细的"对冲质量"维度——远期可填入 `constraint_checks.tail_quality` 供 G14 判断"裁剪后组合的尾部对冲是否真有效"

**为何列为远期非 MVP**: CVaR 计算需收益分布估计（历史模拟/Monte Carlo/参数法），MVP 用权重+行业映射已覆盖主要集中度风险；`var_calculator.py` 已实现 CVaR 但接入 `constraint_checks` 需上下游接口对齐（记入 §6 待定）；31号 Kelly 层已有 `cvar_cap_i`，firm 层再加 CVaR 验证是**补充层**非必需

#### 2.10.2 MPC 多期预测思路（远期演进方向）

**当前方案**: §2.2 求和是单期静态（当前各策略粗仓位直接相加）；§2.5.2 总仓位上限由 RegimeMetaAllocator（G15）日频 Shrinkage 给出，也是单期。

**MPC 演进方向**（[Nystrup/Boyd/Lindström/Madsen, Annals of Operations Research 2019](https://www.researchgate.net/publication/325874988_Multi-period_portfolio_selection_with_drawdown_control), 2026-06 更新）:
- **核心创新——回撤感知风险厌恶**: 根据已实现回撤动态调整风险厌恶系数——"By adjusting the risk aversion based on realized drawdown, it successfully controls drawdowns with little or no sacrifice of mean–variance efficiency. Using leverage it is possible to further increase the return without increasing the maximum drawdown"
- **多期预测**: 基于多变量 HMM 的多期收益均值/协方差预测，MPC 滚动优化未来 H 期
- **交易/持仓成本作为正则化**: "Transaction and holding costs are discussed as a means to address estimation error and regularize the optimization problem"——成本既是真实支出也是估计误差的正则化手段
- **O(N) 加法替代优化器**: 与本项目 §2.2 自然叠加哲学一致——MPC 不必是 MVO，可以是"多期预测 + 滚动调整 budget"

**对本项目的可借鉴点**（非全盘照搬）:
- **回撤感知的 budget 调整**: 当前 G15 Shrinkage 是 regime 驱动（ConfidenceSignal × RiskSignal），可远期增加"已实现回撤"维度——MaxDD 接近阈值时额外收紧 `global_shrinkage`。与 [30号 §2.5](30_multi_strategy_concurrency.md) Drawdown Protocol 四级阈值呼应，但 MPC 是**连续调整**非阶梯
- **多期预测替代单期**: 当前 G15 是日频单期 Shrinkage，远期可演进为"未来 5-10 日滚动预测"——需 HMM 多期预测模块（[10号](10_regime_detector_spec.md) regime detector 已有 4 态 HMM，可扩展转移矩阵预测）
- **不做全盘 MVO**: MPC 论文本身用 MVO，但本项目 §2.6 拒绝 MVO。可借鉴 MPC 的"滚动 + 回撤感知 + 成本正则化"思想，**用加法+裁剪实现**而非优化器——本质是 G15 Shrinkage 的多期化（与本备忘 §2 职责正交，归 G15 远期）

**为何列为远期非 MVP**: 多期 HMM 预测需 10号 regime detector 扩展（当前 4 态日频，多期需转移矩阵预测）；回撤感知 budget 调整需 6+ 月实盘 PnL 校准回撤-风险厌恶映射；当前 G15 Shrinkage C1 验证已通过（MaxDD +7.36pp 改善，[34号 §3.2.3](34_regime_meta_allocator.md)），MVP 够用

#### 2.10.3 独立风险层解耦（架构原则借鉴，非多 agent 实现）

**RMATS**（[arXiv:2605.25311, Yang et al. 2026-05](https://arxiv.org/html/2605.25311v1)）实证: MaxDD 9.62% vs MVO 15.49% vs FinBERT Sentiment 15.28%。核心架构: 4 specialized agents（Sentiment / Report / Analysis / Risk）由 recursive Manager Agent 协调，迭代反馈至权重收敛（‖w^(r+1)−w^(r)‖₂ < ε=0.008，中位数 2 轮收敛，74.1% 在 2 轮内）。**Risk Agent 独立于策略 agent**，专门做 CVaR 估计（EWMA 动态协方差）+ 地缘压力测试 + 自适应多级断路器（drawdown/地缘/波动率超阈值触发）；奖励函数 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)`，λ₁=0.8 / λ₂=1.5（回撤控制优先）。

**对本项目的架构原则借鉴**（非实现照搬）:
- **FirmRiskAggregator 本就是独立风险层**: §2.9 边界声明已确认"不选股 / 不做 Kelly / 不估 regime"——与 RMATS Risk Agent 独立于策略层**同构**。本备忘的设计已符合"独立风险层"原则，无需额外引入 agent 概念
- **CVaR + 断路器**: RMATS Risk Agent 的 CVaR 估计 + 多级断路器与 [30号 §2.5](30_multi_strategy_concurrency.md) Drawdown Protocol（四级阈值 + Kill Switch）+ 本备忘 §2.1 `degraded` 标记 + [G14 三级升级](33_budget_change_handler.md) 呼应——**本项目已用更轻的"硬阈值 + 三级升级"实现等效功能**
- **递归收敛不借鉴**: RMATS 的递归 Manager Agent 协调（多轮反馈至收敛）是**多 agent 系统**特征，本项目用"求和+裁剪"O(N×M) 一次完成，无需多轮收敛——见 §4.4 过度工程审查

**过度工程审查（RMATS 多 agent 对个人项目过重）**:

| RMATS 组件 | 个人项目是否需要 | 裁定 |
|---|---|---|
| 4 agent（Sentiment/Report/Analysis/Risk） | ❌ 过重 | 个人项目 3-5 策略是"独立 sleeve"非"独立 agent"，StrategyBook 已含选股逻辑，无需 LLM agent 重复 |
| 递归 Manager Agent 协调 | ❌ 过重 | O(收敛轮数 × agent 数) + LLM 调用成本；本项目求和+裁剪 O(N×M) 一次完成，无需多轮收敛 |
| HMM regime 分类 | ✅ 已有 | [10号](10_regime_detector_spec.md) regime detector 已实现 4 态 HMM |
| Kalman 信号融合 | ❌ 远期 | 策略层信号融合归 G05 信号工厂，非 G13 职责 |
| CVaR 估计（EWMA 动态协方差） | ✅ 已有 | `var_calculator.py`（MOD-POS-008，production）已实现 |
| 多级断路器 | ✅ 已有 | [30号 §2.5](30_multi_strategy_concurrency.md) Drawdown Protocol 四级阈值 + Kill Switch |
| 地缘压力测试 | ⚠️ 部分已有 | A 股地缘风险通过 D-SIGNAL-68 overlay（[10号](10_regime_detector_spec.md)）+ RiskSignal 13 参数（[34号](34_regime_meta_allocator.md)）已部分覆盖 |

**结论**: RMATS 的**架构原则**（独立风险层 + CVaR + 断路器）本项目已用更轻的方式实现；RMATS 的**多 agent 实现**（4 agent + 递归 Manager + LLM）对个人项目过重，不借鉴。MaxDD 9.62% 的成绩主要来自 CVaR + 断路器（本项目已有等效机制）而非多 agent 协调本身——印证 [charter §3 约束五"少而精"](../../04_architecture_principles_decisions/system_charter.md)：个人项目用 O(N×M) 加法 + 硬阈值 + 三级升级，不上多 agent 系统

#### 2.10.4 Quarter Kelly 与硬裁剪的协同印证

**pooyagolchian 2026-04 实证**: Quarter Kelly（0.25×）78% 仓位 CAGR 10.8% MaxDD −22%，对比 Full Kelly 312% CAGR 18.2% MaxDD −62%——"Quarter Kelly delivers 85% of full Kelly's growth with only 35% of the drawdown"。

**与本项目的协同印证**（已在上下游对齐，非新决策）:
- [31号 §2.3.1](31_position_sizing.md) Kelly 公式已用**半 Kelly**（[浙商证券 2026-07-27](http://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/838481485080/index.phtml) A 股实证背书：半 Kelly 在 A 股高波动环境风险收益比更优）——比 Quarter Kelly 激进一档，但 A 股实证支持
- 本备忘 §2.4 单票 8% 硬上限 + §2.5.2 总仓位上限是 Kelly 之后的**兜底裁剪**——即使 Kelly 算出某标的 15%，8% 硬上限也会削到 8%
- **Quarter Kelly 经验值印证硬上限必要性**: Quarter Kelly 78% 总仓位 MaxDD −22%，与本项目总仓位上限（regime Shrinkage 后 9%~80%，[34号 §3.2.3](34_regime_meta_allocator.md)）+ 单票 8% 同量级——硬裁剪是 Kelly 分数之外的**额外安全网**，两者叠加才把 MaxDD 压到可接受区间
- **CVaR/VaR 比率与 Kelly 分数的互补**: Kelly 决定"下多少注"（基于均值/方差），CVaR 验证"下注后尾部多厚"（基于完整分布）——两者维度正交，本备忘 §2 裁剪（权重域）+ 31号 Kelly（密度域）+ var_calculator CVaR（尾部域）形成三层防御

#### 2.10.5 相关性管理演进（minimax + 突变检测 + crowding 信号层 + PCA/CorrDD 结构层）

> **2026-08-10 八次审查补充**：全网搜索 2026-08-08 最新 portfolio aggregation/firm risk 算法发现相关性管理演进方向，均非 MVP 但为远期/Phase 3 候选。八次审查补 A/B/C 三条，十次审查补 E（PCA/CorrDD 结构层）+ F（MINGLE 因子图）两条，共五条。

**当前方案**: §2.5 相关性聚类待裁定（pairwise ρ>0.6 → 同 cluster → cluster cap），源自 tierzero 2026-01 工程实现。这是**局部二元判定**——只看两两 ρ 是否超阈值，不考虑全局最坏情况依赖。

**演进方向 A——AEGIS Minimax Correlation（全局最坏情况依赖最小化）**:

[AEGIS](https://arxiv.org/abs/2604.09060)（Chakraborty/Singh BIT Mesra, arXiv:2604.09060, 2026-04-13）三层架构的第二层是 **Minimax Correlation Algorithm**——不找"相关性高的剔除"（局部），而是"构造使最大两两相关性最小的子集"（全局）。2006-2025 walk-forward：CAGR 15.41%, MaxDD 28.89%（同期 S&P 500 MaxDD>50%，标准动量 2008 单年 −42.58%）。

| 维度 | 当前 pairwise ρ>0.6（局部） | AEGIS minimax（全局） |
|---|---|---|
| 目标 | 找高相关对，归 cluster，设 cluster cap | 最小化 max(ρ_ij)，构造最分散子集 |
| 复杂度 | O(N²) pairwise + 聚类 | O(N²) + minimax 优化 |
| 优势 | 简单、工程实现轻（tierzero 已验证） | 理论上更稳健——不遗漏"三三组合高相关但两两不高"的隐性集中 |
| 劣势 | 局部视角，可能遗漏高阶集中 | 小规模（3-5 策略 × 10-20 标的）minimax 优化噪声大，与 RARE 评估同源顾虑 |

**评估**: minimax 是比 pairwise ρ>0.6 **更优的理论方向**，但 A 股 3-5 策略小规模下参数噪声大（与 RARE regime-conditional CVaR risk parity 同源问题——小规模需估条件协方差双参数噪声）。**记为 Phase 5+ 远期候选**，重评条件：策略数 >8 且标的数 >50（与 HRP-μ 远期候选条件同步，§3.7/31号 §3.7）

**演进方向 B——相关性突变检测层（stress-aware shrinkage，轻量 Phase 3 候选）**:

[Bayes Group 2026-03](https://www.bayes-group.com/insights/march-shock-multistrat-resilience) 分析 2026-03 地缘冲击（美伊升级+布伦特 $119+关税裁决）：Millennium/Point72 各亏 ~$1.5B，Citadel ~$1B。核心教训："**diversification illusion**"——正常期低相关的 pod（rates RV vs equity vol）在共同宏观冲击下 **tail correlation 飙升**。恢复最快的平台是**实时动态相关性监控**（而非静态 pod 级 limit）。

**对本项目的轻量改进**: 自然叠加 + pro-rata clipping 属于"静态聚合"（§2.2 求和不考虑相关性突变），可增加一个轻量级**相关性突变检测层**：
```
滚动 short-window（5 日）pairwise ρ_short vs long-window（60 日）ρ_long
若 |ρ_short − ρ_long| > 阈值（如 0.3）→ 相关性突变 → 对叠加权重做 shrinkage
shrinkage_factor = 1 − α × max(0, |ρ_short − ρ_long| − threshold)
```
这比直接上 MARCD（§2.10.1 CVaR + §2.10.3 RMATS）**轻得多**——只需滚动 pairwise ρ 计算（已有数据）+ 一个 shrinkage 因子，不需训练 diffusion/HMM/优化器。**记为 Phase 3 候选**（首批策略 3 月实盘后，有 PnL 数据可校准 ρ 突变阈值）

**演进方向 B 的学术严谨版——Bayesian 动态收缩先验（理论背书远期候选）**: 上述 short/long window ρ 偏离度是工程启发式，缺理论保证。[arXiv:2605.06818](https://arxiv.org/abs/2605.06818)（Coulson/Matteson/Wells, Cornell, 2026-05-07）提出 **Dynamic Correlation Matrices with Shrinkage Priors**——低秩因子表示 + 动态收缩先验（latent state innovation variance 在结构突变时自适应增大）+ multivariate factor stochastic volatility，**首次给出动态正则化 Bayesian 模型的 posterior contraction 结果**（averaged Hellinger distance 下显式收敛速率）。相比 rolling window/EWMA（平滑掉突变）和 DCC（低维参数化限制），动态收缩先验在金融压力期"突然局部 shift"场景下适应性更强。**与演进方向 B 的关系**：short/long window ρ 偏离度是"检测突变→shrinkage"的工程版，Bayesian 动态收缩先验是"检测突变→shrinkage"的理论严谨版（有 posterior contraction 保证）。**为何记为远期非 Phase 3**：① Bayesian 低秩因子 + 动态收缩先验工程远比滚动 ρ 重（需 MCMC/VI 推断）；② 小规模（3-5 策略）pairwise ρ 参数少，工程启发式够用，Bayesian 框架优势在中大规模才显现；③ 收敛速率理论保证对个人项目实盘价值有限（个人项目不需学术发表级保证）。**重评条件**：策略数 >8 且 simple short/long window 实测漏检率高时评估升级到 Bayesian 框架

**演进方向 C——BlackRock crowding 警示：相关性聚类延伸到信号特征层**:

[BlackRock Spring 2026 Hedge Fund Outlook](https://hedgeco.net/news/04/2026/blackrock-issues-crowding-warning-for-hedge-funds.html)（2026-04-16）：多策略 pod shop 表面分散，实则因共享数据/模型/宏观叙事而 **crowding**——压力期 hidden correlation 突变，可能"violent unwind"。反馈环：亏损→pod 触限→减仓→价格下行→更多 stop-loss→同步卖出。**AI 驱动策略加剧收敛**。

**对 100% AI 项目的特殊警示**: 单一 AI 开发者会让多策略**天然收敛于相似信号**——crowding 风险比多开发者场景更隐蔽。当前 §2.5 相关性聚类是 **PnL 层**（策略收益相关性），应远期延伸到**信号特征层**（多策略 raw signal 相关性）：
- **Phase 3 候选**: 计算 3-5 策略的 raw signal（选股得分/仓位建议方向）pairwise 相关性，若 >0.6 → 标记"信号同向"→ pro-rata clipping 时**优先削减同 cluster 内信号相似度最高的策略**（而非等比例削减）
- **与 AI Agent Flash Crash 的呼应**: [33号 §3.2.3](33_budget_change_handler.md) 已引 2026-03-11 23 个 AI agent 47 秒 $500M 闪崩——多 AI agent 独立决策但收敛于相似信号 = crowding 极端形态。信号层相关性检测是"不等 PnL 兑现就预警"的前置防线

**为何列三条为远期非 MVP**:
- AEGIS minimax: 小规模参数噪声大，需策略数/标的数显著增加
- 相关性突变检测: 需首批策略 PnL 数据校准阈值（Phase 3）
- 信号层 crowding: 需策略 raw signal 接口标准化（当前 §2.7 FirmTargetPortfolio 只含 holdings 权重，不含 signal 特征）——属 G05 信号工厂职责延伸，非 G13 独立可做

**过度工程审查**: 三条远期演进均**不引入 MVO/协方差/优化器**（与 §2.6 拒绝 MVO 一致），只是在现有 O(N×M) 求和+裁剪框架上叠加"相关性感知 shrinkage 因子"，复杂度增量可控。MVP 用 §2.5 pairwise ρ>0.6 聚类已覆盖主要集中度风险，三条远期是"精度提升"非"功能补缺"

**演进方向 E——GinkGO PCA 共同因子暴露预警 + CorrDD 回撤尾部同步检测（结构层补充，Phase 3 候选）**:

> **2026-08-10 十次审查补充**：§2.10.5 演进方向 A/B/C 分别管"全局最坏情况依赖"（minimax）、"压力期相关性突变"（short/long window ρ）、"信号层 crowding"（raw signal 相关性）。但三者均未覆盖**共同因子暴露**（多策略被同一宏观/风格因子驱动，pairwise ρ 可能不高但 PCA 第一主成分方差解释比极高）和**回撤尾部同步**（正常期 ρ 低但回撤期同步踩踏，pairwise ρ 被"正常期多数样本"稀释）。GinkGO 框架（[Kaoruha 2026-05 GitHub issue](https://github.com/kaoruha/ginkgo/issues)）给出两个互补维度填补此空白，与 [31号 §3.7](31_position_sizing.md) HRP 评估中已引的 PCA 第一主成分预警同源。

**① PCA 共同因子暴露预警（GinkGO 框架核心层）**:
```
输入：N 策略的 T 日 PnL 向量矩阵 R ∈ ℝ^{N×T}
步骤：
  1. 计算策略 PnL 相关矩阵 C = corr(R) ∈ ℝ^{N×N}
  2. PCA 特征值分解：C = V Λ V^T，Λ = diag(λ_1 ≥ λ_2 ≥ ... ≥ λ_N)
  3. 第一主成分方差解释比：VE_1 = λ_1 / Σ λ_i
  4. Herfindahl 集中度指数：H = Σ (λ_i / Σ λ_j)²  （H∈[1/N, 1]，H→1 单因子主导）
预警判据（任一触发→标记 degraded 供 G14 评估）：
  - VE_1 > 50%  → 共同因子暴露过高（多策略被同一隐藏因子驱动，分散化假象）
  - H > 0.4     → 组合集中度异常（单因子贡献 40%+ 方差，N=5 策略时 H_等权=0.2）
```
**与演进方向 A/B/C 的区别**：minimax（方向 A）管"两两 ρ 最坏情况"，PCA 管"N 策略被同一因子驱动"——即使所有 pairwise ρ<0.6，若 VE_1>50% 仍说明多策略共享同一隐藏 beta（如 2026-07 量化私募因子共振：动量/残差波动率/流动性/短期反转 pairwise ρ 不一定 >0.6，但同被"量化拥挤"因子驱动）。PCA 是**全局结构检测**，pairwise ρ 是**局部二元检测**，互补非替代。**复杂度**：PCA 分解 O(N³)，N=3-5 策略 <125 次操作，微秒级，轻量。

**② CorrDD 回撤尾部同步检测（GinkGO 框架尾部层）**:
```
输入：N 策略的回撤序列 DD_i = {dd_i(t)} t=1..T （dd_i(t) = max峰值至 t 的回撤）
步骤：
  1. 计算回撤相关矩阵 CorrDD(i,j) = corr(DD_i, DD_j)
  2. 筛选 CorrDD(i,j) > 0.7 的策略对（回撤尾部高度同步）
预警判据：
  - 任一策略对 CorrDD(i,j) > 0.7 → 回撤同步风险高（正常期 PnL ρ 可能低，但回撤期同跌）
  - 回撤同步策略对数 / 总策略对数 > 50% → 系统性回撤风险（多数策略回撤同步）
```
**与演进方向 B（short/long window ρ 突变检测）的区别**：方向 B 管"PnL 相关性突变"（ρ_short vs ρ_long 偏离），CorrDD 管"回撤序列相关性"——两者检测对象不同：PnL ρ 被"正常期多数样本"稀释（99% 正常日 + 1% 回撤日，ρ 被正常期主导），CorrDD 只看回撤序列捕捉**尾部同步**（与 [30号 §2.5](30_multi_strategy_concurrency.md) Drawdown Protocol 的回撤域对齐）。**实证支撑**：2026-03 地缘冲击（[Bayes Group 2026-03](https://www.bayes-group.com/insights/march-shock-multistrat-resilience)）正是"正常期低相关 pod 回撤期 tail correlation 飙升"——CorrDD 是比 PnL ρ 更早预警此类"diversification illusion"的指标。**复杂度**：CorrDD 计算 O(N²×T)，N=5 策略 T=60 日 <1500 次操作，毫秒级，轻量。

**施工参数（Phase 3 候选）**：① **PnL 窗口 T**：60 日滚动（与 §2.5 tierzero 聚类 30 日 PnL 向量 + [34号](34_regime_meta_allocator.md) PerformanceScore 60 日 Sharpe 窗口对齐）；② **PCA 预警阈值**：VE_1 > 50%（GinkGO 默认）+ H > 0.4（N=5 等权 H=0.2，0.4 = 2× 等权集中度）；③ **CorrDD 预警阈值**：>0.7（与 §2.5.1 90 天相关性淘汰规则 ρ>0.70 同阈值，marcelgautsche "冗余"线）；④ **降级动作**：标记 `degraded=True`（PCA/CorrDD 触发作为第 8/9 项 degraded 条件，第 6=HBI/CSAD、第 7=华泰金工风格拥挤度）+ 通知 G14 评估是否触发"簇内 shrinkage"（对 VE_1 贡献最大的策略降权）。**为何列为 Phase 3 非 MVP**：① 需 6+ 月实盘 PnL 才有 60 日滚动窗口数据；② PCA/CorrDD 是"结构层预警"非"裁剪算法"——MVP §2.4-§2.5 三级裁剪 + §2.10.5 A/B/C 已覆盖主要风险，PCA/CorrDD 是"检测隐藏结构"的增强层；③ 与 [31号 §3.7](31_position_sizing.md) HRP 远期候选 + §2.10.5 A/B/C 重评同步（策略数 >8 且标的数 >50 时全面评估相关性管理升级）

**过度工程审查（演进方向 E）**：PCA 分解 O(N³) + CorrDD 计算 O(N²×T) 均不引入协方差矩阵求逆/MVO/优化器（与 §2.6 拒绝 MVO 一致）——PCA 是**特征值分解**非**协方差求逆优化**，只用于"检测共同因子暴露"非"优化权重"。N=3-5 策略规模下 PCA/CorrDD 计算量 <2500 次操作，毫秒级，轻量。Phase 3 引入不算过重，但 MVP 用 pairwise ρ>0.6 聚类（§2.5 待裁定）已覆盖主要集中度风险，PCA/CorrDD 是"结构精度提升"非"功能补缺"

**Absorption Ratio 经典基线背书 + 2026 实证验证 + VRC Fragility Score 理论参照（2026-08-10 二十一次审查补充）**：上述 GinkGO PCA 的 VE_1（第一主成分方差解释比）本质是 **Absorption Ratio**（[Kritzman/Li/Page/Rigobon 2010 "Principal Components as a Measure of Systemic Risk"](https://www.researchgate.net/publication/315429088_Principal_Components_as_a_Measure_of_Systemic_Risk)）的特例——Absorption Ratio 定义为"前 k=N/5 个特征向量解释的总方差比例"，捕捉市场紧密耦合程度（tightly coupled markets → negative shocks propagate more quickly and broadly）。VE_1 是 k=1 的 Absorption Ratio。**2026 实证验证**：[Hammond 2026-05 "Geometric Observables for Financial Regime Detection"](https://www.researchgate.net/publication/404738503_Geometric_Observables_for_Financial_Regime_Detection) 在 17 个危机窗口（2000-2024）面板上比较 46 种检测方法，**Absorption Ratio（d=0.80）是最强经典基线**（量子启发几何观测 Reduced State Purity d=0.83 排第一但 |ρ|≈0.13 与经典通道不相关可互补，Berry Phase Rate d=0.72 OOS 中位数最高 9/5 危机窗口得分最高）。**对本项目的校准启示**：① GinkGO PCA 的 VE_1 > 50% 阈值有 Absorption Ratio 经典文献背书（非经验拍脑袋），Hammond 2026 实证进一步确认 PCA 特征值集中度是危机检测最可靠的经典指标；② 量子启发几何观测（QCML Hilbert 空间嵌入 + Berry Phase Rate + Spectral Entropy + Reduced State Purity + Hamiltonian Sensitivity）属 Phase 5+ 远期（工程重需 spectral metric learning + 小规模策略数 3-5 时优势不显著 + 9/5 危机窗口 OOS 优势需更大样本验证），不纳入 MVP/Phase 3；③ [Verma 2026-04 "Detecting Market Fragility Through Correlation Breakdown Analysis"](https://pub-637293d6914e45b8a4a3cbe29e1637c1.r2.dev/WMJ-JESD-144-Detecting-Market-Fragility-Through-Correlation-Breakdown-Analysis-Theory-Quantitative-Measurement-and-Hedge-Fund-Implementation.pdf) 提出 **VRC Fragility Score**（DCC 动态条件相关 + MST 最小生成树拓扑 + Absorption Ratio + 因子相关性 + 跨资产背离 + 隐含 vs 实现相关性价差 + 网络连通性 7 组件合成），核心论点 **"correlation breakdown is not a consequence of crisis, it's the mechanism through which crisis propagates"**（相关性崩溃不是危机的后果，而是危机传导的机制）——为本项目 §2.10.5 A/B/C/E/F 多层相关性管理提供**理论背书**：tierzero ρ>0.6（常态分类）+ 90 天规则（结构性收敛淘汰）+ GinkGO PCA/CorrDD（隐藏因子+尾部同步）三层架构正是"检测相关性崩溃机制"的工程落地。**但 VRC 7 组件合成对个人项目属过度工程**（多组件+专有复合指标+需 DCC/MST/隐含相关性数据），本项目三层已覆盖核心需求，VRC 仅作理论参照不施工

**演进方向 F——MINGLE 因子图相关性聚类（远期 P4+ 候选，2026-08-10 十次审查补充）**:

[arXiv:2608.06618](https://arxiv.org/abs/2608.06618)（Beyond Co-Movement: Locality by Exposures Enables a Joint Factor-Graph Framework，2026-08-06）提出 **MINGLE**——ADMM 联合学习隐因子暴露 + 策略间图拓扑结构，优于纯相关性聚类。核心创新：不只检测"策略间相关性"（pairwise ρ / PCA），而是同时学习"策略被哪些隐因子驱动"（因子图）+ "策略间图拓扑关系"（邻接矩阵），两者联合优化。

**与现有 A/B/C/E 的关系**：
- vs 方向 A（AEGIS minimax）：minimax 管"两两 ρ 最坏情况"，MINGLE 管"隐因子+图拓扑联合结构"——MINGLE 是 minimax 的因子图泛化
- vs 方向 E（GinkGO PCA+CorrDD）：PCA 管"共同因子暴露"（单维度），MINGLE 管"隐因子+图拓扑"（双维度联合）——MINGLE 是 PCA 的图结构扩展，能捕捉 PCA 遗漏的"因子间交互拓扑"

**为何记为 P4+ 远期非 Phase 3**：① ADMM 联合优化工程重（需交替迭代收敛，非 PCA 一次分解），个人项目 3-5 策略规模下现有 A/B/C/E 已覆盖主要相关性风险；② MINGLE 的优势在中大规模策略组合（>10 策略）才显著，小规模下隐因子+图拓扑参数噪声大（与 AEGIS minimax 小规模噪声问题同源）；③ 论文 2026-08-06 刚发布，缺乏足够实盘验证。**重评条件**：策略数 >8 且 A/B/C/E 实测漏检率高时评估升级到 MINGLE 因子图框架

**演进方向 E 的理论根基——Copula 尾部依赖（CorrDD 的理论背书，P4+ 远期候选，2026-08-10 十一次审查补充）**:

> 演进方向 E 的 CorrDD（回撤序列相关性）是检测"尾部同步"的**工程实用方案**，但其理论基础是 **Copula 尾部依赖**（[metricgate 2026-06](https://metricgate.com/blogs/copula-dependence-portfolio-risk/) + Sklar 定理）。核心洞察：**相关性度量平均共动，Copula 决定尾部发生什么**——两个组合可以有完全相同的相关矩阵，却因 Copula 族不同而有截然不同的联合崩盘概率。

**① Gaussian vs t-Copula 的尾部依赖差异**：
```python
# 相同相关矩阵 ρ，不同 Copula 族的 lower-tail dependence λ_L
Gaussian Copula:  λ_L = 0   （无论 ρ 多高，极端共跌概率→0）
t-Copula(ν, ρ):   λ_L = 2·t_{ν+1}(-√((ν+1)(1-ρ)/(1+ρ)))  > 0  （ν越小尾部越厚）

# 含义：Gaussian Copula 系统性低估组合级崩盘概率（2008 CDO 定价教训）
#       t-Copula 在危机期资产同跌概率有界非零，更贴近 A 股尾部同步实况
```

**② 为何 CorrDD 是 Copula 思想的工程轻量替代**：完整 Copula 拟合需 ① 估计各策略边际分布 ② 选择 Copula 族（Gaussian/t/Clayton/Gumbel）③ 拟合参数（MLE/IFM）④ 检验拟合优度——对个人项目 3-5 策略规模工程过重且参数噪声大。CorrDD（corr(DD_i, DD_j)）直接用回撤序列的二阶矩捕捉"尾部同步"，无需边际分布假设、无需 Copula 族选择、无需参数拟合，是 Copula 尾部依赖思想的**非参数无分布替代**。与方向 B（short/long window ρ 突变）互补：方向 B 管"PnL 相关性突变"，CorrDD 管"回撤尾部同步"。

**③ 为何记为 P4+ 理论背书非 Phase 3 施工**：Copula 拟合属 Phase 4+ 鲁棒性阶段（与 [10号 §3 G02](10_regime_detector_spec.md) HSMM/Student-t HMM 同期的尾部建模深化），CorrDD 已在 Phase 3 覆盖实用需求。**重评条件**：当 CorrDD 实测漏检"尾部同步但回撤序列平稳"的隐蔽风险时（罕见），或策略数 >8 需多变量 Copula 联合建模时，评估升级到 t-Copula 尾部依赖系数 λ_L 的显式拟合。与 [31号 §2.3.1 Taleb 胖尾论点](31_position_sizing.md) 同源——两者均论证"线性相关性/方差在厚尾场景失效"，31号管单标的 Kelly 仓位层，本条管多策略组合相关性层

#### 2.10.6 单策略集中度上限 + 市场拥挤度检测 + 风格拥挤度（2026-08-10 九次审查补充）

> 全网搜索 2026-08-08 最新 firm risk aggregator/portfolio hard limit 实践发现三个当前缺失的维度：① 单策略集中度上限（FLOX 2026-05）② 市场拥挤度检测（HBI/CSAD，laoyulaoyu 2026-07 + BlackRock 2026-04 实证）③ 风格拥挤度检测（华泰金工 2026-08 动量+成交量双维度分域）。均非 MVP 但为 Phase 3 候选。

**演进方向 D-1——单策略集中度上限（FLOX max_concentration_pct）**:

[FLOX-Foundation/flox PR#183](https://github.com/FLOX-Foundation/flox/pull/183)（2026-05-07）四条组合层风控规则之一是 **max_concentration_pct**——**单策略占总 gross 暴露的比例上限**（仅一个策略有 gross 时抑制其独占）。本项目当前有单票 8%（标的维度）/ 行业 30%（行业维度）/ 总仓位 80%（全局维度）三层硬限，但**缺"单策略占总仓位上限"维度**——若打板策略一次出 5 个信号且都命中 8% 单票上限，该策略占总仓位 40%，组合风险集中于单一策略 alpha 来源。

**与 §2.10.5 演进方向 C（BlackRock crowding 信号层）的区别**：crowding 是"多策略信号同质化"风险（策略间），单策略集中度是"单一策略独占仓位"风险（策略内+策略对组合的占比）。两者正交——crowding 检测信号相似度，集中度上限管仓位占比。

**施工参数参考**：FLOX 默认 max_concentration_pct=0.35（单策略≤35% 总 gross）。本项目 3-5 策略，候选值 30-40%（3 策略时每策略≤33% 天然等权，5 策略时≤40% 允许优势策略略多配）。**Phase 3 候选**：首批策略 3 月实盘后，若实测某策略频发独占>35% 仓位，评估引入单策略集中度上限作为 §2.4 单票裁剪之后的第四级裁剪（级联关系：单票→行业→总仓位→单策略集中度）。

**演进方向 D-2——HBI/CSAD 市场拥挤度检测（O(N) 纯价格，A 股可落地）**:

[laoyulaoyu 羊群行为六法](https://laoyulaoyu.com/index.php/2026/07/01/羊群行为（从众心理）的量化检测：六种方法识别市场过度拥挤信号/)（2026-07-01）给出两个 **O(N) 纯价格计算**的拥挤度指标，完全符合本项目"不估协方差"原则：

| 指标 | 公式 | 信号 | 复杂度 |
|---|---|---|---|
| **HBI（羊群行为指数）** | `HBI = |个股均收益 − 基准均收益| / |基准均收益|` | HBI<0.3 极端一致性（群体陷阱，unwind 风险高）→ 降仓；HBI>2.0 统计异常（独立机会）→ 加仓 | O(N) |
| **CSAD（横截面绝对偏差）** | `CSAD = mean(|个股收益 − 市场均收益|)` | 低 CSAD=羊群（风险区）；高 CSAD=独立决策（机会区） | O(N) |

**与 §2.10.5 演进方向 C 的协同**：BlackRock crowding 警示（2026-04）+ Pomegra 实证（2026-06 Goldman AI 动量 100th 百分位→当日高 beta 动量篮子跌 8%）印证 crowding 风险真实存在。演进方向 C 是"策略信号层 crowding 检测"（需 raw signal 接口，归 G05），HBI/CSAD 是"市场层拥挤度检测"（纯价格数据，A 股可直接算）。**HBI/CSAD 可作为 firm 层 degraded 标记的第 6 项触发条件**：HBI<0.3（市场极端一致性）时标记 degraded → G14 三级升级评估降仓（与 §2.10.5 演进方向 B 相关性突变检测互补——突变检测管策略间 ρ，HBI/CSAD 管市场整体羊群度）。

**为何列为 Phase 3 非 MVP**：① HBI/CSAD 需校准 A 股基准（中证全指/沪深 300）+ 历史 HBI 分位数阈值（60 日/120 日），首批策略实盘前无校准数据；② 单策略集中度上限需首批策略 track record 确认"独占>35%"是否频发；③ 两者均是"精度提升"非"功能补缺"——现有 §2.4-§2.5 三级裁剪 + §2.10.5 相关性管理已覆盖主要集中度风险，HBI/CSAD + 单策略集中度是压力期增强层

**过度工程审查**：HBI/CSAD 是 O(N) 纯价格计算（只需个股收益+基准收益），不引入协方差/优化器/MVO；单策略集中度是 O(M) 比例检查（各策略 gross 求和÷总 gross），同 §2.4 单票裁剪复杂度。两者均轻量，Phase 3 引入不算过重。MVP 用现有三级裁剪 + 相关性聚类（§2.5 待裁定）已够，HBI/CSAD + 单策略集中度是实盘 3 月后的增强候选

**演进方向 D-3——华泰金工风格拥挤度（A 股本土校准，动量+成交量双维度）**:

> **2026-08-10 十次审查补充**：§2.10.6 演进方向 D-2 的 HBI/CSAD 是"市场羊群行为"检测（个股 vs 基准收益离散度），但未覆盖**风格拥挤**（某风格因子被过度拥挤后的反转风险）。A 股有成熟的本土风格拥挤度模型——华泰金工风格拥挤度（动量+成交量双维度分域模型），比 HBI/CSAD 更精准定位"哪种风格在拥挤"，可指导 G14 三级升级时"降哪个策略的仓"。

**华泰金工风格拥挤度模型**（[华泰证券金工 2026-08](https://m.hibor.com.cn/wap_detail.aspx?id=5dc71a9949bce52f3398c30caaf270dd) 机构级实证）：
```
输入：A 股全市场个股的动量因子值 + 成交量因子值
步骤：
  1. 按动量得分分域：高动量组（Top 20%）/ 中动量组 / 低动量组（Bottom 20%）
  2. 按成交量得分分域：高成交组 / 中成交组 / 低成交组
  3. 计算各分域的拥挤度得分 = 该域内个股数的时序百分位（相对 60 日/120 日历史分布）
  4. 风格拥挤度指标：
     - 小盘拥挤度 = 低动量 + 低成交域的个股数占比百分位
     - 大盘拥挤度 = 高动量 + 高成交域的个股数占比百分位
预警判据（任一触发→标记 degraded 供 G14 评估降仓方向）：
  - 小盘拥挤度 > 90% 分位 → 小盘风格高度拥挤（unwind 风险，降小盘策略仓）
  - 大盘拥挤度 < 10% 分位 → 大盘风格极度冷清（资金撤离，降大盘策略仓）
  - 持续期确认：上述条件需连续 20 日维持（防短期脉冲误判）
```

**与 §2.10.6 D-2（HBI/CSAD）的协同**：HBI/CSAD 是"市场整体羊群度"（O(N) 纯价格，回答"市场是否一致"），华泰金工是"风格层拥挤度"（动量×成交量双维度分域，回答"哪种风格在拥挤"）。两者递进——HBI/CSAD 先检测"市场是否拥挤"（HBI<0.3 极端一致性），华泰金工再定位"哪个风格拥挤"（小盘>90% / 大盘<10%），指导 G14 三级升级时**定向降仓**（降拥挤风格的策略而非等比例降所有策略）。**与 §2.10.5 演进方向 C（BlackRock crowding 信号层）的区别**：crowding 管策略信号同质化（策略间），华泰金工管市场风格拥挤（风格间），两者正交。

**施工参数（Phase 3 候选）**：① **分域窗口**：动量/成交量得分用 20 日滚动计算（与 [20 §2.3](20_first_batch_strategies.md) 因子 IC 衰减监控窗口同量级）；② **历史分位数窗口**：60 日 / 120 日双窗口（60 日近期 + 120 日中长期交叉验证）；③ **预警阈值**：小盘 >90% 分位 / 大盘 <10% 分位（华泰金工默认，极端尾部预警）；④ **持续期**：连续 20 日（防短期脉冲，与 §2.5.1 90 天相关性淘汰规则的 30 连续日同源思路但更短——风格拥挤比策略相关性变化更快）；⑤ **降级动作**：标记 `degraded=True` + 通知 G14 评估"定向降仓"（降拥挤风格对应的策略，如小盘拥挤→降打板/小市值策略，大盘冷清→降大盘动量策略）。**为何列为 Phase 3 非 MVP**：① 需 A 股全市场个股动量+成交量数据（[D-FACTOR](../battle_map/battle_map_05_stock_selection.md) 因子工厂已 production，数据可得但需新增分域计算模块）；② 风格拥挤度需 6+ 月历史数据校准分位数阈值；③ 是"定向降仓精度提升"非"功能补缺"——MVP 用 HBI/CSAD（D-2）+ 三级裁剪已覆盖主要拥挤风险，华泰金工是"定位哪个风格拥挤"的增强层

**过度工程审查（演进方向 D-3）**：华泰金工风格拥挤度是 O(N) 分域统计（按动量/成交量分组+百分位计算），不引入协方差/优化器/MVO。与 HBI/CSAD（D-2）同复杂度量级，Phase 3 引入不算过重。MVP 用 HBI/CSAD + 三级裁剪已够，华泰金工是实盘 3 月后"定向降仓"的增强候选

#### 2.10.7 Fassino 风险预算 Cauchy 不动点 —— Phase 4 远期候选

> **v1.0.15 新增**：§3.4 拒绝了"协方差感知聚合（风险预算优化）"因需估协方差矩阵 + 辅助优化问题。2026-03 最新研究提出 Cauchy 不动点构造法——通过 Cauchy 序列直接构造风险预算组合，避免辅助优化问题，并证明解的存在唯一性，为 §3.4 拒绝理由提供远期突破路径。

**算法**（[Fassino 2026-03](https://arxiv.org/abs/2603.17415)，"Risk Budgeting Portfolios via Cauchy Fixed Point"）：

- **核心创新**：传统风险预算组合（Spinu 2013 / Maillard et al. 2010）需求解辅助优化问题 `min_w 1/2 w^T Σ w - Σ_i b_i log(w_i)`（凸优化），Fassino 用**Cauchy 序列不动点迭代**直接构造解：
  1. **不动点映射**：定义映射 `T(w) = diag(Σw)^{-1/2} × b / ||diag(Σw)^{-1/2} × b||`，风险预算组合是 T 的不动点 `w* = T(w*)`
  2. **Cauchy 序列构造**：从任意初始 `w_0`（如等权）出发，迭代 `w_{k+1} = T(w_k)`，Fassino 证明 `{w_k}` 是 Cauchy 序列（`||w_{k+1} - w_k|| → 0`），故收敛到不动点 `w*`
  3. **存在唯一性证明**：在 Σ 正定条件下，T 是压缩映射（contraction mapping），由 Banach 不动点定理直接推出存在唯一性——无需辅助优化问题的 KKT 条件分析

- **与 §3.4 拒绝理由的关系**：
  | 维度 | §3.4 拒绝的风险预算优化 | Fassino Cauchy 不动点 |
  |---|---|---|
  | 求解方式 | 辅助优化问题（凸优化求解器） | 不动点迭代（矩阵乘法 + 归一化） |
  | 存在性证明 | KKT 条件 + 凸性 | Banach 不动点定理（压缩映射） |
  | 协方差需求 | 完整 Σ 矩阵 | 完整 Σ 矩阵（同） |
  | 计算复杂度 | O(N³) 优化 + 迭代 | O(N²) per iteration × K 次迭代 |
  | 实现复杂度 | 需凸优化库（cvxpy/scipy.optimize） | 纯矩阵运算（numpy 足够） |

  §3.4 拒绝风险预算的两理由（① 需估协方差 ② 辅助优化复杂）中，Fassino 直接解决②（不动点迭代替代凸优化），但①仍成立——仍需完整 Σ 矩阵。即 Fassino 降低了求解复杂度但未消除协方差估计需求。

- **与 §2.6 不做 MVO/不估协方差的关系**：§2.6 明确"不做 MVO / 不估协方差——O(N) 加法替代 O(M³) 优化器，等价于永远稳定的等权 risk-budget 优化器"。Fassino 仍需 Σ 矩阵，与 §2.6 核心原则冲突——但 Fassino 的价值在于**当 §2.10.5 相关性管理演进到需估 pairwise ρ 时**（Phase 3+），Cauchy 不动点提供了比凸优化更轻量的风险预算求解路径。即：Fassino 不是让现在就做风险预算，而是为"未来若要做风险预算"提供更优求解算法。

- **与 31号 §3.9 Tepelyan 多元 Kelly sigmoid 标度律的关系**：Tepelyan 解决 multivariate Kelly 的 O(2^N)→O(N) 计算突破（仅需 pairwise ρ），Fassino 解决风险预算的凸优化→不动点迭代求解突破（需完整 Σ）。两者都是"被拒绝算法的计算复杂度突破"——Tepelyan 突破 Kelly 的组合爆炸，Fassino 突破风险预算的优化复杂度。Tepelyan 需 pairwise ρ（更轻量），Fassino 需完整 Σ（更重），两者代表"协方差估计深度"的两个层级。

- **优势**：① **无需优化求解器**——纯矩阵运算 + 迭代，numpy 即可实现，无 cvxpy 依赖；② **Banach 不动点定理保证**——压缩映射自动保证收敛 + 存在唯一性，比 KKT 条件分析更简洁；③ **O(N²) per iteration**——比凸优化 O(N³) 更轻量；④ **可解释性**——不动点迭代 `w_{k+1} = T(w_k)` 每步物理含义明确（用边际风险贡献重归一化权重）

- **为何列为 Phase 4 远期非 MVP**：
  1. **仍需完整 Σ 矩阵**：与 §2.6 "不估协方差"核心原则冲突，Phase 4 评估的前提是 §2.10.5 相关性管理演进已建立 pairwise ρ 估计能力（Phase 3），且策略数扩展到 8+ 使协方差估计的边际价值超过其噪声风险
  2. **当前等权 risk-budget 已足够**：§2.6 论证"自然叠加等价于永远稳定的等权 risk-budget 优化器"，O(N) 加法在 3-5 策略小规模组合中与完整风险预算差异微弱
  3. **Σ 估计噪声风险**：A 股 regime 转折时 Σ 不稳定（§3.4 拒绝理由③），Fassino 虽降低求解复杂度但不解决 Σ 估计噪声——garbage in garbage out

- **重评条件**：① §2.10.5 相关性管理演进（A/B/C/E/F 方向）上线后，pairwise ρ 估计稳定运行 ≥6 月；② 策略数扩展到 8+ 使等权 risk-budget 与真实风险预算差异显著；③ 实盘 ≥1 年后 Σ 估计窗口稳定性验证通过；④ 最小集成路径：先对 Top-5 策略做 Fassino 风险预算 vs 等权对比回测，验证边际收益后再扩展

**过度工程审查（演进方向 D-4 Fassino）**：Fassino Cauchy 不动点迭代是 O(N²) 矩阵运算（Σw 矩阵向量乘 + 归一化），不引入凸优化求解器/MVO/多 agent。计算轻量但**仍需完整 Σ 矩阵**——与 §2.6 核心原则冲突，故列为 Phase 4 远期（非 Phase 3），前提是相关性管理演进已建立 Σ 估计能力。MVP 用自然叠加（等权 risk-budget）已够，Fassino 是"未来若做风险预算"的更优求解算法储备。

#### 2.10.8 Kakinaga & Umeno MFCCA 多重分形组合配置 —— Phase 4 远期候选

> **v1.0.17 新增**：§2.10.7 Fassino 用 Cauchy 不动点解决风险预算的"求解复杂度"问题但仍需 Σ 矩阵。2026-08-05 最新研究（[Kakinaga & Umeno 2026-08 arXiv:2608.04987](https://arxiv.org/abs/2608.04987)，"Portfolio Allocation under Heterogeneous Scales and Multifractality"）提出更激进的方案——**用 MFCCA 符号波动函数替代方差/协方差风险泛函**，从根本上消除 Σ 估计需求，为 §3.4 拒绝风险预算理由①"需估协方差"提供远期突破路径。注意：此为 [36号 §4.13](36_var_es_monitoring.md) Kakinaga 2026-08 MFCCA **方法论文**（arXiv:2608.03968）的**组合应用论文**（同第一作者，不同 arXiv ID，前者建方法后者建应用）。

**算法**（[Kakinaga & Umeno 2026-08-05](https://arxiv.org/abs/2608.04987)）：
- **核心创新**：用 MFCCA 的**有符号波动函数** `F_xy(q, s)` 替代均值-方差配置中的方差/协方差风险泛函——`s` 为时间尺度，`q` 为波动阶数
  1. **符号保留**：标准 MF-DXA 用 `|F_xy(q,s)|`（绝对值）丢失交叉相关方向；MFCCA 用 `F_xy(q,s)`（有符号），同向运动与反向运动组件以**相反符号**贡献风险——更符合"对冲降低组合风险"的经济学直觉
  2. **多尺度**：`s` 参数允许在不同时间尺度（日/周/月）分别建模相关性结构——短尺度捕获微结构噪声，长尺度捕获基本面共同因子
  3. **q=2 退化为均值-方差**：当 `q=2` 时 MFCCA 风险泛函退化为尺度依赖的均值-方差（scale-dependent mean-variance），即 MV 是 MFCCA 在 `q=2` 的特例——MFCCA 是 MV 的严格推广
  4. **多分形谱**：广义 Hurst 指数 `h_xy(q)` 随 q 变化说明交叉相关具有多分形特征（不同幅度波动的相关结构不同），单一 ρ 无法捕获此异质性

- **实证收益**：Kakinaga & Umeno 在多资产组合上实证，MFCCA 配置 vs 均值-方差配置：
  - 在每个 required return 水平上，MFCCA 配置的 **VaR / ES / MaxDD 均更低**（in-sample + out-of-sample）
  - 关键贡献是**符号保留**而非"在波动阶数上聚合"——保留方向信息是尾部风险降低的主因

- **与 §3.4 拒绝理由的关系**：
  | 维度 | §3.4 拒绝的风险预算 | Fassino Cauchy 不动点（§2.10.7） | Kakinaga MFCCA 配置（§2.10.8） |
  |---|---|---|---|
  | 协方差需求 | 完整 Σ | 完整 Σ | **无 Σ 需求**（用 F_xy 替代） |
  | 风险泛函 | `w^T Σ w` | `w^T Σ w` | `Σ_ij w_i w_j F_ij(q, s)` |
  | 求解方式 | 凸优化 | 不动点迭代 | 凸优化（但泛函更鲁棒） |
  | 突破点 | - | 求解复杂度② | 协方差需求① + 风险泛函非平稳 |

  §3.4 拒绝风险预算的三理由中，Kakinaga 直接解决①（无 Σ 需求，用 F_xy 替代），间接缓解③（Σ 估计噪声——F_xy 的多尺度结构对 regime 转折更鲁棒），但②（辅助优化复杂度）仍成立——MFCCA 配置仍是凸优化。即 Kakinaga + Fassino 组合可同时解决①②（MFCCA 泛函 + Cauchy 求解）。

- **与 [36号 §4.13](36_var_es_monitoring.md) MFCCA 方法的关系**：36号 §4.13 登记 MFCCA 作为"协方差矩阵 regime 转变的非参数检测层"（输入诊断），32号 §2.10.8 登记 MFCCA 作为"组合配置的风险泛函替代"（输出决策）。两者正交——36号用 MFCCA 诊断 Σ 是否稳定，32号用 MFCCA 替代 Σ 进入配置。完整远期演进路径：先 36号 §4.13 检测 Σ regime 转变 → 若转变频繁则 32号 §2.10.8 用 MFCCA 替代 Σ → 配合 §2.10.7 Fassino 不动点求解。

- **为何列为 Phase 4 远期非 MVP**：
  1. **F_xy 估计噪声**：MFCCA 需估计多尺度多阶数的波动函数，参数空间比 Σ 更大（s × q 二维网格），3-5 策略小规模组合下 F_xy 估计噪声可能超过其鲁棒性收益
  2. **MVP inverse-vol 已够**：[31号 §2.2.2](31_position_sizing.md) inverse-vol 只估 σ（1 参数/标的）已被 2026 实证确认为"最鲁棒的轻量配置"，MFCCA 是"协方差感知"的更复杂版本——只在策略数扩展到 8+ 且相关性管理需求显现时引入
  3. **多尺度参数调优**：`s` 和 `q` 的选择需策略 track record 积累后用实盘数据校准，MVP 阶段无校准依据

- **重评条件**：① §2.10.5 相关性管理演进上线后，pairwise ρ 估计稳定运行 ≥6 月且发现 ρ 不稳定（regime 转折频繁）；② 策略数扩展到 8+；③ [36号 §4.13](36_var_es_monitoring.md) MFCCA 检测层已上线，证实 Σ regime 转变显著；④ 最小集成路径：先对 Top-5 策略用 q=2（退化为 MV）做 MFCCA vs inverse-vol 对比回测，再扩展到 q≠2 多分形

**过度工程审查（演进方向 D-5 Kakinaga MFCCA）**：MFCCA 配置仍是凸优化（无 MVO/多 agent），但 F_xy 的多尺度多阶数参数空间比 Σ 更大——故列为 Phase 4 远期（与 Fassino 同期），前提是 36号 §4.13 MFCCA 检测层已建立 F_xy 估计能力。MVP 用 inverse-vol（31号 §2.2.2）已够，Kakinaka 是"未来若 Σ 不稳定到需替代"的更鲁棒泛函储备。

#### 2.10.9 Hsieh & Gan Certified Wasserstein DRO LP —— Phase 5+ 远期候选

> **v1.0.17 新增**：§2.6 拒绝 MVO 部分原因是"优化器放大输入噪声"——Wasserstein DRO（Distributionally Robust Optimization）理论上可对冲此风险（在分布不确定性集合上做最坏情况优化），但传统 Wasserstein DRO 计算成本高，难以扩展到大资产数。2026-08-07 最新研究（[Hsieh & Gan 2026-08-07 arXiv:2608.07032](https://arxiv.org/abs/2608.07032)，"Certified High-Dimensional Wasserstein Robust Portfolio Optimization"，National Tsing Hua University）提出**多项式规模 LP 逼近**，将 Wasserstein DRO 从"理论优雅但不可计算"变为"可计算且可扩展到 1000 资产"，为 §2.6 "不估协方差"原则提供远期突破路径。

**算法**（[Hsieh & Gan 2026-08-07](https://arxiv.org/abs/2608.07032)）：
- **核心创新**：用支撑超平面 majorize 效用函数 + 对偶化支撑子问题，将半无穷凸规划转化为有限超平面对偶 LP（在 1-范数 ground metric 下）
  1. **效用超平面 majorize**：对凹效用函数 U(w^T r) 用支撑超平面线性上界近似 `U(w^T r) ≈ inf_k {a_k(w^T r) + b_k}`，将非线性效用转化为 LP 约束
  2. **对偶化支撑子问题**：Wasserstein 球内的最坏情况期望 `sup_{Q: W_p(Q,P_n)≤ε} E_Q[U(w^T r)]` 通过对偶化转化为有限 LP 子问题
  3. **统一逼近误差证书**：给出 robust value 误差 + 近优 gap 的统一上界——**证书化（certified）**意味着算法不仅输出解还输出误差上界，可验证解的质量
  4. **多项式规模**：LP 规模 O(N × K)（N 资产 × K 超平面数），可扩展到 1000 资产

- **实证规模**：Hsieh & Gan 在 476 资产月度再平衡组合上验证，扩展到 1000 资产仍可解——传统 Wasserstein DRO 通常限于 <50 资产

- **与 §2.6 "不估协方差"原则的关系**：
  | 维度 | §2.6 拒绝的 MVO | 传统 Wasserstein DRO | Hsieh Certified LP（§2.10.9） |
  |---|---|---|---|
  | 协方差需求 | 完整 Σ | 完整 Σ（或场景集） | **场景集**（经验分布 P_n） |
  | 噪声对冲 | 无（点估计） | Wasserstein 球对冲 | Wasserstein 球对冲 |
  | 计算复杂度 | O(N³) | 半无穷规划（不可扩展） | 多项式 LP O(N × K) |
  | 误差证书 | 无 | 无 | **有**（统一逼近上界） |

  §2.6 拒绝 MVO 的核心是"优化器放大输入噪声"——Wasserstein DRO 通过在分布不确定性集合上优化最坏情况，理论上对冲了输入噪声。Hsieh 的 LP 逼近使此对冲可计算。即 Hsieh 不解决"协方差估计需求"（仍需场景集），但解决"优化器放大噪声"——通过 Wasserstein 球显式建模分布不确定性。

- **与 §2.10.7 Fassino + §2.10.8 Kakinaga 的关系**：三者代表"协方差/风险泛函"演进的三个层级：
  - **Fassino（§2.10.7）**：保持 `w^T Σ w` 风险泛函 + Cauchy 不动点求解——降低求解复杂度但泛函不变
  - **Kakinaga（§2.10.8）**：用 F_xy 替代 `w^T Σ w` + 凸优化求解——泛函更鲁棒但求解不变
  - **Hsieh（§2.10.9）**：用 Wasserstein 球对冲分布不确定性 + LP 求解——同时改进泛函鲁棒性（DRO）和求解可扩展性（LP）

  三者可叠加：Fassino 不动点可用于 Kakinaga F_xy 泛函的求解；Hsieh Wasserstein 球可用于 Kakinaga F_xy 的 DRO 对冲——但叠加复杂度过高，Phase 5+ 评估时择一或择二组合。

- **为何列为 Phase 5+ 远期非 MVP/Phase 4**：
  1. **过度工程风险高**：Wasserstein DRO + LP 逼近 + 误差证书是三层抽象，对 3-5 策略小规模组合属典型过度工程——MVP inverse-vol 已被实证为最鲁棒轻量配置
  2. **场景集构建成本**：Hsieh 需经验分布 P_n（场景集），3-5 策略 × 60 日窗口 = 300 场景，场景数远少于 476 资产月度场景——LP 规模优势不显现
  3. **DRO 保守性**：Wasserstein 球半径 ε 的选择是 DRO 的核心难题——ε 过大过度保守（最优解接近等权），ε 过小退化为点估计，A 股 regime 转折时 ε 校准困难
  4. **理论优雅但实证不足**：Hsieh 论文侧重计算方法，A 股实证缺乏——需 Phase 4 先用 Kakinaga/Fassino 验证协方差感知配置的边际收益，再考虑 DRO 对冲

- **重评条件**：① §2.10.7 Fassino + §2.10.8 Kakinaga 已上线且证实协方差感知配置显著优于 inverse-vol；② 策略数扩展到 10+ 且资产数扩展到 50+（LP 规模优势显现）；③ Wasserstein 球半径 ε 的校准方法成熟（如 cross-validation 或 bootstrap）；④ 最小集成路径：先对 Top-10 策略做 Hsieh DRO vs Kakinaga MFCCA 对比回测，验证 DRO 对冲的边际收益

**过度工程审查（演进方向 D-6 Hsieh Certified Wasserstein DRO LP）**：Hsieh LP 仍是多项式凸优化（无 MVO/多 agent），但 Wasserstein DRO + LP 逼近 + 误差证书三层抽象对 MVP/Phase 4 属过度工程。列为 Phase 5+ 远期（晚于 Fassino/Kakinaga），仅当协方差感知配置（§2.10.7/§2.10.8）证实边际收益显著且策略/资产规模扩展到 LP 优势显现时评估。MVP 用 inverse-vol 已够。

## 3. 考虑过的替代方案（拒绝理由）

### 3.1 firm 层统一 MVO 优化器 —— 拒绝
- **拒绝理由**（30_multi_strategy_concurrency §3.1）：统一 MVO 需协方差矩阵（5000×5000），是研究课题不是工程任务；协方差估计在 A 股情绪周期切换时全错；优化器放大输入噪声；归因纠缠
- **采用自然叠加**：O(N) 加法替代 O(M³) 优化器，等价于永远稳定的等权 risk-budget 优化器

### 3.2 单票裁剪按策略优先级截断 —— 拒绝
- **拒绝理由**：优先级是 meta-参数（按 Sharpe？按 PnL？按 budget？），需回测/调参/衰减监控，是技术债；优先级截断让低优先级策略"被抹零"，归因失真
- **采用按比例削**（pro-rata clipping）：保持各策略相对贡献不变，归因公平，无 meta 参数，O(1) per symbol

### 3.3 冲突标的按优先级仲裁 —— 拒绝
- **拒绝理由**（30_multi_strategy_concurrency §3.2 拒绝 Model D 同理）：优先级仲裁是 O(N²) 乃至 O(2^N) 复杂度；投票权重是 meta-参数需调参
- **采用净额处理**：O(M) 加法，A 股不能做空时净额 < 0 截断为清仓（max(0, net − current_holdings)）

### 3.4 协方差感知聚合（风险预算优化） —— 拒绝
- **拒绝理由**：需估协方差矩阵，与 30_multi_strategy_concurrency §3.1 拒绝协方差一致
- **采用权重求和+硬上限**：只需持仓权重+行业映射，不估协方差；行业约束按权重归类求和（O(M)），不需协方差

## 4. 上限定义

### 4.1 系统上限
- 3-5 个 StrategyBook → 1 个 FirmRiskAggregator → 1 个 MOD-POS-001
- FirmRiskAggregator 处理标的数 M ≤ 50（个人系统规模），O(N×M) < 250 次操作
- 硬上限参数全部消费 G12（31_position_sizing §2.4），不自定义

### 4.2 演进路径

| 阶段 | 内容 | 触发条件 |
|---|---|---|
| **MVP** ✅ 已完成（2026-08-12 核对） | 求和+冲突净额+单票/行业/总仓位裁剪 | ~~本备忘定稿即可施工~~ → **已施工 production（2026-08-10，MOD-POS-021 v1.0.0，651 行，0 处 NotImplementedError）** |
| **阶段 2** ✅ 已完成（2026-08-12 核对） | `aggregate()` 拆分为 `pre_kelly_aggregate()` + `post_kelly_clip()`，与 MOD-POS-001 Kelly 衔接 | ~~MOD-POS-001 Kelly 精裁决施工完成~~ → **拆分已实现**（§2.1 v1.0.20 确认；MOD-POS-001 `position_sizing_engine.py` 881 行 production 在位） |
| **阶段 3** ⏳ 代码就绪/文档待重建 | `constraint_checks` 与 G14 BudgetChangeHandler 三级升级联动 | ⚠️ 33_budget_change_handler 在 2026-08-11 git 灾难中内容丢失回退骨架 v0.1.0（原 v2.x 定稿内容 git 历史无记录，待重建）；**代码侧已就绪**——budget_change_handler.py（MOD-POS-022）production v1.0.0，接口契约暂以代码 docstring 为真源 |

### 4.3 为何这是上限而非妥协
- Citadel/Millennium 的 pod 模型本质就是 A（独立账本 + firm 风险聚合），**firm 层只做求和+裁剪，不做 MVO**（30_multi_strategy_concurrency §4.3）
- 3-5 策略的 MVO 收益 < 3-5 策略独立加总收益，因为协方差估计误差 > MVO 理论增益
- 真正的上限 = 在 A 框架内把自然叠加 + 三级硬裁剪做到极致，而不是在 firm 层堆优化器
- O(N) 聚合是 A 模型最被低估的优点——用加法替代优化器（30_multi_strategy_concurrency §2.3）

### 4.4 过度工程审查（2026-08-10）

| 组件 | 是否过重 | 裁定 |
|---|---|---|
| **行业硬约束（±10%/绝对 30%）** | ⚠️ 需评估 | **不过重**。2026 实证（[tierzero](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading) 2026-01："common mistake is to set limits only at layer 1 and assume aggregation takes care of itself"——只设策略级限制不够，须有组合级硬限；[algovestiq](https://www.algovestiq.com/learn/answers/how-to-size-stock-positions) 2026-05：行业基准"20-25% per sector"）。A 股板块轮动风险高（情绪周期驱动行业轮动），行业约束是必需风控不是过度工程。执行只需权重+行业映射 O(M)，不需协方差 |
| **总仓位硬约束（12 态+2 overlay）** | ✅ 合适 | regime Shrinkage 节流后的数值上限，FirmRiskAggregator 只消费数字不估 regime（30 §2.2）。O(M) 等比缩放，非过重 |
| **冲突净额处理** | ✅ 合适 | O(M) 加法，A 股不能做空时净额<0 截断为清仓。比优先级仲裁 O(N²) 简单且无 meta 参数 |
| **按比例裁剪（非优先级截断）** | ✅ 合适 | O(1) per symbol，确定性算法无 meta 参数。归因公平 |
| **求和（自然叠加）** | ✅ 合适 | O(N×M) 加法，A 模型核心优点。替代 O(M³) MVO 优化器 |
| **RMATS 式多 agent 协调（4 agent + 递归 Manager + LLM）** | ❌ 过重 | §2.10.3 已审：个人项目 3-5 策略是独立 sleeve 非独立 agent；递归收敛 O(轮数×agent 数) + LLM 成本 vs 本项目 O(N×M) 一次完成。RMATS 的 MaxDD 9.62% 主要来自 CVaR + 断路器（本项目已有等效：`var_calculator.py` + 30号 Drawdown Protocol），非多 agent 本身。**不借鉴实现，只借鉴"独立风险层"架构原则**（FirmRiskAggregator 已符合） |
| **CVaR 裁剪后验证层** | ⚠️ 远期非过重 | §2.10.1 已审：CVaR 是一致性度量优于方差，`var_calculator.py` 已 production。但接入 `constraint_checks` 需上下游接口对齐（§6 待定），MVP 用权重+行业映射已覆盖集中度风险。列为远期演进非 MVP |

**结论**：FirmRiskAggregator 整体不过重。所有操作都是 O(N×M) 以内的加法/比较/缩放，无优化器、无协方差、无 meta 参数。行业硬约束是 A 股板块轮动风险的必需风控（tierzero 2026-01 印证组合级硬限必要性），非过度工程。真正的过重是 MVO/协方差/投票仲裁（均已拒绝 §3）+ RMATS 式多 agent 协调（§2.10.3 拒绝）。CVaR 验证层是合理远期演进非过重，但需上下游对齐后引入。

## 5. 待裁定（暂缓项）

> 以下项目暂不施工，**非永久禁止**。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **冲突标的优先级仲裁** | MVP 用净额处理（O(M)）；优先级仲裁（按策略 Sharpe/PnL 排序）是 O(N²) 且需 meta 参数 | 策略数显著增加（>8）且净额处理不足；有 6+ 月实盘 track record 可量化优先级 |
| **协方差感知行业约束** | MVP 行业约束按权重归类求和（O(M)）；协方差感知（因子模型+shrinkage）可更精准但需估协方差 | 协方差估计方案成熟（因子模型+shrinkage 验证有效），与 30_multi_strategy_concurrency §3.1 重评协方差同步 |
| **动态单票上限（按流动性/市值自适应）** | MVP 固定 8%（总资金口径）；动态上限（小市值/低流动性更严）增加复杂度 | 31_position_sizing §5 单票口径统一后评估 |
| **相关性聚类（correlation clustering）作为行业约束补充** | MVP 行业约束按申万/中信静态归类（O(M)）；相关性聚类（pairwise ρ>0.6 → 同 cluster → cluster cap，tierzero 2026-01）是"不做完整协方差但做二元相关性判定"的中间方案，可覆盖跨行业高相关风险（如 2026-07 量化私募因子共振跨行业踩踏）。需各策略 6+ 月 PnL 数据算 pairwise ρ | ① 各策略 6+ 月实盘 PnL 数据可算 pairwise ρ ② 行业约束实测不足以控制跨行业相关性风险 ③ 与 31号 §3.7 HRP 远期候选重评同步 |
| **CVaR 裁剪后验证层**（§2.10.1） | MVP §2.5 行业/总仓位裁剪用"权重+行业映射"只管集中度不管尾部形状；CVaR 是一致性度量（次可加性）可验证裁剪后组合尾部风险。`var_calculator.py`（MOD-POS-008）已 production 实现组合 CVaR，31号 §2.3.4 Kelly 层已有 `cvar_cap_i`——但 firm 层接入 `constraint_checks` 需上下游接口对齐 | ① `var_calculator.py` 输出接口与 `constraint_checks` 对齐（§6 待定）② 31号 Kelly 层 `cvar_cap_i` 与 firm 层 CVaR 验证的职责边界明确（单标的 vs 组合级，不重复）③ 实盘 6+ 月验证 CVaR 验证层是否提供权重裁剪之外的增量信息 |
| **MPC 多期预测 / 回撤感知 budget**（§2.10.2） | MVP §2.2 求和是单期静态，§2.5.2 总仓位上限由 G15 日频单期 Shrinkage 给出；MPC（Nystrup/Boyd 2019）的"已实现回撤动态调整风险厌恶 + 多期 HMM 预测"可连续调整 budget 而非阶梯。但需 10号 regime detector 扩展多期转移矩阵 + 6+ 月实盘校准回撤-风险厌恶映射 | ① 10号 regime detector 支持 H 期转移矩阵预测 ② G15 Shrinkage 实盘显示单期节流不足（MaxDD 超阈值频发）③ 与 30号 §2.5 Drawdown Protocol 四级阈值的"连续 vs 阶梯"重评同步（MPC 是 Drawdown Protocol 的连续化远期形态） |
| **单策略集中度上限 + HBI/CSAD 拥挤度检测 + 华泰金工风格拥挤度 + PCA/CorrDD 结构层**（§2.10.6 + §2.10.5 E） | MVP 有单票 8%/行业 30%/总仓位 80% 三层硬限，但缺"单策略占总仓位上限"维度（FLOX max_concentration_pct=0.35，D-1）；HBI/CSAD 是 O(N) 纯价格市场羊群度检测（HBI<0.3 极端一致性→降仓，HBI>2.0 独立机会→加仓，可作 degraded 第 6 项触发，D-2）；华泰金工风格拥挤度是动量+成交量双维度分域模型（小盘>90%/大盘<10% 分位预警，可作 degraded 第 7 项触发+定向降仓，D-3）；PCA 第一主成分 VE_1>50% 预警共同因子暴露+CorrDD>0.7 回撤尾部同步检测（可作 degraded 第 8/9 项触发，§2.10.5 E）。四者均 O(N)/O(M)/O(N³) 轻量不引入协方差求逆/MVO | ① 首批策略 3 月实盘后确认"单策略独占>35% 仓位"频发 ② HBI/CSAD + 华泰金工校准 A 股基准+历史分位数阈值 ③ PCA/CorrDD 需 6+ 月 PnL 数据 ④ 与 §2.10.5 A/B/C 相关性聚类重评同步（策略数 >8 且标的数 >50 时全面评估） |

## 6. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| ~~`aggregate()` 拆分为 `pre_kelly_aggregate()` + `post_kelly_clip()`~~ | 本备忘 §2.1 代码现状与设计意图 | ✅ **已完成**（2026-08-10 施工 + v1.0.20 文档确认，2026-08-12 核对源码在位）：两段接口已实现并由 `aggregate()` 便捷入口串联 Kelly passthrough，MOD-POS-001 `position_sizing_engine.py`（881 行 production）在位。本行关闭 |
| 单票 8% vs 5% 三层口径统一（MOD-POS-001/010/021） | 31_position_sizing §2.4.1 / §5 | 待 G04 首批策略产出后统一 |
| `constraint_checks` 与 G14 三级升级的接口契约 | 本备忘 §2.7 / 33_budget_change_handler | ⚠️ 33 号在 2026-08-11 git 灾难中内容丢失回退骨架 v0.1.0（原"v2.9.0 已定稿"内容 git 历史无记录，待重建）。**当前接口契约临时真源** = `budget_change_handler.py`（MOD-POS-022，production v1.0.0，572 行）头部 docstring（INVARIANTS/TierLevel/TierState/收敛检测三条件）+ 本备忘 §2.7 `constraint_checks` 字段定义；33 号重建后本行版本引用回填 |
| 行业映射数据源（申万一级/中信一级） | 本备忘 §2.5.1 | 待 D-FACTOR 行业分类模块确认 |
| **dead-band filter（再平衡死区）归属评估** | 本备忘 §2.2（finlab/quant-portfolio 实践） | **评估结论：不属 G13 范围**。dead-band filter（weight change <阈值不执行再平衡，避免交易成本超信号收益）是执行层机制，属 G14 BudgetChangeHandler（防抖阈值，~~[33号](33_budget_change_handler.md) §6 已登记 budget 变动防抖~~ ⚠️ 33 号骨架化内容丢失，防抖机制现以 `budget_change_handler.py` docstring"日内<5% 忽略/日间累计>10% 强制触发"为真源）或 buy/sell_flow（最小交易阈值）。G13 只管求和+裁剪产出 FirmTargetPortfolio，不管"是否执行再平衡交易"。finlab 用 <2% 阈值，quant-portfolio 用"交易成本超信号收益"判定——具体阈值待 G14 校准。[arXiv:2605.01176v3](https://arxiv.org/html/2605.01176v3)（2026-06）SPO portfolio 的 partial adjustment（δ<1，只闭当前→目标差距的 δ 比例）是 dead-band 的连续版，同属执行层非 G13 |
| **lot 对齐 / 最小交易单位裁剪后归属** | [33号 §3.2.3](33_budget_change_handler.md)（lot 对齐导致收敛偏差） | **评估结论：不属 G13 裁剪算法**。G13 §2.4-§2.5 裁剪产出**权重域** FirmTargetPortfolio（浮点权重）；lot 对齐（A 股 100 股最小交易单位，向下取整）是**执行层** buy/sell_flow（[41号](41_buy_flow.md)/[42号](42_sell_flow.md)的职责）。~~33号 §3.2.3 已注~~ ⚠️ 33 号骨架化后该注记丢失，原意保留于此："lot 对齐导致实际暴露略高于 new_budget，偏差 <1 个 lot 通常 <0.1%，远小于防抖阈值 5%，若累积超限 firm 层 32号兜底裁剪"——即 G13 裁剪用浮点权重，lot 偏差由执行层吸收，G13 仅在累积超限时重新裁剪 |
| **Kelly pro-rata 归一化与 firm 层总仓位裁剪的交互**（防重复缩放） | [31号 §2.3.5](31_position_sizing.md)（Kelly 层 pro-rata）+ 本备忘 §2.5.2（总仓位裁剪等比缩放） | **需对齐**：31号 §2.3.5 在 Kelly 层做 pro-rata 归一化（sum(f_i^final) > 总仓位上限时按比例缩放），本备忘 §2.5.2 总仓位裁剪也做等比缩放。两者可能叠加导致**双重缩放**。施工时须明确：① Kelly 层 pro-rata 用 Kelly 后的 sum vs Kelly 层总仓位上限（可能 = regime_cap）② firm 层 §2.5.2 用裁剪后 sum vs regime_cap ③ 两者口径一致则 Kelly 层 pro-rata 后 firm 层总仓位裁剪自动不触发（`triggered=False`），不会双重缩放。数据流：`pre_kelly_aggregate → MOD-POS-001 Kelly（含 §2.3.5 pro-rata）→ post_kelly_clip（§2.5.2 总仓位裁剪，若 Kelly 已 pro-rata 则跳过）` |
| **CVaR 接口对齐（var_calculator → constraint_checks）** | 本备忘 §2.10.1 / [30号 §2.5](30_multi_strategy_concurrency.md)（var_calculator.py MOD-POS-008） | **待对齐**：`var_calculator.py` 已 production 实现组合 VaR/CVaR，但输出格式未接入本备忘 `constraint_checks`。施工时须定义：① `constraint_checks.tail_risk` 字段结构（VaR_95/CVaR_95/CVaR_VaR_ratio/tail_quality 四轴）② 调用时机（post_kelly_clip 后调用 var_calculator 验证，非裁剪主算法）③ 与 30号 §2.5 drawdown_controller 5 级响应的关系（drawdown_controller 消费同源 CVaR 做分级响应，G13 只记录不重复计算） |
| **pre_kelly_aggregate / post_kelly_clip 幂等性与重入** | 本备忘 §2.1（两段接口） | **待定义**：`idempotency_key` 已在 FirmTargetPortfolio 字段（§2.7），但两段拆分后幂等语义需明确——① pre_kelly 与 post_kelly 是否共享同一 idempotency_key ② 若 MOD-POS-001 Kelly 失败重试，post_kelly_clip 是否需重新调用 pre_kelly_aggregate（答案：否，pre_kelly 结果可缓存，Kelly 重试用同 PreKellyResult）③ 幂等窗口（如日内同 idempotency_key 返回缓存结果） |
| **⚠️ P0：StrategyBook→FirmRiskAggregator 接口字段名三方漂移** | 2026-08-12 代码核对（[30号 §2.2](30_multi_strategy_concurrency.md) 接口契约②已同步标注） | **断裂风险**：代码真源 `TargetPortfolio`（strategy_book.py L102-119）字段为 `positions: dict[str, TargetWeight]` + `budget`；而本备忘伪代码与 `firm_risk_aggregator.py._sum_by_symbol`（L386-394）按 `target_portfolio` / `budget_used` duck-typing 取值——**直接传入 TargetPortfolio 对象会静默取空默认值（`getattr(tp, "target_portfolio", {})` → `{}`），聚合产出全现金组合且不报错**。且 `positions` 值是 `TargetWeight` 对象（含 target_weight/reason/confidence）非裸 float，即使字段名对齐也需取 `.target_weight`。**修复方向**（归代码施工，非本备忘）：① `_sum_by_symbol` 适配 `TargetPortfolio`（读 `positions`/`budget` + 取 `.target_weight`）或 ② 定义显式适配层（TargetPortfolio→dict 转换器）；修复后须补"传 TargetPortfolio 对象"路径的回归测试（原 54 测试疑似只覆盖 dict 输入路径） |
| **T+1 可卖持仓口径假设** | 本备忘 §2.3 净额截断（`max(0, net+current_holdings)`） | **口径假设未明示**：`current_holdings` 假设全部可卖，但 A 股 T+1 下今日买入部分不可卖——若快照含今日买入部分需区分"可卖/冻结"。净额截断若按全量 holdings 计算，极端场景会允许"卖出超过可卖量"的意愿进入下游（执行层 [42号](42_sell_flow.md) sell_flow 兜底）。归执行层职责，但本备忘须明示口径假设：`current_holdings` 应为 **T+1 口径可卖权重**（昨持仓−今日已卖），数据供给方（持仓对账/`position_reconciler`）需按此口径供数 |
| **测试文件丢失重建**（2026-08-11 git clean 灾难，#ARCH-GIT-CLEAN-GUARD-FIX） | 代码头部 [TESTS] 声明 `tests/position/test_firm_risk_aggregator.py` | ⚠️ 测试文件于 2026-08-10 创建未 `git add`，2026-08-11 被 `git clean -fd` 删除且 git 历史无记录——此前声称的"54 单元测试全绿（0.09s）"**当前工作区无法复现**。重建建议：按 §2.1.1 施工伪代码 + §2.7 契约字段 + degraded 5 条件重建用例，重建后立即 `git add`（防护规则①）。同批丢失：`test_strategy_book.py`（70）/ `test_budget_change_handler.py`（47）/ `test_regime_meta_allocator.py`（55），登记 [30号 §6.8](30_multi_strategy_concurrency.md) |
| **capability_canonical_file_registry 未登记** | 硬约束"模块创建必须生成 creation_token 并登记" | ⚠️ MOD-POS-021（及同批 MOD-POS-020/022、MOD-PA-007）未在 `capability_canonical_file_registry.yaml` 登记（该 registry 仅 MOD-POS-009 一条 D_POSITION 记录）。需补登记（creation_token 追溯生成或按补救流程）——不属本备忘施工范围，登记供治理调度 |
| **depgraph maturity 滞后** | [64_d_position.md](../../02_domain_architecture_docs/64_d_position.md)（自动生成） | ⚠️ depgraph（PostgreSQL）中 MOD-POS-020/021/022 仍标 design，64 号自动文档佐证滞后（"设计态/design"）。需 depgraph DB 更新 maturity=production 后重新生成——不属本备忘施工范围，登记供治理调度 |

## 7. 引用

### 7.1 相关 design_memo
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)
  - §2.2 FirmRiskAggregator 定义——本备忘的框架来源
  - §2.3 自然叠加——用加法替代优化器，O(N) 替代 O(N²)
  - §3.1 拒绝 MVO——不做协方差估计
  - §3.2 拒绝 Model D——不做跨策略投票
- [31_position_sizing.md](31_position_sizing.md)
  - §2.1 分层裁定流程——求和→Kelly→裁剪的数据流
  - §2.4 硬上限参数——单票 8%/行业/总仓位（G12 定参数，G13 执行）
  - §2.5 现金管理——显式 CASH 标的
  - §2.6 FirmTargetPortfolio 数据结构契约
  - §8.1 给 G13 的交接项——本备忘的输入清单
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G13 / §5 轨道 B / §7.3 编号占用表
- [01_design_memo_management_spec.md](01_design_memo_management_spec.md) §4.3 推荐章节 / §5.2 引用纪律

### 7.2 depgraph 模块（用 blueprint_id / path 引用）

| 模块 | blueprint_id | path | 本备忘角色 | 当前状态（2026-08-12 核对源码） |
|---|---|---|---|---|
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | 本备忘主体（§2 全部） | ✅ production v1.0.0（651 行，0 处 NotImplementedError）⚠️ 测试文件丢失（54 测试，§6 登记重建） |
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | 上游：产出 StrategyTarget（§2.2 求和输入） | ✅ production v1.0.0（680 行）⚠️ 测试丢失（70） |
| position_sizing_engine | MOD-POS-001 | `src/zephyr/position/core/position_sizing_engine.py` | 下游：Kelly 精裁决（§2.1 步骤③）+ 最终硬限 | ✅ production（881 行）✅ 测试在位 |
| position_limit_enforcer | MOD-POS-010 | `src/zephyr/position/core/position_limit_enforcer.py` | 最终硬限兜底（5% NAV，§2.4 注） | ✅ production ✅ 测试在位 |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | 消费 constraint_checks 做三级升级（G14） | ✅ production v1.0.0（572 行）⚠️ 测试丢失（47）+ 33 号设计文档骨架化（§6 登记） |

> MOD-PA-007（RegimeMetaAllocator，Shrinkage 节流）属 G15，本备忘只消费其输出的 budget 数字。✅ 已 production v1.0.0（594 行，0 处 NotImplementedError，34 号 v2.7.0 确认）⚠️ 测试丢失（55）。
>
> ⚠️ **depgraph DB 滞后**：上述 5 个模块在 depgraph（PostgreSQL）中仍登记 design（[64_d_position.md](../../02_domain_architecture_docs/64_d_position.md) 自动生成文档将 MOD-POS-020/021/022 标"设计态"佐证），需 depgraph 更新后重新生成——登记 §6。

### 7.3 相关 battle_map
- BM-POS-04 跨策略仓位硬限制（MOD-POS-010）——单票 8% / 行业 ±10% / 总仓位 9 态框架（参数来源）
- BM-POS-06 现金管理约束（MOD-POS-006）——CASH 标的约束

### 7.4 开源实证参考
- **[Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book)** — sleeve(alpha)+risk-parity-throttle(firm) 分层，firm 层只做 risk-parity 求和+throttle 不做 MVO。印证本备忘自然叠加+硬裁剪架构（30_multi_strategy_concurrency §7.4 已引）
- **[tierzero multi-venue risk limits](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading)（2026-01）** — 三层限仓栈（strategy → venue → portfolio），"portfolio limit is the hard ceiling"，"common mistake is to set limits only at layer 1 and assume aggregation takes care of itself"。印证 FirmRiskAggregator 组合级硬裁剪必要性（§2.4/§2.5）
- **[algovestiq position sizing](https://www.algovestiq.com/learn/answers/how-to-size-stock-positions)（2026-05）** — 行业基准"hard cap 8-10% per position, 20-25% per sector"。印证单票 8% + 行业 30% 绝对上限（§2.4/§2.5.1）
- **[nautilus_trader #4419](https://github.com/nautechsystems/nautilus_trader/issues/4419)（2026-07）** — portfolio-level gross exposure cap across multi-strategy 是真实需求（多策略各自有 sizing limit 但组合级缺聚合控制）。印证 FirmRiskAggregator 存在理由
- **[go-trader #1270](https://github.com/richkuo/go-trader/issues/1270)（2026-07）** — 相关性标的被当作分散化是风险；direction+asset bucketing 作为协方差替代。印证不做协方差但做硬限的路线（§2.5/§3.4）
- **[finlab multi-strategy portfolio](https://finlab.finance/docs/en/workflows/multi_strategy_portfolio/)（2026）** — 明确"if Strategy A holds 2330 at 5% and Strategy B holds 2330 at 3%, the final portfolio holds 8%"，自然叠加是多策略组合标准实践。dead-band filter 抑制小再平衡交易（weight change <2% 不调整）。印证 §2.2 自然叠加 + §6 dead-band filter 评估
- **[QBase_v2.5 Portfolio 构建指南](https://github.com/S1mon-code/QBase_v2/blob/main/docs/PORTFOLIO.md)（2026-04-09）** — 多策略组合构建实践：与现有组合相关性 <0.40、边际 Sharpe 贡献 >0（SR_candidate > ρ × SR_portfolio）、交易次数影响权重上限（LOW <10 次 → 15% 上限）、加入后 MaxDD 恶化不超过 3%。印证组合级硬限必要性（§2.4/§2.5），相关性/边际 Sharpe 属协方差范畴已拒绝（§3.4）
- **[quant-portfolio multi-sleeve](https://github.com/isaacnicas/quant-portfolio)（2026-06）** — 多 sleeve 交易系统实践：dead-band filter 抑制小再平衡交易（低于最小阈值不执行，避免交易成本超信号收益）+ position caps 防单 name 主导 sleeve 风险预算 + per-order attribution 分离各 sleeve 贡献。印证 §2.2 contributions 归因 + §6 dead-band filter 评估
- **[xfinlink commodity risk parity](https://xfinlink.com/blog/commodity-risk-parity-python)（2026-06-18）** — 6 商品 ETF inverse-vol 实证：return 15.7% vs equal-weight 8.7%，MaxDD -6.7% vs -19.8%，vol 11.7% vs 16.0%。inverse-vol 防最高波动品种主导组合风险。印证 §2.5 行业硬约束必要性（防高波动行业主导）+ 31_position_sizing §2.2.2 inverse-vol 降回撤
- **[A股量化私募7月集体回撤·涵德风控升级](https://m.toutiao.com/group/7670831772460794420/)（2026-08）** — 2026-07 量化私募集体回撤（幻方单月-22%、明汯 9/14 产品年内负），根因是动量/残差波动率/流动性/短期反转因子罕见同向下跌，多因子分散逻辑短期失效 + 机构相似数据训练相近因子同步降低敞口形成踩踏。涵德投资风控升级：单票上限 1%→0.3%、持股 600→900 只、因子软约束→硬约束。**印证 §2.4 单票硬上限裁剪 + §2.5 行业硬约束的实盘价值**——2026-07 极端行情下组合级硬限是生存关键；同时印证 §5 相关性聚类待裁定项的必要性（跨行业因子共振导致静态行业归类不足以控制集中度风险）
- **[breakingalpha Portfolio-Level Risk Constraints](https://breakingalpha.io/insights/portfolio-level-risk-constraints)（2025-11）** — 多策略算法组合的组合级风险约束框架：risk budget framework（volatility budget / VaR budget / drawdown budget）+ dynamic risk budgets（drawdown 时收缩）+ constraint hierarchy（冲突时优先级）。印证 §2.5 约束执行顺序（单票→行业→总仓位，从局部到全局）+ §2.7 constraint_checks 供 G14 三级升级判断
- **[quanthedgeai Multi-Strategy End-to-End](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)（2026-07）** — 多策略组合端到端实践：strategy intake/incubation（research candidate → paper portfolio 6 月 → half-sized live 6 月 → full size）+ allocation/sizing + rebalancing + monitoring + strategy removal + annual review。印证 30_multi_strategy_concurrency §2.1 独立账本 + 本备忘 §2.7 FirmTargetPortfolio 契约（组合级聚合是多策略落地的核心环节）
- **[tierzero correlation clustering](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading)（2026-01）** — pairwise correlation >0.6 的策略归同一 cluster，cluster 有独立 notional limit（比各成员 limit 之和更紧）。印证 §2.5 相关性聚类待裁定项（"不做完整协方差但做二元相关性判定"的中间方案）+ §5 待裁定条件
- **[riskcore: Open-Source Multi-Manager Risk Aggregation](https://github.com/massimotodaro/riskcore)（2026-01）** — 开源多管理人风险聚合平台，核心理念 **"Don't replace PM systems. Aggregate them."** ——READ-ONLY overlay 不替代各 PM 系统，只做跨 PM 聚合。功能：Real-time Position Aggregation（跨 PM/系统合并持仓为单一视图）+ Cross-PM Netting（识别对冲持仓算真实净暴露）+ Firm-level VaR（带相关性处理的聚合 VaR）。**与本项目 FirmRiskAggregator 架构同构**——"不替代策略层选股，只做 firm 层聚合"对应"策略层粗仓位 + firm 层求和裁剪"；Cross-PM Netting 对应 §2.3 冲突标的净额处理；Firm-level VaR 对应 §2.7 constraint_checks 组合级风险检查。riskcore 是机构级（$1B-$50B AUM 多管理人基金）实现，本项目是个人级简化版，但聚合逻辑同构
- **[Passify Global Risk Overlay](https://www.einpresswire.com/article/896092429/passify-releases-new-quantitative-report-on-multi-algorithm-correlation-and-risk-aggregation)（2026-02）** — 多算法相关性风险报告：**"1% risk per trade on ten different bots can quickly escalate into 10% open exposure on a single correlated move"**——策略级 1% 限制在 10 个相关策略叠加后变 10% 暴露。Global Risk Overlay 独立于策略层，监控总组合暴露/杠杆/日浮盈亏，超阈值干预（halt new entries 或 liquidate positions）。印证 §2.4 单票裁剪 + §2.5 行业/总仓位硬约束的必要性（策略级限制不够，需 portfolio overlay）+ §2.5 相关性聚类待裁定（跨策略相关性隐藏集中度风险）+ §2.1 degraded 降级标记（组合级超限触发降级供 G14 三级升级）
- **[algovantis Multi-Strategy Position Sizing](https://algovantis.com/optimizing-position-sizing-for-multi-strategy-risk-management-and-stability/)（2026-03）** — 多策略仓位管理实践：Drawdown-Based Re-sizing（策略回撤时缩减仓位，恢复后逐步加回，自适应断路器）+ 动态相关性矩阵（EWMA 捕捉演变关系）。印证 §2.1 degraded 降级标记（回撤触发降级供 G14 三级升级）+ 33号三级升级机制（drawdown→缩减→恢复流程）+ §2.5 相关性聚类（动态相关性矩阵是相关性聚类的连续版）
- **[Nystrup/Boyd/Lindström/Madsen: Multi-period portfolio selection with drawdown control](https://www.researchgate.net/publication/325874988_Multi-period_portfolio_selection_with_drawdown_control)（Annals of Operations Research 2019, 2026-06 更新）** — MPC（Model Predictive Control）动态优化投资组合并控制回撤：基于多变量 HMM 的多期收益均值/协方差预测，**核心创新是根据已实现回撤动态调整风险厌恶系数**——"adjusting the risk aversion based on realized drawdown successfully controls drawdowns with little or no sacrifice of mean–variance efficiency"。交易/持仓成本作为估计误差的正则化手段。O(N) 加法替代优化器（与本项目 §2.2 自然叠加哲学一致）。**印证 §2.10.2 MPC 多期预测远期演进方向**——G15 Shrinkage 可远期增加"已实现回撤"维度做连续 budget 调整（当前是 regime 驱动单期）
- **[RMATS: Recursive Multi-Agent Trading System](https://arxiv.org/html/2605.25311v1)（arXiv:2605.25311, Yang et al. 2026-05）** — 4 specialized agents（Sentiment/Report/Analysis/Risk）由 recursive Manager Agent 协调，迭代反馈至权重收敛（‖w^(r+1)−w^(r)‖₂ < ε=0.008，中位数 2 轮）。**MaxDD 9.62% vs MVO 15.49% vs FinBERT 15.28%**。Risk Agent 独立于策略 agent，专门做 CVaR 估计（EWMA 动态协方差）+ 地缘压力测试 + 自适应多级断路器；奖励函数 R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)，λ₁=0.8/λ₂=1.5（回撤控制优先）。**印证 §2.10.3 独立风险层架构原则**——FirmRiskAggregator 本就是独立风险层（§2.9 边界声明），与 RMATS Risk Agent 同构；但 RMATS 的多 agent + 递归 Manager + LLM 对个人项目过重（§4.4 审查：不借鉴实现，只借鉴原则）。MaxDD 9.62% 主要来自 CVaR + 断路器（本项目 var_calculator.py + 30号 Drawdown Protocol 已有等效），非多 agent 本身
- **[Noguer i Alonso & Al-Fallouji: Tail Risk Management with Puts and Trend Following — A CVaR Framework for Crashes and Drawdowns](https://arxiv.org/pdf/2607.00883v1)（arXiv:2607.00883, 2026-07）** — 连续时间 CVaR 框架，把 put options + trend-following 两类保护放入统一 tail-risk mandate。核心洞见：尾部风险是"跨损失机制的配置问题"（abrupt crash states / volatility repricing / persistent drawdowns 需不同保护）。**四轴诊断层**：条件凸性 / 尾部事件可靠性 / 非压力 carry / 回撤持续性。convex insurance 跳价即刻重定价，trend following 首次冲击迟到但持续回撤中渐进防御。**印证 §2.10.1 CVaR 作为统一尾部风险度量**——四轴诊断可借鉴为裁剪后 `constraint_checks.tail_quality` 验证维度（当前 §2.5 行业/总仓位裁剪只管集中度不管尾部对冲质量）
- **[Man Numeric: Covering Your Tail — The Case for Expected Shortfall in Tail Risk Management](https://www.man.com/documents/download/81842-e96ab-9099d-e1c10/Numeric_Insights_Covering_Your_Tail%3A_The_Case_for_Expected_Shortfall_in_Tail_Risk_Management_English_%28United_States%29_23-07-2025.pdf)（Joshua Levin, 2025-07）** — CVaR（=Expected Shortfall）优于方差：方差把上行下行对称处理（涨停板=风险），CVaR 显式度量不利结果（只看左尾）。实证两组合相同 variance 但 CVaR 差 −1.32% vs −1.78%（"Portfolio Two is much crashier"）。用于构建具有互补左尾特性的回报流配置。**印证 §2.10.1 CVaR 显式度量不利结果**——与 A 股打板策略"涨停板是好事"直觉一致（34号 §3.2.2 Sortino 选型同理，只惩罚下行波动）
- **[pooyagolchian: Portfolio Risk Management — VaR, CVaR, and Kelly Criterion for 2026 Portfolios](https://pooyagolchian.com/blog/portfolio-risk-var-cvar-kelly-criterion-2026/)（2026-04-13）** — VaR 三方法（Historical/Parametric/Monte Carlo）+ CVaR/VaR 比率实证 ~1.48x（95%），集中组合可 >2.0x——"when bad days happen, they are on average 48% worse than the VaR boundary"。Kelly 分数实证：Full Kelly 312% CAGR 18.2% MaxDD −62% / Half Kelly 156% CAGR 14.1% MaxDD −38% / **Quarter Kelly 78% CAGR 10.8% MaxDD −22%**——"Quarter Kelly delivers 85% of full Kelly's growth with only 35% of the drawdown"。**印证 §2.10.4 Quarter Kelly 与硬裁剪协同**——本项目 31号用半 Kelly（A 股实证）+ §2.4 单票 8% + §2.5.2 总仓位上限是 Kelly 之外的额外安全网；CVaR/VaR 比率可作为 `constraint_checks` 尾部严重度连续指标
- **[nexusfi: Multi-Strategy Automated Futures Trading](https://nexusfi.com/a/automation/multi-strategy-portfolio-automated-futures)（2026-06-05）** — 多策略组合架构：Strategy Engine（产出意图不直接执行）+ **Risk Engine（集中式组合级聚合，跨策略汇总持仓、检查所有限制 per-instrument/per-factor/portfolio-wide、监控相关性、批准或修改订单）** + OMS/Execution。Net Exposure = 跨策略同标的聚合（Strategy A long 3 ES + B short 1 ES = net +2 ES）。**Effective Number of Bets (ENB) = 1/Σwᵢ²** 作为真实分散化度量；**Incremental VaR (IVaR)** = 单策略对组合 VaR 的贡献。三级 kill switch（strategy/underlying/portfolio）。**印证 §2.9 边界声明（FirmRiskAggregator 是独立风险层只消费不选股）+ §2.3 冲突净额（Net Exposure 同构）+ §2.1 degraded（portfolio-level 超限触发干预）**。IVaR 概念可借鉴为 §2.10.1 CVaR 验证层的归因维度（哪只票/哪个策略贡献了多少组合尾部风险）
- **[marcelgautsche: Multi-Strategie-Portfolios — Risk-Budgeting in der Praxis](https://marcelgautsche.de/insights/multi-strategie-portfolios)（2026-06）** — 多策略 risk-budgeting 实践：**Risk-Budget pro Strategie**（每策略固定 % 权益作 risk budget，position sizing 在 budget 内算非总账户）——防"所有策略同时建大仓导致组合风险失控"。相关性阈值：<0.4 好 / >0.7 冗余 / 0.4-0.7 灰区。4 个不相关策略 × 15% MaxDD → 组合 8-10% MaxDD。三模型：Equal Weight / Inverse Volatility / Risk Parity。**印证 §2.2 budget 口径统一（各策略 target_portfolio 权重是相对 strategy_budget 的占比，求和前归一到总资金口径）+ §2.5 相关性聚类待裁定（阈值 0.4/0.7 与 tierzero 0.6 同量级）**。Risk-Budget pro Strategie 与本项目 G15 RegimeMetaAllocator 的 allocation_i × global_shrinkage = effective_budget 同构
- **[Man Group: The Pod-Shop Model Isn't the Only Way](https://hedgenordic.com/2026/06/man-group-the-pod-shop-model-isnt-the-only-way/)（Greg Bond, CIO Man Group, 2026-06-23）** — 多策略不必然走 pod-shop 蓝图：Man Group 1783 Multi-Strategy Fund 在**单一风险框架内**组合 systematic + discretionary 回报流。"A multi-strategy platform sees every underlying position in real time, which changes how risk is managed. Correlations can be monitored as they evolve; crowding can be identified before it becomes a problem; and capital can be reallocated before issues compound"。leverage 在组合层应用。**印证 §2.9 边界声明（FirmRiskAggregator 是集中式组合级聚合）+ 30号 §4.3 修正（Model A 是 Morwane 式"统一风险框架 + 独立 alpha sleeve"非 Citadel pod 式）**。"correlations can be monitored as they evolve" 印证 §2.5 相关性聚类远期演进（动态相关性 vs 静态行业归类）
- **[Wang & Hasuike: Decision-Induced Ranking Explains Prediction Inflation and Excessive Turnover in SPO-Based Portfolio Optimization](https://arxiv.org/html/2605.01176v3)（arXiv:2605.01176v3, 2026-06-05）** — SPO（Smart Predict-then-Optimize）DFL 在组合优化中产生 inflated return signals + unstable reallocations。评估三种稳定机制：**clipping**（裁剪）+ min-max rescaling + **partial portfolio adjustment（δ<1，只闭当前→目标差距的 δ 比例）**。partial adjustment 直接降 turnover，把组合路径在时间上平滑。**印证 §6 dead-band filter 归属评估**——partial adjustment（δ<1）是 dead-band filter 的连续版（dead-band 是二元"超阈值才调"，partial 是"调 δ 比例"），同属执行层非 G13 裁剪算法。clipping 作为稳定机制印证 §2.4-§2.5 硬裁剪的合理性
- **[A.L. Capital Advisory: Conditional Value at Risk (CVaR)](https://alcapitaladvisory.com/research/frameworks/cvar.html)（Anton Ladnyi, CFA, 2026-03-18, 2026-07-09 更新）** — CVaR 定义/公式/计算：集中 3 股组合 1 月 CVaR 16-18% vs 分散 20 股 6-9%（相同 VaR 下尾部差 2-3 倍）。5σ 损失事件比正态分布预测频繁 5 倍。**Basel III/IV 已用 Expected Shortfall（=CVaR）替代 VaR 作为银行内部模型标准**——因 CVaR 捕获尾部严重度非仅概率。Rockafellar-Uryasev 方法把 CVaR 最小化转为线性规划。**印证 §2.10.1 CVaR 是一致性度量（次可加性）+ Basel III/IV 行业标准方向**——本备忘 §2.5 权重+行业映射是 O(M) MVP 方案，CVaR 验证层是远期增强（var_calculator.py 已实现，待接口对齐 §6）
- **[ericxuzhesheng/Relaxed-Risk-Parity-Research](https://github.com/ericxuzhesheng/Relaxed-Risk-Parity-Research)（2026-08-07, 410 commits）** — 宽松风险平价全球资产配置框架：风险预算松弛（软化严格等风险贡献）+ 凸自适应重构（改进求解器稳定性）+ **CVaR 约束**（显式限制尾部损失）+ 换手惩罚（内化交易成本）。是"三因子乘法（当前 G15）→ MVO（已否决）"之间的中间态。**印证 §2.10.1 CVaR 约束方向 + 30号 §4.2 远期演进路径**（Relaxed Risk Parity 已在 30号 §4.2 / 34号 引用为远期，本备忘交叉引用确认 CVaR 约束是该路径的核心组件）
- **[MDPI Economies: From Regime Detection to Decision Rules](https://www.mdpi.com/2227-7099/14/7/268)（Grube Martín-Lunas et al. 2026-07-09）** — 欧洲 10 资产 2000-2026 严格 walk-forward 实证：naive regime-conditional CVaR 分配产生**过高换手率（~226%/年）**，在任何现实交易成本下净表现**低于简单基准**；实现感知替代方案（regime-constrained weight bands）在 ~29% 换手率下恢复差距（net Sharpe 与静态基准差 0.009）。**核心发现**："瓶颈不是 regime 检测，而是透明、稳定、成本感知的决策规则设计"。印证 §2.5.2 总仓位裁剪需 convergence_window 控制 turnover（33号 §6 防抖）+ §2.8 O(N) 聚合须考虑交易成本效率（纯数学聚合合规≠实盘可执行，换手率失控侵蚀净 alpha）+ 31号 §2.4.3 regime Shrinkage 的离散分档比连续 CVaR 重分配更稳（换手率更低）
- **[AEGIS: Taming the Black Swan](https://arxiv.org/abs/2604.09060)（Chakraborty/Singh BIT Mesra, arXiv:2604.09060, 2026-04-13）** — 三层架构：Volatility-Adjusted Momentum 选股 + **Minimax Correlation Algorithm**（最小化最坏情况资产间依赖，非简单 ρ 阈值）+ SLSQP 优化 Sortino。2006-2025 walk-forward CAGR 15.41%, MaxDD 28.89%（S&P 500 MaxDD>50%）。**印证 §2.10.5 演进方向 A**——minimax 是比 pairwise ρ>0.6 更优的全局相关性管理方向，但小规模参数噪声大，记为 Phase 5+ 远期候选
- **[Bayes Group: After the March Shock — Multi-Strategy Resilience](https://www.bayes-group.com/insights/march-shock-multistrat-resilience)（2026-03-30）** — 2026-03 地缘冲击 Millennium/Point72 各亏 ~$1.5B。"diversification illusion"——正常期低相关 pod 在共同宏观冲击下 tail correlation 飙升。恢复最快平台用**实时动态相关性监控**。**印证 §2.10.5 演进方向 B**——相关性突变检测层（short vs long window ρ 偏离度）是轻量 Phase 3 候选，比 MARCD 轻得多
- **[BlackRock Spring 2026 Hedge Fund Outlook](https://hedgeco.net/news/04/2026/blackrock-issues-crowding-warning-for-hedge-funds.html)（2026-04-16）** — 多策略 pod shop 共享数据/模型/宏观叙事导致 crowding，压力期 hidden correlation 突变可能 violent unwind。AI 驱动策略加剧收敛。**印证 §2.10.5 演进方向 C**——100% AI 项目单一开发者让多策略天然收敛，相关性聚类应从 PnL 层延伸到信号特征层
- **[QBase_v2.5 Portfolio Construction Guide](https://github.com/S1mon-code/QBase_v2/blob/main/docs/PORTFOLIO.md)（S1mon-code, 2026-04-09）** — 组合入选硬条件"边际 Sharpe 贡献>0"：新策略 Sharpe 必须 > ρ×现有组合 Sharpe，否则加入后组合 Sharpe 下降。两两相关性≥0.40 标记降权。最多 8 策略。**印证 §2.5 相关性聚类准入门槛**——ρ×SR_portfolio 阈值比固定 ρ<0.4 更合理，可作为策略 sleeve 准入条件（远期归 G05 信号工厂/G15 RegimeMetaAllocator 评估）
- **[Modeling Dynamic Correlation Matrices with Shrinkage Priors](https://arxiv.org/abs/2605.06818)（Coulson/Matteson/Wells, Cornell, arXiv:2605.06818, 2026-05-07）** — Bayesian 低秩因子表示 + 动态收缩先验（latent state innovation variance 在结构突变时自适应增大）+ multivariate factor stochastic volatility。**首次给出动态正则化 Bayesian 模型的 posterior contraction 结果**（averaged Hellinger distance 下显式收敛速率）。相比 rolling window/EWMA（平滑掉突变）和 DCC（低维参数化限制），动态收缩先验在金融压力期"突然局部 shift"场景下适应性更强。**印证 §2.10.5 演进方向 B 的学术严谨版**——short/long window ρ 偏离度是工程启发式，Bayesian 动态收缩先验是有理论保证的严谨版，但工程重（需 MCMC/VI 推断）记为远期候选
- **[FLOX-Foundation/flox PR#183: Portfolio Risk Aggregator](https://github.com/FLOX-Foundation/flox/pull/183)（2026-05-07）** — 开源跨策略 PnL/敞口聚合器，四条组合层风控规则：max_drawdown_pct / max_daily_loss / max_gross_exposure / **max_concentration_pct**（单策略占总 gross 比例上限，仅一个策略有 gross 时抑制）。pre-trade gate `check_order(strategy, notional, side)` + snapshot JSON 可序列化 + 线程安全 + 17 测试。**印证 §2.10.6 演进方向 D-1**——单策略集中度上限是本项目当前缺失的维度（现有单票/行业/总仓位三层无"单策略占比"层），FLOX 默认 0.35 可参考施工
- **[go-trader PR#1291: Portfolio Daily Loss Limit](https://github.com/richkuo/go-trader/pull/1291)（2026-07-09）** — 组合层硬日亏上限（USD），当日聚合已实现亏损达阈值→**持仓增加动作（新建/加仓/翻转/手动开加）全部 hold 到 UTC rollover**；平仓和 SL/TP 管理继续运行，**不强制平仓**。支持热重载。**印证 §2.1 degraded 标记 + 33号三级升级语义**——"只阻开仓不强制平仓"的设计哲学适合 A 股 T+1（T+1 下本就不能当日平，硬日亏上限应作用于次日新建仓决策而非强制平今仓）。本项目三级升级 Tier1 封锁新仓与此同构
- **[laoyulaoyu: 羊群行为量化检测六法](https://laoyulaoyu.com/index.php/2026/07/01/羊群行为（从众心理）的量化检测：六种方法识别市场过度拥挤信号/)（2026-07-01）** — HBI（羊群行为指数）=|个股均收益−基准均收益|/|基准均收益|，HBI<0.3 极端一致性（群体陷阱），>2.0 统计异常（独立机会）；CSAD（横截面绝对偏差）=组合个股收益离散度，低 CSAD=羊群。实战信号：2020-03 HBI_60d=1.8→复苏信号；2022-01 HBI_60d→0.25→群体一致性预警。**印证 §2.10.6 演进方向 D-2**——HBI/CSAD 是 O(N) 纯价格计算完全符合本项目不估协方差原则，可作 firm 层 degraded 第 6 项触发（市场极端一致性→降仓），是 BlackRock crowding 警示的最轻量级 A 股可落地方案
- **[Pomegra: AI Trading Crowding Erases Quant Edge](https://pomegra.io/news/ai-trading-crowding-erases-quant-edge-2026)（2026-06）** — 2026-05 Goldman 标记 AI 动量 positioning 达 5 年数据集 100th 百分位（绝对天花板），当日高 beta 动量篮子跌 8%。75%+ 美股交易量由 quant/algo 驱动。Citadel："AI paradox——帮每家更早识别风险，同时帮所有家更早识别，触发相关退出，加深各自想避免的错位"。**印证 §2.10.5 演进方向 C + §2.10.6 D-2**——100% AI 项目单一开发者让多策略天然收敛，HBI/CSAD 市场层拥挤度检测 + 信号层 crowding 检测是双重防线
- **[GinkGO PCA + CorrDD 相关性结构检测](https://github.com/kaoruha/ginkgo/issues)（Kaoruha 2026-05）** — N 策略 PnL 相关矩阵 PCA 特征值分解，第一主成分方差解释比 VE_1>50% 预警共同因子暴露（多策略被同一隐藏因子驱动的分散化假象，pairwise ρ 无法捕捉）；Herfindahl 指数 H=Σw_i² 衡量组合集中度；CorrDD(i,j)=corr(DD_i,DD_j) 捕捉回撤尾部同步（正常期 PnL ρ 被稀释，CorrDD 只看回撤序列）。**印证 §2.10.5 演进方向 E**——PCA 是全局结构检测（pairwise ρ 是局部二元检测），CorrDD 是尾部同步检测（PnL ρ 被"正常期多数样本"稀释），两者互补填补 A/B/C 三方向未覆盖的"共同因子暴露+回撤尾部同步"空白。与 [31号 §3.7](31_position_sizing.md) HRP 评估中 PCA 第一主成分预警同源
- **[华泰证券金工：风格拥挤度模型](https://m.hibor.com.cn/wap_detail.aspx?id=5dc71a9949bce52f3398c30caaf270dd)（2026-08）** — 动量+成交量双维度分域模型：按动量得分（Top 20%/中/Bottom 20%）×成交量得分分域，计算各域个股数占比的时序百分位。小盘拥挤度>90% 分位→小盘风格高度拥挤（unwind 风险），大盘拥挤度<10% 分位→大盘风格极度冷清（资金撤离）。20 日持续期确认防短期脉冲。**印证 §2.10.6 演进方向 D-3**——华泰金工是 A 股本土风格拥挤度模型，比 HBI/CSAD（市场整体羊群度）更精准定位"哪种风格在拥挤"，指导 G14 三级升级定向降仓（降拥挤风格对应的策略而非等比例降所有策略）。与 HBI/CSAD（D-2）递进——HBI 先检测"市场是否拥挤"，华泰再定位"哪个风格拥挤"
- **[MINGLE: Beyond Co-Movement — Joint Factor-Graph Framework](https://arxiv.org/abs/2608.06618)（arXiv:2608.06618, 2026-08-06）** — ADMM 联合学习隐因子暴露 + 策略间图拓扑结构，优于纯相关性聚类。不只检测"策略间相关性"（pairwise ρ / PCA），而是同时学习"策略被哪些隐因子驱动"（因子图）+ "策略间图拓扑关系"（邻接矩阵），两者联合优化。**印证 §2.10.5 演进方向 F**——MINGLE 是 minimax（方向 A）的因子图泛化 + PCA（方向 E）的图结构扩展，能捕捉 PCA 遗漏的"因子间交互拓扑"。**P4+ 远期候选**：ADMM 联合优化工程重，3-5 策略规模下现有 A/B/C/E 已覆盖主要风险，策略数 >8 且 A/B/C/E 漏检率高时重评

### 7.5 system_charter 约束映射
- §3 约束四（策略三维度解耦）→ FirmRiskAggregator 只管 how much 聚合，不管 what 选股
- §3 约束五（少而精）→ 3-5 策略 O(N×M) 聚合足够，不需 MVO
- §3 约束一（交易成本）→ 聚合后裁剪不引入额外交易成本（只读 budget 做缩放）

### 7.6 已施工设施盘点（2026-08-12 全量核对，通用规则 #11）

> 盘点范围：与本备忘（G13 FirmRiskAggregator）数据流直接相关的全部已施工设施。更广域的四域盘点见 [30号 §7.5](30_multi_strategy_concurrency.md)。**先清楚有什么 → 才知道怎么改 → 才知道该删除/退役什么**。

#### A. G13 数据流核心链（StrategyBook → FirmRiskAggregator → MOD-POS-001 → 下单）

| 模块 | path | 行数 | MATURITY | 测试 | 与本备忘关系 |
|---|---|---|---|---|---|
| MOD-POS-020 StrategyBook | `position/core/strategy_book.py` | 680 | production v1.0.0 | ⚠️ 丢失（70） | §2.2 求和输入（`TargetPortfolio` 产出者——⚠️ 字段名漂移见 §6 P0 行） |
| **MOD-POS-021 FirmRiskAggregator** | `position/core/firm_risk_aggregator.py` | 651 | production v1.0.0 | ⚠️ 丢失（54） | **本备忘主体**：两段拆分已实现（`pre_kelly_aggregate`/`post_kelly_clip`/`aggregate` 便捷入口 + 5 个内部裁剪方法），0 处 NotImplementedError |
| MOD-POS-001 position_sizing_engine | `position/core/position_sizing_engine.py` | 881 | production | ✅ 在位 | §2.1 步骤③ Kelly 精裁决（消费 `PreKellyResult.summed_weights`） |
| MOD-POS-010 position_limit_enforcer | `position/core/position_limit_enforcer.py` | — | production | ✅ 在位 | §2.4 三层口径最终兜底（5% NAV） |
| MOD-POS-022 BudgetChangeHandler | `position/core/budget_change_handler.py` | 572 | production v1.0.0 | ⚠️ 丢失（47） | §2.7 `constraint_checks`/`degraded` 消费者（G14）；33 号文档骨架化 |

#### B. 参数/上限供给方（本备忘只消费不定阈值）

- MOD-PA-007 RegimeMetaAllocator（`pf_alloc/core/regime_meta_allocator.py`，594 行，production v1.0.0，⚠️ 测试丢失 55）——`total_budget` + `regime_cap` 来源（§2.2/§2.5.2）
- 31 号仓位算法（G12）——单票 8%/行业 30%/流动性 ADV 20%-10% 阈值真源（§2.4/§2.4.4/§2.5.1）
- MOD-POS-008 drawdown_controller（603 行 production，✅ 测试在位）+ var_calculator（`risk/core/`，394 行 production Phase 1，✅ 在位）——§2.10.1 CVaR 验证层候选数据源

#### C. 代码-文档契约核对结论（2026-08-12）

- §2.1.1 伪代码 A-G 修复与实际代码**全部一致**：`liquidity_cap` 键初始化（L301）/ degraded 5 条件（L346-353）/ `adv_data` 参数化 + `sector_adv_median` 派生（L505-516）/ `total_budget` 口径（L526）/ `contributions` 透传（L106+L340）/ `sector_overlay_active` 预留（L262）✅
- §2.7 契约字段与 `FirmTargetPortfolio` dataclass（L77-93）**一致**：firm_positions/total_exposure/total_budget/cash_ratio/constraint_checks/conflicts_resolved/degraded/created_at/idempotency_key/schema_version 全在位 ✅
- INVARIANTS（代码 L8）与 §2 决策**一致**：自然叠加/按比例削/不做 MVO/O(N)/冲突净额 ✅
- ⚠️ **唯一不一致**：`_sum_by_symbol` 输入适配（L386-394）按 `target_portfolio`/`budget_used` duck-typing，与 StrategyBook 实际产出 `TargetPortfolio.positions`/`budget` 字段名不匹配（§6 P0 行登记）

#### D. 缺口登记（详见 §6 表尾）

- 4 个测试文件丢失（2026-08-11 git clean 灾难）——"54 测试全绿"当前无法复现
- capability_canonical_file_registry 未登记 MOD-POS-021（硬约束违例）
- depgraph DB maturity 滞后（64 号自动文档标"设计态"）
- StrategyBook→FirmRiskAggregator 字段名三方漂移（P0）

## 8. 交接清单（供兄弟主题组 AI 索引）

> 本节抽取 G13 FirmRiskAggregator 中供兄弟主题组（G12/G14/G15）直接消费的交接点。
> 交接纪律（00_index_trading_decision §7.2）：AI 间不直接通信，通过产出物 + depgraph path 交接。

### 8.1 给 G12 仓位算法（`31_position_sizing`）的回接项

| 回接项 | G13 出处 | G12 需知 |
|---|---|---|
| `FirmTargetPortfolio.firm_positions[symbol].target_weight` 作为 `w_i^sum` | §2.2 / §2.7 | G12 §2.3.4 Kelly 合成规则消费此值 |
| 裁剪后 `target_weight` + `cut_ratio` 供 Kelly 后最终裁剪 | §2.4 / §2.7 | G12 §2.4 硬上限参数由 G13 执行 |
| 不做 Kelly / 不估密度 PDF | §2.9 | Kelly 归 MOD-POS-001（G12） |

### 8.2 给 G14 BudgetChangeHandler（`33_budget_change_handler`）的交接项

| 交接项 | G13 出处 | G14 需自行定义 |
|---|---|---|
| `constraint_checks`（单票/行业/总仓位是否触发裁剪） | §2.7 | 三级升级触发阈值与流程（Tier1 封锁/Tier2 信号/Tier3 强裁） |
| 冲突标的 `conflicts_resolved` 记录 | §2.3 / §2.7 | 是否触发 rebalance 评估 |
| `FirmTargetPortfolio` 数据结构 | §2.7 | rebalance 时 CASH 权重调整 |

### 8.3 给 G15 RegimeMetaAllocator（`34_regime_meta_allocator`）的交接项

| 交接项 | G13 出处 | G15 需知 |
|---|---|---|
| `total_budget` = 所有策略 budget 之和 | §2.2 / §2.7 | G15 Shrinkage 输出的 budget 数字是 G13 求和的输入 |
| 总仓位上限（12 态+2 overlay） | §2.5.2 | G15 定 Shrinkage 参数，G13 只消费 budget 数字 |

### 8.4 G13 不做的事（避免兄弟组误判覆盖范围）

| 不做的事 | 归属 | 说明 |
|---|---|---|
| Kelly 精裁决 | G12（MOD-POS-001） | G13 只求和，Kelly 归 G12 |
| 三级升级机制 | G14（MOD-POS-022） | G13 只记录 constraint_checks，不定降级流程 |
| regime Shrinkage 参数 | G15（MOD-PA-007） | G13 只消费 budget 数字，不估 regime |
| 选股 / 策略定义 | G04 / G05 | G13 只接收 StrategyTarget |
| 单票/行业/总仓位阈值 | G12（31_position_sizing §2.4） | G13 只执行裁剪，不定阈值 |

---

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G13 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active 回填 7 项讨论要点 | §2.2 按标的求和（自然叠加，O(N) 加法替代优化器，budget 口径归一）；§2.3 冲突标的净额处理（不按优先级，A 股不能做空净额<0 截断清仓）；§2.4 单票硬上限按比例削（非优先级截断，归因公平无 meta 参数）；§2.5 行业/总仓位硬约束（按权重归类求和不估协方差，执行顺序单票→行业→总仓位）；§2.6 不做 MVO/不估协方差（30 §3.1 已拒绝）；§2.7 FirmTargetPortfolio 契约（FirmTarget/ConflictRecord 数据结构，权重和+CASH=total_budget）；§2.8 O(N×M) 复杂度保证（N=3-5 策略 M≤50 标的 <250 次操作）；§2.1 聚合流程两段参与+代码现状 aggregate() 拆分待定；§3 拒绝 MVO/优先级截断/优先级仲裁/协方差聚合四方案；§4.4 过度工程审查（行业硬约束必需非过重，tierzero 2026-01 印证组合级硬限必要性）；§5 待裁定 3 项；§6 待定 4 项；§7.4 引 5 条 2026 实证（Morwane/tierzero/algovestiq/nautilus_trader/go-trader）；§8 交接清单 G12/G14/G15；全网搜索 2026 firm risk aggregator/portfolio hard limit/position aggregation 实证 |
| 2026-08-10 | 1.0.1 | 同步 33号定稿状态：§4.2 演进路径阶段3 触发条件"33定稿"→"✅ 已定稿 v1.0.0（可施工）"；§6 开放问题"待 33 定稿"→"33 已定稿 v1.0.0，接口待对齐（33号 §3.2.6 ↔ 本备忘 §2.7）" | 33_budget_change_handler 已于本日升 active v1.0.0，本备忘两处前向引用的"待定稿"措辞陈旧，同步更新 |
| 2026-08-10 | 1.0.2 | 2026-08 最新研究补充 + dead-band filter 归属评估 | §2.2 补 finlab/quant-portfolio 自然叠加实践印证（"Strategy A 5% + B 3% = 8%" + per-order attribution）；§6 新增 dead-band filter 归属评估（结论：不属 G13，归 G14 防抖或 buy/sell_flow 最小交易阈值）；§7.4 补 4 条 2026-08 最新实证（finlab/QBase_v2.5/quant-portfolio/xfinlink commodity）；全网搜索 2026-08-08 最新 portfolio aggregation/position clipping/risk parity 实证 |
| 2026-08-10 | 1.0.3 | 施工流程算法缺失补充 + 相关性聚类待裁定 + 2026-08-08 最新研究 | §2.5.1 补相关性聚类（correlation clustering）作为行业约束补充的待裁定说明（tierzero 2026-01 pairwise ρ>0.6 → cluster cap，"不做完整协方差但做二元相关性判定"中间方案，覆盖跨行业高相关风险如 2026-07 量化私募因子共振）；§5 新增"相关性聚类"待裁定项（重评条件：6+ 月 PnL + 行业约束不足 + 与 31号 §3.7 HRP 同步）；§7.4 补 4 条 2026-08 最新实证（涵德风控升级/breakingalpha portfolio-level risk/quanthedgeai multi-strategy E2E/tierzero correlation clustering）；全网搜索 2026-08-08 最新 portfolio aggregation/firm risk/HRP/correlation clustering 算法，评估选项外更好答案 |
| 2026-08-10 | 1.0.4 | 施工流程算法缺失补充 + riskcore 同构印证 + 2026-08-08 最新研究 | §2.1 补 pre_kelly_aggregate/post_kelly_clip 接口契约（两段接口签名+职责边界+数据流，MOD-POS-001 Kelly 在中间调用）；§2.1 补 degraded 降级标记触发条件（5 条：冲突净额截断/单票裁剪/行业裁剪/总仓位裁剪/Kelly 参数降级传导，degraded≠错误而是安全网正常工作）；§2.5.2 补级联裁剪"每步基于上一步结果"说明（cascading 非独立并行，每步输入=上步输出，单调收敛，归因可追溯 cut_ratio）；§7.4 补 3 条 2026-08 最新实证（riskcore 开源多管理人风险聚合"Don't replace PM systems. Aggregate them."与 FirmRiskAggregator 架构同构/Passify Global Risk Overlay"1%×10 相关策略=10% 暴露"/algovantis drawdown-based re-sizing 自适应断路器）；全网搜索 2026-08-08 最新 portfolio risk aggregation/firm-level overlay/cascading clip 算法，评估选项外更好答案 |
| 2026-08-10 | 1.0.5 | 施工流程算法缺失补充 + 交叉引用版本漂移修复 + 2026-08 最新研究 | §2.3 补净额截断需 current_holdings 输入说明（pre_kelly_aggregate 须额外接收 current_holdings: dict[str,float] 来自 T-1 持仓快照，净额<0 截断 max(0,net+holdings) 不超过现有持仓，剩余意愿记 ConflictRecord）；§2.1 pre_kelly_aggregate 接口签名补 current_holdings 参数（四入参）；§2.4 补 CASH 豁免裁剪说明（CASH 无行业归属/无 contributions/Kelly 豁免，裁剪循环显式跳过 CASH，权重在现金管理步骤作残差计算）；§1.1 状态 v1.0.0→v1.0.5 + 依赖 31号 v1.3.0→v1.8.0（版本漂移修复）；§4.2/§6 33号 v1.0.0→v1.4.0（版本漂移修复）；§7.4 补 1 条 2026-08 最新实证（MDPI Economies regime-conditional CVaR 换手率 226%/年侵蚀净表现，瓶颈是决策规则设计非 regime 检测，印证 convergence_window 必要性 + 离散 regime 分档比连续 CVaR 重分配换手率更低）；全网搜索 2026-08-08 最新 portfolio aggregation/regime CVaR/turnover control 算法，评估选项外更好答案 |
| 2026-08-10 | 1.0.6 | 选项外更好算法补充（2026 最新研究整合）+ 过度工程审查 + 施工流程待定问题补全 | 新增 §2.10 选项之外的更好算法（远期演进方向）：§2.10.1 CVaR 作为统一尾部风险度量（Man Numeric 2025-07 + arXiv:2607.00883 四轴诊断 + alcapitaladvisory Basel III/IV + pooyagolchian CVaR/VaR~1.48x，消费 var_calculator.py 不重算，与 31号 §2.3.4 cvar_cap_i + 30号 §2.5 drawdown_controller 对齐）；§2.10.2 MPC 多期预测（Nystrup/Boyd 2019 回撤感知风险厌恶 + HMM 多期 + 成本正则化，G15 Shrinkage 远期多期化方向）；§2.10.3 独立风险层解耦（RMATS arXiv:2605.25311 MaxDD 9.62% vs MVO 15.49%，FirmRiskAggregator 已是独立风险层同构，多 agent+递归 Manager+LLM 对个人项目过重不借鉴）；§2.10.4 Quarter Kelly 协同印证（pooyagolchian Quarter Kelly 78% CAGR 10.8% MaxDD-22%，印证 §2.4 单票 8% + §2.5.2 总仓位硬裁剪是 Kelly 之外额外安全网）；§4.4 过度工程审查补 RMATS 多 agent + CVaR 验证层两行；§5 待裁定补 CVaR 裁剪后验证层 + MPC 多期预测两项；§6 待定问题补 lot 对齐归属/Kelly pro-rata 与总仓位裁剪防双重缩放/CVaR 接口对齐/pre_kelly-post_kelly 幂等性四项 + dead-band 补 arXiv:2605.01176 partial adjustment 连续版；§7.4 补 12 条 2026 最新实证（5 篇任务指定论文 Nystrup-Boyd/RMATS/CVaR-Crashes/Man-Numeric/pooyagolchian + nexusfi/marcelgautsche/Man-Group/SPO-arxiv/alcapitaladvisory/Relaxed-Risk-Parity 交叉引用）；全网搜索 2026 firm risk aggregator/portfolio risk aggregation/multi-strategy risk budgeting/O(N) portfolio clipping + 5 篇指定论文验证，整合选项外更好算法 |
| 2026-08-10 | 1.0.7 | 施工算法完整伪代码补全 + 交叉引用版本漂移修复 | 新增 §2.1.1 施工算法实现（pre_kelly_aggregate + post_kelly_clip 完整伪代码，对齐 33号 §3.4 handle_budget_change 风格）：pre_kelly_aggregate 含 budget 口径归一化求和（§2.2）+ 冲突标的净额处理（§2.3 含 current_holdings 截断）+ ConflictRecord 生成；post_kelly_clip 含单票裁剪（§2.4 CASH 豁免）→ 行业裁剪（§2.5.1 绝对 30%）→ 总仓位裁剪（§2.5.2 级联等比缩放）→ 现金管理（CASH 残差）+ cut_ratio 累积 + constraint_checks + degraded 标记 + FirmTargetPortfolio 组装；施工要点 7 条（两段调用顺序/CASH 豁免贯穿/级联单调收敛/cut_ratio 累积/degraded 标记/行业偏离待 D-FACTOR/幂等性）；§1.1 依赖 31号 v1.8.0→v1.9.0（版本漂移修复）；§4.2/§6 33号 v1.4.0→v1.5.0（版本漂移修复）；全网搜索 2026-08-08 最新 portfolio aggregation/firm risk clipping 算法，评估施工算法完整性——结论：§2.1.1 完整伪代码补全后施工算法无缺失，与 33号 §3.4 对齐 |
| 2026-08-10 | 1.0.8 | 相关性管理演进三条远期方向 + 交叉引用版本同步 + 2026-08 最新研究 | 新增 §2.10.5 相关性管理演进（minimax + 突变检测 + crowding 信号层）：演进方向 A——AEGIS Minimax Correlation（arXiv:2604.09060 2026-04：全局最坏情况依赖最小化 vs 当前 pairwise ρ>0.6 局部判定，CAGR 15.41%/MaxDD 28.89%，小规模参数噪声大记为 Phase 5+ 远期候选）；演进方向 B——相关性突变检测层（Bayes Group 2026-03：2026-03 地缘冲击 Millennium/Point72 各亏 $1.5B，"diversification illusion"正常期低相关 pod 在共同宏观冲击下 tail correlation 飙升，short vs long window ρ 偏离度 shrinkage 是轻量 Phase 3 候选比 MARCD 轻得多）；演进方向 C——BlackRock crowding 警示（2026-04：多策略 pod shop 共享数据/模型导致 crowding，AI 驱动策略加剧收敛，100% AI 项目单一开发者让多策略天然收敛，相关性聚类应从 PnL 层延伸到信号特征层，与 33号 AI Agent Flash Crash 呼应）；§7.4 补 4 条 2026-08 最新实证（AEGIS minimax/Bayes Group 相关性突变/BlackRock crowding/QBase 边际 Sharpe 准入）；§1.1 状态 v1.0.6→v1.0.8 + 依赖 31号 v1.9.0→v1.10.0 + §4.2 33号 v1.6.0→v1.7.0（版本同步）；全网搜索 2026-08-08 最新 portfolio aggregation/firm risk/correlation clustering/crowding 算法，评估选项外更好答案——AEGIS minimax 为本次搜索发现的最优远期候选（全局 vs 局部相关性管理），相关性突变检测为轻量 Phase 3 候选 |
| 2026-08-10 | 1.0.9 | 交叉引用版本同步（31号 v1.10.0→v1.11.0） | §1.1 依赖 31号 v1.10.0→v1.11.0（31号 v1.11.0 补 Conformal Kelly lockbox 样本外负结果 + 降级触发第 5 项，本备忘只消费 Kelly 输出不受算法变更影响，纯版本引用同步）；全网搜索 2026-08-08 最新 Conformal Kelly/Bayesian Kelly/position sizing 算法评估 32号施工算法完整性——结论：§2.1.1 pre_kelly_aggregate + post_kelly_clip 完整伪代码 + §2.10.5 相关性管理演进已覆盖施工所需，无缺失 |
| 2026-08-10 | 1.0.10 | 相关性突变检测学术严谨版背书 + 2026-08 最新研究 | §2.10.5 演进方向 B 补充 Bayesian 动态收缩先验作为学术严谨版远期候选（arXiv:2605.06818 Coulson/Matteson/Wells Cornell 2026-05-07：低秩因子表示+动态收缩先验+multivariate factor stochastic volatility，首次给出动态正则化 Bayesian 模型 posterior contraction 结果 averaged Hellinger distance 显式收敛速率；相比 rolling window/EWMA 平滑掉突变和 DCC 低维参数化限制，动态收缩先验在金融压力期突然局部 shift 场景适应性更强；short/long window ρ 偏离度是工程启发式缺理论保证，Bayesian 动态收缩先验是有 posterior contraction 保证的严谨版，但工程重需 MCMC/VI 推断+小规模 pairwise ρ 参数少工程启发式够用+收敛速率理论保证对个人项目实盘价值有限，记为策略数>8 且 simple short/long window 实测漏检率高时重评）；§7.4 补 1 条 2026 最新实证；全网搜索 2026-08-08 最新 dynamic correlation estimation/portfolio shrinkage prior/Bayesian correlation 算法，评估选项外更好答案——Bayesian 动态收缩先验为演进方向 B 的理论严谨版远期候选（非 Phase 3，工程重+小规模优势不显著） |
| 2026-08-10 | 1.0.11 | degraded 条件1 bug 修复 + 单策略集中度上限 + HBI/CSAD 拥挤度检测 + tierzero 施工参数 + 2026-08-08 最新研究 | §2.1.1 修复 post_kelly_clip degraded 条件1 bug（原 `any(c.get("truncated") for c in [])` 传空列表永不触发→现正确消费 conflicts 参数 + 补 kelly_param_source 参数判定条件5 + 输出补 conflicts_resolved 字段对齐 §2.7 契约）；§2.5.1 补 tierzero 相关性聚类施工参数（30 日 PnL 向量窗口 + ρ>0.6 聚类阈值 + cluster cap=成员 limit 之和×shrinkage_factor + stale snapshot 2 秒暂停，marcelgautsche ρ 分级 0.4/0.7 印证）；新增 §2.10.6 演进方向 D——单策略集中度上限（FLOX PR#183 max_concentration_pct=0.35 补当前缺失的"单策略占比"维度，Phase 3 第四级裁剪候选）+ HBI/CSAD 市场拥挤度检测（laoyulaoyu 2026-07 O(N) 纯价格 HBI<0.3 拥挤降仓/HBI>2.0 独立加仓，可作 degraded 第 6 项触发，BlackRock crowding 最轻量级 A 股可落地方案）；§5 新增"单策略集中度上限+HBI/CSAD"待裁定项；§1.1 依赖 31号 v1.12.0→v1.14.0（版本同步）；§7.4 补 4 条 2026-08 最新实证（FLOX 单策略集中度/go-trader hold-new-entries 语义/laoyulaoyu HBI-CSAD 羊群检测/Pomegra AI crowding 100th 百分位实证）；全网搜索 2026-08-08 最新 firm risk aggregator/portfolio hard limit/crowding detection/position aggregation 算法，评估施工算法完整性+选项外更好答案——结论：degraded bug 已修复，单策略集中度+HBI/CSAD 为本次搜索发现的两项当前缺失维度（均 Phase 3 轻量候选非 MVP），§2.1.1 施工伪代码+§2.10 演进方向完整可施工 |
| 2026-08-10 | 1.0.12 | 交叉引用版本同步：§4.2 阶段3 触发条件+§6 开放问题表 33号 v1.8.0→v2.3.0（2 处 stale 引用修复） | 十五轮审查交叉引用版本漂移扫描：32号 §4.2 演进路径阶段3+§6 开放问题表引用 33_budget_change_handler v1.8.0（实际 frontmatter v2.3.0），系并发会话持续升级 33号 frontmatter 后 32号交叉引用未同步。本次修复 2 处 stale 引用 |
| 2026-08-10 | 1.0.13 | GinkGO PCA+CorrDD 结构层 + 华泰金工风格拥挤度 + MINGLE 因子图远期登记 + 90天规则修订记录补录 + 33号版本漂移修复 | §2.10.5 新增演进方向 E——GinkGO PCA 共同因子暴露预警（VE_1>50% + Herfindahl H>0.4，O(N³) 特征值分解非协方差求逆，检测多策略被同一隐藏因子驱动的分散化假象，pairwise ρ 无法捕捉）+ CorrDD 回撤尾部同步检测（corr(DD_i,DD_j)>0.7，捕捉正常期 ρ 被稀释的回撤期 tail correlation 飙升，与 Bayes Group 2026-03 diversification illusion 对齐），施工参数 60 日 PnL 窗口 + 第 8/9 项 degraded 条件 + Phase 3 候选；§2.10.5 新增演进方向 F——MINGLE 因子图相关性聚类（arXiv:2608.06618 2026-08-06：ADMM 联合学习隐因子+图拓扑，PCA 的图结构扩展，P4+ 远期候选，策略数>8 且 A/B/C/E 漏检率高时重评）；§2.10.6 新增演进方向 D-3——华泰金工风格拥挤度（动量+成交量双维度分域模型，小盘>90%/大盘<10% 分位预警 + 20 日持续期，O(N) 分域统计，指导 G14 三级升级定向降仓，与 HBI/CSAD 递进——HBI 管市场整体羊群度，华泰管哪个风格拥挤，第 7 项 degraded 条件）；§5 待裁定更新（单策略集中度+HBI/CSAD+华泰金工+PCA/CorrDD 四维度合并条目）；§2.10.5 标题+intro 更新（三条→五条 A/B/C/E/F）；§2.10.6 标题+intro 更新（两个→三个维度 D-1/D-2/D-3）；§4.2+§6 33号 v2.3.0→v2.4.0 版本漂移修复（2 处）；补录 90 天相关性规则（§2.5.1 youcanbuildthings 2026-05-06 实证，v1.0.12 未记录的变更）；全网搜索 2026-08-08 最新 portfolio aggregation/correlation detection/style crowding 算法，评估选项外更好答案——GinkGO PCA+CorrDD 填补"共同因子暴露+回撤尾部同步"空白，华泰金工填补"风格拥挤定向降仓"空白，MINGLE 因子图登记 P4+ 远期（3-5 策略规模现有 A/B/C/E 够用），均非 MVP |
| 2026-08-10 | 1.0.14 | Copula 尾部依赖理论背书 + 31号版本漂移修复 + 2026-08-08 最新研究 | §2.10.5 演进方向 E 后补 Copula 尾部依赖理论根基（metricgate 2026-06 + Sklar 定理：相关性度量平均共动，Copula 决定尾部发生什么——两个组合可有完全相同相关矩阵却因 Copula 族不同有截然不同联合崩盘概率；Gaussian Copula λ_L=0 系统性低估崩盘概率 vs t-Copula λ_L>0 贴近 A 股尾部同步；CorrDD 是 Copula 尾部依赖思想的非参数无分布工程轻量替代，无需边际分布/Copula 族选择/参数拟合；与方向 B 互补——方向 B 管 PnL 相关性突变，CorrDD 管回撤尾部同步；与 31号 §2.3.1 Taleb 胖尾论点同源——两者均论证线性相关性/方差在厚尾场景失效，31号管单标的 Kelly 仓位层，本条管多策略组合相关性层；记为 P4+ 理论背书非 Phase 3 施工，重评条件为 CorrDD 实测漏检或策略数>8）；§1.1 31号 v1.15.0→v1.16.0 版本漂移修复（31号本轮补 Taleb 胖尾 quarter-Kelly 理论背书）；全网搜索 2026-08-08 最新 portfolio aggregation/correlation/copula tail dependence 算法，评估选项外更好答案——Copula 尾部依赖为演进方向 E CorrDD 的理论补强（非算法变更，CorrDD 已覆盖 Phase 3 实用需求，Copula 显式拟合登记 P4+ 远期），施工算法完整性不变 |
| 2026-08-10 | 1.0.15 | §2.10.7 新增 **Fassino 风险预算 Cauchy 不动点**（Fassino 2026-03 arXiv:2603.17415）——Cauchy 序列不动点迭代 `w_{k+1} = T(w_k) = diag(Σw)^{-1/2}×b/||·||` 直接构造风险预算组合，Banach 不动点定理保证存在唯一性（压缩映射），避免辅助优化问题 + O(N²) per iteration 替代凸优化 O(N³) + 纯 numpy 实现无 cvxpy 依赖。**与 §3.4 拒绝风险预算的关系**：直接解决拒绝理由②（辅助优化复杂），但①（需估协方差）仍成立。**与 §2.6 不做 MVO/不估协方差的关系**：仍需完整 Σ 矩阵，与核心原则冲突，但为"未来若做风险预算"提供更优求解算法。**与 31号 §3.9 Tepelyan 的关系**：Tepelyan 突破 Kelly 组合爆炸（仅需 pairwise ρ），Fassino 突破风险预算优化复杂度（需完整 Σ），两者代表协方差估计深度的两个层级。列为 Phase 4 远期（非 Phase 3），前提是 §2.10.5 相关性管理演进已建立 Σ 估计能力。§1.1 依赖 31号 v1.16.0→v1.17.0 版本同步 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。登记搜索 agent 返回的 6 项远期候选算法之一——Fassino 是风险预算的求解复杂度突破（凸优化→不动点迭代），使 §3.4 拒绝理由②失效但①仍成立，属"未来若做风险预算"的更优求解算法储备非 MVP 施工 |
| 2026-08-10 | 1.0.16 | Step 1b 流动性硬上限裁剪执行 + §1.4 硬上限参数清单补流动性口径 + 31号版本同步 v1.17.0→v1.18.0 | 十九次审查发现 31号 §2.4.4 新增流动性硬上限（ADV 口径）后，32号作为执行层须同步补施工算法。§2.3 裁剪伪代码 Step 1 后新增 Step 1b——流动性硬上限裁剪执行（引用 31号 §2.4.4 阈值与口径，本步执行：ADV_20d_P25 最坏情况 + >20% ADV 削到 20% severe 档 + >10% ADV 削半 moderate 档 + ADV 缺失降级取同行业中位数 + constraint_checks["liquidity_cap"] 记录 tier/adv_pct/capped_at_adv）；§1.4 约束条件 31号 §2.4 硬上限参数清单补"§2.4.4 流动性 ADV 口径 20%/10% 两档"；§1.1 依赖 31号 v1.17.0→v1.18.0 版本同步。施工算法完整性——Step 1 单票资金口径 + Step 1b 流动性口径 + Step 2 行业 + Step 3 总仓位 + Step 4 现金 五步级联裁剪链完整，constraint_checks 覆盖 single_name/liquidity_cap/sector/total_exposure 四维度 |
| 2026-08-10 | 1.0.17 | §2.10.8 Kakinaga & Umeno MFCCA 多重分形组合配置（Phase 4 远期） + §2.10.9 Hsieh & Gan Certified Wasserstein DRO LP（Phase 5+ 远期）两项协方差/风险泛函演进候选登记 | 二十四次审查全网搜索 2026-08-08 最新 portfolio allocation/risk functional/DRO 算法，搜索 agent 返回 10 篇前沿论文筛除已登记/不适配，登记 2 项高价值远期候选：① §2.10.8 Kakinaga & Umeno 2026-08-05 arXiv:2608.04987——用 MFCCA 有符号波动函数 F_xy(q,s) 替代 w^TΣw 风险泛函，符号保留（同向/反向运动以相反符号贡献风险）+ 多尺度（s 时间尺度）+ q=2 退化为 MV（MFCCA 是 MV 严格推广）+ 实证 VaR/ES/MaxDD 均低于 MV。直接解决 §3.4 拒绝风险预算理由①（无 Σ 需求，用 F_xy 替代），间接缓解③（F_xy 多尺度对 regime 转折更鲁棒），但②（辅助优化复杂度）仍成立——Kakinaga + Fassino 组合可同时解决①②。与 36号 §4.13 MFCCA 方法论（arXiv:2608.03968 同第一作者不同 arXiv ID）正交：36号管输入诊断（检测 Σ regime 转变），32号管输出决策（替代 Σ 进入配置）。列为 Phase 4 远期（与 Fassino 同期，前提是 36号 §4.13 已建立 F_xy 估计能力）；② §2.10.9 Hsieh & Gan 2026-08-07 arXiv:2608.07032——多项式规模 LP 逼近 Wasserstein DRO 期望效用组合优化，支撑超平面 majorize 效用 + 对偶化支撑子问题 + 统一逼近误差证书（certified）+ O(N×K) 可扩展到 1000 资产。解决 §2.6 拒绝 MVO 的"优化器放大输入噪声"——Wasserstein 球显式建模分布不确定性对冲噪声。与 Fassino/Kakinaga 构成协方差/风险泛函演进三级路径：Fassino（保 w^TΣw + 不动点求解）→ Kakinaga（F_xy 替代 w^TΣw + 凸优化求解）→ Hsieh（Wasserstein 球 DRO + LP 求解）。列为 Phase 5+ 远期（晚于 Fassino/Kakinaga，三层抽象对 MVP/Phase 4 属过度工程，仅当协方差感知配置证实边际收益且策略/资产规模扩展到 LP 优势显现时评估）。施工算法完整性结论：32 号施工流程算法闭环无缺失独立环节，2 项均为远期候选登记非施工算法缺失 |
| 2026-08-10 | 1.0.18 | §2.10.5 E 补 Absorption Ratio 经典基线背书 + Hammond 2026 实证验证 + VRC Fragility Score 理论参照 | 二十一次审查全网搜索 2026-08-08 最新 market fragility/correlation breakdown/regime detection 算法。§2.10.5 E（GinkGO PCA VE_1）补三项：① Absorption Ratio（Kritzman/Li/Page/Rigobon 2010）经典基线背书——GinkGO PCA 的 VE_1 本质是 Absorption Ratio 的 k=1 特例（Absorption Ratio 定义为前 k=N/5 个特征向量解释的总方差比例），VE_1 > 50% 阈值有经典文献背书非经验拍脑袋；② Hammond 2026-05 "Geometric Observables for Financial Regime Detection" 17 危机窗口 46 方法面板实证——Absorption Ratio（d=0.80）是最强经典基线（量子启发 Reduced State Purity d=0.83 排第一但 |ρ|≈0.13 与经典通道不相关可互补，Berry Phase Rate d=0.72 OOS 中位数最高），进一步确认 PCA 特征值集中度是危机检测最可靠经典指标；③ Verma 2026-04 VRC Fragility Score（DCC+MST+Absorption Ratio+因子相关性+跨资产背离+隐含vs实现相关性价差+网络连通性 7 组件）核心论点"correlation breakdown is not a consequence of crisis, it's the mechanism through which crisis propagates"为 §2.10.5 A/B/C/E/F 多层相关性管理提供理论背书，但 7 组件合成对个人项目属过度工程（多组件+专有复合指标+需 DCC/MST/隐含相关性数据）仅作理论参照不施工。QCML 量子启发几何观测登记 Phase 5+ 远期（工程重需 spectral metric learning + 小规模策略数优势不显著）。施工算法完整性结论：32 号施工流程算法闭环无缺失独立环节，本次为经典基线背书+2026 实证验证+理论参照补充非施工算法变更 |
| 2026-08-10 | 1.0.19 | pre_kelly/post_kelly 两段伪代码缺陷修复 A-G 闭环 + 交叉引用版本漂移修复（31号 v1.18.0→v1.22.0、33号 v2.4.0→v2.9.0 共 3 处） | 用户要求持续改进。审计 32号 §2.1.1 施工伪代码发现 7 项缺陷闭环修复：A——constraint_checks 初始化缺 liquidity_cap 键致 Step 1b 流动性裁剪 KeyError，补 `{"triggered": False, "cuts": []}`；B——degraded 降级条件遗漏 liquidity_cap 触发，G14 BudgetChangeHandler 无法感知流动性降级，补 `or constraint_checks["liquidity_cap"]["triggered"]`；C——Step 1b 引用未定义变量 adv_data/sector_adv_median，改为 adv_data 作参数传入 + sector_adv_median 从 adv_data 派生；D——Step 1b 用 total_capital 但函数签名是 total_budget，口径统一为 total_budget；E——Step 1b 流动性 ADV 裁剪施工算法补全（severe 档 >20% ADV 削到 20% + moderate 档 >10% ADV 削半 + ADV 缺失降级同行业中位数）；F——contributions 数据流断裂（归因数据丢失）：PreKellyResult 仅 3 字段未含 contributions，pre_kelly_aggregate 内部构建 contributions 却未通过 return 传出，post_kelly_clip 的 contributions 参数永远 None 致 firm_positions[symbol]["contributions"] 写空 dict——修复：PreKellyResult 增 contributions 字段 + pre_kelly_aggregate return 带上 contributions + 施工要点 1 补 contributions 数据传递说明；G——sector_overlay_active 参数注释澄清（原"当前未消费"易误判为死代码，实为 §2.5.1 行业偏离裁剪 overlay 档 ±15% vs ±10% 的接口前向兼容预留，待 D-FACTOR 行业分类确认后连同偏离裁剪一起消费）。§1.1 状态行 v1.0.18→v1.0.19 + 补 A-G 修复说明。交叉引用版本漂移：§1.1 依赖 31号 v1.18.0→v1.22.0、§4.2 阶段3 + §6 开放问题表 33号 v2.4.0→v2.9.0（3 处 stale 引用，系并发会话持续升级 31/33号 frontmatter 后 32号交叉引用未同步）。施工算法完整性结论：A-G 修复后 §2.1.1 pre_kelly_aggregate + post_kelly_clip 两段伪代码数据流完整闭环（contributions 归因链路贯通 + degraded 5 条件全覆盖 + 流动性裁剪可执行），无新施工算法缺失 |
| 2026-08-10 | 1.0.20 | （补录）文档-代码一致性修复：§1.2 L39+§2.1 L76 代码状态描述从"骨架/待拆分"更新为"已施工 production" | 六十五轮文档-代码一致性审查：MOD-POS-021 实际已施工完成（两段拆分 pre_kelly_aggregate+post_kelly_clip 已实现、aggregate 便捷入口串联、54 单元测试全绿 0.09s、MATURITY=production），§1.2/§2.1 两处描述滞后修正。**本条目当时漏记入修订记录，v1.0.21 补录**——教训：frontmatter 版本号与 §1.1 状态行升级时必须同步写修订记录，否则出现"版本号前进但修订记录断档" |
| 2026-08-12 | 1.0.21 | 灾后修复 + 全量设施盘点 + 第 3 轮算法审查新发现：① **33 号骨架化交叉引用修正 4 处**——33_budget_change_handler 在 2026-08-11 git clean 灾难（#ARCH-GIT-CLEAN-GUARD-FIX）中内容丢失回退骨架 v0.1.0（v2.x 定稿内容 git 历史无记录），§4.2 阶段 3 + §6 接口契约行/dead-band 行/lot 对齐行引用全部修正为"代码 docstring 为临时真源"；② **§4.2 演进路径三阶段状态更新**——MVP/阶段 2 标记已完成（2026-08-12 核对源码在位），阶段 3 标"代码就绪/文档待重建"；③ **§6 开放问题**：拆分行关闭（✅ 已完成）、新增 6 行——**⚠️ P0 字段名三方漂移**（代码核对发现：`TargetPortfolio.positions`/`budget` vs `_sum_by_symbol` duck-typing 取 `target_portfolio`/`budget_used`，直接传对象静默产出全现金组合不报错；修复归代码施工+补 TargetPortfolio 输入路径回归测试）+ **T+1 可卖持仓口径假设**（§2.3 净额截断 current_holdings 应为 T+1 口径可卖权重，供数方 position_reconciler 需按此口径）+ 测试丢失重建/registry 未登记/depgraph 滞后三行；④ **§7.2 表补"当前状态（2026-08-12 核对源码）"列**；⑤ **§7.6 新增已施工设施盘点**（规则 #11）：G13 数据流核心链 5 模块 + 参数供给方 + 代码-文档契约核对结论（§2.1.1 A-G 修复与代码全部一致/§2.7 契约字段一致/INVARIANTS 一致，唯一不一致=字段名漂移）；⑥ §9 补录 v1.0.20 漏记条目；⑦ §1.1 依赖 31号 v1.18.0→v1.23.0 版本漂移修复 | 架构审查任务（30/32 号）第 1-3 轮：盘点发现 33 号骨架化致 4 处引用悬空、§4.2 表滞后、修订记录缺 v1.0.20、§7.2 无状态列、缺设施盘点节；第 3 轮算法审查新发现字段名三方漂移 P0 断裂风险 + T+1 可卖口径假设未明示。按"事实性漂移修复+决策类登记开放问题"原则处置。**施工方式**：worktree 隔离（主区并发会话持续回退致修改 2 次丢失，用户裁定改 worktree 施工） |
