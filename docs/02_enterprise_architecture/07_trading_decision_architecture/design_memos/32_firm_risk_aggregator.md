---
ttl: permanent
doc_type: architecture_view
title: FirmRiskAggregator 多策略聚合风控逻辑
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: firm_risk_aggregator
scope: 07_trading_decision_architecture
---

# FirmRiskAggregator 多策略聚合风控逻辑

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G13 主题组派生，将 FirmRiskAggregator 的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：Citadel pod 模型 firm 层风险聚合；Morwane risk-parity-throttle；A 股单票 8% 硬上限（公募双十约束简化）；行业集中度约束；不做 MVO/协方差估计的 O(N) 聚合（30_multi_strategy_concurrency §3.1 已拒绝 MVO）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G13 FirmRiskAggregator 逻辑 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | G12（仓位算法，[31_position_sizing](31_position_sizing.md) 已定稿 v1.2.0）、G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)）、G18（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)） |
| 对标 | Citadel pod 模型 firm 层风险聚合 / Morwane risk-parity-throttle |
| 正交性 | ✅ 与 regime 正交（聚合逻辑不依赖 regime，但聚合结果受 regime 节流影响） |
| 优先级 | P2 |
| 状态 | ✅ active — 按标的求和+硬上限裁剪+行业约束+冲突处理+firm_target_portfolio 契约已定稿 |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 采用 Model A 多策略并发架构：每个策略独立 sleeve（独立账本），各自产出 `sleeve_target_portfolio`。FirmRiskAggregator 负责将所有 sleeve 的目标组合聚合为 firm 级 `firm_target_portfolio`，并施加 firm 级硬约束。

**核心定位**（30_multi_strategy_concurrency §2.3）：聚合器是"裁剪者"而非"优化器"——不做 MVO、不做协方差估计，只做 O(N) 的按标的求和 + 硬上限裁剪。复杂的风险优化在各 sleeve 内部完成，聚合层只保证 firm 级硬约束不被突破。

### 2.2 核心问题

1. **按标的自然叠加**：多策略可能同时持有同一标的，需自然求和得到 firm 级持仓。
2. **单票硬上限**：单票总持仓 >8% 需按比例削（A 股公募双十约束简化，私募可更宽松但 8% 是安全线）。
3. **行业/总仓位约束**：行业集中度 ≤30%，总仓位 ≤100%（含现金管理）。
4. **冲突标的处理**：一策略买入、另一策略卖出同一标的 → 净额处理（多空对冲），而非优先级裁决。
5. **不做 MVO**：聚合层不做协方差估计和均值方差优化（30_multi_strategy_concurrency §3.1 已拒绝），保持 O(N) 复杂度。
6. **firm_target_portfolio 契约**：输出标准化契约，供 [40_execution_broker](40_execution_broker.md) 执行。

### 2.3 约束条件

- **O(N) 复杂度**：N=标的数，聚合必须在单次遍历内完成，不可做 O(N²) 协方差计算
- **不做 MVO**：30_multi_strategy_concurrency §3.1 明确拒绝 MVO，聚合层只裁剪不优化
- **与 Kill Switch 联动**：Kill Switch 触发时，聚合器输出全空 firm_target_portfolio
- **与回撤 Protocol 联动**：回撤触发减仓时，聚合器按 Shrinkage 缩减各 sleeve 输入

## 3. 决策

### 3.1 架构定义

FirmRiskAggregator 由聚合层、约束层、输出层三层构成：

```
聚合层: 各 sleeve_target_portfolio → 按标的求和(净额) → firm_raw_portfolio
                                                        ↓
约束层: 单票硬上限裁剪 → 行业集中度约束 → 总仓位约束 → Kill Switch/回撤联动
                                                        ↓
输出层: firm_target_portfolio 契约 → 40_execution_broker
```

### 3.2 按标的求和算法（聚合层）

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import numpy as np


@dataclass
class SleevePosition:
    """单 sleeve 的单标的持仓。"""
    symbol: str
    weight: float              # 权重（正=多头，负=空头，A 股无空头故通常为正）
    strategy_id: str
    notional: float            # 名义额（元）


@dataclass
class SleeveTargetPortfolio:
    """单 sleeve 的目标组合。"""
    strategy_id: str
    positions: list[SleevePosition]
    total_weight: float        # sleeve 总权重
    sleeve_budget: float       # sleeve 资金预算比例


