---
ttl: permanent
doc_type: architecture_view
title: 回测框架对接
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-12
topic: backtest_framework_docking
scope: 07_trading_decision_architecture
---

# 回测框架对接

> **性质**：决策备忘（G23）。核心事实：BM-BT-01~07 的**框架代码已基本全部 production**（D_BACKTEST 51 模块 = 50 生产 + 1 设计），regime 侧已按 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §2.1 完成对接；本文回填框架 why，并裁定**策略侧**（20 号首批 3 策略）如何复用同一框架。
> **历史说明**：00_index 标本文"active v1.7.4"，磁盘仅存骨架——完整版曾丢失，本版按已施工代码 + 11/53 号设计依据重建为 1.0.0。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G23 回测框架对接 |
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿 v1.2.0） |
| 对标 | 11 号 regime 对接范式 / Morwane walk-forward |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 优先级 | P2（G04 后） |
| 状态 | ✅ active v1.0.0（框架 production；策略侧编排与缺口见 §6/§7） |

## 2. 背景

**项目处境**：D_BACKTEST 域已施工 51 个模块（35 号域文档：50 生产 + 1 设计），覆盖引擎/撮合/PIT/WFA/过拟合检测/门控全链路。regime 侧（11 号）已按"复用同一框架"完成对接并产出 C1 对比器等适配件。策略侧（首批打板/多因子/事件驱动）尚无对等的验证流水线编排。

**核心问题**：策略验证与 regime 验证共用框架，但验证目标相反——策略要证"alpha 显著"，regime 只证"节流有效、不伤害即可"。对接不是接代码（代码已在），而是裁定策略侧逐环节的用法与门控标准。

**约束条件**：A 股 T+1、涨跌停、100 股整手、印花税/佣金——回测必须产生实盘可复现的成交（撮合一致性）；样本量有限（个股历史十余年）——过拟合是最大敌人；单机算力——向量化优先、事件驱动按需。

## 3. 决策

### 3.1 已施工设施盘点（BM-BT-01~07 代码映射）

| 环节 | 代码落点 | 状态 |
|---|---|---|
| BM-BT-01 引擎与撮合 | engine_base.py（ABC+注册表）/ vectorized_engine.py / event_driven_engine.py / shrinkage_engine.py / matching_logic.py（纯函数撮合：市价/限价/5 档 tick，万三佣金+1bp 滑点+印花税，全 Decimal）/ portfolio.py（T+1 锁定/非负约束）/ scheduler.py（网格搜索+并发） | ✅ production |
| BM-BT-02 持仓组合与数据接入 | data_handler.py（BacktestDataHandler/MultiSourceDataHandler+PIT 合并）/ cache_manager / data_quality_checker | ✅ production |
| BM-BT-03 绩效指标与 Tick 回放 | metrics.py（Sharpe 用 10 年期国债 rf=2.5%，样本<60 不算 Sharpe）/ tick_replay.py；03-E 密度预测验证（CRPS）未施工 | 主体 ✅ |
| BM-BT-04 PIT 铁律 | pit_manager.py（AS OF JOIN + Embargo + 一致性测试 + 幸存者偏差检测）；04-C Purged K-Fold 无代码 | 04-A/B ✅ |
| BM-BT-05 过拟合检测 | overfitting_detector.py（三维度+三层）/ walk_forward.whites_reality_check / metrics.calculate_dsr + simulation/deflated_sharpe_calculator.py；05-F/I/J 未施工 | 核心 ✅ |
| BM-BT-06 Walk-Forward | walk_forward.py 三模式（rolling/anchored/expanding，块长自动 T^(1/3)）；06-C 自适应 WF 无代码 | 06-A/B ✅ |
| BM-BT-07 决策门控与上线 | decision_gate.py（IS→WFA→OOS 不可跳级+参数锁定）/ io 三件套（result_sink/repository/decisiongraph_adapter）；07-H result_deployer 设计态（受限需 D-EX-CORE 就绪） | 07-A~G ✅ |

**回测=实盘一致性的核心 why**：`MatchingLogic` 纯函数撮合被 D_BACKTEST 与 D_EX_CORE MiniQmtBroker **共同调用**——回测和实盘走同一段撮合代码，从根上消除行为偏差；`Portfolio` 在组合层强制 T+1/非负，防止回测产生实盘不可能的成交。

### 3.2 要点①：BM-BT-01~07 在策略验证中的用法

策略侧复用映射（对标 11 号 §2.1 regime 范式）：

