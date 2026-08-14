---
ttl: permanent
doc_type: architecture_view
title: FirmRiskAggregator 逻辑（组合层风险聚合）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.23"
date: 2026-08-14
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
| 状态 | ✅ 已定稿 v1.0.23（§2.1.1 伪代码 A-G 修复闭环；§2.10.7 Fassino Cauchy 不动点 + §2.10.8 Kakinaga MFCCA + §2.10.9 Hsieh Certified Wasserstein DRO LP 三项远期候选登记（协方差/风险泛函演进三级路径 Fassino→Kakinaga→Hsieh）；§2.11 作战地图口径裁定三环节闭合（BM-SEL-21/BM-RC-07-B/BM-RC-07-C）；已施工 production（8e4d60d5，60 测试全绿）。历史细节见 §9 修订记录） |

### 1.2 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1，不能做空）
- 多策略并发架构已定稿为 Model A（独立账本 + firm 风险聚合），见 [30_multi_strategy_concurrency §2](30_multi_strategy_concurrency.md)
- 3-5 个 StrategyBook 各自产出 `StrategyTarget`（粗仓位），需在 firm 层聚合为统一的 `FirmTargetPortfolio`
- [MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) **✅ 已施工（firm_risk_aggregator.py，8e4d60d5，60 测试）** production：两段接口 `pre_kelly_aggregate()`+`post_kelly_clip()` 已实现，`aggregate()` 便捷入口内部串联两段+Kelly passthrough，MATURITY=production。§2.1.1 施工伪代码 A-G 修复全部在位（constraint_checks liquidity_cap 键 / degraded 条件 / adv_data 参数化 / total_budget 口径 / contributions 透传 / sector_overlay_active 预留）

### 1.3 核心问题
30_multi_strategy_concurrency §2.2 已锁定 FirmRiskAggregator 的**职能框架**（求和+硬上限裁剪+冲突处理，不做 MVO），但未定义：
- 求和的确切语义（权重直接相加？budget 口径如何统一？）
- 单票硬上限裁剪的执行算法（按比例削 vs 按策略优先级截断）
- 行业/总仓位硬约束的执行顺序与口径
- 冲突标的（一策略买一策略卖同标的）如何处理
- 输出 `FirmTargetPortfolio` 的数据结构契约
- O(N) 复杂度如何保证（不退化为准 O(N²) 的优化器）

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

> **✅ 已施工（firm_risk_aggregator.py，8e4d60d5，60 测试）**：[MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) 已按设计意图拆分为两段——`pre_kelly_aggregate()`（求和+冲突净额）+ `post_kelly_clip()`（单票/流动性/行业/总仓位/现金），由 MOD-POS-001 在中间调用 Kelly。`aggregate()` 便捷入口内部串联 `pre_kelly_aggregate → kelly_fn(passthrough) → post_kelly_clip`，实现"先精算后兜底"（31_position_sizing §2.1）。MATURITY=production。

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
> 代码实现另含条件 4b：**流动性裁剪触发**（`constraint_checks["liquidity_cap"]["triggered"]`，v1.0.19 补，G14 感知流动性降级）。
>
> **degraded=False** 的含义：所有策略意愿完全表达、无裁剪触发、Kelly 主源（密度 PDF）正常。degraded 不等于错误——降级是防御性安全网正常工作的表现，但需 G14 审计是否需三级升级收敛

### 2.1.1 施工算法实现（pre_kelly_aggregate + post_kelly_clip 完整伪代码）

> **✅ 已施工（firm_risk_aggregator.py，8e4d60d5，60 测试）**：完整伪代码已落为 [MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) production 代码（651 行，0 处 NotImplementedError，MATURITY=production），本节折叠为接口级摘要，代码为真源。

**常量**（参数来源：31_position_sizing §2.4）：`SINGLE_NAME_CAP=0.08`（单票 8% 总资金口径）/ `SECTOR_DEVIATION_CAP=0.10`（±10%）/ `SECTOR_DEVIATION_CAP_OVERLAY=0.15`（叠加态 ±15%）/ `SECTOR_ABSOLUTE_CAP=0.30`（绝对 30%）/ `CASH_SYMBOL="CASH"`（豁免裁剪）。**PreKellyResult 字段**：`summed_weights: dict[str, float]`（归一后权重，含净额截断）+ `conflicts: list[dict]`（ConflictRecord）+ `total_exposure_pre_kelly: float` + `contributions: dict[str, dict[str, float]]`（symbol→{strategy_id: 贡献权重}，v1.0.19 补，须透传 post_kelly_clip 写入 `firm_positions[symbol]["contributions"]` 归因）。

**pre_kelly_aggregate 步骤**：Step 1 budget 口径归一化求和——`account_weight = tp_weight × budget_used / total_budget`（CASH 跳过，§2.4 豁免），同步累计 `contributions`；Step 2 冲突净额——同 symbol 兼有正/负贡献即冲突，`net<0` 时 `final = max(0, net + current_holdings[symbol])` 截断并记 ConflictRecord（`truncated`/`final_weight`/`truncated_amount`），`net≥0` 或同向直接用求和值。

**post_kelly_clip 级联裁剪**（每步输入=上步输出，只减不增，单调收敛）：
- **Step 1 单票**：>8% 按比例削至 8%，记 `cut_ratio`；
- **Step 1b 流动性（31号 §2.4.4 ADV 口径）**：`adv_data: symbol→{adv_20d_p25}` 参数化传入；`position_value = weight × total_budget`，`adv_pct = position_value / adv_20d_p25`；`adv_pct>0.20` severe 档削到 20% ADV，`>0.10` moderate 档削半；ADV 缺失/停牌降级取同行业 ADV 中位数（`sector_adv_median` 从 adv_data 派生）；记入 `constraint_checks["liquidity_cap"]`（tier/adv_pct/capped_at_adv）；
- **Step 2 行业**：归类求和后超绝对 30% 的行业内按比例削（偏离 ±10%/±15% 裁剪需行业基准权重，待 D-FACTOR 行业分类模块确认，§6）；
- **Step 3 总仓位**：`sum(clipped) > regime_cap` 时等比缩放（Kelly 层 §2.3.5 已 pro-rata 归一化则自动跳过 `triggered=False`，不双重缩放，§6）；
- **Step 4 现金**：`CASH = total_budget − total_exposure` 残差（浮点负值兜底 0）。

**post_kelly_clip 其余签名参数**：`sector_overlay_active=False`（⚠️ 预留非死代码：§2.5.1 偏离裁剪 overlay 档 ±15% vs ±10% 的开关，D-FACTOR 落地后连同偏离裁剪一起消费）/ `contributions`（None 时归因写空 dict 降级）/ `conflicts`（degraded 条件 1 判定必需）/ `kelly_param_source="density_pdf"`（degraded 条件 5 判定）。**cut_ratio 累积**：多级裁剪按 `1 − (1−r1)×(1−r2)` 公式合并，归因可追溯；`constraint_checks` 中每级裁剪独立记录 `triggered` + `cuts`/`scale`。

**degraded 组装（代码实现）**：`conflicts 任一 truncated`（条件1）∨ `single_name.triggered`（2）∨ `sector.triggered`（3）∨ `total_exposure.triggered`（4）∨ `liquidity_cap.triggered`（4b，v1.0.19 补）∨ `kelly_param_source=="historical_fallback"`（5）。

**A-G 修复记录摘要（v1.0.19 闭环，2026-08-12 核对与代码全部一致）**：A——`constraint_checks` 初始化补 `liquidity_cap` 键（原 Step 1b KeyError）；B——degraded 补 `liquidity_cap.triggered` 析取（G14 可感知流动性降级）；C——Step 1b `adv_data` 改为参数传入 + `sector_adv_median` 从 adv_data 派生（原引用未定义变量）；D——Step 1b `total_capital`→`total_budget` 口径统一；E——Step 1b ADV 两档裁剪算法补全（severe>20% 削到 20% / moderate>10% 削半 / 缺失降级同行业中位数）；F——`PreKellyResult` 增 `contributions` 字段并透传（原数据流断裂致归因丢失）；G——`sector_overlay_active` 注释澄清为 §2.5.1 接口前向兼容预留（非死代码）。

**施工要点**：① 数据流 `StrategyBook → pre_kelly_aggregate → MOD-POS-001 Kelly → post_kelly_clip → FirmTargetPortfolio`，`conflicts`/`contributions`/`kelly_param_source` 三参数须跨段传递（原传空列表致条件 1 永不触发 bug 已修复）；② CASH 豁免贯穿全流程（pre_kelly 求和跳过、post_kelly 裁剪跳过、Step 4 残差计算）；③ 级联单调收敛，Kelly 已 pro-rata 时 Step 3 不触发；④ 幂等：`idempotency_key` 防重复聚合，pre_kelly 结果可缓存，Kelly 重试用同 PreKellyResult（§6 幂等性行）。

### 2.2 按标的求和（自然叠加）—— 讨论要点 ①

**算法**：各 StrategyBook 的 `target_portfolio` 按 symbol 直接相加（S1 给 600519 = 3% + S2 给 600519 = 5% → 求和后 600519 = 8%）。

**为什么用加法不用优化器**（30_multi_strategy_concurrency §2.3）：
- **等价于永远稳定的等权 risk-budget 优化器**：多策略选到同一只票时仓位自然叠加，无需调投票权重，无需估协方差
- **O(N) 替代 O(N²)**：N 个策略 M 个标的，求和是 O(N×M)；MVO 优化器是 O(M²) 甚至 O(M³)（协方差矩阵求逆）
- **归因清晰**：求和后每只票的权重 = 各策略贡献之和，可追溯到 `contributions: dict[str, float]`（`FirmTarget` 字段）
- 行业实践印证（finlab "A 5% + B 3% = 8%" / quant-portfolio per-order attribution / rustybt order netting / APEX ADR-0012 netting+sub-books / youcanbuildthings "netting is arithmetic"）见 §7.4

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
- **A 股不能做空约束**：净额 < 0 时截断为 max(0, net_weight − current_holdings_weight)，即最多清仓不做空

> **净额截断需 current_holdings 输入（2026-08-10 施工流程补充）**：`pre_kelly_aggregate()` 除 `targets` 外**须额外接收 `current_holdings: dict[str, float]`**（symbol → 当前持仓权重，来自持仓对账 MOD-POS-008 / position_limit_enforcer 的 T-1 收盘快照，非 StrategyTarget 产出）。`current_holdings_weight = current_holdings.get(symbol, 0.0)`；净额 < 0 时 `final_weight = max(0, net_weight + current_holdings_weight)`（净卖出不超过现有持仓，剩余意愿记入 `ConflictRecord` 供归因审计）；净额 ≥ 0 时 `final_weight = net_weight`（current_holdings 不参与）。T+1 可卖口径假设见 §6 开放问题行。

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