@dataclass
class FirmPosition:
    """firm 级单标的持仓（聚合后）。"""
    symbol: str
    total_weight: float        # 聚合后总权重
    total_notional: float      # 聚合后名义额
    contributing_strategies: list[str]  # 贡献策略列表
    is_capped: bool            # 是否被硬上限裁剪
    cap_ratio: float           # 裁剪比例（1.0=未裁剪）


@dataclass
class FirmTargetPortfolio:
    """firm 级目标组合——聚合器输出契约。"""
    positions: dict[str, FirmPosition]   # {symbol: FirmPosition}
    total_weight: float                   # 总仓位
    industry_exposure: dict[str, float]   # {行业: 权重}
    cash_weight: float                    # 现金权重
    kill_switch_active: bool              # Kill Switch 是否激活
    drawdown_shrinkage: float             # 回撤缩减系数
    timestamp: str


def aggregate_sleeves(
    sleeve_portfolios: list[SleeveTargetPortfolio],
    symbol_to_industry: dict[str, str],   # {symbol: 行业}
) -> dict[str, FirmPosition]:
    """按标的求和——自然叠加各 sleeve 持仓（O(N) 复杂度）。

    核心逻辑（30_multi_strategy_concurrency §2.3）：
    - 多策略持有同一标的 → 权重相加
    - 冲突标的（一买一卖）→ 净额处理（多空对冲）
    - 不做优先级裁决，净额即最终持仓

    复杂度：O(N)，N=总持仓数（跨所有 sleeve）
    """
    firm_positions: dict[str, FirmPosition] = {}

    for sleeve in sleeve_portfolios:
        for pos in sleeve.positions:
            if pos.symbol not in firm_positions:
                firm_positions[pos.symbol] = FirmPosition(
                    symbol=pos.symbol,
                    total_weight=0.0,
                    total_notional=0.0,
                    contributing_strategies=[],
                    is_capped=False,
                    cap_ratio=1.0,
                )
            fp = firm_positions[pos.symbol]
            fp.total_weight += pos.weight
            fp.total_notional += pos.notional
            if pos.strategy_id not in fp.contributing_strategies:
                fp.contributing_strategies.append(pos.strategy_id)

    return firm_positions
```

### 3.3 单票硬上限裁剪算法（约束层）

```python
def apply_single_position_cap(
    firm_positions: dict[str, FirmPosition],
    max_single_position: float = 0.08,   # 单票 8% 硬上限
) -> dict[str, FirmPosition]:
    """单票硬上限裁剪——超过 8% 按比例削减各策略贡献。

    裁剪逻辑：
    - 若某标的 total_weight > max_single_position
    - 按各策略贡献比例等比削减（公平裁剪，不偏袒任何策略）
    - cap_ratio = max_single_position / total_weight
    - 削减后 total_weight = max_single_position

    注意：裁剪是"目标组合"层面的，实际执行时需生成对应的卖出指令。
    被裁剪的权重释放为现金，不重新分配给其他标的（避免聚合层做优化）。
    """
    for symbol, fp in firm_positions.items():
        if fp.total_weight > max_single_position:
            cap_ratio = max_single_position / fp.total_weight
            fp.total_weight *= cap_ratio
            fp.total_notional *= cap_ratio
            fp.is_capped = True
            fp.cap_ratio = cap_ratio

    return firm_positions
```

### 3.4 行业集中度约束算法（约束层）

```python
def apply_industry_concentration_cap(
    firm_positions: dict[str, FirmPosition],
    symbol_to_industry: dict[str, str],
    max_industry_concentration: float = 0.30,  # 单行业 30% 上限
) -> dict[str, FirmPosition]:
    """行业集中度约束——单行业权重超过 30% 按比例削减。

    裁剪逻辑：
    - 按 symbol_to_industry 映射计算各行业总权重
    - 若某行业总权重 > max_industry_concentration
    - 该行业所有标的按等比削减（cap_ratio = 上限/实际）
    - 削减后行业总权重 = max_industry_concentration

    注意：行业分类使用申万一级行业（31 个），避免过细导致约束失效。
    """
    # 计算各行业总权重
    industry_weights: dict[str, float] = {}
    for symbol, fp in firm_positions.items():
        industry = symbol_to_industry.get(symbol, "UNKNOWN")
        industry_weights[industry] = industry_weights.get(industry, 0.0) + fp.total_weight

    # 裁剪超限行业
    for industry, ind_weight in industry_weights.items():
        if ind_weight > max_industry_concentration:
            cap_ratio = max_industry_concentration / ind_weight
            for symbol, fp in firm_positions.items():
                if symbol_to_industry.get(symbol, "UNKNOWN") == industry:
                    fp.total_weight *= cap_ratio
                    fp.total_notional *= cap_ratio
                    fp.is_capped = True
                    fp.cap_ratio = min(fp.cap_ratio, cap_ratio)

    return firm_positions