| 环节 | 策略验证用法 |
|---|---|
| 01 引擎 | 多因子/事件驱动用向量化引擎（速度快、网格搜索友好）；打板用事件驱动引擎（Tick/分钟级，撮合真实感优先） |
| 02 数据 | 统一走 BacktestDataHandler，PIT 合并强制开启 |
| 03 指标 | calculate_full_metrics（基础+DSR）为唯一产出口径 |
| 04 PIT | 三件套全开：AS OF JOIN + Embargo 5 个交易日 + 幸存者偏差检测（退市股入池） |
| 05 过拟合 | 三维度全跑 + strict_overfitting_gate=True（引擎层硬阻断，SIM-56） |
| 06 WFA | rolling 为主（A 股非平稳），anchored 对照；White's Reality Check 校正多重比较 |
| 07 门控 | DecisionGate.evaluate 三阶段不可跳级；can_deploy 后仍需人工审批（技术门控≠上线许可） |

### 3.3 要点②：策略回测 vs regime 回测差异（裁定）

沿用 11 号 §1.3 六维差异并补策略侧裁定：

| 维度 | 策略回测 | regime 回测 |
|---|---|---|
| 验证目标 | **证 alpha 显著**（Sharpe>0.5 准入） | 证节流有效、不伤害即可 |
| 过拟合风险 | 高（参数多、直接挖收益）→ 三维度+DSR 全负荷 | 低（自由度小）→ 简化 |
| 门控标准 | IS Sharpe≥0.5 + WFA 多数 fold 通过 + OOS/IS≥0.70 | 节流对比实验（C1 对比器） |
| 输出消费 | 上线许可 + budget 分配输入 | Shrinkage 系数 |
| 因果链 | 信号→持仓→PnL 全链 | regime 标签→仓位缩放 |
| 对接模块 | DecisionGate + overfitting_detector 全量 | shrinkage_provider/engine 适配层 |

### 3.4 要点③：策略上线门控 IS→WFA→OOS（已施工，53 号锚点补位）

`decision_gate.py`（791 行 production，不变量："IS→WFA→OOS 不可跳级；参数锁定；Sharpe>0.5 准入"）：
- **IS 段**：Sharpe≥0.5 准入 + 参数稳定性（±10% 窗口 Sharpe 变化<20% 判高原，相邻点降>50% 判悬崖——避悬崖比找峰值重要）；
- **WFA 段**：多数通过（>50% fold）+ 灾难否决（任一 fold MaxDD>50% 一票否决）；WFA 看 fold 相对稳定性而非绝对准入（阈值 0.0）；
- **OOS 段**：参数锁定强制 + OOS/IS Sharpe≥0.70（SSoT 单向导入自 overfitting_detector）；
- `evaluate()` 编排不可跳级，`can_deploy` 仅技术门控，正式上线需人工审批。
本节即 [53_simulation_live_path](53_simulation_live_path.md) §3.1 引用的"52 号 §3.4 IS→WFA→OOS 门控放行"锚点——回测门控通过是 53 号 PARALLEL→SHADOW→GRAY_RAMP 三阶段迁移的前置。2026 年业界共识（WFA+DSR+canary 部署三过滤器）与本链路同构：canary ≈ 53 号 GRAY_RAMP。

### 3.5 要点④：过拟合检测三维度（已施工）

`overfitting_detector.py`：①walk-forward 稳定性（正 Sharpe fold≥60%、CV≤1.5、无灾难 fold）②参数敏感性（±10% 扰动 Sharpe 变化≤30%）③泛化（跨时段/跨标的正 Sharpe≥60%）；三层防线：检测器 → SIM-38 样本内外对比（<0.70 硬否决）→ SIM-56 引擎层 OverfittingGateError 硬阻断。why 三维度而非单维度：单一维度都有绕开路径（WF 稳定可参数刷出来、参数稳定可时段刷出来），三维交叉才构成个人可执行的最低可信标准。

### 3.6 要点⑤：Deflated Sharpe（已施工，双实现待统编）

DSR（Bailey & López de Prado 2014）两处实现：`backtest/core/metrics.py calculate_dsr`（非正态修正+多重测试偏差修正，DSR<0.5 判过拟合）与 `simulation/deflated_sharpe_calculator.py`（MOD-SIM-024，阈值 0.95，有专属测试）。why 必须 DSR：个人开发试错次数多（AI 并发生成策略变体），多重比较偏差是首要过拟合来源——2026 年研究复算：3 次试错即可让零 alpha 策略呈现统计显著假象；`n_trials` 强制调用方传实际试错次数，防默认值自我安慰。双实现口径不一的统编问题登记 §7。