> **8% vs 5% 口径**：31_position_sizing §2.4.1 已澄清三层口径（MOD-POS-001 默认 5% / MOD-POS-021 聚合 8% / MOD-POS-010 硬限 5%）。FirmRiskAggregator 用 8% 做聚合后裁剪，MOD-POS-010 的 5% 是最终兜底。三层口径待统一（31_position_sizing §5，§6 开放问题行）。
>
> **CASH 豁免裁剪（2026-08-10 施工流程补充）**：CASH 虚拟标的（31号 §2.5 现金管理）**不参与单票/行业/总仓位裁剪**——CASH 无行业归属、无策略 contributions（现金由 firm 层统一管理非策略产出）、Kelly 豁免（31号 §2.3.6 CASH σ≈0）。裁剪循环显式跳过 CASH；CASH 权重在现金管理步骤（§2.5.2 Step 4）作为残差计算：`CASH = total_budget − sum(裁剪后股票权重)`，确保 `holdings` 权重和 + `cash_ratio` = `total_budget`

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

**口径**：按持仓权重按行业归类求和，**不估协方差**（与 30_multi_strategy_concurrency §3.1 一致）。偏离基准 ±10%/±15% 裁剪需行业基准权重数据（申万/中信行业基准），待 D-FACTOR 行业分类模块确认（§6）；MVP 只做绝对上限 30%。