```

### 3.5 总仓位与 Kill Switch/回撤联动算法（约束层）

```python
def apply_total_position_and_risk_linkage(
    firm_positions: dict[str, FirmPosition],
    max_total_position: float = 1.0,       # 总仓位上限 100%
    kill_switch_active: bool = False,      # Kill Switch 状态
    drawdown_shrinkage: float = 1.0,       # 回撤缩减系数 [0, 1]
) -> tuple[dict[str, FirmPosition], float]:
    """总仓位约束 + Kill Switch/回撤联动。

    联动逻辑：
    1. Kill Switch 激活 → 全部清仓，输出空组合（fail-closed）
    2. 回撤缩减 → 所有持仓乘 drawdown_shrinkage（来自 [35_drawdown_protocol_impl]）
    3. 总仓位超限 → 等比削减所有持仓

    回撤缩减系数映射（35_drawdown_protocol_impl §3.2）：
    - NORMAL: 1.0（不减仓）
    - WARNING(8-15%): 0.8（减 20%）
    - REDUCING(15-20%): 0.5（减 50%）
    - HALTED(20-25%): 0.0（全部停止）
    - LIQUIDATING(>25%): 0.0（强制清仓）
    """
    # Kill Switch 优先——fail-closed
    if kill_switch_active:
        for fp in firm_positions.values():
            fp.total_weight = 0.0
            fp.total_notional = 0.0
            fp.is_capped = True
            fp.cap_ratio = 0.0
        return firm_positions, 0.0

    # 回撤缩减
    if drawdown_shrinkage < 1.0:
        for fp in firm_positions.values():
            fp.total_weight *= drawdown_shrinkage
            fp.total_notional *= drawdown_shrinkage
            if drawdown_shrinkage < 1.0:
                fp.is_capped = True
                fp.cap_ratio *= drawdown_shrinkage

    # 总仓位约束
    total_weight = sum(fp.total_weight for fp in firm_positions.values())
    if total_weight > max_total_position and total_weight > 0:
        scale = max_total_position / total_weight
        for fp in firm_positions.values():
            fp.total_weight *= scale
            fp.total_notional *= scale
            fp.is_capped = True
            fp.cap_ratio *= scale

    cash_weight = max(0.0, 1.0 - sum(fp.total_weight for fp in firm_positions.values()))
    return firm_positions, cash_weight


def compute_industry_exposure(
    firm_positions: dict[str, FirmPosition],
    symbol_to_industry: dict[str, str],
) -> dict[str, float]:
    """计算行业暴露——用于监控和报告。"""
    industry_exposure: dict[str, float] = {}
    for symbol, fp in firm_positions.items():
        industry = symbol_to_industry.get(symbol, "UNKNOWN")
        industry_exposure[industry] = industry_exposure.get(industry, 0.0) + fp.total_weight
    return industry_exposure
```

### 3.6 firm_target_portfolio 输出契约（输出层）

```python
from datetime import datetime


def build_firm_target_portfolio(
    sleeve_portfolios: list[SleeveTargetPortfolio],
    symbol_to_industry: dict[str, str],
    max_single_position: float = 0.08,
    max_industry_concentration: float = 0.30,
    max_total_position: float = 1.0,
    kill_switch_active: bool = False,
    drawdown_shrinkage: float = 1.0,
) -> FirmTargetPortfolio:
    """构建 firm_target_portfolio——聚合器主入口（O(N) 复杂度）。

    完整流程：
    1. 按标的求和（§3.2）
    2. 单票硬上限裁剪（§3.3）
    3. 行业集中度约束（§3.4）
    4. 总仓位 + Kill Switch/回撤联动（§3.5）
    5. 计算行业暴露和现金权重
    6. 输出 firm_target_portfolio 契约

    输出契约供 40_execution_broker 执行：
    - positions: {symbol: FirmPosition} 目标持仓
    - 40_execution_broker 对比当前持仓与目标持仓，生成买卖指令
    """
    # 步骤 1：按标的求和
    firm_positions = aggregate_sleeves(sleeve_portfolios, symbol_to_industry)

    # 步骤 2：单票硬上限
    firm_positions = apply_single_position_cap(firm_positions, max_single_position)

    # 步骤 3：行业集中度
    firm_positions = apply_industry_concentration_cap(
        firm_positions, symbol_to_industry, max_industry_concentration
    )

    # 步骤 4：总仓位 + Kill Switch/回撤
    firm_positions, cash_weight = apply_total_position_and_risk_linkage(
        firm_positions, max_total_position, kill_switch_active, drawdown_shrinkage
    )

    # 步骤 5：行业暴露
    industry_exposure = compute_industry_exposure(firm_positions, symbol_to_industry)

    # 步骤 6：输出契约
    return FirmTargetPortfolio(
        positions=firm_positions,
        total_weight=sum(fp.total_weight for fp in firm_positions.values()),
        industry_exposure=industry_exposure,
        cash_weight=cash_weight,
        kill_switch_active=kill_switch_active,
        drawdown_shrinkage=drawdown_shrinkage,
        timestamp=datetime.now().isoformat(),
    )