## 4. 考虑过的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 策略侧另建独立回测栈 | 拒绝——同一撮合/PIT/门控复用是"回测=实盘一致"与"策略/regime 可比"的前提 |
| 外部回测框架（backtrader/zipline/vectorbt） | 拒绝——A 股 T+1/涨跌停/整手/印花税原生内建比改造外部框架更可靠；且撮合须与 MiniQmtBroker 共享 |
| 门控全自动上线（can_deploy 即部署） | 拒绝——07-H result_deployer 保持设计态，实盘部署必须人工审批（53 号迁移路径亦如此） |
| CPCV+PBO 立即补齐 | 暂缓——2026 金标准但实现重；现有 WFA+White's RC+DSR 已覆盖多重比较主风险，列 §6 待裁定 |
| BM-BT 七环节砍到 3-4 环节 | 拒绝——七环节代码已全部 production，砍环节=删已绿代码且无收益；环节粒度对应"引擎/数据/指标/PIT/过拟合/WFA/门控"各自独立演进轴，合并反而耦合 |

## 5. 上限定义

**系统上限**：三引擎（向量化/事件驱动/Shrinkage）+ 三维度过拟合 + 三阶段门控 + DSR，对个人 3-5 策略组合已是上限。**演进路径**：策略侧编排入口（统一"策略验证流水线"调用 DecisionGate）随首批上线补；CPCV/Purged K-Fold/Permutation Test 按需升级（首批变体数量>50 时多重比较风险升级再启用）。**为何是上限**：05-F/I/J（Permutation/组合级/p-hacking 追踪）与自适应 WF 属研究级组件（OE-009 同族），个人系统变体规模不需要。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| CPCV + PBO（BM-BT-05 升级） | 实现重；现有组合已覆盖主风险 | 策略变体 >50 或 DSR 频繁误报 |
| Purged K-Fold（BM-BT-04-C） | WFA 的 Embargo 已部分等效；独立实现待 P1-18 | 标签重叠窗口策略（多周期持仓）上线时 |
| 07-H result_deployer（自动部署） | 受限项：涉实盘安全，需 D-EX-CORE 就绪 | 53 号 GRAY_RAMP 完成后 |
| 03-E CRPS 密度预测验证 | 仅 regime 密度预测需要，策略侧无消费方 | regime 密度预测上线时（11 号范围） |

## 7. 待定问题（G23 五要点逐项裁定）

- [x] ① **BM-BT-01~07 策略验证用法**——✅ 已定（§3.2 映射表）；🔨 缺统一编排入口（策略验证流水线），随首批上线施工。
- [x] ② **策略 vs regime 回测差异**——✅ 已裁定（§3.3）。
- [x] ③ **IS→WFA→OOS 门控**——✅ 代码已施工（§3.4）。⚠️ 缺口：regime 适配版门控未启动（11 号 §0.5 Phase 5，归 11 号）；DSR 未接入 DecisionGate 判定链——**待决策**：是否把 dsr≥阈值 加为 OOS 段第四条件。
- [x] ④ **过拟合三维度**——✅ 代码已施工（§3.5）。缺口：05-F/I/J 与 05-H 归因分解（登记 §6）。
- [x] ⑤ **Deflated Sharpe**——✅ 代码已施工（§3.6）。⚠️ **待决策（双实现统编）**：backtest 版（阈值 0.5）vs simulation 版（阈值 0.95）裁定唯一 SSoT，或明确分工（引擎内快速筛查用 backtest 版 / 独立评估报告用 simulation 版）。

**代码层新发现问题**：
1. **四个核心模块零单测**——walk_forward.py / decision_gate.py / overfitting_detector.py / pit_manager.py 均无专属测试（G23 的骨架在裸奔）；backtest 版 calculate_dsr 亦无直接测试。补测试列 P1。
2. battle_map_03 详节滞后——BT-07 metrics 扩展标 planned（DSR 实际已施工）、scheduler 标 planned（已 production），需同步 battle_map 真源（越界，登记在此）。
3. 53 号 §3.1 对"52 号 §3.4"的悬空引用已由本版 §3.4 补位。
4. **00_index 同步（越界登记）**：00_index 标本文"active v1.7.4"，与本版 1.0.0 不一致，需同步（详见 33 号 §7 新发现 7 的统一登记）。

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G23
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §1.3 / §2.1（regime 对接范式）
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [53_simulation_live_path](53_simulation_live_path.md) §3.1（回测→模拟→实盘迁移，引用本文 §3.4）
- 35_d_backtest（D_BACKTEST 域 51 模块清单）
- 代码：`src/zephyr/backtest/core/`（engine_base/walk_forward/pit_manager/metrics/decision_gate/overfitting_detector/matching_logic/portfolio）
- battle_map_03_backtest_validation（BM-BT-01~07 状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G23 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active：回填 BM-BT-01~07 全部代码映射与五要点裁定；§3.4 补 53 号悬空引用锚点；§4 补"七环节不砍"裁定；登记双 DSR 统编等 4 项新发现 | 完整版（v1.7.4）曾丢失，按已施工代码重建；未施工项（CPCV/Purged K-Fold 等）入 §6 待裁定不擅自补齐 |