> **相关性聚类（correlation clustering）作为行业约束的补充——待裁定**：行业归类是静态分类，A 股存在跨行业高相关（2026-07 量化私募动量/残差波动率/流动性/短期反转因子同向下跌，跨行业同步踩踏）。[tierzero](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading) 2026-01：pairwise ρ>0.6 归同一 cluster，cluster 设独立 notional limit（比各成员 limit 之和更紧）——"不做完整协方差但做二元相关性判定"的中间方案（O(N²) 但 N 小，不需协方差矩阵求逆）。**tierzero 施工参数**：30 日滚动 PnL 向量窗口；ρ>0.6 聚类阈值（marcelgautsche 2026-06 分级：<0.4 好 / >0.7 冗余 / 0.4-0.7 灰区）；cluster cap = 成员 limit 之和 × shrinkage_factor（例：3×30%×0.55 → 簇 cap 50%）；stale snapshot 检测（position snapshot 非 delta，2 秒 stale 暂停该策略新订单）。**当前 MVP 不做**，重评条件见 §5；与 [31号 §3.7](31_position_sizing.md) HRP 的区别：二元判定+cluster cap 是 tierzero 简化版，比 HRP 轻得多。与 §2.10.5 演进方向 B 的区别：tierzero 是"静态归类+簇 cap"（PnL 层），方向 B 是"动态 ρ 突变检测+shrinkage"（stress-aware），两者可叠加。
>
> **90 天相关性持续高位淘汰规则——备选（[youcanbuildthings 2026-05-06](https://youcanbuildthings.com/articles/multi-strategy-trading-bot-python)）**：两策略 90 日滚动 ρ>0.70 持续 30 连续日 → 分散化收益消失 → 标记 `degraded=True` + 通知 G14 评估淘汰其一（保留 track record 更优者；G13 只检测+标记，停运决策归 G14）。与 tierzero 递进——先簇 cap 降权，持续高位再淘汰。参数：90 日窗口（捕捉中长期结构性收敛）/ ρ>0.70（marcelgautsche "冗余"线）/ 30 连续日（防短期脉冲）。需 6+ 月实盘 PnL，列备选非 MVP；与 §2.10.5 方向 C（信号层 crowding 早期预警）互补。

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

> **级联裁剪"每步基于上一步结果"说明（2026-08-10 施工流程补充）**：三级裁剪是**级联（cascading）**关系，非独立并行——每步的输入是上一步的输出：Step 1 单票裁剪（kelly_adjusted → ≤8%）→ Step 2 行业裁剪（行业内按比例削至 ≤30%/±10%）→ Step 3 总仓位裁剪（等比缩放至 ≤regime_cap）→ Step 4 现金管理（CASH=1−sum）。
>
> **为什么级联而非独立**：独立并行合并会导致归因纠缠（无法区分被行业裁剪 vs 单票裁剪削了多少）；级联设计保证 `cut_ratio` 可追溯，`constraint_checks` 中每级独立记录 `triggered: bool` + `cut_amount: float`。**单调收敛保证**：每步只减不增（`clipped_n ≤ clipped_{n-1}`），最终总暴露 ≤ Kelly 后总暴露 ≤ 求和后总暴露；若任一步裁剪后已 ≤ regime_cap，后续步骤自动跳过（`triggered=False`）。

> **总仓位上限来源**：FirmRiskAggregator 不读 regime 状态，只收到 RegimeMetaAllocator（G15）Shrinkage 后的 budget 数值上限（30_multi_strategy_concurrency §2.2"策略本身不知道市场态，只收到 budget 数字"）。

### 2.6 不做 MVO / 不估协方差 —— 讨论要点 ⑤

**决策**：FirmRiskAggregator 只做求和+裁剪+冲突净额，**不做 MVO，不估协方差矩阵**。

**依据**（30_multi_strategy_concurrency §3.1 已拒绝，本备忘确认执行）：
- 协方差估计在 A 股情绪周期切换时全错（冰点期相关性飙升到 0.8+）
- 优化器放大输入噪声：小幅协方差扰动 → 权重大幅跳动
- 归因纠缠：亏钱时无法区分"策略 alpha 错"还是"优化器权重错"还是"协方差估错"
- AI 能写对优化器代码，但写不出"准确的协方差矩阵"——那是数据+研究问题。**代码印证**：[MOD-POS-021](file:///d:/ZephyrAlpha/src/zephyr/position/core/firm_risk_aggregator.py) 依赖仅 `zephyr.position.core.strategy_book`，无 scipy/numpy 优化器依赖，无协方差计算

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

**与 MOD-POS-001 的衔接**：`PreKellyResult.summed_weights[symbol]` 交 MOD-POS-001 作为 `w_i^sum` 做 Kelly 精裁决（31号 §2.3.4），产出 `kelly_adjusted` 后交回 `post_kelly_clip` 做 §2.4 硬上限裁剪，最终产出 `FirmTargetPortfolio`。`FirmTargetPortfolio` 是 firm 层最终输出（非 Kelly 输入），交下游下单执行层。

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
- **不用协方差**：行业归类只需权重+行业映射 O(M)，不需协方差矩阵 O(M²)。**规模**：3-5 策略 × 每策略 10-20 标的（M≤50），O(N×M) < 250 次操作微秒级完成；O(N²) 优化器在此规模无性能优势但引入协方差估计风险

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

> 当前 §2 决策（自然叠加 + 三级硬裁剪 + 冲突净额）是 MVP 施工目标，O(N×M) 简单确定。本节记录 2026 最新研究中**选项之外**的更好算法，作为远期演进方向——非 MVP，重评条件见 §5。本节只写 why，how 归施工层（[01_design_memo_management_spec §4.3](01_design_memo_management_spec.md)）。

#### 2.10.1 CVaR 作为统一尾部风险度量（替代/增强方差与权重归类）

**当前方案**: §2.5 裁剪用"持仓权重+行业映射"管集中度，不估协方差（§2.6）——但**只管集中度不管尾部形状**（[Man Numeric 2025-07](https://www.man.com/documents/download/81842-e96ab-9099d-e1c10/Numeric_Insights_Covering_Your_Tail%3A_The_Case_for_Expected_Shortfall_in_Tail_Risk_Management_English_%28United_States%29_23-07-2025.pdf)：相同 variance 两组合 CVaR 差 −1.32% vs −1.78%）。

**CVaR 演进方向**（裁剪后组合尾部**验证**，非裁剪主算法）: CVaR 是一致性风险度量（次可加性），Basel III/IV 已用 ES=CVaR 替代 VaR（[alcapitaladvisory 2026-07](https://alcapitaladvisory.com/research/frameworks/cvar.html)）；只看左尾，与 A 股"涨停板是好事"一致（[34号 §3.2.2](34_regime_meta_allocator.md) Sortino 同理）；CVaR/VaR 比率实证 ~1.48x（95%）、集中组合 >2.0x（[pooyagolchian 2026-04](https://pooyagolchian.com/blog/portfolio-risk-var-cvar-kelly-criterion-2026/)）——尾部严重度连续指标，可填入 `constraint_checks` 供 G14。**上下游对齐（只消费不重算）**: [31号 §2.3.4](31_position_sizing.md) Kelly 层已有 `cvar_cap_i`（单标的）；[30号 §2.5](30_multi_strategy_concurrency.md) `var_calculator.py`（MOD-POS-008 production）已有组合 CVaR + 5 级响应；[arXiv:2607.00883](https://arxiv.org/pdf/2607.00883v1) 四轴诊断（条件凸性/尾部可靠性/非压力 carry/回撤持续性）远期可填 `constraint_checks.tail_quality`。**为何远期非 MVP**：需收益分布估计；接入需上下游接口对齐（§6 CVaR 接口行）。

#### 2.10.2 MPC 多期预测思路（远期演进方向）

**当前方案**: §2.2 求和是单期静态；§2.5.2 总仓位上限由 G15 日频单期 Shrinkage 给出。**MPC 演进方向**（[Nystrup/Boyd/Lindström/Madsen, Annals of Operations Research 2019](https://www.researchgate.net/publication/325874988_Multi-period_portfolio_selection_with_drawdown_control), 2026-06 更新）: 核心创新是**按已实现回撤动态调整风险厌恶系数**（"controls drawdowns with little or no sacrifice of mean–variance efficiency"）+ 多变量 HMM 多期预测滚动优化 + 交易/持仓成本作正则化；MPC 不必是 MVO——可借鉴"滚动+回撤感知+成本正则化"用加法+裁剪实现（与 §2.2 哲学一致）。

**可借鉴点**: G15 Shrinkage 远期增"已实现回撤"维度（MaxDD 近阈值收紧 `global_shrinkage`，[30号 §2.5](30_multi_strategy_concurrency.md) 四级阶梯的连续化）；多期化需 [10号](10_regime_detector_spec.md) HMM 扩展转移矩阵预测。属 G15 远期，与 G13 正交。**为何远期非 MVP**：多期 HMM 需 10号扩展；回撤-风险厌恶映射需 6+ 月实盘校准；G15 Shrinkage C1 验证已过（MaxDD +7.36pp，[34号 §3.2.3](34_regime_meta_allocator.md)）。

#### 2.10.3 独立风险层解耦（架构原则借鉴，非多 agent 实现）

**RMATS**（[arXiv:2605.25311, Yang et al. 2026-05](https://arxiv.org/html/2605.25311v1)）: MaxDD 9.62% vs MVO 15.49% vs FinBERT Sentiment 15.28%。4 agents（Sentiment/Report/Analysis/Risk）由递归 Manager 协调（中位 2 轮收敛，ε=0.008）；**Risk Agent 独立于策略层**做 CVaR（EWMA 动态协方差）+ 地缘压力测试 + 多级断路器；奖励 `R_t = r_t − 0.8σ_t − 1.5·max(0, DD_t−θ)`（回撤控制优先）。**对本项目（原则借鉴非实现照搬）**: FirmRiskAggregator 本就是独立风险层（§2.9），与 RMATS Risk Agent 同构；CVaR+断路器已由 `var_calculator.py` + [30号 §2.5](30_multi_strategy_concurrency.md) Drawdown Protocol + §2.1 `degraded` + [G14 三级升级](33_budget_change_handler.md) 等效覆盖；递归多轮收敛不借鉴（本项目 O(N×M) 一次完成）。

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

**结论**: RMATS 的**架构原则**（独立风险层+CVaR+断路器）本项目已用更轻方式实现；**多 agent 实现**对个人项目过重不借鉴。MaxDD 9.62% 主要来自 CVaR+断路器（本项目已有等效）而非多 agent 协调本身——印证 [charter §3 约束五"少而精"](../../04_architecture_principles_decisions/system_charter.md)。

#### 2.10.4 Quarter Kelly 与硬裁剪的协同印证

**pooyagolchian 2026-04 实证**: Quarter Kelly（0.25×）78% 仓位 CAGR 10.8% MaxDD −22%，对比 Full Kelly 312% CAGR 18.2% MaxDD −62%——"Quarter Kelly delivers 85% of full Kelly's growth with only 35% of the drawdown"。**协同印证**（上下游已对齐，非新决策）: [31号 §2.3.1](31_position_sizing.md) 已用**半 Kelly**（[浙商证券 2026-07-27](http://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/838481485080/index.phtml) A 股实证，比 Quarter Kelly 激进一档）；本备忘 §2.4 单票 8% + §2.5.2 总仓位上限是 Kelly 后的**兜底裁剪**（Kelly 算出 15% 也削到 8%），与 Quarter Kelly 78% 总仓位 MaxDD −22% 同量级（regime Shrinkage 后 9%~80%，[34号 §3.2.3](34_regime_meta_allocator.md)）；Kelly（密度域）+ §2 裁剪（权重域）+ var_calculator CVaR（尾部域）三层防御正交。

#### 2.10.5 相关性管理演进（minimax + 突变检测 + crowding 信号层 + PCA/CorrDD 结构层）

> 本节登记五条远期方向（A/B/C/E/F），均非 MVP；重评条件见 §5 待裁定表。**当前方案**：§2.5.1 相关性聚类待裁定（pairwise ρ>0.6 → cluster cap，tierzero 2026-01）——**局部二元判定**。

**演进方向 A——AEGIS Minimax Correlation（全局最坏情况依赖最小化）**: [AEGIS](https://arxiv.org/abs/2604.09060)（arXiv:2604.09060, 2026-04-13）——不找"相关性高的剔除"（局部），而是"构造使最大两两相关性最小的子集"（全局）。2006-2025 walk-forward：CAGR 15.41%, MaxDD 28.89%。理论更优但小规模参数噪声大。**Phase 5+**，重评：策略数 >8 且标的数 >50（与 31号 §3.7 HRP 同步）。

**演进方向 B——相关性突变检测层（stress-aware shrinkage，Phase 3 候选）**: [Bayes Group 2026-03](https://www.bayes-group.com/insights/march-shock-multistrat-resilience)——2026-03 地缘冲击 Millennium/Point72 各亏 ~$1.5B，核心教训"**diversification illusion**"：正常期低相关 pod 在共同宏观冲击下 tail correlation 飙升；恢复最快平台用**实时动态相关性监控**。轻量改进：滚动 short-window（5 日）ρ_short vs long-window（60 日）ρ_long，若 |Δ|>0.3 → 突变 → shrinkage（`factor = 1−α·max(0,|Δ|−threshold)`），只需滚动 pairwise ρ + 一个 shrinkage 因子，比 MARCD/CVaR/多 agent 轻得多。Phase 3 候选（首批策略 3 月实盘后校准）。**方向 B 学术严谨版**——[arXiv:2605.06818](https://arxiv.org/abs/2605.06818)（Coulson/Matteson/Wells, Cornell, 2026-05-07）低秩因子 + 动态收缩先验 + multivariate factor stochastic volatility，首次给出 posterior contraction 显式收敛速率；比 rolling window/EWMA（平滑突变）和 DCC（低维参数化限制）压力期适应性更强，但工程重（MCMC/VI）记远期。

**演进方向 C——BlackRock crowding 警示：相关性聚类延伸到信号特征层**: [BlackRock 2026-04](https://hedgeco.net/news/04/2026/blackrock-issues-crowding-warning-for-hedge-funds.html)——pod shop 共享数据/模型致 **crowding**，压力期 hidden correlation 突变可能 violent unwind；**AI 驱动策略加剧收敛**。**对 100% AI 项目特殊警示**：单一 AI 开发者让多策略天然收敛。Phase 3 候选：raw signal pairwise ρ>0.6 → 标"信号同向"→ 裁剪时**优先削减同 cluster 内信号相似度最高策略**（非等比例）。与 [33号 §3.2.3](33_budget_change_handler.md) AI Agent Flash Crash（2026-03-11，23 agent 47 秒 $500M）呼应。**为何三条列远期非 MVP**: AEGIS 小规模噪声大；突变检测需实盘 PnL 校准；信号层 crowding 需 raw signal 接口标准化（§2.7 只含权重不含 signal，属 G05）。三条均不引入 MVO/协方差/优化器，在 O(N×M) 框架上叠加相关性感知 shrinkage；MVP 用 §2.5.1 pairwise ρ>0.6 已覆盖主要集中度风险。

**演进方向 E——GinkGO PCA 共同因子暴露预警 + CorrDD 回撤尾部同步检测（结构层，Phase 3 候选）**: A/B/C 未覆盖**共同因子暴露**（pairwise ρ 不高但 PCA 第一主成分方差解释比极高）与**回撤尾部同步**（pairwise ρ 被正常期样本稀释）。[GinkGO 框架](https://github.com/kaoruha/ginkgo/issues)（Kaoruha 2026-05）与 [31号 §3.7](31_position_sizing.md) HRP 评估同源：

**① PCA 共同因子暴露预警**：`VE_1 = λ_1/Σλ_i > 50%`（共同因子暴露过高，如 2026-07 量化私募因子共振）/ `H = Σ(λ_i/Σλ_j)² > 0.4`（单因子主导）；即使所有 pairwise ρ<0.6，VE_1>50% 仍说明多策略共享隐藏 beta。PCA 是**全局结构检测**，pairwise ρ 是局部二元检测，互补。**② CorrDD 回撤尾部同步检测**：`CorrDD(i,j) = corr(DD_i,DD_j) > 0.7`（回撤尾部高度同步）/ 同步策略对数占比 >50%（系统性回撤风险）；PnL ρ 被"99% 正常日"稀释，CorrDD 只看回撤序列捕捉尾部同步（与 [30号 §2.5](30_multi_strategy_concurrency.md) Drawdown Protocol 回撤域对齐）；2026-03 地缘冲击正是"正常期低相关 pod 回撤期 tail correlation 飙升"——CorrDD 更早预警 diversification illusion。PCA O(N³) <125 次操作（N≤5），CorrDD O(N²×T) <1500 次（N=5,T=60）。**施工参数（Phase 3）**：60 日滚动 PnL 窗口（与 [34号](34_regime_meta_allocator.md) PerformanceScore 60 日 Sharpe 对齐）；阈值 VE_1>50% / H>0.4 / CorrDD>0.7；触发作第 8/9 项 degraded（第 6=HBI/CSAD、第 7=华泰金工风格拥挤度）+ G14 评估簇内 shrinkage。**为何 Phase 3 非 MVP**：需 6+ 月实盘 PnL；属结构层预警非裁剪算法；PCA 特征值分解非协方差求逆，与 §2.6 不冲突。

**Absorption Ratio 经典基线背书 + 2026 实证 + VRC 理论参照**：VE_1 本质是 **Absorption Ratio**（[Kritzman/Li/Page/Rigobon 2010](https://www.researchgate.net/publication/315429088_Principal_Components_as_a_Measure_of_Systemic_Risk)）的 k=1 特例（前 k=N/5 特征向量解释的方差比例）。[Hammond 2026-05](https://www.researchgate.net/publication/404738503_Geometric_Observables_for_Financial_Regime_Detection) 17 危机窗口（2000-2024）46 方法面板实证：**Absorption Ratio（d=0.80）是最强经典基线**（量子启发 Reduced State Purity d=0.83 第一但 |ρ|≈0.13 与经典通道不相关可互补；Berry Phase Rate d=0.72 OOS 中位最高）——VE_1>50% 阈值有经典文献背书非拍脑袋。量子启发几何观测属 Phase 5+。[Verma 2026-04 VRC Fragility Score](https://pub-637293d6914e45b8a4a3cbe29e1637c1.r2.dev/WMJ-JESD-144-Detecting-Market-Fragility-Through-Correlation-Breakdown-Analysis-Theory-Quantitative-Measurement-and-Hedge-Fund-Implementation.pdf)（7 组件合成）核心论点"**correlation breakdown is not a consequence of crisis, it's the mechanism through which crisis propagates**"为 A/B/C/E/F 多层管理提供理论背书，但 7 组件对个人项目过度工程，仅理论参照。

**演进方向 F——MINGLE 因子图相关性聚类（P4+ 远期）**: [arXiv:2608.06618](https://arxiv.org/abs/2608.06618)（2026-08-06）ADMM 联合学习隐因子 + 策略间图拓扑，是 minimax 的因子图泛化 + PCA 的图结构扩展。**P4+ 非 Phase 3**：ADMM 交替迭代工程重；3-5 策略小规模 A/B/C/E 已够；论文新发布缺实盘验证。重评：策略数 >8 且 A/B/C/E 漏检率高。**方向 E 理论根基——Copula 尾部依赖（P4+ 远期）**: CorrDD 理论基础是 Copula 尾部依赖（[metricgate 2026-06](https://metricgate.com/blogs/copula-dependence-portfolio-risk/) + Sklar 定理）：**相关性度量平均共动，Copula 决定尾部发生什么**——相同相关矩阵不同 Copula 族有截然不同联合崩盘概率。Gaussian Copula `λ_L=0`（系统性低估崩盘概率，2008 CDO 教训）vs t-Copula `λ_L>0`（ν 越小尾部越厚，贴近 A 股尾部同步）。CorrDD 是 Copula 思想的**非参数无分布工程轻量替代**（免边际分布/族选择/参数拟合），与方向 B 互补（B 管 PnL 突变，CorrDD 管回撤尾部）。显式 Copula 拟合列 P4+（与 [10号 §3 G02](10_regime_detector_spec.md) Student-t HMM 同期），重评：CorrDD 漏检或策略数 >8。与 [31号 §2.3.1 Taleb 胖尾论点](31_position_sizing.md) 同源。

#### 2.10.6 单策略集中度上限 + 市场拥挤度检测 + 风格拥挤度（2026-08-10 九次审查补充）

> 三个当前缺失维度：① 单策略集中度上限（FLOX 2026-05）② 市场拥挤度检测（HBI/CSAD）③ 风格拥挤度（华泰金工动量+成交量双维度分域）。均 Phase 3 候选非 MVP。

**演进方向 D-1——单策略集中度上限（FLOX max_concentration_pct）**: [FLOX PR#183](https://github.com/FLOX-Foundation/flox/pull/183)（2026-05-07）——**单策略占总 gross 暴露的比例上限**（默认 0.35）。本项目有单票 8%/行业 30%/总仓位三层硬限，但缺"单策略占总仓位上限"维度（若打板策略 5 个信号都命中 8% 上限，该策略占 40%，组合风险集中于单一 alpha 来源）。与 §2.10.5 方向 C（策略间信号同质化）正交。候选值 30-40%（3 策略时每策略≤33% 天然等权，5 策略时≤40%）。**Phase 3**：首批策略 3 月实盘后若独占>35% 频发，引入为第四级裁剪（单票→行业→总仓位→单策略集中度）。

**演进方向 D-2——HBI/CSAD 市场拥挤度检测（O(N) 纯价格，A 股可落地）**: [laoyulaoyu 羊群行为六法](https://laoyulaoyu.com/index.php/2026/07/01/羊群行为（从众心理）的量化检测：六种方法识别市场过度拥挤信号/)（2026-07-01），完全符合"不估协方差"原则：

| 指标 | 公式 | 信号 | 复杂度 |
|---|---|---|---|
| **HBI（羊群行为指数）** | `HBI = |个股均收益 − 基准均收益| / |基准均收益|` | HBI<0.3 极端一致性（群体陷阱，unwind 风险高）→ 降仓；HBI>2.0 统计异常（独立机会）→ 加仓 | O(N) |
| **CSAD（横截面绝对偏差）** | `CSAD = mean(|个股收益 − 市场均收益|)` | 低 CSAD=羊群（风险区）；高 CSAD=独立决策（机会区） | O(N) |

方向 C 是策略信号层 crowding（需 raw signal 接口，归 G05），HBI/CSAD 是市场层拥挤度（纯价格，A 股直接可算）——可作 firm 层 degraded **第 6 项触发**（HBI<0.3 → G14 评估降仓），与方向 B（策略间 ρ 突变）互补。**为何 Phase 3 非 MVP**：需校准 A 股基准（中证全指/沪深 300）+ 历史 HBI 分位数阈值（60/120 日）。

**演进方向 D-3——华泰金工风格拥挤度（A 股本土校准，动量+成交量双维度）**: [华泰证券金工 2026-08](https://m.hibor.com.cn/wap_detail.aspx?id=5dc71a9949bce52f3398c30caaf270dd)——HBI/CSAD 管"市场是否一致"，未覆盖**风格拥挤**（某风格因子过度拥挤后的反转风险）：按动量（Top 20%/中/Bottom 20%）×成交量分域，各域拥挤度 = 域内个股数占比的时序百分位；小盘拥挤度（低动量+低成交域）>90% 分位 → 小盘 unwind 风险；大盘拥挤度（高动量+高成交域）<10% 分位 → 大盘资金撤离；连续 20 日确认防脉冲。与 D-2 递进——HBI 先检测"市场是否拥挤"，华泰再定位"哪个风格拥挤"，指导 G14 **定向降仓**（降拥挤风格策略而非等比例全降）；与方向 C（策略间信号同质）正交。**施工参数（Phase 3）**：动量/成交量 20 日滚动（与 [20 §2.3](20_first_batch_strategies.md) IC 衰减窗口同量级）；60/120 日双分位窗口；触发作 degraded **第 7 项**。**为何 Phase 3 非 MVP**：需 A 股全市场数据（D-FACTOR 因子工厂已 production，需新增分域计算模块）+ 6+ 月历史校准分位阈值；O(N) 分域统计，不引入协方差/优化器。

#### 2.10.7 Fassino 风险预算 Cauchy 不动点 —— Phase 4 远期候选

> **v1.0.15 新增**：Cauchy 不动点构造法直接构造风险预算组合，避免辅助优化问题并证明存在唯一性——§3.4 拒绝理由②（求解复杂度）的远期突破路径。

**算法**（[Fassino 2026-03, arXiv:2603.17415](https://arxiv.org/abs/2603.17415)）：传统风险预算需求解 `min_w 1/2 w^T Σ w − Σ_i b_i log(w_i)`（凸优化），Fassino 用**不动点迭代**：映射 `T(w) = diag(Σw)^{-1/2}×b / ||diag(Σw)^{-1/2}×b||`，从任意 w_0（如等权）迭代 `w_{k+1} = T(w_k)` 收敛；Σ 正定下 T 是压缩映射，Banach 不动点定理直接给出存在唯一性（免 KKT 分析）。

| 维度 | §3.4 拒绝的风险预算优化 | Fassino Cauchy 不动点 |
|---|---|---|
| 求解方式 | 辅助优化问题（凸优化求解器） | 不动点迭代（矩阵乘法 + 归一化） |
| 存在性证明 | KKT 条件 + 凸性 | Banach 不动点定理（压缩映射） |
| 协方差需求 | 完整 Σ 矩阵 | 完整 Σ 矩阵（同） |
| 计算复杂度 | O(N³) 优化 + 迭代 | O(N²) per iteration × K 次迭代 |
| 实现复杂度 | 需凸优化库（cvxpy/scipy.optimize） | 纯矩阵运算（numpy 足够） |

**与既有裁定的关系**：直接解决 §3.4 理由②（辅助优化复杂）但①（需估协方差）仍成立；仍需完整 Σ，与 §2.6 核心原则冲突——价值在于"未来若做风险预算"（§2.10.5 演进到需估 pairwise ρ 时）提供更轻求解路径。与 [31号 §3.9](31_position_sizing.md) Tepelyan 多元 Kelly sigmoid 标度律同属"被拒绝算法的计算复杂度突破"——Tepelyan 突破 Kelly 组合爆炸（仅需 pairwise ρ，更轻），Fassino 突破风险预算优化复杂度（需完整 Σ，更重），代表协方差估计深度两个层级。**为何 Phase 4 非 MVP**：① 仍需完整 Σ（与 §2.6 冲突），前提是 §2.10.5 已建立 pairwise ρ 估计且策略数 8+ 使协方差边际价值超过噪声风险；② 等权 risk-budget 在 3-5 策略与完整风险预算差异微弱（§2.6）；③ A 股 regime 转折 Σ 不稳定（garbage in garbage out）。**重评条件**：① §2.10.5 相关性估计稳定运行 ≥6 月 ② 策略数 8+ ③ 实盘 ≥1 年 Σ 窗口稳定性验证 ④ 最小集成：Top-5 策略 Fassino vs 等权对比回测验证边际收益后扩展。

#### 2.10.8 Kakinaga & Umeno MFCCA 多重分形组合配置 —— Phase 4 远期候选

> **v1.0.17 新增**：用 MFCCA 有符号波动函数替代方差/协方差风险泛函，从根本上消除 Σ 估计需求——§3.4 拒绝理由①的远期突破路径。此为 [36号 §4.13](36_var_es_monitoring.md) MFCCA 方法论文（arXiv:2608.03968）的**组合应用论文**（同第一作者，arXiv:2608.04987）。**算法**（[Kakinaga & Umeno 2026-08-05](https://arxiv.org/abs/2608.04987)）：用 MFCCA **有符号波动函数** `F_xy(q, s)`（s 时间尺度，q 波动阶数）替代 `w^T Σ w`：① **符号保留**——同向/反向运动组件以相反符号贡献风险（标准 MF-DXA 用 |F_xy| 丢失方向），符合"对冲降低组合风险"直觉；② **多尺度**——短尺度捕获微结构噪声，长尺度捕获基本面共同因子；③ **q=2 退化为均值-方差**——MFCCA 是 MV 的严格推广；④ **多分形谱**——广义 Hurst 指数 h_xy(q) 随 q 变化，单一 ρ 无法捕获此异质性。实证：每个 required return 水平上 MFCCA 配置的 VaR/ES/MaxDD 均低于 MV（in/out-of-sample），关键贡献是符号保留。

| 维度 | §3.4 拒绝的风险预算 | Fassino Cauchy 不动点（§2.10.7） | Kakinaga MFCCA 配置（§2.10.8） |
|---|---|---|---|
| 协方差需求 | 完整 Σ | 完整 Σ | **无 Σ 需求**（用 F_xy 替代） |
| 风险泛函 | `w^T Σ w` | `w^T Σ w` | `Σ_ij w_i w_j F_ij(q, s)` |
| 求解方式 | 凸优化 | 不动点迭代 | 凸优化（但泛函更鲁棒） |
| 突破点 | - | 求解复杂度② | 协方差需求① + 风险泛函非平稳 |

Kakinaga 直接解决①（无 Σ）并间接缓解③（F_xy 多尺度对 regime 转折更鲁棒），②仍成立（仍是凸优化）——Kakinaga+Fassino 组合可同时解决①②。与 [36号 §4.13](36_var_es_monitoring.md) 正交：36号用 MFCCA 诊断 Σ regime 转变（输入），32号用 MFCCA 替代 Σ 进入配置（输出）；完整路径：36号检测 Σ 转变频繁 → 32号 MFCCA 替代 → 配合 Fassino 求解。**为何 Phase 4 非 MVP**：① F_xy 参数空间比 Σ 更大（s×q 二维网格），3-5 策略下估计噪声可能超鲁棒性收益；② [31号 §2.2.2](31_position_sizing.md) inverse-vol（1 参数/标的）已实证"最鲁棒轻量配置"；③ s/q 选择需 track record 校准。**重评条件**：① §2.10.5 上线后 ρ 实测不稳定 ② 策略数 8+ ③ 36号 §4.13 证实 Σ regime 转变显著 ④ 最小集成：Top-5 策略 q=2（退化为 MV）MFCCA vs inverse-vol 对比回测后扩展到 q≠2。

#### 2.10.9 Hsieh & Gan Certified Wasserstein DRO LP —— Phase 5+ 远期候选

> **v1.0.17 新增**：§2.6 拒绝 MVO 部分因"优化器放大输入噪声"——Wasserstein DRO 理论上对冲此风险但传统计算不可扩展。[Hsieh & Gan 2026-08-07, arXiv:2608.07032](https://arxiv.org/abs/2608.07032)（National Tsing Hua University）多项式规模 LP 逼近使其可计算且扩展到 1000 资产。**算法**：① 支撑超平面 majorize 凹效用 `U(w^T r) ≈ inf_k {a_k(w^T r)+b_k}` 转化为 LP 约束；② 对偶化 Wasserstein 球内最坏情况期望子问题（1-范数 ground metric）；③ **统一逼近误差证书**（certified——输出解同时输出误差上界，可验证解质量）；④ LP 规模 O(N×K)（N 资产 × K 超平面），476 资产月度再平衡验证，可扩展到 1000 资产（传统 DRO 限于 <50）。

| 维度 | §2.6 拒绝的 MVO | 传统 Wasserstein DRO | Hsieh Certified LP（§2.10.9） |
|---|---|---|---|
| 协方差需求 | 完整 Σ | 完整 Σ（或场景集） | **场景集**（经验分布 P_n） |
| 噪声对冲 | 无（点估计） | Wasserstein 球对冲 | Wasserstein 球对冲 |
| 计算复杂度 | O(N³) | 半无穷规划（不可扩展） | 多项式 LP O(N × K) |
| 误差证书 | 无 | 无 | **有**（统一逼近上界） |

Hsieh 不解决"协方差估计需求"（仍需场景集），但解决"优化器放大噪声"（Wasserstein 球显式建模分布不确定性）。**三级路径关系**：Fassino（保 w^TΣw+不动点求解）→ Kakinaga（F_xy 替代泛函+凸优化）→ Hsieh（Wasserstein 球 DRO+LP 求解）；可叠加但复杂度过高，Phase 5+ 评估时择一或择二。**为何 Phase 5+ 非 MVP/Phase 4**：① 三层抽象（DRO+LP 逼近+误差证书）对 3-5 策略属过度工程；② 场景集构建成本高（3-5 策略×60 日=300 场景，LP 规模优势不显现）；③ 球半径 ε 校准难（过大过度保守近等权，过小退化为点估计，A 股 regime 转折校准困难）；④ A 股实证缺乏。**重评条件**：① Fassino+Kakinaga 已证实协方差感知配置边际收益 ② 策略数 10+ 且资产数 50+（LP 优势显现）③ ε 校准方法成熟（cross-validation/bootstrap）④ 最小集成：Top-10 策略 Hsieh DRO vs Kakinaga MFCCA 对比回测。

### 2.11 作战地图组合优化口径裁定（BM-SEL-21 / BM-RC-07-B / BM-RC-07-C 闭合）

> **v1.0.22 新增**：作战地图全覆盖补丁——作战地图三个环节的定义口径与本备忘 §2.6/§3.4 已裁定路线存在冲突或链路缺口，本节给出明确二选一裁定与链路补全。

#### 2.11.1 BM-SEL-21 组合优化（design 父环节）——口径冲突裁定：维持"自然叠加+Kelly+硬裁剪"

**定位**：BM-SEL-21 组合优化（L3，design，MOD-PF-002）——BM 环节定义假设统一优化引擎：`max Σ(w×score) s.t. 仓位/容量/行业/风格/相关性(corr<0.7)/拥挤`，输入投票输出 ~30 只 → 输出 N 只下单清单+权重（60 秒级，30→N≤10 只）。

**裁定**：**维持本备忘路线（默认项）**——自然叠加（O(N) 加法）+ firm 层半 Kelly 精裁决 + 三级硬裁剪，**不建 maxΣ(w×score) 统一优化引擎**。BM 环节定义修订建议登记（见下）。理由：① 30号 §3.1 已裁定不做 MVO/不估协方差，BM-SEL-21 的"corr<0.7 约束 + 拥挤度约束 + maxΣ(w×score)"本质是受约束均值-方差变体，与该裁定直接冲突；② [31号 §3.6](31_position_sizing.md) 实证（Conformal Kelly §6.4）：硬上限约束下 per-asset Kelly 优于 multivariate 解（"under a binding gross cap only the direction survives"），BM 假设的优化器增益在 3-5 策略小规模下被协方差估计噪声吞没；③ 行业/相关性/拥挤约束已由"硬裁剪（§2.5）+ §2.10.5 相关性管理演进 + §2.10.6 拥挤度检测"以**裁剪与监控**形态覆盖，无需优化器形态。**重评条件**：① 策略数 >8 且标的数 >50；② §2.10.5 相关性估计成熟运行 ≥6 月；③ 实盘 ≥1 年——届时按 §2.10.7 Fassino（Phase 4）→ §2.10.8 MFCCA（Phase 4）→ §2.10.9 Hsieh DRO（Phase 5+）三级路径评估优化器引入，而非直接上 maxΣ(w×score)。

**BM 环节定义修订建议登记**：建议将 BM-SEL-21 的 process 描述从"maxΣ(w×score) s.t. 仓位/容量/行业/风格/相关性/拥挤"修订为"自然叠加 + Kelly 精裁决 + 硬裁剪（31/32 号已定稿路线）"；子环节 BM-SEL-21-B（组合优化器，MOD-PF-002，production）的"均值方差优化→风险预算→约束求解"描述同步对齐为"Kelly 约束（只减不增）+ 硬裁剪求解"；corr<0.7 / 拥挤度约束映射到 §2.10.5 / §2.10.6 监控层。本登记不擅自改 BM 真源，留作战地图维护批次处理。

#### 2.11.2 BM-RC-07-B 风险预算优化求解（production）——同上冲突裁定：Kelly 上限+风险预算消费，优化求解登记 Phase 4

**定位**：BM-RC-07-B 风险预算优化求解（L4 风控域，production，MOD-RK-08 `core/risk_budget_allocator.py`）——BM 环节定义假设"风险预算优化求解器分配 + 风险贡献计算器"，VaR 产出后分配各资产风险预算 → BM-RC-07-C 再平衡。

**裁定**：与 §2.11.1 同一冲突的风控域投影——**当前生效路线 = Kelly 上限 + 风险预算消费**（[25_multifactor_strategy_detail §2.1](25_multifactor_strategy_detail.md) 风险预算框架：预算由 34 号 RegimeMetaAllocator 分配、策略消费预算、Kelly 只减不增做上限精裁），**不建独立风险预算优化求解器**；BM 定义的"优化求解"登记 **Phase 4 演进**（§2.10.7 Fassino 远期候选——Cauchy 不动点已解决 §3.4 拒绝理由②求解复杂度，但理由①协方差需求未解决，拒绝裁定维持）。理由：① 风险预算的"分配"在 34 号已落地（budget 数字驱动），"优化求解"是对分配结果的二次精调，3-5 策略小规模下边际收益不显著；② BM-RC-07-B degradation"求解器未收敛→等比例预算（保守）"恰好说明当前自然叠加基线就是其降级形态——当前实现等价于"永远处于降级态的求解器"，稳定性反而更高。**重评条件**：同 §2.11.1 三条件 + 34 号 budget 分配实盘显示等权/线性分配不足（风险贡献严重失衡）时启动 Fassino 评估。

#### 2.11.3 BM-RC-07-C 风险贡献与再平衡（production）——"预算 vs 实际→再平衡触发"链路补全

**定位**：BM-RC-07-C 风险贡献与再平衡（L4，production，MOD-RK-08）——风险预算 vs 实际暴露 → 风险贡献计算 + 再平衡触发 + 约束处理 → BM-POS 仓位调整。

**裁定**：链路两段**分层承载**——① **监控层（风险贡献计算）**：引用 [54_reconciliation_attribution](54_reconciliation_attribution.md) §3.14 MCR/CCR 风险分解（Euler 齐次函数定理：MCR_i=(Σw)_i/σ_p，CCR_i=w_i×MCR_i，求和不变量 ΣCCR=σ_p，Phase 2.5 候选）作为"预算 vs 实际"偏离的度量层——Brinson 管"谁赚了钱"，MCR/CCR 管"谁贡献了风险"，预算（目标风险贡献）与实际 CCR 的偏离即 BM-RC-07-C"预算偏离阈值"的判定输入；② **执行层（再平衡触发）**：偏离超阈值后的再平衡触发**联动走 [31号 §2.8.2](31_position_sizing.md)**（BM-POS-07 漂移/日历双驱动执行链 + 成本-收益门槛），本备忘（G13）只产出 FirmTargetPortfolio，不重复建再平衡触发器。理由：风险贡献监控是归因域职责（54 号），再平衡执行是仓位域职责（31 号），G13 聚合器保持单一职责；MCR/CCR 需经验协方差矩阵与 §2.6"不估协方差"的张力已由 54 号定位为 Phase 2.5 候选消解——**监控层**用协方差做事后归因 ≠ **决策层**用协方差做下单优化，归因不进入交易链路。**重评条件**：54 号 MCR/CCR 上线后，若"预算 vs 实际"偏离频发但 31号 §2.8.2 成本-收益门槛全部拦截（纠偏不经济），评估偏离阈值与再平衡门槛的联合校准。

**契约/参数**：BM-RC-07-C 触发条件 = |实际 CCR_i − 预算 CCR_i| / 预算 CCR_i > 偏离阈值（具体数值待 54 号 Phase 2.5 施工时校准，BM 定义"再平衡触发阈值"未定值）；输入 = 风险预算（BM-RC-07-B / 34 号 budget）+ 实际暴露（BM-RC-04 盘中监控）；输出 = 再平衡信号 → 31号 §2.8.2 执行链；降级 = 再平衡器异常 → 人工再平衡（BM-RC-07-C degradation 原值）。

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
| **MVP** ✅ 已完成（2026-08-12 核对） | 求和+冲突净额+单票/行业/总仓位裁剪 | **已施工 production（2026-08-10，MOD-POS-021 v1.0.0，651 行，0 处 NotImplementedError；60 测试全绿 8e4d60d5）** |
| **阶段 2** ✅ 已完成（2026-08-12 核对） | `aggregate()` 拆分为 `pre_kelly_aggregate()` + `post_kelly_clip()`，与 MOD-POS-001 Kelly 衔接 | **拆分已实现**（§2.1；MOD-POS-001 `position_sizing_engine.py` 881 行 production 在位） |
| **阶段 3** ⏳ 代码就绪/文档待重建 | `constraint_checks` 与 G14 BudgetChangeHandler 三级升级联动 | ⚠️ 33_budget_change_handler 在 2026-08-11 git 灾难中内容丢失回退骨架 v0.1.0（原 v2.x 定稿内容 git 历史无记录，待重建）；**代码侧已就绪**——budget_change_handler.py（MOD-POS-022）production v1.0.0，接口契约暂以代码 docstring 为真源 |

### 4.3 为何这是上限而非妥协
- Citadel/Millennium 的 pod 模型本质就是 A（独立账本 + firm 风险聚合），**firm 层只做求和+裁剪，不做 MVO**（30_multi_strategy_concurrency §4.3）
- 3-5 策略的 MVO 收益 < 3-5 策略独立加总收益，因为协方差估计误差 > MVO 理论增益
- 真正的上限 = 在 A 框架内把自然叠加 + 三级硬裁剪做到极致，而不是在 firm 层堆优化器
- O(N) 聚合是 A 模型最被低估的优点——用加法替代优化器（30_multi_strategy_concurrency §2.3）

### 4.4 过度工程审查（2026-08-10）

| 组件 | 是否过重 | 裁定 |
|---|---|---|
| **行业硬约束（±10%/绝对 30%）** | ⚠️ 需评估 | **不过重**。2026 实证（[tierzero](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading) 2026-01："common mistake is to set limits only at layer 1 and assume aggregation takes care of itself"；[algovestiq](https://www.algovestiq.com/learn/answers/how-to-size-stock-positions) 2026-05：行业基准"20-25% per sector"）。A 股板块轮动风险高，行业约束是必需风控。执行只需权重+行业映射 O(M)，不需协方差 |
| **总仓位硬约束（12 态+2 overlay）** | ✅ 合适 | regime Shrinkage 节流后的数值上限，FirmRiskAggregator 只消费数字不估 regime（30 §2.2）。O(M) 等比缩放 |
| **冲突净额处理** | ✅ 合适 | O(M) 加法，A 股不能做空时净额<0 截断为清仓。比优先级仲裁 O(N²) 简单且无 meta 参数 |
| **按比例裁剪（非优先级截断）** | ✅ 合适 | O(1) per symbol，确定性算法无 meta 参数。归因公平 |
| **求和（自然叠加）** | ✅ 合适 | O(N×M) 加法，A 模型核心优点。替代 O(M³) MVO 优化器 |
| **RMATS 式多 agent 协调（4 agent + 递归 Manager + LLM）** | ❌ 过重 | §2.10.3 已审：个人项目 3-5 策略是独立 sleeve 非独立 agent；RMATS MaxDD 9.62% 主要来自 CVaR+断路器（本项目已有等效：`var_calculator.py` + 30号 Drawdown Protocol），非多 agent 本身。**不借鉴实现，只借鉴"独立风险层"架构原则** |
| **CVaR 裁剪后验证层** | ⚠️ 远期非过重 | §2.10.1 已审：CVaR 是一致性度量，`var_calculator.py` 已 production；接入 `constraint_checks` 需上下游接口对齐（§6），MVP 用权重+行业映射已覆盖集中度风险 |

**结论**：FirmRiskAggregator 整体不过重。所有操作都是 O(N×M) 以内的加法/比较/缩放，无优化器、无协方差、无 meta 参数。行业硬约束是 A 股板块轮动风险的必需风控，非过度工程。真正的过重是 MVO/协方差/投票仲裁（§3 已拒绝）+ RMATS 式多 agent 协调（§2.10.3 拒绝）。CVaR 验证层是合理远期演进，需上下游对齐后引入。

## 5. 待裁定（暂缓项）

> 以下项目暂不施工，**非永久禁止**。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **冲突标的优先级仲裁** | MVP 用净额处理（O(M)）；优先级仲裁（按策略 Sharpe/PnL 排序）是 O(N²) 且需 meta 参数 | 策略数显著增加（>8）且净额处理不足；有 6+ 月实盘 track record 可量化优先级 |
| **协方差感知行业约束** | MVP 行业约束按权重归类求和（O(M)）；协方差感知（因子模型+shrinkage）可更精准但需估协方差 | 协方差估计方案成熟（因子模型+shrinkage 验证有效），与 30_multi_strategy_concurrency §3.1 重评协方差同步 |
| **动态单票上限（按流动性/市值自适应）** | MVP 固定 8%（总资金口径）；动态上限（小市值/低流动性更严）增加复杂度 | 31_position_sizing §5 单票口径统一后评估 |
| **相关性聚类（correlation clustering）作为行业约束补充** | MVP 行业约束按申万/中信静态归类（O(M)）；相关性聚类（pairwise ρ>0.6 → 同 cluster → cluster cap，tierzero 2026-01）是"不做完整协方差但做二元相关性判定"的中间方案，可覆盖跨行业高相关风险（如 2026-07 量化私募因子共振跨行业踩踏）。需各策略 6+ 月 PnL 数据算 pairwise ρ | ① 各策略 6+ 月实盘 PnL 数据可算 pairwise ρ ② 行业约束实测不足以控制跨行业相关性风险 ③ 与 31号 §3.7 HRP 远期候选重评同步 |
| **CVaR 裁剪后验证层**（§2.10.1） | MVP §2.5 裁剪只管集中度不管尾部形状；CVaR 是一致性度量可验证裁剪后组合尾部风险。`var_calculator.py`（MOD-POS-008）已 production，31号 §2.3.4 Kelly 层已有 `cvar_cap_i`——但 firm 层接入 `constraint_checks` 需上下游接口对齐 | ① `var_calculator.py` 输出接口与 `constraint_checks` 对齐（§6）② 31号 Kelly 层 `cvar_cap_i` 与 firm 层 CVaR 验证的职责边界明确（单标的 vs 组合级，不重复）③ 实盘 6+ 月验证增量信息 |
| **MPC 多期预测 / 回撤感知 budget**（§2.10.2） | MVP §2.2 求和单期静态，§2.5.2 上限由 G15 日频单期 Shrinkage 给出；MPC（Nystrup/Boyd 2019）"已实现回撤动态调整风险厌恶 + 多期 HMM 预测"可连续调整 budget。但需 10号扩展多期转移矩阵 + 6+ 月实盘校准回撤-风险厌恶映射 | ① 10号 regime detector 支持 H 期转移矩阵预测 ② G15 Shrinkage 实盘显示单期节流不足（MaxDD 超阈值频发）③ 与 30号 §2.5 Drawdown Protocol"连续 vs 阶梯"重评同步 |
| **单策略集中度上限 + HBI/CSAD 拥挤度检测 + 华泰金工风格拥挤度 + PCA/CorrDD 结构层**（§2.10.6 + §2.10.5 E） | MVP 有单票 8%/行业 30%/总仓位 80% 三层硬限，缺"单策略占总仓位上限"维度（FLOX max_concentration_pct=0.35，D-1）；HBI/CSAD 是 O(N) 纯价格市场羊群度检测（HBI<0.3 降仓 / HBI>2.0 加仓，degraded 第 6 项，D-2）；华泰金工风格拥挤度动量+成交量双维度分域（小盘>90%/大盘<10% 分位+20 日持续，degraded 第 7 项+定向降仓，D-3）；PCA VE_1>50% 共同因子暴露 + CorrDD>0.7 回撤尾部同步（degraded 第 8/9 项，§2.10.5 E）。四者均 O(N)/O(M)/O(N³) 轻量不引入协方差求逆/MVO | ① 首批策略 3 月实盘后确认"单策略独占>35% 仓位"频发 ② HBI/CSAD + 华泰金工校准 A 股基准+历史分位数阈值 ③ PCA/CorrDD 需 6+ 月 PnL 数据 ④ 与 §2.10.5 A/B/C 相关性聚类重评同步（策略数 >8 且标的数 >50 时全面评估） |

## 6. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| ~~`aggregate()` 拆分为 `pre_kelly_aggregate()` + `post_kelly_clip()`~~ | 本备忘 §2.1 代码现状与设计意图 | ✅ **已完成**（2026-08-10 施工 + v1.0.20 文档确认，2026-08-12 核对源码在位）：两段接口已实现并由 `aggregate()` 便捷入口串联 Kelly passthrough，MOD-POS-001 `position_sizing_engine.py`（881 行 production）在位。本行关闭 |
| 单票 8% vs 5% 三层口径统一（MOD-POS-001/010/021） | 31_position_sizing §2.4.1 / §5 | 待 G04 首批策略产出后统一 |
| `constraint_checks` 与 G14 三级升级的接口契约 | 本备忘 §2.7 / 33_budget_change_handler | ⚠️ 33 号在 2026-08-11 git 灾难中内容丢失回退骨架 v0.1.0（原"v2.9.0 已定稿"内容 git 历史无记录，待重建）。**当前接口契约临时真源** = `budget_change_handler.py`（MOD-POS-022，production v1.0.0，572 行）头部 docstring（INVARIANTS/TierLevel/TierState/收敛检测三条件）+ 本备忘 §2.7 `constraint_checks` 字段定义；33 号重建后本行版本引用回填 |
| 行业映射数据源（申万一级/中信一级） | 本备忘 §2.5.1 | 待 D-FACTOR 行业分类模块确认 |
| **dead-band filter（再平衡死区）归属评估** | 本备忘 §2.2（finlab/quant-portfolio 实践） | **评估结论：不属 G13 范围**。dead-band filter（weight change <阈值不执行再平衡，避免交易成本超信号收益）是执行层机制，属 G14 BudgetChangeHandler（防抖阈值，⚠️ 33 号骨架化内容丢失，防抖机制现以 `budget_change_handler.py` docstring"日内<5% 忽略/日间累计>10% 强制触发"为真源）或 buy/sell_flow（最小交易阈值）。G13 只管求和+裁剪产出 FirmTargetPortfolio，不管"是否执行再平衡交易"。finlab 用 <2% 阈值，quant-portfolio 用"交易成本超信号收益"判定——具体阈值待 G14 校准。[arXiv:2605.01176v3](https://arxiv.org/html/2605.01176v3)（2026-06）SPO portfolio 的 partial adjustment（δ<1，只闭当前→目标差距的 δ 比例）是 dead-band 的连续版，同属执行层非 G13 |
| **lot 对齐 / 最小交易单位裁剪后归属** | [33号 §3.2.3](33_budget_change_handler.md)（lot 对齐导致收敛偏差） | **评估结论：不属 G13 裁剪算法**。G13 §2.4-§2.5 裁剪产出**权重域** FirmTargetPortfolio（浮点权重）；lot 对齐（A 股 100 股最小交易单位，向下取整）是**执行层** buy/sell_flow（[41号](41_buy_flow.md)/[42号](42_sell_flow.md)的职责）。⚠️ 33 号骨架化后原注记丢失，原意保留于此："lot 对齐导致实际暴露略高于 new_budget，偏差 <1 个 lot 通常 <0.1%，远小于防抖阈值 5%，若累积超限 firm 层 32号兜底裁剪"——即 G13 裁剪用浮点权重，lot 偏差由执行层吸收，G13 仅在累积超限时重新裁剪 |
| **Kelly pro-rata 归一化与 firm 层总仓位裁剪的交互**（防重复缩放） | [31号 §2.3.5](31_position_sizing.md)（Kelly 层 pro-rata）+ 本备忘 §2.5.2（总仓位裁剪等比缩放） | **需对齐**：31号 §2.3.5 在 Kelly 层做 pro-rata 归一化（sum(f_i^final) > 总仓位上限时按比例缩放），本备忘 §2.5.2 总仓位裁剪也做等比缩放。两者可能叠加导致**双重缩放**。施工时须明确：① Kelly 层 pro-rata 用 Kelly 后的 sum vs Kelly 层总仓位上限（可能 = regime_cap）② firm 层 §2.5.2 用裁剪后 sum vs regime_cap ③ 两者口径一致则 Kelly 层 pro-rata 后 firm 层总仓位裁剪自动不触发（`triggered=False`），不会双重缩放。数据流：`pre_kelly_aggregate → MOD-POS-001 Kelly（含 §2.3.5 pro-rata）→ post_kelly_clip（§2.5.2 总仓位裁剪，若 Kelly 已 pro-rata 则跳过）` |
| **CVaR 接口对齐（var_calculator → constraint_checks）** | 本备忘 §2.10.1 / [30号 §2.5](30_multi_strategy_concurrency.md)（var_calculator.py MOD-POS-008） | **待对齐**：`var_calculator.py` 已 production 实现组合 VaR/CVaR，但输出格式未接入本备忘 `constraint_checks`。施工时须定义：① `constraint_checks.tail_risk` 字段结构（VaR_95/CVaR_95/CVaR_VaR_ratio/tail_quality 四轴）② 调用时机（post_kelly_clip 后调用 var_calculator 验证，非裁剪主算法）③ 与 30号 §2.5 drawdown_controller 5 级响应的关系（drawdown_controller 消费同源 CVaR 做分级响应，G13 只记录不重复计算） |
| **pre_kelly_aggregate / post_kelly_clip 幂等性与重入** | 本备忘 §2.1（两段接口） | **待定义**：`idempotency_key` 已在 FirmTargetPortfolio 字段（§2.7），但两段拆分后幂等语义需明确——① pre_kelly 与 post_kelly 是否共享同一 idempotency_key ② 若 MOD-POS-001 Kelly 失败重试，post_kelly_clip 是否需重新调用 pre_kelly_aggregate（答案：否，pre_kelly 结果可缓存，Kelly 重试用同 PreKellyResult）③ 幂等窗口（如日内同 idempotency_key 返回缓存结果） |
| **~~⚠️ P0：StrategyBook→FirmRiskAggregator 接口字段名三方漂移~~** | 2026-08-12 代码核对（[30号 §2.2](30_multi_strategy_concurrency.md) 接口契约②已同步标注） | ✅ **已关闭（AI-FRA-001，8e4d60d5 已 merge，60 测试全绿）**。原漂移诊断备查：代码真源 `TargetPortfolio` dataclass（strategy_book.py）字段为 `positions: dict[str, TargetWeight]` + `budget`；而原 `_sum_by_symbol()` duck-typing 按 `target_portfolio`/`budget_used` 取值——直接传入 TargetPortfolio 对象会静默取空默认值，聚合产出全现金组合且不报错；且 `positions` 值是 `TargetWeight` 对象（含 target_weight/reason/confidence）非裸 float。修复含"传 TargetPortfolio 对象"路径回归测试 |
| **T+1 可卖持仓口径假设** | 本备忘 §2.3 净额截断（`max(0, net+current_holdings)`） | **口径假设未明示**：`current_holdings` 假设全部可卖，但 A 股 T+1 下今日买入部分不可卖——若快照含今日买入部分需区分"可卖/冻结"。净额截断若按全量 holdings 计算，极端场景会允许"卖出超过可卖量"的意愿进入下游（执行层 [42号](42_sell_flow.md) sell_flow 兜底）。归执行层职责，但本备忘须明示口径假设：`current_holdings` 应为 **T+1 口径可卖权重**（昨持仓−今日已卖），数据供给方（持仓对账/`position_reconciler`）需按此口径供数 |
| **~~测试文件丢失重建~~**（2026-08-11 git clean 灾难，#ARCH-GIT-CLEAN-GUARD-FIX） | 代码头部 [TESTS] 声明 `tests/position/test_firm_risk_aggregator.py` | ✅ **已重建（AI-FRA-001，8e4d60d5 已 merge）：60 测试全绿**。原灾难备查：测试文件 2026-08-10 创建未 `git add`，2026-08-11 被 `git clean -fd` 删除且 git 历史无记录。同批仍丢失待重建：`test_strategy_book.py`（70）/ `test_budget_change_handler.py`（47）/ `test_regime_meta_allocator.py`（55），登记 [30号 §6.8](30_multi_strategy_concurrency.md) |
| **capability_canonical_file_registry 未登记** | 硬约束"模块创建必须生成 creation_token 并登记" | ⚠️ MOD-POS-021（及同批 MOD-POS-020/022、MOD-PA-007）未在 `capability_canonical_file_registry.yaml` 登记（该 registry 仅 MOD-POS-009 一条 D_POSITION 记录）。需补登记（creation_token 追溯生成或按补救流程）——不属本备忘施工范围，登记供治理调度 |
| **depgraph maturity 滞后** | [64_d_position.md](../../02_domain_architecture_docs/64_d_position.md)（自动生成） | ⚠️ depgraph（PostgreSQL）中 MOD-POS-020/021/022 仍标 design，64 号自动文档佐证滞后（"设计态/design"）。需 depgraph DB 更新 maturity=production 后重新生成——不属本备忘施工范围，登记供治理调度 |

## 7. 引用

### 7.1 相关 design_memo
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)——§2.2 FirmRiskAggregator 定义（框架来源）/ §2.3 自然叠加 O(N) 替代 O(N²) / §3.1 拒绝 MVO / §3.2 拒绝 Model D
- [31_position_sizing.md](31_position_sizing.md)——§2.1 分层裁定流程（求和→Kelly→裁剪）/ §2.4 硬上限参数（G12 定 G13 执行）/ §2.5 现金管理 CASH / §2.6 FirmTargetPortfolio 契约 / §8.1 给 G13 的交接项
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G13 / §5 轨道 B / §7.3 编号占用表
- [01_design_memo_management_spec.md](01_design_memo_management_spec.md) §4.3 推荐章节 / §5.2 引用纪律

### 7.2 depgraph 模块（用 blueprint_id / path 引用）

| 模块 | blueprint_id | path | 本备忘角色 | 当前状态（2026-08-12 核对源码） |
|---|---|---|---|---|
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | 本备忘主体（§2 全部） | ✅ production v1.0.0（651 行，0 处 NotImplementedError）✅ 60 测试全绿（AI-FRA-001，8e4d60d5） |
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | 上游：产出 StrategyTarget（§2.2 求和输入） | ✅ production v1.0.0（680 行）⚠️ 测试丢失（70） |
| position_sizing_engine | MOD-POS-001 | `src/zephyr/position/core/position_sizing_engine.py` | 下游：Kelly 精裁决（§2.1 步骤③）+ 最终硬限 | ✅ production（881 行）✅ 测试在位 |
| position_limit_enforcer | MOD-POS-010 | `src/zephyr/position/core/position_limit_enforcer.py` | 最终硬限兜底（5% NAV，§2.4 注） | ✅ production ✅ 测试在位 |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | 消费 constraint_checks 做三级升级（G14） | ✅ production v1.0.0（572 行）⚠️ 测试丢失（47）+ 33 号设计文档骨架化（§6 登记） |

> MOD-PA-007（RegimeMetaAllocator，Shrinkage 节流）属 G15，本备忘只消费其输出的 budget 数字。✅ 已 production v1.0.0（594 行，0 处 NotImplementedError，34 号 v2.7.0 确认）⚠️ 测试丢失（55）。⚠️ **depgraph DB 滞后**：上述 5 个模块在 depgraph（PostgreSQL）中仍登记 design（[64_d_position.md](../../02_domain_architecture_docs/64_d_position.md) 自动生成文档将 MOD-POS-020/021/022 标"设计态"佐证），需 depgraph 更新后重新生成——登记 §6。

### 7.3 相关 battle_map
- BM-POS-04 跨策略仓位硬限制（MOD-POS-010）——单票 8% / 行业 ±10% / 总仓位 9 态框架（参数来源）
- BM-POS-06 现金管理约束（MOD-POS-006）——CASH 标的约束

### 7.4 开源实证参考
- **聚合架构同构**：[Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book)（sleeve(alpha)+risk-parity-throttle(firm) 分层，firm 层只 risk-parity 求和+throttle 不做 MVO）；[riskcore](https://github.com/massimotodaro/riskcore)（2026-01，**"Don't replace PM systems. Aggregate them."** READ-ONLY overlay + Cross-PM Netting + Firm-level VaR，与本备忘"策略层粗仓位+firm 层求和裁剪"/§2.3 冲突净额/§2.7 constraint_checks 同构，机构级 $1B-$50B 实现，本项目是个人级简化版）；[nexusfi Multi-Strategy Futures](https://nexusfi.com/a/automation/multi-strategy-portfolio-automated-futures)（2026-06，Risk Engine 集中式组合级聚合，Net Exposure 跨策略净额同构 §2.3，ENB=1/Σwᵢ² 真实分散化度量，IVaR 单策略组合 VaR 贡献可借鉴为 §2.10.1 归因维度，三级 kill switch）
- **组合级硬限必要性**：[tierzero multi-venue risk limits](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading)（2026-01，三层限仓栈 strategy→venue→portfolio，"portfolio limit is the hard ceiling"）；[algovestiq position sizing](https://www.algovestiq.com/learn/answers/how-to-size-stock-positions)（2026-05，"hard cap 8-10% per position, 20-25% per sector"）；[nautilus_trader #4419](https://github.com/nautechsystems/nautilus_trader/issues/4419)（2026-07，多策略组合级 gross exposure cap 真实需求）；[Passify Global Risk Overlay](https://www.einpresswire.com/article/896092429/passify-releases-new-quantitative-report-on-multi-algorithm-correlation-and-risk-aggregation)（2026-02，**"1% risk per trade on ten different bots → 10% open exposure on a single correlated move"**，overlay 超阈值 halt new entries——印证 §2.4/§2.5 硬约束 + degraded 标记）；[QBase_v2.5 Portfolio 构建指南](https://github.com/S1mon-code/QBase_v2/blob/main/docs/PORTFOLIO.md)（2026-04，相关性<0.40、边际 Sharpe 贡献>0（SR_candidate > ρ×SR_portfolio）、交易次数影响权重上限、MaxDD 恶化≤3%，最多 8 策略）；[A股量化私募7月集体回撤·涵德风控升级](https://m.toutiao.com/group/7670831772460794420/)（2026-08，2026-07 幻方单月-22%，动量/残差波动率/流动性/短期反转因子同向下跌踩踏，涵德单票 1%→0.3%、持股 600→900、软约束→硬约束——印证 §2.4/§2.5 硬限实盘价值 + §5 相关性聚类必要性）；[breakingalpha Portfolio-Level Risk Constraints](https://breakingalpha.io/insights/portfolio-level-risk-constraints)（2025-11，risk budget framework + dynamic risk budgets + constraint hierarchy，印证 §2.5 执行顺序从局部到全局 + §2.7 constraint_checks 供 G14）
- **自然叠加/净额/归因**：[finlab multi-strategy portfolio](https://finlab.finance/docs/en/workflows/multi_strategy_portfolio/)（2026，"Strategy A 5% + B 3% = 8%"，dead-band filter <2%）；[quant-portfolio multi-sleeve](https://github.com/isaacnicas/quant-portfolio)（2026-06，dead-band + position caps + per-order attribution）；[marcelgautsche Multi-Strategie-Portfolios](https://marcelgautsche.de/insights/multi-strategie-portfolios)（2026-06，Risk-Budget pro Strategie 防同步建大仓，相关性 <0.4 好/>0.7 冗余/0.4-0.7 灰区，4 不相关策略×15% MaxDD→组合 8-10%，与 G15 allocation_i×global_shrinkage 同构）；[quanthedgeai Multi-Strategy E2E](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)（2026-07，intake/incubation/allocation/rebalancing/removal 全流程）
- **相关性/crowding/集中度检测**：[tierzero correlation clustering](https://tierzero.dev/blog/portfolio-risk-limits-multi-venue-algo-trading)（2026-01，ρ>0.6 同簇+簇 cap，§2.5.1/§5）；[go-trader #1270](https://github.com/richkuo/go-trader/issues/1270)（2026-07，相关性标的≠分散化，direction+asset bucketing 作协方差替代）；[AEGIS minimax](https://arxiv.org/abs/2604.09060)（arXiv:2604.09060，2026-04，CAGR 15.41%/MaxDD 28.89%，§2.10.5 A）；[Bayes Group March Shock](https://www.bayes-group.com/insights/march-shock-multistrat-resilience)（2026-03，diversification illusion + 实时动态相关性监控，§2.10.5 B）；[BlackRock crowding warning](https://hedgeco.net/news/04/2026/blackrock-issues-crowding-warning-for-hedge-funds.html)（2026-04，共享数据/模型致 crowding，AI 加剧收敛，§2.10.5 C）；[Coulson/Matteson/Wells Bayesian 动态收缩先验](https://arxiv.org/abs/2605.06818)（arXiv:2605.06818，2026-05，posterior contraction 收敛速率，§2.10.5 B 严谨版）；[Pomegra AI Trading Crowding](https://pomegra.io/news/ai-trading-crowding-erases-quant-edge-2026)（2026-06，Goldman AI 动量 positioning 100th 百分位当日高 beta 动量篮子跌 8%）；[GinkGO PCA+CorrDD](https://github.com/kaoruha/ginkgo/issues)（2026-05，VE_1>50%/H>0.4/CorrDD>0.7，§2.10.5 E）；[MINGLE 因子图](https://arxiv.org/abs/2608.06618)（arXiv:2608.06618，2026-08，ADMM 隐因子+图拓扑联合，§2.10.5 F）；[FLOX PR#183](https://github.com/FLOX-Foundation/flox/pull/183)（2026-05，max_concentration_pct=0.35 单策略占比上限，§2.10.6 D-1）；[laoyulaoyu 羊群行为六法](https://laoyulaoyu.com/index.php/2026/07/01/羊群行为（从众心理）的量化检测：六种方法识别市场过度拥挤信号/)（2026-07，HBI<0.3/>2.0、CSAD，§2.10.6 D-2）；[华泰金工风格拥挤度](https://m.hibor.com.cn/wap_detail.aspx?id=5dc71a9949bce52f3398c30caaf270dd)（2026-08，动量×成交量分域，小盘>90%/大盘<10%+20 日持续，§2.10.6 D-3）；[Man Group pod-shop 非唯一](https://hedgenordic.com/2026/06/man-group-the-pod-shop-model-isnt-the-only-way/)（2026-06，单一风险框架组合 systematic+discretionary，"correlations can be monitored as they evolve"，印证 §2.9 + 动态相关性远期）
- **CVaR/尾部风险**：[Man Numeric Covering Your Tail](https://www.man.com/documents/download/81842-e96ab-9099d-e1c10/Numeric_Insights_Covering_Your_Tail%3A_The_Case_for_Expected_Shortfall_in_Tail_Risk_Management_English_%28United_States%29_23-07-2025.pdf)（2025-07，相同 variance CVaR −1.32% vs −1.78%）；[A.L. Capital CVaR](https://alcapitaladvisory.com/research/frameworks/cvar.html)（2026-03，Basel III/IV 用 ES 替代 VaR，集中 3 股 CVaR 16-18% vs 分散 20 股 6-9%）；[Noguer i Alonso CVaR Crashes](https://arxiv.org/pdf/2607.00883v1)（arXiv:2607.00883，2026-07，四轴诊断可填入 constraint_checks.tail_quality）；[pooyagolchian VaR/CVaR/Kelly](https://pooyagolchian.com/blog/portfolio-risk-var-cvar-kelly-criterion-2026/)（2026-04，CVaR/VaR ~1.48x，Quarter Kelly 78%/CAGR 10.8%/MaxDD −22%，§2.10.4）；[ericxuzhesheng/Relaxed-Risk-Parity-Research](https://github.com/ericxuzhesheng/Relaxed-Risk-Parity-Research)（2026-08，风险预算松弛+CVaR 约束+换手惩罚，30号 §4.2 远期路径核心组件）
- **远期演进/执行层**：[Nystrup/Boyd MPC drawdown control](https://www.researchgate.net/publication/325874988_Multi-period_portfolio_selection_with_drawdown_control)（2019/2026-06 更新，回撤感知风险厌恶，§2.10.2）；[RMATS](https://arxiv.org/html/2605.25311v1)（arXiv:2605.25311，2026-05，MaxDD 9.62%，§2.10.3 独立风险层原则）；[MDPI Economies regime-conditional CVaR](https://www.mdpi.com/2227-7099/14/7/268)（2026-07，换手 226%/年侵蚀净表现，瓶颈是决策规则非 regime 检测，印证离散分档+防抖必要性）；[Wang & Hasuike SPO](https://arxiv.org/html/2605.01176v3)（arXiv:2605.01176v3，2026-06，partial adjustment δ<1 是 dead-band 连续版，clipping 稳定机制印证 §2.4-§2.5）；[go-trader PR#1291](https://github.com/richkuo/go-trader/pull/1291)（2026-07，日亏上限只阻开仓不强制平仓，与 T+1 语义兼容，同构 G14 Tier1 封锁新仓）；[algovantis Multi-Strategy Sizing](https://algovantis.com/optimizing-position-sizing-for-multi-strategy-risk-management-and-stability/)（2026-03，Drawdown-Based Re-sizing + EWMA 动态相关性，印证 degraded + G14 三级升级）；[xfinlink commodity risk parity](https://xfinlink.com/blog/commodity-risk-parity-python)（2026-06，inverse-vol return 15.7% vs 等权 8.7%、MaxDD -6.7% vs -19.8%，印证 §2.5 防高波动行业主导 + 31号 §2.2.2）

### 7.5 system_charter 约束映射
- §3 约束四（策略三维度解耦）→ FirmRiskAggregator 只管 how much 聚合，不管 what 选股
- §3 约束五（少而精）→ 3-5 策略 O(N×M) 聚合足够，不需 MVO
- §3 约束一（交易成本）→ 聚合后裁剪不引入额外交易成本（只读 budget 做缩放）

### 7.6 已施工设施盘点（2026-08-12 全量核对，通用规则 #11）

> 盘点范围：与本备忘（G13 FirmRiskAggregator）数据流直接相关的全部已施工设施。更广域的四域盘点见 [30号 §7.5](30_multi_strategy_concurrency.md)。**先清楚有什么 → 才知道怎么改 → 才知道该删除/退役什么**。

#### A. G13 数据流核心链（StrategyBook → FirmRiskAggregator → MOD-POS-001 → 下单）

| 模块 | path | 行数 | MATURITY | 测试 | 与本备忘关系 |
|---|---|---|---|---|---|
| MOD-POS-020 StrategyBook | `position/core/strategy_book.py` | 680 | production v1.0.0 | ⚠️ 丢失（70） | §2.2 求和输入（`TargetPortfolio` 产出者——字段名漂移已修复，§6 P0 行） |
| **MOD-POS-021 FirmRiskAggregator** | `position/core/firm_risk_aggregator.py` | 651 | production v1.0.0 | ✅ 60 全绿（8e4d60d5） | **本备忘主体**：两段拆分已实现（`pre_kelly_aggregate`/`post_kelly_clip`/`aggregate` 便捷入口 + 内部裁剪方法），0 处 NotImplementedError |
| MOD-POS-001 position_sizing_engine | `position/core/position_sizing_engine.py` | 881 | production | ✅ 在位 | §2.1 步骤③ Kelly 精裁决（消费 `PreKellyResult.summed_weights`） |
| MOD-POS-010 position_limit_enforcer | `position/core/position_limit_enforcer.py` | — | production | ✅ 在位 | §2.4 三层口径最终兜底（5% NAV） |
| MOD-POS-022 BudgetChangeHandler | `position/core/budget_change_handler.py` | 572 | production v1.0.0 | ⚠️ 丢失（47） | §2.7 `constraint_checks`/`degraded` 消费者（G14）；33 号文档骨架化 |

#### B. 参数/上限供给方（本备忘只消费不定阈值）

- MOD-PA-007 RegimeMetaAllocator（`pf_alloc/core/regime_meta_allocator.py`，594 行，production v1.0.0，⚠️ 测试丢失 55）——`total_budget` + `regime_cap` 来源（§2.2/§2.5.2）
- 31 号仓位算法（G12）——单票 8%/行业 30%/流动性 ADV 20%-10% 阈值真源（§2.4/§2.4.4/§2.5.1）
- MOD-POS-008 drawdown_controller（603 行 production，✅ 测试在位）+ var_calculator（`risk/core/`，394 行 production Phase 1，✅ 在位）——§2.10.1 CVaR 验证层候选数据源

#### C. 代码-文档契约核对结论（2026-08-12）

- §2.1.1 伪代码 A-G 修复与实际代码**全部一致**：`constraint_checks` 初始化含 `liquidity_cap` 键 / degraded 条件组装段 / `_clip_liquidity()` 的 `adv_data` 参数化 + `sector_adv_median` 派生 / `total_budget` 口径 / `PreKellyResult.contributions` 字段透传 / `post_kelly_clip` 签名的 `sector_overlay_active` 预留参数 ✅
- §2.7 契约字段与 `FirmTargetPortfolio` dataclass 定义**一致**：firm_positions/total_exposure/total_budget/cash_ratio/constraint_checks/conflicts_resolved/degraded/created_at/idempotency_key/schema_version 全在位 ✅；代码头部 [INVARIANTS] 与 §2 决策**一致**（自然叠加/按比例削/不做 MVO/O(N)/冲突净额）✅
- ✅ 原"唯一不一致"（`_sum_by_symbol()` 按 `target_portfolio`/`budget_used` duck-typing 与 `TargetPortfolio.positions`/`budget` 字段名不匹配）**已修复**（AI-FRA-001，8e4d60d5，§6 P0 行）

#### D. 缺口登记（详见 §6 表尾）

- MOD-POS-021 60 测试已重建全绿（8e4d60d5）；同批仍丢失待重建：strategy_book（70）/ budget_change_handler（47）/ regime_meta_allocator（55）（2026-08-11 git clean 灾难）
- capability_canonical_file_registry 未登记 MOD-POS-021（硬约束违例）
- depgraph DB maturity 滞后（64 号自动文档标"设计态"）

## 8. 交接清单（供兄弟主题组 AI 索引）

> 本节抽取 G13 FirmRiskAggregator 中供兄弟主题组（G12/G14/G15）直接消费的交接点。交接纪律（00_index_trading_decision §7.2）：AI 间不直接通信，通过产出物 + depgraph path 交接。

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
| 2026-08-12 | 1.0.22 | 作战地图全覆盖补丁——BM-SEL-21 / BM-RC-07-B / BM-RC-07-C | §2.11 新增作战地图组合优化口径裁定小节（3 环节闭合）：① §2.11.1 BM-SEL-21（design 父环节）二选一裁定——BM 假设 maxΣ(w×score) s.t. corr<0.7/拥挤统一优化引擎 vs 本文 §3.4 已裁定路线冲突，裁定维持"自然叠加+Kelly 精裁决+硬裁剪"（默认项），BM 环节定义修订建议登记（process 描述对齐 31/32 号路线+SEL-21-B 描述对齐+约束映射监控层，留 BM 维护批次不擅自改真源）；② §2.11.2 BM-RC-07-B（production）同上冲突裁定——当前=Kelly 上限+风险预算消费（25号 §2.1 框架，预算 34号分配/Kelly 只减不增精裁），优化求解登记 Phase 4 演进（§2.10.7 Fassino Cauchy 不动点远期，拒绝理由①协方差需求未解决裁定维持）；③ §2.11.3 BM-RC-07-C（production）"预算 vs 实际→再平衡触发"链路补全——监控层引用 54号 §3.14 MCR/CCR 风险贡献分解（Euler 分解 Phase 2.5 候选）为偏离度量层，执行层联动 31号 §2.8.2 再平衡执行链，G13 保持单一职责不建再平衡触发器 |
| 2026-08-14 | 1.0.23 | 压缩精简：已施工内容折叠，零信息丢失审查通过（AI-DOCS-001） | §2.1.1 完整伪代码折叠为接口级摘要（production 代码为真源，8e4d60d5，60 测试）；§2.1"代码现状对齐"过程段折叠为 ✅ 已施工标记；§2.10 远期演进方向散文压缩（算法核心/参数/对比表格/链接/Phase 与重评条件全保留）；§7.4 对标实证按主题归组（全部链接保留）；§6 P0 字段名漂移行 + 测试丢失行随 AI-FRA-001 关闭（8e4d60d5 已 merge）；§7.2/§7.6 状态同步。接口契约/degraded 5 条件/liquidity_cap-adv_data-total_budget 口径/§6 全部开放问题/A-G 修复摘要零丢失自审通过 |
