---
ttl: permanent
doc_type: architecture_view
title: BudgetChangeHandler 三级升级
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-12
topic: budget_change_handler
scope: 07_trading_decision_architecture
---

# BudgetChangeHandler 三级升级

> **性质**：决策备忘（G14）。本文回填已施工代码的设计 why——`src/zephyr/position/core/budget_change_handler.py`（MOD-POS-022，572 行，MATURITY=production）。
> **历史说明**：00_index 曾标本文"active v2.10.0 已定稿"，30 号/37 号亦引用"v2.10.0 / §3.2.3 / §3.4"，但磁盘上仅存 v0.1.0 骨架——完整版曾丢失（与 16 号两篇同属未提交丢失事故）。本版按已施工代码 + 30/31/32 号设计依据重建，版本号重置为 1.0.0。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G14 BudgetChangeHandler 三级升级 |
| 所属 | 作战地图 08 + [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.4 |
| 依赖 | G12（[31_position_sizing](31_position_sizing.md)）、G13（[32_firm_risk_aggregator](32_firm_risk_aggregator.md)） |
| 对标 | 机构级 budget rebalance 协议 |
| 正交性 | ⚠️ budget 来源依赖 RegimeMetaAllocator（G15），但三级升级逻辑本身正交 |
| 优先级 | P2 |
| 状态 | ✅ active v1.0.0（代码 production；测试与事件链缺口见 §6/§7） |

## 2. 背景

**项目处境**：30 号 §2.4 已定多策略并发的核心原则——"budget 是硬约束，策略的自主权在'怎么适应 budget'，不在'要不要适应'"。RegimeMetaAllocator（G15）按 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` 产出 budget 分配，budget 变动时必须有一个执行者把"数字变化"变成"仓位收敛"。

**核心问题**：budget 下调时，如何既尊重策略自主（让策略自选砍哪些仓），又保证 firm 层硬约束必达（策略不能死扛）？上调简单（抬高上限自然部署，现金拖累可接受），下调才是难点。

**约束条件**：
- T+1——当日买入不可卖，收敛必须给 1-2 个交易日自然调仓空间，不能要求瞬时达标；
- 个人单账户——无交易员人工干预，机制必须全自动、行为可预测；
- 单机进程——状态缓存在进程内即可起步，跨日持久化列入 Phase 2。

## 3. 决策

### 3.1 架构定义：指令型状态机，只产指令不执行

BudgetChangeHandler 是**纯指令型状态机**：输入 budget 变动，输出三个 frozen 指令 dataclass——`FreezeNewPositions`（CTR-POS-022-F）/ `RebalanceRequest`（CTR-POS-022-R）/ `ForcedTrim`（CTR-POS-022-T），本身不触碰任何下单/持仓接口。

why（为什么这么设计）：
1. **可纯单元测试**——无 IO、无券商依赖，状态机全路径可在内存中回放；
2. **与 D-EX-CORE 解耦**——指令的消费方是 StrategyBook（MOD-POS-020 收 rebalance 指令）与 FirmRiskAggregator（MOD-POS-021 收 ForcedTrim），执行细节演进不回流影响本模块；
3. **指令即审计**——每条指令自带 `timestamp` + `schema_version="1.0"`，且 `TierState.instructions_issued` 逐条留痕（tier/reason/at），满足"每级独立 log 可复盘"。

### 3.2 三级升级（30 号 §2.4 的代码落地）

| 级别 | 触发 | 行为 | 代码落点 |
|---|---|---|---|
| Tier1 封锁新仓 | budget 下调瞬间（与 Tier2 同调用内连发） | 发 `FreezeNewPositions(cancel_pending_buy_orders=True, keep_pending_sell_orders=True)` | `_trigger_three_tier_escalation()` L399-450 |
| Tier2 策略自主收敛 | Tier1 后立即 | 发 `RebalanceRequest(new_budget, convergence_window)`，策略在窗口期内自选砍仓 | 同上 L424-444 |
| Tier3 按比例强裁 | 窗口超时（或 firm 风险违例，见 §7-③） | 发 `ForcedTrim(trim_ratio=(exposure−target)/exposure)`，等比缩放不挑仓位 | `_escalate_to_tier3()` L492-542 |

why 三级而非直接强砍（30 号 L209-212 裁定）：①尊重策略自主权——策略最知道哪笔仓位该砍；②避免在随机时刻强卖的成本——高换手策略 1-2 天内自然收敛，Tier3 实际不触发；③低换手策略由 Tier3 兜底防死扛。Tier1 撤买单留卖单的不对称设计：第一时间止血防惯性开仓，减仓方向（卖单）不受限。

### 3.3 防抖双层（代码 L64-68，30 号 §2.4 之外的补充决策）

- `DEBOUNCE_THRESHOLD = 0.05`——日内抖动 <5% 忽略，防止 Shrinkage 高频微调引发反复封锁/解封；
- `CUMULATIVE_TREND_THRESHOLD = 0.10`——日间累计连降 >10% 强制触发，防抖不能过度到对趋势性缩水视而不见；
- **上调对称性豁免**——budget 上调即时 re-target 不防抖（上调是机会不是风险，`handle_budget_change()` L251-261）；收敛中再变动同样豁免防抖直接 re-target（`_retarget_in_convergence()` L452-490）。

### 3.4 convergence_window 按换手率差异化

默认 `DEFAULT_CONVERGENCE_WINDOWS = {打板: 2d, 多因子: 4d, 事件驱动: 3d}`，缺省 3 天（L74-79）。依据 30 号 §6.4 经验区间（打板 1-2 天 / 多因子 3-5 天 / 事件 2-3 天）取中值。why 差异化：换手率决定自然收敛速度——打板隔日即换仓，2 天足够；多因子周频调仓，给 4 天；事件驱动居中。窗口参数为 C 类可调，首批策略实盘后校准。

### 3.5 收敛判定三条件（`check_convergence()` L296-377）

1. `ε_pos = 5%`——仓位差 <5% 视为收敛。why 5%：A 股 T+1 下给 1-2 日自然调仓空间，太小会误触发 Tier3，太大形同虚设（30 号 L216-227 裁定）；
2. `ε_days = 1`——连续维持 1 个交易日，防单日假收敛；
3. 窗口内无新 firm 违例——代码显式声明由调用者保证（L307），本模块不重复检查。
边界全部 fail-safe：`exposure ≤ 0` 直接 CONVERGED；窗口结束时 `exposure ≤ target` 认定已收敛不强裁。

### 3.6 rebalance_to_budget 接口契约——"策略不能说我不卖"

契约直接写进 `RebalanceRequest.interface_contract` 载荷字符串（L118：必须返回 target_portfolio 总暴露 ≤ new_budget）。策略侧已施工：`src/zephyr/position/core/strategy_book.py` `rebalance_to_budget()` L304-390——上调不强制买入仅抬上限（现金拖累可接受，30 号 §2.4）；下调按 confidence 降序保留最自信仓位、边界仓位部分保留、其余全砍，保证 total_weight ≤ new_budget。

### 3.7 已施工设施盘点

| 设施 | 位置 | 状态 |
|---|---|---|
| 三级状态机 + 五态 TierLevel（IDLE/T1/T2/T3/CONVERGED） | budget_change_handler.py L82-89 | ✅ production |
| 防抖双层 + 上调豁免 | L217-294 | ✅ production |
| 差异化窗口 + 收敛三条件 | L296-450 | ✅ production |
| 策略侧 rebalance_to_budget | strategy_book.py L304-390 | ✅ production |
| firm 侧 degraded 标记（五触发条件，供 G14 判升级） | firm_risk_aggregator.py L344-362 | ✅ production（消费入口未接线，见 §7-③） |
| 预算分配上游 RegimeMetaAllocator | pf_alloc/core/regime_meta_allocator.py | ✅ production（事件链未接线，见 §7 新发现 3） |
| 模块登记 | blueprint_registry.yaml MOD-POS-022 Active / module_translation_registry L41262 | ✅ 已登记 |

## 4. 考虑过的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 直接按比例强裁（无 Tier1/2） | 随机时刻强卖成本高；抹杀策略自主权——策略最知道砍哪笔（30 号 §2.4 裁定） |
| 纯策略自主、无 firm 层兜底 | 低换手策略可能死扛，budget 硬约束失守；Tier3 是必达性保证 |
| 事件溯源 + DB 持久化 TierState | 暂缓——单机进程内缓存够用；blueprint §9 列 Phase 2，重评条件=多进程/服务化部署 |
| 窗口统一固定值（不按换手率差异化） | 拒绝——打板 2 天与多因子 4 天的自然收敛速度差一倍，统一值不是误触发就是形同虚设 |

## 5. 上限定义

**系统上限**：三级升级 + 防抖双层 + 差异化窗口，对个人双账户、3-5 策略并发已是上限。不再加更细的级别（如 Tier1.5 部分封锁）——级别越多复盘归因越模糊。
**演进路径**（Phase 2 候选，30 号 §2.4 L229-237）：no-trade 半带闭式解 `b*=[3cσ²/(2λ)]^(1/3)`（或 b=TE·√3≈5.2%），把固定 ε_pos=5% 升级为按策略 σ 差异化——首批跑出实测 σ 后再裁定。2026 年多策略组合运维研究（quanthedgeai 2026-07）佐证 no-trade band 方向：±25% 权重带 + 再平衡频率上限是机构落地常用形态。
**为何是上限**：个人系统无多账户/多 PM 的资本调度复杂度（已裁剪 OE-002），三级已覆盖"止血→自主→兜底"全语义。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| TierState 跨日持久化（DB） | 单机单进程够用；持久化引入 schema 维护成本 | 多进程部署或跨日收敛窗口成为常态 |
| E-POS-40/41 事件发射（BudgetChangeHandled/TierEscalation） | 当前无事件消费方，instructions_issued 内存留痕够复盘 | 复盘编排器（G26）上线需要消费时 |
| Phase 2 no-trade 半带闭式解 | 需实测策略 σ，首批未上线 | 首批 3 个月 track record 后 |
| 收敛后显式解冻指令（frozen=False） | Tier1 瞬时语义隐式过期当前够用 | 若 StrategyBook 实现持久 frozen 标志时必须补 |

## 7. 待定问题（G14 六要点逐项裁定）

> 原讨论要点逐条对齐现状；✅=代码已施工，⚠️=有缺口需人决策。

- [x] ① **Tier1 封锁新仓（瞬时）**——✅ 已施工（§3.2）。遗留：StrategyBook 侧 frozen 标志/新开仓拦截未实现，FreezeNewPositions 当前依赖执行层自觉——**待决策**：是否在 StrategyBook 补 frozen 拦截，还是保持指令即日志的轻量语义。
- [x] ② **Tier2 rebalance_to_budget 信号**——✅ 已施工（§3.6 契约 + 策略侧实现）。
- [x] ③ **Tier3 按比例强裁**——✅ 超时路径已施工。⚠️ **缺口**：30 号 §2.4 与 blueprint §3.4(b) 均定义"firm 风险违例不等窗口直接 Tier3"，32 号 degraded 标记已产出，但 handler 无消费入口——**待决策**：补 `on_firm_violation()` 入口，还是维持单一超时路径（简化但 firm 违例响应慢一个窗口期）。
- [x] ④ **convergence_window 差异化**——✅ 已施工（打板 2/多因子 4/事件 3）。⚠️ **待校准**：窗口值为经验区间中值，首批上线后按实测换手率校准（30 号 §6.4 标"需人决策"）。
- [x] ⑤ **rebalance_to_budget 接口契约**——✅ 已施工（§3.6）。
- [x] ⑥ **每级独立 log/复盘**——🟧 部分：instructions_issued 内存留痕 + action 中文字符串已具备，但无 logger/事件总线发射——**待决策**：接入统一日志的时机（随 G26 复盘编排一并做？）。

**代码层新发现问题（登记待处理，不属原六要点）**：
1. **测试为零与"47 测试全绿"表述漂移**——30 号 L88/L214 称"47 单测全绿"，模块头 [TESTS] 声明 `tests/position/test_budget_change_handler.py`，但磁盘上该文件不存在、全 tests/ 零命中。需补测试（blueprint §7 规划 Phase 1 ~28 条）并修正 30 号表述（越界改动，登记在此）。
2. **错误码撞号**——模块头声明 BudgetChangeError=ZA-POS-0022，与 strategy_book.py L13 RebalanceRefusedError 同号；blueprint §6 另用 ZA-POS-0040~0044 段。需统一错误码段。
3. **BudgetChanged 事件链未接线**——RegimeMetaAllocator 只产 BudgetAllocation，全仓库无 `handle_budget_change` 调用方：当前是无生产调用方的纯库模块，接线随 G15→G14 集成时完成。
4. **`_retarget_in_convergence` 下调重置窗口硬编码查"多因子"**（L482-484），忽略策略自身类型——代码瑕疵，待修。
5. **fail-closed 声明与实现不符**——头部 INVARIANTS 称"TierState 读取失败假设 Tier1 封锁"，实际 state 缺失时 check_convergence 返回 NO_ACTION（fail-open）。需对齐其一。
6. **文档漂移**——30 号 L214 称 481 行（实际 572）且提及不存在的方法名 `_check_tier2_convergence_or_escalate`；blueprint §11.1 仍标"❌ 未实现"。越界修正登记在此。
7. **00_index 同步（越界登记）**：00_index §0/§7.3 对本批 7 篇重建文档的版本登记全部滞后（15 号 v1.21.2 / 33 号 v2.10.0 / 52 号 v1.7.4 / 55 号 v1.21.0 / 16 号两篇 / 27 号 v0.4.0），需统一同步为本轮重建版本。

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G14
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.4（三级升级原则）/ §6.4（窗口经验区间）
- [31_position_sizing](31_position_sizing.md) §8.2（G12→G14 交接表：上限触发条件归 G12，降级流程归本文）
- [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（degraded 标记五条件）
- 代码：`src/zephyr/position/core/` 下 budget_change_handler.py / strategy_book.py / firm_risk_aggregator.py
- battle_map_08_position_management（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G14 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active：回填 §2-§6 全部决策 why（指令型状态机/三级升级/防抖双层/差异化窗口/收敛三条件/接口契约）；§7 六要点逐项对齐代码现状并登记 7 项代码层新发现 | 完整版曾丢失，按已施工代码（MOD-POS-022 production 572 行）+ 30/31/32 号设计依据重建；不擅自定决策，缺口全部入 §7 |