```

### 3.7 O(N) 复杂度保证

| 步骤 | 复杂度 | 说明 |
|---|---|---|
| 按标的求和 | O(N) | N=总持仓数，单次遍历 |
| 单票硬上限裁剪 | O(M) | M=标的数 ≤ N |
| 行业集中度约束 | O(M) | M=标的数 |
| 总仓位约束 | O(M) | M=标的数 |
| Kill Switch/回撤 | O(M) | M=标的数 |
| **总计** | **O(N)** | 线性复杂度，无 O(N²) 协方差计算 |

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **MVO 优化** | 均值方差优化 firm 级组合 | 30_multi_strategy_concurrency §3.1 已拒绝；需 O(N²) 协方差估计；聚合层只裁剪不优化 |
| **协方差估计** | 估计标的间协方差做风险预算 | O(N²) 复杂度；协方差估计噪声大；MVP 阶段过度工程 |
| **优先级裁决** | 冲突标的按策略优先级裁决 | 净额处理更简单且符合对冲逻辑；优先级需人工设定有偏 |
| **风险平价** | 按风险贡献分配 | 需协方差估计；O(N²)；Phase 1.5+ 评估 |
| **层级裁剪** | 按 sleeve 优先级分层裁剪 | 不公平；等比裁剪更透明可审计 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **单票硬上限** | 8% | A 股公募双十约束简化；私募安全线 |
| **行业集中度** | 30% | 申万一级行业 31 个，30% 防止行业押注 |
| **总仓位** | 100% | 含现金管理，不满仓留流动性 |
| **现金下限** | 5% | 最低流动性缓冲 |
| **Kill Switch** | 全清仓 | fail-closed，激活即全空 |

**演进路径**：
- MVP：按标的求和 + 硬上限裁剪 + 行业约束 + Kill Switch/回撤联动（O(N)）
- Phase 1.5：风险平价评估（需协方差数据积累）
- Phase 2：动态行业约束（regime 条件调整行业上限）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **风险平价** | 需协方差数据 | Phase 1.5+ 积累 6 月 P&L 后 |
| **动态行业约束** | 需 regime 条件映射 | Phase 2+ regime 验证后 |
| **sleeve 优先级** | 净额处理已够 | 多策略冲突高频出现时重评 |

## 7. 待定问题（讨论要点）

- [x] ① 按标的求和（自然叠加）→ §3.2 定型
- [x] ② 单票硬上限裁剪（>8% 按比例削）→ §3.3 定型
- [x] ③ 行业/总仓位硬约束 → §3.4/§3.5 定型
- [x] ④ 冲突标的处理（净额）→ §3.2 定型（净额求和）
- [x] ⑤ 不做 MVO，不做协方差估计 → §3.7 O(N) 保证
- [x] ⑥ 输出 firm_target_portfolio 契约 → §3.6 定型
- [x] ⑦ O(N) 复杂度保证 → §3.7 定型

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G13
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 / §2.3 / §3.1
- [31_position_sizing](31_position_sizing.md)（G12 产出物，sleeve 级仓位输入）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，回撤缩减系数来源）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，流动性危机联动）
- [40_execution_broker](40_execution_broker.md)（firm_target_portfolio 消费方）
- [33_budget_change_handler](33_budget_change_handler.md)（G14，budget 变更联动）
- battle_map_08_position_management（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G13 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 补齐按标的求和+硬上限裁剪+行业约束+Kill Switch/回撤联动+firm_target_portfolio 契约+O(N) 保证 | 聚合层只裁剪不优化，整合 30_multi_strategy_concurrency §2.3/§3.1 决策 |
